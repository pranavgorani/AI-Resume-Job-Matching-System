import hashlib
import json
import logging
import re
from typing import Any, Dict, List, Optional

from .ai_provider import get_ai_coordinator

logger = logging.getLogger("talentproof.ai.resume")

RESUME_EXTRACTION_SYSTEM = """
You are an expert ATS and candidate intelligence system.
Analyze the provided resume text and extract comprehensive structured data in valid JSON format.
Ensure you strictly extract the following fields:
1. name (string)
2. email (string)
3. phone (string)
4. location (string)
5. education (list of objects with degree, institution, field_of_study, graduation_year)
6. companies (list of string company names)
7. job_titles (list of string past/current roles)
8. employment_dates (list of objects with company, title, start_date, end_date, is_current, duration_months)
9. years_of_experience (numeric float)
10. skills (list of string technical and functional skills)
11. certifications (list of strings or objects)
12. projects (list of objects with title, description, technologies, metrics)
13. technologies (list of specific tools, libraries, frameworks, languages)
14. achievements (list of quantifiable bullet points with numbers and metrics)

Return ONLY valid JSON matching this schema.
"""

class ResumeAnalyzer:
    """
    Analyzes resume text using Gemini (primary) with Hugging Face fallback and caching.
    """
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}

    def analyze(self, resume_text: str) -> Dict[str, Any]:
        """Extract all 14 structured fields from resume text."""
        cleaned_text = resume_text.strip()
        if not cleaned_text:
            return self._empty_result()

        cache_key = hashlib.sha256(cleaned_text.encode("utf-8")).hexdigest()
        if cache_key in self._cache:
            return self._cache[cache_key]

        coordinator = get_ai_coordinator()

        prompt = f"""
Extract candidate information from the following resume text:

--- RESUME TEXT ---
{cleaned_text[:12000]}
--- END RESUME TEXT ---

Return a JSON object with:
{{
  "name": "Candidate Full Name",
  "email": "candidate@example.com",
  "phone": "+1-xxx-xxx-xxxx",
  "location": "City, Country/State",
  "education": [
    {{"degree": "B.S. Computer Science", "institution": "University Name", "graduation_year": 2020}}
  ],
  "companies": ["Company A", "Company B"],
  "job_titles": ["Senior Backend Engineer", "Software Engineer"],
  "employment_dates": [
    {{"company": "Company A", "title": "Senior Engineer", "start_date": "2022-01", "end_date": "Present", "is_current": true, "duration_months": 24}}
  ],
  "years_of_experience": 5.0,
  "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
  "certifications": ["AWS Certified Solutions Architect"],
  "projects": [
    {{"title": "Distributed Task Queue", "description": "Built resilient queue handling 100k events/sec", "technologies": ["Python", "Redis", "Kafka"], "metrics": "Reduced latency by 45%"}}
  ],
  "technologies": ["Python", "Docker", "PostgreSQL", "Redis", "AWS", "Git"],
  "achievements": [
    "Scaled platform infrastructure from 10k to 500k DAU with 99.99% uptime",
    "Reduced API response latency by 45% through Redis caching and query indexing"
  ]
}}
"""

        import concurrent.futures
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        try:
            future = executor.submit(coordinator.generate_json, prompt, RESUME_EXTRACTION_SYSTEM)
            result = future.result(timeout=2.5)
            executor.shutdown(wait=False, cancel_futures=True)

            # Ensure all required keys exist
            formatted = self._normalize_result(result, cleaned_text)
            self._cache[cache_key] = formatted
            return formatted
        except Exception as e:
            executor.shutdown(wait=False, cancel_futures=True)
            logger.info(f"AI resume extraction skipped or timed out ({type(e).__name__}). Using fast deterministic extraction.")
            # Heuristic extraction fallback
            fallback = self._heuristic_extraction(cleaned_text)
            self._cache[cache_key] = fallback
            return fallback

    def _normalize_result(self, raw: Dict[str, Any], text: str) -> Dict[str, Any]:
        """Ensures all 14 fields are cleanly typed and populated."""
        if not isinstance(raw, dict):
            return self._heuristic_extraction(text)
        return {
            "name": str(raw.get("name") or "Unknown Candidate"),
            "email": str(raw.get("email") or ""),
            "phone": str(raw.get("phone") or ""),
            "location": str(raw.get("location") or ""),
            "education": raw.get("education") or [],
            "companies": raw.get("companies") or [],
            "job_titles": raw.get("job_titles") or [],
            "employment_dates": raw.get("employment_dates") or [],
            "years_of_experience": float(raw.get("years_of_experience") or 3.0),
            "skills": raw.get("skills") or [],
            "certifications": raw.get("certifications") or [],
            "projects": raw.get("projects") or [],
            "technologies": raw.get("technologies") or [],
            "achievements": raw.get("achievements") or [],
            "raw_text": text
        }

    def _empty_result(self) -> Dict[str, Any]:
        return {
            "name": "Unknown",
            "email": "",
            "phone": "",
            "location": "",
            "education": [],
            "companies": [],
            "job_titles": [],
            "employment_dates": [],
            "years_of_experience": 0.0,
            "skills": [],
            "certifications": [],
            "projects": [],
            "technologies": [],
            "achievements": [],
            "raw_text": ""
        }

    def _heuristic_extraction(self, text: str) -> Dict[str, Any]:
        """Regex and rule-based fallback when AI services are unreachable."""
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
        phone_match = re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)

        first_line = text.split("\n")[0].strip()[:50]
        name = first_line if first_line and not any(k in first_line.lower() for k in ["resume", "curriculum", "page"]) else "Extracted Candidate"

        # Common tech skills
        common_skills = [
            "Python", "FastAPI", "Django", "Flask", "JavaScript", "TypeScript", "React",
            "Node.js", "Docker", "Kubernetes", "AWS", "Azure", "GCP", "PostgreSQL",
            "MySQL", "MongoDB", "Redis", "Kafka", "Git", "CI/CD", "GraphQL", "REST"
        ]
        found_skills = [s for s in common_skills if re.search(rf"\b{re.escape(s)}\b", text, re.IGNORECASE)]

        return {
            "name": name,
            "email": email_match.group(0) if email_match else "",
            "phone": phone_match.group(0) if phone_match else "",
            "location": "",
            "education": [],
            "companies": [],
            "job_titles": [],
            "employment_dates": [],
            "years_of_experience": 3.0,
            "skills": found_skills,
            "certifications": [],
            "projects": [],
            "technologies": found_skills,
            "achievements": [],
            "raw_text": text
        }


resume_analyzer = ResumeAnalyzer()

def get_resume_analyzer() -> ResumeAnalyzer:
    return resume_analyzer
