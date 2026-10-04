-- ==============================================================================
-- TalentProof AI - Supabase PostgreSQL & pgvector Schema
-- "Don't just rank resumes. Prove the match."
-- ==============================================================================

-- 1. Enable pgvector Extension for Semantic Vector Search
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Storage Bucket Creation for Resumes
INSERT INTO storage.buckets (id, name, public)
VALUES ('resumes', 'resumes', true)
ON CONFLICT (id) DO NOTHING;

-- Storage RLS: Allow authenticated and anon reads, controlled uploads
CREATE POLICY "Public Resume Access" ON storage.objects
FOR SELECT USING (bucket_id = 'resumes');

CREATE POLICY "Allow Resume Uploads" ON storage.objects
FOR INSERT WITH CHECK (bucket_id = 'resumes');

-- ==============================================================================
-- Core Tables
-- ==============================================================================

-- 1. Jobs Table
CREATE TABLE IF NOT EXISTS public.jobs (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    company TEXT,
    seniority TEXT DEFAULT 'Mid-Level',
    domain TEXT DEFAULT 'Technology',
    location TEXT DEFAULT 'Remote',
    work_mode TEXT DEFAULT 'Remote',
    minimum_experience NUMERIC(4, 1) DEFAULT 0.0,
    education TEXT,
    raw_description TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. Requirements Table (Tiered MUST / SHOULD / NICE TO HAVE)
CREATE TABLE IF NOT EXISTS public.requirements (
    id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL REFERENCES public.jobs(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    category TEXT DEFAULT 'technical',
    priority_tier TEXT DEFAULT 'MUST_HAVE', -- MUST_HAVE, SHOULD_HAVE, NICE_TO_HAVE
    weight NUMERIC(4, 2) DEFAULT 1.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 3. Candidates Table
CREATE TABLE IF NOT EXISTS public.candidates (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    location TEXT,
    summary TEXT,
    years_of_experience NUMERIC(4, 1) DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 4. Resumes Table (PDF Metadata & Storage Path)
CREATE TABLE IF NOT EXISTS public.resumes (
    id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL REFERENCES public.candidates(id) ON DELETE CASCADE,
    storage_path TEXT NOT NULL,
    file_url TEXT,
    file_name TEXT NOT NULL,
    file_size_bytes INTEGER,
    raw_text TEXT,
    content_hash TEXT,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 5. Experiences Table
CREATE TABLE IF NOT EXISTS public.experiences (
    id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL REFERENCES public.candidates(id) ON DELETE CASCADE,
    company TEXT NOT NULL,
    job_title TEXT NOT NULL,
    start_date TEXT,
    end_date TEXT,
    is_current BOOLEAN DEFAULT false,
    duration_months INTEGER DEFAULT 0,
    description TEXT,
    technologies JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 6. Skills Table
CREATE TABLE IF NOT EXISTS public.skills (
    id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL REFERENCES public.candidates(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    category TEXT DEFAULT 'technical',
    proficiency TEXT DEFAULT 'intermediate',
    years_used NUMERIC(4, 1),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 7. Projects Table
CREATE TABLE IF NOT EXISTS public.projects (
    id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL REFERENCES public.candidates(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    technologies JSONB DEFAULT '[]'::jsonb,
    metrics TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 8. Candidate Claims Table
CREATE TABLE IF NOT EXISTS public.candidate_claims (
    id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL REFERENCES public.candidates(id) ON DELETE CASCADE,
    claim_text TEXT NOT NULL,
    category TEXT,
    source_section TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 9. Evidence Table (Evidence-First Verification)
CREATE TABLE IF NOT EXISTS public.evidence (
    id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL REFERENCES public.candidates(id) ON DELETE CASCADE,
    job_id TEXT NOT NULL REFERENCES public.jobs(id) ON DELETE CASCADE,
    requirement TEXT NOT NULL,
    candidate_claim TEXT,
    resume_evidence TEXT,
    evidence_strength TEXT DEFAULT 'INFERRED', -- DIRECT, INFERRED, WEAK, NONE
    status TEXT NOT NULL, -- SUPPORTED, PARTIALLY_SUPPORTED, MISSING, CONTRADICTORY, NOT_ENOUGH_INFORMATION, TRANSFERABLE
    confidence NUMERIC(4, 2) DEFAULT 0.85,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 10. Contradictions Table (Integrity & Discrepancy Auditing)
CREATE TABLE IF NOT EXISTS public.contradictions (
    id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL REFERENCES public.candidates(id) ON DELETE CASCADE,
    type TEXT NOT NULL, -- TIMELINE_OVERLAP, SKILL_WITHOUT_EVIDENCE, INCONSISTENT_EXPERIENCE, etc.
    severity TEXT DEFAULT 'LOW', -- LOW, MEDIUM, HIGH
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    recommendation TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 11. Skill Gaps Table
CREATE TABLE IF NOT EXISTS public.skill_gaps (
    id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL REFERENCES public.candidates(id) ON DELETE CASCADE,
    job_id TEXT NOT NULL REFERENCES public.jobs(id) ON DELETE CASCADE,
    skill_name TEXT NOT NULL,
    criticality TEXT DEFAULT 'REQUIRED', -- REQUIRED, PREFERRED
    is_transferable BOOLEAN DEFAULT false,
    transferable_alternative TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 12. Embeddings Table (Supabase pgvector)
CREATE TABLE IF NOT EXISTS public.embeddings (
    id BIGSERIAL PRIMARY KEY,
    entity_type TEXT NOT NULL, -- 'job_requirement', 'candidate_skill', 'project', 'resume_section'
    entity_id TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding vector(768),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE INDEX IF NOT EXISTS embeddings_vector_idx ON public.embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- 13. Match Results Table (Deterministic 7-Factor Engine)
CREATE TABLE IF NOT EXISTS public.match_results (
    id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL REFERENCES public.jobs(id) ON DELETE CASCADE,
    candidate_id TEXT NOT NULL REFERENCES public.candidates(id) ON DELETE CASCADE,
    overall_match_score NUMERIC(5, 2) NOT NULL,
    current_fit_score NUMERIC(5, 2) NOT NULL,
    potential_fit_score NUMERIC(5, 2) NOT NULL,
    evidence_score NUMERIC(5, 2) NOT NULL,
    hiring_confidence NUMERIC(5, 2) NOT NULL,
    coverage NUMERIC(5, 2) NOT NULL,
    recommendation TEXT NOT NULL,
    score_breakdown JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 14. Interview Questions Table (Interview Intelligence)
CREATE TABLE IF NOT EXISTS public.interview_questions (
    id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL REFERENCES public.candidates(id) ON DELETE CASCADE,
    job_id TEXT NOT NULL REFERENCES public.jobs(id) ON DELETE CASCADE,
    category TEXT NOT NULL, -- technical, experience, project, behavioral, verification
    question TEXT NOT NULL,
    target TEXT,
    rationale TEXT,
    evaluation_criteria TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- ==============================================================================
-- Row Level Security (RLS) Configuration
-- ==============================================================================
ALTER TABLE public.jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.requirements ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.candidates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.resumes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.experiences ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.candidate_claims ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.contradictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.skill_gaps ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.match_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.interview_questions ENABLE ROW LEVEL SECURITY;

-- Anonymous and Authenticated read policies for application
DO $$
DECLARE
    t text;
BEGIN
    FOR t IN
        SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'
    LOOP
        EXECUTE format('CREATE POLICY "Allow public read on %I" ON public.%I FOR SELECT USING (true);', t, t);
        EXECUTE format('CREATE POLICY "Allow public write on %I" ON public.%I FOR ALL USING (true) WITH CHECK (true);', t, t);
    END LOOP;
END;
$$;

-- ==============================================================================
-- Vector Search RPC Function
-- ==============================================================================
CREATE OR REPLACE FUNCTION match_embeddings (
  query_embedding vector(768),
  match_threshold float,
  match_count int
)
RETURNS TABLE (
  id bigint,
  entity_type text,
  entity_id text,
  content text,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    embeddings.id,
    embeddings.entity_type,
    embeddings.entity_id,
    embeddings.content,
    1 - (embeddings.embedding <=> query_embedding) AS similarity
  FROM embeddings
  WHERE 1 - (embeddings.embedding <=> query_embedding) > match_threshold
  ORDER BY similarity DESC
  LIMIT match_count;
END;
$$;
