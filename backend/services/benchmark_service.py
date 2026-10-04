import logging
import random
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from app.models import orm
from app.routes.matching import run_matching_engine

logger = logging.getLogger("talentproof.benchmark")

FIRST_NAMES = [
    "Alex", "Elena", "Marcus", "Sarah", "David", "Priya", "Jordan", "Michael", "Chen", "Sofia",
    "Liam", "Olivia", "Noah", "Emma", "Ethan", "Ava", "Lucas", "Mia", "Mason", "Isabella",
    "Oliver", "Harper", "Elijah", "Evelyn", "James", "Abigail", "Benjamin", "Emily", "Sebastian", "Elizabeth",
    "Logan", "Sofia", "Jackson", "Avery", "Jack", "Ella", "Aidan", "Scarlett", "Samuel", "Chloe",
    "Henry", "Victoria", "Matthew", "Grace", "Joseph", "Zoey", "Levi", "Penelope", "Mateo", "Riley"
]

LAST_NAMES = [
    "Vance", "Rostova", "Mercer", "Chen", "Sterling", "Patel", "Thorne", "Hayes", "Tanaka", "Rossi",
    "Kim", "Dubois", "Johansson", "Silva", "Novak", "Garcia", "Müller", "Kowalski", "Santos", "Mehta",
    "Walker", "Adams", "Wright", "Lopez", "Hill", "Scott", "Green", "Adams", "Baker", "Gonzalez",
    "Nelson", "Carter", "Mitchell", "Perez", "Roberts", "Turner", "Phillips", "Campbell", "Parker", "Evans",
    "Edwards", "Collins", "Stewart", "Sanchez", "Morris", "Rogers", "Reed", "Cook", "Morgan", "Bell"
]

COMPANIES = [
    "Stripe", "Datadog", "Snowflake", "Scale AI", "Vercel", "Shopify", "Cloudflare",
    "Linear", "Retool", "Supabase", "Anthropic", "Ramp", "Notion", "Brex", "GitHub"
]

UNIVERSITIES = [
    "Stanford University", "MIT", "UC Berkeley", "Carnegie Mellon", "University of Washington",
    "Georgia Tech", "University of Waterloo", "UT Austin", "Cornell University", "UIUC"
]

CITIES = [
    "San Francisco, CA", "New York, NY", "Seattle, WA", "Austin, TX", "Toronto, ON",
    "Boston, MA", "Chicago, IL", "Vancouver, BC", "London, UK", "Remote"
]

TARGET_JOB_TITLE = "Senior Full Stack AI Engineer"
TARGET_JOB_DESC = """
We are looking for a Senior Full Stack AI Engineer to design and scale intelligent recruiter systems.
Requirements:
Must have:
- Python (production backend development)
- FastAPI (REST APIs, high-performance async services)
- React (modern component architecture)
- TypeScript (strict typing, frontend applications)
- PostgreSQL (relational modeling, indexing, SQL queries)
- AWS (deploying scalable cloud infrastructure)
- LLMs (building prompt workflows, fine-tuning, embeddings)
- Microservices (distributed architectures)
- 3+ years experience

Preferred / Nice to have:
- Docker (containerization)
- LLM APIs (OpenAI, Anthropic, Gemini)
"""

REQUIRED_SKILLS = ["Python", "FastAPI", "React", "TypeScript", "PostgreSQL", "AWS", "LLMs", "Microservices"]
PREFERRED_SKILLS = ["Docker", "LLM APIs", "Redis", "Kafka"]

