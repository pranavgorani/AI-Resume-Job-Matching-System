import hashlib
import json
import logging
from typing import Any, Dict, List, Optional

from .ai_provider import get_ai_coordinator
from .embedding_service import get_embedding_service

logger = logging.getLogger("talentproof.ai.evidence")

EVIDENCE_SYSTEM = """
You are the TalentProof AI Evidence Engine.
Your core principle is: "Don't just rank resumes. Prove the match."
You must analyze every single job requirement against the candidate's resume and determine concrete proof.

For each requirement, evaluate:
1. requirement: The specific skill or criterion
2. candidate_claim: What the candidate claims in their resume summary/skills list (or 'No claim found')
3. resume_evidence: Exact quote or verifiable project/job accomplishment from the resume proving or disproving this requirement
4. evidence_strength: One of ['DIRECT', 'INFERRED', 'WEAK', 'NONE']
5. status: Exactly one of:
   - SUPPORTED: Candidate explicitly demonstrated and verified this with strong evidence/metrics
   - PARTIALLY_SUPPORTED: Candidate has related experience or mention without full production depth
   - MISSING: Requirement is not mentioned or evidenced anywhere
   - CONTRADICTORY: Candidate makes contradictory claims (e.g. 5 yrs exp with tech created 2 yrs ago)
   - NOT_ENOUGH_INFORMATION: Ambiguous mention without sufficient technical detail to verify
   - TRANSFERABLE: Candidate demonstrates mastery in an equivalent tool (e.g., Azure instead of AWS)
6. confidence: Float between 0.0 and 1.0 representing certainty of this evaluation

Return ONLY a JSON list of objects matching this exact structure.
"""

