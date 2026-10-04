import datetime
from fastapi import APIRouter, Depends, Query, Response, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from services.reports.report_service import get_analytics_report_data
from services.reports.csv_report import generate_csv_report
from services.reports.pdf_report import generate_pdf_report
from services.reports.docx_report import generate_docx_report

router = APIRouter(prefix="/api/reports", tags=["Reports"])

@router.get("/analytics/data")
def get_analytics_json(
    job_id: Optional[int] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    risk: Optional[str] = Query(None),
    min_score: Optional[float] = Query(None),
    max_score: Optional[float] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Returns full real-time database analytics, KPI metrics, chart distributions,
    and data-grounded AI insights based on active filters.
    """
    return get_analytics_report_data(
        db=db,
        job_id=job_id,
        date_from=date_from,
        date_to=date_to,
        status=status,
        risk=risk,
        min_score=min_score,
        max_score=max_score
    )

@router.get("/analytics/csv")
def download_analytics_csv(
    job_id: Optional[int] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    risk: Optional[str] = Query(None),
    min_score: Optional[float] = Query(None),
    max_score: Optional[float] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Generates and downloads TalentProof_Analytics_Report_YYYY-MM-DD.csv
    matching active filters.
    """
    data = get_analytics_report_data(
        db=db,
        job_id=job_id,
        date_from=date_from,
        date_to=date_to,
        status=status,
        risk=risk,
        min_score=min_score,
        max_score=max_score
    )
    csv_content = generate_csv_report(data)
    today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    filename = f"TalentProof_Analytics_Report_{today}.csv"

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@router.get("/analytics/pdf")
def download_analytics_pdf(
    job_id: Optional[int] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    risk: Optional[str] = Query(None),
    min_score: Optional[float] = Query(None),
    max_score: Optional[float] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Generates and downloads TalentProof_Analytics_Report_YYYY-MM-DD.pdf
    matching active filters.
    """
    data = get_analytics_report_data(
        db=db,
        job_id=job_id,
        date_from=date_from,
        date_to=date_to,
        status=status,
        risk=risk,
        min_score=min_score,
        max_score=max_score
    )
    pdf_bytes = generate_pdf_report(data)
    today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    filename = f"TalentProof_Analytics_Report_{today}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@router.get("/analytics/docx")
def download_analytics_docx(
    job_id: Optional[int] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    risk: Optional[str] = Query(None),
    min_score: Optional[float] = Query(None),
    max_score: Optional[float] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Generates and downloads TalentProof_Analytics_Report_YYYY-MM-DD.docx
    matching active filters.
    """
    data = get_analytics_report_data(
        db=db,
        job_id=job_id,
        date_from=date_from,
        date_to=date_to,
        status=status,
        risk=risk,
        min_score=min_score,
        max_score=max_score
    )
    docx_bytes = generate_docx_report(data)
    today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    filename = f"TalentProof_Analytics_Report_{today}.docx"

    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
