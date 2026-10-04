import React from "react";
import { X, HelpCircle, ArrowUpRight, CheckCircle2, AlertTriangle, ShieldAlert } from "lucide-react";

interface WhyNotModalProps {
  isOpen: boolean;
  onClose: () => void;
  candidateName: string;
  matchScore: number;
  barriers: string[];
  evidenceNeeded: string[];
  tradeoffSummary?: string;
}

export const WhyNotModal: React.FC<WhyNotModalProps> = ({
  isOpen,
  onClose,
  candidateName,
  matchScore,
  barriers,
  evidenceNeeded,
  tradeoffSummary,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="w-full max-w-2xl bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="p-5 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between bg-slate-50 dark:bg-slate-950">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-rose-500/10 text-rose-600 flex items-center justify-center">
              <HelpCircle className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-base text-slate-900 dark:text-white">
                Why Not {candidateName}?
              </h3>
              <p className="text-xs text-slate-500">
                Decision Intelligence • Current Match: {matchScore}%
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-200/50"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-6 text-sm">
          {/* Head to Head Comparison */}
          {tradeoffSummary && (
            <div className="p-4 rounded-xl bg-indigo-50/70 dark:bg-indigo-950/40 border border-indigo-200/60 dark:border-indigo-800/60 text-slate-800 dark:text-slate-200">
              <h4 className="font-bold text-xs uppercase tracking-wider text-indigo-700 dark:text-indigo-400 mb-1.5 flex items-center gap-1.5">
                <ArrowUpRight className="w-4 h-4" /> Peer Outranking Summary
              </h4>
              <p className="text-xs leading-relaxed">{tradeoffSummary}</p>
            </div>
          )}

          {/* Primary Barriers to #1 */}
          <div>
            <h4 className="font-bold text-xs uppercase tracking-wider text-slate-500 mb-2.5 flex items-center gap-1.5">
              <ShieldAlert className="w-4 h-4 text-amber-500" /> Primary Decision Barriers Preventing #1 Rank
            </h4>
            <div className="space-y-2">
              {barriers.map((b, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200/70 dark:border-slate-800 flex items-start gap-2.5 text-xs text-slate-700 dark:text-slate-300"
                >
                  <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
                  <span>{b}</span>
                </div>
              ))}
            </div>
          </div>

          {/* What Evidence Would Change the Decision */}
          <div>
            <h4 className="font-bold text-xs uppercase tracking-wider text-slate-500 mb-2.5 flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-500" /> What Evidence Would Reverse This Decision?
            </h4>
            <div className="space-y-2">
              {evidenceNeeded.map((ev, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-lg bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-200/50 dark:border-emerald-800/50 flex items-start gap-2.5 text-xs text-emerald-900 dark:text-emerald-200"
                >
                  <span className="w-4 h-4 rounded-full bg-emerald-500/20 text-emerald-700 dark:text-emerald-400 flex items-center justify-center text-[10px] font-bold shrink-0 mt-0.5">
                    {idx + 1}
                  </span>
                  <span>{ev}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg text-xs font-semibold bg-slate-900 text-white dark:bg-white dark:text-slate-900 hover:opacity-90"
          >
            Close Intelligence Modal
          </button>
        </div>
      </div>
    </div>
  );
};
