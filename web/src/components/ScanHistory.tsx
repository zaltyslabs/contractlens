"use client";

import { useState } from "react";
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
  const [reportHtml, setReportHtml] = useState<string | null>(null);
  const [reportTitle, setReportTitle] = useState("");

  function openReport(scan: ScanRecord) {
    if (scan.reportData?.report_html) {
      setReportHtml(scan.reportData.report_html);
      setReportTitle(scan.filename);
    }
  }

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
              className="flex items-center gap-4 p-4 rounded-xl bg-surface border border-white/[0.06] hover:border-white/[0.12] transition"
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
              {s.reportData?.report_html && (
                <button
                  onClick={() => openReport(s)}
                  className="text-xs font-semibold text-brand-500 hover:text-brand-400 px-3 py-1.5 rounded-lg border border-brand-500/20 hover:bg-brand-500/10 transition shrink-0"
                >
                  View Report
                </button>
              )}
            </div>
          );
        })}
      </div>

      {/* Report Modal */}
      {reportHtml && (
        <div
          className="fixed inset-0 z-[200] bg-black/70 backdrop-blur-sm flex items-center justify-center p-5"
          onClick={() => setReportHtml(null)}
        >
          <div
            className="bg-surface border border-white/[0.08] rounded-2xl w-full max-w-3xl max-h-[85vh] flex flex-col shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between px-5 py-3.5 border-b border-white/[0.07] shrink-0">
              <h3 className="text-sm font-bold text-white truncate">{reportTitle}</h3>
              <button
                onClick={() => setReportHtml(null)}
                className="w-8 h-8 rounded-lg flex items-center justify-center text-gray-500 hover:bg-white/[0.04] hover:text-white transition"
              >
                ✕
              </button>
            </div>
            <div className="overflow-auto flex-1">
              <iframe
                srcDoc={reportHtml}
                className="w-full h-full min-h-[60vh] border-0"
                sandbox="allow-scripts"
                title="Contract Analysis Report"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
