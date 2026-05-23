"use client";

import { useEffect } from "react";
import { X } from "lucide-react";
import { UploadResponse } from "@/lib/types";

interface Props {
  open: boolean;
  onClose: () => void;
  data: UploadResponse | null;
}

export default function ReportModal({ open, onClose, data }: Props) {
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    if (open) document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open || !data) return null;

  const zones = Object.entries(data.zones);

  return (
    <div className="fixed inset-0 z-[200] bg-black/70 backdrop-blur-sm flex items-center justify-center p-5" onClick={onClose}>
      <div className="bg-surface border border-white/[0.08] rounded-2xl w-full max-w-2xl max-h-[85vh] overflow-y-auto shadow-2xl" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="flex items-start justify-between p-6 pb-0">
          <div>
            <h2 className="text-lg font-bold text-white">Analysis Report</h2>
            <p className="text-sm text-gray-500 mt-0.5">{data.metadata?.title || "Contract Review"}</p>
          </div>
          <button onClick={onClose} className="w-8 h-8 rounded-lg flex items-center justify-center text-gray-500 hover:bg-white/[0.04] hover:text-white transition shrink-0">
            <X size={16} />
          </button>
        </div>

        {/* Overall risk */}
        <div className="flex items-center gap-2.5 px-6 pt-4">
          <span className="text-sm text-gray-500">Overall risk</span>
          <span className={`text-xs font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full ${
            data.risk === "high" ? "bg-risk-high/10 text-risk-high" :
            data.risk === "medium" ? "bg-risk-medium/10 text-risk-medium" :
            "bg-risk-low/10 text-risk-low"
          }`}>
            {data.risk}
          </span>
        </div>

        {/* Scoreboard */}
        <div className="grid grid-cols-2 gap-0.5 bg-white/[0.04] mx-6 my-4 rounded-xl overflow-hidden">
          {zones.map(([key, zone]) => (
            <div key={key} className="bg-surface p-4">
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-xs font-semibold text-gray-300">
                  {key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
                </span>
                <span className={`text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded ${
                  zone.risk === "high" ? "bg-risk-high/10 text-risk-high" :
                  zone.risk === "medium" ? "bg-risk-medium/10 text-risk-medium" :
                  "bg-risk-low/10 text-risk-low"
                }`}>
                  {zone.risk}
                </span>
              </div>
              <p className="text-xs text-gray-400 leading-relaxed">{zone.summary}</p>
            </div>
          ))}
        </div>

        {/* Actions */}
        {data.recommendations && data.recommendations.length > 0 && (
          <div className="px-6 pb-6">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-3">
              Recommended Actions
            </h3>
            <ol className="space-y-2">
              {data.recommendations.map((r, i) => (
                <li key={i} className="flex gap-2.5 text-sm text-gray-300">
                  <span className="text-brand-500 font-bold shrink-0">{i + 1}.</span>
                  <span>{r}</span>
                </li>
              ))}
            </ol>
          </div>
        )}

        {/* Disclaimer */}
        <div className="px-6 pb-6">
          <p className="text-[11px] text-gray-600 text-center border-t border-white/[0.06] pt-4">
            Not legal advice. This analysis is informational only — consult a licensed attorney before signing.
          </p>
        </div>
      </div>
    </div>
  );
}
