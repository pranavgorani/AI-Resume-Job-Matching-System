from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

# --- Weights ---
class ScoringWeights(BaseModel):
    required_skills: float = 0.35
    relevant_experience: float = 0.20
    project_evidence: float = 0.15
    education_cert: float = 0.10
    preferred_skills: float = 0.10
    domain_relevance: float = 0.05
    evidence_confidence: float = 0.05

# --- Job Requirements ---
class RequirementCreate(BaseModel):
    name: str
    category: str = "skill"
    tier: str = "MUST_HAVE" # MUST_HAVE, SHOULD_HAVE, NICE_TO_HAVE
    description: Optional[str] = None
    expected_years: float = 0.0
    weight: float = 1.0

class RequirementOut(RequirementCreate):
    id: int
    job_id: int

    class Config:
        from_attributes = True

# --- Jobs ---
class JobCreate(BaseModel):
    title: str
    raw_description: str
    seniority: Optional[str] = "Mid-Senior"
    min_years_experience: Optional[float] = 3.0
    education_required: Optional[str] = "Bachelor's degree or equivalent"
    location: Optional[str] = "Remote"
    work_mode: Optional[str] = "Remote / Hybrid"
    weights: Optional[ScoringWeights] = None

class JobAnalysisResponse(BaseModel):
    job_title: str
    seniority: str
    min_years_experience: float
    education_required: str
    location: str
    work_mode: str
    critical_requirements: List[str]
    optional_requirements: List[str]
    must_have_skills: List[str]
    should_have_skills: List[str]
    nice_to_have_skills: List[str]
    responsibilities: List[str]
    tools_and_tech: List[str]
    domain_knowledge: List[str]
    soft_skills: List[str]
    classified_requirements: List[RequirementCreate]

class JobOut(BaseModel):
    id: int
    title: str
    raw_description: str
    seniority: str
    min_years_experience: float
    education_required: str
    location: str
    work_mode: str
    responsibilities: List[str] = []
    tools_and_tech: List[str] = []
    domain_knowledge: List[str] = []
    soft_skills: List[str] = []
    status: str
    weights: Optional[Dict[str, float]] = None
    created_at: datetime
    requirements: List[RequirementOut] = []
    candidates_count: Optional[int] = 0
    shortlisted_count: Optional[int] = 0
    average_match_score: Optional[float] = 0.0

    class Config:
        from_attributes = True

# --- Candidate details ---
class ExperienceItem(BaseModel):
    company: str
    role: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration_years: float = 0.0
    responsibilities: List[str] = []
    achievements: List[str] = []
    technologies: List[str] = []

class EducationItem(BaseModel):
    degree: str
    institution: str
    graduation_year: Optional[str] = None
    field: Optional[str] = None
    gpa: Optional[str] = None

class SkillItem(BaseModel):
    name: str
    category: str = "technical"
    years_of_experience: float = 0.0
    proficiency_claimed: str = "proficient"

class ProjectItem(BaseModel):
    title: str
    description: Optional[str] = None
    technologies: List[str] = []
    contribution: Optional[str] = None
    results_metrics: Optional[str] = None

class CertificationItem(BaseModel):
    name: str
    issuer: Optional[str] = None
    issue_date: Optional[str] = None

class CandidateClaimOut(BaseModel):
    id: int
    claim_text: str
    claimed_skill: Optional[str]
    claimed_duration_years: Optional[float]
    verification_status: str
    confidence_score: float
    verification_notes: Optional[str]

    class Config:
        from_attributes = True

class EvidenceItemOut(BaseModel):
    id: int
    requirement_name: str
    claim_snippet: Optional[str]
    evidence_snippet: str
    source_section: str
    strength: str # HIGH (GREEN), PARTIAL (YELLOW), WEAK_MISSING (RED), CONTRADICTORY (PURPLE)
    evidence_score: float
    is_transferable: bool = False
    transferable_explanation: Optional[str] = None
    justification: Optional[str] = None

    class Config:
        from_attributes = True

class RiskFlagOut(BaseModel):
    id: int
    flag_type: str
    severity: str
    headline: str
    details: str
    neutral_recommendation: str

    class Config:
        from_attributes = True

class InterviewQuestionOut(BaseModel):
    id: int
    category: str
    target_requirement: Optional[str]
    question: str
    suggested_focus: Optional[str]
    context_trigger: Optional[str]

    class Config:
        from_attributes = True

