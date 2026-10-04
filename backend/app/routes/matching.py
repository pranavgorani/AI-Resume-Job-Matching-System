from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.database import get_db
from app.models import orm, schemas
from app.services.contradiction_detector import verify_claims_and_detect_contradictions
from app.services.evidence_engine import build_evidence_graph
from app.services.scoring_engine import calculate_candidate_scores
from app.services.interview_engine import generate_interview_questions
from app.services.why_not_engine import generate_why_not_analysis

router = APIRouter(prefix="/api/matching", tags=["Matching"])

@router.post("/run")
def run_matching_engine(
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Executes the full Evidence-First Matching Engine for a Job across all candidates.
    Pipeline:
      Job Intelligence
        ↓
      Resume Extraction
        ↓
      Evidence Mapping
        ↓
      Claim Verification
        ↓
      Contradiction Detection
        ↓
      Transferable Skill Analysis
        ↓
      Deterministic Scoring Engine
        ↓
      Interview Question Generation
        ↓
      Why-Not Analysis
    """
    job_id = payload.get("job_id")
    if not job_id:
        raise HTTPException(status_code=400, detail="job_id is required")

    job = db.query(orm.Job).filter(orm.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    requirements = db.query(orm.JobRequirement).filter(orm.JobRequirement.job_id == job_id).all()
    req_dicts = [
        {
            "id": r.id,
            "name": r.name,
            "category": r.category,
            "tier": r.tier,
            "expected_years": r.expected_years,
            "weight": r.weight
        }
        for r in requirements
    ]

    candidates = db.query(orm.Candidate).all()
    if not candidates:
        return {"status": "success", "message": "No candidates in database yet.", "matched_count": 0}

    # Clear prior match results for this job to ensure fresh deterministic calculation
    db.query(orm.MatchResult).filter(orm.MatchResult.job_id == job_id).delete()
    db.commit()

    processed_matches = []

    for cand in candidates:
        # Prepare candidate dictionary
        cand_dict = {
            "id": cand.id,
            "name": cand.name,
            "summary": cand.summary,
            "total_experience_years": cand.total_experience_years,
            "experiences": [
                {
                    "company": e.company,
                    "role": e.role,
                    "start_date": e.start_date,
                    "end_date": e.end_date,
                    "duration_years": e.duration_years,
                    "responsibilities": e.responsibilities or [],
                    "technologies": e.technologies or []
                }
                for e in cand.experiences
            ],
            "educations": [
                {
                    "degree": ed.degree,
                    "institution": ed.institution,
                    "graduation_year": ed.graduation_year,
                    "field": ed.field
                }
                for ed in cand.educations
            ],
            "skills": [{"name": s.name, "category": s.category, "proficiency_claimed": s.proficiency_claimed} for s in cand.skills],
            "projects": [
                {
                    "title": p.title,
                    "description": p.description,
                    "technologies": p.technologies or [],
                    "contribution": p.contribution,
                    "results_metrics": p.results_metrics
                }
                for p in cand.projects
            ],
            "certifications": [{"name": c.name} for c in cand.certifications],
            "explicit_claims": [
                {
                    "claim_text": cl.claim_text,
                    "claimed_skill": cl.claimed_skill,
                    "claimed_duration_years": cl.claimed_duration_years,
                    "claimed_seniority": cl.claimed_seniority
                }
                for cl in cand.claims
            ]
        }

        # 1. Claim Verification & Contradiction Detection
        claims_verified, risk_flags = verify_claims_and_detect_contradictions(
            cand_dict,
            job_min_experience=job.min_years_experience,
            job_required_skills=[r["name"] for r in req_dicts if r["tier"] == "MUST_HAVE"]
        )

        # Clear and update Risk Flags in DB
        db.query(orm.RiskFlag).filter(orm.RiskFlag.candidate_id == cand.id).delete()
        for rf in risk_flags:
            db.add(orm.RiskFlag(
                candidate_id=cand.id,
                job_id=job.id,
                flag_type=rf["flag_type"],
                severity=rf["severity"],
                headline=rf["headline"],
                details=rf["details"],
                neutral_recommendation=rf["neutral_recommendation"]
            ))

        # 2. Build Evidence Graph
        evidence_items = build_evidence_graph(req_dicts, cand_dict, risk_flags)
        
        # Clear and update Evidence items in DB
        db.query(orm.CandidateEvidence).filter(orm.CandidateEvidence.candidate_id == cand.id).delete()
        for ev in evidence_items:
            db.add(orm.CandidateEvidence(
                candidate_id=cand.id,
                job_requirement_id=ev.get("job_requirement_id"),
                requirement_name=ev["requirement_name"],
                claim_snippet=ev.get("claim_snippet"),
                evidence_snippet=ev["evidence_snippet"],
                source_section=ev.get("source_section", "general"),
                strength=ev["strength"],
                evidence_score=ev["evidence_score"],
                is_transferable=ev.get("is_transferable", False),
                transferable_explanation=ev.get("transferable_explanation"),
                justification=ev.get("justification")
            ))

        # 3. Deterministic Explainable Scoring
        scores = calculate_candidate_scores(
            req_dicts,
            evidence_items,
            cand_dict,
            risk_flags,
            custom_weights=job.weights or {}
        )

        # 4. Generate Interview Questions
        interview_qs = generate_interview_questions(evidence_items, risk_flags, cand_dict)
        db.query(orm.InterviewQuestion).filter(orm.InterviewQuestion.candidate_id == cand.id).delete()
        for iq in interview_qs:
            db.add(orm.InterviewQuestion(
                candidate_id=cand.id,
                job_id=job.id,
                category=iq["category"],
                target_requirement=iq.get("target_requirement"),
                question=iq["question"],
                suggested_focus=iq.get("suggested_focus"),
                context_trigger=iq.get("context_trigger")
            ))

        processed_matches.append({
            "candidate_id": cand.id,
            "candidate_name": cand.name,
            "cand_dict": cand_dict,
            "scores": scores,
            "evidence_items": evidence_items,
            "risk_flags": risk_flags
        })

    # Sort to determine rank #1 for Why-Not analysis
    processed_matches.sort(key=lambda m: m["scores"]["overall_match_score"], reverse=True)
    top_cand = processed_matches[0] if processed_matches else None
    top_cand_dict = {"id": top_cand["candidate_id"], "name": top_cand["candidate_name"], "match_score": top_cand["scores"]["overall_match_score"]} if top_cand else None

    # Persist MatchResults and SkillGaps
    for pm in processed_matches:
        scores = pm["scores"]
        why_not = generate_why_not_analysis(
            pm["candidate_id"],
            pm["candidate_name"],
            scores["overall_match_score"],
            pm["evidence_items"],
            pm["risk_flags"],
            top_candidate=top_cand_dict
        )

        match_res = orm.MatchResult(
            job_id=job.id,
            candidate_id=pm["candidate_id"],
            overall_match_score=scores["overall_match_score"],
            hiring_confidence_score=scores["hiring_confidence_score"],
            evidence_confidence_score=scores["evidence_confidence_score"],
            evidence_coverage_percentage=scores["evidence_coverage_percentage"],
            potential_match_score=scores["potential_match_score"],
            score_breakdown=scores["score_breakdown"],
            supported_requirements_count=scores["supported_requirements_count"],
            total_requirements_count=scores["total_requirements_count"],
            missing_requirements_count=scores["missing_requirements_count"],
            contradiction_count=scores["contradiction_count"],
            recommendation=scores["recommendation"],
            recommendation_summary=scores["recommendation_summary"],
            potential_reason=scores["potential_reason"],
            why_not_reasons=why_not["barriers"],
            outranking_tradeoffs=why_not["tradeoff_summary"]
        )
        db.add(match_res)
        db.commit()
        db.refresh(match_res)

        # Persist Skill Gaps
        for ev in pm["evidence_items"]:
            if ev.get("strength") in ["WEAK_MISSING", "PARTIAL", "CONTRADICTORY"]:
                gap_status = "TRANSFERABLE" if ev.get("is_transferable") else ("MISSING" if ev.get("strength") == "WEAK_MISSING" else "PARTIAL")
                priority = "HIGH" if ev.get("strength") == "WEAK_MISSING" else "MEDIUM"
                db.add(orm.SkillGap(
                    match_result_id=match_res.id,
                    skill_name=ev["requirement_name"],
                    status=gap_status,
                    learning_priority=priority,
                    alternative_available=ev.get("transferable_explanation"),
                    gap_notes=ev.get("justification")
                ))

    db.commit()

    return {
        "status": "success",
        "job_id": job.id,
        "job_title": job.title,
        "matched_candidates_count": len(processed_matches),
        "top_ranked_candidate": top_cand["candidate_name"] if top_cand else None,
        "top_score": top_cand["scores"]["overall_match_score"] if top_cand else 0.0
    }

@router.get("/{job_id}", response_model=List[schemas.CandidateTableRow])
def get_job_matches(job_id: int, db: Session = Depends(get_db)):
    """
    Returns ranked candidates for a specific job matching table.
    """
    matches = (
        db.query(orm.MatchResult)
        .filter(orm.MatchResult.job_id == job_id)
        .order_by(orm.MatchResult.overall_match_score.desc())
        .all()
    )
    
    rows = []
    for rank, m in enumerate(matches, 1):
        cand = m.candidate
        flags_count = len(cand.risk_flags) if cand.risk_flags else 0
        
        # Check transferable
        transferable_name = None
        for ev in cand.evidence_items:
            if ev.is_transferable:
                transferable_name = ev.requirement_name
                break

        rows.append(schemas.CandidateTableRow(
            rank=rank,
            candidate_id=cand.id,
            name=cand.name,
            email=cand.email,
            match_score=m.overall_match_score,
            evidence_score=m.evidence_confidence_score,
            hiring_confidence=m.hiring_confidence_score,
            potential_score=m.potential_match_score,
            required_skills_coverage=f"{m.supported_requirements_count}/{m.total_requirements_count}",
            experience_years=cand.total_experience_years,
            risk_flags_count=flags_count,
            recommendation=m.recommendation,
            top_transferable_skill=transferable_name
        ))
    return rows

@router.put("/{job_id}/weights")
def update_weights_and_recalculate(
    job_id: int,
    weights: schemas.ScoringWeights,
    db: Session = Depends(get_db)
):
    """
    Recruiter updates scoring weights and immediately recalculates all candidate match rankings.
    """
    job = db.query(orm.Job).filter(orm.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.weights = weights.dict()
    db.commit()

    # Re-run matching
    run_matching_engine({"job_id": job_id}, db)
    return {"status": "success", "message": "Weights updated and candidate scores re-ranked."}
