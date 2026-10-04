import re
from typing import List, Dict, Any, Tuple
from app.services.transferable_engine import find_transferable_match

def build_evidence_graph(
    requirements: List[Dict[str, Any]],
    candidate_data: Dict[str, Any],
    risk_flags: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Constructs the Evidence Graph mapping each Job Requirement to Candidate Evidence:
    JOB REQUIREMENT -> CANDIDATE CLAIM -> RESUME EVIDENCE -> EVIDENCE STRENGTH
    
    Status / Colors:
    GREEN  = HIGH (Strongly supported)
    YELLOW = PARTIAL (Partially supported / Transferable)
    RED    = WEAK_MISSING (Missing / weak evidence)
    PURPLE = CONTRADICTORY (Contradictory / suspicious claim)
    """
    evidence_items = []
    
    experiences = candidate_data.get("experiences", [])
    projects = candidate_data.get("projects", [])
    skills = [s.get("name", "") for s in candidate_data.get("skills", [])]
    total_exp = float(candidate_data.get("total_experience_years", 0.0))
    
    # Check if there is an active contradiction flag on any skill
    contradiction_skills = set()
    for flag in risk_flags:
        if flag.get("flag_type") == "UNBACKED_EXPERTISE":
            # Extract skill name from details
            for s in skills:
                if s.lower() in flag.get("details", "").lower():
                    contradiction_skills.add(s.lower())
        elif flag.get("flag_type") == "DURATION_MISMATCH":
            contradiction_skills.add("experience")

    for req in requirements:
        req_name = req.get("name", "")
        req_name_clean = req_name.lower()
        req_category = req.get("category", "skill")
        req_tier = req.get("tier", "MUST_HAVE")
        expected_years = float(req.get("expected_years", 0.0))

        # Check for contradictions first (PURPLE)
        if any(cs in req_name_clean for cs in contradiction_skills) or (req_category == "experience" and "experience" in contradiction_skills):
            evidence_items.append({
                "job_requirement_id": req.get("id"),
                "requirement_name": req_name,
                "claim_snippet": f"Claimed advanced competence in {req_name}",
                "evidence_snippet": "Inconsistency detected: Candidate listed expertise in resume skill block, but independent work & project corpora contain zero tangible delivery artifacts.",
                "source_section": "skills",
                "strength": "CONTRADICTORY", # PURPLE
                "evidence_score": 25.0,
                "is_transferable": False,
                "transferable_explanation": None,
                "justification": "Claimed capability lacks empirical backing across reported production responsibilities."
            })
            continue

        # If it's an Experience requirement
        if req_category == "experience" or "experience" in req_name_clean:
            if total_exp >= expected_years:
                strength = "HIGH" # GREEN
                score = min(100.0, 85.0 + (total_exp - expected_years) * 5.0)
                snippet = f"Verified {total_exp:.1f} years total cumulative engineering tenure across {len(experiences)} professional roles."
                justification = f"Exceeds minimum duration threshold of {expected_years:.0f} years."
            elif total_exp >= (expected_years * 0.7):
                strength = "PARTIAL" # YELLOW
                score = 65.0
                snippet = f"Chronological history shows {total_exp:.1f} years verified experience against {expected_years:.0f} years targeted."
                justification = f"Close to target with {expected_years - total_exp:.1f} years delta; high velocity potential."
            else:
                strength = "WEAK_MISSING" # RED
                score = 35.0
                snippet = f"Total substantiated chronology stands at {total_exp:.1f} years."
                justification = f"Significant duration gap ({expected_years - total_exp:.1f} years below requested tenure)."

            evidence_items.append({
                "job_requirement_id": req.get("id"),
                "requirement_name": req_name,
                "claim_snippet": f"{total_exp:.1f} years professional experience",
                "evidence_snippet": snippet,
                "source_section": "experience",
                "strength": strength,
                "evidence_score": score,
                "is_transferable": False,
                "transferable_explanation": None,
                "justification": justification
            })
            continue

        # Search direct evidence across experiences and projects
        matching_experiences = []
        for exp in experiences:
            exp_text = f"{exp.get('company', '')} {exp.get('role', '')} {' '.join(exp.get('responsibilities', []))} {' '.join(exp.get('technologies', []))}".lower()
            if re.search(r'\b' + re.escape(req_name_clean) + r'\b', exp_text):
                matching_experiences.append(exp)

        matching_projects = []
        for proj in projects:
            proj_text = f"{proj.get('title', '')} {proj.get('description', '')} {' '.join(proj.get('technologies', []))} {proj.get('contribution', '')}".lower()
            if re.search(r'\b' + re.escape(req_name_clean) + r'\b', proj_text):
                matching_projects.append(proj)

        # Check direct match
        has_direct_skill = any(req_name_clean == s.lower() or req_name_clean in s.lower() for s in skills)

        if matching_experiences and matching_projects:
            # Strongest evidence: Both real company role AND tangible project
            evidence_items.append({
                "job_requirement_id": req.get("id"),
                "requirement_name": req_name,
                "claim_snippet": f"Proficient in {req_name}",
                "evidence_snippet": f"Production usage at {matching_experiences[0].get('company')} as {matching_experiences[0].get('role')} + Key project '{matching_projects[0].get('title')}': {matching_projects[0].get('description')}",
                "source_section": "experience + projects",
                "strength": "HIGH", # GREEN
                "evidence_score": 94.0,
                "is_transferable": False,
                "transferable_explanation": None,
                "justification": f"Substantiated by verified workplace responsibilities and concrete production project delivery."
            })
        elif matching_experiences:
            # Good evidence from company experience
            evidence_items.append({
                "job_requirement_id": req.get("id"),
                "requirement_name": req_name,
                "claim_snippet": f"Workplace experience in {req_name}",
                "evidence_snippet": f"Deployed at {matching_experiences[0].get('company')} ({matching_experiences[0].get('start_date')}-{matching_experiences[0].get('end_date')}): {matching_experiences[0].get('responsibilities', [''])[0]}",
                "source_section": "experience",
                "strength": "HIGH", # GREEN
                "evidence_score": 86.0,
                "is_transferable": False,
                "transferable_explanation": None,
                "justification": "Direct production usage verified in professional career timeline."
            })
        elif matching_projects:
            # Good evidence from dedicated projects
            evidence_items.append({
                "job_requirement_id": req.get("id"),
                "requirement_name": req_name,
                "claim_snippet": f"Hands-on project competence in {req_name}",
                "evidence_snippet": f"Engineered in '{matching_projects[0].get('title')}': {matching_projects[0].get('description')} ({matching_projects[0].get('results_metrics', 'Active deployment')})",
                "source_section": "projects",
                "strength": "HIGH" if req_tier != "MUST_HAVE" else "PARTIAL", # GREEN or YELLOW
                "evidence_score": 80.0,
                "is_transferable": False,
                "transferable_explanation": None,
                "justification": "Substantiated through concrete codebase project implementation."
            })
        elif has_direct_skill:
            # Candidate claims skill, but no projects/exp explicitly describe it in depth
            evidence_items.append({
                "job_requirement_id": req.get("id"),
                "requirement_name": req_name,
                "claim_snippet": f"Lists {req_name} in core technical competencies",
                "evidence_snippet": f"Skill listed in candidate profile, but limited detailed implementation bullets found in resume body.",
                "source_section": "skills",
                "strength": "PARTIAL", # YELLOW
                "evidence_score": 58.0,
                "is_transferable": False,
                "transferable_explanation": None,
                "justification": "Mentioned in resume profile without extensive descriptive project metrics."
            })
        else:
            # Check Transferable skill
            transferable = find_transferable_match(req_name, skills)
            if transferable:
                evidence_items.append({
                    "job_requirement_id": req.get("id"),
                    "requirement_name": req_name,
                    "claim_snippet": f"Demonstrated background in {transferable['alternative_skill']}",
                    "evidence_snippet": f"{transferable['explanation']}",
                    "source_section": "transferable_skills",
                    "strength": "PARTIAL", # YELLOW
                    "evidence_score": round(transferable["transfer_factor"] * 85.0, 1),
                    "is_transferable": True,
                    "transferable_explanation": transferable["explanation"],
                    "justification": f"Candidate lacks direct {req_name} evidence, but has strong {transferable['alternative_skill']} background that transfers with high velocity."
                })
            else:
                # Missing (RED)
                evidence_items.append({
                    "job_requirement_id": req.get("id"),
                    "requirement_name": req_name,
                    "claim_snippet": "No claim found",
                    "evidence_snippet": f"Zero direct or transferable mentions of {req_name} identified in resume document.",
                    "source_section": "none",
                    "strength": "WEAK_MISSING", # RED
                    "evidence_score": 0.0,
                    "is_transferable": False,
                    "transferable_explanation": None,
                    "justification": f"Unaddressed requirement. Recruiter follow-up or training plan required."
                })

    return evidence_items
