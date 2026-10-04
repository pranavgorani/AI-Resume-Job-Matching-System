import hashlib
import json
import logging
from typing import Any, Dict, List, Optional

from .ai_provider import get_ai_coordinator

logger = logging.getLogger("talentproof.ai.interview")

INTERVIEW_SYSTEM = """
You are the TalentProof AI Interview Intelligence Engine.
Your role is to formulate deep, targeted interview questions derived strictly from candidate gaps, evidence ambiguities, and role requirements.

You must categorize questions into:
- technical: Probing technical depth on claimed expertise or critical job requirements
- experience: Inquiring about scale, team collaboration, and real-world trade-offs
- project: Drilling into architecture, metrics, and implementation details of cited projects
- behavioral: Assessing conflict resolution, ownership, and handling ambiguous deadlines
- verification: Tactfully verifying weak evidence, missing skills, or detected inconsistencies

For every question return:
- question (string)
- category (string: technical, experience, project, behavioral, verification)
- target (string: the skill, gap, or inconsistency being targeted)
- rationale (string: why this specific question is critical for this candidate)
- evaluation_criteria (string: what positive and negative signals the interviewer should listen for)

Return ONLY valid JSON array.
"""

class InterviewGenerator:
    """
    Generates tailored interview questions targeting candidate evidence gaps, contradictions, and claimed strengths.
    """
    def __init__(self):
        self._cache: Dict[str, List[Dict[str, Any]]] = {}

    def generate_questions(
        self,
        candidate_data: Dict[str, Any],
        job_data: Dict[str, Any],
        evidence_rows: Optional[List[Dict[str, Any]]] = None,
        contradictions: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """Generates 5-10 tailored questions covering all 5 categories."""
        candidate_name = candidate_data.get("name", "Candidate")
        cache_key = hashlib.sha256(f"{candidate_name}:{job_data.get('job_title', '')}".encode("utf-8")).hexdigest()
        if cache_key in self._cache:
            return self._cache[cache_key]

        coordinator = get_ai_coordinator()

        # Gather target gaps from evidence
        missing_skills = []
        weak_evidence = []
        if evidence_rows:
            for row in evidence_rows:
                st = row.get("status", "")
                if st in ("MISSING", "NOT_ENOUGH_INFORMATION"):
                    missing_skills.append(row.get("requirement", ""))
                elif st in ("PARTIALLY_SUPPORTED", "TRANSFERABLE") or row.get("evidence_strength") == "WEAK":
                    weak_evidence.append(row.get("requirement", ""))

        prompt = f"""
Generate targeted interview questions for:
Candidate: {candidate_name}
Role: {job_data.get('job_title', 'Software Engineer')} (Seniority: {job_data.get('seniority', 'Senior')})

Job Requirements: {json.dumps(job_data.get('required_skills', [])[:8])}
Missing or Unverified Skills: {json.dumps(missing_skills[:5])}
Areas with Weak/Transferable Evidence: {json.dumps(weak_evidence[:5])}
Potential Verification Flags: {json.dumps([c.get('title') for c in (contradictions or [])][:3])}
Candidate Projects: {json.dumps([p.get('title') for p in candidate_data.get('projects', [])][:3])}

Generate 5-8 targeted interview questions distributed across the 5 categories (technical, experience, project, behavioral, verification).

Return JSON array:
[
  {{
    "question": "In your resume, you mention building a distributed task queue with Redis and Kafka. How did you handle partition rebalancing and message ordering under peak loads?",
    "category": "project",
    "target": "Distributed Task Queue",
    "rationale": "Verify hands-on architectural depth for claimed project metrics.",
    "evaluation_criteria": "Look for specific mentions of Kafka consumer group offsets, idempotency keys, and dead-letter queues."
  }}
]
"""

        try:
            result = coordinator.generate_json(prompt, system_instruction=INTERVIEW_SYSTEM)
            items = result if isinstance(result, list) else result.get("questions", [])
            normalized = self._normalize_questions(items)
            self._cache[cache_key] = normalized
            return normalized
        except Exception as e:
            logger.warning(f"AI interview generation error: {type(e).__name__}. Generating deterministic questions.")
            fallback = self._deterministic_questions(candidate_data, job_data, missing_skills)
            self._cache[cache_key] = fallback
            return fallback

    def _normalize_questions(self, raw_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        valid_cats = {"technical", "experience", "project", "behavioral", "verification"}
        normalized = []
        for it in raw_items:
            cat = str(it.get("category", "technical")).lower()
            if cat not in valid_cats:
                cat = "technical"

            normalized.append({
                "question": str(it.get("question", "")),
                "category": cat,
                "target": str(it.get("target", "Role Alignment")),
                "rationale": str(it.get("rationale", "Evaluate role competency")),
                "evaluation_criteria": str(it.get("evaluation_criteria", "Assess technical accuracy and problem-solving clarity."))
            })
        return normalized

    def _deterministic_questions(
        self,
        candidate_data: Dict[str, Any],
        job_data: Dict[str, Any],
        missing_skills: List[str]
    ) -> List[Dict[str, Any]]:
        title = job_data.get("job_title", "Software Engineer")
        target_gap = missing_skills[0] if missing_skills else "Cloud Architecture"

        return [
            {
                "question": f"How have you designed and scaled backend architectures to handle increased concurrency for {title} roles?",
                "category": "technical",
                "target": "System Concurrency",
                "rationale": "Assess core technical depth and architectural maturity.",
                "evaluation_criteria": "Listen for discussion of caching layers, connection pooling, and horizontal scaling strategies."
            },
            {
                "question": f"Our role prioritizes {target_gap}, which was not explicitly detailed on your resume. What hands-on experience or equivalent tools have you used?",
                "category": "verification",
                "target": target_gap,
                "rationale": f"Verify candidate adaptability and self-reported skills in {target_gap}.",
                "evaluation_criteria": "Candidate should demonstrate strong foundational concepts and rapid learning agility."
            },
            {
                "question": "Can you walk through your most technically complex project, specifically the key trade-offs you made when selecting your tech stack?",
                "category": "project",
                "target": "Project Architecture",
                "rationale": "Differentiate copy-paste tutorials from deep production engineering.",
                "evaluation_criteria": "Look for honest retrospective trade-offs (e.g. why SQL vs NoSQL was chosen)."
            },
            {
                "question": "Tell me about a time you identified a critical production bottleneck or outage. How did you triage, resolve, and prevent recurrence?",
                "category": "experience",
                "target": "Incident Management",
                "rationale": "Test operational resilience and post-mortem accountability.",
                "evaluation_criteria": "Look for systematic root-cause analysis rather than ad-hoc band-aids."
            },
            {
                "question": "Describe a scenario where you strongly disagreed with an architectural decision proposed by a peer or manager. How did you handle it?",
                "category": "behavioral",
                "target": "Technical Collaboration",
                "rationale": "Evaluate communication, ego, and data-driven debate.",
                "evaluation_criteria": "Constructive dissent backed by data, combined with commitment once a decision was finalized."
            }
        ]


interview_generator = InterviewGenerator()

def get_interview_generator() -> InterviewGenerator:
    return interview_generator
