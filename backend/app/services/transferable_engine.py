from typing import Dict, List, Optional, Tuple

TRANSFERABLE_MAP: Dict[str, Dict[str, Tuple[str, str, float]]] = {
    # target_skill: { candidate_skill: (transferability_level, explanation, factor) }
    "aws": {
        "azure": ("HIGH", "Candidate lacks direct AWS evidence but demonstrates strong Azure cloud infrastructure experience that readily transfers.", 0.82),
        "gcp": ("HIGH", "Candidate lacks direct AWS evidence but has deep Google Cloud Platform experience with transferable cloud patterns.", 0.85),
        "cloud computing": ("MEDIUM", "Demonstrates broad cloud architectural competence though specific AWS services require onboarding.", 0.70)
    },
    "azure": {
        "aws": ("HIGH", "Candidate lacks direct Azure evidence but possesses extensive AWS cloud experience with parallel primitives.", 0.85),
        "gcp": ("HIGH", "Candidate possesses strong GCP infrastructure skills that translate directly to Azure services.", 0.80)
    },
    "gcp": {
        "aws": ("HIGH", "Candidate has strong AWS cloud architecture experience with equivalent GCP managed services.", 0.85),
        "azure": ("HIGH", "Candidate demonstrates enterprise Azure skills that translate well to GCP.", 0.80)
    },
    "react": {
        "vue": ("HIGH", "Strong Vue.js reactive component architecture experience translates smoothly to React paradigms.", 0.80),
        "angular": ("MEDIUM", "Comprehensive Angular enterprise SPA experience provides strong foundations for React.", 0.75),
        "svelte": ("HIGH", "Modern reactive component design experience in Svelte transfers directly to React.", 0.80)
    },
    "fastapi": {
        "flask": ("HIGH", "Extensive Python Flask backend development provides immediate familiarity with Python REST microservices.", 0.85),
        "django": ("HIGH", "Deep Django web framework experience translates cleanly to FastAPI async services.", 0.80),
        "express": ("MEDIUM", "Asynchronous HTTP routing and middleware expertise translates conceptually to FastAPI.", 0.70)
    },
    "postgresql": {
        "mysql": ("HIGH", "Strong relational SQL database schema design and querying experience directly transfers.", 0.88),
        "oracle": ("MEDIUM", "Enterprise RDBMS experience provides rigorous relational foundation for PostgreSQL.", 0.80),
        "sqlite": ("MEDIUM", "Relational SQL familiarity, though PostgreSQL concurrency and indexing require brief orientation.", 0.70)
    },
    "docker": {
        "podman": ("HIGH", "OCI container build and deployment expertise translates directly to Docker.", 0.90),
        "kubernetes": ("HIGH", "Advanced Kubernetes container orchestration presupposes strong container fundamentals.", 0.88)
    },
    "kubernetes": {
        "docker": ("MEDIUM", "Strong containerization background provides foundational stepping stone for container orchestration.", 0.65),
        "ecs": ("HIGH", "AWS ECS container cluster management provides transferable orchestration principles.", 0.80)
    },
    "llm apis": {
        "langchain": ("HIGH", "Framework experience with LangChain covers LLM prompting, chaining, and API integration.", 0.90),
        "openai": ("HIGH", "Direct OpenAI API integration experience directly translates to Gemini and modern LLM APIs.", 0.92),
        "nlp": ("MEDIUM", "Classical NLP experience gives theoretical foundation for modern generative AI interfaces.", 0.70),
        "pytorch": ("HIGH", "Hands-on PyTorch deep learning background provides superior architectural understanding of model inference.", 0.85)
    },
    "typescript": {
        "javascript": ("HIGH", "Deep JavaScript mastery allows rapid adoption of TypeScript static typing constructs.", 0.82),
        "java": ("MEDIUM", "Strong statically typed object-oriented foundation facilitates TypeScript adoption.", 0.72),
        "c#": ("MEDIUM", "C# strong typing and modern language constructs transfer cleanly to TypeScript.", 0.75)
    }
}

def find_transferable_match(target_req: str, candidate_skills: List[str]) -> Optional[Dict[str, any]]:
    """
    Checks if a candidate skill can transfer to the target job requirement.
    """
    target_clean = target_req.strip().lower()
    
    # Check exact synonym / direct equivalence
    for req_key, transfers in TRANSFERABLE_MAP.items():
        if req_key in target_clean or target_clean in req_key:
            for skill in candidate_skills:
                skill_clean = skill.strip().lower()
                for alt_key, (level, explanation, factor) in transfers.items():
                    if alt_key in skill_clean or skill_clean in alt_key:
                        return {
                            "target_requirement": target_req,
                            "alternative_skill": skill,
                            "transferability_level": level,
                            "explanation": explanation,
                            "transfer_factor": factor
                        }
    return None
