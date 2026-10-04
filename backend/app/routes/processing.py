import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import orm, schemas

logger = logging.getLogger("talentproof.processing")
router = APIRouter(prefix="/api/processing", tags=["Processing"])

@router.get("/status/{job_id}")
def get_processing_status(job_id: int, db: Session = Depends(get_db)):
    """
    Returns live processing status for all resumes uploaded to a job.
    Supports real-time UI polling across Queued, Parsing, Analyzing, Completed, Failed stages.
    """
    proc_jobs = (
        db.query(orm.ProcessingJob)
        .filter(orm.ProcessingJob.job_id == job_id)
        .order_by(orm.ProcessingJob.created_at.desc())
        .all()
    )
    candidates = (
        db.query(orm.Candidate)
        .filter(orm.Candidate.job_id == job_id)
        .all()
    )

    queued_count = sum(1 for c in candidates if (c.processing_status or "").upper() in ("QUEUED", "UPLOADING", "UPLOADED"))
    parsing_count = sum(1 for c in candidates if (c.processing_status or "").upper() == "PARSING")
    analyzing_count = sum(1 for c in candidates if (c.processing_status or "").upper() == "ANALYZING")
    completed_count = sum(1 for c in candidates if (c.processing_status or "").upper() == "COMPLETED")
    failed_count = sum(1 for c in candidates if (c.processing_status or "").upper() == "FAILED")

    return {
        "job_id": job_id,
        "total_candidates": len(candidates),
        "counts": {
            "queued": queued_count,
            "parsing": parsing_count,
            "analyzing": analyzing_count,
            "completed": completed_count,
            "failed": failed_count,
        },
        "is_all_completed": len(candidates) > 0 and (completed_count + failed_count) == len(candidates),
        "processing_jobs": [
            {
                "id": pj.id,
                "candidate_id": pj.candidate_id,
                "file_name": pj.file_name,
                "status": pj.status,
                "stage": pj.stage,
                "progress_percent": pj.progress_percent,
                "error_message": pj.error_message,
                "created_at": pj.created_at.isoformat() if pj.created_at else None,
                "updated_at": pj.updated_at.isoformat() if pj.updated_at else None,
            }
            for pj in proc_jobs
        ],
        "candidates": [
            {
                "id": c.id,
                "name": c.name,
                "processing_status": c.processing_status or "COMPLETED",
                "processing_error": c.processing_error,
            }
            for c in candidates
        ],
    }

@router.get("/job/{job_id}")
def get_job_processing_summary(job_id: int, db: Session = Depends(get_db)):
    """Alias for /status/{job_id} conforming to API naming conventions."""
    return get_processing_status(job_id=job_id, db=db)

@router.post("/retry/{candidate_id}")
def retry_candidate_analysis(candidate_id: int, db: Session = Depends(get_db)):
    """
    Retries failed analysis for a candidate without requiring re-upload.
    Re-uses stored document text or re-fetches original document from Supabase Storage.
    """
    candidate = db.query(orm.Candidate).filter(orm.Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    resume = db.query(orm.Resume).filter(orm.Resume.candidate_id == candidate_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="No resume record found for candidate")

    raw_text = resume.raw_text
    # If raw_text was missing/failed, attempt to download file from Supabase Storage
    if not raw_text or raw_text == "EXTRACTION_FAILED":
        if resume.storage_path:
            try:
                from services.supabase_service import get_supabase_service
                from app.services.parser import extract_text_from_bytes
                file_bytes = get_supabase_service().download_resume_file(resume.storage_path)
                if file_bytes:
                    raw_text, detected_type = extract_text_from_bytes(file_bytes, resume.file_name)
                    resume.raw_text = raw_text
                    db.commit()
            except Exception as dl_err:
                logger.warning(f"Could not re-download document: {dl_err}")

    if not raw_text or raw_text == "EXTRACTION_FAILED":
        raise HTTPException(status_code=422, detail="Document text unavailable for retry. Please upload again.")

    try:
        candidate.processing_status = "ANALYZING"
        resume.processing_status = "ANALYZING"
        candidate.processing_error = None
        resume.processing_error = None
        db.commit()

        # Execute matching engine for candidate's job
        if candidate.job_id:
            from app.routes.matching import run_matching_engine
            run_matching_engine({"job_id": candidate.job_id}, db)

        candidate.processing_status = "COMPLETED"
        resume.processing_status = "COMPLETED"
        db.commit()

        match_res = None
        if candidate.job_id:
            match_res = db.query(orm.MatchResult).filter(
                orm.MatchResult.candidate_id == candidate.id,
                orm.MatchResult.job_id == candidate.job_id
            ).first()

        return {
            "success": True,
            "candidate_id": candidate.id,
            "status": "COMPLETED",
            "message": "Analysis successfully retried and completed.",
            "match_score": match_res.overall_match_score if match_res else 0.0,
            "recommendation": match_res.recommendation if match_res else "REVIEW"
        }
    except Exception as e:
        candidate.processing_status = "FAILED"
        candidate.processing_error = str(e)
        resume.processing_status = "FAILED"
        resume.processing_error = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Retry failed: {str(e)}")
