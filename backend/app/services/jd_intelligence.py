import re
from typing import Dict, Any, List
from app.services.gemini_client import gemini_service
from app.models.schemas import JobAnalysisResponse, RequirementCreate

TECH_KEYWORDS = [
    "python", "fastapi", "django", "flask", "react", "typescript", "javascript",
    "postgresql", "postgres", "mysql", "mongodb", "redis", "docker", "kubernetes",
    "aws", "azure", "gcp", "llm", "llm apis", "langchain", "pytorch", "tensorflow",
    "rest api", "graphql", "ci/cd", "git", "linux", "system design", "microservices",
    "sql", "nosql", "tailwind", "next.js", "node.js"
]

def analyze_job_description(title: str, text: str) -> JobAnalysisResponse:
    """
    Parses and categorizes a Job Description into structured requirements:
    MUST_HAVE, SHOULD_HAVE, NICE_TO_HAVE, responsibilities, years experience, etc.
    """
    # 1. Try with Gemini if available
    if gemini_service.is_available():
        prompt = f"""
You are an expert recruitment intelligence AI. Analyze this job description:
Title: {title}
Description:
{text}

Extract the following in strictly valid JSON:
{{
  "job_title": "{title}",
  "seniority": "e.g. Senior / Mid-Level / Lead",
  "min_years_experience": 3.0,
  "education_required": "e.g. Bachelor's in Computer Science or equivalent",
  "location": "e.g. Remote / New York / Hybrid",
  "work_mode": "Remote / On-site / Hybrid",
  "critical_requirements": ["Python", "FastAPI"],
  "optional_requirements": ["AWS"],
  "must_have_skills": ["Python", "FastAPI", "React", "TypeScript", "PostgreSQL"],
  "should_have_skills": ["Docker", "LLM APIs"],
  "nice_to_have_skills": ["AWS", "Redis"],
  "responsibilities": ["Design full stack architecture", "Build REST APIs"],
  "tools_and_tech": ["Python", "Docker", "Git"],
  "domain_knowledge": ["Generative AI", "Distributed Systems"],
  "soft_skills": ["Technical leadership", "Communication"],
  "classified_requirements": [
    {{"name": "Python", "category": "skill", "tier": "MUST_HAVE", "expected_years": 3.0, "weight": 1.0}},
    {{"name": "FastAPI", "category": "skill", "tier": "MUST_HAVE", "expected_years": 2.0, "weight": 1.0}}
  ]
}}
"""
        result = gemini_service.generate_json(prompt)
        if result and "classified_requirements" in result:
            try:
                classified = [RequirementCreate(**r) for r in result.get("classified_requirements", [])]
                return JobAnalysisResponse(
                    job_title=result.get("job_title", title),
                    seniority=result.get("seniority", "Senior"),
                    min_years_experience=float(result.get("min_years_experience", 3.0)),
                    education_required=result.get("education_required", "Bachelor's in Computer Science or equivalent"),
                    location=result.get("location", "Remote"),
                    work_mode=result.get("work_mode", "Remote / Hybrid"),
                    critical_requirements=result.get("critical_requirements", []),
                    optional_requirements=result.get("optional_requirements", []),
                    must_have_skills=result.get("must_have_skills", []),
                    should_have_skills=result.get("should_have_skills", []),
                    nice_to_have_skills=result.get("nice_to_have_skills", []),
                    responsibilities=result.get("responsibilities", []),
                    tools_and_tech=result.get("tools_and_tech", []),
                    domain_knowledge=result.get("domain_knowledge", []),
                    soft_skills=result.get("soft_skills", []),
                    classified_requirements=classified
                )
            except Exception as e:
                # Fallback to deterministic parser
                pass

    # 2. Deterministic high-precision fallback
    return _deterministic_jd_analysis(title, text)

