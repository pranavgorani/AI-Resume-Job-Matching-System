from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import orm, schemas
from app.services.copilot_engine import query_copilot, parse_natural_filter

router = APIRouter(prefix="/api/copilot", tags=["Copilot"])

@router.post("/query", response_model=schemas.CopilotQueryResponse)
def handle_copilot_query(payload: schemas.CopilotQueryRequest, db: Session = Depends(get_db)):
    job = None
    if payload.job_id:
        job = db.query(orm.Job).filter(orm.Job.id == payload.job_id).first()
    if not job:
        job = db.query(orm.Job).order_by(orm.Job.created_at.desc()).first()

    candidates = db.query(orm.Candidate).all()
    candidates_data = []
    for cand in candidates:
        match = None
        if job:
            match = db.query(orm.MatchResult).filter(orm.MatchResult.candidate_id == cand.id, orm.MatchResult.job_id == job.id).first()
        else:
            match = db.query(orm.MatchResult).filter(orm.MatchResult.candidate_id == cand.id).order_by(orm.MatchResult.overall_match_score.desc()).first()

        candidates_data.append({
            "id": cand.id,
            "name": cand.name,
            "match_score": match.overall_match_score if match else 75.0,
            "evidence_score": match.evidence_confidence_score if match else 70.0,
            "experience_years": cand.total_experience_years,
            "recommendation": match.recommendation if match else "CONSIDER",
            "risk_flags_count": len(cand.risk_flags),
            "skills": [{"name": s.name} for s in cand.skills],
            "projects": [{"title": p.title, "description": p.description} for p in cand.projects]
        })

    job_data = {"id": job.id, "title": job.title} if job else None
    result = query_copilot(payload.query, job_data, candidates_data)

    return schemas.CopilotQueryResponse(
        answer=result["answer"],
        suggested_actions=result.get("suggested_actions", []),
        candidate_highlight_ids=result.get("candidate_highlight_ids", [])
    )

@router.post("/filter", response_model=schemas.NaturalFilterResponse)
def handle_natural_filter(payload: schemas.NaturalFilterRequest, db: Session = Depends(get_db)):
    candidates = db.query(orm.Candidate).all()
    candidates_data = []
    for cand in candidates:
        match = db.query(orm.MatchResult).filter(orm.MatchResult.candidate_id == cand.id, orm.MatchResult.job_id == payload.job_id).first()
        candidates_data.append({
            "id": cand.id,
            "name": cand.name,
            "match_score": match.overall_match_score if match else 70.0,
            "evidence_score": match.evidence_confidence_score if match else 65.0,
            "experience_years": cand.total_experience_years,
            "skills": [{"name": s.name} for s in cand.skills]
        })

    filter_res = parse_natural_filter(payload.query, candidates_data)
    return schemas.NaturalFilterResponse(
        parsed_filters=filter_res["parsed_filters"],
        matched_candidate_ids=filter_res["matched_candidate_ids"],
        explanation=filter_res["explanation"]
    )
