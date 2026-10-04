import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from services.benchmark_service import run_50_resume_benchmark
from app.models import orm

client = TestClient(app)

def test_benchmark_generation_and_accuracy():
    """Verify that 50 synthetic resumes run, match deterministically, and persist to database."""
    db = SessionLocal()
    try:
        results = run_50_resume_benchmark(seed=42, db=db)
        assert results is not None
        assert results["total"] == 50
        assert results["completed"] == 50
        assert results["failed"] == 0
        assert results["average_match"] > 0
        assert results["average_evidence"] > 0
        assert results["f1"] >= 0.70  # Accurate classification of strong vs weak fit
        assert len(results["candidates"]) == 50

        # Verify DB persistence of AnalysisRun
        run_record = db.query(orm.AnalysisRun).filter(orm.AnalysisRun.id == results["benchmark_run_id"]).first()
        assert run_record is not None
        assert run_record.total_candidates == 50
        assert run_record.status == "COMPLETED"
    finally:
        db.close()

def test_upload_idempotency_and_deduplication():
    """Verify uploading identical resume bytes under the same job detects duplicate."""
    db = SessionLocal()
    try:
        # Create a test job
        job = orm.Job(
            title="Idempotency Test Role",
            raw_description="Python FastAPI backend role",
            seniority="Mid",
            min_years_experience=2.0
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        file_bytes = b"SAMPLE RESUME CONTENT\nName: Jordan Vance\nSkills: Python, FastAPI, React\nExperience: 4 years"
        files = {"file": ("jordan_vance.txt", file_bytes, "text/plain")}
        data = {"job_id": str(job.id)}

        # 1. First Upload
        res1 = client.post("/api/resumes/upload", files=files, data=data)
        assert res1.status_code == 200
        d1 = res1.json()
        assert d1["success"] is True
        cand_id = d1["candidate_id"]

        # 2. Second Upload with identical file bytes
        files2 = {"file": ("jordan_vance.txt", file_bytes, "text/plain")}
        res2 = client.post("/api/resumes/upload", files=files2, data=data)
        assert res2.status_code == 200
        d2 = res2.json()
        assert d2.get("duplicate") is True
        assert d2.get("candidate_id") == cand_id
        assert "already uploaded" in d2.get("message", "").lower()
    finally:
        db.close()

def test_job_isolation():
    """Verify candidates belonging to Job A do NOT appear when querying Job B."""
    db = SessionLocal()
    try:
        job_a = orm.Job(title="Job Alpha", raw_description="Alpha role")
        job_b = orm.Job(title="Job Beta", raw_description="Beta role")
        db.add_all([job_a, job_b])
        db.commit()
        db.refresh(job_a)
        db.refresh(job_b)

        cand_a = orm.Candidate(job_id=job_a.id, name="Candidate Alpha", total_experience_years=3.0)
        cand_b = orm.Candidate(job_id=job_b.id, name="Candidate Beta", total_experience_years=5.0)
        db.add_all([cand_a, cand_b])
        db.commit()

        # Query candidates for Job Alpha
        res_a = client.get(f"/api/candidates?job_id={job_a.id}")
        assert res_a.status_code == 200
        names_a = [c["name"] for c in res_a.json()]
        assert "Candidate Alpha" in names_a
        assert "Candidate Beta" not in names_a

        # Query candidates for Job Beta
        res_b = client.get(f"/api/candidates?job_id={job_b.id}")
        assert res_b.status_code == 200
        names_b = [c["name"] for c in res_b.json()]
        assert "Candidate Beta" in names_b
        assert "Candidate Alpha" not in names_b
    finally:
        db.close()
