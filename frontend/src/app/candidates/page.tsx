"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { 
  Users, 
  Search, 
  AlertTriangle, 
  CheckCircle2, 
  ArrowRight, 
  PlayCircle, 
  Filter, 
  Layers, 
  ShieldCheck, 
  XCircle,
  Eye,
  Check,
  RefreshCw,
  Clock,
  Sparkles
} from "lucide-react";
import { getCandidates, seedDemoData, getJobs } from "@/lib/api";
import { CandidateTableRow } from "@/lib/types";

export default function CandidatesPoolPage() {
  const router = useRouter();
  const [candidates, setCandidates] = useState<CandidateTableRow[]>([]);
  const [jobs, setJobs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);

  // Filters
  const [search, setSearch] = useState("");
  const [selectedJob, setSelectedJob] = useState<string>("ALL");
  const [matchScoreFilter, setMatchScoreFilter] = useState<number>(0);
  const [evidenceScoreFilter, setEvidenceScoreFilter] = useState<number>(0);
  const [experienceFilter, setExperienceFilter] = useState<string>("ALL");
  const [riskFilter, setRiskFilter] = useState<string>("ALL");
  const [recFilter, setRecFilter] = useState<string>("ALL");
  const [hiringConfFilter, setHiringConfFilter] = useState<number>(0);

  // Selection for comparison
  const [selectedIds, setSelectedIds] = useState<number[]>([]);

  // Local candidate statuses (Shortlist, Reject, Verify)
  const [statusOverrides, setStatusOverrides] = useState<Record<number, string>>({});

  const load = async () => {
    try {
      setLoading(true);
      const [candList, jobList] = await Promise.all([
        getCandidates({ job_id: selectedJob !== "ALL" ? selectedJob : undefined }),
        getJobs().catch(() => [])
      ]);
      setCandidates(candList);
      setJobs(jobList);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [selectedJob]);

  const handleSeed = async () => {
    setSeeding(true);
    try {
      await seedDemoData();
      await load();
    } catch (e: any) {
      alert(e.message);
    } finally {
      setSeeding(false);
    }
  };

  const handleToggleSelect = (id: number) => {
    if (selectedIds.includes(id)) {
      setSelectedIds(selectedIds.filter((item) => item !== id));
    } else {
      if (selectedIds.length >= 5) {
        alert("You can select up to 5 candidates for side-by-side comparison.");
        return;
      }
      setSelectedIds([...selectedIds, id]);
    }
  };

  const handleSetStatus = (id: number, status: string) => {
    setStatusOverrides(prev => ({
      ...prev,
      [id]: prev[id] === status ? "" : status
    }));
  };

  const handleCompareSelected = () => {
    if (selectedIds.length < 2) {
      alert("Please select at least 2 candidates to compare.");
      return;
    }
    const jId = selectedJob !== "ALL" ? selectedJob : (jobs[0]?.id || 1);
    router.push(`/compare?job_id=${jId}&ids=${selectedIds.join(",")}`);
  };

  // Multi-dimensional filtering
  const filtered = candidates.filter((c) => {
    if (search && !c.name.toLowerCase().includes(search.toLowerCase()) && !c.email?.toLowerCase().includes(search.toLowerCase())) {
      return false;
    }
    if (matchScoreFilter > 0 && c.match_score < matchScoreFilter) {
      return false;
    }
    if (evidenceScoreFilter > 0 && c.evidence_score < evidenceScoreFilter) {
      return false;
    }
    if (hiringConfFilter > 0 && c.hiring_confidence < hiringConfFilter) {
      return false;
    }
    if (recFilter !== "ALL" && c.recommendation !== recFilter) {
      return false;
    }
    if (riskFilter === "ZERO_RISK" && c.risk_flags_count > 0) {
      return false;
    }
    if (riskFilter === "HAS_RISKS" && c.risk_flags_count === 0) {
      return false;
    }
    if (experienceFilter !== "ALL") {
      const minExp = parseFloat(experienceFilter);
      if (c.experience_years < minExp) return false;
    }
    return true;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-indigo-600 uppercase tracking-widest">
              Talent Pool
            </span>
            <span className="text-[10px] font-semibold bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 px-2 py-0.5 rounded-full border border-indigo-200 dark:border-indigo-800">
              {candidates.length} Indexed Dossiers
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white mt-1">
            Candidate Intelligence
          </h1>
          <p className="text-xs text-slate-500">
            Ranked candidate dossiers, verified evidence coverage, risk indicators, and hiring recommendations
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleSeed}
            disabled={seeding}
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800 hover:bg-indigo-100 transition-colors"
          >
            <PlayCircle className="w-4 h-4" />
            {seeding ? "Seeding..." : "Load 8 Demo Candidates"}
          </button>
        </div>
      </div>

      {/* Multi-Filter Bar */}
      <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
            <Filter className="w-3.5 h-3.5 text-indigo-600" /> Multi-Dimensional Filters
          </div>
          <button
            onClick={() => {
              setSearch("");
              setSelectedJob("ALL");
              setMatchScoreFilter(0);
              setEvidenceScoreFilter(0);
              setExperienceFilter("ALL");
              setRiskFilter("ALL");
              setRecFilter("ALL");
              setHiringConfFilter(0);
            }}
            className="text-[11px] font-semibold text-indigo-600 hover:underline"
          >
            Reset Filters
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-2.5">
          {/* 1. Search */}
          <div className="lg:col-span-2 relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search candidate..."
              className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>

          {/* 2. Job */}
          <div>
            <select
              value={selectedJob}
              onChange={(e) => setSelectedJob(e.target.value)}
              className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg px-2.5 py-1.5 text-xs font-medium text-slate-700 dark:text-slate-200 focus:outline-none"
            >
              <option value="ALL">All Jobs</option>
              {jobs.map((j) => (
                <option key={j.id} value={j.id}>
                  {j.title}
                </option>
              ))}
            </select>
          </div>

          {/* 3. Match Score */}
          <div>
            <select
              value={matchScoreFilter}
              onChange={(e) => setMatchScoreFilter(Number(e.target.value))}
              className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg px-2.5 py-1.5 text-xs font-medium text-slate-700 dark:text-slate-200 focus:outline-none"
            >
              <option value={0}>Match: Any</option>
              <option value={90}>Match ≥ 90%</option>
              <option value={80}>Match ≥ 80%</option>
              <option value={70}>Match ≥ 70%</option>
              <option value={60}>Match ≥ 60%</option>
            </select>
          </div>

          {/* 4. Evidence Score */}
          <div>
            <select
              value={evidenceScoreFilter}
              onChange={(e) => setEvidenceScoreFilter(Number(e.target.value))}
              className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg px-2.5 py-1.5 text-xs font-medium text-slate-700 dark:text-slate-200 focus:outline-none"
            >
              <option value={0}>Evidence: Any</option>
              <option value={85}>Evidence ≥ 85%</option>
              <option value={75}>Evidence ≥ 75%</option>
              <option value={65}>Evidence ≥ 65%</option>
            </select>
          </div>

          {/* 5. Experience */}
          <div>
            <select
              value={experienceFilter}
              onChange={(e) => setExperienceFilter(e.target.value)}
              className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg px-2.5 py-1.5 text-xs font-medium text-slate-700 dark:text-slate-200 focus:outline-none"
            >
              <option value="ALL">Exp: Any</option>
              <option value="1">1+ yrs</option>
              <option value="3">3+ yrs</option>
              <option value="5">5+ yrs</option>
              <option value="8">8+ yrs</option>
            </select>
          </div>

          {/* 6. Risk */}
          <div>
            <select
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value)}
              className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg px-2.5 py-1.5 text-xs font-medium text-slate-700 dark:text-slate-200 focus:outline-none"
            >
              <option value="ALL">Risk: All</option>
              <option value="ZERO_RISK">0 Flags Only</option>
              <option value="HAS_RISKS">Has Flags</option>
            </select>
          </div>

          {/* 7. Recommendation */}
          <div>
            <select
              value={recFilter}
              onChange={(e) => setRecFilter(e.target.value)}
              className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg px-2.5 py-1.5 text-xs font-medium text-slate-700 dark:text-slate-200 focus:outline-none"
            >
              <option value="ALL">Rec: All</option>
              <option value="STRONGLY_RECOMMEND">Strongly Rec.</option>
              <option value="RECOMMEND">Recommend</option>
              <option value="CONSIDER">Consider</option>
              <option value="VERIFY">Verification</option>
            </select>
          </div>
        </div>
      </div>

      {/* Floating Compare Action Bar */}
      {selectedIds.length > 0 && (
        <div className="p-3.5 rounded-xl bg-indigo-600 text-white flex items-center justify-between shadow-lg shadow-indigo-600/30 animate-in fade-in">
          <div className="flex items-center gap-2 text-xs font-semibold">
            <Layers className="w-4 h-4" />
            <span>{selectedIds.length} candidates selected for side-by-side comparison</span>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSelectedIds([])}
              className="text-xs text-indigo-200 hover:text-white underline"
            >
              Clear
            </button>
            <button
              onClick={handleCompareSelected}
              className="px-4 py-1.5 rounded-lg bg-white text-indigo-700 text-xs font-bold shadow hover:bg-indigo-50 transition-colors"
            >
              Compare Selected →
            </button>
          </div>
        </div>
      )}

      {/* Candidate Intelligence Table */}
      {loading ? (
        <div className="p-12 text-center text-xs text-slate-400 space-y-3">
          <RefreshCw className="w-6 h-6 animate-spin text-indigo-600 mx-auto" />
          <p>Assembling candidate intelligence...</p>
        </div>
      ) : filtered.length === 0 ? (
        <div className="p-12 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-center space-y-3">
          <Users className="w-10 h-10 text-slate-300 dark:text-slate-700 mx-auto" />
          <p className="text-sm font-semibold text-slate-600 dark:text-slate-400">No candidates match your filters.</p>
          <button
            onClick={() => {
              setSearch("");
              setMatchScoreFilter(0);
              setRecFilter("ALL");
            }}
            className="text-xs px-4 py-2 rounded-lg bg-indigo-600 text-white font-semibold shadow"
          >
            Clear Filters
          </button>
        </div>
      ) : (
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 dark:bg-slate-800/60 border-b border-slate-200 dark:border-slate-800 text-slate-500 uppercase tracking-wider font-semibold">
                <tr>
                  <th className="py-3.5 px-3 w-8">
                    <span className="sr-only">Select</span>
                  </th>
                  <th className="py-3.5 px-3">Rank</th>
                  <th className="py-3.5 px-4">Candidate</th>
                  <th className="py-3.5 px-3 text-center">Match</th>
                  <th className="py-3.5 px-3 text-center">Evidence</th>
                  <th className="py-3.5 px-3 text-center">Hiring Confidence</th>
                  <th className="py-3.5 px-3 text-center">Coverage</th>
                  <th className="py-3.5 px-3 text-center">Experience</th>
                  <th className="py-3.5 px-3 text-center">Risk</th>
                  <th className="py-3.5 px-3 text-center">Potential</th>
                  <th className="py-3.5 px-3 text-center">Recommendation</th>
                  <th className="py-3.5 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {filtered.map((cand) => {
                  const override = statusOverrides[cand.candidate_id];
                  const isSelected = selectedIds.includes(cand.candidate_id);

                  return (
                    <tr
                      key={cand.candidate_id}
                      className={`hover:bg-slate-50/80 dark:hover:bg-slate-800/50 transition-colors ${
                        isSelected ? "bg-indigo-50/40 dark:bg-indigo-950/20" : ""
                      }`}
                    >
                      {/* Checkbox */}
                      <td className="py-3.5 px-3">
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={() => handleToggleSelect(cand.candidate_id)}
                          className="rounded text-indigo-600 cursor-pointer"
                        />
                      </td>

                      {/* Rank */}
                      <td className="py-3.5 px-3 font-black text-slate-600 dark:text-slate-400">
                        #{cand.rank}
                      </td>

                      {/* Candidate */}
                      <td className="py-3.5 px-4">
                        <Link
                          href={`/candidates/${cand.candidate_id}`}
                          className="font-bold text-slate-900 dark:text-white hover:text-indigo-600 hover:underline block text-sm"
                        >
                          {cand.name}
                        </Link>
                        <span className="text-[11px] text-slate-400 block">{cand.email}</span>
                        {override && (
                          <span className={`inline-block mt-0.5 text-[9px] font-bold px-1.5 py-0.2 rounded uppercase ${
                            override === "SHORTLISTED"
                              ? "bg-emerald-100 text-emerald-800"
                              : override === "REJECTED"
                              ? "bg-rose-100 text-rose-800"
                              : "bg-amber-100 text-amber-800"
                          }`}>
                            Status: {override}
                          </span>
                        )}
                      </td>

                      {/* Match Score */}
                      <td className="py-3.5 px-3 text-center font-extrabold text-sm text-indigo-600 dark:text-indigo-400">
                        {cand.match_score}%
                      </td>

                      {/* Evidence */}
                      <td className="py-3.5 px-3 text-center font-bold text-emerald-600">
                        {cand.evidence_score}%
                      </td>

                      {/* Hiring Confidence */}
                      <td className="py-3.5 px-3 text-center font-bold text-amber-600">
                        {cand.hiring_confidence}%
                      </td>

                      {/* Coverage */}
                      <td className="py-3.5 px-3 text-center font-mono font-medium text-slate-600 dark:text-slate-300">
                        {cand.required_skills_coverage}
                      </td>

                      {/* Experience */}
                      <td className="py-3.5 px-3 text-center text-slate-600 dark:text-slate-400">
                        {cand.experience_years} yrs
                      </td>

                      {/* Risk */}
                      <td className="py-3.5 px-3 text-center">
                        {cand.risk_flags_count > 0 ? (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-semibold bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800">
                            <AlertTriangle className="w-3 h-3 text-amber-600" />
                            {cand.risk_flags_count} flag{cand.risk_flags_count > 1 ? "s" : ""}
                          </span>
                        ) : (
                          <span className="text-emerald-600 font-medium inline-flex items-center gap-1">
                            <CheckCircle2 className="w-3 h-3" /> 0 flags
                          </span>
                        )}
                      </td>

                      {/* Potential */}
                      <td className="py-3.5 px-3 text-center font-bold text-indigo-600">
                        {cand.potential_score}%
                      </td>

                      {/* Recommendation */}
                      <td className="py-3.5 px-3 text-center">
                        <span
                          className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase ${
                            cand.recommendation === "STRONGLY_RECOMMEND"
                              ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300"
                              : cand.recommendation === "RECOMMEND"
                              ? "bg-indigo-100 text-indigo-800 dark:bg-indigo-900/40 dark:text-indigo-300"
                              : cand.recommendation === "VERIFY"
                              ? "bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300"
                              : "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-400"
                          }`}
                        >
                          {cand.recommendation.replace("_", " ")}
                        </span>
                      </td>

                      {/* Actions: Inspect, Compare, Shortlist, Reject, Verify */}
                      <td className="py-3.5 px-4 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          {/* Inspect */}
                          <Link
                            href={`/candidates/${cand.candidate_id}`}
                            className="px-2 py-1 rounded text-[11px] font-semibold bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-300 hover:bg-indigo-100"
                            title="Inspect Candidate Dossier"
                          >
                            Inspect
                          </Link>

                          {/* Compare */}
                          <button
                            onClick={() => handleToggleSelect(cand.candidate_id)}
                            className={`px-2 py-1 rounded text-[11px] font-semibold transition-colors ${
                              isSelected
                                ? "bg-indigo-600 text-white"
                                : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200"
                            }`}
                            title="Select for comparison"
                          >
                            Compare
                          </button>

                          {/* Shortlist */}
                          <button
                            onClick={() => handleSetStatus(cand.candidate_id, "SHORTLISTED")}
                            className={`px-2 py-1 rounded text-[11px] font-semibold transition-colors ${
                              override === "SHORTLISTED"
                                ? "bg-emerald-600 text-white"
                                : "bg-emerald-50 dark:bg-emerald-950/30 text-emerald-700 dark:text-emerald-300 hover:bg-emerald-100"
                            }`}
                            title="Shortlist candidate"
                          >
                            Shortlist
                          </button>

                          {/* Reject */}
                          <button
                            onClick={() => handleSetStatus(cand.candidate_id, "REJECTED")}
                            className={`px-2 py-1 rounded text-[11px] font-semibold transition-colors ${
                              override === "REJECTED"
                                ? "bg-rose-600 text-white"
                                : "bg-rose-50 dark:bg-rose-950/30 text-rose-700 dark:text-rose-300 hover:bg-rose-100"
                            }`}
                            title="Reject candidate"
                          >
                            Reject
                          </button>

                          {/* Verify */}
                          <button
                            onClick={() => handleSetStatus(cand.candidate_id, "VERIFY")}
                            className={`px-2 py-1 rounded text-[11px] font-semibold transition-colors ${
                              override === "VERIFY"
                                ? "bg-amber-600 text-white"
                                : "bg-amber-50 dark:bg-amber-950/30 text-amber-700 dark:text-amber-300 hover:bg-amber-100"
                            }`}
                            title="Mark for verification"
                          >
                            Verify
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
