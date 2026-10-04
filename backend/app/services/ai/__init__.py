# Re-export from services.ai so both app.services.ai and services.ai work seamlessly
import sys
from pathlib import Path

# Add backend directory to sys.path if not present
backend_dir = str(Path(__file__).resolve().parent.parent.parent.parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from services.ai import (
    AIProvider,
    GeminiProvider,
    HuggingFaceProvider,
    ResilientAICoordinator,
    get_ai_coordinator,
    EmbeddingService,
    get_embedding_service,
    cosine_similarity,
    ResumeAnalyzer,
    get_resume_analyzer,
    JobAnalyzer,
    get_job_analyzer,
    EvidenceAnalyzer,
    get_evidence_analyzer,
    ContradictionDetector,
    get_contradiction_detector,
    InterviewGenerator,
    get_interview_generator,
)

__all__ = [
    "AIProvider",
    "GeminiProvider",
    "HuggingFaceProvider",
    "ResilientAICoordinator",
    "get_ai_coordinator",
    "EmbeddingService",
    "get_embedding_service",
    "cosine_similarity",
    "ResumeAnalyzer",
    "get_resume_analyzer",
    "JobAnalyzer",
    "get_job_analyzer",
    "EvidenceAnalyzer",
    "get_evidence_analyzer",
    "ContradictionDetector",
    "get_contradiction_detector",
    "InterviewGenerator",
    "get_interview_generator",
]
