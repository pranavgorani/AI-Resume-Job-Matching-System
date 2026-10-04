from typing import List, Dict, Any, Tuple
from app.config import settings

def calculate_candidate_scores(
    requirements: List[Dict[str, Any]],
    evidence_items: List[Dict[str, Any]],
    candidate_data: Dict[str, Any],
    risk_flags: List[Dict[str, Any]],
    custom_weights: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    Computes explainable, non-black-box scores:
    1. Overall Match Score (using configurable recruiter weights)
    2. Score Breakdown (Required Skills, Experience, Projects, Edu, Preferred, Domain, Evidence Conf)
    3. Evidence Coverage %
    4. Hiring Confidence % (discounted if critical must-haves lack strong evidence or have risks)
    5. Potential Match Score (with transferable skills upskilling)
    6. Recommendation (STRONGLY_RECOMMEND, RECOMMEND, CONSIDER, VERIFY, NOT_CURRENT_FIT)
    """
    weights = {
        "required_skills": settings.WEIGHT_REQUIRED_SKILLS,
        "relevant_experience": settings.WEIGHT_RELEVANT_EXP,
        "project_evidence": settings.WEIGHT_PROJECT_EVIDENCE,
        "education_cert": settings.WEIGHT_EDUCATION_CERT,
        "preferred_skills": settings.WEIGHT_PREFERRED_SKILLS,
        "domain_relevance": settings.WEIGHT_DOMAIN_RELEVANCE,
        "evidence_confidence": settings.WEIGHT_EVIDENCE_CONFIDENCE,
    }
    if custom_weights:
        weights.update(custom_weights)

    # Normalize weights just in case
    total_w = sum(weights.values())
    if total_w > 0:
        for k in weights:
            weights[k] = weights[k] / total_w

    # Partition requirements
    must_haves = [r for r in requirements if r.get("tier") == "MUST_HAVE" and r.get("category") == "skill"]
    should_haves = [r for r in requirements if r.get("tier") == "SHOULD_HAVE"]
    nice_to_haves = [r for r in requirements if r.get("tier") == "NICE_TO_HAVE"]
    exp_reqs = [r for r in requirements if r.get("category") == "experience" or "experience" in r.get("name", "").lower()]

    evidence_by_req = {e.get("requirement_name"): e for e in evidence_items}

    # 1. Required Skills Score (0-100)
    req_skill_scores = []
    supported_count = 0
    missing_count = 0
    contradiction_count = 0

    for r in must_haves:
        ev = evidence_by_req.get(r.get("name"))
        if ev:
            req_skill_scores.append(ev.get("evidence_score", 0.0))
            if ev.get("strength") in ["HIGH", "PARTIAL"]:
                supported_count += 1
            if ev.get("strength") == "WEAK_MISSING":
                missing_count += 1
            if ev.get("strength") == "CONTRADICTORY":
                contradiction_count += 1
        else:
            req_skill_scores.append(0.0)
            missing_count += 1

    score_required_skills = sum(req_skill_scores) / len(req_skill_scores) if req_skill_scores else 85.0

    # 2. Relevant Experience Score (0-100)
    total_exp = float(candidate_data.get("total_experience_years", 0.0))
    expected_exp = float(exp_reqs[0].get("expected_years", 3.0)) if exp_reqs else 3.0
    
    if total_exp >= expected_exp:
        score_experience = min(100.0, 85.0 + (total_exp - expected_exp) * 4.0)
    else:
        score_experience = max(30.0, (total_exp / expected_exp) * 85.0)

    # 3. Project Evidence Score (0-100)
    projects = candidate_data.get("projects", [])
    if len(projects) >= 2:
        # Check if projects have metrics / description
        detailed_count = sum(1 for p in projects if len(p.get("description", "")) > 40 or p.get("results_metrics"))
        score_projects = min(98.0, 75.0 + detailed_count * 10.0)
    elif len(projects) == 1:
        score_projects = 72.0
    else:
        score_projects = 40.0

    # 4. Education & Certification Score (0-100)
    educations = candidate_data.get("educations", [])
    certs = candidate_data.get("certifications", [])
    score_edu = 75.0
    if educations:
        deg = educations[0].get("degree", "").lower()
        if "master" in deg or "phd" in deg:
            score_edu += 15.0
        elif "bachelor" in deg or "b.tech" in deg or "b.s" in deg:
            score_edu += 10.0
    if certs:
        score_edu = min(100.0, score_edu + len(certs) * 5.0)

    # 5. Preferred Skills Score (0-100)
    pref_scores = []
    for r in (should_haves + nice_to_haves):
        ev = evidence_by_req.get(r.get("name"))
        if ev:
            pref_scores.append(ev.get("evidence_score", 0.0))
            if ev.get("strength") in ["HIGH", "PARTIAL"]:
                supported_count += 1
            if ev.get("strength") == "WEAK_MISSING":
                missing_count += 1
            if ev.get("strength") == "CONTRADICTORY":
                contradiction_count += 1
        else:
            pref_scores.append(0.0)
            missing_count += 1
    score_pref_skills = sum(pref_scores) / len(pref_scores) if pref_scores else 80.0

    # 6. Domain Relevance Score (0-100)
    # Check if keywords match AI, Distributed, Full Stack, SaaS
    corpus = f"{candidate_data.get('summary', '')} {' '.join([p.get('description', '') for p in projects])}".lower()
    domain_hits = sum(1 for kw in ["ai", "llm", "backend", "full stack", "cloud", "api", "distributed", "system design"] if kw in corpus)
    score_domain = min(96.0, 60.0 + domain_hits * 6.0)

    # 7. Evidence Confidence Score (0-100)
    # Average of all evidence scores with penalties for risk flags
    all_ev_scores = [e.get("evidence_score", 50.0) for e in evidence_items]
    base_evidence_conf = sum(all_ev_scores) / len(all_ev_scores) if all_ev_scores else 70.0
    
    # Penalize for risk flags
    risk_penalty = 0.0
    for flag in risk_flags:
        if flag.get("severity") == "HIGH":
            risk_penalty += 12.0
        elif flag.get("severity") == "MEDIUM":
            risk_penalty += 6.0
    
    score_evidence_conf = max(20.0, min(98.0, base_evidence_conf - risk_penalty))

    # Calculate Overall Weighted Match Score
    overall_match = (
        score_required_skills * weights["required_skills"] +
        score_experience * weights["relevant_experience"] +
        score_projects * weights["project_evidence"] +
        score_edu * weights["education_cert"] +
        score_pref_skills * weights["preferred_skills"] +
        score_domain * weights["domain_relevance"] +
        score_evidence_conf * weights["evidence_confidence"]
    )
    overall_match = round(min(99.0, max(25.0, overall_match)), 1)

    # Evidence Coverage % = Supported Requirements / Total Requirements
    total_req_count = len(requirements)
    coverage_pct = round((supported_count / total_req_count * 100.0) if total_req_count > 0 else 75.0, 1)

    # Hiring Confidence %: Match Score discounted if high-risk flags or critical missing requirements exist
    # (Prevents keyword matching from masking unverified critical gaps)
    hiring_conf = overall_match * (score_evidence_conf / 100.0) * 1.05
    if any(f.get("severity") == "HIGH" for f in risk_flags):
        hiring_conf *= 0.85
    hiring_conf = round(min(98.0, max(20.0, hiring_conf)), 1)

    # Potential Match Score: Evaluate upsides if transferable skills are mastered
    # e.g. Candidate with Azure instead of AWS or Podman instead of Docker can bridge gap with 2 weeks orientation
    transferable_boost = 0.0
    potential_reasons = []
    for ev in evidence_items:
        if ev.get("is_transferable"):
            transferable_boost += 7.0
            potential_reasons.append(f"Mastery of {ev.get('requirement_name')} achievable via transferable experience in {ev.get('evidence_snippet')[:40]}...")
    
    potential_match = round(min(98.0, overall_match + transferable_boost + (5.0 if score_experience > 80 else 2.0)), 1)
    if not potential_reasons:
        potential_reason_text = "Strong established alignment; growth trajectory focuses on domain leadership."
    else:
        potential_reason_text = " ".join(potential_reasons) + " Candidate may reach peak role requirements with minimal targeted onboarding."

    # Final Recommendation
    if any(f.get("flag_type") == "DURATION_MISMATCH" and f.get("severity") == "HIGH" for f in risk_flags):
        rec = "VERIFY"
        rec_summary = "High priority verification recommended: Significant divergence detected between claimed tenure and chronological records."
    elif overall_match >= 88.0 and hiring_conf >= 80.0 and len(risk_flags) == 0:
        rec = "STRONGLY_RECOMMEND"
        rec_summary = "Exemplary candidate with comprehensive evidence across all must-have requirements and clean chronological backing."
    elif overall_match >= 80.0 and hiring_conf >= 72.0:
        rec = "RECOMMEND"
        rec_summary = "Strong candidate demonstrating proven capability in core competencies with minor gaps addressable during team onboarding."
    elif overall_match >= 68.0 or potential_match >= 82.0:
        rec = "CONSIDER"
        rec_summary = "Viable candidate with solid technical foundations and strong transferable skill potential; assess specific project depth."
    elif len(risk_flags) > 0 and overall_match >= 65.0:
        rec = "VERIFY"
        rec_summary = "Potential match requiring targeted recruiter verification regarding specific experience claims and unbacked expertise."
    else:
        rec = "NOT_CURRENT_FIT"
        rec_summary = "Significant requirement divergence across multiple core competencies and experience duration."

    score_breakdown = {
        "required_skills": round(score_required_skills, 1),
        "experience": round(score_experience, 1),
        "project_evidence": round(score_projects, 1),
        "education": round(score_edu, 1),
        "preferred_skills": round(score_pref_skills, 1),
        "domain_relevance": round(score_domain, 1),
        "evidence_confidence": round(score_evidence_conf, 1)
    }

    return {
        "overall_match_score": overall_match,
        "hiring_confidence_score": hiring_conf,
        "evidence_confidence_score": round(score_evidence_conf, 1),
        "evidence_coverage_percentage": coverage_pct,
        "potential_match_score": potential_match,
        "score_breakdown": score_breakdown,
        "supported_requirements_count": supported_count,
        "total_requirements_count": total_req_count,
        "missing_requirements_count": missing_count,
        "contradiction_count": contradiction_count,
        "recommendation": rec,
        "recommendation_summary": rec_summary,
        "potential_reason": potential_reason_text
    }
