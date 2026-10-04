from fastapi import APIRouter, Depends, Body, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from app.database import get_db, init_db
from app.models import orm
from app.seed_data import DEMO_JOB, DEMO_CANDIDATES
from app.routes.matching import run_matching_engine

router = APIRouter(prefix="/api/demo", tags=["Demo"])

@router.post("/seed")
def seed_demo_dataset(
    payload: Optional[Dict[str, Any]] = Body(None),
    job_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Demo candidate initialization:
    Seeds candidate archetypes for the specified job_id (or default demo job),
    then automatically executes the complete Evidence-First Matching Engine.
    """
    # 0. Ensure tables exist
    init_db()

    target_job_id = None
    if payload and isinstance(payload, dict) and payload.get("job_id"):
        try:
            target_job_id = int(payload.get("job_id"))
        except (ValueError, TypeError):
            pass
    elif job_id is not None:
        target_job_id = int(job_id)

    job = None
    if target_job_id and target_job_id > 0:
        job = db.query(orm.Job).filter(orm.Job.id == target_job_id).first()

    if not job:
        # Check if default demo job already exists
        existing_job = db.query(orm.Job).filter(orm.Job.title == DEMO_JOB["title"]).first()
        if existing_job:
            job = existing_job
            job.raw_description = DEMO_JOB["raw_description"]
            job.seniority = DEMO_JOB["seniority"]
            job.min_years_experience = DEMO_JOB["min_years_experience"]
            job.education_required = DEMO_JOB["education_required"]
            job.location = DEMO_JOB["location"]
            job.work_mode = DEMO_JOB["work_mode"]
            job.responsibilities = DEMO_JOB["responsibilities"]
            job.tools_and_tech = DEMO_JOB["tools_and_tech"]
            job.domain_knowledge = DEMO_JOB["domain_knowledge"]
            job.soft_skills = DEMO_JOB["soft_skills"]
            job.status = "active"
            db.commit()
        else:
            job = orm.Job(
                title=DEMO_JOB["title"],
                raw_description=DEMO_JOB["raw_description"],
                seniority=DEMO_JOB["seniority"],
                min_years_experience=DEMO_JOB["min_years_experience"],
                education_required=DEMO_JOB["education_required"],
                location=DEMO_JOB["location"],
                work_mode=DEMO_JOB["work_mode"],
                responsibilities=DEMO_JOB["responsibilities"],
                tools_and_tech=DEMO_JOB["tools_and_tech"],
                domain_knowledge=DEMO_JOB["domain_knowledge"],
                soft_skills=DEMO_JOB["soft_skills"],
                status="active"
            )
            db.add(job)
            db.commit()
            db.refresh(job)

    # Ensure job requirements exist for matching
    existing_reqs = db.query(orm.JobRequirement).filter(orm.JobRequirement.job_id == job.id).count()
    if existing_reqs == 0:
        for req in DEMO_JOB["requirements"]:
            db.add(orm.JobRequirement(
                job_id=job.id,
                name=req["name"],
                category=req["category"],
                tier=req["tier"],
                description=f"Core capability in {req['name']}",
                expected_years=req["expected_years"],
                weight=req["weight"]
            ))
        db.commit()

    # Clean old candidate records for THIS target job
    try:
        cands_to_clean = db.query(orm.Candidate).filter(orm.Candidate.job_id == job.id).all()
        cand_ids = [c.id for c in cands_to_clean]
        if cand_ids:
            db.query(orm.InterviewQuestion).filter(orm.InterviewQuestion.candidate_id.in_(cand_ids)).delete(synchronize_session=False)
            db.query(orm.RiskFlag).filter(orm.RiskFlag.candidate_id.in_(cand_ids)).delete(synchronize_session=False)
            db.query(orm.CandidateEvidence).filter(orm.CandidateEvidence.candidate_id.in_(cand_ids)).delete(synchronize_session=False)
            db.query(orm.CandidateClaim).filter(orm.CandidateClaim.candidate_id.in_(cand_ids)).delete(synchronize_session=False)
            db.query(orm.CandidateProject).filter(orm.CandidateProject.candidate_id.in_(cand_ids)).delete(synchronize_session=False)
            db.query(orm.CandidateSkill).filter(orm.CandidateSkill.candidate_id.in_(cand_ids)).delete(synchronize_session=False)
            db.query(orm.CandidateEducation).filter(orm.CandidateEducation.candidate_id.in_(cand_ids)).delete(synchronize_session=False)
            db.query(orm.CandidateExperience).filter(orm.CandidateExperience.candidate_id.in_(cand_ids)).delete(synchronize_session=False)
            db.query(orm.Resume).filter(orm.Resume.candidate_id.in_(cand_ids)).delete(synchronize_session=False)
            db.query(orm.Candidate).filter(orm.Candidate.id.in_(cand_ids)).delete(synchronize_session=False)
        db.query(orm.MatchResult).filter(orm.MatchResult.job_id == job.id).delete(synchronize_session=False)
        db.commit()
    except Exception:
        db.rollback()

    # 3. Create Requirements
    for req in DEMO_JOB["requirements"]:
        db.add(orm.JobRequirement(
            job_id=job.id,
            name=req["name"],
            category=req["category"],
            tier=req["tier"],
            description=f"Core capability in {req['name']}",
            expected_years=req["expected_years"],
            weight=req["weight"]
        ))
    db.commit()

    # 4. Insert all 8 Candidates
    for c_data in DEMO_CANDIDATES:
        cand = orm.Candidate(
            job_id=job.id,
            name=c_data["name"],
            email=c_data["email"],
            phone=c_data["phone"],
            location=c_data["location"],
            linkedin=c_data["linkedin"],
            github=c_data["github"],
            portfolio=c_data["portfolio"],
            summary=c_data["summary"],
            total_experience_years=c_data["total_experience_years"]
        )
        db.add(cand)
        db.commit()
        db.refresh(cand)

        # Resume record
        db.add(orm.Resume(
            candidate_id=cand.id,
            file_name=f"{cand.name.replace(' ', '_')}_Resume.pdf",
            file_type="pdf",
            raw_text=c_data["summary"] + " " + " ".join([p["description"] for p in c_data.get("projects", [])]),
            parsed_json=c_data
        ))

        # Experiences
        for exp in c_data.get("experiences", []):
            db.add(orm.CandidateExperience(
                candidate_id=cand.id,
                company=exp["company"],
                role=exp["role"],
                start_date=exp["start_date"],
                end_date=exp["end_date"],
                duration_years=exp["duration_years"],
                responsibilities=exp["responsibilities"],
                achievements=exp.get("achievements", []),
                technologies=exp["technologies"]
            ))

        # Educations
        for edu in c_data.get("educations", []):
            db.add(orm.CandidateEducation(
                candidate_id=cand.id,
                degree=edu["degree"],
                institution=edu["institution"],
                graduation_year=edu["graduation_year"],
                field=edu["field"],
                gpa=edu.get("gpa")
            ))

        # Skills
        for s in c_data.get("skills", []):
            db.add(orm.CandidateSkill(
                candidate_id=cand.id,
                name=s["name"],
                category=s["category"],
                years_of_experience=s["years_of_experience"],
                proficiency_claimed=s["proficiency_claimed"]
            ))

        # Projects
        for p in c_data.get("projects", []):
            db.add(orm.CandidateProject(
                candidate_id=cand.id,
                title=p["title"],
                description=p["description"],
                technologies=p["technologies"],
                contribution=p["contribution"],
                results_metrics=p.get("results_metrics")
            ))

        # Certifications
        for cert in c_data.get("certifications", []):
            db.add(orm.CandidateCertification(
                candidate_id=cand.id,
                name=cert["name"],
                issuer=cert.get("issuer"),
                issue_date=cert.get("issue_date")
            ))

        # Explicit Claims
        for cl in c_data.get("explicit_claims", []):
            db.add(orm.CandidateClaim(
                candidate_id=cand.id,
                claim_text=cl["claim_text"],
                claimed_skill=cl.get("claimed_skill"),
                claimed_duration_years=cl.get("claimed_duration_years"),
                claimed_seniority=cl.get("claimed_seniority"),
                verification_status="SUPPORTED",
                confidence_score=0.88
            ))

    db.commit()

    # 5. Run Matching Engine
    match_output = run_matching_engine({"job_id": job.id}, db)

    return {
        "status": "success",
        "message": "Demo environment successfully seeded and evaluated with 8 candidate archetypes!",
        "job_id": job.id,
        "job_title": job.title,
        "candidates_count": len(DEMO_CANDIDATES),
        "matching_summary": match_output
    }
