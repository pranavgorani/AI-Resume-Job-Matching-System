"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { 
  BarChart3, 
  TrendingUp, 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle2, 
  FileCheck2,
  Layers,
  Download,
  Filter,
  RefreshCw,
  Sparkles,
  ArrowUpRight,
  Info,
  ChevronDown
} from "lucide-react";
import { getAnalyticsReportData, getReportDownloadUrl, getJobs } from "@/lib/api";

export default function AnalyticsPage() {
  const [data, setData] = useState<any>(null);
  const [jobs, setJobs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [downloadMenuOpen, setDownloadMenuOpen] = useState(false);

  // Active filters
  const [selectedJobId, setSelectedJobId] = useState<string>("");
  const [selectedStatus, setSelectedStatus] = useState<string>("ALL");
  const [selectedRisk, setSelectedRisk] = useState<string>("ALL");
  const [minScore, setMinScore] = useState<number>(0);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);
      const params: Record<string, any> = {};
      if (selectedJobId) params.job_id = selectedJobId;
      if (selectedStatus && selectedStatus !== "ALL") params.status = selectedStatus;
      if (selectedRisk && selectedRisk !== "ALL") params.risk = selectedRisk;
      if (minScore > 0) params.min_score = minScore;

      const [res, jobsList] = await Promise.all([
        getAnalyticsReportData(params),
        getJobs().catch(() => [])
      ]);
      setData(res);
      setJobs(jobsList);
    } catch (err: any) {
      setError(err.message || "Unable to load analytics.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAnalytics();
  }, [selectedJobId, selectedStatus, selectedRisk, minScore]);

  const getExportParams = () => {
    const params: Record<string, any> = {};
    if (selectedJobId) params.job_id = selectedJobId;
    if (selectedStatus && selectedStatus !== "ALL") params.status = selectedStatus;
    if (selectedRisk && selectedRisk !== "ALL") params.risk = selectedRisk;
    if (minScore > 0) params.min_score = minScore;
    return params;
  };

  const handleDownload = (format: "csv" | "pdf" | "docx") => {
    setDownloadMenuOpen(false);
    const url = getReportDownloadUrl(format, getExportParams());
    window.open(url, "_blank");
  };

  const kpis = data?.kpis || {};
  const dists = data?.distributions || {};
  const candidates = data?.candidates || [];
  const insights = data?.ai_insights || [];

  return (
    <div className="space-y-8 pb-12">
      {/* Page Header & Top-Right Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-widest text-indigo-600 dark:text-indigo-400">
              Talent Analytics
            </span>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
              Live Database Verified
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white mt-1">
            Recruitment Analytics
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-0.5">
            Deep insights into candidate quality, skills, evidence, risk, and hiring performance.
          </p>
        </div>

        {/* Top-Right Download Report Dropdown */}
        <div className="relative flex items-center gap-2 self-start md:self-auto">
          <button
            onClick={() => loadAnalytics()}
            title="Refresh Data"
            className="p-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </button>

          <div className="relative">
            <button
              onClick={() => setDownloadMenuOpen(!downloadMenuOpen)}
              className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-700 text-white shadow-md shadow-indigo-600/20 transition-all active:scale-95"
            >
              <Download className="w-4 h-4" />
              <span>DOWNLOAD REPORT</span>
              <ChevronDown className="w-3.5 h-3.5 opacity-80" />
            </button>

            {downloadMenuOpen && (
              <div className="absolute right-0 mt-2 w-52 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-xl z-50 py-1.5 animate-in fade-in zoom-in-95">
                <div className="px-3 py-1.5 border-b border-slate-100 dark:border-slate-800">
                  <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                    Export Filtered View
                  </p>
                </div>
                <button
                  onClick={() => handleDownload("csv")}
                  className="w-full text-left px-3.5 py-2 text-xs font-semibold text-slate-700 dark:text-slate-200 hover:bg-indigo-50 dark:hover:bg-indigo-950/50 hover:text-indigo-600 flex items-center justify-between"
                >
                  <span>Download CSV (.csv)</span>
                  <span className="text-[10px] text-slate-400">Data</span>
                </button>
                <button
                  onClick={() => handleDownload("pdf")}
                  className="w-full text-left px-3.5 py-2 text-xs font-semibold text-slate-700 dark:text-slate-200 hover:bg-indigo-50 dark:hover:bg-indigo-950/50 hover:text-indigo-600 flex items-center justify-between"
                >
                  <span>Download PDF (.pdf)</span>
                  <span className="text-[10px] text-slate-400">12 Sections</span>
                </button>
                <button
                  onClick={() => handleDownload("docx")}
                  className="w-full text-left px-3.5 py-2 text-xs font-semibold text-slate-700 dark:text-slate-200 hover:bg-indigo-50 dark:hover:bg-indigo-950/50 hover:text-indigo-600 flex items-center justify-between"
                >
                  <span>Download DOCX (.docx)</span>
                  <span className="text-[10px] text-slate-400">Word Doc</span>
                </button>
                <div className="border-t border-slate-100 dark:border-slate-800 my-1" />
                <button
                  onClick={() => handleDownload("csv")}
                  className="w-full text-left px-3.5 py-2 text-xs font-bold text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-950/50 flex items-center justify-between"
                >
                  <span>Export Current View</span>
                  <ArrowUpRight className="w-3.5 h-3.5" />
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-1.5 text-xs font-bold text-slate-500">
            <Filter className="w-3.5 h-3.5 text-indigo-600" /> Filters:
          </div>

          {/* Job Filter */}
          <select
            value={selectedJobId}
            onChange={(e) => setSelectedJobId(e.target.value)}
            className="bg-slate-50 dark:bg-slate-800/80 border border-slate-300 dark:border-slate-700 rounded-xl px-3 py-1.5 text-xs font-semibold text-slate-800 dark:text-slate-100 focus:outline-none"
          >
            <option value="">All Requisitions</option>
            {jobs.map((j) => (
              <option key={j.id} value={j.id}>
                {j.title}
              </option>
            ))}
          </select>

          {/* Recommendation Status Filter */}
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="bg-slate-50 dark:bg-slate-800/80 border border-slate-300 dark:border-slate-700 rounded-xl px-3 py-1.5 text-xs font-semibold text-slate-800 dark:text-slate-100 focus:outline-none"
          >
            <option value="ALL">All Recommendations</option>
            <option value="STRONGLY_RECOMMEND">Strongly Recommend</option>
            <option value="RECOMMEND">Recommend</option>
            <option value="CONSIDER">Consider</option>
            <option value="VERIFY">Verification Required</option>
          </select>

          {/* Risk Level Filter */}
          <select
            value={selectedRisk}
            onChange={(e) => setSelectedRisk(e.target.value)}
            className="bg-slate-50 dark:bg-slate-800/80 border border-slate-300 dark:border-slate-700 rounded-xl px-3 py-1.5 text-xs font-semibold text-slate-800 dark:text-slate-100 focus:outline-none"
          >
            <option value="ALL">All Risk Levels</option>
            <option value="NO_RISK">No Risk</option>
            <option value="LOW">Low Risk</option>
            <option value="MEDIUM">Medium Risk</option>
            <option value="HIGH">High Risk</option>
          </select>
        </div>

        {/* Min Score Filter Slider */}
        <div className="flex items-center gap-3 text-xs">
          <span className="font-semibold text-slate-500">Min Match:</span>
          <input
            type="range"
            min="0"
            max="95"
            step="5"
            value={minScore}
            onChange={(e) => setMinScore(Number(e.target.value))}
            className="w-24 accent-indigo-600 cursor-pointer"
          />
          <span className="font-mono font-bold text-indigo-600 dark:text-indigo-400 w-8">
            {minScore}%
          </span>
          {minScore > 0 && (
            <button
              onClick={() => setMinScore(0)}
              className="text-[11px] text-slate-400 hover:text-slate-600 underline"
            >
              Reset
            </button>
          )}
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/60 flex items-center justify-between text-xs text-rose-700 dark:text-rose-300">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-rose-600" />
            <span>{error}</span>
          </div>
          <button
            onClick={loadAnalytics}
            className="px-3 py-1 bg-rose-600 text-white rounded-lg font-bold hover:bg-rose-700 transition-colors"
          >
            Retry
          </button>
        </div>
      )}

      {/* 8 KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
        {[
          { label: "Total Candidates", value: kpis.total_candidates ?? "-", unit: "", color: "text-slate-900 dark:text-white" },
          { label: "Average Match", value: kpis.average_match ?? "-", unit: "%", color: "text-indigo-600 dark:text-indigo-400" },
          { label: "Average Evidence", value: kpis.average_evidence ?? "-", unit: "%", color: "text-emerald-600 dark:text-emerald-400" },
          { label: "Hiring Confidence", value: kpis.average_hiring_confidence ?? "-", unit: "%", color: "text-amber-600 dark:text-amber-400" },
          { label: "Shortlist Rate", value: kpis.shortlist_rate ?? "-", unit: "%", color: "text-violet-600 dark:text-violet-400" },
          { label: "Verification Rate", value: kpis.verification_rate ?? "-", unit: "%", color: "text-rose-600 dark:text-rose-400" },
          { label: "High Risk Flags", value: kpis.high_risk_candidates ?? "-", unit: "", color: "text-red-500" },
          { label: "Avg Experience", value: kpis.average_experience ?? "-", unit: "y", color: "text-cyan-600 dark:text-cyan-400" },
        ].map((kpi, idx) => (
          <div
            key={idx}
            className="p-3.5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between"
          >
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider line-clamp-1">
              {kpi.label}
            </span>
            <div className="mt-2">
              <span className={`text-xl font-extrabold ${kpi.color}`}>
                {kpi.value}{kpi.unit}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* 10 ANALYTICS GRAPHS GRID */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

        {/* GRAPH 1: Candidate Match Score Distribution (Bar Chart) */}
        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
            <div>
              <h3 className="font-extrabold text-sm text-slate-900 dark:text-white">
                1. Match Score Distribution
              </h3>
              <p className="text-[11px] text-slate-500">Binned frequency of overall match scores</p>
            </div>
            <span className="text-xs font-mono font-bold text-indigo-600">Bar Chart</span>
          </div>

          <div className="space-y-2 pt-2">
            {Object.entries(dists.match_distribution || {}).map(([range, count]: [string, any]) => {
              const total = Math.max(1, kpis.total_candidates || 1);
              const pct = Math.round((count / total) * 100);
              return (
                <div key={range} className="space-y-1">
                  <div className="flex justify-between text-xs font-medium">
                    <span className="text-slate-600 dark:text-slate-300">{range}%</span>
                    <span className="font-mono text-slate-400">{count} ({pct}%)</span>
                  </div>
                  <div className="h-2 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-indigo-500 to-indigo-600 rounded-full transition-all duration-500"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* GRAPH 2: Evidence Score Distribution (Bar Chart) */}
        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
            <div>
              <h3 className="font-extrabold text-sm text-slate-900 dark:text-white">
                2. Evidence Score Distribution
              </h3>
              <p className="text-[11px] text-slate-500">Degree of concrete resume proof backing claims</p>
            </div>
            <span className="text-xs font-mono font-bold text-emerald-600">Bar Chart</span>
          </div>

          <div className="space-y-2 pt-2">
            {Object.entries(dists.evidence_distribution || {}).map(([range, count]: [string, any]) => {
              const total = Math.max(1, kpis.total_candidates || 1);
              const pct = Math.round((count / total) * 100);
              return (
                <div key={range} className="space-y-1">
                  <div className="flex justify-between text-xs font-medium">
                    <span className="text-slate-600 dark:text-slate-300">{range}%</span>
                    <span className="font-mono text-slate-400">{count} ({pct}%)</span>
                  </div>
                  <div className="h-2 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-emerald-500 to-teal-500 rounded-full transition-all duration-500"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* GRAPH 3: Match Score vs Evidence Score (Scatter Chart) */}
        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4 md:col-span-2">
          <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
            <div>
              <h3 className="font-extrabold text-sm text-slate-900 dark:text-white">
                3. Evidence Score vs Match Score
              </h3>
              <p className="text-[11px] text-slate-500">
                X-Axis: Evidence Score (0–100%) | Y-Axis: Match Score (0–100%) • Each node represents a candidate
              </p>
            </div>
            <span className="text-xs font-mono font-bold text-violet-600">Scatter Plot</span>
          </div>

          <div className="relative h-64 w-full bg-slate-50 dark:bg-slate-950/60 rounded-xl border border-slate-200 dark:border-slate-800 p-4">
            {/* Grid Lines */}
            <div className="absolute inset-4 grid grid-cols-4 grid-rows-4 pointer-events-none">
              {Array.from({ length: 16 }).map((_, i) => (
                <div key={i} className="border-t border-l border-slate-200/50 dark:border-slate-800/50" />
              ))}
            </div>

            {/* Quadrant annotations */}
            <div className="absolute top-6 right-6 text-[10px] font-bold text-emerald-600 bg-emerald-50 dark:bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-500/20">
              High Match & High Evidence (Hire Priority)
            </div>
            <div className="absolute top-6 left-6 text-[10px] font-bold text-amber-600 bg-amber-50 dark:bg-amber-950/80 px-2 py-0.5 rounded border border-amber-500/20">
              High Match & Low Evidence (Verification Needed)
            </div>

            {/* Candidate Scatter Points */}
            {candidates.map((c: any) => {
              const xPct = Math.max(5, Math.min(95, c.evidence_score));
              const yPct = Math.max(5, Math.min(95, 100 - c.match_score)); // Invert for CSS top
              return (
                <div
                  key={c.candidate_id}
                  className="absolute group"
                  style={{ left: `${xPct}%`, top: `${yPct}%`, transform: "translate(-50%, -50%)" }}
                >
                  <Link
                    href={`/candidates/${c.candidate_id}`}
                    className={`block w-4 h-4 rounded-full ring-2 ring-white dark:ring-slate-900 shadow-md transition-transform group-hover:scale-150 ${
                      c.risk_level === "HIGH"
                        ? "bg-rose-500"
                        : c.recommendation === "STRONGLY_RECOMMEND"
                        ? "bg-emerald-500"
                        : "bg-indigo-600"
                    }`}
                  />
                  {/* Tooltip */}
                  <div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-1.5 hidden group-hover:flex flex-col items-center z-30 pointer-events-none">
                    <div className="bg-slate-900 text-white text-[11px] font-bold px-2 py-1 rounded shadow-lg whitespace-nowrap border border-slate-700">
                      {c.candidate_name}: Match {c.match_score}% | Evidence {c.evidence_score}%
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
          <div className="flex justify-between text-[11px] font-bold text-slate-400 px-2">
            <span>0% Evidence</span>
            <span>50% Evidence</span>
            <span>100% Evidence →</span>
          </div>
        </div>

        {/* GRAPH 4: Top Required Skills (Horizontal Bar Chart) */}
        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
            <div>
              <h3 className="font-extrabold text-sm text-slate-900 dark:text-white">
                4. Top Verified Candidate Skills
              </h3>
              <p className="text-[11px] text-slate-500">Most prevalent technologies evidenced in portfolios</p>
            </div>
            <span className="text-xs font-mono font-bold text-indigo-600">Horizontal Bar</span>
          </div>

          <div className="space-y-2 pt-2">
            {(dists.top_skills || []).slice(0, 7).map((s: any) => {
              const maxCount = Math.max(1, kpis.total_candidates || 1);
              const pct = Math.round((s.count / maxCount) * 100);
              return (
                <div key={s.skill} className="space-y-1">
                  <div className="flex justify-between text-xs font-semibold">
                    <span className="text-slate-800 dark:text-slate-200">{s.skill}</span>
                    <span className="font-mono text-slate-400">{s.count} candidates ({pct}%)</span>
                  </div>
                  <div className="h-2 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-indigo-600 rounded-full"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* GRAPH 5: Candidate Skill Coverage Table */}
        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
            <div>
              <h3 className="font-extrabold text-sm text-slate-900 dark:text-white">
                5. Candidate Skill Coverage
              </h3>
              <p className="text-[11px] text-slate-500">Required vs available skill density</p>
            </div>
            <span className="text-xs font-mono font-bold text-cyan-600">Coverage Matrix</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-200 dark:border-slate-800 text-[10px] font-bold text-slate-400 uppercase">
                  <th className="pb-2">Skill</th>
                  <th className="pb-2 text-center">Required</th>
                  <th className="pb-2 text-center">Available</th>
                  <th className="pb-2 text-right">Coverage %</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {(dists.top_skills || []).slice(0, 6).map((s: any) => {
                  const maxC = Math.max(1, kpis.total_candidates || 1);
                  const cov = Math.round((s.count / maxC) * 100);
                  return (
                    <tr key={s.skill} className="hover:bg-slate-50 dark:hover:bg-slate-800/40">
                      <td className="py-2 font-bold text-slate-800 dark:text-slate-200">{s.skill}</td>
                      <td className="py-2 text-center text-slate-500">{maxC}</td>
                      <td className="py-2 text-center font-bold text-indigo-600">{s.count}</td>
                      <td className="py-2 text-right">
                        <span className={`font-mono font-bold ${cov >= 75 ? "text-emerald-600" : cov >= 50 ? "text-amber-600" : "text-rose-500"}`}>
                          {cov}%
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* GRAPH 6: Risk Distribution (Segment / Donut Chart) */}
        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
            <div>
              <h3 className="font-extrabold text-sm text-slate-900 dark:text-white">
                6. Risk Distribution
              </h3>
              <p className="text-[11px] text-slate-500">Integrity and verification alert severity</p>
            </div>
            <span className="text-xs font-mono font-bold text-amber-600">Distribution</span>
          </div>

          <div className="space-y-3 pt-2">
            {Object.entries(dists.risk_distribution || {}).map(([level, count]: [string, any]) => {
              const total = Math.max(1, kpis.total_candidates || 1);
              const pct = Math.round((count / total) * 100);
              const color = level === "High" ? "bg-rose-500" : level === "Medium" ? "bg-amber-500" : level === "Low" ? "bg-blue-500" : "bg-emerald-500";
              return (
                <div key={level} className="space-y-1">
                  <div className="flex justify-between text-xs font-semibold">
                    <span className="text-slate-700 dark:text-slate-300">{level}</span>
                    <span className="font-mono text-slate-400">{count} ({pct}%)</span>
                  </div>
                  <div className="h-2 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                    <div className={`h-full ${color} rounded-full`} style={{ width: `${pct}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* GRAPH 7: Hiring Funnel */}
        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
            <div>
              <h3 className="font-extrabold text-sm text-slate-900 dark:text-white">
                7. Hiring Pipeline Funnel
              </h3>
              <p className="text-[11px] text-slate-500">Candidate velocity across stages</p>
            </div>
            <span className="text-xs font-mono font-bold text-violet-600">Funnel</span>
          </div>

          <div className="space-y-2 pt-2">
            {(dists.hiring_funnel || []).map((stage: any, i: number) => {
              const maxC = Math.max(1, kpis.total_candidates || 1);
              const pct = Math.round((stage.count / maxC) * 100);
              return (
                <div key={stage.stage} className="p-2 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-800 flex items-center justify-between text-xs">
                  <span className="font-bold text-slate-800 dark:text-slate-200">{stage.stage}</span>
                  <div className="flex items-center gap-3">
                    <div className="w-24 h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                      <div className="h-full bg-violet-600 rounded-full" style={{ width: `${pct}%` }} />
                    </div>
                    <span className="font-mono font-bold text-indigo-600 dark:text-indigo-400 w-8 text-right">
                      {stage.count}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* GRAPH 8: Experience Distribution (Bar Chart) */}
        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
            <div>
              <h3 className="font-extrabold text-sm text-slate-900 dark:text-white">
                8. Experience Distribution
              </h3>
              <p className="text-[11px] text-slate-500">Years of verified professional experience</p>
            </div>
            <span className="text-xs font-mono font-bold text-cyan-600">Binned Exp</span>
          </div>

          <div className="space-y-2 pt-2">
            {Object.entries(dists.experience_distribution || {}).map(([band, count]: [string, any]) => {
              const total = Math.max(1, kpis.total_candidates || 1);
              const pct = Math.round((count / total) * 100);
              return (
                <div key={band} className="space-y-1">
                  <div className="flex justify-between text-xs font-medium">
                    <span className="text-slate-700 dark:text-slate-300">{band}</span>
                    <span className="font-mono text-slate-400">{count} ({pct}%)</span>
                  </div>
                  <div className="h-2 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-cyan-600 rounded-full" style={{ width: `${pct}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* GRAPH 9: Recommendation Distribution */}
        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
            <div>
              <h3 className="font-extrabold text-sm text-slate-900 dark:text-white">
                9. Recommendation Distribution
              </h3>
              <p className="text-[11px] text-slate-500">Recruiter action classification</p>
            </div>
            <span className="text-xs font-mono font-bold text-emerald-600">Decision</span>
          </div>

          <div className="space-y-2 pt-2">
            {Object.entries(dists.recommendation_distribution || {}).map(([rec, count]: [string, any]) => {
              const total = Math.max(1, kpis.total_candidates || 1);
              const pct = Math.round((count / total) * 100);
              return (
                <div key={rec} className="space-y-1">
                  <div className="flex justify-between text-xs font-semibold">
                    <span className="text-slate-700 dark:text-slate-300">{rec}</span>
                    <span className="font-mono text-slate-400">{count} ({pct}%)</span>
                  </div>
                  <div className="h-2 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-emerald-600 rounded-full" style={{ width: `${pct}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* GRAPH 10: Current Fit vs Potential Fit */}
        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4 md:col-span-2">
          <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
            <div>
              <h3 className="font-extrabold text-sm text-slate-900 dark:text-white">
                10. Current Fit vs Potential Fit
              </h3>
              <p className="text-[11px] text-slate-500">
                Demonstrated capability vs learning acceleration powered by transferable skills
              </p>
            </div>
            <span className="text-xs font-mono font-bold text-indigo-600">Comparative</span>
          </div>

          <div className="space-y-3 pt-2">
            {candidates.slice(0, 8).map((c: any) => (
              <div key={c.candidate_id} className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="font-bold text-slate-800 dark:text-slate-200">{c.candidate_name}</span>
                  <div className="space-x-3 text-[11px] font-mono">
                    <span className="text-indigo-600 font-bold">Current: {c.current_fit}%</span>
                    <span className="text-emerald-600 font-bold">Potential: {c.potential_fit}%</span>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div className="h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${c.current_fit}%` }} />
                  </div>
                  <div className="h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${c.potential_fit}%` }} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* SECTION 15: AI RECRUITMENT INSIGHTS (Derived from real DB data) */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-indigo-500/10 via-violet-500/10 to-emerald-500/10 border border-indigo-500/20 shadow-sm space-y-4">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
          <h2 className="font-extrabold text-base text-slate-900 dark:text-white">
            AI Recruitment Intelligence Insights
          </h2>
          <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-indigo-600 text-white ml-2">
            Grounded in Real Data
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {insights.map((insight: string, idx: number) => (
            <div
              key={idx}
              className="p-3.5 rounded-xl bg-white/80 dark:bg-slate-900/80 border border-slate-200/80 dark:border-slate-800 text-xs text-slate-800 dark:text-slate-200 flex items-start gap-2.5"
            >
              <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
              <p className="font-medium leading-relaxed">{insight}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
