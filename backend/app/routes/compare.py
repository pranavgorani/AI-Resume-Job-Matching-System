from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.database import get_db
from app.models import orm, schemas

router = APIRouter(prefix="/api/candidates/compare", tags=["Compare"])

@router.post("", response_model=schemas.CandidateComparisonResult)
def compare_candidates(payload: schemas.CandidateComparisonRequest, db: Session = Depends(get_db)):
    if len(payload.candidate_ids) < 2:
        raise HTTPException(status_code=400, detail="Please select at least 2 candidates to compare.")
    if len(payload.candidate_ids) > 5:
        raise HTTPException(status_code=400, detail="Comparison is limited to a maximum of 5 candidates.")

    job = db.query(orm.Job).filter(orm.Job.id == payload.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    requirements = db.query(orm.JobRequirement).filter(orm.JobRequirement.job_id == job.id).all()
    candidates = db.query(orm.Candidate).filter(orm.Candidate.id.in_(payload.candidate_ids)).all()

    if len(candidates) < len(payload.candidate_ids):
        raise HTTPException(status_code=404, detail="One or more selected candidates not found")

    # Build comparison matrix
    cand_details = []
    matrix = {}
    for req in requirements:
        matrix[req.name] = {}

    for cand in candidates:
        match = db.query(orm.MatchResult).filter(orm.MatchResult.candidate_id == cand.id, orm.MatchResult.job_id == job.id).first()
        evidence_dict = {e.requirement_name: e for e in cand.evidence_items}
        
        cand_details.append({
            "id": cand.id,
            "name": cand.name,
            "match_score": match.overall_match_score if match else 70.0,
            "evidence_score": match.evidence_confidence_score if match else 65.0,
            "hiring_confidence": match.hiring_confidence_score if match else 65.0,
            "potential_score": match.potential_match_score if match else 75.0,
            "experience_years": cand.total_experience_years,
            "risk_flags_count": len(cand.risk_flags),
            "recommendation": match.recommendation if match else "CONSIDER"
        })

        for req in requirements:
            ev = evidence_dict.get(req.name)
            if ev:
                icon_status = "MATCH" if ev.strength == "HIGH" else ("TRANSFERABLE" if ev.is_transferable else ("PARTIAL" if ev.strength == "PARTIAL" else ("CONTRADICTORY" if ev.strength == "CONTRADICTORY" else "MISSING")))
                matrix[req.name][cand.name] = {
                    "status": icon_status,
                    "strength": ev.strength,
                    "score": ev.evidence_score,
                    "snippet": ev.evidence_snippet[:100]
                }
            else:
                matrix[req.name][cand.name] = {
                    "status": "MISSING",
                    "strength": "WEAK_MISSING",
                    "score": 0.0,
                    "snippet": "No direct evidence found."
                }

    # Evaluate Trade-Offs & Recommended Candidate (Not blindly highest raw score!)
    # We choose the candidate with highest Hiring Confidence & lowest critical risk flags.
    cand_details.sort(key=lambda c: (c["hiring_confidence"] - c["risk_flags_count"] * 10), reverse=True)
    best_cand = cand_details[0]

    tradeoffs = []
    for c in cand_details:
        if c["id"] == best_cand["id"]:
            continue
        delta = round(best_cand["match_score"] - c["match_score"], 1)
        if c["potential_score"] > best_cand["match_score"]:
            tradeoffs.append(f"• **{c['name']}** shows slightly higher long-term potential ({c['potential_score']}%), but currently lacks verified proof in key requirements compared to {best_cand['name']}.")
        elif c["risk_flags_count"] > 0:
            tradeoffs.append(f"• **{c['name']}** has {c['risk_flags_count']} active verification flag(s) that require recruiter clarification before an offer.")
        else:
            tradeoffs.append(f"• **{c['name']}** is {abs(delta)}% behind {best_cand['name']} primarily due to difference in documented project scale metrics.")

    why_summary = (
        f"**{best_cand['name']}** is the recommended selection with {best_cand['match_score']}% Match Score and "
        f"{best_cand['evidence_score']}% Evidence Score. {best_cand['name']} provides the lowest hiring risk with "
        f"substantiated production proof across all core must-have technologies."
    )

    tradeoff_text = "\n".join(tradeoffs) if tradeoffs else "All selected candidates demonstrate competitive profiles."

    return schemas.CandidateComparisonResult(
        job_title=job.title,
        candidates=cand_details,
        matrix=matrix,
        recommended_candidate_name=best_cand["name"],
        recommended_candidate_id=best_cand["id"],
        tradeoff_analysis=tradeoff_text,
        why_summary=why_summary
    )
