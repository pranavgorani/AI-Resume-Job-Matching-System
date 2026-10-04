"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { 
  Briefcase, 
  Users, 
  CheckCircle2, 
  AlertTriangle, 
  Award, 
  TrendingUp, 
  ArrowRight, 
  Plus, 
  PlayCircle,
  FileCheck2,
  Sparkles,
  Layers,
  ShieldCheck,
  RefreshCw
} from "lucide-react";
import { getJobs, getAnalyticsReportData, seedDemoData } from "@/lib/api";

export default function DashboardPage() {
  const router = useRouter();
  const [data, setData] = useState<any>(null);
  const [jobs, setJobs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);
      const [analyticsData, jobsData] = await Promise.all([
        getAnalyticsReportData(),
        getJobs().catch(() => [])
      ]);
      setData(analyticsData);
      setJobs(jobsData);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSeed = async () => {
    setSeeding(true);
    try {
      const res = await seedDemoData();
      await loadData();
      router.push(`/jobs/${res.job_id}`);
    } catch (e: any) {
      alert(`Seed failed: ${e.message}`);
    } finally {
      setSeeding(false);
    }
  };

  const kpis = data?.kpis || {};
  const dists = data?.distributions || {};
  const candidates = data?.candidates || [];

  // Top KPI calculations from real data
  const activeJobsCount = jobs.length;
  const totalCandidatesCount = kpis.total_candidates || 0;
  const shortlistedCount = candidates.filter((c: any) => 
    c.recommendation === "STRONGLY_RECOMMEND" || c.recommendation === "RECOMMEND"
  ).length;
  const highMatchesCount = candidates.filter((c: any) => c.match_score >= 85).length;
  const verificationRequiredCount = candidates.filter((c: any) => 
    c.verification_status === "REQUIRED" || c.recommendation === "VERIFY"
  ).length;
  const avgMatchScore = kpis.average_match || 0;

  return (
    <div className="space-y-8 pb-12">
      {/* Dashboard Title & Subtitle */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-widest text-indigo-600 dark:text-indigo-400">
              TalentProof Intelligence
            </span>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
              Live Database Connected
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white mt-1">
            Recruiter Intelligence Dashboard
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-0.5">
            Real-time evidence verification, candidate match ranking, and risk intelligence
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={loadData}
            title="Refresh Dashboard"
            className="p-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </button>

          <button
            onClick={handleSeed}
            disabled={seeding}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-bold bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800 hover:bg-indigo-100 transition-all shadow-sm"
          >
            <PlayCircle className={`w-4 h-4 ${seeding ? "animate-spin" : ""}`} />
            <span>{seeding ? "Loading..." : "Load Demo Candidates"}</span>
          </button>

          <Link
            href="/jobs/new"
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-700 text-white shadow-md shadow-indigo-600/20 transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>New Job</span>
          </Link>
        </div>
      </div>

      {/* TOP 6 KPI CARDS */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5">
        {[
          { label: "Active Jobs", value: activeJobsCount, icon: Briefcase, color: "text-indigo-600 dark:text-indigo-400", bg: "bg-indigo-500/10" },
          { label: "Total Candidates", value: totalCandidatesCount, icon: Users, color: "text-slate-900 dark:text-white", bg: "bg-slate-500/10" },
          { label: "Shortlisted", value: shortlistedCount, icon: CheckCircle2, color: "text-emerald-600 dark:text-emerald-400", bg: "bg-emerald-500/10" },
          { label: "High Matches (≥85%)", value: highMatchesCount, icon: Award, color: "text-violet-600 dark:text-violet-400", bg: "bg-violet-500/10" },
          { label: "Verification Required", value: verificationRequiredCount, icon: AlertTriangle, color: "text-amber-600 dark:text-amber-400", bg: "bg-amber-500/10" },
          { label: "Average Match Score", value: `${avgMatchScore}%`, icon: TrendingUp, color: "text-cyan-600 dark:text-cyan-400", bg: "bg-cyan-500/10" },
        ].map((kpi, idx) => {
          const Icon = kpi.icon;
          return (
            <div
              key={idx}
              className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between space-y-2 hover:border-slate-300 dark:hover:border-slate-700 transition-colors"
            >
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 line-clamp-1">
                  {kpi.label}
                </span>
                <div className={`p-1.5 rounded-lg ${kpi.bg}`}>
                  <Icon className={`w-3.5 h-3.5 ${kpi.color}`} />
                </div>
              </div>
              <div className="mt-1">
                <span className={`text-2xl font-black ${kpi.color}`}>
                  {kpi.value}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* DASHBOARD GRAPHS SECTION (6 PROFESSIONAL CHARTS) */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-extrabold text-slate-900 dark:text-white flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-indigo-600" />
            Recruiter Analytics & Distributions
          </h2>
          <Link
            href="/analytics"
            className="text-xs font-bold text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1"
          >
            <span>View Deep Analytics</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

          {/* GRAPH 1: Candidate Match Score Distribution (Bar Chart) */}
          <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
              <h3 className="font-bold text-xs text-slate-900 dark:text-white">
                Match Score Distribution
              </h3>
              <span className="text-[10px] font-mono text-indigo-600 font-bold">Bar Chart</span>
            </div>
            <div className="space-y-2 pt-1">
              {Object.entries(dists.match_distribution || {}).map(([range, count]: [string, any]) => {
                const total = Math.max(1, totalCandidatesCount || 1);
                const pct = Math.round((count / total) * 100);
                return (
                  <div key={range} className="space-y-1">
                    <div className="flex justify-between text-[11px]">
                      <span className="font-medium text-slate-600 dark:text-slate-300">{range}%</span>
                      <span className="font-mono text-slate-400">{count} ({pct}%)</span>
                    </div>
                    <div className="h-1.5 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-indigo-600 rounded-full" style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* GRAPH 2: Evidence Score vs Match Score (Scatter Chart) */}
          <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
              <h3 className="font-bold text-xs text-slate-900 dark:text-white">
                Evidence vs Match Score
              </h3>
              <span className="text-[10px] font-mono text-violet-600 font-bold">Scatter Plot</span>
            </div>
            <div className="relative h-44 w-full bg-slate-50 dark:bg-slate-950/60 rounded-xl border border-slate-200 dark:border-slate-800 p-3">
              <div className="absolute inset-3 grid grid-cols-2 grid-rows-2 pointer-events-none border border-slate-200/50 dark:border-slate-800/50">
                <div className="border-r border-b border-slate-200/50 dark:border-slate-800/50" />
                <div className="border-b border-slate-200/50 dark:border-slate-800/50" />
                <div className="border-r border-slate-200/50 dark:border-slate-800/50" />
                <div />
              </div>
              {candidates.map((c: any) => {
                const xPct = Math.max(5, Math.min(95, c.evidence_score));
                const yPct = Math.max(5, Math.min(95, 100 - c.match_score));
                return (
                  <Link
                    key={c.candidate_id}
                    href={`/candidates/${c.candidate_id}`}
                    title={`${c.candidate_name}: Match ${c.match_score}%, Evidence ${c.evidence_score}%`}
                    style={{ left: `${xPct}%`, top: `${yPct}%`, transform: "translate(-50%, -50%)" }}
                    className={`absolute w-3.5 h-3.5 rounded-full ring-2 ring-white dark:ring-slate-900 transition-transform hover:scale-150 ${
                      c.risk_level === "HIGH" ? "bg-rose-500" : c.recommendation === "STRONGLY_RECOMMEND" ? "bg-emerald-500" : "bg-indigo-600"
                    }`}
                  />
                );
              })}
            </div>
            <div className="flex justify-between text-[10px] font-mono text-slate-400">
              <span>0% Ev.</span>
              <span>100% Ev. →</span>
            </div>
          </div>

          {/* GRAPH 3: Top Candidate Skills (Horizontal Bar Chart) */}
          <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
              <h3 className="font-bold text-xs text-slate-900 dark:text-white">
                Top Candidate Skills
              </h3>
              <span className="text-[10px] font-mono text-emerald-600 font-bold">Dynamic</span>
            </div>
            <div className="space-y-2 pt-1">
              {(dists.top_skills || []).slice(0, 5).map((s: any) => {
                const maxCount = Math.max(1, totalCandidatesCount || 1);
                const pct = Math.round((s.count / maxCount) * 100);
                return (
                  <div key={s.skill} className="space-y-1">
                    <div className="flex justify-between text-[11px] font-semibold">
                      <span className="text-slate-800 dark:text-slate-200 truncate">{s.skill}</span>
                      <span className="font-mono text-slate-400">{s.count} ({pct}%)</span>
                    </div>
                    <div className="h-1.5 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* GRAPH 4: Hiring Pipeline (Funnel) */}
          <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
              <h3 className="font-bold text-xs text-slate-900 dark:text-white">
                Hiring Pipeline Funnel
              </h3>
              <span className="text-[10px] font-mono text-violet-600 font-bold">Pipeline</span>
            </div>
            <div className="space-y-1.5 pt-1">
              {(dists.hiring_funnel || []).map((stage: any) => {
                const maxC = Math.max(1, totalCandidatesCount || 1);
                const pct = Math.round((stage.count / maxC) * 100);
                return (
                  <div key={stage.stage} className="p-1.5 rounded-lg bg-slate-50 dark:bg-slate-800/40 border border-slate-200/50 dark:border-slate-800 flex items-center justify-between text-[11px]">
                    <span className="font-medium text-slate-700 dark:text-slate-200">{stage.stage}</span>
                    <span className="font-mono font-bold text-indigo-600 dark:text-indigo-400">{stage.count}</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* GRAPH 5: Risk Distribution */}
          <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
              <h3 className="font-bold text-xs text-slate-900 dark:text-white">
                Risk Distribution
              </h3>
              <span className="text-[10px] font-mono text-amber-600 font-bold">Integrity</span>
            </div>
            <div className="space-y-2 pt-1">
              {Object.entries(dists.risk_distribution || {}).map(([level, count]: [string, any]) => {
                const total = Math.max(1, totalCandidatesCount || 1);
                const pct = Math.round((count / total) * 100);
                const color = level === "High" ? "bg-rose-500" : level === "Medium" ? "bg-amber-500" : level === "Low" ? "bg-blue-500" : "bg-emerald-500";
                return (
                  <div key={level} className="space-y-1">
                    <div className="flex justify-between text-[11px] font-semibold">
                      <span className="text-slate-700 dark:text-slate-300">{level}</span>
                      <span className="font-mono text-slate-400">{count} ({pct}%)</span>
                    </div>
                    <div className="h-1.5 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                      <div className={`h-full ${color} rounded-full`} style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* GRAPH 6: Recommendation Distribution */}
          <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
              <h3 className="font-bold text-xs text-slate-900 dark:text-white">
                Recommendation Distribution
              </h3>
              <span className="text-[10px] font-mono text-emerald-600 font-bold">Decisions</span>
            </div>
            <div className="space-y-2 pt-1">
              {Object.entries(dists.recommendation_distribution || {}).map(([rec, count]: [string, any]) => {
                const total = Math.max(1, totalCandidatesCount || 1);
                const pct = Math.round((count / total) * 100);
                return (
                  <div key={rec} className="space-y-1">
                    <div className="flex justify-between text-[11px] font-semibold">
                      <span className="text-slate-700 dark:text-slate-300">{rec}</span>
                      <span className="font-mono text-slate-400">{count} ({pct}%)</span>
                    </div>
                    <div className="h-1.5 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-emerald-600 rounded-full" style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* RECENT JOBS TABLE */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
          <div>
            <h2 className="font-extrabold text-sm text-slate-900 dark:text-white flex items-center gap-2">
              <Briefcase className="w-4 h-4 text-indigo-600" /> Active Job Requisitions
            </h2>
            <p className="text-xs text-slate-500">Target roles with verified candidate matches</p>
          </div>
          <Link
            href="/jobs"
            className="text-xs font-bold text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1"
          >
            <span>View All Jobs</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-100 dark:border-slate-800 text-[10px] font-bold text-slate-400 uppercase">
                <th className="py-2.5 px-3">Role Title</th>
                <th className="py-2.5 px-3">Seniority</th>
                <th className="py-2.5 px-3">Location</th>
                <th className="py-2.5 px-3">Min Exp</th>
                <th className="py-2.5 px-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {jobs.map((job) => (
                <tr key={job.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/40">
                  <td className="py-3 px-3">
                    <Link
                      href={`/jobs/${job.id}`}
                      className="font-bold text-slate-900 dark:text-white hover:text-indigo-600"
                    >
                      {job.title}
                    </Link>
                  </td>
                  <td className="py-3 px-3 font-semibold text-slate-600 dark:text-slate-300">
                    {job.seniority}
                  </td>
                  <td className="py-3 px-3 text-slate-500">{job.location}</td>
                  <td className="py-3 px-3 text-slate-500">{job.min_years_experience} yrs</td>
                  <td className="py-3 px-3 text-right">
                    <Link
                      href={`/jobs/${job.id}`}
                      className="px-3 py-1 rounded-lg text-xs font-bold bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-300 hover:bg-indigo-100 transition-colors"
                    >
                      View Requisition →
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
