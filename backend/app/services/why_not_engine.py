from typing import List, Dict, Any, Optional

def generate_why_not_analysis(
    candidate_id: int,
    candidate_name: str,
    candidate_match_score: float,
    evidence_items: List[Dict[str, Any]],
    risk_flags: List[Dict[str, Any]],
    top_candidate: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Computes deep 'Why Not This Candidate?' decision intelligence:
    - What barriers prevent them from securing the #1 spot
    - What evidence would fundamentally reverse this evaluation
    - Head-to-head delta against the top-ranked candidate
    """
    barriers = []
    evidence_needed = []
    
    # 1. Missing Must-Haves
    missing_items = [e for e in evidence_items if e.get("strength") == "WEAK_MISSING"]
    for m in missing_items:
        barriers.append(f"Missing direct evidence for critical requirement: {m.get('requirement_name')}")
        evidence_needed.append(f"Demonstrable code repository, live production URL, or architectural design doc proving hands-on {m.get('requirement_name')} deployment.")

    # 2. Risk Flags & Contradictions
    for f in risk_flags:
        barriers.append(f"{f.get('headline')} ({f.get('severity')} severity)")
        if f.get("flag_type") == "DURATION_MISMATCH":
            evidence_needed.append("Clarification / recommendation letter verifying start/end dates for past contracts or independent engagements.")
        elif f.get("flag_type") == "UNBACKED_EXPERTISE":
            evidence_needed.append("Live technical walkthrough or coding sample demonstrating production utilization of the claimed skill.")

    # 3. Transferable but not native
    transferable_items = [e for e in evidence_items if e.get("is_transferable")]
    for t in transferable_items:
        barriers.append(f"Relies on transferable capability ({t.get('claim_snippet')}) rather than native production tenure in {t.get('requirement_name')}.")
        evidence_needed.append(f"Successful completion of a practical take-home or technical pairing session utilizing {t.get('requirement_name')}.")

    if not barriers:
        barriers.append("Candidate is in top contention; minor score variances relate to project scale metrics compared to top peer.")

    if not evidence_needed:
        evidence_needed.append("Detailed walkthrough of system scale metrics (requests/sec, latency, cost optimizations) during technical interview.")

    # 4. Outranking comparison
    if top_candidate and top_candidate.get("id") != candidate_id:
        top_name = top_candidate.get("name", "Top Candidate")
        top_score = top_candidate.get("match_score", 92.0)
        delta = round(top_score - candidate_match_score, 1)
        tradeoff_summary = (
            f"{top_name} currently outranks {candidate_name} by +{delta}% match points. "
            f"While {candidate_name} shows strong fundamentals, {top_name} provides unflagged, verified production evidence across all core Must-Have technologies."
        )
    else:
        tradeoff_summary = f"{candidate_name} is currently the highest-ranked candidate in this requisition pool."

    return {
        "barriers": barriers,
        "evidence_needed": evidence_needed,
        "tradeoff_summary": tradeoff_summary
    }
