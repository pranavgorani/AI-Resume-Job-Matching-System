import Link from "next/link";
import { AlertCircle, ArrowLeft, Plus } from "lucide-react";

export default function JobNotFound() {
  return (
    <div className="max-w-2xl mx-auto px-4 py-16 flex items-center justify-center min-h-[65vh]">
      <div className="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-8 sm:p-10 text-center shadow-xl relative overflow-hidden">
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-amber-500 via-rose-500 to-indigo-500" />
        
        <div className="w-16 h-16 rounded-2xl bg-amber-500/10 dark:bg-amber-500/20 border border-amber-500/20 flex items-center justify-center mx-auto mb-6 text-amber-500">
          <AlertCircle className="w-8 h-8" />
        </div>

        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 text-[11px] font-bold uppercase tracking-wider mb-3">
          Error 404 • Not Found
        </div>

        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white mb-2">
          Job Not Found
        </h1>

        <p className="text-sm text-slate-600 dark:text-slate-400 max-w-md mx-auto mb-8 leading-relaxed">
          This job may have been deleted or is no longer available.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
          <Link
            href="/jobs"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 text-xs font-bold transition-colors border border-slate-200 dark:border-slate-700"
          >
            <ArrowLeft className="w-4 h-4" />
            ← Back to Jobs
          </Link>
          <Link
            href="/jobs/new"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/25 transition-all"
          >
            <Plus className="w-4 h-4" />
            Create New Job
          </Link>
        </div>
      </div>
    </div>
  );
}
