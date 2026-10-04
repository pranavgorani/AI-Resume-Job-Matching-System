from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import orm

router = APIRouter(prefix="/api/export", tags=["Export"])

@router.get("/candidate/{candidate_id}")
def export_candidate_report(candidate_id: int, db: Session = Depends(get_db)):
    cand = db.query(orm.Candidate).filter(orm.Candidate.id == candidate_id).first()
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found")

    match = db.query(orm.MatchResult).filter(orm.MatchResult.candidate_id == candidate_id).first()
    
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>TalentProof AI — Candidate Match Intelligence Report — {cand.name}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 40px; color: #1e293b; line-height: 1.6; max-width: 900px; margin: auto; }}
  .header {{ border-bottom: 2px solid #e2e8f0; padding-bottom: 20px; margin-bottom: 30px; }}
  .badge {{ display: inline-block; padding: 4px 12px; border-radius: 9999px; font-weight: 600; font-size: 12px; }}
  .badge-green {{ background: #dcfce7; color: #166534; }}
  .badge-purple {{ background: #f3e8ff; color: #6b21a8; }}
  .card {{ border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin-bottom: 20px; }}
  .score-box {{ font-size: 32px; font-weight: 800; color: #0284c7; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
  th, td {{ text-align: left; padding: 10px; border-bottom: 1px solid #f1f5f9; }}
  th {{ background: #f8fafc; font-size: 13px; text-transform: uppercase; color: #64748b; }}
</style>
</head>
<body>
  <div class="header">
    <div style="font-size: 13px; font-weight: 700; color: #0284c7; letter-spacing: 1px;">TALENTPROOF AI INTELLIGENCE DOSSIER</div>
    <h1 style="margin: 6px 0;">{cand.name}</h1>
    <div>{cand.email or ''} • {cand.location or ''} • {cand.total_experience_years} Years Experience</div>
  </div>

  <div style="display: flex; gap: 20px; margin-bottom: 30px;">
    <div class="card" style="flex: 1;">
      <div style="font-size: 12px; color: #64748b;">OVERALL MATCH</div>
      <div class="score-box">{match.overall_match_score if match else 75}%</div>
      <div style="font-weight: 600; margin-top: 4px;">{match.recommendation if match else 'CONSIDER'}</div>
    </div>
    <div class="card" style="flex: 1;">
      <div style="font-size: 12px; color: #64748b;">EVIDENCE CONFIDENCE</div>
      <div class="score-box" style="color: #059669;">{match.evidence_confidence_score if match else 70}%</div>
      <div style="font-size: 13px; color: #64748b;">Non-keyword grounded</div>
    </div>
    <div class="card" style="flex: 1;">
      <div style="font-size: 12px; color: #64748b;">HIRING CONFIDENCE</div>
      <div class="score-box" style="color: #d97706;">{match.hiring_confidence_score if match else 65}%</div>
      <div style="font-size: 13px; color: #64748b;">Risk-adjusted confidence</div>
    </div>
  </div>

  <h2>Requirement Evidence Mapping</h2>
  <table>
    <thead>
      <tr>
        <th>Requirement</th>
        <th>Strength</th>
        <th>Evidence Snippet</th>
        <th>Score</th>
      </tr>
    </thead>
    <tbody>
"""
    for ev in cand.evidence_items:
        color = "#166534" if ev.strength == "HIGH" else ("#854d0e" if ev.strength == "PARTIAL" else ("#6b21a8" if ev.strength == "CONTRADICTORY" else "#991b1b"))
        bg = "#dcfce7" if ev.strength == "HIGH" else ("#fef9c3" if ev.strength == "PARTIAL" else ("#f3e8ff" if ev.strength == "CONTRADICTORY" else "#fee2e2"))
        html += f"""
      <tr>
        <td><strong>{ev.requirement_name}</strong></td>
        <td><span style="background: {bg}; color: {color}; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 700;">{ev.strength}</span></td>
        <td style="font-size: 13px;">{ev.evidence_snippet}</td>
        <td><strong>{ev.evidence_score:.0f}%</strong></td>
      </tr>
"""
    html += """
    </tbody>
  </table>

  <h2 style="margin-top: 40px;">Risk & Verification Flags</h2>
"""
    if cand.risk_flags:
        for rf in cand.risk_flags:
            html += f"""
  <div class="card" style="border-left: 4px solid #f59e0b;">
    <h3 style="margin: 0 0 6px 0; color: #b45309;">⚠ {rf.headline}</h3>
    <p style="margin: 0 0 8px 0; font-size: 14px;">{rf.details}</p>
    <div style="background: #f8fafc; padding: 10px; border-radius: 6px; font-size: 13px; color: #475569;">
      <strong>Recruiter Guidance:</strong> {rf.neutral_recommendation}
    </div>
  </div>
"""
    else:
        html += "<p style='color: #059669;'>✓ No timeline overlaps, unbacked expertise, or duration inconsistencies detected.</p>"

    html += """
  <h2 style="margin-top: 40px;">Generated Interview Questions</h2>
"""
    for iq in cand.interview_questions:
        html += f"""
  <div class="card">
    <div style="font-size: 11px; font-weight: 700; color: #0284c7; text-transform: uppercase;">{iq.category} — {iq.target_requirement or 'Core Competency'}</div>
    <p style="font-size: 15px; font-weight: 600; margin: 8px 0;">"{iq.question}"</p>
    <div style="font-size: 13px; color: #64748b;"><strong>Focus:</strong> {iq.suggested_focus}</div>
  </div>
"""

    html += """
  <footer style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #e2e8f0; font-size: 12px; color: #94a3b8; text-align: center;">
    Generated by TalentProof AI • Evidence-First Candidate Intelligence Platform • Fair Match Compliant
  </footer>
</body>
</html>
"""
    return Response(content=html, media_type="text/html")
