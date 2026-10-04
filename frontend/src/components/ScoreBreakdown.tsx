import React from "react";
import { ShieldCheck, Target, TrendingUp, Sparkles, HelpCircle } from "lucide-react";

interface ScoreBreakdownProps {
  overallScore: number;
  hiringConfidence: number;
  evidenceConfidence: number;
  potentialScore: number;
  breakdown: Record<string, number>;
  recommendation: string;
}

export const ScoreBreakdown: React.FC<ScoreBreakdownProps> = ({
  overallScore,
  hiringConfidence,
  evidenceConfidence,
  potentialScore,
  breakdown,
  recommendation,
}) => {
  const metricItems = [
    { label: "Required Skill Coverage (35%)", key: "required_skills", value: breakdown.required_skills ?? 85 },
    { label: "Relevant Experience (20%)", key: "experience", value: breakdown.experience ?? 80 },
    { label: "Project Evidence (15%)", key: "project_evidence", value: breakdown.project_evidence ?? 80 },
    { label: "Education & Certifications (10%)", key: "education", value: breakdown.education ?? 80 },
    { label: "Preferred Skill Coverage (10%)", key: "preferred_skills", value: breakdown.preferred_skills ?? 75 },
    { label: "Domain Relevance (5%)", key: "domain_relevance", value: breakdown.domain_relevance ?? 80 },
    { label: "Evidence Confidence (5%)", key: "evidence_confidence", value: breakdown.evidence_confidence ?? 75 },
  ];

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm space-y-6">
      {/* Top 3 High-Level Intelligence Scores */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Match Score */}
        <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/80 dark:border-slate-700/80">
          <div className="flex items-center justify-between text-xs text-slate-500 font-medium mb-1">
            <span className="flex items-center gap-1.5 font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300">
              <Target className="w-3.5 h-3.5 text-indigo-600" /> Overall Match
            </span>
            <span className="text-[10px] bg-indigo-50 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400 px-1.5 py-0.5 rounded font-bold">
              WEIGHTED
            </span>
          </div>
          <div className="text-3xl font-extrabold text-slate-900 dark:text-white">
            {overallScore}%
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Multi-factor deterministic synthesis</p>
        </div>

        {/* Hiring Confidence */}
        <div className="p-4 rounded-xl bg-amber-500/5 border border-amber-500/20">
          <div className="flex items-center justify-between text-xs text-amber-700 dark:text-amber-400 font-medium mb-1">
            <span className="flex items-center gap-1.5 font-bold uppercase tracking-wider">
              <ShieldCheck className="w-3.5 h-3.5" /> Hiring Confidence
            </span>
            <span className="text-[10px] bg-amber-500/10 text-amber-700 dark:text-amber-300 px-1.5 py-0.5 rounded font-bold">
              RISK-ADJUSTED
            </span>
          </div>
          <div className="text-3xl font-extrabold text-amber-700 dark:text-amber-400">
            {hiringConfidence}%
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Discounted for unverified claims & risk flags</p>
        </div>

        {/* Talent Potential Mode */}
        <div className="p-4 rounded-xl bg-emerald-500/5 border border-emerald-500/20">
          <div className="flex items-center justify-between text-xs text-emerald-700 dark:text-emerald-400 font-medium mb-1">
            <span className="flex items-center gap-1.5 font-bold uppercase tracking-wider">
              <TrendingUp className="w-3.5 h-3.5" /> Potential Match
            </span>
            <span className="text-[10px] bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 px-1.5 py-0.5 rounded font-bold">
              UPSKILLING
            </span>
          </div>
          <div className="text-3xl font-extrabold text-emerald-600 dark:text-emerald-400">
            {potentialScore}%
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Transferable capabilities upside</p>
        </div>
      </div>

      {/* 7-Factor Explainable Bars */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300">
            Explainable Weight Breakdown (No Black Box)
          </h4>
          <span className="text-[11px] text-slate-500">Recruiter Configurable</span>
        </div>

        <div className="space-y-3">
          {metricItems.map((item, idx) => (
            <div key={idx} className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-600 dark:text-slate-400 font-medium">{item.label}</span>
                <span className="font-bold text-slate-900 dark:text-white font-mono">{Math.round(item.value)}/100</span>
              </div>
              <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-2 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-indigo-500 to-emerald-500 h-full rounded-full transition-all duration-500"
                  style={{ width: `${Math.min(100, Math.max(0, item.value))}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
