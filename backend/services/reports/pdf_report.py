import io
import datetime
from typing import Any, Dict
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)

def generate_pdf_report(data: Dict[str, Any]) -> bytes:
    """
    Generates a professional 12-section PDF report using ReportLab.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=26,
        leading=32,
        textColor=colors.HexColor("#0f172a"),
        alignment=0
    )
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=13,
        leading=18,
        textColor=colors.HexColor("#6366f1"),
        alignment=0
    )
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=20,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=14,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'ReportBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155")
    )
    bold_body = ParagraphStyle(
        'ReportBodyBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1e1b4b")
    )

    story = []

    # -------------------------------------------------------------
    # COVER / HEADER
    # -------------------------------------------------------------
    story.append(Paragraph("TALENTPROOF AI", ParagraphStyle('Brand', fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor("#4f46e5"), spaceAfter=4)))
    story.append(Paragraph("Recruitment Intelligence Analytics Report", title_style))
    story.append(Paragraph("Evidence-Based Talent Matching • Deterministic Scoring Engine • Anti-Hallucination Verified", subtitle_style))
    story.append(Spacer(1, 10))

    meta_text = f"<b>Date:</b> {data.get('date_generated', datetime.datetime.utcnow().strftime('%Y-%m-%d'))} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Position:</b> {data.get('job_title', 'All Positions')} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Total Evaluated:</b> {len(data.get('candidates', []))} Candidates"
    story.append(Paragraph(meta_text, body_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#cbd5e1"), spaceAfter=14))

    # -------------------------------------------------------------
    # 1. EXECUTIVE SUMMARY
    # -------------------------------------------------------------
    story.append(Paragraph("1. Executive Summary", section_heading))
    kpis = data.get("kpis", {})
    exec_summary = f"""
    This executive report provides an audited intelligence synthesis of <b>{kpis.get('total_candidates', 0)} candidates</b> evaluated for <b>{data.get('job_title', 'the role')}</b>. 
    Rather than relying on ungrounded resume keyword matches, TalentProof AI employs an <b>Evidence-First Verification Graph</b> 
    substantiating claims against demonstrable project deliverables and chronological employment history. 
    The candidate pool displays an average match score of <b>{kpis.get('average_match', 0)}%</b> with 
    an average evidence confidence of <b>{kpis.get('average_evidence', 0)}%</b>. 
    Currently, <b>{kpis.get('shortlist_rate', 0)}%</b> of candidates meet or exceed the bar for positive recommendation, 
    while <b>{kpis.get('verification_rate', 0)}%</b> require recruiter inquiry regarding potential chronological or claim discrepancies.
    """
    story.append(Paragraph(exec_summary.strip(), body_style))
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # 2. KPI OVERVIEW TABLE
    # -------------------------------------------------------------
    story.append(Paragraph("2. Key Performance Indicators", section_heading))
    kpi_data = [
        ["Total Candidates", f"{kpis.get('total_candidates', 0)}", "Average Match Score", f"{kpis.get('average_match', 0)}%"],
        ["Average Evidence Score", f"{kpis.get('average_evidence', 0)}%", "Hiring Confidence", f"{kpis.get('average_hiring_confidence', 0)}%"],
        ["Shortlist Rate", f"{kpis.get('shortlist_rate', 0)}%", "Verification Rate", f"{kpis.get('verification_rate', 0)}%"],
        ["High Risk Candidates", f"{kpis.get('high_risk_candidates', 0)}", "Average Experience", f"{kpis.get('average_experience', 0)} yrs"],
    ]
    kpi_table = Table(kpi_data, colWidths=[140, 110, 150, 130])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor("#4f46e5")),
        ('TEXTCOLOR', (3, 0), (3, -1), colors.HexColor("#059669")),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 12))

    # -------------------------------------------------------------
    # 3. CANDIDATE RANKING TABLE
    # -------------------------------------------------------------
    story.append(Paragraph("3. Candidate Ranking & Score Breakdown", section_heading))
    table_header = ["Rank", "Candidate", "Match", "Evidence", "Hiring Conf.", "Exp.", "Risk", "Recommendation"]
    table_rows = [table_header]
    
    for i, c in enumerate(data.get("candidates", [])[:15], 1):
        table_rows.append([
            f"#{i}",
            c.get("candidate_name", "Candidate"),
            f"{c.get('match_score', 0)}%",
            f"{c.get('evidence_score', 0)}%",
            f"{c.get('hiring_confidence', 0)}%",
            f"{c.get('experience', 0)}y",
            c.get("risk_level", "LOW"),
            c.get("recommendation", "CONSIDER").replace("_", " ")
        ])

    rank_table = Table(table_rows, colWidths=[35, 135, 55, 60, 75, 45, 55, 75])
    rank_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (2, 0), (5, -1), 'CENTER'),
    ]))
    story.append(rank_table)
    story.append(Spacer(1, 14))

    # -------------------------------------------------------------
    # 4 & 5. MATCH & EVIDENCE SCORE DISTRIBUTIONS
    # -------------------------------------------------------------
    story.append(Paragraph("4. Match & Evidence Score Distributions", section_heading))
    dists = data.get("distributions", {})
    match_dist = dists.get("match_distribution", {})
    ev_dist = dists.get("evidence_distribution", {})

    dist_rows = [
        ["Score Tier", "Candidate Count (Match)", "Candidate Count (Evidence)"],
        ["90–100% (Exceptional)", str(match_dist.get("90-100", 0)), str(ev_dist.get("90-100", 0))],
        ["80–89% (Strong)", str(match_dist.get("80-89", 0)), str(ev_dist.get("80-89", 0))],
        ["70–79% (Qualified)", str(match_dist.get("70-79", 0)), str(ev_dist.get("70-79", 0))],
        ["60–69% (Moderate)", str(match_dist.get("60-69", 0)), str(ev_dist.get("60-69", 0))],
        ["Below 60% (Unqualified)", str(match_dist.get("Below 60", 0)), str(ev_dist.get("Below 60", 0))],
    ]
    dist_table = Table(dist_rows, colWidths=[200, 165, 165])
    dist_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#334155")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(dist_table)
    story.append(Spacer(1, 12))

    # -------------------------------------------------------------
    # 6. SKILL ANALYSIS
    # -------------------------------------------------------------
    story.append(Paragraph("5. Top Verified Candidate Skills", section_heading))
    top_skills = dists.get("top_skills", [])
    if top_skills:
        skill_header = ["Technical Skill", "Verified Candidate Count", "Prevalence in Active Pool"]
        skill_rows = [skill_header]
        total_cand = max(1, len(data.get("candidates", [])))
        for s in top_skills[:8]:
            pct = round((s.get("count", 0) / total_cand) * 100)
            skill_rows.append([s.get("skill", ""), str(s.get("count", 0)), f"{pct}%"])
        sk_table = Table(skill_rows, colWidths=[230, 150, 150])
        sk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#475569")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('PADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(sk_table)
    else:
        story.append(Paragraph("No skills indexed for current selection.", body_style))
    story.append(Spacer(1, 12))

    # -------------------------------------------------------------
    # 7 & 8. RISK ANALYSIS & HIRING FUNNEL
    # -------------------------------------------------------------
    story.append(Paragraph("6. Risk Analysis & Hiring Funnel", section_heading))
    risk_d = dists.get("risk_distribution", {})
    funnel_d = dists.get("hiring_funnel", [])

    risk_text = f"<b>Risk Distribution:</b> No Risk: {risk_d.get('No Risk', 0)} &nbsp;|&nbsp; Low Risk: {risk_d.get('Low', 0)} &nbsp;|&nbsp; Medium Risk: {risk_d.get('Medium', 0)} &nbsp;|&nbsp; High Risk: {risk_d.get('High', 0)}"
    story.append(Paragraph(risk_text, body_style))
    story.append(Spacer(1, 6))

    if funnel_d:
        funnel_headers = [f.get("stage") for f in funnel_d]
        funnel_counts = [str(f.get("count")) for f in funnel_d]
        fn_table = Table([funnel_headers, funnel_counts], colWidths=[105] * len(funnel_headers))
        fn_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('PADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(fn_table)
    story.append(Spacer(1, 12))

    # -------------------------------------------------------------
    # 9. CURRENT FIT VS POTENTIAL FIT
    # -------------------------------------------------------------
    story.append(Paragraph("7. Current Fit vs Potential Fit", section_heading))
    fit_summary = """
    TalentProof AI decouples <b>Current Fit</b> (demonstrated production mastery of required tools) 
    from <b>Potential Fit</b> (capability to rapidly ramp up based on transferable skills, such as Azure translating to AWS). 
    Candidates exhibiting high potential deltas represent accelerated hire opportunities at competitive comp bands.
    """
    story.append(Paragraph(fit_summary.strip(), body_style))
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # 10. AI RECRUITMENT INSIGHTS
    # -------------------------------------------------------------
    story.append(Paragraph("8. AI Recruitment Intelligence Insights", section_heading))
    insights = data.get("ai_insights", [])
    for ins in insights:
        story.append(Paragraph(f"• {ins}", body_style))
    story.append(Spacer(1, 12))

    # -------------------------------------------------------------
    # 11. VERIFICATION REQUIRED CANDIDATES
    # -------------------------------------------------------------
    story.append(Paragraph("9. Verification Required Candidates", section_heading))
    verif_candidates = [c for c in data.get("candidates", []) if c.get("verification_status") == "REQUIRED"]
    if verif_candidates:
        verif_data = [["Candidate", "Flags Count", "Potential Inconsistency"]]
        for vc in verif_candidates[:6]:
            details = "; ".join(vc.get("risk_flags_details", [])[:2]) or "Verification recommended"
            verif_data.append([
                vc.get("candidate_name", ""),
                str(vc.get("risk_flags_count", 1)),
                details
            ])
        v_table = Table(verif_data, colWidths=[140, 80, 310])
        v_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#fef3c7")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#92400e")),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#fde68a")),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('PADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(v_table)
    else:
        story.append(Paragraph("✓ All current candidates have verified timelines with zero active contradiction alerts.", body_style))
    story.append(Spacer(1, 12))

    # -------------------------------------------------------------
    # 12. RECOMMENDATIONS & CONCLUSION
    # -------------------------------------------------------------
    story.append(Paragraph("10. Strategic Recommendations", section_heading))
    recs = """
    1. <b>Prioritize Top Ranked Candidates:</b> Proceed immediately with interview rounds for top candidates exhibiting Match Scores above 85% and clean evidence verification graphs.<br/>
    2. <b>Conduct Verification Inquiries:</b> For flagged profiles, ask the neutral verification questions generated by the Interview Intelligence engine to clarify timeline overlaps without bias.<br/>
    3. <b>Leverage Transferable Skills:</b> Candidates possessing complementary technology stacks should be considered for technical screening rather than rejected outright.
    """
    story.append(Paragraph(recs.strip(), body_style))
    story.append(Spacer(1, 16))

    # Footer note
    footer_text = "Generated by TalentProof AI • Evidence-First Candidate Intelligence Platform • Strictly Confidential"
    story.append(Paragraph(footer_text, ParagraphStyle('Footer', fontName='Helvetica-Oblique', fontSize=7.5, textColor=colors.HexColor("#94a3b8"), alignment=1)))

    doc.build(story)
    return buffer.getvalue()
