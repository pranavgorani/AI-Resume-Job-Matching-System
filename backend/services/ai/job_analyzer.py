import hashlib
import json
import logging
import re
from typing import Any, Dict, List, Optional

from .ai_provider import get_ai_coordinator

logger = logging.getLogger("talentproof.ai.job")

JOB_ANALYSIS_SYSTEM = """
You are an expert technical recruiter and talent architect.
Analyze the provided Job Description (JD) and extract a comprehensive, structured role breakdown in valid JSON format.
Strictly extract and categorize:
- job_title (string)
- seniority (string: Junior, Mid-Level, Senior, Staff, Principal, Lead)
- required_skills (list of strings)
- preferred_skills (list of strings)
- minimum_experience (float/int years)
- education (string degree requirement)
- certifications (list of strings)
- responsibilities (list of strings)
- technologies (list of specific tools, languages, platforms)
- domain (string e.g. Fintech, Healthcare, Cloud Infrastructure, E-commerce, B2B SaaS)
- location (string)
- work_mode (string: Remote, Hybrid, On-site)
- must_have (list of non-negotiable critical requirements)
- should_have (list of important requirements)
- nice_to_have (list of bonus skills/traits)

Return ONLY valid JSON matching this schema.
"""

class JobAnalyzer:
    """
    Analyzes Job Descriptions using Gemini (primary) with Hugging Face fallback and caching.
    """
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}

    def analyze(self, jd_text: str) -> Dict[str, Any]:
        """Extract structured requirements, seniority, and tiered must/should/nice categories."""
        cleaned_text = jd_text.strip()
        if not cleaned_text:
            return self._empty_result()

        cache_key = hashlib.sha256(cleaned_text.encode("utf-8")).hexdigest()
        if cache_key in self._cache:
            return self._cache[cache_key]

        coordinator = get_ai_coordinator()

        prompt = f"""
Analyze this Job Description and return a complete JSON object:

--- JOB DESCRIPTION ---
{cleaned_text[:10000]}
--- END JOB DESCRIPTION ---

Return JSON formatted as:
{{
  "job_title": "Senior Backend Engineer",
  "seniority": "Senior",
  "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
  "preferred_skills": ["Kubernetes", "Redis", "Kafka", "GraphQL"],
  "minimum_experience": 5.0,
  "education": "Bachelor's degree in Computer Science or equivalent practical experience",
  "certifications": ["AWS Certified Solutions Architect Associate (Preferred)"],
  "responsibilities": [
    "Design and scale microservices handling millions of requests daily",
    "Architect database models and optimize query execution plans",
    "Lead technical reviews and mentor junior engineering staff"
  ],
  "technologies": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS", "Redis"],
  "domain": "Enterprise Cloud SaaS",
  "location": "San Francisco, CA / Remote",
  "work_mode": "Hybrid",
  "must_have": [
    "5+ years of production Python development",
    "Hands-on expertise with relational databases (PostgreSQL/MySQL)",
    "Production experience deploying on AWS or cloud environments"
  ],
  "should_have": [
    "Experience building asynchronous APIs with FastAPI or asyncio",
    "Containerization experience with Docker & Kubernetes"
  ],
  "nice_to_have": [
    "Prior experience with high-throughput streaming (Kafka/RabbitMQ)",
    "Familiarity with Vector databases or GenAI APIs"
  ]
}}
"""

        try:
            result = coordinator.generate_json(prompt, system_instruction=JOB_ANALYSIS_SYSTEM)
            formatted = self._normalize_result(result, cleaned_text)
            self._cache[cache_key] = formatted
            return formatted
        except Exception as e:
            logger.warning(f"AI job description extraction error: {type(e).__name__}. Using rule-based fallback.")
            fallback = self._heuristic_extraction(cleaned_text)
            self._cache[cache_key] = fallback
            return fallback

    def _normalize_result(self, raw: Dict[str, Any], text: str) -> Dict[str, Any]:
        return {
            "job_title": str(raw.get("job_title", "Software Engineer")),
            "seniority": str(raw.get("seniority", "Mid-Level")),
            "required_skills": raw.get("required_skills", []),
            "preferred_skills": raw.get("preferred_skills", []),
            "minimum_experience": float(raw.get("minimum_experience", 3.0) or 3.0),
            "education": str(raw.get("education", "Bachelor's degree in CS or related field")),
            "certifications": raw.get("certifications", []),
            "responsibilities": raw.get("responsibilities", []),
            "technologies": raw.get("technologies", []),
            "domain": str(raw.get("domain", "Technology")),
            "location": str(raw.get("location", "Remote")),
            "work_mode": str(raw.get("work_mode", "Remote")),
            "must_have": raw.get("must_have", raw.get("required_skills", [])),
            "should_have": raw.get("should_have", []),
            "nice_to_have": raw.get("nice_to_have", raw.get("preferred_skills", [])),
            "raw_text": text
        }

    def _empty_result(self) -> Dict[str, Any]:
        return {
            "job_title": "Untitled Role",
            "seniority": "Mid-Level",
            "required_skills": [],
            "preferred_skills": [],
            "minimum_experience": 0.0,
            "education": "",
            "certifications": [],
            "responsibilities": [],
            "technologies": [],
            "domain": "General",
            "location": "Remote",
            "work_mode": "Remote",
            "must_have": [],
            "should_have": [],
            "nice_to_have": [],
            "raw_text": ""
        }

    def _heuristic_extraction(self, text: str) -> Dict[str, Any]:
        first_line = text.split("\n")[0].strip()[:60]
        title = first_line if first_line else "Software Engineer"

        tech_keywords = [
            "Python", "FastAPI", "React", "TypeScript", "JavaScript", "Docker",
            "Kubernetes", "AWS", "Azure", "GCP", "PostgreSQL", "SQL", "Redis",
            "Kafka", "GraphQL", "Java", "Go", "C++"
        ]
        found_skills = [s for s in tech_keywords if re.search(rf"\b{re.escape(s)}\b", text, re.IGNORECASE)]

        return {
            "job_title": title,
            "seniority": "Senior" if "senior" in text.lower() else "Mid-Level",
            "required_skills": found_skills[:5] if found_skills else ["Python", "FastAPI"],
            "preferred_skills": found_skills[5:] if len(found_skills) > 5 else ["Docker", "AWS"],
            "minimum_experience": 3.0,
            "education": "Bachelor's degree or equivalent",
            "certifications": [],
            "responsibilities": ["Design and maintain core platform services"],
            "technologies": found_skills,
            "domain": "Technology",
            "location": "Remote",
            "work_mode": "Remote",
            "must_have": found_skills[:3] if found_skills else ["Python"],
            "should_have": found_skills[3:5] if len(found_skills) > 3 else ["SQL"],
            "nice_to_have": found_skills[5:] if len(found_skills) > 5 else ["Cloud"],
            "raw_text": text
        }


job_analyzer = JobAnalyzer()

def get_job_analyzer() -> JobAnalyzer:
    return job_analyzer
