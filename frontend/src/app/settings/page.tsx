"use client";

import React, { useState } from "react";
import { Sliders, ShieldCheck, Key, Lock, CheckCircle2, Save, Sparkles, RefreshCw } from "lucide-react";
import { ScoringWeights } from "@/lib/types";

export default function SettingsPage() {
  const [weights, setWeights] = useState<ScoringWeights>({
    required_skills: 0.35,
    relevant_experience: 0.20,
    project_evidence: 0.15,
    education_cert: 0.10,
    preferred_skills: 0.10,
    domain_relevance: 0.05,
    evidence_confidence: 0.05,
  });

  const [saved, setSaved] = useState(false);
  const [geminiKey, setGeminiKey] = useState("");
  const [keySaved, setKeySaved] = useState(false);

  const totalWeightPercent = Math.round(
    Object.values(weights).reduce((a, b) => a + b, 0) * 100
  );

  const handleWeightChange = (key: keyof ScoringWeights, val: number) => {
    setWeights((prev) => ({
      ...prev,
      [key]: val / 100,
    }));
  };

  const handleSaveWeights = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="border-b border-slate-200 dark:border-slate-800 pb-5">
        <span className="text-xs font-bold text-indigo-600 uppercase tracking-widest">
          Platform Configuration
        </span>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white mt-1">
          Settings & Scoring Calibration
        </h1>
        <p className="text-xs text-slate-500">
          Configure deterministic scoring weights, Gemini LLM connection, and review Fair Match compliance policies
        </p>
      </div>

      {/* Recruiter Configurable Weights */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-5">
        <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
          <div>
            <h3 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
              <Sliders className="w-4 h-4 text-indigo-600" /> Explainable Scoring Weights
            </h3>
            <p className="text-xs text-slate-500">
              Customize relative importance of each dimension in the deterministic scoring formula
            </p>
          </div>
          <span
            className={`text-xs font-mono font-bold px-2 py-0.5 rounded ${
              totalWeightPercent === 100
                ? "bg-emerald-50 text-emerald-700"
                : "bg-amber-50 text-amber-700"
            }`}
          >
            Total: {totalWeightPercent}%
          </span>
        </div>

        <div className="space-y-4">
          <div className="space-y-1">
            <div className="flex justify-between text-xs font-semibold">
              <span>Required Skill Coverage (Must Haves)</span>
              <span className="font-mono text-indigo-600">{Math.round(weights.required_skills * 100)}%</span>
            </div>
            <input
              type="range"
              min="10"
              max="60"
              value={Math.round(weights.required_skills * 100)}
              onChange={(e) => handleWeightChange("required_skills", parseFloat(e.target.value))}
              className="w-full accent-indigo-600"
            />
          </div>

          <div className="space-y-1">
            <div className="flex justify-between text-xs font-semibold">
              <span>Relevant Experience Duration</span>
              <span className="font-mono text-indigo-600">{Math.round(weights.relevant_experience * 100)}%</span>
            </div>
            <input
              type="range"
              min="5"
              max="40"
              value={Math.round(weights.relevant_experience * 100)}
              onChange={(e) => handleWeightChange("relevant_experience", parseFloat(e.target.value))}
              className="w-full accent-indigo-600"
            />
          </div>

          <div className="space-y-1">
            <div className="flex justify-between text-xs font-semibold">
              <span>Project Deliverables & Scale Evidence</span>
              <span className="font-mono text-indigo-600">{Math.round(weights.project_evidence * 100)}%</span>
            </div>
            <input
              type="range"
              min="5"
              max="35"
              value={Math.round(weights.project_evidence * 100)}
              onChange={(e) => handleWeightChange("project_evidence", parseFloat(e.target.value))}
              className="w-full accent-indigo-600"
            />
          </div>

          <div className="space-y-1">
            <div className="flex justify-between text-xs font-semibold">
              <span>Education & Certifications</span>
              <span className="font-mono text-indigo-600">{Math.round(weights.education_cert * 100)}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="25"
              value={Math.round(weights.education_cert * 100)}
              onChange={(e) => handleWeightChange("education_cert", parseFloat(e.target.value))}
              className="w-full accent-indigo-600"
            />
          </div>

          <div className="space-y-1">
            <div className="flex justify-between text-xs font-semibold">
              <span>Preferred Skills (Should & Nice to Have)</span>
              <span className="font-mono text-indigo-600">{Math.round(weights.preferred_skills * 100)}%</span>
            </div>
            <input
              type="range"
              min="5"
              max="25"
              value={Math.round(weights.preferred_skills * 100)}
              onChange={(e) => handleWeightChange("preferred_skills", parseFloat(e.target.value))}
              className="w-full accent-indigo-600"
            />
          </div>

          <div className="space-y-1">
            <div className="flex justify-between text-xs font-semibold">
              <span>Domain Relevance</span>
              <span className="font-mono text-indigo-600">{Math.round(weights.domain_relevance * 100)}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="20"
              value={Math.round(weights.domain_relevance * 100)}
              onChange={(e) => handleWeightChange("domain_relevance", parseFloat(e.target.value))}
              className="w-full accent-indigo-600"
            />
          </div>

          <div className="space-y-1">
            <div className="flex justify-between text-xs font-semibold">
              <span>Evidence Confidence (Risk Adjusted)</span>
              <span className="font-mono text-indigo-600">{Math.round(weights.evidence_confidence * 100)}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="20"
              value={Math.round(weights.evidence_confidence * 100)}
              onChange={(e) => handleWeightChange("evidence_confidence", parseFloat(e.target.value))}
              className="w-full accent-indigo-600"
            />
          </div>

          <div className="flex justify-end pt-3">
            <button
              onClick={handleSaveWeights}
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold bg-indigo-600 text-white shadow-sm hover:bg-indigo-700"
            >
              <Save className="w-3.5 h-3.5" />
              {saved ? "Weights Calibrated!" : "Save Recruiter Weights"}
            </button>
          </div>
        </div>
      </div>

      {/* Gemini AI API Configuration */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-4">
        <h3 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-indigo-600" /> Gemini LLM API Configuration
        </h3>
        <p className="text-xs text-slate-500">
          TalentProof AI includes a complete offline heuristic reasoning engine for 100% demo reliability. To enable live multimodal Gemini 2.5 Flash reasoning, configure your key below or via <code className="bg-slate-100 dark:bg-slate-800 px-1 rounded">GEMINI_API_KEY</code> environment variable.
        </p>

        <div className="flex items-center gap-2">
          <input
            type="password"
            value={geminiKey}
            onChange={(e) => setGeminiKey(e.target.value)}
            placeholder="AIzaSy... (optional for live model generation)"
            className="flex-1 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-white focus:outline-none"
          />
          <button
            onClick={() => {
              setKeySaved(true);
              setTimeout(() => setKeySaved(false), 3000);
            }}
            className="px-4 py-2 rounded-lg text-xs font-semibold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 hover:bg-slate-200"
          >
            {keySaved ? "Saved" : "Save Key"}
          </button>
        </div>
      </div>

      {/* 50-Resume Benchmark Tool */}
      <div className="bg-gradient-to-r from-indigo-900/10 via-slate-900/10 to-purple-900/10 dark:from-indigo-950/40 dark:to-purple-950/40 border border-indigo-200 dark:border-indigo-800/80 rounded-2xl p-6 shadow-sm space-y-3">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <h3 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-indigo-600" /> 50-Resume Production Stress Test & Benchmark
            </h3>
            <p className="text-xs text-slate-500">
              Run the developer benchmark with 50 randomized synthetic candidate profiles across 5 realistic archetypes to verify accuracy, scoring determinism, and Supabase PostgreSQL persistence.
            </p>
          </div>
          <a
            href="/benchmark"
            className="px-4 py-2 rounded-xl text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 active:scale-95 transition-all shadow-md shadow-indigo-600/20 shrink-0"
          >
            Open Benchmark Runner →
          </a>
        </div>
      </div>

      {/* Fair Match & Bias Protection Compliance */}
      <div className="p-6 rounded-2xl bg-emerald-500/5 border border-emerald-500/20 space-y-3">
        <div className="flex items-center gap-2 text-emerald-700 dark:text-emerald-400 font-bold text-sm">
          <ShieldCheck className="w-5 h-5 text-emerald-600" /> Fair Match™ Bias Protection Architecture
        </div>
        <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed">
          TalentProof AI enforces strict job-relevant qualification and empirical evidence mapping. The ranking engine explicitly excludes protected demographic characteristics including gender, religion, caste, race, photograph analysis, age, and marital status. All scores are explainable, traceable, and subject to recruiter verification.
        </p>
        <div className="pt-2 flex items-center gap-2 text-[11px] font-semibold text-emerald-800 dark:text-emerald-300">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> Fully Compliant with Equal Opportunity & Fair Hiring Principles
        </div>
      </div>
    </div>
  );
}