class SkillGapOut(BaseModel):
    skill_name: str
    status: str # AVAILABLE, PARTIAL, MISSING, TRANSFERABLE
    learning_priority: str # HIGH, MEDIUM, LOW
    alternative_available: Optional[str] = None
    gap_notes: Optional[str] = None

class MatchResultOut(BaseModel):
    id: int
    job_id: int
    candidate_id: int
    overall_match_score: float
    hiring_confidence_score: float
    evidence_confidence_score: float
    evidence_coverage_percentage: float
    potential_match_score: float
    score_breakdown: Dict[str, float]
    supported_requirements_count: int
    total_requirements_count: int
    missing_requirements_count: int
    contradiction_count: int
    recommendation: str
    recommendation_summary: Optional[str]
    potential_reason: Optional[str]
    why_not_reasons: List[str] = []
    outranking_tradeoffs: Optional[str] = None
    skill_gaps: List[SkillGapOut] = []

    class Config:
        from_attributes = True

class CandidateDetailOut(BaseModel):
    id: int
    name: str
    email: Optional[str]
    phone: Optional[str]
    location: Optional[str]
    linkedin: Optional[str]
    github: Optional[str]
    portfolio: Optional[str]
    summary: Optional[str]
    total_experience_years: float
    experiences: List[ExperienceItem] = []
    educations: List[EducationItem] = []
    skills: List[SkillItem] = []
    projects: List[ProjectItem] = []
    certifications: List[CertificationItem] = []
    claims: List[CandidateClaimOut] = []
    evidence_items: List[EvidenceItemOut] = []
    risk_flags: List[RiskFlagOut] = []
    interview_questions: List[InterviewQuestionOut] = []
    match_result: Optional[MatchResultOut] = None
    processing_status: Optional[str] = "COMPLETED"
    processing_error: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CandidateTableRow(BaseModel):
    rank: int = 1
    candidate_id: int
    job_id: Optional[int] = None
    name: str = "Unnamed Candidate"
    email: Optional[str] = None
    match_score: float = 0.0
    evidence_score: float = 0.0
    hiring_confidence: float = 0.0
    potential_score: float = 0.0
    required_skills_coverage: str = "0/0"
    experience_years: float = 0.0
    risk_flags_count: int = 0
    recommendation: str = "REVIEW"
    top_transferable_skill: Optional[str] = None
    processing_status: str = "COMPLETED"
    processing_error: Optional[str] = None

# --- Processing & Jobs ---
class ProcessingJobOut(BaseModel):
    id: str
    job_id: int
    candidate_id: Optional[int] = None
    file_name: str
    status: str # QUEUED, UPLOADING, UPLOADED, PARSING, ANALYZING, COMPLETED, FAILED
    stage: str
    progress_percent: int = 0
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Benchmark ---
class BenchmarkCandidateItem(BaseModel):
    candidate_id: int
    name: str
    match_score: float
    evidence_score: float
    hiring_confidence: float
    risk_level: str
    recommendation: str
    expected_category: str
    actual_category: str
    status: str

class BenchmarkRunResponse(BaseModel):
    benchmark_run_id: str
    job_id: int
    seed: int
    total: int
    completed: int
    failed: int
    average_match: float
    average_evidence: float
    average_hiring_confidence: float
    high_risk_count: int
    strong_count: int
    moderate_count: int
    weak_count: int
    poor_count: int
    processing_time_seconds: float
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1: Optional[float] = None
    candidates: List[BenchmarkCandidateItem] = []

# --- Comparison ---
class CandidateComparisonRequest(BaseModel):
    job_id: int
    candidate_ids: List[int]

class CandidateComparisonResult(BaseModel):
    job_title: str
    candidates: List[Dict[str, Any]]
    matrix: Dict[str, Dict[str, Any]] # Requirement -> { CandidateName: Status }
    recommended_candidate_name: str
    recommended_candidate_id: int
    tradeoff_analysis: str
    why_summary: str

# --- Copilot ---
class CopilotQueryRequest(BaseModel):
    job_id: Optional[int] = None
    candidate_id: Optional[int] = None
    query: str

class CopilotQueryResponse(BaseModel):
    answer: str
    suggested_actions: List[str] = []
    applied_filters: Optional[Dict[str, Any]] = None
    candidate_highlight_ids: List[int] = []

# --- Natural Filter ---
class NaturalFilterRequest(BaseModel):
    job_id: int
    query: str

class NaturalFilterResponse(BaseModel):
    parsed_filters: Dict[str, Any]
    matched_candidate_ids: List[int]
    explanation: str
