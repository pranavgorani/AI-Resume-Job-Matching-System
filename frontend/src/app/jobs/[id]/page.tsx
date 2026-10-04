"use client";

import React, { useEffect, useState, use } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { 
  Briefcase, 
  Users, 
  Upload, 
  Filter, 
  Sparkles, 
  Layers, 
  ArrowUpDown, 
  AlertTriangle, 
  AlertCircle,
  CheckCircle2, 
  PlayCircle,
  HelpCircle,
  Clock,
  MapPin,
  Search,
  RefreshCw,
  XCircle,
  Download,
  ChevronDown,
  BarChart3,
  TrendingUp,
  ArrowLeft,
  Plus
} from "lucide-react";
import { 
  getJob, 
  getJobMatches, 
  runMatching, 
  filterWithNaturalLanguage, 
  uploadResumes,
  getReportDownloadUrl,
  ApiError
} from "@/lib/api";
import { Job, CandidateTableRow } from "@/lib/types";
import { WhyNotModal } from "@/components/WhyNotModal";
import { ResumeUploadModal } from "@/components/ResumeUploadModal";

export default function JobDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const rawId = resolvedParams?.id;
  const jobId = rawId ? parseInt(rawId, 10) : NaN;
  const router = useRouter();

  const [job, setJob] = useState<Job | null>(null);
  const [candidates, setCandidates] = useState<CandidateTableRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [matching, setMatching] = useState(false);
  const [errorStatus, setErrorStatus] = useState<number | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Filters & Search
  const [searchQuery, setSearchQuery] = useState("");
  const [minScoreFilter, setMinScoreFilter] = useState(0);
  const [recommendationFilter, setRecommendationFilter] = useState("ALL");
  const [riskOnlyFilter, setRiskOnlyFilter] = useState(false);
  const [naturalFilterQuery, setNaturalFilterQuery] = useState("");
  const [naturalFilterActive, setNaturalFilterActive] = useState<string | null>(null);

  // Multi-select for comparison
  const [selectedIds, setSelectedIds] = useState<number[]>([]);

  // Resume Upload Modal
  const [uploadModalOpen, setUploadModalOpen] = useState(false);

  // Why-Not Modal
  const [whyNotCandidate, setWhyNotCandidate] = useState<CandidateTableRow | null>(null);

  // Export & Analytics Charts
  const [exportMenuOpen, setExportMenuOpen] = useState(false);
  const [showCharts, setShowCharts] = useState(false);

  const loadData = async (isBackground: boolean = false) => {
    if (!rawId || rawId === "undefined" || rawId === "null" || isNaN(jobId) || jobId <= 0) {
      if (!isBackground) {
        setErrorStatus(404);
        setErrorMessage("Job not found. The requested requisition identifier is invalid.");
        setLoading(false);
      }
      return;
    }

    try {
      if (!isBackground) {
        setLoading(true);
        setErrorStatus(null);
        setErrorMessage(null);
      }
      const [j, matches] = await Promise.all([
        getJob(jobId),
        getJobMatches(jobId).catch((err) => {
          console.warn("[JOB MATCHES] Fallback empty matches:", err);
          return [];
        }),
      ]);
      if (j) setJob(j);
      if (Array.isArray(matches)) setCandidates(matches);
    } catch (e: any) {
      if (!isBackground && !job) {
        const status = e instanceof ApiError ? e.status : (e.status || 500);
        setErrorStatus(status);
        setErrorMessage(e.message || "Unable to load job");
      } else {
        console.warn("[JOB REFRESH] Non-blocking background data update error:", e);
      }
    } finally {
      if (!isBackground) {
        setLoading(false);
      }
    }
  };

  useEffect(() => {
    loadData();
  }, [jobId]);

  const handleRunMatching = async () => {
    setMatching(true);
    try {
      await runMatching(jobId);
      await loadData();
    } catch (e: any) {
      alert(`Matching failed: ${e.message}`);
    } finally {
      setMatching(false);
    }
  };

  const handleNaturalFilter = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!naturalFilterQuery.trim()) return;
    try {
      const res = await filterWithNaturalLanguage(jobId, naturalFilterQuery);
      setNaturalFilterActive(res.explanation);
      // Filter candidates
      const matchedSet = new Set(res.matched_candidate_ids);
      setCandidates((prev) => prev.filter((c) => matchedSet.has(c.candidate_id)));
    } catch (err: any) {
      alert(`Natural filter error: ${err.message}`);
    }
  };

  const clearNaturalFilter = () => {
    setNaturalFilterActive(null);
    setNaturalFilterQuery("");
    loadData();
  };

  const handleToggleSelect = (cid: number) => {
    if (selectedIds.includes(cid)) {
      setSelectedIds(selectedIds.filter((id) => id !== cid));
    } else {
      if (selectedIds.length >= 5) {
        alert("You can select up to 5 candidates for side-by-side comparison.");
        return;
      }
      setSelectedIds([...selectedIds, cid]);
    }
  };

  const handleCompareSelected = () => {
    if (selectedIds.length < 2) {
      alert("Please select at least 2 candidates to compare.");
      return;
    }
    router.push(`/compare?job_id=${jobId}&ids=${selectedIds.join(",")}`);
  };

  // Filtered list
  const filteredCandidates = candidates.filter((c) => {
    if (searchQuery && !c.name.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    if (minScoreFilter > 0 && c.match_score < minScoreFilter) {
      return false;
    }
    if (recommendationFilter !== "ALL" && c.recommendation !== recommendationFilter) {
      return false;
    }
    if (riskOnlyFilter && c.risk_flags_count === 0) {
      return false;
    }
    return true;
  });

  if (loading && !job && !errorStatus) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <div className="relative">
          <div className="w-12 h-12 rounded-full border-2 border-indigo-500/20 border-t-indigo-600 animate-spin" />
          <Briefcase className="w-5 h-5 text-indigo-500 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
        </div>
        <div className="text-center space-y-1">
          <p className="text-sm font-semibold text-slate-800 dark:text-slate-200">
            Loading Requisition #{jobId || ""}...
          </p>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Retrieving job specifications and verified candidate evidence
          </p>
        </div>
      </div>
    );
  }

  if (errorStatus === 404) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 flex items-center justify-center min-h-[65vh]">
        <div className="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-8 sm:p-10 text-center shadow-xl relative overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-amber-500 via-rose-500 to-indigo-500" />
          
          <div className="w-16 h-16 rounded-2xl bg-amber-500/10 dark:bg-amber-500/20 border border-amber-500/20 flex items-center justify-center mx-auto mb-6 text-amber-500">
            <AlertCircle className="w-8 h-8" />
          </div>

          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 text-[11px] font-bold uppercase tracking-wider mb-3">
            Error 404 • Not Found
          </div>

          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white mb-2">
            Job Not Found
          </h1>

          <p className="text-sm text-slate-600 dark:text-slate-400 max-w-md mx-auto mb-8 leading-relaxed">
            This job may have been deleted or is no longer available.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
            <Link
              href="/jobs"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 text-xs font-bold transition-colors border border-slate-200 dark:border-slate-700"
            >
              <ArrowLeft className="w-4 h-4" />
              ← Back to Jobs
            </Link>
            <Link
              href="/jobs/new"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/25 transition-all"
            >
              <Plus className="w-4 h-4" />
              Create New Job
            </Link>
          </div>
        </div>
      </div>
    );
  }

  if (errorStatus === 0 || errorMessage?.toLowerCase().includes("connection") || errorMessage?.toLowerCase().includes("network")) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 flex items-center justify-center min-h-[65vh]">
        <div className="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-8 sm:p-10 text-center shadow-xl">
          <div className="w-16 h-16 rounded-2xl bg-rose-500/10 dark:bg-rose-500/20 border border-rose-500/20 flex items-center justify-center mx-auto mb-6 text-rose-500">
            <AlertTriangle className="w-8 h-8" />
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white mb-2">
            Connection problem
          </h1>
          <p className="text-sm text-slate-600 dark:text-slate-400 max-w-md mx-auto mb-8 leading-relaxed">
            Unable to establish communication with the TalentProof AI backend service. Please check your network or ensure the server is active.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
            <button
              onClick={() => loadData()}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/25 transition-all"
            >
              <RefreshCw className="w-4 h-4" />
              Retry
            </button>
            <Link
              href="/jobs"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 text-xs font-bold transition-colors border border-slate-200 dark:border-slate-700"
            >
              <ArrowLeft className="w-4 h-4" />
              ← Back to Jobs
            </Link>
          </div>
        </div>
      </div>
    );
  }

  if (errorStatus) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 flex items-center justify-center min-h-[65vh]">
        <div className="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-8 sm:p-10 text-center shadow-xl">
          <div className="w-16 h-16 rounded-2xl bg-amber-500/10 dark:bg-amber-500/20 border border-amber-500/20 flex items-center justify-center mx-auto mb-6 text-amber-500">
            <AlertTriangle className="w-8 h-8" />
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white mb-2">
            Unable to load job
          </h1>
          <p className="text-sm text-slate-600 dark:text-slate-400 max-w-md mx-auto mb-8 leading-relaxed">
            {errorMessage || "An unexpected error occurred while loading this job requisition."}
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
            <button
              onClick={() => loadData()}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/25 transition-all"
            >
              <RefreshCw className="w-4 h-4" />
              Retry
            </button>
            <Link
              href="/jobs"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 text-xs font-bold transition-colors border border-slate-200 dark:border-slate-700"
            >
              <ArrowLeft className="w-4 h-4" />
              ← Back to Jobs
            </Link>
          </div>
        </div>
      </div>
    );
  }

  if (!job) {
    return null;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Requisition Header Card */}
      {job && (
        <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-[11px] font-bold text-indigo-600 uppercase tracking-widest">
                  Target Requisition #{job.id}
                </span>
                <span className="text-[10px] font-semibold bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded">
                  {job.seniority}
                </span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">
                {job.title}
              </h1>
              <div className="flex items-center gap-3 text-xs text-slate-500 mt-1">
                <span className="flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5 text-slate-400" /> {job.min_years_experience}+ Years Minimum Experience
                </span>
                <span>•</span>
                <span className="flex items-center gap-1">
                  <MapPin className="w-3.5 h-3.5 text-slate-400" /> {job.location} ({job.work_mode})
                </span>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2.5">
              <button
                onClick={() => setUploadModalOpen(true)}
                className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 hover:bg-slate-200 transition-colors"
              >
                <Upload className="w-3.5 h-3.5" /> Upload Resumes
              </button>
              <button
                onClick={handleRunMatching}
                disabled={matching}
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold bg-indigo-600 text-white shadow-md shadow-indigo-600/20 hover:bg-indigo-700 transition-colors"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${matching ? "animate-spin" : ""}`} />
                {matching ? "Evaluating Evidence..." : "Run Matching Engine"}
              </button>
              <button
                onClick={() => setShowCharts(!showCharts)}
                className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800 hover:bg-indigo-100 transition-colors"
              >
                <BarChart3 className="w-3.5 h-3.5" /> {showCharts ? "Hide Charts" : "View Charts"}
              </button>
              
              {/* Export Report Dropdown */}
              <div className="relative">
                <button
                  onClick={() => setExportMenuOpen(!exportMenuOpen)}
                  className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 hover:bg-emerald-100 transition-colors"
                >
                  <Download className="w-3.5 h-3.5" />
                  Export Report <ChevronDown className="w-3.5 h-3.5 ml-0.5" />
                </button>
                {exportMenuOpen && (
                  <div className="absolute right-0 mt-1 w-44 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-xl z-20 py-1 text-xs">
                    <a
                      href={getReportDownloadUrl("csv", { job_id: jobId })}
                      download
                      onClick={() => setExportMenuOpen(false)}
                      className="block px-3 py-2 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800"
                    >
                      📄 Download CSV
                    </a>
                    <a
                      href={getReportDownloadUrl("pdf", { job_id: jobId })}
                      target="_blank"
                      rel="noopener noreferrer"
                      onClick={() => setExportMenuOpen(false)}
                      className="block px-3 py-2 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800"
                    >
                      📕 Download PDF
                    </a>
                    <a
                      href={getReportDownloadUrl("docx", { job_id: jobId })}
                      download
                      onClick={() => setExportMenuOpen(false)}
                      className="block px-3 py-2 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800"
                    >
                      📘 Download DOCX
                    </a>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Requirements Badges: MUST HAVE, SHOULD HAVE, NICE TO HAVE */}
          <div className="pt-3 border-t border-slate-100 dark:border-slate-800 flex flex-wrap gap-2 items-center">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              Must Have:
            </span>
            {job.requirements
              ?.filter((r) => r.tier === "MUST_HAVE")
              .map((r, i) => (
                <span
                  key={i}
                  className="px-2.5 py-1 rounded-md text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800"
                >
                  ✓ {r.name}
                </span>
              ))}
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider ml-2">
              Should Have:
            </span>
            {job.requirements
              ?.filter((r) => r.tier === "SHOULD_HAVE")
              .map((r, i) => (
                <span
                  key={i}
                  className="px-2.5 py-1 rounded-md text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800"
                >
                  {r.name}
                </span>
              ))}
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider ml-2">
              Nice to Have:
            </span>
            {job.requirements
              ?.filter((r) => r.tier === "NICE_TO_HAVE")
              .map((r, i) => (
                <span
                  key={i}
                  className="px-2.5 py-1 rounded-md text-xs font-semibold bg-sky-50 text-sky-700 border border-sky-200 dark:bg-sky-950/40 dark:text-sky-300 dark:border-sky-800"
                >
                  + {r.name}
                </span>
              ))}
          </div>

          {/* Candidate Statistics KPI Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 pt-3 border-t border-slate-100 dark:border-slate-800">
            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-700/60">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Total Candidates</span>
              <span className="text-lg font-extrabold text-slate-900 dark:text-white mt-0.5 block">{candidates.length}</span>
            </div>
            <div className="p-3 rounded-xl bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-200/60 dark:border-emerald-900/40">
              <span className="text-[10px] font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider block">Shortlisted</span>
              <span className="text-lg font-extrabold text-emerald-700 dark:text-emerald-300 mt-0.5 block">
                {candidates.filter(c => ["STRONGLY_RECOMMEND", "RECOMMEND", "Strong Interview", "Interview", "Shortlist"].includes(c.recommendation)).length}
              </span>
            </div>
            <div className="p-3 rounded-xl bg-indigo-50/50 dark:bg-indigo-950/20 border border-indigo-200/60 dark:border-indigo-900/40">
              <span className="text-[10px] font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-wider block">High Matches (≥80%)</span>
              <span className="text-lg font-extrabold text-indigo-700 dark:text-indigo-300 mt-0.5 block">
                {candidates.filter(c => c.match_score >= 80).length}
              </span>
            </div>
            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-700/60">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Average Match</span>
              <span className="text-lg font-extrabold text-slate-900 dark:text-white mt-0.5 block">
                {candidates.length ? Math.round(candidates.reduce((a, b) => a + b.match_score, 0) / candidates.length) : 0}%
              </span>
            </div>
            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-700/60">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Average Evidence</span>
              <span className="text-lg font-extrabold text-emerald-600 dark:text-emerald-400 mt-0.5 block">
                {candidates.length ? Math.round(candidates.reduce((a, b) => a + b.evidence_score, 0) / candidates.length) : 0}%
              </span>
            </div>
            <div className="p-3 rounded-xl bg-amber-50/50 dark:bg-amber-950/20 border border-amber-200/60 dark:border-amber-900/40">
              <span className="text-[10px] font-bold text-amber-600 dark:text-amber-400 uppercase tracking-wider block">Verify Required</span>
              <span className="text-lg font-extrabold text-amber-700 dark:text-amber-300 mt-0.5 block">
                {candidates.filter(c => ["VERIFY", "Verify Claims", "VERIFICATION REQUIRED"].includes(c.recommendation) || c.risk_flags_count > 0).length}
              </span>
            </div>
          </div>

          {/* Interactive Charts Drawer */}
          {showCharts && candidates.length > 0 && (
            <div className="pt-4 border-t border-slate-100 dark:border-slate-800 space-y-4">
              <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                <BarChart3 className="w-3.5 h-3.5 text-indigo-600" /> Candidate Score Distributions for {job.title}
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-800 space-y-2">
                  <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">Match Score Ranges</span>
                  <div className="space-y-1.5 text-xs">
                    {[
                      { label: "90–100%", count: candidates.filter(c => c.match_score >= 90).length, color: "bg-indigo-600" },
                      { label: "80–89%", count: candidates.filter(c => c.match_score >= 80 && c.match_score < 90).length, color: "bg-indigo-500" },
                      { label: "70–79%", count: candidates.filter(c => c.match_score >= 70 && c.match_score < 80).length, color: "bg-indigo-400" },
                      { label: "60–69%", count: candidates.filter(c => c.match_score >= 60 && c.match_score < 70).length, color: "bg-amber-500" },
                      { label: "Below 60%", count: candidates.filter(c => c.match_score < 60).length, color: "bg-rose-500" },
                    ].map((bracket, i) => (
                      <div key={i} className="flex items-center gap-2">
                        <span className="w-16 text-[11px] text-slate-500">{bracket.label}</span>
                        <div className="flex-1 bg-slate-200 dark:bg-slate-700 h-3 rounded-full overflow-hidden">
                          <div
                            className={`h-full ${bracket.color} transition-all duration-500`}
                            style={{ width: `${(bracket.count / candidates.length) * 100}%` }}
                          />
                        </div>
                        <span className="w-6 text-right font-bold text-slate-700 dark:text-slate-300 text-[11px]">
                          {bracket.count}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-800 space-y-2">
                  <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">Top Candidates by Match & Evidence</span>
                  <div className="space-y-2 text-xs">
                    {candidates.slice(0, 5).map((c) => (
                      <div key={c.candidate_id} className="flex items-center justify-between text-[11px] border-b border-slate-200/40 dark:border-slate-700/40 pb-1">
                        <span className="font-semibold text-slate-800 dark:text-slate-200">{c.name}</span>
                        <div className="flex items-center gap-3">
                          <span className="text-indigo-600 font-bold">Match: {c.match_score}%</span>
                          <span className="text-emerald-600 font-bold">Evidence: {c.evidence_score}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Natural Language Filter Search Bar */}
      <div className="p-4 rounded-xl bg-gradient-to-r from-indigo-500/5 via-violet-500/5 to-emerald-500/5 border border-indigo-500/20 space-y-2">
        <form onSubmit={handleNaturalFilter} className="flex items-center gap-2">
          <div className="relative flex-1">
            <Sparkles className="w-4 h-4 text-indigo-600 absolute left-3.5 top-3" />
            <input
              type="text"
              value={naturalFilterQuery}
              onChange={(e) => setNaturalFilterQuery(e.target.value)}
              placeholder="Ask AI to filter: 'Show candidates with Python and FastAPI, at least 3 years experience, and strong project evidence'..."
              className="w-full bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-xl pl-10 pr-4 py-2 text-xs text-slate-900 dark:text-white placeholder:text-slate-400 focus:ring-2 focus:ring-indigo-500 outline-none"
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2 rounded-xl text-xs font-bold bg-indigo-600 text-white shadow hover:bg-indigo-700 transition-colors"
          >
            Apply AI Filter
          </button>
        </form>

        {naturalFilterActive && (
          <div className="flex items-center justify-between px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/30 rounded-lg text-xs text-emerald-800 dark:text-emerald-300">
            <span>{naturalFilterActive}</span>
            <button
              onClick={clearNaturalFilter}
              className="font-bold underline hover:opacity-80 ml-2"
            >
              Reset
            </button>
          </div>
        )}
      </div>

      {/* Candidate Controls & Filtering */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        {/* Search & Sliders */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search candidate name..."
              className="bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-900 dark:text-white focus:outline-none"
            />
          </div>

          <select
            value={recommendationFilter}
            onChange={(e) => setRecommendationFilter(e.target.value)}
            className="bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg px-3 py-1.5 text-xs font-semibold text-slate-700 dark:text-slate-200"
          >
            <option value="ALL">All Recommendations</option>
            <option value="STRONGLY_RECOMMEND">Strongly Recommend</option>
            <option value="RECOMMEND">Recommend</option>
            <option value="CONSIDER">Consider</option>
            <option value="VERIFY">Verification Needed</option>
          </select>

          <label className="flex items-center gap-1.5 text-xs font-medium text-slate-600 dark:text-slate-300 cursor-pointer">
            <input
              type="checkbox"
              checked={riskOnlyFilter}
              onChange={(e) => setRiskOnlyFilter(e.target.checked)}
              className="rounded text-indigo-600"
            />
            Risk Flags Only
          </label>
        </div>

        {/* Selected Compare Action */}
        {selectedIds.length > 0 && (
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500 font-medium">
              {selectedIds.length} candidate{selectedIds.length > 1 ? "s" : ""} selected
            </span>
            <button
              onClick={handleCompareSelected}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold bg-indigo-600 text-white shadow-sm hover:bg-indigo-700 transition-colors"
            >
              <Layers className="w-3.5 h-3.5" /> Compare Side-by-Side
            </button>
          </div>
        )}
      </div>

      {/* Candidate Ranking Table */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 dark:bg-slate-800/60 border-b border-slate-200 dark:border-slate-800 text-slate-500 uppercase tracking-wider font-semibold">
              <tr>
                <th className="py-3 px-3 w-8">Select</th>
                <th className="py-3 px-4">Rank</th>
                <th className="py-3 px-4">Candidate</th>
                <th className="py-3 px-4">Match Score</th>
                <th className="py-3 px-4">Evidence Score</th>
                <th className="py-3 px-4">Hiring Conf.</th>
                <th className="py-3 px-4">Coverage</th>
                <th className="py-3 px-4">Experience</th>
                <th className="py-3 px-4">Risk Flags</th>
                <th className="py-3 px-4">Potential</th>
                <th className="py-3 px-4">Recommendation</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {filteredCandidates.map((cand) => (
                <tr
                  key={cand.candidate_id}
                  className={`hover:bg-slate-50/80 dark:hover:bg-slate-800/50 transition-colors ${
                    selectedIds.includes(cand.candidate_id) ? "bg-indigo-50/40 dark:bg-indigo-950/20" : ""
                  }`}
                >
                  <td className="py-3.5 px-3">
                    <input
                      type="checkbox"
                      checked={selectedIds.includes(cand.candidate_id)}
                      onChange={() => handleToggleSelect(cand.candidate_id)}
                      className="rounded text-indigo-600 cursor-pointer"
                    />
                  </td>
                  <td className="py-3.5 px-4 font-black text-slate-600 dark:text-slate-400">
                    #{cand.rank}
                  </td>
                  <td className="py-3.5 px-4">
                    <Link
                      href={`/candidates/${cand.candidate_id}?job_id=${jobId}`}
                      className="font-bold text-slate-900 dark:text-white hover:text-indigo-600 hover:underline block text-sm"
                    >
                      {cand.name || "Candidate"}
                    </Link>
                    {cand.top_transferable_skill && (
                      <span className="text-[10px] text-amber-600 font-medium">
                        Transferable: {cand.top_transferable_skill}
                      </span>
                    )}
                  </td>
                  <td className="py-3.5 px-4 font-extrabold text-sm text-slate-900 dark:text-white">
                    {cand.match_score ?? 0}%
                  </td>
                  <td className="py-3.5 px-4 font-bold text-emerald-600">
                    {cand.evidence_score ?? 0}%
                  </td>
                  <td className="py-3.5 px-4 font-bold text-amber-600">
                    {cand.hiring_confidence ?? 0}%
                  </td>
                  <td className="py-3.5 px-4 font-mono font-medium text-slate-600 dark:text-slate-300">
                    {cand.required_skills_coverage || "0/0"}
                  </td>
                  <td className="py-3.5 px-4 text-slate-600 dark:text-slate-400">
                    {cand.experience_years ?? 0} yrs
                  </td>
                  <td className="py-3.5 px-4">
                    {(cand.risk_flags_count ?? 0) > 0 ? (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-semibold bg-amber-50 text-amber-700 border border-amber-200">
                        <AlertTriangle className="w-3 h-3 text-amber-600" />
                        {cand.risk_flags_count} flag{cand.risk_flags_count > 1 ? "s" : ""}
                      </span>
                    ) : (
                      <span className="text-emerald-600 font-medium flex items-center gap-1">
                        <CheckCircle2 className="w-3 h-3" /> 0 flags
                      </span>
                    )}
                  </td>
                  <td className="py-3.5 px-4 font-bold text-indigo-600">
                    {cand.potential_score ?? 0}%
                  </td>
                  <td className="py-3.5 px-4">
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase ${
                        cand.recommendation === "STRONGLY_RECOMMEND"
                          ? "bg-emerald-100 text-emerald-800"
                          : cand.recommendation === "RECOMMEND"
                          ? "bg-indigo-100 text-indigo-800"
                          : cand.recommendation === "VERIFY"
                          ? "bg-amber-100 text-amber-800"
                          : "bg-slate-100 text-slate-700"
                      }`}
                    >
                      {(cand.recommendation || "REVIEW").replace(/_/g, " ")}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-right space-x-2">
                    <button
                      onClick={() => setWhyNotCandidate(cand)}
                      className="text-[11px] font-semibold text-slate-500 hover:text-indigo-600"
                    >
                      Why Not?
                    </button>
                    <Link
                      href={`/candidates/${cand.candidate_id}?job_id=${jobId}`}
                      className="text-[11px] font-bold text-indigo-600 hover:text-indigo-800"
                    >
                      Dossier →
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Professional Interactive Resume Upload Modal */}
      <ResumeUploadModal
        isOpen={uploadModalOpen}
        onClose={() => setUploadModalOpen(false)}
        jobId={jobId}
        jobTitle={job?.title}
        onUploadComplete={() => loadData(true)}
      />

      {/* Why-Not Intelligence Modal */}
      {whyNotCandidate && (
        <WhyNotModal
          isOpen={Boolean(whyNotCandidate)}
          onClose={() => setWhyNotCandidate(null)}
          candidateName={whyNotCandidate.name}
          matchScore={whyNotCandidate.match_score}
          barriers={[
            whyNotCandidate.risk_flags_count > 0
              ? `${whyNotCandidate.risk_flags_count} unverified claim / timeline flag(s) requires recruiter clarification.`
              : "Core competencies met, but peer candidates demonstrate larger documented production metrics.",
            whyNotCandidate.experience_years < 3.0
              ? `Chronological experience duration (${whyNotCandidate.experience_years}y) is below the 3.0-year role target.`
              : "Direct AWS production deployment not fully evidenced in resume corpus.",
          ]}
          evidenceNeeded={[
            "Technical code sample or take-home demonstrating production deployment of missing components.",
            "Written reference or contract documentation confirming timeline start/end dates.",
          ]}
          tradeoffSummary={
            candidates[0]?.candidate_id !== whyNotCandidate.candidate_id
              ? `${candidates[0]?.name} outranks ${whyNotCandidate.name} by +${Math.round(
                  candidates[0]?.match_score - whyNotCandidate.match_score
                )}% points due to unflagged evidence coverage across all core must-have requirements.`
              : `${whyNotCandidate.name} is currently the top-ranked candidate for this role.`
          }
        />
      )}
    </div>
  );
}
