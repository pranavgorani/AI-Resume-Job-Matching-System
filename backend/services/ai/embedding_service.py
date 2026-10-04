import hashlib
import math
import re
from typing import Dict, List, Optional, Tuple, Union

# Known Transferable Skill Graph for high-precision semantic matching
TRANSFERABLE_MAPPINGS = {
    "aws": {"azure": 0.85, "gcp": 0.88, "google cloud": 0.88, "cloud computing": 0.90},
    "azure": {"aws": 0.85, "gcp": 0.85, "cloud computing": 0.90},
    "gcp": {"aws": 0.88, "azure": 0.85, "cloud computing": 0.90},
    "react": {"vue": 0.80, "angular": 0.75, "svelte": 0.82, "next.js": 0.95},
    "vue": {"react": 0.80, "angular": 0.72},
    "angular": {"react": 0.75, "vue": 0.72},
    "postgresql": {"mysql": 0.88, "sql server": 0.82, "oracle": 0.80, "sqlite": 0.85},
    "mysql": {"postgresql": 0.88, "mariadb": 0.98},
    "fastapi": {"flask": 0.85, "django": 0.80, "express": 0.70},
    "flask": {"fastapi": 0.85, "django": 0.82},
    "django": {"fastapi": 0.80, "flask": 0.82, "rails": 0.75, "spring boot": 0.70},
    "docker": {"podman": 0.92, "containerization": 0.95, "kubernetes": 0.85},
    "kubernetes": {"docker swarm": 0.80, "nomad": 0.75, "helm": 0.88},
    "pytorch": {"tensorflow": 0.86, "keras": 0.84, "jax": 0.82},
    "tensorflow": {"pytorch": 0.86, "keras": 0.90},
    "kafka": {"rabbitmq": 0.82, "sqs": 0.80, "event-driven": 0.90},
    "rabbitmq": {"kafka": 0.82, "sqs": 0.85},
}

# Related skills that are NOT interchangeable matches (e.g., Python vs Java)
RELATED_ONLY_MAPPINGS = {
    ("python", "java"): 0.55,
    ("java", "c#"): 0.70,
    ("c++", "rust"): 0.65,
    ("javascript", "python"): 0.50,
}

def generate_deterministic_embedding(text: str, dim: int = 768) -> List[float]:
    """
    Generates a deterministic 768-dimensional normalized pseudo-vector based on character
    and token hashes. Guarantees consistent vector math even offline.
    """
    if not text:
        return [0.0] * dim

    vec = [0.0] * dim
    words = re.findall(r"\w+", text.lower())
    if not words:
        words = [text.lower()]

    for i, word in enumerate(words):
        h = int(hashlib.md5(f"{word}:{i}".encode("utf-8")).hexdigest(), 16)
        idx = h % dim
        sign = 1.0 if ((h >> 4) % 2 == 0) else -1.0
        vec[idx] += sign * (1.0 + (len(word) % 5) * 0.2)

    # Normalize
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 0:
        vec = [x / norm for x in vec]
    return vec


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculates cosine similarity between two vectors."""
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return max(0.0, min(1.0, dot / (norm1 * norm2)))


class EmbeddingService:
    """
    Manages vector embeddings generation, semantic matching, and caching.
    """
    def __init__(self):
        self._cache: Dict[str, List[float]] = {}

    def get_embedding(self, text: str) -> List[float]:
        """Fetch or generate embedding vector for given text."""
        cleaned = text.strip()
        if not cleaned:
            return [0.0] * 768

        if cleaned in self._cache:
            return self._cache[cleaned]

        try:
            from .ai_provider import get_ai_coordinator
            coordinator = get_ai_coordinator()
            embeddings = coordinator.generate_embeddings(cleaned)
            if embeddings and len(embeddings) > 0 and len(embeddings[0]) > 0:
                vec = embeddings[0]
                self._cache[cleaned] = vec
                return vec
        except Exception:
            pass

        # Offline fallback
        vec = generate_deterministic_embedding(cleaned)
        self._cache[cleaned] = vec
        return vec

    def calculate_skill_match(self, required_skill: str, candidate_skill: str) -> Tuple[str, float]:
        """
        Classifies skill match into:
        - MATCH: direct match (e.g., AWS -> AWS)
        - TRANSFERABLE: transferable skill (e.g., AWS -> Azure)
        - RELATED: related technology but not substitute (e.g., Python -> Java)
        - NONE: unrelated
        """
        req = required_skill.strip().lower()
        cand = candidate_skill.strip().lower()

        # Direct string equality or substring match
        if req == cand:
            return ("MATCH", 1.0)
        if req in cand or cand in req:
            return ("MATCH", 0.95)

        # Check explicit transferable graph
        if req in TRANSFERABLE_MAPPINGS and cand in TRANSFERABLE_MAPPINGS[req]:
            sim = TRANSFERABLE_MAPPINGS[req][cand]
            return ("TRANSFERABLE", sim)
        if cand in TRANSFERABLE_MAPPINGS and req in TRANSFERABLE_MAPPINGS[cand]:
            sim = TRANSFERABLE_MAPPINGS[cand][req]
            return ("TRANSFERABLE", sim)

        # Check related pairs
        if (req, cand) in RELATED_ONLY_MAPPINGS:
            return ("RELATED", RELATED_ONLY_MAPPINGS[(req, cand)])
        if (cand, req) in RELATED_ONLY_MAPPINGS:
            return ("RELATED", RELATED_ONLY_MAPPINGS[(cand, req)])

        # Semantic embedding similarity
        v1 = self.get_embedding(req)
        v2 = self.get_embedding(cand)
        sim = cosine_similarity(v1, v2)

        if sim >= 0.88:
            return ("MATCH", sim)
        elif sim >= 0.72:
            return ("TRANSFERABLE", sim)
        elif sim >= 0.50:
            return ("RELATED", sim)
        else:
            return ("NONE", sim)


embedding_service = EmbeddingService()

def get_embedding_service() -> EmbeddingService:
    return embedding_service