def ensure_benchmark_job(db: Session) -> orm.Job:
    """Finds or provisions the canonical target job for the benchmark."""
    job = db.query(orm.Job).filter(orm.Job.title == TARGET_JOB_TITLE).first()
    if not job:
        job = orm.Job(
            title=TARGET_JOB_TITLE,
            raw_description=TARGET_JOB_DESC,
            seniority="Senior",
            min_years_experience=3.0,
            education_required="Bachelor's in Computer Science or equivalent",
            location="Remote / San Francisco",
            work_mode="Remote",
            responsibilities=[
                "Build reactive full-stack web applications using Next.js and FastAPI",
                "Integrate multimodal LLMs and vector search embeddings",
                "Design clean database schemas in PostgreSQL with connection pooling",
                "Deploy resilient microservices to cloud infrastructure on AWS"
            ],
            tools_and_tech=["Python", "FastAPI", "React", "TypeScript", "PostgreSQL", "AWS", "LLMs", "Docker"],
            domain_knowledge=["AI Recruitment Intelligence", "Distributed Systems", "Cloud Architecture"],
            soft_skills=["Architecture leadership", "Technical communication", "Pragmatism"],
            weights={
                "required_skills": 0.35,
                "relevant_experience": 0.20,
                "project_evidence": 0.15,
                "education_cert": 0.10,
                "preferred_skills": 0.10,
                "domain_relevance": 0.05,
                "evidence_confidence": 0.05
            }
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        # Create classified requirements
        reqs = [
            ("Python", "skill", "MUST_HAVE", 3.0, 1.0),
            ("FastAPI", "skill", "MUST_HAVE", 2.0, 1.0),
            ("React", "skill", "MUST_HAVE", 3.0, 1.0),
            ("TypeScript", "skill", "MUST_HAVE", 2.0, 1.0),
            ("PostgreSQL", "skill", "MUST_HAVE", 2.0, 1.0),
            ("AWS", "skill", "MUST_HAVE", 2.0, 1.0),
            ("LLMs", "skill", "MUST_HAVE", 1.0, 1.0),
            ("Microservices", "skill", "MUST_HAVE", 2.0, 1.0),
            ("3+ years experience", "experience", "MUST_HAVE", 3.0, 1.0),
            ("Docker", "skill", "NICE_TO_HAVE", 1.0, 0.5),
            ("LLM APIs", "skill", "NICE_TO_HAVE", 1.0, 0.5),
        ]
        for name, cat, tier, exp_yrs, wt in reqs:
            db.add(orm.JobRequirement(
                job_id=job.id,
                name=name,
                category=cat,
                tier=tier,
                expected_years=exp_yrs,
                weight=wt
            ))
        db.commit()
        db.refresh(job)

    return job

def generate_synthetic_profile(
    rng: random.Random,
    index: int,
    category: str,
    job_id: int
) -> Dict[str, Any]:
    """
    Generates a deterministic, realistic synthetic candidate profile based on category:
    - excellent: 10 candidates (all must-haves, 5-8 yrs, strong projects, high evidence)
    - strong: 10 candidates (7/8 must-haves, GCP instead of AWS transferable, 4-6 yrs)
    - moderate: 10 candidates (50-70% must-haves, 2-4 yrs, partial projects)
    - weak: 10 candidates (1-2 must-haves, junior <2 yrs, missing core backend)
    - poor: 10 candidates (unrelated domain, 0-1 match, contradiction or no evidence)
    """
    first_name = FIRST_NAMES[index % len(FIRST_NAMES)]
    last_name = LAST_NAMES[(index * 7 + 3) % len(LAST_NAMES)]
    name = f"{first_name} {last_name}"
    email = f"{first_name.lower()}.{last_name.lower()}{index}@benchmark.talentproof.ai"
    city = rng.choice(CITIES)
    univ = rng.choice(UNIVERSITIES)
    comp1 = rng.choice(COMPANIES)
    comp2 = rng.choice([c for c in COMPANIES if c != comp1])

    if category == "excellent":
        expected_cat = "RECOMMEND"
        exp_years = rng.uniform(5.5, 9.0)
        skills = REQUIRED_SKILLS + rng.sample(PREFERRED_SKILLS, 2)
        summary = f"Staff/Senior AI Engineer with {exp_years:.1f} years building production LLM applications and scalable microservices in Python, FastAPI, and React."
        experiences = [
            {
                "company": comp1,
                "role": "Senior Full Stack AI Engineer",
                "start_date": "2022-01",
                "end_date": "Present",
                "duration_years": round(exp_years - 2.5, 1),
                "responsibilities": [
                    "Architected high-throughput FastAPI and Python microservices on AWS ECS handling 25k req/sec",
                    "Integrated LangChain and Gemini LLM APIs for automated entity extraction and summarization",
                    "Built reactive recruiter dashboards with React 19, TypeScript, and Tailwind CSS",
                    "Optimized PostgreSQL query latency by 45% using composite indexing and connection pooling"
                ],
                "achievements": [
                    "Reduced AI inference cost by 38% via embedding caching",
                    "Delivered zero-downtime microservices migration on AWS"
                ],
                "technologies": ["Python", "FastAPI", "React", "TypeScript", "PostgreSQL", "AWS", "LLMs", "Docker"]
            },
            {
                "company": comp2,
                "role": "Full Stack Software Engineer",
                "start_date": "2019-06",
                "end_date": "2021-12",
                "duration_years": 2.5,
                "responsibilities": [
                    "Developed full-stack web features using React and Python REST services",
                    "Managed PostgreSQL database migrations and Docker container pipelines"
                ],
                "achievements": ["Scaled platform to 300k active users"],
                "technologies": ["Python", "React", "TypeScript", "PostgreSQL", "Docker"]
            }
        ]
        projects = [
            {
                "title": "Autonomous LLM Retrieval Engine",
                "description": "Enterprise RAG pipeline with pgvector and FastAPI",
                "technologies": ["Python", "FastAPI", "LLMs", "PostgreSQL", "AWS"],
                "contribution": "Lead Architect",
                "results_metrics": "Sub-50ms p95 retrieval latency across 5M vectors"
            }
        ]
        risks = []

    elif category == "strong":
        expected_cat = "RECOMMEND"
        exp_years = rng.uniform(4.0, 6.0)
        # Missing AWS directly, has GCP as transferable; missing Microservices explicit keyword
        skills = ["Python", "FastAPI", "React", "TypeScript", "PostgreSQL", "GCP", "LLMs", "Docker"]
        summary = f"Full Stack Engineer with {exp_years:.1f} years experience specializing in TypeScript frontend and Python cloud services."
        experiences = [
            {
                "company": comp1,
                "role": "Full Stack Engineer",
                "start_date": "2021-03",
                "end_date": "Present",
                "duration_years": round(exp_years - 1.5, 1),
                "responsibilities": [
                    "Engineered cloud web services in FastAPI and Python deployed on Google Cloud Platform (GCP)",
                    "Constructed design systems and analytics views in React and TypeScript",
                    "Implemented semantic search workflows using LLM APIs"
                ],
                "achievements": ["Improved frontend bundle size by 30%"],
                "technologies": ["Python", "FastAPI", "React", "TypeScript", "PostgreSQL", "GCP", "LLMs"]
            }
        ]
        projects = [
            {
                "title": "Recruitment Sourcing Copilot",
                "description": "AI-assisted candidate outreach tool using React and Python",
                "technologies": ["React", "TypeScript", "Python", "LLMs"],
                "contribution": "Core Engineer",
                "results_metrics": "Adopted by 45 hiring teams"
            }
        ]
        risks = []

    elif category == "moderate":
        expected_cat = "CONSIDER"
        exp_years = rng.uniform(2.5, 4.0)
        # Has Python and PostgreSQL, but frontend in Vue instead of React, no LLM production experience
        skills = ["Python", "Django", "Vue.js", "JavaScript", "PostgreSQL", "AWS", "Git"]
        summary = f"Software Developer with {exp_years:.1f} years building backend web applications with Python and relational databases."
        experiences = [
            {
                "company": comp1,
                "role": "Software Developer",
                "start_date": "2022-06",
                "end_date": "Present",
                "duration_years": round(exp_years, 1),
                "responsibilities": [
                    "Built Django backend APIs and connected PostgreSQL databases",
                    "Created frontend views in Vue.js and JavaScript",
                    "Configured AWS S3 and EC2 instances"
                ],
                "achievements": ["Automated client reporting pipeline"],
                "technologies": ["Python", "Django", "PostgreSQL", "AWS"]
            }
        ]
        projects = [
            {
                "title": "Internal Admin Dashboard",
                "description": "CRUD web interface for inventory tracking",
                "technologies": ["Python", "Django", "PostgreSQL"],
                "contribution": "Developer",
                "results_metrics": "Supported 10 internal operators"
            }
        ]
        risks = []

    elif category == "weak":
        expected_cat = "VERIFY"
        exp_years = rng.uniform(1.0, 2.0)
        # Junior developer with HTML/CSS/JS, claims 5 years experience (contradiction!)
        skills = ["HTML", "CSS", "JavaScript", "React", "Node.js"]
        summary = "Junior web developer eager to learn backend development and cloud architecture."
        experiences = [
            {
                "company": comp1,
                "role": "Junior Frontend Developer",
                "start_date": "2023-08",
                "end_date": "Present",
                "duration_years": round(exp_years, 1),
                "responsibilities": [
                    "Assisted with React UI components and bug fixing in CSS",
                    "Wrote unit tests in Jest"
                ],
                "achievements": ["Resolved 35 UI bug tickets"],
                "technologies": ["JavaScript", "React", "CSS"]
            }
        ]
        projects = [
            {
                "title": "Personal Portfolio",
                "description": "Static portfolio website",
                "technologies": ["React", "Vite"],
                "contribution": "Creator",
                "results_metrics": "Deployed on GitHub Pages"
            }
        ]
        risks = [
            {
                "flag_type": "EXPERIENCE_GAP",
                "severity": "HIGH",
                "headline": "Junior Experience Level Below Requirement",
                "details": f"Candidate possesses {exp_years:.1f} years experience versus 3.0 years required.",
                "neutral_recommendation": "Verify whether candidate has additional unlisted experience or strong open source projects."
            }
        ]

    else:  # poor
        expected_cat = "NOT_CURRENT_FIT"
        exp_years = rng.uniform(1.0, 3.0)
        # Completely unrelated domain (e.g. manual QA / WordPress / accountant)
        skills = ["WordPress", "Manual Testing", "Excel", "Data Entry", "Photoshop"]
        summary = "Digital marketing assistant and WordPress administrator with experience editing content and testing web pages."
        experiences = [
            {
                "company": "Local Agency",
                "role": "Content Administrator",
                "start_date": "2022-01",
                "end_date": "2024-01",
                "duration_years": round(exp_years, 1),
                "responsibilities": [
                    "Updated WordPress blog posts and edited images in Photoshop",
                    "Performed manual cross-browser testing on mobile devices"
                ],
                "achievements": ["Published 120 blog articles"],
                "technologies": ["WordPress", "Excel"]
            }
        ]
        projects = []
        risks = [
            {
                "flag_type": "UNBACKED_EXPERTISE",
                "severity": "HIGH",
                "headline": "Zero Target Skill Alignment",
                "details": "Candidate profile contains no verified experience in Python, FastAPI, React, or cloud systems.",
                "neutral_recommendation": "Review other candidates possessing relevant software engineering background."
            }
        ]

    return {
        "index": index,
        "category": category,
        "expected_category": expected_cat,
        "name": name,
        "email": email,
        "location": city,
        "university": univ,
        "total_experience_years": round(exp_years, 1),
        "summary": summary,
        "skills": skills,
        "experiences": experiences,
        "projects": projects,
        "risks": risks
    }

def run_50_resume_benchmark(
    seed: int = 12345,
    db: Session = None
) -> Dict[str, Any]:
    """
    Executes the 50-Resume Stress Test & Benchmark Pipeline.
    1. Provisions canonical target job
    2. Generates 50 distinct synthetic candidate profiles (10 excellent, 10 strong, 10 moderate, 10 weak, 10 poor)
    3. Persists all 50 candidates, resumes, and child entities to Supabase PostgreSQL
    4. Executes the deterministic matching engine
    5. Calculates precision, recall, F1, and score distribution
    6. Persists AnalysisRun record with benchmark summary
    """
    start_time = time.time()
    rng = random.Random(seed)
    benchmark_run_id = f"bench-{uuid.uuid4().hex[:12]}"
    logger.info(f"[BENCHMARK] Starting 50-resume benchmark run {benchmark_run_id} with seed={seed}")

    # Step 1: Ensure Target Job
    job = ensure_benchmark_job(db)

    # Step 2: Distribution setup (10 of each category)
    categories = (
        ["excellent"] * 10 +
        ["strong"] * 10 +
        ["moderate"] * 10 +
        ["weak"] * 10 +
        ["poor"] * 10
    )
    rng.shuffle(categories)

    created_candidates: List[Tuple[orm.Candidate, str, str]] = []
    failed_indices = []

    # Step 3: Candidate & Resume Ingestion Loop
    for idx, cat in enumerate(categories, 1):
        try:
            profile = generate_synthetic_profile(rng, idx, cat, job.id)

            cand = orm.Candidate(
                job_id=job.id,
                name=profile["name"],
                email=profile["email"],
                location=profile["location"],
                summary=profile["summary"],
                total_experience_years=profile["total_experience_years"],
                processing_status="ANALYZING"
            )
            db.add(cand)
            db.commit()
            db.refresh(cand)

            # Create Resume record
            raw_text = f"RESUME OF {cand.name}\nLocation: {cand.location}\nExperience: {cand.total_experience_years} years\n\nSummary:\n{cand.summary}\n\nSkills:\n" + ", ".join(profile["skills"])
            resume_rec = orm.Resume(
                candidate_id=cand.id,
                job_id=job.id,
                original_filename=f"{profile['name'].replace(' ', '_')}_Resume.pdf",
                file_name=f"{profile['name'].replace(' ', '_')}_Resume.pdf",
                storage_bucket="resume-files",
                storage_path=f"resumes/job-{job.id}/candidate-{cand.id}/synthetic_resume.pdf",
                file_type="pdf",
                file_size=len(raw_text.encode('utf-8')),
                file_hash=uuid.uuid4().hex,
                processing_status="ANALYZING",
                raw_text=raw_text,
                parsed_json={"synthetic": True, "category": cat}
            )
            db.add(resume_rec)

            # Add Skills
            for sk in profile["skills"]:
                db.add(orm.CandidateSkill(
                    candidate_id=cand.id,
                    name=sk,
                    category="technical",
                    years_of_experience=min(profile["total_experience_years"], 4.0),
                    proficiency_claimed="proficient"
                ))

            # Add Experiences
            for exp in profile["experiences"]:
                db.add(orm.CandidateExperience(
                    candidate_id=cand.id,
                    company=exp["company"],
                    role=exp["role"],
                    start_date=exp["start_date"],
                    end_date=exp["end_date"],
                    duration_years=exp["duration_years"],
                    responsibilities=exp["responsibilities"],
                    achievements=exp.get("achievements", []),
                    technologies=exp["technologies"]
                ))

            # Add Education
            db.add(orm.CandidateEducation(
                candidate_id=cand.id,
                degree="Bachelor of Science in Computer Science",
                institution=profile["university"],
                graduation_year="2020",
                field="Computer Science"
            ))

            # Add Projects
            for prj in profile["projects"]:
                db.add(orm.CandidateProject(
                    candidate_id=cand.id,
                    title=prj["title"],
                    description=prj["description"],
                    technologies=prj["technologies"],
                    contribution=prj["contribution"],
                    results_metrics=prj["results_metrics"]
                ))

            # Add Pre-seeded Risks if any
            for rk in profile["risks"]:
                db.add(orm.RiskFlag(
                    candidate_id=cand.id,
                    job_id=job.id,
                    flag_type=rk["flag_type"],
                    severity=rk["severity"],
                    headline=rk["headline"],
                    details=rk["details"],
                    neutral_recommendation=rk["neutral_recommendation"]
                ))

            db.commit()
            created_candidates.append((cand, cat, profile["expected_category"]))

        except Exception as cand_err:
            db.rollback()
            logger.error(f"[BENCHMARK] Candidate #{idx} generation failed: {cand_err}")
            failed_indices.append(idx)
            continue

    # Step 4: Execute Deterministic Matching Engine across all candidates for this job
    run_matching_engine({"job_id": job.id}, db)

    # Step 5: Read back match results and evaluate accuracy
    benchmark_candidates = []
    match_scores = []
    evidence_scores = []
    hiring_confs = []
    high_risk_count = 0
    cat_counts = {"strong": 0, "moderate": 0, "weak": 0, "poor": 0}

    # Confusion matrix counters for accuracy evaluation:
    # Positive Ground Truth: excellent + strong
    # Negative Ground Truth: moderate + weak + poor
    tp, fp, tn, fn = 0, 0, 0, 0

    for cand, expected_profile_cat, ground_truth_rec in created_candidates:
        cand.processing_status = "COMPLETED"
        match = db.query(orm.MatchResult).filter(
            orm.MatchResult.candidate_id == cand.id,
            orm.MatchResult.job_id == job.id
        ).first()

        m_score = float(match.overall_match_score) if match else 0.0
        e_score = float(match.evidence_confidence_score) if match else 0.0
        h_conf = float(match.hiring_confidence_score) if match else 0.0
        actual_rec = match.recommendation if match else "REVIEW"

        match_scores.append(m_score)
        evidence_scores.append(e_score)
        hiring_confs.append(h_conf)

        flags_cnt = len(cand.risk_flags) if cand.risk_flags else 0
        if flags_cnt > 0:
            high_risk_count += 1

        # Classify actual recommendation category
        if actual_rec in ("STRONGLY_RECOMMEND", "RECOMMEND"):
            cat_counts["strong"] += 1
            actual_cat_label = "Strong Fit"
        elif actual_rec == "CONSIDER":
            cat_counts["moderate"] += 1
            actual_cat_label = "Moderate Fit"
        elif actual_rec == "VERIFY":
            cat_counts["weak"] += 1
            actual_cat_label = "Weak Fit"
        else:
            cat_counts["poor"] += 1
            actual_cat_label = "Poor Fit"

        # Ground truth evaluation
        is_ground_truth_positive = expected_profile_cat in ("excellent", "strong")
        is_model_positive = actual_rec in ("STRONGLY_RECOMMEND", "RECOMMEND")

        if is_ground_truth_positive and is_model_positive:
            tp += 1
        elif not is_ground_truth_positive and is_model_positive:
            fp += 1
        elif not is_ground_truth_positive and not is_model_positive:
            tn += 1
        else:
            fn += 1

        benchmark_candidates.append({
            "candidate_id": cand.id,
            "name": cand.name,
            "match_score": m_score,
            "evidence_score": e_score,
            "hiring_confidence": h_conf,
            "risk_level": "High" if flags_cnt > 0 else "Low",
            "recommendation": actual_rec,
            "expected_category": expected_profile_cat.title(),
            "actual_category": actual_cat_label,
            "status": "COMPLETED"
        })

    db.commit()

    # Step 6: Compute Accuracy Metrics
    precision = round(tp / (tp + fp), 3) if (tp + fp) > 0 else 1.0
    recall = round(tp / (tp + fn), 3) if (tp + fn) > 0 else 1.0
    f1 = round(2 * (precision * recall) / (precision + recall), 3) if (precision + recall) > 0 else 0.0

    duration = round(time.time() - start_time, 2)
    avg_match = round(sum(match_scores) / len(match_scores), 1) if match_scores else 0.0
    avg_evidence = round(sum(evidence_scores) / len(evidence_scores), 1) if evidence_scores else 0.0
    avg_hiring = round(sum(hiring_confs) / len(hiring_confs), 1) if hiring_confs else 0.0

    summary = {
        "benchmark_run_id": benchmark_run_id,
        "job_id": job.id,
        "seed": seed,
        "total": len(categories),
        "completed": len(created_candidates),
        "failed": len(failed_indices),
        "average_match": avg_match,
        "average_evidence": avg_evidence,
        "average_hiring_confidence": avg_hiring,
        "high_risk_count": high_risk_count,
        "strong_count": cat_counts["strong"],
        "moderate_count": cat_counts["moderate"],
        "weak_count": cat_counts["weak"],
        "poor_count": cat_counts["poor"],
        "processing_time_seconds": duration,
        "precision": precision,
        "recall": recall,
        "f1": f1
    }

    # Step 7: Persist AnalysisRun to PostgreSQL
    analysis_run = orm.AnalysisRun(
        id=benchmark_run_id,
        job_id=job.id,
        benchmark_run_id=benchmark_run_id,
        seed=seed,
        total_candidates=len(categories),
        completed_count=len(created_candidates),
        failed_count=len(failed_indices),
        results_summary=summary,
        status="COMPLETED"
    )
    db.add(analysis_run)
    db.commit()

    logger.info(f"[BENCHMARK COMPLETE] {benchmark_run_id}: F1={f1}, Duration={duration}s")
    summary["candidates"] = benchmark_candidates
    return summary
