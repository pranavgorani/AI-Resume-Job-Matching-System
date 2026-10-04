from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}

def test_demo_seed_and_matching():
    # 1. Trigger 1-click Demo Seed
    res = client.post("/api/demo/seed")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["candidates_count"] == 8
    job_id = data["job_id"]

    # 2. Check Jobs List
    jobs_res = client.get("/api/jobs")
    assert jobs_res.status_code == 200
    assert len(jobs_res.json()) >= 1

    # 3. Check Ranked Matches
    match_res = client.get(f"/api/matching/{job_id}")
    assert match_res.status_code == 200
    rows = match_res.json()
    assert len(rows) == 8
    # Rank 1 should have high score
    assert rows[0]["rank"] == 1
    assert rows[0]["match_score"] >= 88.0

    # 4. Check Candidate Detail
    cand_id = rows[0]["candidate_id"]
    cand_res = client.get(f"/api/candidates/{cand_id}?job_id={job_id}")
    assert cand_res.status_code == 200
    cand_data = cand_res.json()
    assert "evidence_items" in cand_data
    assert "interview_questions" in cand_data
    assert "match_result" in cand_data
    assert len(cand_data["evidence_items"]) > 0

    # 5. Check Comparison
    compare_res = client.post("/api/candidates/compare", json={
        "job_id": job_id,
        "candidate_ids": [rows[0]["candidate_id"], rows[1]["candidate_id"], rows[2]["candidate_id"]]
    })
    assert compare_res.status_code == 200
    comp_data = compare_res.json()
    assert "matrix" in comp_data
    assert "recommended_candidate_name" in comp_data
    assert "tradeoff_analysis" in comp_data

    # 6. Check Copilot Query
    copilot_res = client.post("/api/copilot/query", json={
        "job_id": job_id,
        "query": "Why is the top candidate ranked #1?"
    })
    assert copilot_res.status_code == 200
    cop_data = copilot_res.json()
    assert "answer" in cop_data
    assert len(cop_data["answer"]) > 20

    # 7. Check Natural Filter
    filter_res = client.post("/api/copilot/filter", json={
        "job_id": job_id,
        "query": "Show candidates with Python and FastAPI, at least 3 years experience, and strong project evidence"
    })
    assert filter_res.status_code == 200
    filt_data = filter_res.json()
    assert "matched_candidate_ids" in filt_data
    assert len(filt_data["matched_candidate_ids"]) > 0
