from typing import List, Dict, Any

def generate_interview_questions(
    evidence_items: List[Dict[str, Any]],
    risk_flags: List[Dict[str, Any]],
    candidate_data: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Generates targeted, high-impact interview questions categorized into:
    TECHNICAL, EXPERIENCE, PROJECT, BEHAVIORAL, VERIFICATION.
    """
    questions = []
    
    # 1. VERIFICATION questions for Risk Flags and Contradictions
    for flag in risk_flags:
        ftype = flag.get("flag_type")
        if ftype == "DURATION_MISMATCH":
            questions.append({
                "category": "VERIFICATION",
                "target_requirement": "Experience Duration",
                "question": "Can you walk us through your employment timeline and clarify the duration of your hands-on experience, specifically regarding full-time vs internship or freelance contributions?",
                "suggested_focus": "Clarify discrepancy between claimed tenure and verifiable chronology.",
                "context_trigger": flag.get("headline")
            })
        elif ftype == "TIMELINE_OVERLAP":
            questions.append({
                "category": "VERIFICATION",
                "target_requirement": "Academic & Employment Concurrency",
                "question": "Your resume indicates concurrent full-time graduate degree enrollment while holding a Senior Engineer title. Could you elaborate on your working arrangement and time allocation during this phase?",
                "suggested_focus": "Understand depth of senior responsibility during full-time academic studies.",
                "context_trigger": flag.get("headline")
            })
        elif ftype == "UNBACKED_EXPERTISE":
            questions.append({
                "category": "VERIFICATION",
                "target_requirement": flag.get("headline"),
                "question": "You highlighted expertise in this technology in your skills profile, but there are limited project deliverables detailed. Could you walk us through an end-to-end production feature you built with it?",
                "suggested_focus": "Differentiate between theoretical awareness and battle-tested production capability.",
                "context_trigger": flag.get("headline")
            })

    # 2. TECHNICAL questions for Transferable & Weak Requirements
    for ev in evidence_items:
        req_name = ev.get("requirement_name")
        if ev.get("is_transferable"):
            questions.append({
                "category": "TECHNICAL",
                "target_requirement": req_name,
                "question": f"While you have substantial depth in {ev.get('claim_snippet', 'an alternative framework')}, our stack heavily leverages {req_name}. How would you translate your architectural patterns into {req_name}, and what nuances would you watch out for?",
                "suggested_focus": f"Assess mental model adaptability from alternative technology to {req_name}.",
                "context_trigger": f"Transferable skill detected: {ev.get('transferable_explanation')}"
            })
        elif ev.get("strength") == "WEAK_MISSING":
            questions.append({
                "category": "TECHNICAL",
                "target_requirement": req_name,
                "question": f"This position requires working with {req_name}. What is your familiarity with this technology, and how have you approached rapidly ramping up on unfamiliar tools in past roles?",
                "suggested_focus": "Determine self-learning velocity and conceptual grasp.",
                "context_trigger": f"Missing critical requirement: {req_name}"
            })

    # 3. PROJECT questions for key highlighted deliverables
    projects = candidate_data.get("projects", [])
    if projects:
        top_proj = projects[0]
        questions.append({
            "category": "PROJECT",
            "target_requirement": top_proj.get("title", "Flagship Project"),
            "question": f"In your project '{top_proj.get('title')}', what was the single biggest architectural bottleneck you encountered, what alternatives did you evaluate, and how did you measure success after release?",
            "suggested_focus": "Evaluate critical decision-making, performance profiling, and ownership depth.",
            "context_trigger": f"Key project: {top_proj.get('title')}"
        })

    # 4. EXPERIENCE & SYSTEM DESIGN questions
    questions.append({
        "category": "EXPERIENCE",
        "target_requirement": "Distributed Architecture & Scalability",
        "question": "Describe a distributed system or API workflow you personally designed from scratch. How did you handle network partition, database connection pooling, and eventual consistency under peak traffic?",
        "suggested_focus": "Evaluate senior-level distributed systems maturity and failure mode anticipation.",
        "context_trigger": "Evaluation for Senior Full Stack AI Engineer requirements"
    })

    # 5. BEHAVIORAL question
    questions.append({
        "category": "BEHAVIORAL",
        "target_requirement": "Technical Disagreement & Cross-Functional Alignment",
        "question": "Tell us about a time you strongly disagreed with a product manager or tech lead on a technical trade-off (e.g., speed vs. code hygiene). How did you present your evidence and what was the resolution?",
        "suggested_focus": "Assess professional maturity, diplomatic communication, and pragmatic balance.",
        "context_trigger": "Collaboration and engineering leadership standard"
    })

    return questions
