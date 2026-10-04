import React from "react";
import { CheckCircle2, AlertTriangle, XCircle, AlertOctagon, ArrowRightLeft } from "lucide-react";

interface EvidenceBadgeProps {
  strength: "HIGH" | "PARTIAL" | "WEAK_MISSING" | "CONTRADICTORY" | string;
  isTransferable?: boolean;
  score?: number;
  showIcon?: boolean;
  className?: string;
}

export const EvidenceBadge: React.FC<EvidenceBadgeProps> = ({
  strength,
  isTransferable = false,
  score,
  showIcon = true,
  className = "",
}) => {
  if (isTransferable) {
    return (
      <span
        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-amber-500/10 text-amber-600 border border-amber-500/20 ${className}`}
      >
        {showIcon && <ArrowRightLeft className="w-3.5 h-3.5" />}
        TRANSFERABLE {score !== undefined && `• ${Math.round(score)}%`}
      </span>
    );
  }

  switch (strength) {
    case "HIGH":
      return (
        <span
          className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-emerald-500/10 text-emerald-600 border border-emerald-500/20 ${className}`}
        >
          {showIcon && <CheckCircle2 className="w-3.5 h-3.5" />}
          STRONG EVIDENCE {score !== undefined && `• ${Math.round(score)}%`}
        </span>
      );

    case "PARTIAL":
      return (
        <span
          className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-amber-500/10 text-amber-600 border border-amber-500/20 ${className}`}
        >
          {showIcon && <AlertTriangle className="w-3.5 h-3.5" />}
          PARTIAL EVIDENCE {score !== undefined && `• ${Math.round(score)}%`}
        </span>
      );

    case "CONTRADICTORY":
      return (
        <span
          className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-purple-500/10 text-purple-600 border border-purple-500/20 ${className}`}
        >
          {showIcon && <AlertOctagon className="w-3.5 h-3.5" />}
          CONTRADICTION DETECTED {score !== undefined && `• ${Math.round(score)}%`}
        </span>
      );

    case "WEAK_MISSING":
    default:
      return (
        <span
          className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-rose-500/10 text-rose-600 border border-rose-500/20 ${className}`}
        >
          {showIcon && <XCircle className="w-3.5 h-3.5" />}
          MISSING / WEAK {score !== undefined && `• ${Math.round(score)}%`}
        </span>
      );
  }
};
