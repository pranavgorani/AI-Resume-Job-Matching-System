import shutil
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.config import settings
from app.models import orm
from app.services.parser import extract_text_from_file
from app.services.resume_intelligence import extract_resume_data

router = APIRouter(prefix="/api/resumes", tags=["Resumes"])

@router.post("/upload")
async def upload_single_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Accepts PDF, DOCX, or TXT resume, parses content, and registers candidate.
    """
    ext = Path(file.filename).suffix.lower()
    if ext not in [".pdf", ".docx", ".doc", ".txt", ".md"]:
        raise HTTPException(status_code=400, detail=f"Unsupported file format: {ext}. Please upload PDF, DOCX, or TXT.")

    file_id = str(uuid.uuid4())[:8]
    safe_name = f"{file_id}_{file.filename}"
    save_path = settings.UPLOAD_DIR / safe_name

    # Read file bytes for storage and processing
    try:
        file_bytes = await file.read()
        with open(save_path, "wb") as buffer:
            buffer.write(file_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Extract text from document
    try:
        raw_text, detected_type = extract_text_from_file(save_path)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not parse document: {str(e)}")

    if not raw_text or len(raw_text.strip()) < 30:
        raise HTTPException(status_code=422, detail="Document text is empty or contains insufficient content.")

    # Upload to Supabase Storage bucket 'resumes'
    from services.supabase_service import get_supabase_service
    from services.ai import get_resume_analyzer, get_embedding_service
    
    storage_info = get_supabase_service().upload_resume_pdf(file_bytes, file.filename)

    # Extract structured candidate data using ResumeAnalyzer + resume_intelligence
    extracted = extract_resume_data(raw_text)
    try:
        ai_extracted = get_resume_analyzer().analyze(raw_text)
        if ai_extracted.get("name") and ai_extracted["name"] != "Unknown Candidate":
            extracted["name"] = ai_extracted["name"]
        if ai_extracted.get("email"):
            extracted["email"] = ai_extracted["email"]
        if ai_extracted.get("phone"):
            extracted["phone"] = ai_extracted["phone"]
        if ai_extracted.get("years_of_experience"):
            extracted["total_experience_years"] = ai_extracted["years_of_experience"]
        if ai_extracted.get("skills"):
            # Merge unique skills
            existing_skill_names = {s.get("name", "").lower() for s in extracted.get("skills", [])}
            for sk in ai_extracted["skills"]:
                if sk.lower() not in existing_skill_names:
                    extracted.setdefault("skills", []).append({
                        "name": sk,
                        "category": "technical",
                        "years_of_experience": 2.0,
                        "proficiency_claimed": "proficient"
                    })
    except Exception as ai_err:
        pass

    # Persist Candidate
    candidate = orm.Candidate(
        name=extracted.get("name", "Unknown Candidate"),
        email=extracted.get("email"),
        phone=extracted.get("phone"),
        location=extracted.get("location"),
        linkedin=extracted.get("linkedin"),
        github=extracted.get("github"),
        portfolio=extracted.get("portfolio"),
        summary=extracted.get("summary"),
        total_experience_years=float(extracted.get("total_experience_years", 3.0))
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    # Persist Resume record with Supabase Storage metadata
    resume_rec = orm.Resume(
        candidate_id=candidate.id,
        file_name=file.filename,
        file_path=storage_info.get("storage_path", str(save_path)),
        file_type=detected_type,
        raw_text=raw_text,
        parsed_json={
            **extracted,
            "supabase_file_url": storage_info.get("file_url"),
            "storage_provider": storage_info.get("storage_provider")
        }
    )
    db.add(resume_rec)

    # Generate pgvector embedding for candidate summary & skills
    try:
        skill_text = ", ".join([s.get("name", "") for s in extracted.get("skills", [])])
        embed_content = f"{candidate.name} | {candidate.summary or ''} | Skills: {skill_text}"
        embedding_vec = get_embedding_service().get_embedding(embed_content)
        get_supabase_service().store_embedding(
            entity_type="candidate",
            entity_id=str(candidate.id),
            content=embed_content,
            embedding=embedding_vec
        )
    except Exception:
        pass

    # Persist Experience, Education, Skills, Projects, Certifications, Claims
    for exp in extracted.get("experiences", []):
        db.add(orm.CandidateExperience(
            candidate_id=candidate.id,
            company=exp.get("company", "Company"),
            role=exp.get("role", "Engineer"),
            start_date=exp.get("start_date"),
            end_date=exp.get("end_date"),
            duration_years=float(exp.get("duration_years", 1.0)),
            responsibilities=exp.get("responsibilities", []),
            achievements=exp.get("achievements", []),
            technologies=exp.get("technologies", [])
        ))

    for edu in extracted.get("educations", []):
        db.add(orm.CandidateEducation(
            candidate_id=candidate.id,
            degree=edu.get("degree", "Degree"),
            institution=edu.get("institution", "Institution"),
            graduation_year=str(edu.get("graduation_year", "")),
            field=edu.get("field", ""),
            gpa=str(edu.get("gpa", ""))
        ))

    for s in extracted.get("skills", []):
        db.add(orm.CandidateSkill(
            candidate_id=candidate.id,
            name=s.get("name", "Skill"),
            category=s.get("category", "technical"),
            years_of_experience=float(s.get("years_of_experience", 2.0)),
            proficiency_claimed=s.get("proficiency_claimed", "proficient")
        ))

    for p in extracted.get("projects", []):
        db.add(orm.CandidateProject(
            candidate_id=candidate.id,
            title=p.get("title", "Project"),
            description=p.get("description", ""),
            technologies=p.get("technologies", []),
            contribution=p.get("contribution", ""),
            results_metrics=p.get("results_metrics", "")
        ))

    for c in extracted.get("certifications", []):
        db.add(orm.CandidateCertification(
            candidate_id=candidate.id,
            name=c.get("name", "Certification"),
            issuer=c.get("issuer"),
            issue_date=c.get("issue_date")
        ))

    for cl in extracted.get("explicit_claims", []):
        db.add(orm.CandidateClaim(
            candidate_id=candidate.id,
            claim_text=cl.get("claim_text", ""),
            claimed_skill=cl.get("claimed_skill"),
            claimed_duration_years=cl.get("claimed_duration_years"),
            claimed_seniority=cl.get("claimed_seniority"),
            verification_status="SUPPORTED",
            confidence_score=0.85
        ))

    db.commit()

    return {
        "status": "success",
        "message": f"Successfully parsed and registered candidate {candidate.name}",
        "candidate_id": candidate.id,
        "name": candidate.name,
        "skills_detected": len(extracted.get("skills", [])),
        "total_experience_years": candidate.total_experience_years
    }

@router.post("/batch")
async def upload_batch_resumes(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Uploads and processes multiple resumes simultaneously.
    """
    results = []
    for file in files:
        try:
            res = await upload_single_resume(file, db)
            results.append(res)
        except Exception as e:
            results.append({
                "status": "error",
                "file_name": file.filename,
                "error": str(e)
            })
    return {"processed": len(results), "results": results}
