import csv
import io
import datetime
from typing import Any, Dict

def generate_csv_report(data: Dict[str, Any]) -> str:
    """
    Generates clean CSV report string matching the specified analytics export structure.
    """
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")

    # Header Row
    headers = [
        "Candidate ID",
        "Candidate Name",
        "Job",
        "Match Score",
        "Evidence Score",
        "Hiring Confidence",
        "Current Fit",
        "Potential Fit",
        "Experience",
        "Matched Skills",
        "Missing Skills",
        "Transferable Skills",
        "Risk Level",
        "Risk Flags",
        "Recommendation",
        "Verification Status"
    ]
    writer.writerow(headers)

    # Candidate Rows
    for cand in data.get("candidates", []):
        row = [
            cand.get("candidate_id", ""),
            cand.get("candidate_name", ""),
            cand.get("job", ""),
            f"{cand.get('match_score', 0)}%",
            f"{cand.get('evidence_score', 0)}%",
            f"{cand.get('hiring_confidence', 0)}%",
            f"{cand.get('current_fit', 0)}%",
            f"{cand.get('potential_fit', 0)}%",
            f"{cand.get('experience', 0)} yrs",
            "; ".join(cand.get("matched_skills", [])),
            "; ".join(cand.get("missing_skills", [])),
            "; ".join(cand.get("transferable_skills", [])),
            cand.get("risk_level", "NO_RISK"),
            "; ".join(cand.get("risk_flags_details", [])),
            cand.get("recommendation", "CONSIDER"),
            cand.get("verification_status", "VERIFIED")
        ]
        writer.writerow(row)

    return output.getvalue()
