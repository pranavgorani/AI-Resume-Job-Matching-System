"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { 
  Briefcase, 
  Plus, 
  PlayCircle, 
  Clock, 
  MapPin, 
  Users, 
  MoreVertical, 
  Copy, 
  Archive, 
  Trash2, 
  ExternalLink, 
  Search, 
  Filter,
  CheckCircle2,
  TrendingUp,
  Building,
  RefreshCw,
  Edit3
} from "lucide-react";
import { getJobs, seedDemoData, duplicateJob, archiveJob, deleteJob } from "@/lib/api";
import { Job } from "@/lib/types";

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [actionMenuOpen, setActionMenuOpen] = useState<number | null>(null);

  const load = async () => {
    try {
      setLoading(true);
      const res = await getJobs();
      setJobs(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

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

  const handleDuplicate = async (id: number) => {
    try {
      await duplicateJob(id);
      setActionMenuOpen(null);
      await load();
    } catch (e: any) {
      alert(`Duplicate failed: ${e.message}`);
    }
  };

  const handleArchive = async (id: number) => {
    try {
      await archiveJob(id);
      setActionMenuOpen(null);
      await load();
    } catch (e: any) {
      alert(`Archive toggle failed: ${e.message}`);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this job requisition? This will remove all associated matches.")) return;
    try {
      await deleteJob(id);
      setActionMenuOpen(null);
      await load();
    } catch (e: any) {
      alert(`Delete failed: ${e.message}`);
    }
  };

  const filteredJobs = jobs.filter((job) => {
    if (search && !job.title.toLowerCase().includes(search.toLowerCase()) && !job.location.toLowerCase().includes(search.toLowerCase())) {
      return false;
    }
    if (statusFilter !== "ALL" && job.status.toLowerCase() !== statusFilter.toLowerCase()) {
      return false;
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
              Requisition Pool
            </span>
            <span className="text-[10px] font-semibold bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 px-2 py-0.5 rounded-full border border-indigo-200 dark:border-indigo-800">
              {jobs.length} Active Positions
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white mt-1">
            Job Requisitions
          </h1>
          <p className="text-xs text-slate-500">
            Manage target roles, evidence scoring criteria, requirement weights, and candidate pipelines
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleSeed}
            disabled={seeding}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800 hover:bg-indigo-100 transition-colors"
          >
            <PlayCircle className="w-4 h-4" />
            {seeding ? "Seeding..." : "Load Demo Job"}
          </button>
          <Link
            href="/jobs/new"
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-indigo-600 text-white shadow-md shadow-indigo-600/20 hover:bg-indigo-700 transition-colors"
          >
            <Plus className="w-4 h-4" /> Create New Job
          </Link>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3 flex-1 max-w-md">
          <div className="relative w-full">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search job title, location, or tech..."
              className="w-full bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg px-3 py-1.5 text-xs font-semibold text-slate-700 dark:text-slate-200"
          >
            <option value="ALL">All Status</option>
            <option value="ACTIVE">Active</option>
            <option value="ARCHIVED">Archived</option>
          </select>
        </div>

        <div className="text-xs text-slate-500">
          Showing <span className="font-semibold text-slate-700 dark:text-slate-300">{filteredJobs.length}</span> of {jobs.length} jobs
        </div>
      </div>

      {/* Main Jobs Table */}
      {loading ? (
        <div className="p-12 text-center text-xs text-slate-400 space-y-3">
          <RefreshCw className="w-6 h-6 animate-spin text-indigo-600 mx-auto" />
          <p>Loading job requisitions...</p>
        </div>
      ) : filteredJobs.length === 0 ? (
        <div className="p-12 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-center space-y-4">
          <Briefcase className="w-10 h-10 text-slate-300 dark:text-slate-700 mx-auto" />
          <div>
            <h3 className="text-sm font-bold text-slate-800 dark:text-slate-200">No job requisitions found</h3>
            <p className="text-xs text-slate-500 mt-1">Get started by creating your first role or seeding our benchmark position.</p>
          </div>
          <div className="flex justify-center gap-3">
            <button
              onClick={handleSeed}
              className="text-xs px-4 py-2 rounded-xl bg-indigo-50 text-indigo-600 font-semibold border border-indigo-200"
            >
              Seed Canonical Demo Job
            </button>
            <Link
              href="/jobs/new"
              className="text-xs px-4 py-2 rounded-xl bg-indigo-600 text-white font-semibold shadow"
            >
              + Create New Job
            </Link>
          </div>
        </div>
      ) : (
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 dark:bg-slate-800/60 border-b border-slate-200 dark:border-slate-800 text-slate-500 uppercase tracking-wider font-semibold">
                <tr>
                  <th className="py-3.5 px-4 font-bold">Job Title</th>
                  <th className="py-3.5 px-4">Seniority</th>
                  <th className="py-3.5 px-4">Location</th>
                  <th className="py-3.5 px-4">Work Mode</th>
                  <th className="py-3.5 px-4">Experience</th>
                  <th className="py-3.5 px-4 text-center">Candidates</th>
                  <th className="py-3.5 px-4 text-center">Shortlisted</th>
                  <th className="py-3.5 px-4 text-center">Avg Match</th>
                  <th className="py-3.5 px-4 text-center">Status</th>
                  <th className="py-3.5 px-4">Created Date</th>
                  <th className="py-3.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {filteredJobs.map((job) => {
                  const createdDate = job.created_at
                    ? new Date(job.created_at).toLocaleDateString("en-US", {
                        month: "short",
                        day: "numeric",
                        year: "numeric",
                      })
                    : "Recently";

                  return (
                    <tr
                      key={job.id}
                      className="hover:bg-slate-50/80 dark:hover:bg-slate-800/50 transition-colors"
                    >
                      {/* Job Title */}
                      <td className="py-3.5 px-4">
                        <Link
                          href={`/jobs/${job.id}`}
                          className="font-bold text-slate-900 dark:text-white hover:text-indigo-600 transition-colors block text-sm"
                        >
                          {job.title}
                        </Link>
                        <span className="text-[10px] text-slate-400">
                          ID: #{job.id} • {job.requirements?.length || 0} requirements
                        </span>
                      </td>

                      {/* Seniority */}
                      <td className="py-3.5 px-4">
                        <span className="inline-block px-2 py-0.5 rounded text-[11px] font-semibold bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300">
                          {job.seniority || "Mid-Senior"}
                        </span>
                      </td>

                      {/* Location */}
                      <td className="py-3.5 px-4 text-slate-700 dark:text-slate-300">
                        <div className="flex items-center gap-1">
                          <MapPin className="w-3 h-3 text-slate-400" />
                          <span>{job.location || "Remote"}</span>
                        </div>
                      </td>

                      {/* Work Mode */}
                      <td className="py-3.5 px-4 text-slate-600 dark:text-slate-400">
                        {job.work_mode || "Hybrid"}
                      </td>

                      {/* Experience */}
                      <td className="py-3.5 px-4 text-slate-700 dark:text-slate-300 font-medium">
                        {job.min_years_experience}+ yrs
                      </td>

                      {/* Candidates Count */}
                      <td className="py-3.5 px-4 text-center font-bold text-slate-900 dark:text-white">
                        {job.candidates_count ?? (job as any).match_results?.length ?? 0}
                      </td>

                      {/* Shortlisted */}
                      <td className="py-3.5 px-4 text-center">
                        <span className="inline-block px-2 py-0.5 rounded-full text-[11px] font-extrabold bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300">
                          {job.shortlisted_count ?? 0}
                        </span>
                      </td>

                      {/* Average Match */}
                      <td className="py-3.5 px-4 text-center">
                        <span className="font-extrabold text-sm text-indigo-600 dark:text-indigo-400">
                          {job.average_match_score ? `${job.average_match_score}%` : "—"}
                        </span>
                      </td>

                      {/* Status */}
                      <td className="py-3.5 px-4 text-center">
                        <span
                          className={`inline-block px-2 py-0.5 rounded text-[10px] font-extrabold uppercase ${
                            job.status === "active"
                              ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300"
                              : "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400"
                          }`}
                        >
                          {job.status || "active"}
                        </span>
                      </td>

                      {/* Created Date */}
                      <td className="py-3.5 px-4 text-slate-500 whitespace-nowrap">
                        {createdDate}
                      </td>

                      {/* Actions */}
                      <td className="py-3.5 px-4 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          <Link
                            href={`/jobs/${job.id}`}
                            className="px-2.5 py-1 rounded-md text-xs font-semibold bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-300 hover:bg-indigo-100 transition-colors"
                            title="Open Requisition"
                          >
                            Open
                          </Link>

                          <div className="relative">
                            <button
                              onClick={() => setActionMenuOpen(actionMenuOpen === job.id ? null : job.id)}
                              className="p-1 rounded-md hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-400 hover:text-slate-600"
                            >
                              <MoreVertical className="w-4 h-4" />
                            </button>

                            {actionMenuOpen === job.id && (
                              <div className="absolute right-0 mt-1 w-36 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-xl z-20 py-1 text-left text-xs animate-in fade-in">
                                <Link
                                  href={`/jobs/${job.id}`}
                                  className="flex items-center gap-2 px-3 py-1.5 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800"
                                >
                                  <Edit3 className="w-3.5 h-3.5 text-slate-400" /> Edit
                                </Link>
                                <button
                                  onClick={() => handleDuplicate(job.id)}
                                  className="w-full flex items-center gap-2 px-3 py-1.5 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800"
                                >
                                  <Copy className="w-3.5 h-3.5 text-slate-400" /> Duplicate
                                </button>
                                <button
                                  onClick={() => handleArchive(job.id)}
                                  className="w-full flex items-center gap-2 px-3 py-1.5 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800"
                                >
                                  <Archive className="w-3.5 h-3.5 text-slate-400" /> {job.status === "active" ? "Archive" : "Unarchive"}
                                </button>
                                <div className="border-t border-slate-100 dark:border-slate-800 my-1" />
                                <button
                                  onClick={() => handleDelete(job.id)}
                                  className="w-full flex items-center gap-2 px-3 py-1.5 text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/30"
                                >
                                  <Trash2 className="w-3.5 h-3.5" /> Delete
                                </button>
                              </div>
                            )}
                          </div>
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
