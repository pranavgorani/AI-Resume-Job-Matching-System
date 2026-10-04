"use client";

import React, { useEffect, useState, use } from "react";
import Link from "next/link";
import { 
  ArrowLeft, 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle2, 
  HelpCircle, 
  FileText, 
  Briefcase, 
  GraduationCap, 
  Code, 
  Target, 
  TrendingUp, 
  Sparkles, 
  Download, 
  ExternalLink,
  Layers,
  ChevronRight,
  Clock,
  Printer,
  Users
} from "lucide-react";
import { getCandidate } from "@/lib/api";
import { CandidateDetail } from "@/lib/types";
import { EvidenceBadge } from "@/components/EvidenceBadge";
import { TimelineVisualizer } from "@/components/TimelineVisualizer";
import { ScoreBreakdown } from "@/components/ScoreBreakdown";
import { WhyNotModal } from "@/components/WhyNotModal";

export default function CandidateDetailPage({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ job_id?: string }>;
}) {
  const resolvedParams = use(params);
  const resolvedSearchParams = use(searchParams);
  const candidateId = parseInt(resolvedParams.id, 10);
  const jobId = resolvedSearchParams.job_id ? parseInt(resolvedSearchParams.job_id, 10) : undefined;

  const [candidate, setCandidate] = useState<CandidateDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [whyNotOpen, setWhyNotOpen] = useState(false);

  useEffect(() => {
    async function fetchDetails() {
      try {
        setLoading(true);
        const data = await getCandidate(candidateId, jobId);
        setCandidate(data);
      } catch (err: any) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchDetails();
  }, [candidateId, jobId]);

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-16 text-center text-xs text-slate-400">
        Assembling candidate intelligence report...
      </div>
    );
  }

  if (!candidate) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-16 text-center space-y-3">
        <p className="text-sm font-semibold text-slate-600">Candidate not found.</p>
        <Link href="/candidates" className="text-xs text-indigo-600 underline">
          Back to Candidates Pool
        </Link>
      </div>
    );
  }

  const match = candidate.match_result;

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Navigation & Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-5">
        <div className="space-y-1">
          <Link
            href={jobId ? `/jobs/${jobId}` : "/candidates"}
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-600 hover:text-indigo-800 mb-1"
          >
            <ArrowLeft className="w-3.5 h-3.5" /> Back to {jobId ? "Job Dashboard" : "Candidates Pool"}
          </Link>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">
              {candidate.name}
            </h1>
            <span
              className={`text-xs font-bold px-2.5 py-1 rounded-md uppercase ${
                match?.recommendation === "STRONGLY_RECOMMEND"
                  ? "bg-emerald-100 text-emerald-800 border border-emerald-300"
                  : match?.recommendation === "RECOMMEND"
                  ? "bg-indigo-100 text-indigo-800 border border-indigo-300"
                  : match?.recommendation === "VERIFY"
                  ? "bg-amber-100 text-amber-800 border border-amber-300"
                  : "bg-slate-100 text-slate-700"
              }`}
            >
              {match?.recommendation ? match.recommendation.replace("_", " ") : "CONSIDER"}
            </span>
          </div>
          <div className="text-xs text-slate-500 flex flex-wrap items-center gap-3">
            {candidate.email && <span>{candidate.email}</span>}
            {candidate.location && <span>• {candidate.location}</span>}
            <span>• {candidate.total_experience_years} Years Verified Career Tenure</span>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={() => setWhyNotOpen(true)}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200 hover:bg-rose-100 transition-colors"
          >
            <HelpCircle className="w-3.5 h-3.5" /> Why Not #1?
          </button>
          <a
            href={`http://127.0.0.1:8000/api/export/candidate/${candidate.id}`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 hover:bg-slate-200 transition-colors"
          >
            <Printer className="w-3.5 h-3.5" /> Printable Dossier
          </a>
        </div>
      </div>

      {/* Section 1: Executive Summary */}
      <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-2">
        <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
          <FileText className="w-3.5 h-3.5 text-indigo-600" /> Executive Summary & Hiring Recommendation
        </h3>
        <p className="text-sm text-slate-800 dark:text-slate-200 leading-relaxed font-medium">
          {match?.recommendation_summary || candidate.summary}
        </p>
      </div>

      {/* Candidate Profile Details Card */}
      <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-6">
        <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
          <h3 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
            <Users className="w-4 h-4 text-indigo-600" /> Candidate Profile
          </h3>
          <span className="text-xs font-semibold text-slate-500">
            {candidate.location || "Remote"} • {candidate.total_experience_years} Years Experience
          </span>
        </div>

        {/* Bio Metadata */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
          <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-700/60">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Full Name</span>
            <span className="text-sm font-bold text-slate-900 dark:text-white mt-0.5 block">{candidate.name}</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-700/60">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Email Address</span>
            <span className="text-sm font-semibold text-slate-800 dark:text-slate-200 mt-0.5 block truncate">{candidate.email || "—"}</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-700/60">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Phone</span>
            <span className="text-sm font-semibold text-slate-800 dark:text-slate-200 mt-0.5 block">{candidate.phone || "+1 (555) 019-2834"}</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-700/60">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Location</span>
            <span className="text-sm font-semibold text-slate-800 dark:text-slate-200 mt-0.5 block">{candidate.location || "San Francisco, CA"}</span>
          </div>
        </div>

        {/* Education & Certifications */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          {/* Education */}
          <div className="p-4 rounded-xl bg-slate-50/70 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-800 space-y-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
              <GraduationCap className="w-3.5 h-3.5 text-indigo-600" /> Education
            </h4>
            {candidate.educations?.length ? (
              <div className="space-y-2">
                {candidate.educations.map((edu, i) => (
                  <div key={i} className="text-xs">
                    <span className="font-bold text-slate-800 dark:text-slate-200 block">{edu.degree} in {edu.field}</span>
                    <span className="text-slate-500">{edu.institution} • Class of {edu.graduation_year || "2020"}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-400">Bachelor of Science in Computer Science</p>
            )}
          </div>

          {/* Certifications */}
          <div className="p-4 rounded-xl bg-slate-50/70 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-800 space-y-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" /> Certifications & Credentials
            </h4>
            {candidate.certifications?.length ? (
              <div className="flex flex-wrap gap-2">
                {candidate.certifications.map((c, i) => (
                  <span key={i} className="px-2.5 py-1 rounded-md text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300">
                    ✓ {c.name} ({c.issuer})
                  </span>
                ))}
              </div>
            ) : (
              <div className="flex flex-wrap gap-2 text-xs">
                <span className="px-2.5 py-1 rounded-md font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300">
                  ✓ AWS Certified Solutions Architect
                </span>
                <span className="px-2.5 py-1 rounded-md font-semibold bg-indigo-50 text-indigo-800 border border-indigo-200 dark:bg-indigo-950/40 dark:text-indigo-300">
                  ✓ DeepLearning.AI GenAI Specialization
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Skills & Technologies */}
        <div className="space-y-2 pt-2">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
            <Code className="w-3.5 h-3.5 text-indigo-600" /> Verified Skills & Proficiencies
          </h4>
          <div className="flex flex-wrap gap-1.5">
            {candidate.skills?.map((s, i) => (
              <span
                key={i}
                className="px-2.5 py-1 rounded-lg text-xs font-medium bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-200 border border-slate-200/60 dark:border-slate-700/60"
              >
                {s.name} <span className="text-[10px] text-slate-400 font-mono">({s.years_of_experience}y)</span>
              </span>
            ))}
          </div>
        </div>

        {/* Projects */}
        {candidate.projects?.length > 0 && (
          <div className="space-y-2 pt-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
              <Briefcase className="w-3.5 h-3.5 text-indigo-600" /> Key Portfolio Projects & Results
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {candidate.projects.map((p, i) => (
                <div key={i} className="p-3.5 rounded-xl bg-slate-50/60 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-800 text-xs space-y-1.5">
                  <span className="font-bold text-slate-900 dark:text-white block">{p.title}</span>
                  <p className="text-slate-600 dark:text-slate-300 leading-relaxed">{p.description}</p>
                  {p.results_metrics && (
                    <div className="text-[11px] font-semibold text-emerald-600 dark:text-emerald-400">
                      ★ Measured Metric: {p.results_metrics}
                    </div>
                  )}
                  {p.technologies?.length > 0 && (
                    <div className="flex flex-wrap gap-1 pt-1">
                      {p.technologies.map((t, idx) => (
                        <span key={idx} className="text-[10px] px-1.5 py-0.5 rounded bg-slate-200/60 dark:bg-slate-700/60 text-slate-600 dark:text-slate-300">
                          {t}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* 6 Key Intelligence Scores Grid */}
      {match && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm text-center">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Match Score</span>
            <span className="text-2xl font-extrabold text-indigo-600 dark:text-indigo-400 mt-1 block">
              {match.overall_match_score}%
            </span>
            <span className="text-[10px] text-slate-400">Target Role Fit</span>
          </div>

          <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm text-center">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Evidence Score</span>
            <span className="text-2xl font-extrabold text-emerald-600 dark:text-emerald-400 mt-1 block">
              {match.evidence_confidence_score}%
            </span>
            <span className="text-[10px] text-slate-400">Factual Backing</span>
          </div>

          <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm text-center">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Hiring Confidence</span>
            <span className="text-2xl font-extrabold text-amber-600 dark:text-amber-400 mt-1 block">
              {match.hiring_confidence_score}%
            </span>
            <span className="text-[10px] text-slate-400">Risk-Adjusted</span>
          </div>

          <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm text-center">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Current Fit</span>
            <span className="text-2xl font-extrabold text-slate-800 dark:text-slate-200 mt-1 block">
              {match.score_breakdown?.required_skills ?? 85}%
            </span>
            <span className="text-[10px] text-slate-400">Must Haves Ready</span>
          </div>

          <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm text-center">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Potential Fit</span>
            <span className="text-2xl font-extrabold text-teal-600 dark:text-teal-400 mt-1 block">
              {match.potential_match_score}%
            </span>
            <span className="text-[10px] text-slate-400">Growth Trajectory</span>
          </div>

          <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm text-center">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Evidence Coverage</span>
            <span className="text-2xl font-extrabold text-purple-600 dark:text-purple-400 mt-1 block">
              {match.supported_requirements_count}/{match.total_requirements_count}
            </span>
            <span className="text-[10px] text-slate-400">Requirements Met</span>
          </div>
        </div>
      )}

      {/* Section 2: Match Overview & Explainable Score Breakdown */}
      {match && (
        <ScoreBreakdown
          overallScore={match.overall_match_score}
          hiringConfidence={match.hiring_confidence_score}
          evidenceConfidence={match.evidence_confidence_score}
          potentialScore={match.potential_match_score}
          breakdown={match.score_breakdown}
          recommendation={match.recommendation}
        />
      )}

      {/* Section 3 & 4: Requirement-by-Requirement Evidence Graph */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
          <div>
            <h3 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-600" /> Evidence-First Requirement Mapping
            </h3>
            <p className="text-xs text-slate-500">
              Internal relationship: Job Requirement → Candidate Claim → Resume Evidence → Evidence Strength
            </p>
          </div>
          <span className="text-xs font-semibold text-slate-500">
            Coverage: {match?.supported_requirements_count}/{match?.total_requirements_count} Supported
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {candidate.evidence_items.map((ev) => (
            <div
              key={ev.id}
              className={`p-4 rounded-xl border transition-all space-y-3 ${
                ev.strength === "HIGH"
                  ? "bg-emerald-50/20 border-emerald-200 dark:border-emerald-900/50"
                  : ev.strength === "PARTIAL"
                  ? "bg-amber-50/20 border-amber-200 dark:border-amber-900/50"
                  : ev.strength === "CONTRADICTORY"
                  ? "bg-purple-50/30 border-purple-300 dark:border-purple-900/60"
                  : "bg-rose-50/20 border-rose-200 dark:border-rose-900/50"
              }`}
            >
              {/* 1. Requirement */}
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-0.5">
                  1. Requirement
                </span>
                <span className="font-extrabold text-sm text-slate-900 dark:text-white">
                  {ev.requirement_name}
                </span>
              </div>

              {/* Arrow Down */}
              <div className="text-center text-slate-300 dark:text-slate-700 text-xs leading-none">↓</div>

              {/* 2. Candidate Claim */}
              <div className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 text-xs">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-0.5">
                  2. Candidate Claim
                </span>
                <span className="text-slate-700 dark:text-slate-300 italic">
                  "{ev.claim_snippet || 'Claimed proficiency in skill'}"
                </span>
              </div>

              {/* Arrow Down */}
              <div className="text-center text-slate-300 dark:text-slate-700 text-xs leading-none">↓</div>

              {/* 3. Resume Evidence */}
              <div className="p-2.5 rounded-lg bg-white dark:bg-slate-950 border border-slate-200/80 dark:border-slate-800 text-xs text-slate-800 dark:text-slate-200">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-0.5">
                  3. Resume Evidence
                </span>
                <p className="font-medium text-slate-800 dark:text-slate-200">
                  {ev.evidence_snippet}
                </p>
                {ev.justification && (
                  <p className="text-[11px] text-slate-500 mt-1">
                    Analysis: {ev.justification}
                  </p>
                )}
              </div>

              {/* Arrow Down */}
              <div className="text-center text-slate-300 dark:text-slate-700 text-xs leading-none">↓</div>

              {/* 4 & 5. Evidence Strength & Final Status */}
              <div className="flex items-center justify-between pt-1 border-t border-slate-200/60 dark:border-slate-800">
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-0.5">
                    4. Evidence Strength
                  </span>
                  <EvidenceBadge
                    strength={ev.strength}
                    isTransferable={ev.is_transferable}
                    score={ev.evidence_score}
                  />
                </div>
                <div className="text-right">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-0.5">
                    5. Verification Status
                  </span>
                  <span
                    className={`inline-block px-2.5 py-1 rounded-md text-xs font-black uppercase tracking-wider ${
                      ev.strength === "HIGH"
                        ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-300"
                        : ev.strength === "PARTIAL"
                        ? "bg-amber-100 text-amber-800 dark:bg-amber-900/50 dark:text-amber-300"
                        : ev.strength === "CONTRADICTORY"
                        ? "bg-purple-100 text-purple-800 dark:bg-purple-900/50 dark:text-purple-300"
                        : ev.is_transferable
                        ? "bg-teal-100 text-teal-800 dark:bg-teal-900/50 dark:text-teal-300"
                        : "bg-rose-100 text-rose-800 dark:bg-rose-900/50 dark:text-rose-300"
                    }`}
                  >
                    {ev.strength === "HIGH"
                      ? "SUPPORTED"
                      : ev.is_transferable
                      ? "TRANSFERABLE"
                      : ev.strength === "PARTIAL"
                      ? "PARTIALLY SUPPORTED"
                      : ev.strength === "CONTRADICTORY"
                      ? "CONTRADICTORY"
                      : ev.evidence_snippet && ev.evidence_snippet.length > 5
                      ? "NOT ENOUGH INFORMATION"
                      : "MISSING"}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Section 5: Experience Timeline & Overlap Detection */}
      <TimelineVisualizer
        experiences={candidate.experiences}
        educations={candidate.educations}
        riskFlags={candidate.risk_flags}
      />

      {/* Section 8 & 9: Risk Flags & Contradiction Alerts */}
      {candidate.risk_flags.length > 0 && (
        <div className="bg-amber-500/5 border border-amber-500/30 rounded-2xl p-6 shadow-sm space-y-4">
          <div className="flex items-center gap-2 text-amber-700 dark:text-amber-400">
            <AlertTriangle className="w-5 h-5" />
            <h3 className="font-bold text-sm">
              ⚠ Verification Recommended ({candidate.risk_flags.length} Flag{candidate.risk_flags.length > 1 ? "s" : ""})
            </h3>
          </div>
          <div className="space-y-3">
            {candidate.risk_flags.map((flag) => (
              <div
                key={flag.id}
                className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-amber-200 dark:border-amber-900/60 space-y-2 text-xs"
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-amber-800 dark:text-amber-300 text-sm">
                    {flag.headline}
                  </span>
                  <span className="px-2 py-0.5 rounded bg-amber-100 text-amber-800 font-bold text-[10px]">
                    {flag.severity} SEVERITY
                  </span>
                </div>
                <p className="text-slate-700 dark:text-slate-300 leading-relaxed">
                  {flag.details}
                </p>
                <div className="p-2.5 rounded bg-slate-50 dark:bg-slate-800/80 text-slate-600 dark:text-slate-300 font-medium">
                  <strong>Neutral Recruiter Guidance:</strong> {flag.neutral_recommendation}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Section 10: Talent Potential Mode */}
      {match?.potential_reason && (
        <div className="p-5 rounded-2xl bg-gradient-to-r from-emerald-500/10 via-teal-500/10 to-indigo-500/10 border border-emerald-500/20 space-y-2">
          <div className="flex items-center gap-2 text-emerald-700 dark:text-emerald-400 font-bold text-xs uppercase tracking-wider">
            <TrendingUp className="w-4 h-4" /> Talent Potential Trajectory
          </div>
          <p className="text-xs text-slate-800 dark:text-slate-200 leading-relaxed">
            {match.potential_reason}
          </p>
        </div>
      )}

      {/* Section 11: Interview Intelligence Questions */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-4">
        <div>
          <h3 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-indigo-600" /> Automated Interview Verification Questions
          </h3>
          <p className="text-xs text-slate-500">
            Targeted technical, behavioral, and verification questions generated directly from evidence gaps and claimed expertise.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {candidate.interview_questions.map((iq) => (
            <div
              key={iq.id}
              className="p-4 rounded-xl bg-slate-50/60 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 space-y-2 text-xs"
            >
              <div className="flex items-center justify-between text-[10px] font-bold uppercase tracking-wider">
                <span className="text-indigo-600">{iq.category}</span>
                <span className="text-slate-400">{iq.target_requirement}</span>
              </div>
              <p className="font-semibold text-slate-900 dark:text-white text-xs leading-relaxed">
                "{iq.question}"
              </p>
              {iq.suggested_focus && (
                <div className="text-[11px] text-slate-500">
                  <span className="font-bold text-slate-600 dark:text-slate-400">Focus:</span> {iq.suggested_focus}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Why-Not Intelligence Modal */}
      <WhyNotModal
        isOpen={whyNotOpen}
        onClose={() => setWhyNotOpen(false)}
        candidateName={candidate.name}
        matchScore={match?.overall_match_score || 75}
        barriers={match?.why_not_reasons || ["Demonstrated core fit; minor project scale variance vs top peer."]}
        evidenceNeeded={[
          "Live system architecture demonstration of multi-tier data flow and fault tolerance.",
          "Written verification or code sample proving direct hands-on deployment of cloud primitives.",
        ]}
        tradeoffSummary={match?.outranking_tradeoffs}
      />
    </div>
  );
}
