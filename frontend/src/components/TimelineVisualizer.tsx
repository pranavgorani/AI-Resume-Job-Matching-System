import React from "react";
import { Briefcase, GraduationCap, AlertTriangle, Calendar } from "lucide-react";
import { RiskFlag } from "@/lib/types";

interface Experience {
  company: string;
  role: string;
  start_date?: string;
  end_date?: string;
  duration_years: number;
  responsibilities: string[];
  technologies: string[];
}

interface Education {
  degree: string;
  institution: string;
  graduation_year?: string;
  field?: string;
}

interface TimelineVisualizerProps {
  experiences: Experience[];
  educations: Education[];
  riskFlags: RiskFlag[];
}

export const TimelineVisualizer: React.FC<TimelineVisualizerProps> = ({
  experiences,
  educations,
  riskFlags,
}) => {
  // Combine all items into chronological list
  const timelineItems: Array<{
    type: "exp" | "edu";
    title: string;
    subtitle: string;
    date: string;
    duration?: string;
    details?: string[];
    isOverlapping?: boolean;
    flagText?: string;
  }> = [];

  const overlapFlag = riskFlags.find((f) => f.flag_type === "TIMELINE_OVERLAP");

  educations.forEach((edu) => {
    timelineItems.push({
      type: "edu",
      title: edu.degree,
      subtitle: edu.institution,
      date: edu.graduation_year || "Degree",
      details: edu.field ? [edu.field] : [],
      isOverlapping: Boolean(overlapFlag),
      flagText: overlapFlag ? "Academic enrollment period overlapped with senior employment" : undefined,
    });
  });

  experiences.forEach((exp) => {
    const isOverlapped = Boolean(
      overlapFlag && (exp.role.toLowerCase().includes("senior") || exp.role.toLowerCase().includes("lead"))
    );
    timelineItems.push({
      type: "exp",
      title: exp.role,
      subtitle: exp.company,
      date: `${exp.start_date || "Start"} — ${exp.end_date || "End"}`,
      duration: `${exp.duration_years.toFixed(1)} yrs`,
      details: exp.technologies.slice(0, 5),
      isOverlapping: isOverlapped,
      flagText: isOverlapped ? overlapFlag?.headline : undefined,
    });
  });

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="font-bold text-slate-900 dark:text-white text-sm flex items-center gap-2">
            <Calendar className="w-4 h-4 text-indigo-600" /> Career & Education Chronology
          </h3>
          <p className="text-xs text-slate-500">Timeline verification & overlap detection engine</p>
        </div>
        {riskFlags.some((f) => f.flag_type === "TIMELINE_OVERLAP" || f.flag_type === "DURATION_MISMATCH") && (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-amber-500/10 text-amber-600 border border-amber-500/20">
            <AlertTriangle className="w-3.5 h-3.5" /> Timeline Verification Flagged
          </span>
        )}
      </div>

      <div className="relative border-l-2 border-slate-200 dark:border-slate-800 ml-3.5 pl-6 space-y-6">
        {timelineItems.map((item, idx) => (
          <div key={idx} className="relative group">
            {/* Timeline Dot */}
            <div
              className={`absolute -left-[31px] top-1 w-6 h-6 rounded-full border-2 flex items-center justify-center text-xs ${
                item.isOverlapping
                  ? "bg-amber-100 border-amber-500 text-amber-700"
                  : item.type === "exp"
                  ? "bg-indigo-50 border-indigo-500 text-indigo-600 dark:bg-indigo-950"
                  : "bg-emerald-50 border-emerald-500 text-emerald-600 dark:bg-emerald-950"
              }`}
            >
              {item.type === "exp" ? <Briefcase className="w-3 h-3" /> : <GraduationCap className="w-3 h-3" />}
            </div>

            {/* Content Card */}
            <div
              className={`p-3.5 rounded-lg border text-xs transition-all ${
                item.isOverlapping
                  ? "bg-amber-500/5 border-amber-500/30"
                  : "bg-slate-50/50 dark:bg-slate-800/40 border-slate-200/80 dark:border-slate-800 hover:border-slate-300"
              }`}
            >
              <div className="flex items-center justify-between gap-2 mb-1">
                <span className="font-bold text-slate-900 dark:text-white text-sm">{item.title}</span>
                <span className="text-[11px] font-mono text-slate-500 bg-white dark:bg-slate-900 px-2 py-0.5 rounded border border-slate-200 dark:border-slate-700">
                  {item.date} {item.duration && `(${item.duration})`}
                </span>
              </div>
              <div className="text-slate-600 dark:text-slate-400 font-medium mb-2">{item.subtitle}</div>

              {item.details && item.details.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-1">
                  {item.details.map((t, i) => (
                    <span
                      key={i}
                      className="px-2 py-0.5 rounded bg-slate-200/70 dark:bg-slate-700/60 text-[10px] text-slate-700 dark:text-slate-300"
                    >
                      {t}
                    </span>
                  ))}
                </div>
              )}

              {item.isOverlapping && item.flagText && (
                <div className="mt-2.5 p-2 rounded bg-amber-100/70 dark:bg-amber-950/40 border border-amber-300/50 dark:border-amber-800 text-[11px] text-amber-800 dark:text-amber-300 flex items-start gap-1.5 font-medium">
                  <AlertTriangle className="w-3.5 h-3.5 shrink-0 mt-0.5" />
                  <span>{item.flagText}</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
