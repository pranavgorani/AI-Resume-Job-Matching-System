import os
import pytest
from services.ai.ai_provider import get_ai_coordinator
from services.ai.gemini_service import GeminiProvider
from services.ai.huggingface_service import HuggingFaceProvider
from services.ai.embedding_service import get_embedding_service, cosine_similarity
from services.ai.resume_analyzer import get_resume_analyzer
from services.ai.job_analyzer import get_job_analyzer
from services.ai.evidence_analyzer import get_evidence_analyzer
from services.ai.contradiction_detector import get_contradiction_detector, STANDARD_VERIFICATION_NOTICE
from services.ai.interview_generator import get_interview_generator
from services.supabase_service import get_supabase_service

def test_environment_variables_configured():
    """Verify secrets are loaded properly from environment."""
    assert os.getenv("GEMINI_API_KEY") is not None
    assert len(os.getenv("GEMINI_API_KEY", "")) > 10
    assert os.getenv("HF_TOKEN") is not None
    assert len(os.getenv("HF_TOKEN", "")) > 5
    assert os.getenv("SUPABASE_URL") is not None
    assert "supabase.co" in os.getenv("SUPABASE_URL", "")

def test_gemini_provider_live():
    """Verify GeminiProvider initializes and generates text."""
    provider = GeminiProvider()
    assert provider.is_available() is True
    res = provider.generate_text("Reply with exactly the word SUCCESS", temperature=0.0)
    assert res is not None
    assert "SUCCESS" in res.upper()

def test_huggingface_provider_configured():
    """Verify HuggingFaceProvider initializes with token."""
    provider = HuggingFaceProvider()
    assert provider.is_available() is True
    assert provider.provider_name == "huggingface"

def test_supabase_service_configured():
    """Verify SupabaseService initializes and can handle uploads."""
    svc = get_supabase_service()
    assert svc.is_configured is True
    # Test uploading a small sample resume PDF
    upload_res = svc.upload_resume_pdf(b"%PDF-1.4 sample resume content", "test_resume.pdf")
    assert upload_res is not None
    assert "storage_path" in upload_res
    assert "file_url" in upload_res

def test_embedding_service_semantic_distinctions():
    """
    Verify semantic matching:
    - AWS -> AWS = MATCH
    - AWS -> Azure = TRANSFERABLE
    - Python -> Java = RELATED (not MATCH)
    """
    svc = get_embedding_service()
    
    # 1. Direct match
    match_type, sim = svc.calculate_skill_match("AWS", "AWS")
    assert match_type == "MATCH"
    assert sim >= 0.95

    # 2. Transferable skill (AWS -> Azure)
    match_type, sim = svc.calculate_skill_match("AWS", "Azure")
    assert match_type == "TRANSFERABLE"
    assert sim >= 0.70

    # 3. Related skill but not identical substitute (Python -> Java)
    match_type, sim = svc.calculate_skill_match("Python", "Java")
    assert match_type in ("RELATED", "NONE")
    assert match_type != "MATCH"

def test_resume_analyzer_14_fields():
    """Verify ResumeAnalyzer extracts all 14 structured fields."""
    analyzer = get_resume_analyzer()
    sample_text = """
    Alex Rivera
    alex.rivera@example.com | (555) 234-5678 | San Francisco, CA
    
    Experience:
    TechCorp - Senior Backend Engineer (2021 - Present)
    - Architected Python and FastAPI microservices handling 100k requests/sec.
    - Optimized PostgreSQL database schema and queries.
    
    Skills: Python, FastAPI, Docker, Kubernetes, AWS, PostgreSQL, Redis.
    Education: B.S. Computer Science, University of California, Berkeley (2020).
    Certifications: AWS Certified Solutions Architect.
    Projects: Distributed Task Queue - asynchronous workers processing 50k jobs/sec with Kafka.
    """
    res = analyzer.analyze(sample_text)
    
    # Check 14 fields
    required_fields = [
        "name", "email", "phone", "location", "education", "companies",
        "job_titles", "employment_dates", "years_of_experience", "skills",
        "certifications", "projects", "technologies", "achievements"
    ]
    for field in required_fields:
        assert field in res, f"Field '{field}' missing from ResumeAnalyzer output"

    assert "Alex" in res["name"] or res["name"] != "Unknown"
    assert len(res["skills"]) > 0

