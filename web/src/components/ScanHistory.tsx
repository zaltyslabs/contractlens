"use client";

import { ScanRecord } from "@/lib/types";

const RISK_COLORS: Record<string, string> = {
  high: "bg-risk-high",
  medium: "bg-risk-medium",
  low: "bg-risk-low",
  pending: "bg-gray-600",
};

const RISK_LABELS: Record<string, string> = {
  high: "High risk",
  medium: "Medium risk",
  low: "Low risk",
  pending: "Pending",
};

interface Props {
  scans: ScanRecord[];
}

export default function ScanHistory({ scans }: Props) {
  if (!scans.length) {
    return (
      <div className="text-center py-14 text-sm text-gray-500">
        No scans yet. Upload your first contract above.
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-white">Scan history</h3>
        <span className="text-xs text-gray-600">{scans.length} scan{scans.length !== 1 ? "s" : ""}</span>
      </div>
      <div className="flex flex-col gap-2">
        {scans.map((s) => {
          const rc = s.risk === "pending" ? "pending" : s.risk;
          return (
            <div
              key={s.id}
              className="flex items-center gap-4 p-4 rounded-xl bg-surface border border-white/[0.06] hover:border-white/[0.12] transition cursor-pointer"
            >
              <div className={`w-1 self-stretch rounded-full ${RISK_COLORS[rc]} shrink-0`} />
              <div className="flex-1 min-w-0">
                <div className="text-sm font-semibold text-white truncate">{s.filename}</div>
                <div className="text-xs text-gray-500 mt-0.5">
                  {new Date(s.date).toLocaleDateString("en-US", {
                    month: "short",
                    day: "numeric",
                    year: "numeric",
                  })}{" "}
                  ·{" "}
                  <span className={s.risk === "high" ? "text-risk-high" : s.risk === "medium" ? "text-risk-medium" : "text-gray-400"}>
                    {RISK_LABELS[s.risk] || s.risk}
                  </span>
                </div>
              </div>
              <span className="text-gray-600 text-sm shrink-0">›</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
