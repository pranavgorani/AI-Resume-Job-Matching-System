import pytest
from app.services.jd_intelligence import analyze_job_description
from app.services.resume_intelligence import extract_resume_data
from app.services.transferable_engine import find_transferable_match
from app.services.contradiction_detector import verify_claims_and_detect_contradictions
from app.services.evidence_engine import build_evidence_graph
from app.services.scoring_engine import calculate_candidate_scores
from app.services.why_not_engine import generate_why_not_analysis

def test_jd_intelligence_extraction():
    sample_jd = """
    We need a Senior Full Stack AI Engineer with 4+ years of experience.
    Must have Python, FastAPI, React, and PostgreSQL.
    Docker and AWS are should haves.
    Nice to have Redis and Tailwind.
    """
    res = analyze_job_description("Senior Full Stack AI Engineer", sample_jd)
    assert res.job_title == "Senior Full Stack AI Engineer"
    assert res.min_years_experience >= 3.0
    assert len(res.classified_requirements) > 0
    # Must have contains Python and FastAPI
    req_names = [r.name.lower() for r in res.classified_requirements]
    assert any("python" in n for n in req_names)
    assert any("fastapi" in n for n in req_names)

def test_transferable_skills_detection():
    # Azure transfers to AWS with HIGH transferability
    transfer = find_transferable_match("AWS", ["Python", "Azure", "Docker"])
    assert transfer is not None
    assert transfer["alternative_skill"] == "Azure"
    assert transfer["transferability_level"] == "HIGH"
    assert transfer["transfer_factor"] > 0.75

def test_contradiction_detection():
    candidate_data = {
        "name": "Test Candidate",
        "total_experience_years": 2.0,
        "educations": [
            {
                "degree": "Full-time Master of Science",
                "institution": "Tech University",
                "graduation_year": "2021-2023"
            }
        ],
        "experiences": [
            {
                "company": "Corp",
                "role": "Senior Engineer & Tech Lead",
                "start_date": "2021",
                "end_date": "2023",
                "duration_years": 2.0,
                "responsibilities": ["Coding"],
                "technologies": ["Python"]
            }
        ],
        "skills": [
            {"name": "React", "proficiency_claimed": "expert"} # unbacked
        ],
        "projects": [],
        "explicit_claims": [
            {"claim_text": "5 years of Python experience", "claimed_skill": "Python", "claimed_duration_years": 5.0}
        ]
    }
    claims, flags = verify_claims_and_detect_contradictions(candidate_data, job_min_experience=3.0)
    
    # Expect duration mismatch flag
    assert any(f["flag_type"] == "DURATION_MISMATCH" for f in flags)
    # Expect timeline overlap flag
    assert any(f["flag_type"] == "TIMELINE_OVERLAP" for f in flags)
    # Expect unbacked expertise flag
    assert any(f["flag_type"] == "UNBACKED_EXPERTISE" for f in flags)

def test_evidence_graph_and_scoring():
    reqs = [
        {"id": 1, "name": "Python", "category": "skill", "tier": "MUST_HAVE", "expected_years": 3.0, "weight": 1.0},
        {"id": 2, "name": "AWS", "category": "skill", "tier": "SHOULD_HAVE", "expected_years": 2.0, "weight": 0.75},
        {"id": 3, "name": "3+ Years Experience", "category": "experience", "tier": "MUST_HAVE", "expected_years": 3.0, "weight": 1.0}
    ]
    candidate_data = {
        "name": "Sample Candidate",
        "total_experience_years": 4.0,
        "experiences": [
            {
                "company": "Apex",
                "role": "Software Engineer",
                "start_date": "2022",
                "end_date": "Present",
                "duration_years": 4.0,
                "responsibilities": ["Built Python FastAPI backend microservices"],
                "technologies": ["Python", "Azure"]
            }
        ],
        "skills": [{"name": "Python"}, {"name": "Azure"}],
        "projects": [
            {
                "title": "Cloud Portal",
                "description": "Engineered web application using Python and Azure infrastructure.",
                "technologies": ["Python", "Azure"]
            }
        ]
    }
    
    ev_items = build_evidence_graph(reqs, candidate_data, risk_flags=[])
    assert len(ev_items) == 3
    
    # Python should be HIGH (Green)
    py_ev = next(e for e in ev_items if e["requirement_name"] == "Python")
    assert py_ev["strength"] == "HIGH"
    
    # AWS should be recognized as Transferable (Yellow) via Azure
    aws_ev = next(e for e in ev_items if e["requirement_name"] == "AWS")
    assert aws_ev["is_transferable"] is True
    assert aws_ev["strength"] == "PARTIAL"

    scores = calculate_candidate_scores(reqs, ev_items, candidate_data, risk_flags=[])
    assert scores["overall_match_score"] > 70.0
    assert scores["hiring_confidence_score"] > 60.0
    assert scores["potential_match_score"] >= scores["overall_match_score"]
