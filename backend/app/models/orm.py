import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.database import Base

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    jobs = relationship("Job", back_populates="organization")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(50), default="recruiter")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    title = Column(String(255), nullable=False)
    raw_description = Column(Text, nullable=False)
    seniority = Column(String(100), default="Mid-Senior")
    min_years_experience = Column(Float, default=3.0)
    education_required = Column(String(255), default="Bachelor's in Computer Science or equivalent")
    location = Column(String(255), default="Remote")
    work_mode = Column(String(100), default="Remote / Hybrid")
    responsibilities = Column(JSON, default=list)
    tools_and_tech = Column(JSON, default=list)
    domain_knowledge = Column(JSON, default=list)
    soft_skills = Column(JSON, default=list)
    status = Column(String(50), default="active")
    weights = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    organization = relationship("Organization", back_populates="jobs")
    requirements = relationship("JobRequirement", back_populates="job", cascade="all, delete-orphan")
    match_results = relationship("MatchResult", back_populates="job", cascade="all, delete-orphan")
    candidates = relationship("Candidate", back_populates="job", cascade="all, delete-orphan")

class JobRequirement(Base):
    __tablename__ = "job_requirements"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(100), default="skill") # skill, experience, education, domain, certification
    tier = Column(String(50), default="MUST_HAVE") # MUST_HAVE, SHOULD_HAVE, NICE_TO_HAVE
    description = Column(Text, nullable=True)
    weight = Column(Float, default=1.0)
    expected_years = Column(Float, default=0.0)

    job = relationship("Job", back_populates="requirements")

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(100), nullable=True)
    location = Column(String(255), nullable=True)
    linkedin = Column(String(255), nullable=True)
    github = Column(String(255), nullable=True)
    portfolio = Column(String(255), nullable=True)
    summary = Column(Text, nullable=True)
    total_experience_years = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    job = relationship("Job", back_populates="candidates")
    resumes = relationship("Resume", back_populates="candidate", cascade="all, delete-orphan")
    experiences = relationship("CandidateExperience", back_populates="candidate", cascade="all, delete-orphan")
    educations = relationship("CandidateEducation", back_populates="candidate", cascade="all, delete-orphan")
    skills = relationship("CandidateSkill", back_populates="candidate", cascade="all, delete-orphan")
    projects = relationship("CandidateProject", back_populates="candidate", cascade="all, delete-orphan")
    certifications = relationship("CandidateCertification", back_populates="candidate", cascade="all, delete-orphan")
    claims = relationship("CandidateClaim", back_populates="candidate", cascade="all, delete-orphan")
    evidence_items = relationship("CandidateEvidence", back_populates="candidate", cascade="all, delete-orphan")
    match_results = relationship("MatchResult", back_populates="candidate", cascade="all, delete-orphan")
    risk_flags = relationship("RiskFlag", back_populates="candidate", cascade="all, delete-orphan")
    interview_questions = relationship("InterviewQuestion", back_populates="candidate", cascade="all, delete-orphan")

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=True)
    file_type = Column(String(50), default="pdf")
    raw_text = Column(Text, nullable=False)
    parsed_json = Column(JSON, default=dict)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)

    candidate = relationship("Candidate", back_populates="resumes")

class CandidateExperience(Base):
    __tablename__ = "candidate_experience"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    company = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False)
    start_date = Column(String(100), nullable=True)
    end_date = Column(String(100), nullable=True) # or "Present"
    duration_years = Column(Float, default=0.0)
    responsibilities = Column(JSON, default=list)
    achievements = Column(JSON, default=list)
    technologies = Column(JSON, default=list)

    candidate = relationship("Candidate", back_populates="experiences")

class CandidateEducation(Base):
    __tablename__ = "candidate_education"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    degree = Column(String(255), nullable=False)
    institution = Column(String(255), nullable=False)
    graduation_year = Column(String(50), nullable=True)
    field = Column(String(255), nullable=True)
    gpa = Column(String(50), nullable=True)

    candidate = relationship("Candidate", back_populates="educations")

class CandidateSkill(Base):
    __tablename__ = "candidate_skills"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(100), default="technical") # technical, framework, cloud, database, soft_skill
    years_of_experience = Column(Float, default=0.0)
    proficiency_claimed = Column(String(100), default="proficient")

    candidate = relationship("Candidate", back_populates="skills")

class CandidateProject(Base):
    __tablename__ = "candidate_projects"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    technologies = Column(JSON, default=list)
    contribution = Column(Text, nullable=True)
    results_metrics = Column(Text, nullable=True)

    candidate = relationship("Candidate", back_populates="projects")

class CandidateCertification(Base):
    __tablename__ = "candidate_certifications"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    name = Column(String(255), nullable=False)
    issuer = Column(String(255), nullable=True)
    issue_date = Column(String(100), nullable=True)

    candidate = relationship("Candidate", back_populates="certifications")

