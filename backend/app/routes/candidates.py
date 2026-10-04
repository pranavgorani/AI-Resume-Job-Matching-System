from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import orm, schemas

router = APIRouter(prefix="/api/candidates", tags=["Candidates"])

@router.get("", response_model=List[schemas.CandidateTableRow])
def list_all_candidates(
    job_id: Optional[int] = Query(None),
    min_score: Optional[float] = Query(None),
    recommendation: Optional[str] = Query(None),
    has_risks: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Search and filter candidates pool by job, minimum match score, recommendation, or risk status.
    """
    query = db.query(orm.Candidate)
    if job_id:
        # Strictly filter to candidates belonging to this job_id or evaluated for this job_id
        matched_cand_ids = db.query(orm.MatchResult.candidate_id).filter(orm.MatchResult.job_id == job_id)
        query = query.filter(
            (orm.Candidate.job_id == job_id) | (orm.Candidate.id.in_(matched_cand_ids))
        )
    candidates = query.all()

    rows = []
    for cand in candidates:
        match = None
        if job_id:
            match = db.query(orm.MatchResult).filter(orm.MatchResult.candidate_id == cand.id, orm.MatchResult.job_id == job_id).first()
        else:
            match = db.query(orm.MatchResult).filter(orm.MatchResult.candidate_id == cand.id).order_by(orm.MatchResult.overall_match_score.desc()).first()

        match_score = float(match.overall_match_score) if match else 0.0
        evidence_score = float(match.evidence_confidence_score) if match else 0.0
        hiring_conf = float(match.hiring_confidence_score) if match else 0.0
        pot_score = float(match.potential_match_score) if match else match_score
        rec = match.recommendation if match else "EVALUATING"
        cov = f"{match.supported_requirements_count}/{match.total_requirements_count}" if match else "0/0"

        flags_cnt = len(cand.risk_flags) if cand.risk_flags else 0

        # Apply filters if provided
        if min_score is not None and match_score < min_score:
            continue
        if recommendation is not None and rec.upper() != recommendation.upper():
            continue
        if has_risks is True and flags_cnt == 0:
            continue
        if has_risks is False and flags_cnt > 0:
            continue

        transferable_name = None
        for ev in cand.evidence_items:
            if ev.is_transferable:
                transferable_name = ev.requirement_name
                break

        rows.append(schemas.CandidateTableRow(
            rank=0, # sorted below
            candidate_id=cand.id,
            name=cand.name,
            email=cand.email,
            match_score=match_score,
            evidence_score=evidence_score,
            hiring_confidence=hiring_conf,
            potential_score=pot_score,
            required_skills_coverage=cov,
            experience_years=cand.total_experience_years,
            risk_flags_count=flags_cnt,
            recommendation=rec,
            top_transferable_skill=transferable_name
        ))

    rows.sort(key=lambda r: r.match_score, reverse=True)
    for idx, r in enumerate(rows, 1):
        r.rank = idx

    return rows

@router.get("/{candidate_id}", response_model=schemas.CandidateDetailOut)
def get_candidate_details(candidate_id: int, job_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    """
    Returns comprehensive Candidate Match Intelligence Report.
    """
    cand = db.query(orm.Candidate).filter(orm.Candidate.id == candidate_id).first()
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found")

    match = None
    if job_id:
        match = db.query(orm.MatchResult).filter(orm.MatchResult.candidate_id == candidate_id, orm.MatchResult.job_id == job_id).first()
    else:
        match = db.query(orm.MatchResult).filter(orm.MatchResult.candidate_id == candidate_id).order_by(orm.MatchResult.overall_match_score.desc()).first()

    return schemas.CandidateDetailOut(
        id=cand.id,
        name=cand.name,
        email=cand.email,
        phone=cand.phone,
        location=cand.location,
        linkedin=cand.linkedin,
        github=cand.github,
        portfolio=cand.portfolio,
        summary=cand.summary,
        total_experience_years=cand.total_experience_years,
        experiences=[
            schemas.ExperienceItem(
                company=e.company,
                role=e.role,
                start_date=e.start_date,
                end_date=e.end_date,
                duration_years=e.duration_years,
                responsibilities=e.responsibilities or [],
                achievements=e.achievements or [],
                technologies=e.technologies or []
            )
            for e in cand.experiences
        ],
        educations=[
            schemas.EducationItem(
                degree=ed.degree,
                institution=ed.institution,
                graduation_year=ed.graduation_year,
                field=ed.field,
                gpa=ed.gpa
            )
            for ed in cand.educations
        ],
        skills=[
            schemas.SkillItem(
                name=s.name,
                category=s.category,
                years_of_experience=s.years_of_experience,
                proficiency_claimed=s.proficiency_claimed
            )
            for s in cand.skills
        ],
        projects=[
            schemas.ProjectItem(
                title=p.title,
                description=p.description,
                technologies=p.technologies or [],
                contribution=p.contribution,
                results_metrics=p.results_metrics
            )
            for p in cand.projects
        ],
        certifications=[
            schemas.CertificationItem(
                name=c.name,
                issuer=c.issuer,
                issue_date=c.issue_date
            )
            for c in cand.certifications
        ],
        claims=[
            schemas.CandidateClaimOut(
                id=cl.id,
                claim_text=cl.claim_text,
                claimed_skill=cl.claimed_skill,
                claimed_duration_years=cl.claimed_duration_years,
                verification_status=cl.verification_status,
                confidence_score=cl.confidence_score,
                verification_notes=cl.verification_notes
            )
            for cl in cand.claims
        ],
        evidence_items=[
            schemas.EvidenceItemOut(
                id=ev.id,
                requirement_name=ev.requirement_name,
                claim_snippet=ev.claim_snippet,
                evidence_snippet=ev.evidence_snippet,
                source_section=ev.source_section,
                strength=ev.strength,
                evidence_score=ev.evidence_score,
                is_transferable=ev.is_transferable,
                transferable_explanation=ev.transferable_explanation,
                justification=ev.justification
            )
            for ev in cand.evidence_items
        ],
        risk_flags=[
            schemas.RiskFlagOut(
                id=rf.id,
                flag_type=rf.flag_type,
                severity=rf.severity,
                headline=rf.headline,
                details=rf.details,
                neutral_recommendation=rf.neutral_recommendation
            )
            for rf in cand.risk_flags
        ],
        interview_questions=[
            schemas.InterviewQuestionOut(
                id=iq.id,
                category=iq.category,
                target_requirement=iq.target_requirement,
                question=iq.question,
                suggested_focus=iq.suggested_focus,
                context_trigger=iq.context_trigger
            )
            for iq in cand.interview_questions
        ],
        match_result=schemas.MatchResultOut(
            id=match.id,
            job_id=match.job_id,
            candidate_id=match.candidate_id,
            overall_match_score=match.overall_match_score,
            hiring_confidence_score=match.hiring_confidence_score,
            evidence_confidence_score=match.evidence_confidence_score,
            evidence_coverage_percentage=match.evidence_coverage_percentage,
            potential_match_score=match.potential_match_score,
            score_breakdown=match.score_breakdown or {},
            supported_requirements_count=match.supported_requirements_count,
            total_requirements_count=match.total_requirements_count,
            missing_requirements_count=match.missing_requirements_count,
            contradiction_count=match.contradiction_count,
            recommendation=match.recommendation,
            recommendation_summary=match.recommendation_summary,
            potential_reason=match.potential_reason,
            why_not_reasons=match.why_not_reasons or [],
            outranking_tradeoffs=match.outranking_tradeoffs,
            skill_gaps=[
                schemas.SkillGapOut(
                    skill_name=sg.skill_name,
                    status=sg.status,
                    learning_priority=sg.learning_priority,
                    alternative_available=sg.alternative_available,
                    gap_notes=sg.gap_notes
                )
                for sg in match.skill_gaps
            ]
        ) if match else None
    )

@router.get("/{candidate_id}/evidence")
def get_candidate_evidence(candidate_id: int, db: Session = Depends(get_db)):
    evs = db.query(orm.CandidateEvidence).filter(orm.CandidateEvidence.candidate_id == candidate_id).all()
    return evs

@router.get("/{candidate_id}/risks")
def get_candidate_risks(candidate_id: int, db: Session = Depends(get_db)):
    risks = db.query(orm.RiskFlag).filter(orm.RiskFlag.candidate_id == candidate_id).all()
    return risks

@router.get("/{candidate_id}/interview-questions")
def get_candidate_interview_questions(candidate_id: int, db: Session = Depends(get_db)):
    qs = db.query(orm.InterviewQuestion).filter(orm.InterviewQuestion.candidate_id == candidate_id).all()
    return qs
