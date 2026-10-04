import hashlib
import json
import logging
import re
from typing import Any, Dict, List

from .ai_provider import get_ai_coordinator

logger = logging.getLogger("talentproof.ai.contradiction")

STANDARD_VERIFICATION_NOTICE = "Potential inconsistency detected. Recruiter verification recommended."

CONTRADICTION_SYSTEM = f"""
You are the TalentProof AI Contradiction and Integrity Auditor.
Your responsibility is to analyze candidate resumes for chronological, credential, and skill inconsistencies.

CRITICAL TONE DIRECTIVE:
Never accuse or defame the candidate. You are an objective auditor assisting recruiters.
Every single identified inconsistency MUST conclude with or state:
"{STANDARD_VERIFICATION_NOTICE}"

Look for:
1. Inconsistent years of experience (e.g., claiming 10 years experience when first role was in 2021)
2. Overlapping employment dates (e.g., full-time on-site overlapping roles at two companies)
3. Skill claims without evidence (e.g., listing Kubernetes as an expert skill, but zero projects or jobs mention containerization)
4. Inconsistent job titles (e.g., jumping from intern directly to VP in 3 months)
5. Impossible timelines (e.g., technology claimed before its public release date, or college graduation dates conflicting with employment)
6. Conflicting education information

Return ONLY a JSON list of contradiction items with:
- type: string (TIMELINE_OVERLAP, SKILL_WITHOUT_EVIDENCE, INCONSISTENT_EXPERIENCE, TITLE_INCONSISTENCY, IMPOSSIBLE_TIMELINE, EDUCATION_CONFLICT)
- severity: string (LOW, MEDIUM, HIGH)
- title: string
- description: string (Must contain '{STANDARD_VERIFICATION_NOTICE}')
- recommendation: string for the recruiter
"""

class ContradictionDetector:
    """
    Detects chronological, credential, and evidence inconsistencies in resumes.
    Always maintains professional, non-accusatory tone.
    """
    def __init__(self):
        self._cache: Dict[str, List[Dict[str, Any]]] = {}

    def detect_contradictions(self, candidate_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Audits candidate data for potential inconsistencies."""
        resume_text = candidate_data.get("raw_text", "")
        if not resume_text:
            resume_text = json.dumps(candidate_data)

        cache_key = hashlib.sha256(resume_text[:4000].encode("utf-8")).hexdigest()
        if cache_key in self._cache:
            return self._cache[cache_key]

        coordinator = get_ai_coordinator()

        prompt = f"""
Audit the following candidate information for discrepancies:

--- CANDIDATE DATA ---
{resume_text[:10000]}
--- END CANDIDATE DATA ---

Return JSON array:
[
  {{
    "type": "TIMELINE_OVERLAP",
    "severity": "MEDIUM",
    "title": "Concurrent Full-Time Employment",
    "description": "Employment dates for Company A and Company B show an overlap of 6 months. {STANDARD_VERIFICATION_NOTICE}",
    "recommendation": "Clarify during screening if one of the roles was advisory or part-time contract."
  }}
]
"""

        try:
            result = coordinator.generate_json(prompt, system_instruction=CONTRADICTION_SYSTEM)
            items = result if isinstance(result, list) else result.get("contradictions", [])
            normalized = self._normalize_contradictions(items)
            self._cache[cache_key] = normalized
            return normalized
        except Exception as e:
            logger.warning(f"AI contradiction detection error: {type(e).__name__}. Running rule-based auditor.")
            fallback = self._rule_based_audit(candidate_data)
            self._cache[cache_key] = fallback
            return fallback

    def _normalize_contradictions(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        normalized = []
        for it in items:
            desc = str(it.get("description", ""))
            if STANDARD_VERIFICATION_NOTICE not in desc:
                desc = f"{desc} {STANDARD_VERIFICATION_NOTICE}".strip()

            normalized.append({
                "type": str(it.get("type", "VERIFICATION_FLAG")),
                "severity": str(it.get("severity", "LOW")).upper(),
                "title": str(it.get("title", "Integrity Flag")),
                "description": desc,
                "recommendation": str(it.get("recommendation", f"Recruiter review suggested. {STANDARD_VERIFICATION_NOTICE}"))
            })
        return normalized

    def _rule_based_audit(self, candidate: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Audits dates and skill claims algorithmically."""
        flags = []
        employment = candidate.get("employment_dates", candidate.get("experiences", []))

        # Check for overlapping employment dates
        if len(employment) >= 2:
            try:
                for i in range(len(employment) - 1):
                    role1 = employment[i]
                    role2 = employment[i + 1]
                    s1 = str(role1.get("start_date", ""))
                    e1 = str(role1.get("end_date", ""))
                    s2 = str(role2.get("start_date", ""))
                    if s1 and s2 and s1[:4] == s2[:4] and "present" in e1.lower() and "present" in str(role2.get("end_date", "")).lower():
                        flags.append({
                            "type": "TIMELINE_OVERLAP",
                            "severity": "MEDIUM",
                            "title": "Concurrent Active Positions",
                            "description": f"Overlapping concurrent active positions listed for {role1.get('company', 'Role 1')} and {role2.get('company', 'Role 2')}. {STANDARD_VERIFICATION_NOTICE}",
                            "recommendation": "Confirm whether the second role was freelance or concurrent consulting."
                        })
            except Exception:
                pass

        # Check for claimed skills with zero project or experience evidence
        skills = candidate.get("skills", [])
        text = candidate.get("raw_text", "").lower()
        unsubstantiated = []
        for s in skills:
            # If skill is listed, check if it's only mentioned in the skills block (appears only once in text)
            count = len(re.findall(rf"\b{re.escape(s.lower())}\b", text))
            if count <= 1 and len(s) > 3:
                unsubstantiated.append(s)

        if len(unsubstantiated) >= 3:
            flags.append({
                "type": "SKILL_WITHOUT_EVIDENCE",
                "severity": "LOW",
                "title": "Skills Claimed Without Contextual Evidence",
                "description": f"Skills {', '.join(unsubstantiated[:3])} appear in the skills summary but lack project or work history substantiation. {STANDARD_VERIFICATION_NOTICE}",
                "recommendation": f"Probe candidate's practical production experience in {unsubstantiated[0]} during technical round."
            })

        return flags


contradiction_detector = ContradictionDetector()

def get_contradiction_detector() -> ContradictionDetector:
    return contradiction_detector
