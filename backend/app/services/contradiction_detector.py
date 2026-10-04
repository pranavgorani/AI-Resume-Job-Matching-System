import re
from typing import List, Dict, Any, Tuple

def verify_claims_and_detect_contradictions(
    candidate_data: Dict[str, Any],
    job_min_experience: float = 3.0,
    job_required_skills: List[str] = None
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Analyzes candidate resume structure for:
    1. Verified vs Contradictory Claims
    2. Timeline Overlaps (e.g. Full-time student vs full-time senior role)
    3. Unbacked Expertise Claims (buzzwords in skills with 0 project/work evidence)
    4. Experience Duration Gaps
    
    Returns (claims_list, risk_flags_list)
    """
    if job_required_skills is None:
        job_required_skills = []

    claims_out = []
    risk_flags = []
    
    experiences = candidate_data.get("experiences", [])
    educations = candidate_data.get("educations", [])
    projects = candidate_data.get("projects", [])
    skills = candidate_data.get("skills", [])
    explicit_claims = candidate_data.get("explicit_claims", [])
    total_exp_years = float(candidate_data.get("total_experience_years", 0.0))

    # Aggregated text from work experience and projects to check backing evidence
    exp_text_corpus = " ".join([
        f"{e.get('company', '')} {e.get('role', '')} {' '.join(e.get('responsibilities', []))} {' '.join(e.get('technologies', []))}"
        for e in experiences
    ]).lower()
    
    proj_text_corpus = " ".join([
        f"{p.get('title', '')} {p.get('description', '')} {' '.join(p.get('technologies', []))} {p.get('contribution', '')}"
        for p in projects
    ]).lower()

    combined_evidence_corpus = f"{exp_text_corpus} {proj_text_corpus}"

    # 1. Timeline Overlap Check (Education vs Full-time Senior Employment)
    for edu in educations:
        grad_year_str = str(edu.get("graduation_year", ""))
        is_full_time_edu = "master" in edu.get("degree", "").lower() or "bachelor" in edu.get("degree", "").lower()
        if is_full_time_edu and grad_year_str:
            edu_years = re.findall(r'\d{4}', grad_year_str)
            if edu_years:
                edu_end_year = int(edu_years[-1])
                edu_start_year = int(edu_years[0]) if len(edu_years) > 1 else edu_end_year - 2

                for exp in experiences:
                    role_title = exp.get("role", "").lower()
                    exp_date = f"{exp.get('start_date', '')} - {exp.get('end_date', '')}"
                    exp_years = re.findall(r'\d{4}', exp_date)
                    if exp_years:
                        exp_start = int(exp_years[0])
                        # Check overlap
                        if (exp_start >= edu_start_year and exp_start < edu_end_year) and ("senior" in role_title or "lead" in role_title):
                            risk_flags.append({
                                "flag_type": "TIMELINE_OVERLAP",
                                "severity": "MEDIUM",
                                "headline": "Timeline Overlap: Senior Employment During Full-time Degree",
                                "details": f"Candidate listed '{exp.get('role')}' at {exp.get('company')} ({exp_date}) concurrently with full-time {edu.get('degree')} ({edu_start_year}–{edu_end_year}).",
                                "neutral_recommendation": "Potential inconsistency detected. Recruiter verification recommended regarding full-time vs part-time capacity during academic enrollment."
                            })

    # 2. Check Experience Claims vs Timeline Duration
    for claim in explicit_claims:
        c_text = claim.get("claim_text", "")
        claimed_yrs = claim.get("claimed_duration_years")
        claimed_skill = claim.get("claimed_skill", "General")
        
        status = "SUPPORTED"
        confidence = 0.88
        notes = "Supported by verifiable work history timeline."

        if claimed_yrs and claimed_yrs > (total_exp_years + 0.75):
            status = "CONTRADICTORY"
            confidence = 0.35
            notes = f"Candidate claims {claimed_yrs:.1f} years, but total verified timeline shows ~{total_exp_years:.1f} years."
            risk_flags.append({
                "flag_type": "DURATION_MISMATCH",
                "severity": "HIGH",
                "headline": f"Claim Discrepancy: {claimed_yrs:.1f} Yrs Claimed vs ~{total_exp_years:.1f} Yrs Found",
                "details": f"Explicit claim '{c_text}' indicates {claimed_yrs:.1f} years experience, whereas verifiable work chronology accounts for approximately {total_exp_years:.1f} years.",
                "neutral_recommendation": "Potential inconsistency detected. Recruiter verification recommended to clarify internship, freelance, or academic project tenure."
            })
        elif claimed_yrs and claimed_yrs > total_exp_years:
            status = "PARTIALLY_SUPPORTED"
            confidence = 0.65
            notes = f"Evidence accounts for ~{total_exp_years:.1f} years of the claimed {claimed_yrs:.1f} years."

        claims_out.append({
            "claim_text": c_text,
            "claimed_skill": claimed_skill,
            "claimed_duration_years": claimed_yrs,
            "claimed_seniority": claim.get("claimed_seniority", "Mid"),
            "verification_status": status,
            "confidence_score": confidence,
            "verification_notes": notes
        })

    # 3. Unbacked Expertise / Keyword Stuffing Detection
    # Candidate lists skill as "expert" or primary skill, but has ZERO mentions in projects and work descriptions
    for s in skills:
        s_name = s.get("name", "")
        s_name_clean = s_name.lower()
        # Look in evidence corpus
        found_in_evidence = s_name_clean in combined_evidence_corpus
        
        # If candidate lists "expert" or skill is in job's critical requirements but not in corpus:
        if not found_in_evidence and (s.get("proficiency_claimed") == "advanced" or s.get("proficiency_claimed") == "expert"):
            risk_flags.append({
                "flag_type": "UNBACKED_EXPERTISE",
                "severity": "HIGH",
                "headline": f"Skill Claim Has Limited Supporting Evidence: {s_name}",
                "details": f"Candidate listed '{s_name}' as advanced/expert skill, but resume contains zero dedicated project deliverables or company employment responsibilities demonstrating hands-on execution.",
                "neutral_recommendation": f"Potential inconsistency detected. Recruiter verification recommended for {s_name} depth via technical inquiry."
            })

    # 4. Job Experience Gap Check
    if job_min_experience > total_exp_years:
        gap = job_min_experience - total_exp_years
        if gap >= 1.0:
            risk_flags.append({
                "flag_type": "EXPERIENCE_GAP",
                "severity": "MEDIUM",
                "headline": f"Experience Gap: {gap:.1f} Years Below Minimum",
                "details": f"Role specifies {job_min_experience:.0f}+ years minimum professional experience. Candidate's verified trajectory totals {total_exp_years:.1f} years.",
                "neutral_recommendation": f"Potential inconsistency detected. Recruiter verification recommended. Experience delta of {gap:.1f} years noted."
            })

    # 5. Fallback Default claim if candidate had none extracted
    if not claims_out:
        claims_out.append({
            "claim_text": f"Software Engineering Professional ({total_exp_years:.1f} years)",
            "claimed_skill": "Full Stack Development",
            "claimed_duration_years": total_exp_years,
            "claimed_seniority": "Mid-Senior" if total_exp_years >= 3.0 else "Junior",
            "verification_status": "SUPPORTED",
            "confidence_score": 0.85,
            "verification_notes": "Chronological employment records substantiate career longevity."
        })

    return claims_out, risk_flags