class CandidateClaim(Base):
    __tablename__ = "candidate_claims"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    claim_text = Column(Text, nullable=False)
    claimed_skill = Column(String(255), nullable=True)
    claimed_duration_years = Column(Float, nullable=True)
    claimed_seniority = Column(String(100), nullable=True)
    verification_status = Column(String(50), default="SUPPORTED") # SUPPORTED, PARTIALLY_SUPPORTED, UNSUPPORTED, CONTRADICTORY, INSUFFICIENT_INFO
    confidence_score = Column(Float, default=0.8)
    verification_notes = Column(Text, nullable=True)

    candidate = relationship("Candidate", back_populates="claims")

class CandidateEvidence(Base):
    __tablename__ = "candidate_evidence"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    job_requirement_id = Column(Integer, ForeignKey("job_requirements.id"), nullable=True)
    requirement_name = Column(String(255), nullable=False)
    claim_snippet = Column(Text, nullable=True)
    evidence_snippet = Column(Text, nullable=False)
    source_section = Column(String(100), default="experience") # experience, projects, education, certification
    strength = Column(String(50), default="HIGH") # HIGH (Green), PARTIAL (Yellow), WEAK_MISSING (Red), CONTRADICTORY (Purple)
    evidence_score = Column(Float, default=80.0) # 0 to 100
    is_transferable = Column(Boolean, default=False)
    transferable_explanation = Column(Text, nullable=True)
    justification = Column(Text, nullable=True)

    candidate = relationship("Candidate", back_populates="evidence_items")

class MatchResult(Base):
    __tablename__ = "match_results"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    
    # Core Scores
    overall_match_score = Column(Float, nullable=False) # 0 to 100
    hiring_confidence_score = Column(Float, nullable=False) # 0 to 100
    evidence_confidence_score = Column(Float, nullable=False) # 0 to 100
    evidence_coverage_percentage = Column(Float, nullable=False) # % of requirements backed by evidence
    potential_match_score = Column(Float, nullable=False) # Current vs Potential Fit
    
    # Score Breakdown
    score_breakdown = Column(JSON, default=dict) # required_skills, experience, project_evidence, etc.
    
    # Requirement Coverage Counts
    supported_requirements_count = Column(Integer, default=0)
    total_requirements_count = Column(Integer, default=0)
    missing_requirements_count = Column(Integer, default=0)
    contradiction_count = Column(Integer, default=0)
    
    # Recommendation
    recommendation = Column(String(100), default="CONSIDER") # STRONGLY_RECOMMEND, RECOMMEND, CONSIDER, VERIFY, NOT_CURRENT_FIT
    recommendation_summary = Column(Text, nullable=True)
    potential_reason = Column(Text, nullable=True)
    
    # "Why Not" analysis
    why_not_reasons = Column(JSON, default=list)
    outranking_tradeoffs = Column(Text, nullable=True)
    
    calculated_at = Column(DateTime, default=datetime.datetime.utcnow)

    job = relationship("Job", back_populates="match_results")
    candidate = relationship("Candidate", back_populates="match_results")
    skill_gaps = relationship("SkillGap", back_populates="match_result", cascade="all, delete-orphan")

class SkillGap(Base):
    __tablename__ = "skill_gaps"

    id = Column(Integer, primary_key=True, index=True)
    match_result_id = Column(Integer, ForeignKey("match_results.id"), nullable=False)
    skill_name = Column(String(255), nullable=False)
    status = Column(String(50), default="MISSING") # AVAILABLE, PARTIAL, MISSING, TRANSFERABLE
    learning_priority = Column(String(50), default="MEDIUM") # HIGH, MEDIUM, LOW
    alternative_available = Column(String(255), nullable=True)
    gap_notes = Column(Text, nullable=True)

    match_result = relationship("MatchResult", back_populates="skill_gaps")

class RiskFlag(Base):
    __tablename__ = "risk_flags"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    flag_type = Column(String(100), nullable=False) # TIMELINE_OVERLAP, EXPERIENCE_GAP, UNBACKED_EXPERTISE, DURATION_MISMATCH
    severity = Column(String(50), default="MEDIUM") # HIGH, MEDIUM, LOW
    headline = Column(String(255), nullable=False)
    details = Column(Text, nullable=False)
    neutral_recommendation = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    candidate = relationship("Candidate", back_populates="risk_flags")

class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    category = Column(String(100), nullable=False) # TECHNICAL, EXPERIENCE, PROJECT, BEHAVIORAL, VERIFICATION
    target_requirement = Column(String(255), nullable=True)
    question = Column(Text, nullable=False)
    suggested_focus = Column(Text, nullable=True)
    context_trigger = Column(Text, nullable=True)

    candidate = relationship("Candidate", back_populates="interview_questions")

class Comparison(Base):
    __tablename__ = "comparisons"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    candidate_ids = Column(JSON, nullable=False) # list of candidate IDs
    comparison_matrix = Column(JSON, nullable=False)
    recommended_candidate_id = Column(Integer, nullable=True)
    tradeoff_analysis = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(255), nullable=False)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(Integer, nullable=True)
    details = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
