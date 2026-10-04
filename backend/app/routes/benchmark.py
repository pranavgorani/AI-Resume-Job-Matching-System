import logging
from typing import Optional
from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import orm, schemas
from services.benchmark_service import run_50_resume_benchmark

logger = logging.getLogger("talentproof.benchmark_route")
router = APIRouter(prefix="/api/benchmark", tags=["Benchmark"])

@router.post("/run", response_model=schemas.BenchmarkRunResponse)
def run_benchmark_endpoint(
    payload: dict = Body(default={}),
    db: Session = Depends(get_db)
):
    """
    Developer / Admin benchmark endpoint:
    Executes 50 synthetic resume analyses with reproducible seed,
    stress-testing the evidence-first pipeline, PostgreSQL persistence, and scoring determinism.
    """
    seed = payload.get("seed", 12345)
    try:
        results = run_50_resume_benchmark(seed=seed, db=db)
        return results
    except Exception as e:
        logger.error(f"[BENCHMARK ERROR] {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Benchmark execution failed: {str(e)}")

@router.get("/latest")
def get_latest_benchmark(db: Session = Depends(get_db)):
    """
    Returns the most recent benchmark run results from PostgreSQL.
    """
    latest = (
        db.query(orm.AnalysisRun)
        .filter(orm.AnalysisRun.benchmark_run_id.isnot(None))
        .order_by(orm.AnalysisRun.created_at.desc())
        .first()
    )
    if not latest:
        return {"has_run": False, "message": "No benchmark runs recorded yet."}
    
    return {
        "has_run": True,
        "run_id": latest.id,
        "job_id": latest.job_id,
        "seed": latest.seed,
        "total": latest.total_candidates,
        "completed": latest.completed_count,
        "failed": latest.failed_count,
        "summary": latest.results_summary,
        "created_at": latest.created_at.isoformat() if latest.created_at else None
    }
