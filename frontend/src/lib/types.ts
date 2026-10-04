export interface ScoringWeights {
  required_skills: number;
  relevant_experience: number;
  project_evidence: number;
  education_cert: number;
  preferred_skills: number;
  domain_relevance: number;
  evidence_confidence: number;
}

export interface JobRequirement {
  id: number;
  job_id: number;
  name: string;
  category: string;
  tier: "MUST_HAVE" | "SHOULD_HAVE" | "NICE_TO_HAVE";
  description?: string;
  expected_years: number;
  weight: number;
}

export interface Job {
  id: number;
  title: string;
  raw_description: string;
  seniority: string;
  min_years_experience: number;
  education_required: string;
  location: string;
  work_mode: string;
  responsibilities: string[];
  tools_and_tech: string[];
  domain_knowledge: string[];
  soft_skills: string[];
  status: string;
  weights?: Record<string, number>;
  created_at: string;
  requirements: JobRequirement[];
  candidates_count?: number;
  shortlisted_count?: number;
  average_match_score?: number;
}

export interface CandidateTableRow {
  rank: number;
  candidate_id: number;
  name: string;
  email?: string;
  match_score: number;
  evidence_score: number;
  hiring_confidence: number;
  potential_score: number;
  required_skills_coverage: string;
  experience_years: number;
  risk_flags_count: number;
  recommendation: "STRONGLY_RECOMMEND" | "RECOMMEND" | "CONSIDER" | "VERIFY" | "NOT_CURRENT_FIT";
  top_transferable_skill?: string;
}

export interface EvidenceItem {
  id: number;
  requirement_name: string;
  claim_snippet?: string;
  evidence_snippet: string;
  source_section: string;
  strength: "HIGH" | "PARTIAL" | "WEAK_MISSING" | "CONTRADICTORY";
  evidence_score: number;
  is_transferable: boolean;
  transferable_explanation?: string;
  justification?: string;
}

export interface RiskFlag {
  id: number;
  flag_type: string;
  severity: "HIGH" | "MEDIUM" | "LOW";
  headline: string;
  details: string;
  neutral_recommendation: string;
}

export interface InterviewQuestion {
  id: number;
  category: "TECHNICAL" | "EXPERIENCE" | "PROJECT" | "BEHAVIORAL" | "VERIFICATION";
  target_requirement?: string;
  question: string;
  suggested_focus?: string;
  context_trigger?: string;
}

export interface SkillGap {
  skill_name: string;
  status: "AVAILABLE" | "PARTIAL" | "MISSING" | "TRANSFERABLE";
  learning_priority: "HIGH" | "MEDIUM" | "LOW";
  alternative_available?: string;
  gap_notes?: string;
}

export interface MatchResult {
  id: number;
  job_id: number;
  candidate_id: number;
  overall_match_score: number;
  hiring_confidence_score: number;
  evidence_confidence_score: number;
  evidence_coverage_percentage: number;
  potential_match_score: number;
  score_breakdown: Record<string, number>;
  supported_requirements_count: number;
  total_requirements_count: number;
  missing_requirements_count: number;
  contradiction_count: number;
  recommendation: "STRONGLY_RECOMMEND" | "RECOMMEND" | "CONSIDER" | "VERIFY" | "NOT_CURRENT_FIT";
  recommendation_summary?: string;
  potential_reason?: string;
  why_not_reasons: string[];
  outranking_tradeoffs?: string;
  skill_gaps: SkillGap[];
}

export interface CandidateDetail {
  id: number;
  name: string;
  email?: string;
  phone?: string;
  location?: string;
  linkedin?: string;
  github?: string;
  portfolio?: string;
  summary?: string;
  total_experience_years: number;
  experiences: {
    company: string;
    role: string;
    start_date?: string;
    end_date?: string;
    duration_years: number;
    responsibilities: string[];
    achievements: string[];
    technologies: string[];
  }[];
  educations: {
    degree: string;
    institution: string;
    graduation_year?: string;
    field?: string;
    gpa?: string;
  }[];
  skills: {
    name: string;
    category: string;
    years_of_experience: number;
    proficiency_claimed: string;
  }[];
  projects: {
    title: string;
    description?: string;
    technologies: string[];
    contribution?: string;
    results_metrics?: string;
  }[];
  certifications: {
    name: string;
    issuer?: string;
    issue_date?: string;
  }[];
  claims: {
    id: number;
    claim_text: string;
    claimed_skill?: string;
    claimed_duration_years?: number;
    verification_status: string;
    confidence_score: number;
    verification_notes?: string;
  }[];
  evidence_items: EvidenceItem[];
  risk_flags: RiskFlag[];
  interview_questions: InterviewQuestion[];
  match_result?: MatchResult;
}

export interface ComparisonResult {
  job_title: string;
  candidates: {
    id: number;
    name: string;
    match_score: number;
    evidence_score: number;
    hiring_confidence: number;
    potential_score: number;
    experience_years: number;
    risk_flags_count: number;
    recommendation: string;
  }[];
  matrix: Record<string, Record<string, {
    status: string;
    strength: string;
    score: number;
    snippet: string;
  }>>;
  recommended_candidate_name: string;
  recommended_candidate_id: number;
  tradeoff_analysis: string;
  why_summary: string;
}

export interface CopilotResponse {
  answer: string;
  suggested_actions: string[];
  candidate_highlight_ids: number[];
}