def _deterministic_jd_analysis(title: str, text: str) -> JobAnalysisResponse:
    text_lower = text.lower()
    
    # Seniority extraction
    seniority = "Mid-Senior"
    if "lead" in text_lower or "staff" in text_lower or "principal" in text_lower:
        seniority = "Lead / Staff"
    elif "senior" in text_lower or "sr." in text_lower:
        seniority = "Senior"
    elif "junior" in text_lower or "associate" in text_lower or "entry" in text_lower:
        seniority = "Junior / Entry"

    # Years of experience extraction
    min_years = 3.0
    exp_match = re.search(r'(\d+)\+?\s*(?:-\s*\d+)?\s*(?:years?|yrs?)(?:\s+of)?\s+experience', text_lower)
    if exp_match:
        try:
            min_years = float(exp_match.group(1))
        except ValueError:
            min_years = 3.0

    # Skills detection
    found_skills = []
    for kw in TECH_KEYWORDS:
        # Match as whole word
        pattern = r'\b' + re.escape(kw) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.append(kw.title() if kw != "aws" and kw != "llm" and kw != "ci/cd" else kw.upper())

    # Segment into Must / Should / Nice
    must_have = []
    should_have = []
    nice_to_have = []
    
    # Sections inspection
    must_markers = ["must have", "required", "qualifications", "minimum requirements", "core skills"]
    nice_markers = ["nice to have", "preferred", "bonus", "good to have", "plus"]
    
    for skill in found_skills:
        s_lower = skill.lower()
        if any(marker in text_lower for marker in nice_markers) and (s_lower in ["aws", "redis", "graphql", "tailwind"]):
            nice_to_have.append(skill)
        elif s_lower in ["docker", "kubernetes", "llm apis", "ci/cd"]:
            should_have.append(skill)
        else:
            must_have.append(skill)

    if not must_have and found_skills:
        must_have = found_skills[:4]
        should_have = found_skills[4:7]
        nice_to_have = found_skills[7:]

    # Classified Requirements
    classified: List[RequirementCreate] = []
    for s in must_have:
        classified.append(RequirementCreate(
            name=s,
            category="skill",
            tier="MUST_HAVE",
            description=f"Demonstrated professional capability in {s}",
            expected_years=min_years,
            weight=1.0
        ))
    for s in should_have:
        classified.append(RequirementCreate(
            name=s,
            category="skill",
            tier="SHOULD_HAVE",
            description=f"Hands-on experience with {s}",
            expected_years=max(1.0, min_years - 1.0),
            weight=0.75
        ))
    for s in nice_to_have:
        classified.append(RequirementCreate(
            name=s,
            category="skill",
            tier="NICE_TO_HAVE",
            description=f"Familiarity or bonus exposure to {s}",
            expected_years=1.0,
            weight=0.50
        ))

    # Experience requirement
    classified.append(RequirementCreate(
        name=f"{int(min_years)}+ Years Professional Experience",
        category="experience",
        tier="MUST_HAVE",
        description=f"Minimum {int(min_years)} years of relevant software engineering experience",
        expected_years=min_years,
        weight=1.0
    ))

    # Responsibilities extraction (lines with bullets or verbs)
    responsibilities = []
    for line in text.splitlines():
        line_s = line.strip()
        if (line_s.startswith("-") or line_s.startswith("•") or line_s.startswith("*")) and len(line_s) > 15:
            responsibilities.append(line_s.lstrip("-•* ").strip())
        if len(responsibilities) >= 6:
            break
            
    if not responsibilities:
        responsibilities = [
            f"Architect and develop scalable full-stack web applications and AI services.",
            f"Build robust backend APIs and data integration pipelines using modern Python frameworks.",
            f"Collaborate with product and ML teams to implement user-centric intelligent features.",
            f"Maintain high standards of software quality, automated testing, and CI/CD deployment."
        ]

    return JobAnalysisResponse(
        job_title=title,
        seniority=seniority,
        min_years_experience=min_years,
        education_required="Bachelor's degree in Computer Science, Software Engineering, or related technical field",
        location="Remote (Global)" if "remote" in text_lower else "Hybrid / On-site",
        work_mode="Remote" if "remote" in text_lower else "Hybrid",
        critical_requirements=must_have[:5],
        optional_requirements=nice_to_have,
        must_have_skills=must_have,
        should_have_skills=should_have,
        nice_to_have_skills=nice_to_have,
        responsibilities=responsibilities,
        tools_and_tech=found_skills,
        domain_knowledge=["Full Stack Web Architecture", "AI & LLM Integration", "Distributed Systems"],
        soft_skills=["Cross-functional Collaboration", "System Design Communication", "Ownership & Autonomy"],
        classified_requirements=classified
    )