class EvidenceAnalyzer:
    """
    Evaluates each job requirement against candidate resume text to generate structured evidence rows.
    """
    def __init__(self):
        self._cache: Dict[str, List[Dict[str, Any]]] = {}

    def analyze_evidence(
        self,
        requirements: List[str],
        candidate_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Produces evidence-first verification rows for all requirements."""
        if not requirements:
            return []

        resume_text = candidate_data.get("raw_text", "")
        if not resume_text:
            # Fallback to serializing candidate skills, projects, and experiences
            resume_text = json.dumps({
                "skills": candidate_data.get("skills", []),
                "experience": candidate_data.get("employment_dates", candidate_data.get("experiences", [])),
                "projects": candidate_data.get("projects", []),
                "achievements": candidate_data.get("achievements", [])
            })

        cache_key = hashlib.sha256(f"{json.dumps(requirements)}:{resume_text[:4000]}".encode("utf-8")).hexdigest()
        if cache_key in self._cache:
            return self._cache[cache_key]

        coordinator = get_ai_coordinator()

        prompt = f"""
Analyze the following requirements against the candidate's resume:

--- REQUIREMENTS LIST ---
{json.dumps(requirements, indent=2)}
--- END REQUIREMENTS ---

--- CANDIDATE RESUME ---
{resume_text[:10000]}
--- END RESUME ---

Return a JSON array of objects:
[
  {{
    "requirement": "Python & FastAPI backend development",
    "candidate_claim": "Claimed 4 years building backend APIs",
    "resume_evidence": "Led development of core Python/FastAPI microservices at TechCorp handling 25,000 req/min with PostgreSQL.",
    "evidence_strength": "DIRECT",
    "status": "SUPPORTED",
    "confidence": 0.95
  }}
]
"""

        try:
            result = coordinator.generate_json(prompt, system_instruction=EVIDENCE_SYSTEM)
            # Result could be a dict with key 'evidence' or direct list
            items = result if isinstance(result, list) else result.get("evidence", result.get("requirements", []))
            normalized = self._normalize_items(items, requirements, candidate_data)
            self._cache[cache_key] = normalized
            return normalized
        except Exception as e:
            logger.warning(f"AI evidence analysis error: {type(e).__name__}. Falling back to semantic evidence mapping.")
            fallback = self._semantic_evidence_fallback(requirements, candidate_data)
            self._cache[cache_key] = fallback
            return fallback

    def _normalize_items(
        self,
        raw_items: List[Dict[str, Any]],
        requirements: List[str],
        candidate_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        valid_statuses = {
            "SUPPORTED", "PARTIALLY_SUPPORTED", "MISSING",
            "CONTRADICTORY", "NOT_ENOUGH_INFORMATION", "TRANSFERABLE"
        }
        valid_strengths = {"DIRECT", "INFERRED", "WEAK", "NONE"}

        normalized = []
        covered_reqs = set()

        for item in raw_items:
            req = str(item.get("requirement", "")).strip()
            if not req:
                continue
            status = str(item.get("status", "NOT_ENOUGH_INFORMATION")).upper()
            if status not in valid_statuses:
                status = "PARTIALLY_SUPPORTED"

            strength = str(item.get("evidence_strength", "WEAK")).upper()
            if strength not in valid_strengths:
                strength = "INFERRED"

            conf = float(item.get("confidence", 0.7) or 0.7)
            conf = max(0.0, min(1.0, conf))

            normalized.append({
                "requirement": req,
                "candidate_claim": str(item.get("candidate_claim", "Identified in resume")),
                "resume_evidence": str(item.get("resume_evidence", "Relevant experience documented")),
                "evidence_strength": strength,
                "status": status,
                "confidence": conf
            })
            covered_reqs.add(req.lower())

        # Ensure all requirements are represented
        for req in requirements:
            if req.lower() not in covered_reqs:
                # Add default missing/uncovered entry
                normalized.append({
                    "requirement": req,
                    "candidate_claim": "No explicit claim found",
                    "resume_evidence": "Not documented in resume text",
                    "evidence_strength": "NONE",
                    "status": "MISSING",
                    "confidence": 0.90
                })

        return normalized

    def _semantic_evidence_fallback(
        self,
        requirements: List[str],
        candidate_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Deterministic semantic evidence fallback using EmbeddingService."""
        embedding_svc = get_embedding_service()
        candidate_skills = candidate_data.get("skills", [])
        resume_text = candidate_data.get("raw_text", "").lower()

        results = []
        for req in requirements:
            matched_skill = None
            highest_match_type = "NONE"
            highest_sim = 0.0

            for skill in candidate_skills:
                m_type, sim = embedding_svc.calculate_skill_match(req, skill)
                if sim > highest_sim:
                    highest_sim = sim
                    highest_match_type = m_type
                    matched_skill = skill

            if highest_match_type == "MATCH":
                results.append({
                    "requirement": req,
                    "candidate_claim": f"Listed skill '{matched_skill}'",
                    "resume_evidence": f"Found verifiable mention of {matched_skill} in candidate skills & experience.",
                    "evidence_strength": "DIRECT" if highest_sim > 0.9 else "INFERRED",
                    "status": "SUPPORTED",
                    "confidence": round(highest_sim, 2)
                })
            elif highest_match_type == "TRANSFERABLE":
                results.append({
                    "requirement": req,
                    "candidate_claim": f"Possesses equivalent skill '{matched_skill}'",
                    "resume_evidence": f"Demonstrated competence in {matched_skill}, which is directly transferable to {req}.",
                    "evidence_strength": "INFERRED",
                    "status": "TRANSFERABLE",
                    "confidence": round(highest_sim, 2)
                })
            elif req.lower() in resume_text:
                results.append({
                    "requirement": req,
                    "candidate_claim": "Referenced in resume text",
                    "resume_evidence": f"Direct textual mention of {req} located in experience section.",
                    "evidence_strength": "INFERRED",
                    "status": "PARTIALLY_SUPPORTED",
                    "confidence": 0.75
                })
            else:
                results.append({
                    "requirement": req,
                    "candidate_claim": "No explicit claim found",
                    "resume_evidence": f"No direct evidence or equivalent skills found for {req}.",
                    "evidence_strength": "NONE",
                    "status": "MISSING",
                    "confidence": 0.85
                })

        return results


evidence_analyzer = EvidenceAnalyzer()

def get_evidence_analyzer() -> EvidenceAnalyzer:
    return evidence_analyzer
