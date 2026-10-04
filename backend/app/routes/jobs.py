import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import orm, schemas
from app.services.jd_intelligence import analyze_job_description

logger = logging.getLogger("talentproof.jobs")
router = APIRouter(prefix="/api/jobs", tags=["Jobs"])

@router.post("", response_model=schemas.JobOut)
def create_job(payload: schemas.JobCreate, db: Session = Depends(get_db)):
    # 1. Analyze JD automatically
    analysis = analyze_job_description(payload.title, payload.raw_description)
    
    # 2. Persist Job
    job = orm.Job(
        title=payload.title,
        raw_description=payload.raw_description,
        seniority=analysis.seniority,
        min_years_experience=analysis.min_years_experience,
        education_required=analysis.education_required,
        location=analysis.location,
        work_mode=analysis.work_mode,
        responsibilities=analysis.responsibilities,
        tools_and_tech=analysis.tools_and_tech,
        domain_knowledge=analysis.domain_knowledge,
        soft_skills=analysis.soft_skills,
        weights=payload.weights.dict() if payload.weights else {}
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # 3. Persist Classified Requirements
    for req in analysis.classified_requirements:
        orm_req = orm.JobRequirement(
            job_id=job.id,
            name=req.name,
            category=req.category,
            tier=req.tier,
            description=req.description,
            expected_years=req.expected_years,
            weight=req.weight
        )
        db.add(orm_req)
    db.commit()
    db.refresh(job)

    return job

def _enrich_job(job: orm.Job) -> schemas.JobOut:
    candidates = job.candidates or []
    matches = job.match_results or []
    cand_count = len(candidates)
    shortlisted_count = sum(
        1 for m in matches if m.recommendation in ["RECOMMEND", "STRONGLY_RECOMMEND"]
    )
    avg_score = (
        round(sum(m.overall_match_score for m in matches) / len(matches), 1)
        if len(matches) > 0
        else 0.0
    )
    job_out = schemas.JobOut.model_validate(job)
    job_out.candidates_count = cand_count
    job_out.shortlisted_count = shortlisted_count
    job_out.average_match_score = avg_score
    return job_out

@router.get("", response_model=List[schemas.JobOut])
def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(orm.Job).order_by(orm.Job.created_at.desc()).all()
    return [_enrich_job(j) for j in jobs]

@router.get("/{job_id}", response_model=schemas.JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    if not job_id or job_id <= 0:
        logger.warning(f"[JOB DEBUG] Invalid job_id requested: {job_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A valid job ID is required"
        )
    logger.info(f"[JOB DEBUG] database lookup for job_id={job_id}")
    job = db.query(orm.Job).filter(orm.Job.id == job_id).first()
    if not job:
        logger.warning(f"[JOB DEBUG] Job not found in database for job_id={job_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    return _enrich_job(job)

@router.put("/{job_id}", response_model=schemas.JobOut)
def update_job(job_id: int, payload: schemas.JobCreate, db: Session = Depends(get_db)):
    job = db.query(orm.Job).filter(orm.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.title = payload.title
    job.raw_description = payload.raw_description
    if payload.seniority: job.seniority = payload.seniority
    if payload.min_years_experience: job.min_years_experience = payload.min_years_experience
    if payload.location: job.location = payload.location
    if payload.work_mode: job.work_mode = payload.work_mode
    db.commit()
    db.refresh(job)
    return _enrich_job(job)

@router.post("/{job_id}/duplicate", response_model=schemas.JobOut)
def duplicate_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(orm.Job).filter(orm.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    dup_job = orm.Job(
        title=f"{job.title} (Copy)",
        raw_description=job.raw_description,
        seniority=job.seniority,
        min_years_experience=job.min_years_experience,
        education_required=job.education_required,
        location=job.location,
        work_mode=job.work_mode,
        responsibilities=job.responsibilities,
        tools_and_tech=job.tools_and_tech,
        domain_knowledge=job.domain_knowledge,
        soft_skills=job.soft_skills,
        status="active",
        weights=job.weights or {}
    )
    db.add(dup_job)
    db.commit()
    db.refresh(dup_job)

    for req in job.requirements or []:
        dup_req = orm.JobRequirement(
            job_id=dup_job.id,
            name=req.name,
            category=req.category,
            tier=req.tier,
            description=req.description,
            expected_years=req.expected_years,
            weight=req.weight
        )
        db.add(dup_req)
    db.commit()
    db.refresh(dup_job)
    return _enrich_job(dup_job)

@router.put("/{job_id}/archive", response_model=schemas.JobOut)
def toggle_archive_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(orm.Job).filter(orm.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.status = "archived" if job.status == "active" else "active"
    db.commit()
    db.refresh(job)
    return _enrich_job(job)

@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(orm.Job).filter(orm.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()
    return {"status": "deleted", "job_id": job_id}

@router.post("/analyze-raw", response_model=schemas.JobAnalysisResponse)
def analyze_raw_jd(payload: schemas.JobCreate):
    """
    Allows recruiter to preview extracted requirements and tiers (MUST, SHOULD, NICE)
    before final job submission.
    """
    return analyze_job_description(payload.title, payload.raw_description)

@router.put("/{job_id}/requirements", response_model=schemas.JobOut)
def update_job_requirements(job_id: int, requirements: List[schemas.RequirementCreate], db: Session = Depends(get_db)):
    job = db.query(orm.Job).filter(orm.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Remove existing
    db.query(orm.JobRequirement).filter(orm.JobRequirement.job_id == job_id).delete()
    
    # Insert updated
    for r in requirements:
        new_req = orm.JobRequirement(
            job_id=job_id,
            name=r.name,
            category=r.category,
            tier=r.tier,
            description=r.description,
            expected_years=r.expected_years,
            weight=r.weight
        )
        db.add(new_req)
    db.commit()
    db.refresh(job)
    return job
