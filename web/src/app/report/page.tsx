"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export default function ReportPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const scanId = searchParams.get("id");

  const [reportHtml, setReportHtml] = useState<string | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!scanId) {
      setError("No report ID specified.");
      return;
    }

    const stored = localStorage.getItem("contractlens_scans");
    if (!stored) {
      setError("No scans found in storage.");
      return;
    }

    try {
      const scans = JSON.parse(stored);
      const scan = scans.find((s: { id: string }) => s.id === scanId);
      if (scan?.reportData?.report_html) {
        setReportHtml(scan.reportData.report_html);
      } else {
        setError("Report data not found for this scan.");
      }
    } catch {
      setError("Failed to read scan data.");
    }
  }, [scanId]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6">
        <div className="text-center max-w-md">
          <p className="text-red-400 mb-4">{error}</p>
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 text-sm font-semibold text-brand-500 hover:text-brand-400 transition"
          >
            <ArrowLeft size={16} />
            Back to dashboard
          </Link>
        </div>
      </div>
    );
  }

  if (!reportHtml) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-brand-500/30 border-t-brand-500 rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950">
      {/* Top bar */}
      <div className="sticky top-0 z-50 border-b border-white/[0.07] bg-gray-950/90 backdrop-blur-xl px-4 h-14 flex items-center gap-4">
        <Link
          href="/dashboard"
          className="flex items-center gap-2 text-sm text-gray-400 hover:text-white transition"
        >
          <ArrowLeft size={16} />
          Back to dashboard
        </Link>
        <div className="flex-1" />
        <span className="text-xs text-gray-600">ContractLens Report</span>
      </div>

      {/* Report content */}
      <div className="max-w-4xl mx-auto py-8 px-4">
        <iframe
          srcDoc={reportHtml}
          className="w-full min-h-[calc(100vh-8rem)] border-0 rounded-xl"
          sandbox="allow-scripts"
          title="Contract Analysis Report"
        />
      </div>
    </div>
  );
}
