# AI-Resume-Job-Matching-System# TalentProof AI

> **"Don't just rank resumes. Prove the match."**
> 
> *Official Submission for ALGOTHON'26 — Problem Statement: ALG-AI-01 (AI Resume & Job Matching System)*

---

## 1. Executive Summary & Vision

Traditional Applicant Tracking Systems (ATS) rely on shallow keyword frequency matching. Candidates exploit this with buzzword stuffing, while high-potential candidates with transferable competencies are rejected, and recruiters are left with opaque black-box percentages.

**TalentProof AI** is an evidence-based candidate intelligence platform. It replaces black-box keyword matching with an internal **Evidence Graph**:

```
Job Description
      ↓
Requirement Intelligence (MUST / SHOULD / NICE TO HAVE)
      ↓
Candidate Resume Extraction (Personal, Education, Chronology, Skills, Projects, Claims)
      ↓
Evidence Mapping (Requirement → Claim → Resume Evidence → Evidence Strength)
      ↓
Claim Verification Engine (Supported, Partially Supported, Unsupported, Contradictory)
      ↓
Contradiction Detection (Timeline Overlap, Unbacked Buzzwords, Experience Gaps)
      ↓
Transferable Skill Detection (e.g., Azure → AWS, PyTorch → LLM APIs)
      ↓
Deterministic Explainable Scoring (7 Configurable Dimensions)
      ↓
Interview Verification Questions (Technical, Experience, Project, Behavioral, Verification)
```

---

## 2. Core Innovations & Key Differentiators

