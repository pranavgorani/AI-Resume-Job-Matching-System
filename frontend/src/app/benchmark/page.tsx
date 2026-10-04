"use client";

import React, { useState, useEffect } from "react";
import { 
  Play, 
  RefreshCw, 
  ShieldCheck, 
  CheckCircle2, 
  AlertTriangle, 
  Zap, 
  TrendingUp, 
  Activity,
  Layers,
  Award,
  Clock,
  ArrowRight
} from "lucide-react";
import Link from "next/link";
import { runBenchmark, getLatestBenchmark } from "@/lib/api";

export default function BenchmarkPage() {
  const [seed, setSeed] = useState<number>(12345);
  const [isRunning, setIsRunning] = useState(false);
  const [progressStage, setProgressStage] = useState<string>("");
  const [progressCount, setProgressCount] = useState<number>(0);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getLatestBenchmark()
      .then((data) => {
        if (data?.has_run && data?.summary) {
          setResults({
            ...data.summary,
            benchmark_run_id: data.run_id,
            seed: data.seed,
          });
        }
      })
      .catch(() => {});
  }, []);

  const handleRunBenchmark = async () => {
    setIsRunning(true);
    setError(null);
    setProgressStage("Preparing 50 resumes...");
    setProgressCount(0);

    // Realistic UI progress simulation matching Section 25
    const progressInterval = setInterval(() => {
      setProgressCount((prev) => {
        if (prev < 12) {
          setProgressStage("Preparing 50 resumes...");
          return prev + 2;
        } else if (prev < 24) {
          setProgressStage("Uploaded to Supabase Storage...");
          return prev + 3;
        } else if (prev < 36) {
          setProgressStage("Parsing resume text...");
          return prev + 2;
        } else if (prev < 48) {
          setProgressStage("Mapping evidence & calculating explainable scores...");
          return prev + 1;
        }
        return prev;
      });
    }, 180);

    try {
      const res = await runBenchmark(seed);
      clearInterval(progressInterval);
      setProgressStage("Completed 50 / 50");
      setProgressCount(50);
      setResults(res);
    } catch (err: any) {
      clearInterval(progressInterval);
      setError(err?.message || "Benchmark failed to complete. Please retry.");
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-in fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-5">
        <div>
          <span className="text-xs font-bold text-indigo-600 uppercase tracking-widest flex items-center gap-1.5">
            <Zap className="w-3.5 h-3.5" /> Production Quality Assurance
          </span>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white mt-1">
            50-Resume Production Benchmark
          </h1>
          <p className="text-xs text-slate-500">
            Stress-test the end-to-end evidence pipeline against 50 randomized profiles across 5 realistic archetypes
          </p>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-slate-100 dark:bg-slate-800/80 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-700">
            <span className="text-xs text-slate-500 font-medium">Seed:</span>
            <input
              type="number"
              value={seed}
              onChange={(e) => setSeed(parseInt(e.target.value) || 12345)}
              className="w-20 bg-transparent text-xs font-mono font-bold text-slate-900 dark:text-white focus:outline-none"
              disabled={isRunning}
            />
          </div>

          <button
            onClick={handleRunBenchmark}
            disabled={isRunning}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-xs text-white bg-indigo-600 hover:bg-indigo-700 active:scale-95 disabled:opacity-50 transition-all shadow-md shadow-indigo-600/20"
          >
            {isRunning ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Processing 50 Resumes...
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current" />
                Run 50 Resume Benchmark
              </>
            )}
          </button>
        </div>
      </div>

      {/* Live Processing Indicator */}
      {isRunning && (
        <div className="bg-indigo-50/70 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800 rounded-2xl p-6 space-y-4 animate-pulse">
          <div className="flex items-center justify-between text-xs font-bold text-indigo-700 dark:text-indigo-300">
            <span className="flex items-center gap-2">
              <Activity className="w-4 h-4 animate-spin" />
              {progressStage}
            </span>
            <span className="font-mono text-sm">{progressCount} / 50 Completed</span>
          </div>
          <div className="w-full bg-indigo-100 dark:bg-indigo-900/60 rounded-full h-2.5 overflow-hidden">
            <div
              className="bg-indigo-600 h-2.5 rounded-full transition-all duration-300"
              style={{ width: `${(progressCount / 50) * 100}%` }}
            />
          </div>
        </div>
      )}

      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 rounded-xl text-xs text-red-700 dark:text-red-400 flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          {error}
        </div>
      )}

      {/* Benchmark Summary Metrics */}
      {results && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            <div className="bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200 dark:border-slate-800">
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Total</span>
              <p className="text-2xl font-black text-slate-900 dark:text-white mt-1">
                {results.total || 50}
              </p>
              <span className="text-[10px] text-emerald-600 font-bold">
                {results.completed || 50} Persisted
              </span>
            </div>

            <div className="bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200 dark:border-slate-800">
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Avg Match</span>
              <p className="text-2xl font-black text-indigo-600 dark:text-indigo-400 mt-1">
                {results.average_match}%
              </p>
              <span className="text-[10px] text-slate-400">Deterministic</span>
            </div>

            <div className="bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200 dark:border-slate-800">
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Avg Evidence</span>
              <p className="text-2xl font-black text-emerald-600 dark:text-emerald-400 mt-1">
                {results.average_evidence}%
              </p>
              <span className="text-[10px] text-slate-400">Claims Verified</span>
            </div>

            <div className="bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200 dark:border-slate-800">
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Hiring Confidence</span>
              <p className="text-2xl font-black text-purple-600 dark:text-purple-400 mt-1">
                {results.average_hiring_confidence}%
              </p>
              <span className="text-[10px] text-slate-400">Risk-Adjusted</span>
            </div>

            <div className="bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200 dark:border-slate-800">
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Ground Truth F1</span>
              <p className="text-2xl font-black text-amber-600 dark:text-amber-400 mt-1">
                {results.f1 !== undefined ? (results.f1 * 100).toFixed(1) + "%" : "N/A"}
              </p>
              <span className="text-[10px] text-slate-400">
                P: {results.precision !== undefined ? (results.precision * 100).toFixed(0) + "%" : "-"} | R: {results.recall !== undefined ? (results.recall * 100).toFixed(0) + "%" : "-"}
              </span>
            </div>

            <div className="bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200 dark:border-slate-800">
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Runtime</span>
              <p className="text-2xl font-black text-slate-700 dark:text-slate-300 mt-1">
                {results.processing_time_seconds}s
              </p>
              <span className="text-[10px] text-slate-400">Total duration</span>
            </div>
          </div>

          {/* Distribution breakdown */}
          <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-4 text-xs font-semibold">
              <span className="text-slate-500 uppercase tracking-wider">Fit Classification:</span>
              <span className="px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800">
                Strong: {results.strong_count || 0}
              </span>
              <span className="px-2.5 py-1 rounded-full bg-blue-50 text-blue-700 dark:bg-blue-950/60 dark:text-blue-400 border border-blue-200 dark:border-blue-800">
                Moderate: {results.moderate_count || 0}
              </span>
              <span className="px-2.5 py-1 rounded-full bg-amber-50 text-amber-700 dark:bg-amber-950/60 dark:text-amber-400 border border-amber-200 dark:border-amber-800">
                Weak: {results.weak_count || 0}
              </span>
              <span className="px-2.5 py-1 rounded-full bg-red-50 text-red-700 dark:bg-red-950/60 dark:text-red-400 border border-red-200 dark:border-red-800">
                Poor: {results.poor_count || 0}
              </span>
              <span className="px-2.5 py-1 rounded-full bg-purple-50 text-purple-700 dark:bg-purple-950/60 dark:text-purple-400 border border-purple-200 dark:border-purple-800">
                High Risk Flags: {results.high_risk_count || 0}
              </span>
            </div>

            {results.job_id && (
              <Link
                href={`/jobs/${results.job_id}`}
                className="text-xs font-bold text-indigo-600 hover:text-indigo-700 flex items-center gap-1"
              >
                Inspect Benchmark Requisition #{results.job_id} <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            )}
          </div>

          {/* Candidate Table */}
          {results.candidates && results.candidates.length > 0 && (
            <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm">
              <div className="p-4 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
                <h3 className="font-bold text-sm text-slate-900 dark:text-white">
                  Benchmark Candidate Dataset ({results.candidates.length} Profiles)
                </h3>
                <span className="text-xs text-slate-400 font-mono">Run: {results.benchmark_run_id}</span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 dark:bg-slate-800/60 text-slate-500 font-bold uppercase tracking-wider border-b border-slate-100 dark:border-slate-800">
                    <tr>
                      <th className="py-3 px-4">#</th>
                      <th className="py-3 px-4">Candidate</th>
                      <th className="py-3 px-4">Expected</th>
                      <th className="py-3 px-4">Actual Fit</th>
                      <th className="py-3 px-4">Match %</th>
                      <th className="py-3 px-4">Evidence %</th>
                      <th className="py-3 px-4">Confidence %</th>
                      <th className="py-3 px-4">Risk</th>
                      <th className="py-3 px-4">Recommendation</th>
                      <th className="py-3 px-4">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                    {results.candidates.map((cand: any, idx: number) => (
                      <tr key={cand.candidate_id || idx} className="hover:bg-slate-50/60 dark:hover:bg-slate-800/40">
                        <td className="py-3 px-4 font-mono text-slate-400">{idx + 1}</td>
                        <td className="py-3 px-4 font-bold text-slate-900 dark:text-white">
                          {cand.name}
                        </td>
                        <td className="py-3 px-4">
                          <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                            {cand.expected_category}
                          </span>
                        </td>
                        <td className="py-3 px-4 font-semibold text-slate-700 dark:text-slate-300">
                          {cand.actual_category}
                        </td>
                        <td className="py-3 px-4 font-mono font-bold text-indigo-600">
                          {cand.match_score}%
                        </td>
                        <td className="py-3 px-4 font-mono text-emerald-600">
                          {cand.evidence_score}%
                        </td>
                        <td className="py-3 px-4 font-mono text-purple-600">
                          {cand.hiring_confidence}%
                        </td>
                        <td className="py-3 px-4">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              cand.risk_level === "High"
                                ? "bg-red-50 text-red-700 dark:bg-red-950/60 dark:text-red-400"
                                : "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-400"
                            }`}
                          >
                            {cand.risk_level}
                          </span>
                        </td>
                        <td className="py-3 px-4 font-semibold text-slate-600 dark:text-slate-300">
                          {cand.recommendation}
                        </td>
                        <td className="py-3 px-4">
                          <Link
                            href={`/candidates/${cand.candidate_id}`}
                            className="text-indigo-600 hover:text-indigo-700 font-bold"
                          >
                            Inspect →
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
