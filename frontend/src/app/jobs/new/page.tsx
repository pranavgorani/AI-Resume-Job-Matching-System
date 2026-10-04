"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { 
  Sparkles, 
  ArrowRight, 
  Plus, 
  Trash2, 
  CheckCircle2, 
  Layers, 
  Briefcase, 
  Info,
  Clock
} from "lucide-react";
import { analyzeRawJD, createJob } from "@/lib/api";

interface RequirementItem {
  name: string;
  category: string;
  tier: "MUST_HAVE" | "SHOULD_HAVE" | "NICE_TO_HAVE";
  expected_years: number;
  weight: number;
}

export default function NewJobPage() {
  const router = useRouter();

  const [title, setTitle] = useState("Senior Full Stack AI Engineer");
  const [description, setDescription] = useState(`We are looking for a Senior Full Stack AI Engineer to join our core intelligence team.
You will architect scalable Python backend microservices using FastAPI and design reactive user interfaces using React and TypeScript.
Core requirements:
- 3+ years professional software development experience.
- Deep hands-on experience in Python and FastAPI.
- Production experience with React, TypeScript, and state management.
- Strong knowledge of PostgreSQL database schema design and query optimization.
- Familiarity with Docker containerization and AWS cloud infrastructure.
- Experience integrating LLM APIs (Gemini, OpenAI, Claude) in production applications.
`);

  const [analyzing, setAnalyzing] = useState(false);
  const [analyzed, setAnalyzed] = useState(false);
  const [seniority, setSeniority] = useState("Senior");
  const [minExp, setMinExp] = useState(3.0);
  const [education, setEducation] = useState("Bachelor's degree in CS or equivalent");
  const [location, setLocation] = useState("Remote");
  const [workMode, setWorkMode] = useState("Hybrid / Remote");
  const [requirements, setRequirements] = useState<RequirementItem[]>([]);
  const [creating, setCreating] = useState(false);

  const handleAnalyzeJD = async () => {
    if (!description.trim()) return;
    setAnalyzing(true);
    try {
      const res = await analyzeRawJD(title, description);
      setSeniority(res.seniority);
      setMinExp(res.min_years_experience);
      setEducation(res.education_required);
      setLocation(res.location);
      setWorkMode(res.work_mode);
      setRequirements(res.classified_requirements || []);
      setAnalyzed(true);
    } catch (err: any) {
      alert(`JD Analysis error: ${err.message}`);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleAddRequirement = () => {
    setRequirements((prev) => [
      ...prev,
      {
        name: "New Skill",
        category: "skill",
        tier: "SHOULD_HAVE",
        expected_years: 2.0,
        weight: 0.8,
      },
    ]);
  };

  const handleRemoveRequirement = (idx: number) => {
    setRequirements((prev) => prev.filter((_, i) => i !== idx));
  };

  const handleUpdateReq = (idx: number, field: string, val: any) => {
    setRequirements((prev) =>
      prev.map((r, i) => (i === idx ? { ...r, [field]: val } : r))
    );
  };

  const handleFinalSubmit = async () => {
    setCreating(true);
    try {
      const payload = {
        title,
        raw_description: description,
        seniority,
        min_years_experience: minExp,
        education_required: education,
        location,
        work_mode: workMode,
      };
      const created = await createJob(payload);
      router.push(`/jobs/${created.id}`);
    } catch (err: any) {
      alert(`Job creation failed: ${err.message}`);
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Title */}
      <div>
        <span className="text-xs font-bold text-indigo-600 uppercase tracking-widest">
          Job Intelligence Engine
        </span>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white mt-1">
          Create & Analyze Job Requisition
        </h1>
        <p className="text-xs text-slate-500">
          Enter raw Job Description text. AI extracts structured competencies and classifies requirements into MUST, SHOULD, and NICE TO HAVE tiers.
        </p>
      </div>

      {/* Step 1: Input Job Details */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-5">
        <h2 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <Briefcase className="w-4 h-4 text-indigo-600" /> Requisition Details
        </h2>

        <div className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Job Title
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg px-3.5 py-2 text-xs text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500 outline-none"
              placeholder="e.g. Senior Full Stack AI Engineer"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Raw Job Description Text
            </label>
            <textarea
              rows={8}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg p-3 text-xs text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500 outline-none font-mono"
              placeholder="Paste complete Job Description here..."
            />
          </div>

          <div className="flex justify-end">
            <button
              onClick={handleAnalyzeJD}
              disabled={analyzing || !description.trim()}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-xs bg-indigo-600 text-white shadow-md shadow-indigo-600/20 hover:bg-indigo-700 active:scale-95 transition-all disabled:opacity-50"
            >
              <Sparkles className={`w-4 h-4 ${analyzing ? "animate-spin" : ""}`} />
              {analyzing ? "Extracting Requirements..." : "Analyze JD With AI"}
            </button>
          </div>
        </div>
      </div>

      {/* Step 2: Extracted Requirements Review & Edit */}
      {analyzed && (
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-6 animate-in fade-in">
          <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-4">
            <div>
              <h2 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" /> Extracted Requirements & Classification
              </h2>
              <p className="text-xs text-slate-500">
                Review and adjust the extracted requirements and tiers before publishing to matching engine.
              </p>
            </div>
            <button
              onClick={handleAddRequirement}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 transition-colors"
            >
              <Plus className="w-3.5 h-3.5" /> Add Requirement
            </button>
          </div>

          {/* Metadata Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Seniority</span>
              <div className="font-bold text-slate-900 dark:text-white mt-0.5">{seniority}</div>
            </div>
            <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Min Experience</span>
              <div className="font-bold text-slate-900 dark:text-white mt-0.5">{minExp}+ Years</div>
            </div>
            <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Location</span>
              <div className="font-bold text-slate-900 dark:text-white mt-0.5">{location}</div>
            </div>
            <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Work Mode</span>
              <div className="font-bold text-slate-900 dark:text-white mt-0.5">{workMode}</div>
            </div>
          </div>

          {/* Classified Requirements Table / List */}
          <div className="space-y-2">
            {requirements.map((req, idx) => (
              <div
                key={idx}
                className="flex items-center gap-3 p-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/40 text-xs"
              >
                <div className="flex-1 font-semibold text-slate-900 dark:text-white">
                  <input
                    type="text"
                    value={req.name}
                    onChange={(e) => handleUpdateReq(idx, "name", e.target.value)}
                    className="w-full bg-transparent font-bold focus:outline-none"
                  />
                </div>

                <div className="w-36">
                  <select
                    value={req.tier}
                    onChange={(e) => handleUpdateReq(idx, "tier", e.target.value)}
                    className={`w-full text-xs font-semibold py-1 px-2 rounded-md border ${
                      req.tier === "MUST_HAVE"
                        ? "bg-indigo-50 border-indigo-200 text-indigo-700"
                        : req.tier === "SHOULD_HAVE"
                        ? "bg-amber-50 border-amber-200 text-amber-700"
                        : "bg-slate-100 border-slate-200 text-slate-600"
                    }`}
                  >
                    <option value="MUST_HAVE">MUST HAVE</option>
                    <option value="SHOULD_HAVE">SHOULD HAVE</option>
                    <option value="NICE_TO_HAVE">NICE TO HAVE</option>
                  </select>
                </div>

                <div className="flex items-center gap-1 w-24">
                  <Clock className="w-3 h-3 text-slate-400" />
                  <input
                    type="number"
                    step="0.5"
                    value={req.expected_years}
                    onChange={(e) => handleUpdateReq(idx, "expected_years", parseFloat(e.target.value) || 0)}
                    className="w-12 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded px-1.5 py-0.5 text-xs text-center"
                  />
                  <span className="text-[11px] text-slate-400">yrs</span>
                </div>

                <button
                  onClick={() => handleRemoveRequirement(idx)}
                  className="p-1 rounded text-slate-400 hover:text-rose-500 hover:bg-rose-50 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>

          {/* Confirm & Publish */}
          <div className="pt-4 border-t border-slate-200 dark:border-slate-800 flex justify-end">
            <button
              onClick={handleFinalSubmit}
              disabled={creating}
              className="flex items-center gap-2 px-6 py-2.5 rounded-xl font-bold text-xs bg-emerald-600 text-white shadow-md shadow-emerald-600/20 hover:bg-emerald-700 active:scale-95 transition-all"
            >
              {creating ? "Creating..." : "Publish Job & Enable Matching Engine"}
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