| Innovation | What Traditional ATS Does | What TalentProof AI Does |
|---|---|---|
| **Evidence Graph** | Matches occurrences of words (e.g. "Python"). | Maps `Job Requirement → Candidate Claim → Resume Artifact → Evidence Strength` with percentage confidence. |
| **Claim Verification Engine** | Believes candidate claims verbatim. | Audits claims against chronological employment records (e.g., claims 5 yrs Python vs. verified ~2.5 yrs). |
| **Contradiction Detection** | Blind to employment concurrency. | Detects timeline overlaps (e.g. Senior Tech Lead title during concurrent full-time Master's enrollment) and unbacked buzzwords. |
| **Transferable Skill Reasoning** | Counts non-identical technologies as 0% (e.g. Azure vs AWS). | Recognizes transferable architectures (Azure → AWS with 82% transferability factor) without falsely claiming equivalence. |
| **Talent Potential Mode** | Only measures static keyword count. | Distinguishes **Current Fit** (e.g. 72%) from **Potential Fit** (e.g. 91% with targeted upskilling). |
| **Hiring Confidence vs Match Score** | Gives one misleading score. | Decouples **Match Score** from **Hiring Confidence** (penalized if critical must-haves lack verifiable production proof). |
| **"Why Not This Candidate?"** | Shows generic score delta. | Explains the specific barriers preventing a candidate from securing #1, peer trade-offs, and exact evidence required to reverse the decision. |
| **Interview Intelligence** | Generic behavioral question templates. | Automatically generates category-specific questions (Technical, Experience, Project, Behavioral, Verification) grounded in resume evidence gaps. |
| **AI Recruiter Copilot** | Generic ChatGPT chatbot. | Recruiter assistant grounded directly in the candidate pool dataset for natural-language queries and conversational filtering. |
| **Fair Match™ Bias Protection** | Unchecked demographic proxy bias. | Completely removes demographic attributes (gender, religion, caste, race, photograph, age) from ranking formulas. |

---

## 3. The 8 Canonical Demo Archetypes

The platform includes a built-in **1-Click "Try Live Demo"** button that initializes the role **"Senior Full Stack AI Engineer"** and evaluates 8 distinct candidate archetypes:

1. **Rahul Sharma (#1 Ranked — 93.6% Match, 93.8% Evidence)**: Perfect candidate with verified production proof across Python, FastAPI, React, TypeScript, PostgreSQL, and AWS, with quantified scale metrics and 0 flags.
2. **Priya Nair (#2 Ranked — 87.6% Match, 88.5% Evidence)**: Transferable skills candidate possessing enterprise Azure and PyTorch background that translates directly to AWS and LLM APIs.
3. **Amit Patel (#3 Ranked — 84.5% Match, 83.0% Evidence)**: Strong candidate with solid full-stack experience and verified project deliverables.
4. **Vikram Singh (#4 Ranked — 75.8% Match, 72.3% Evidence)**: Backend-specialized candidate missing React and TypeScript must-haves.
5. **Rohan Mehta (#5 Ranked — 75.8% Match, 90.5% Potential)**: Accelerated high-potential junior candidate (1.8 years experience) with open-source repositories and hackathon wins.
6. **Ananya Sen (#6 Ranked — 68.0% Match, 35.2% Evidence, 2 Flags)**: Contradictory claim candidate (claimed 5 yrs Python vs. 2.5 yrs timeline; Senior Dev title during full-time Master's degree).
7. **Siddharth Verma (#7 Ranked — 61.4% Match, 47.1% Evidence)**: 7-year corporate consultant with vague responsibility bullets and no concrete project metrics.
8. **Neha Gupta (#8 Ranked — 57.2% Match, 20.0% Evidence, 8 Flags)**: Keyword-stuffed resume listing every tech buzzword in skills block without project evidence — **a traditional ATS would rank her in top tier, but TalentProof AI exposes the 20% evidence confidence!**

---

## 4. Architecture & Tech Stack

```
Frontend (Next.js 16 + TypeScript + Tailwind CSS)
      │
      ▼ REST APIs (JSON / Multipart)
FastAPI Backend (Python 3.14)
      ├── Document Parser (PDF via PyPDF, DOCX via python-docx, TXT)
      ├── JD Intelligence Engine (Must / Should / Nice to have classification)
      ├── Resume Intelligence Engine (Structured extraction)
      ├── Evidence Graph Builder (4-Tier: Green, Yellow, Red, Purple)
      ├── Claim Verification & Contradiction Detector (Chronology & Overlap)
      ├── Transferable Skill Matrix (Cross-framework mapping)
      ├── Deterministic Scoring Engine (7 Configurable Dimensions)
      ├── Interview Question Generator (5 Categories)
      ├── Why-Not Decision Intelligence Engine
      └── AI Recruiter Copilot (Natural query & filtering)
      │
      ▼ ORM Layer (SQLAlchemy 2.0)
SQLite (Zero-friction local demo) / PostgreSQL / Supabase
      │
      ▼ LLM Layer
Gemini 2.5 Flash / Graceful Fallback Heuristic Reasoner
```

---

## 5. Folder Structure

```
algohack/
├── backend/
│   ├── app/
│   │   ├── config.py                 # Pydantic Settings, DB URL, Gemini config
│   │   ├── database.py               # SQLAlchemy engine & session manager
│   │   ├── main.py                   # FastAPI app with CORS & lifespan
│   │   ├── seed_data.py              # 8 realistic candidate profiles + demo job
│   │   ├── models/
│   │   │   ├── orm.py                # 14 SQLAlchemy tables
│   │   │   └── schemas.py            # Pydantic request/response models
│   │   ├── routes/
│   │   │   ├── jobs.py               # Job CRUD & AI JD analysis
│   │   │   ├── resumes.py            # PDF/DOCX/TXT upload & parsing
│   │   │   ├── candidates.py         # Candidate dossiers & intelligence
│   │   │   ├── matching.py           # Evidence-First Matching Engine
│   │   │   ├── compare.py            # Side-by-side comparison & trade-offs
│   │   │   ├── copilot.py            # AI Recruiter Copilot & NL filter
│   │   │   ├── demo.py               # 1-Click demo seed endpoint
│   │   │   └── export.py             # Printable dossier export
│   │   ├── services/
│   │   │   ├── parser.py             # Multi-format document parser
│   │   │   ├── jd_intelligence.py    # Requirement classifier
│   │   │   ├── resume_intelligence.py# Resume entity extractor
│   │   │   ├── evidence_engine.py    # Evidence graph constructor
│   │   │   ├── contradiction_detector.py # Overlap & unbacked claim detector
│   │   │   ├── transferable_engine.py# Cross-technology transfer mapping
│   │   │   ├── scoring_engine.py     # Deterministic non-blackbox scoring
│   │   │   ├── interview_engine.py   # Question generator
│   │   │   ├── why_not_engine.py     # Decision intelligence engine
│   │   │   ├── copilot_engine.py     # Copilot reasoning engine
│   │   │   └── gemini_client.py      # Gemini API wrapper with fallback
│   │   └── tests/
│   │       ├── test_all.py           # Unit tests (extraction, scoring, flags)
│   │       └── test_api.py           # Integration tests (APIs, seed, matching)
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── app/
    │   │   ├── layout.tsx            # Global layout with Copilot drawer
    │   │   ├── page.tsx              # Landing page (Match, Evidence, Verify)
    │   │   ├── dashboard/page.tsx    # Recruiter analytics dashboard
    │   │   ├── jobs/page.tsx         # Jobs listing
    │   │   ├── jobs/new/page.tsx     # Job creator & AI requirement classifier
    │   │   ├── jobs/[id]/page.tsx    # Candidate ranking table & filters
    │   │   ├── candidates/page.tsx   # Candidate directory
    │   │   ├── candidates/[id]/page.tsx # 12-Section Candidate Dossier
    │   │   ├── compare/page.tsx      # Side-by-side comparison matrix
    │   │   ├── analytics/page.tsx    # Evidence confidence & gap analytics
    │   │   └── settings/page.tsx     # Weights calibration & Fair Match
    │   ├── components/
    │   │   ├── Navbar.tsx            # Navigation & 1-Click demo trigger
    │   │   ├── CopilotDrawer.tsx     # AI Recruiter Copilot drawer
    │   │   ├── EvidenceBadge.tsx     # Green/Yellow/Red/Purple badge system
    │   │   ├── TimelineVisualizer.tsx# Visual career & overlap timeline
    │   │   ├── ScoreBreakdown.tsx    # 7-factor explainable scoring meter
    │   │   └── WhyNotModal.tsx       # "Why Not #1?" decision modal
    │   └── lib/
    │       ├── api.ts                # Typed client connecting to backend
    │       └── types.ts              # TypeScript interfaces
    ├── package.json
    └── tailwind.config.ts
```

---

## 6. Deterministic Scoring Formulation

Scoring is **never an arbitrary LLM hallucination**. It is calculated mathematically using configurable recruiter weights:

$$\text{Overall Match Score} = \sum_{i=1}^{7} (W_i \times S_i)$$

1. **Required Skill Coverage ($W_1 = 35\%$)**: Supported Must-Have requirements backed by empirical evidence.
2. **Relevant Experience ($W_2 = 20\%$)**: Ratio of verified chronological tenure to role requirement.
3. **Project Deliverables ($W_3 = 15\%$)**: Quantified project deliverables with metrics and architectural scale.
4. **Education & Certifications ($W_4 = 10\%$)**: Degree relevance and industry certifications.
5. **Preferred Skills ($W_5 = 10\%$)**: Should-Have and Nice-to-Have coverage.
6. **Domain Relevance ($W_6 = 5\%$)**: Alignment with full-stack, distributed, and AI systems.
7. **Evidence Confidence ($W_7 = 5\%$)**: Aggregate evidence strength discounted by active risk flags.

---

## 7. How to Run Locally

### Prerequisites
- Node.js (v18+)
- Python (3.10+)

### Step 1: Start the Backend
```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Backend API will be live at `http://127.0.0.1:8000` (API Docs at `http://127.0.0.1:8000/docs`).

### Step 2: Start the Frontend
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` in your browser.

### Step 3: Run the Demo
Click the **"Try Live Demo"** button on the navbar or landing page. In 1 click, the system seeds the "Senior Full Stack AI Engineer" job, parses the 8 candidates, evaluates evidence, detects contradictions, and ranks them in real time!

---

## 8. Test Suite Verification

Run the comprehensive pytest suite:
```bash
$env:PYTHONPATH="backend"
python -m pytest backend/app/tests/ -v
```
**Results: 6 Passed, 0 Failed (100% Pass Rate)**
- `test_jd_intelligence_extraction`: PASSED
- `test_transferable_skills_detection`: PASSED
- `test_contradiction_detection`: PASSED
- `test_evidence_graph_and_scoring`: PASSED
- `test_health`: PASSED
- `test_demo_seed_and_matching`: PASSED