def test_job_analyzer_tiered_requirements():
    """Verify JobAnalyzer extracts MUST_HAVE, SHOULD_HAVE, NICE_TO_HAVE."""
    analyzer = get_job_analyzer()
    sample_jd = """
    Staff Machine Learning Engineer
    San Francisco, CA / Remote
    
    Requirements:
    - 6+ years experience in Python and PyTorch
    - Deep expertise in LLMs and Transformer architectures
    - Bachelor's in CS or equivalent
    
    Preferred:
    - Kubernetes and Distributed GPU training experience
    - Prior work with Triton or vLLM
    """
    res = analyzer.analyze(sample_jd)
    assert res["job_title"] is not None
    assert "must_have" in res
    assert "should_have" in res
    assert "nice_to_have" in res
    assert res["minimum_experience"] >= 3.0

def test_evidence_analyzer_verification():
    """Verify EvidenceAnalyzer assigns statuses and evidence strengths."""
    analyzer = get_evidence_analyzer()
    reqs = ["Python backend development", "AWS Cloud Architecture"]
    candidate_data = {
        "name": "Sarah Connor",
        "skills": ["Python", "Azure", "Docker"],
        "raw_text": "Built Python APIs with FastAPI. Hosted cloud workloads on Azure."
    }
    evidence_rows = analyzer.analyze_evidence(reqs, candidate_data)
    assert len(evidence_rows) == 2
    
    for row in evidence_rows:
        assert "requirement" in row
        assert "candidate_claim" in row
        assert "resume_evidence" in row
        assert "evidence_strength" in row
        assert "status" in row
        assert "confidence" in row
        assert row["status"] in [
            "SUPPORTED", "PARTIALLY_SUPPORTED", "MISSING",
            "CONTRADICTORY", "NOT_ENOUGH_INFORMATION", "TRANSFERABLE"
        ]

def test_contradiction_detector_mandatory_phrase():
    """Verify ContradictionDetector strictly uses the mandatory non-accusatory phrase."""
    detector = get_contradiction_detector()
    candidate_data = {
        "name": "Jordan Lee",
        "skills": ["Quantum Computing", "Rust", "Haskell", "Fortran"],
        "employment_dates": [
            {"company": "Alpha Corp", "start_date": "2022-01", "end_date": "Present"},
            {"company": "Beta Corp", "start_date": "2022-01", "end_date": "Present"}
        ],
        "raw_text": "Jordan Lee. Skills: Quantum Computing, Rust, Haskell, Fortran. Worked at Alpha Corp (2022 - Present) and Beta Corp (2022 - Present)."
    }
    flags = detector.detect_contradictions(candidate_data)
    for flag in flags:
        assert STANDARD_VERIFICATION_NOTICE in flag["description"] or STANDARD_VERIFICATION_NOTICE in flag["recommendation"]

def test_interview_generator_categories():
    """Verify InterviewGenerator covers question categories."""
    generator = get_interview_generator()
    candidate_data = {
        "name": "Morgan Davis",
        "skills": ["Python", "Django"],
        "projects": [{"title": "High-Throughput Ingestion"}]
    }
    job_data = {
        "job_title": "Senior Backend Engineer",
        "seniority": "Senior",
        "required_skills": ["Python", "FastAPI", "Kubernetes"]
    }
    questions = generator.generate_questions(candidate_data, job_data)
    assert len(questions) >= 4
    categories = {q["category"].lower() for q in questions}
    valid_categories = {"technical", "experience", "project", "behavioral", "verification"}
    assert len(categories.intersection(valid_categories)) >= 2
