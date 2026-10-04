"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { 
  ShieldCheck, 
  Sparkles, 
  PlayCircle, 
  ArrowRight, 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  AlertOctagon,
  Layers,
  Search,
  Zap,
  Target,
  FileText,
  Lock,
  ChevronRight
} from "lucide-react";
import { seedDemoData } from "@/lib/api";

export default function LandingPage() {
  const router = useRouter();
  const [seeding, setSeeding] = useState(false);

  const handleLaunchDemo = async () => {
    try {
      setSeeding(true);
      const res = await seedDemoData();
      router.push(`/jobs/${res.job_id}`);
    } catch (err: any) {
      alert(`Demo failed: ${err.message}`);
    } finally {
      setSeeding(false);
    }
  };

  return (
    <div className="flex flex-col min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-16 pb-20 md:pt-24 md:pb-28 border-b border-slate-200 dark:border-slate-800 bg-gradient-to-b from-white via-slate-50 to-indigo-50/20 dark:from-slate-950 dark:via-slate-900 dark:to-indigo-950/20">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-6">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 border border-indigo-500/20 text-xs font-semibold shadow-sm animate-pulse">
            <Sparkles className="w-3.5 h-3.5" />
            ALGOTHON'26 AI Resume & Job Matching Finalist System
          </div>

          {/* Heading */}
          <h1 className="text-4xl sm:text-6xl font-black tracking-tight text-slate-900 dark:text-white max-w-4xl mx-auto leading-tight sm:leading-none">
            Don't just rank resumes. <br className="hidden sm:inline" />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 via-violet-600 to-emerald-500">
              Prove the match.
            </span>
          </h1>

          {/* Subtitle */}
          <p className="text-lg sm:text-xl text-slate-600 dark:text-slate-300 max-w-2xl mx-auto leading-relaxed">
            Evidence-based AI candidate intelligence for faster, more explainable, and fraud-resistant hiring decisions.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
            <button
              onClick={handleLaunchDemo}
              disabled={seeding}
              id="hero-demo-cta"
              className="flex items-center gap-2.5 px-6 py-3.5 rounded-xl font-bold text-sm bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-lg shadow-indigo-600/25 hover:opacity-95 hover:scale-[1.02] active:scale-95 transition-all"
            >
              <PlayCircle className={`w-5 h-5 ${seeding ? "animate-spin" : ""}`} />
              {seeding ? "Seeding 8 Candidates..." : "TRY LIVE DEMO"}
            </button>
            <Link
              href="/jobs/new"
              className="flex items-center gap-2 px-6 py-3.5 rounded-xl font-bold text-sm bg-white dark:bg-slate-900 text-slate-800 dark:text-white border border-slate-300 dark:border-slate-700 shadow-sm hover:bg-slate-50 dark:hover:bg-slate-800 transition-all"
            >
              CREATE JOB <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          {/* Fair Match Trust Banner */}
          <div className="pt-8 flex items-center justify-center gap-3 text-xs text-slate-500 font-medium">
            <span className="flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400 font-semibold">
              <ShieldCheck className="w-4 h-4" /> Fair Match Compliant
            </span>
            <span>•</span>
            <span>No Demographic Bias</span>
            <span>•</span>
            <span>Deterministic Scoring</span>
            <span>•</span>
            <span>Contradiction Detection</span>
          </div>
        </div>
      </section>

      {/* 3 Core Concepts: MATCH, EVIDENCE, VERIFY */}
      <section className="py-16 md:py-20 max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center space-y-2 mb-12">
          <h2 className="text-xs font-bold tracking-widest text-indigo-600 uppercase">Architecture Differentiator</h2>
          <p className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">
            The Evidence-First Matching Engine
          </p>
          <p className="text-sm text-slate-500 max-w-lg mx-auto">
            Traditional ATS tools rely on shallow keyword frequency. TalentProof AI builds an explainable Evidence Graph.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Concept 1: MATCH */}
          <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm hover:shadow-md transition-shadow space-y-4">
            <div className="w-12 h-12 rounded-xl bg-indigo-500/10 text-indigo-600 flex items-center justify-center font-bold text-lg">
              01
            </div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-white">1. Intelligent Job Requirements</h3>
            <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
              Analyzes job descriptions to classify skills into <strong className="text-slate-900 dark:text-white">MUST HAVE</strong>, <strong className="text-slate-900 dark:text-white">SHOULD HAVE</strong>, and <strong className="text-slate-900 dark:text-white">NICE TO HAVE</strong> before matching.
            </p>
            <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60 text-xs font-mono space-y-1">
              <div className="text-emerald-600">✓ Python → MUST HAVE</div>
              <div className="text-indigo-600">✓ FastAPI → MUST HAVE</div>
              <div className="text-amber-600">✓ Docker → SHOULD HAVE</div>
              <div className="text-slate-500">✓ AWS → NICE TO HAVE</div>
            </div>
          </div>

          {/* Concept 2: EVIDENCE */}
          <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm hover:shadow-md transition-shadow space-y-4">
            <div className="w-12 h-12 rounded-xl bg-emerald-500/10 text-emerald-600 flex items-center justify-center font-bold text-lg">
              02
            </div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-white">2. Grounded Evidence Mapping</h3>
            <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
              Traces every candidate claim directly to tangible resume deliverables, project codebases, and company responsibilities with confidence scoring.
            </p>
            <div className="space-y-1.5 text-xs">
              <div className="flex items-center justify-between p-2 rounded bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 font-semibold">
                <span>GREEN: Strongly Supported</span>
                <span>88%+</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded bg-amber-500/10 text-amber-700 dark:text-amber-300 font-semibold">
                <span>YELLOW: Partial / Transferable</span>
                <span>Azure → AWS</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded bg-rose-500/10 text-rose-700 dark:text-rose-300 font-semibold">
                <span>RED: Missing Evidence</span>
                <span>0%</span>
              </div>
            </div>
          </div>

          {/* Concept 3: VERIFY */}
          <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm hover:shadow-md transition-shadow space-y-4">
            <div className="w-12 h-12 rounded-xl bg-purple-500/10 text-purple-600 flex items-center justify-center font-bold text-lg">
              03
            </div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-white">3. Contradiction & Risk Detection</h3>
            <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
              Identifies timeline overlaps (e.g. Senior Dev during full-time Master's) and unbacked buzzwords, generating targeted interview verification questions.
            </p>
            <div className="p-3 rounded-lg bg-purple-500/10 border border-purple-500/20 text-xs text-purple-800 dark:text-purple-300 space-y-1">
              <div className="font-bold flex items-center gap-1">
                <AlertOctagon className="w-3.5 h-3.5" /> PURPLE: Contradiction Flag
              </div>
              <div className="text-[11px] text-purple-700 dark:text-purple-400">
                Claim: 5 yrs Python • Evidence: ~2.5 yrs
              </div>
              <div className="text-[10px] text-slate-500 mt-1 italic">
                Generates neutral verification question
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Comparison: ATS vs TalentProof AI */}
      <section className="py-16 bg-slate-100/70 dark:bg-slate-900/50 border-y border-slate-200 dark:border-slate-800">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
          <div className="text-center space-y-2">
            <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">
              Why Keyword ATS Systems Fail
            </h2>
            <p className="text-xs sm:text-sm text-slate-500">
              See how TalentProof AI defeats keyword-stuffing hacks and uncovers real talent.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Traditional ATS */}
            <div className="p-6 rounded-2xl bg-white dark:bg-slate-950 border border-rose-200 dark:border-rose-900/50 space-y-4">
              <div className="flex items-center gap-2 text-rose-600 font-bold text-sm">
                <XCircle className="w-5 h-5" /> Traditional Keyword ATS
              </div>
              <ul className="text-xs text-slate-600 dark:text-slate-400 space-y-2.5">
                <li className="flex items-start gap-2">
                  <span className="text-rose-500 font-bold">✕</span>
                  <span><strong>Fooled by buzzword stuffing:</strong> Ranks candidates high just for pasting tech keywords into a skills block without evidence.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-rose-500 font-bold">✕</span>
                  <span><strong>Black-box arbitrary score:</strong> Generates a single opaque percentage without showing supporting proof.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-rose-500 font-bold">✕</span>
                  <span><strong>Ignores transferable skills:</strong> Rejects great candidates simply because they used Azure instead of AWS.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-rose-500 font-bold">✕</span>
                  <span><strong>Zero contradiction checks:</strong> Blind to timeline overlaps, concurrent degrees, and inflated tenure.</span>
                </li>
              </ul>
            </div>

            {/* TalentProof AI */}
            <div className="p-6 rounded-2xl bg-white dark:bg-slate-950 border border-emerald-300 dark:border-emerald-800 space-y-4 shadow-md">
              <div className="flex items-center gap-2 text-emerald-600 font-bold text-sm">
                <CheckCircle2 className="w-5 h-5" /> TalentProof AI
              </div>
              <ul className="text-xs text-slate-700 dark:text-slate-300 space-y-2.5">
                <li className="flex items-start gap-2">
                  <span className="text-emerald-500 font-bold">✓</span>
                  <span><strong>Evidence Graph verification:</strong> Inspects real projects and metrics to expose unbacked buzzwords.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-emerald-500 font-bold">✓</span>
                  <span><strong>Explainable 7-factor scoring:</strong> Every score is traceable to requirements, experience, and project proof.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-emerald-500 font-bold">✓</span>
                  <span><strong>Transferable skill intelligence:</strong> Recognizes Azure → AWS, Podman → Docker, and PyTorch → LLM APIs.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-emerald-500 font-bold">✓</span>
                  <span><strong>Contradiction & timeline audits:</strong> Flags timeline discrepancies and generates targeted interview questions.</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto py-8 border-t border-slate-200 dark:border-slate-800 text-center text-xs text-slate-500">
        <p>TalentProof AI • ALGOTHON'26 Official Submission • Evidence-First Candidate Intelligence Platform</p>
      </footer>
    </div>
  );
}
