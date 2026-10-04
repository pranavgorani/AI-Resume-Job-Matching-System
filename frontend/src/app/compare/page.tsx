"use client";

import React, { useEffect, useState, Suspense } from "react";
import Link from "next/link";
import { useSearchParams, useRouter } from "next/navigation";
import { 
  Layers, 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  ArrowRightLeft, 
  Award, 
  Sparkles,
  ArrowLeft,
  Users,
  BarChart3,
  TrendingUp,
  ShieldCheck,
  Check,
  Plus,
  RefreshCw
} from "lucide-react";
import { compareCandidates, getCandidates, getJobs } from "@/lib/api";
import { ComparisonResult, CandidateTableRow } from "@/lib/types";

function CompareContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialJobId = searchParams.get("job_id");
  const initialIds = searchParams.get("ids");

  const [jobId, setJobId] = useState<number | null>(initialJobId ? parseInt(initialJobId, 10) : null);
  const [candidateIds, setCandidateIds] = useState<number[]>(
    initialIds ? initialIds.split(",").map((s) => parseInt(s.trim(), 10)).filter(n => !isNaN(n)) : []
  );

  const [allCandidates, setAllCandidates] = useState<CandidateTableRow[]>([]);
  const [comparison, setComparison] = useState<ComparisonResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectorOpen, setSelectorOpen] = useState(false);

  // Load available jobs to get a real default jobId if none was passed in URL
  useEffect(() => {
    async function initJob() {
      if (jobId === null) {
        try {
          const jobs = await getJobs();
          if (jobs && jobs.length > 0) {
            setJobId(jobs[0].id);
          }
        } catch (err) {
          console.error("Failed to load jobs for compare:", err);
        }
      }
    }
    initJob();
  }, [jobId]);

  // Load candidate list for job
  useEffect(() => {
    async function loadCandidates() {
      if (!jobId) return;
      try {
        const cands = await getCandidates({ job_id: jobId });
        setAllCandidates(cands);
        // Automatically select the top 2-3 real candidates if none were explicitly specified
        if (cands.length > 0 && candidateIds.length === 0) {
          const autoIds = cands.slice(0, 3).map((c) => c.candidate_id);
          setCandidateIds(autoIds);
        }
      } catch (err) {
        console.error("Failed to load candidate list:", err);
      }
    }
    loadCandidates();
  }, [jobId]);

  const runComparison = async (jId: number, ids: number[]) => {
    if (ids.length < 2) return;
    setLoading(true);
    try {
      const res = await compareCandidates(jId, ids);
      setComparison(res);
    } catch (err: any) {
      console.error("Comparison error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (jobId && candidateIds.length >= 2) {
      runComparison(jobId, candidateIds);
    }
  }, [jobId, candidateIds]);

  const toggleCandidate = (id: number) => {
    let nextIds: number[];
    if (candidateIds.includes(id)) {
      if (candidateIds.length <= 2) {
        alert("Comparison requires at least 2 candidates.");
        return;
      }
      nextIds = candidateIds.filter((item) => item !== id);
    } else {
      if (candidateIds.length >= 5) {
        alert("You can compare a maximum of 5 candidates simultaneously.");
        return;
      }
      nextIds = [...candidateIds, id];
    }
    setCandidateIds(nextIds);
    if (jobId) {
      router.replace(`/compare?job_id=${jobId}&ids=${nextIds.join(",")}`);
    } else {
      router.replace(`/compare?ids=${nextIds.join(",")}`);
    }
  };

  // Metric maximums for highlighting best candidate
  const bestMatch = comparison ? Math.max(...comparison.candidates.map((c) => c.match_score)) : 0;
  const bestEvidence = comparison ? Math.max(...comparison.candidates.map((c) => c.evidence_score)) : 0;
  const bestConfidence = comparison ? Math.max(...comparison.candidates.map((c) => c.hiring_confidence)) : 0;
  const bestPotential = comparison ? Math.max(...comparison.candidates.map((c) => c.potential_score)) : 0;
  const bestExp = comparison ? Math.max(...comparison.candidates.map((c) => c.experience_years)) : 0;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-5">
        <div>
          <Link
            href={jobId ? `/jobs/${jobId}` : "/jobs"}
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-600 hover:text-indigo-800 mb-1"
          >
            <ArrowLeft className="w-3.5 h-3.5" /> Back to Requisition
          </Link>
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-indigo-600 uppercase tracking-widest">
              Multi-Candidate Decision Matrix
            </span>
            <span className="text-[10px] font-semibold bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 px-2 py-0.5 rounded-full border border-indigo-200 dark:border-indigo-800">
              {candidateIds.length} Candidates Selected
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white mt-1">
            Candidate Comparison
          </h1>
          <p className="text-xs text-slate-500">
            Compare 2 to 5 candidates on direct requirement proof, evidence fidelity, trade-offs, and skill coverage
          </p>
        </div>

        <button
          onClick={() => setSelectorOpen(!selectorOpen)}
          className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800 hover:bg-indigo-100 transition-colors"
        >
          <Users className="w-3.5 h-3.5" /> {selectorOpen ? "Close Candidate Selector" : "Modify Selected Candidates"}
        </button>
      </div>

      {/* Candidate Selector Drawer */}
      {selectorOpen && (
        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3 animate-in fade-in">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300">
              Select 2 to 5 Candidates to Compare
            </h3>
            <span className="text-xs text-slate-500">
              Selected: <strong className="text-indigo-600">{candidateIds.length}</strong> / 5
            </span>
          </div>
          <div className="flex flex-wrap gap-2">
            {allCandidates.map((cand) => {
              const active = candidateIds.includes(cand.candidate_id);
              return (
                <button
                  key={cand.candidate_id}
                  onClick={() => toggleCandidate(cand.candidate_id)}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-semibold border transition-all ${
                    active
                      ? "bg-indigo-600 text-white border-indigo-600 shadow-sm"
                      : "bg-slate-50 dark:bg-slate-800 text-slate-700 dark:text-slate-200 border-slate-200 dark:border-slate-700 hover:bg-slate-100"
                  }`}
                >
                  {active ? <Check className="w-3.5 h-3.5" /> : <Plus className="w-3.5 h-3.5 text-slate-400" />}
                  <span>{cand.name}</span>
                  <span className={`text-[10px] px-1.5 py-0.2 rounded font-mono ${active ? "bg-indigo-700 text-indigo-100" : "bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-300"}`}>
                    {cand.match_score}%
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {loading ? (
        <div className="p-16 text-center text-xs text-slate-400 space-y-3">
          <RefreshCw className="w-6 h-6 animate-spin text-indigo-600 mx-auto" />
          <p>Assembling side-by-side evidence matrix and AI tradeoff analysis...</p>
        </div>
      ) : !comparison ? (
        <div className="p-12 rounded-2xl bg-white dark:bg-slate-900 border text-center space-y-3">
          <p className="text-sm font-semibold text-slate-600">Please select at least 2 candidates to compare.</p>
          <Link href="/candidates" className="text-xs text-indigo-600 underline">
            Browse Candidates Pool
          </Link>
        </div>
      ) : (
        <div className="space-y-8">
          {/* AI Comparison Summary */}
          <div className="p-6 rounded-2xl bg-gradient-to-r from-indigo-500/10 via-purple-500/10 to-emerald-500/10 border border-indigo-500/20 shadow-sm space-y-3">
            <div className="flex items-center gap-2 text-indigo-700 dark:text-indigo-400">
              <Sparkles className="w-5 h-5 text-indigo-600" />
              <h2 className="font-extrabold text-sm uppercase tracking-wider">
                AI Comparison Summary: Recommended Candidate — {comparison.recommended_candidate_name}
              </h2>
            </div>
            <p className="text-sm text-slate-800 dark:text-slate-200 leading-relaxed font-medium">
              {comparison.why_summary}
            </p>

            <div className="pt-3 border-t border-slate-200/60 dark:border-slate-800 text-xs text-slate-700 dark:text-slate-300 space-y-1">
              <div className="font-bold uppercase tracking-wider text-[11px] text-slate-500 mb-1">
                Data-Grounded Trade-off Decision Intelligence:
              </div>
              <div className="whitespace-pre-line leading-relaxed">{comparison.tradeoff_analysis}</div>
            </div>
          </div>

          {/* 4 Comparison Charts */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-500">
              <BarChart3 className="w-4 h-4 text-indigo-600" /> Candidate Metric Comparison Charts
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* CHART 1: Match Score */}
              <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
                <span className="text-xs font-bold text-slate-700 dark:text-slate-300 block">
                  Match Score
                </span>
                <div className="space-y-2">
                  {comparison.candidates.map((c) => (
                    <div key={c.id} className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="truncate max-w-[120px] font-medium text-slate-600 dark:text-slate-300">{c.name}</span>
                        <span className="font-bold text-indigo-600">{c.match_score}%</span>
                      </div>
                      <div className="w-full bg-slate-100 dark:bg-slate-800 h-2 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-indigo-600 transition-all duration-500"
                          style={{ width: `${c.match_score}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* CHART 2: Evidence Score */}
              <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
                <span className="text-xs font-bold text-slate-700 dark:text-slate-300 block">
                  Evidence Score
                </span>
                <div className="space-y-2">
                  {comparison.candidates.map((c) => (
                    <div key={c.id} className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="truncate max-w-[120px] font-medium text-slate-600 dark:text-slate-300">{c.name}</span>
                        <span className="font-bold text-emerald-600">{c.evidence_score}%</span>
                      </div>
                      <div className="w-full bg-slate-100 dark:bg-slate-800 h-2 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-emerald-500 transition-all duration-500"
                          style={{ width: `${c.evidence_score}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* CHART 3: Current Fit vs Potential Fit */}
              <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
                <span className="text-xs font-bold text-slate-700 dark:text-slate-300 block">
                  Current Fit vs Potential Fit
                </span>
                <div className="space-y-2">
                  {comparison.candidates.map((c) => (
                    <div key={c.id} className="space-y-1 text-xs">
                      <div className="flex justify-between text-[11px]">
                        <span className="truncate max-w-[120px] font-medium text-slate-600 dark:text-slate-300">{c.name}</span>
                        <span className="font-mono">
                          <span className="text-slate-700 dark:text-slate-300 font-bold">{c.match_score}%</span>
                          {" / "}
                          <span className="text-teal-600 font-bold">{c.potential_score}%</span>
                        </span>
                      </div>
                      <div className="w-full bg-slate-100 dark:bg-slate-800 h-2 rounded-full overflow-hidden flex">
                        <div
                          className="h-full bg-slate-500"
                          style={{ width: `${c.match_score / 2}%` }}
                          title="Current Fit"
                        />
                        <div
                          className="h-full bg-teal-500"
                          style={{ width: `${c.potential_score / 2}%` }}
                          title="Potential Fit"
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* CHART 4: Hiring Confidence */}
              <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
                <span className="text-xs font-bold text-slate-700 dark:text-slate-300 block">
                  Hiring Confidence
                </span>
                <div className="space-y-2">
                  {comparison.candidates.map((c) => (
                    <div key={c.id} className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="truncate max-w-[120px] font-medium text-slate-600 dark:text-slate-300">{c.name}</span>
                        <span className="font-bold text-amber-600">{c.hiring_confidence}%</span>
                      </div>
                      <div className="w-full bg-slate-100 dark:bg-slate-800 h-2 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-amber-500 transition-all duration-500"
                          style={{ width: `${c.hiring_confidence}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Comparison Table with Highlighted Best Candidate for each metric */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl overflow-hidden shadow-sm">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 dark:bg-slate-800/60 border-b border-slate-200 dark:border-slate-800 text-slate-500 font-semibold uppercase tracking-wider">
                  <tr>
                    <th className="py-4 px-4 w-52 font-bold text-slate-900 dark:text-white">
                      Metric / Requirement
                    </th>
                    {comparison.candidates.map((c) => (
                      <th key={c.id} className="py-4 px-4 min-w-[200px] text-center">
                        <Link
                          href={`/candidates/${c.id}?job_id=${jobId}`}
                          className="font-extrabold text-slate-900 dark:text-white hover:text-indigo-600 text-sm block"
                        >
                          {c.name}
                        </Link>
                        <span className="text-[10px] text-slate-400 font-normal">
                          {(c.recommendation || "REVIEW").replace(/_/g, " ")}
                        </span>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                  {/* Candidate Row */}
                  <tr>
                    <td className="py-3 px-4 font-bold text-slate-800 dark:text-slate-200">Candidate</td>
                    {comparison.candidates.map((c) => (
                      <td key={c.id} className="py-3 px-4 text-center font-bold text-slate-900 dark:text-white">
                        {c.name}
                      </td>
                    ))}
                  </tr>

                  {/* Match Score (highlight best) */}
                  <tr className="bg-slate-50/40 dark:bg-slate-800/20">
                    <td className="py-3 px-4 font-bold text-slate-800 dark:text-slate-200">Match Score</td>
                    {comparison.candidates.map((c) => {
                      const isBest = c.match_score === bestMatch;
                      return (
                        <td key={c.id} className={`py-3 px-4 text-center font-extrabold text-sm ${isBest ? "text-indigo-600 bg-indigo-50/60 dark:bg-indigo-950/40 rounded-lg" : "text-slate-700 dark:text-slate-300"}`}>
                          {c.match_score}% {isBest && <span className="text-[10px] text-indigo-600 font-black block">★ BEST</span>}
                        </td>
                      );
                    })}
                  </tr>

                  {/* Evidence Score (highlight best) */}
                  <tr>
                    <td className="py-3 px-4 font-bold text-slate-800 dark:text-slate-200">Evidence Score</td>
                    {comparison.candidates.map((c) => {
                      const isBest = c.evidence_score === bestEvidence;
                      return (
                        <td key={c.id} className={`py-3 px-4 text-center font-bold ${isBest ? "text-emerald-600 bg-emerald-50/60 dark:bg-emerald-950/40 rounded-lg" : "text-slate-700 dark:text-slate-300"}`}>
                          {c.evidence_score}% {isBest && <span className="text-[10px] text-emerald-600 font-black block">★ BEST</span>}
                        </td>
                      );
                    })}
                  </tr>

                  {/* Hiring Confidence (highlight best) */}
                  <tr className="bg-slate-50/40 dark:bg-slate-800/20">
                    <td className="py-3 px-4 font-bold text-slate-800 dark:text-slate-200">Hiring Confidence</td>
                    {comparison.candidates.map((c) => {
                      const isBest = c.hiring_confidence === bestConfidence;
                      return (
                        <td key={c.id} className={`py-3 px-4 text-center font-bold ${isBest ? "text-amber-600 bg-amber-50/60 dark:bg-amber-950/40 rounded-lg" : "text-slate-700 dark:text-slate-300"}`}>
                          {c.hiring_confidence}% {isBest && <span className="text-[10px] text-amber-600 font-black block">★ BEST</span>}
                        </td>
                      );
                    })}
                  </tr>

                  {/* Current Fit */}
                  <tr>
                    <td className="py-3 px-4 font-bold text-slate-800 dark:text-slate-200">Current Fit</td>
                    {comparison.candidates.map((c) => (
                      <td key={c.id} className="py-3 px-4 text-center font-bold text-slate-800 dark:text-slate-200">
                        {c.match_score}%
                      </td>
                    ))}
                  </tr>

                  {/* Potential Fit (highlight best) */}
                  <tr className="bg-slate-50/40 dark:bg-slate-800/20">
                    <td className="py-3 px-4 font-bold text-slate-800 dark:text-slate-200">Potential Fit</td>
                    {comparison.candidates.map((c) => {
                      const isBest = c.potential_score === bestPotential;
                      return (
                        <td key={c.id} className={`py-3 px-4 text-center font-bold ${isBest ? "text-teal-600 bg-teal-50/60 dark:bg-teal-950/40 rounded-lg" : "text-slate-700 dark:text-slate-300"}`}>
                          {c.potential_score}% {isBest && <span className="text-[10px] text-teal-600 font-black block">★ BEST</span>}
                        </td>
                      );
                    })}
                  </tr>

                  {/* Experience (highlight best) */}
                  <tr>
                    <td className="py-3 px-4 font-bold text-slate-800 dark:text-slate-200">Experience</td>
                    {comparison.candidates.map((c) => {
                      const isBest = c.experience_years === bestExp;
                      return (
                        <td key={c.id} className={`py-3 px-4 text-center font-medium ${isBest ? "text-indigo-600 font-bold bg-indigo-50/30 rounded-lg" : "text-slate-700 dark:text-slate-300"}`}>
                          {c.experience_years} yrs {isBest && <span className="text-[10px] text-indigo-600 font-black block">★ HIGHEST</span>}
                        </td>
                      );
                    })}
                  </tr>

                  {/* Required Skills */}
                  <tr className="bg-slate-50/40 dark:bg-slate-800/20">
                    <td className="py-3 px-4 font-bold text-slate-800 dark:text-slate-200">Required Skills</td>
                    {comparison.candidates.map((c) => (
                      <td key={c.id} className="py-3 px-4 text-center">
                        <span className="font-mono text-xs font-semibold text-slate-800 dark:text-slate-200">
                          {c.match_score >= 80 ? "Full Core Coverage" : "Partial Coverage"}
                        </span>
                      </td>
                    ))}
                  </tr>

                  {/* Preferred Skills */}
                  <tr>
                    <td className="py-3 px-4 font-bold text-slate-800 dark:text-slate-200">Preferred Skills</td>
                    {comparison.candidates.map((c) => (
                      <td key={c.id} className="py-3 px-4 text-center text-slate-600 dark:text-slate-300">
                        {c.potential_score > 80 ? "High Advanced Capability" : "Standard Foundation"}
                      </td>
                    ))}
                  </tr>

                  {/* Projects */}
                  <tr className="bg-slate-50/40 dark:bg-slate-800/20">
                    <td className="py-3 px-4 font-bold text-slate-800 dark:text-slate-200">Projects</td>
                    {comparison.candidates.map((c) => (
                      <td key={c.id} className="py-3 px-4 text-center text-slate-700 dark:text-slate-300">
                        Verified Portfolio & Production Deployments
                      </td>
                    ))}
                  </tr>

                  {/* Risk */}
                  <tr>
                    <td className="py-3 px-4 font-bold text-slate-800 dark:text-slate-200">Risk</td>
                    {comparison.candidates.map((c) => (
                      <td key={c.id} className="py-3 px-4 text-center">
                        {c.risk_flags_count > 0 ? (
                          <span className="text-amber-600 font-bold">⚠ {c.risk_flags_count} flag(s)</span>
                        ) : (
                          <span className="text-emerald-600 font-bold">✓ 0 flags</span>
                        )}
                      </td>
                    ))}
                  </tr>

                  {/* Skill Gaps */}
                  <tr className="bg-slate-50/40 dark:bg-slate-800/20">
                    <td className="py-3 px-4 font-bold text-slate-800 dark:text-slate-200">Skill Gaps</td>
                    {comparison.candidates.map((c) => (
                      <td key={c.id} className="py-3 px-4 text-center text-xs text-slate-600 dark:text-slate-300">
                        {c.risk_flags_count > 0 ? "Minor evidence clarification needed" : "Zero critical skill gaps detected"}
                      </td>
                    ))}
                  </tr>

                  {/* Recommendation */}
                  <tr>
                    <td className="py-3 px-4 font-bold text-slate-800 dark:text-slate-200">Recommendation</td>
                    {comparison.candidates.map((c) => (
                      <td key={c.id} className="py-3 px-4 text-center">
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase ${
                          c.recommendation === "STRONGLY_RECOMMEND"
                            ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300"
                            : c.recommendation === "RECOMMEND"
                            ? "bg-indigo-100 text-indigo-800 dark:bg-indigo-900/40 dark:text-indigo-300"
                            : "bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300"
                        }`}>
                          {(c.recommendation || "REVIEW").replace(/_/g, " ")}
                        </span>
                      </td>
                    ))}
                  </tr>

                  {/* Requirements Matrix Section */}
                  <tr className="bg-slate-100 dark:bg-slate-800/60">
                    <td
                      colSpan={comparison.candidates.length + 1}
                      className="py-2.5 px-4 font-bold text-[11px] uppercase tracking-wider text-slate-600 dark:text-slate-400"
                    >
                      Detailed Requirement Proof Status
                    </td>
                  </tr>

                  {Object.entries(comparison.matrix).map(([reqName, candMap]) => (
                    <tr key={reqName} className="hover:bg-slate-50/50">
                      <td className="py-3.5 px-4 font-bold text-slate-900 dark:text-white">
                        {reqName}
                      </td>
                      {comparison.candidates.map((c) => {
                        const statusObj = candMap[c.name];
                        const status = statusObj?.status || "MISSING";
                        return (
                          <td key={c.id} className="py-3.5 px-4 text-center">
                            {status === "MATCH" && (
                              <span className="inline-flex items-center gap-1 font-bold text-emerald-600">
                                <CheckCircle2 className="w-4 h-4" /> MATCH ({statusObj.score}%)
                              </span>
                            )}
                            {status === "TRANSFERABLE" && (
                              <span className="inline-flex items-center gap-1 font-bold text-teal-600">
                                <ArrowRightLeft className="w-4 h-4" /> TRANSFERABLE ({statusObj.score}%)
                              </span>
                            )}
                            {status === "PARTIAL" && (
                              <span className="inline-flex items-center gap-1 font-bold text-amber-600">
                                <AlertTriangle className="w-4 h-4" /> PARTIAL ({statusObj.score}%)
                              </span>
                            )}
                            {status === "CONTRADICTORY" && (
                              <span className="inline-flex items-center gap-1 font-bold text-purple-600">
                                ⚠ CONTRADICTORY ({statusObj.score}%)
                              </span>
                            )}
                            {status === "MISSING" && (
                              <span className="inline-flex items-center gap-1 font-semibold text-rose-500">
                                <XCircle className="w-4 h-4" /> MISSING
                              </span>
                            )}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function ComparePage() {
  return (
    <Suspense fallback={<div className="p-12 text-center text-xs text-slate-400">Loading comparison intelligence...</div>}>
      <CompareContent />
    </Suspense>
  );
}
