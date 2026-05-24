"use client";

import { useState, useRef } from "react";
import { Upload, Loader2 } from "lucide-react";
import { uploadContract } from "@/lib/api";

interface Props {
  onComplete: () => void;
  email?: string;
}

export default function UploadZone({ onComplete, email }: Props) {
  const [dragover, setDragover] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState("");
  const [filename, setFilename] = useState("");
  const [error, setError] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  async function handleFile(file: File) {
    if (!file) return;
    setError("");
    setFilename(file.name);
    setUploading(true);

    const steps = [
      "Extracting text…",
      "Checking 6 danger zones…",
      "Generating report…",
      "Sending to your email…",
    ];

    try {
      // Start progress animation
      let i = 0;
      setStatus(steps[0]);
      const interval = setInterval(() => {
        i++;
        if (i < steps.length) setStatus(steps[i]);
      }, 2000);

      const result = await uploadContract(file, email || "");

      clearInterval(interval);
      setStatus("Analysis complete!");

      // Save to localStorage so ScanHistory can display it
      const scanRecord = {
        id: crypto.randomUUID?.() || Date.now().toString(),
        filename: file.name,
        date: new Date().toISOString(),
        risk: result.risk,
        status: "done" as const,
        reportData: result,
      };
      const stored = JSON.parse(
        localStorage.getItem("contractlens_scans") || "[]"
      );
      stored.unshift(scanRecord);
      localStorage.setItem("contractlens_scans", JSON.stringify(stored));

      onComplete();
    } catch (err) {
      setStatus("");
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  return (
    <div>
      {!uploading && (
        <div
          className={`border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition ${
            dragover
              ? "border-brand-500 bg-brand-500/[0.04]"
              : "border-white/[0.08] hover:border-white/[0.15] hover:bg-white/[0.01]"
          }`}
          onClick={() => fileRef.current?.click()}
          onDragOver={(e) => { e.preventDefault(); setDragover(true); }}
          onDragLeave={() => setDragover(false)}
          onDrop={(e) => { e.preventDefault(); setDragover(false); handleFile(e.dataTransfer.files[0]); }}
        >
          <div className="w-14 h-14 rounded-xl bg-white/[0.03] border border-white/[0.08] flex items-center justify-center mx-auto mb-4">
            <Upload size={22} className="text-brand-500" />
          </div>
          <h3 className="text-lg font-bold text-white mb-2">Upload a contract</h3>
          <p className="text-sm text-gray-400 mb-5">
            Drag and drop a PDF, DOCX, or TXT file — or click to browse
          </p>
          <button
            className="px-5 py-2.5 rounded-lg text-sm font-semibold bg-brand-500 hover:bg-brand-600 text-white transition"
            onClick={(e) => { e.stopPropagation(); fileRef.current?.click(); }}
          >
            Choose file
          </button>
          <input
            ref={fileRef}
            type="file"
            accept=".pdf,.docx,.txt,.md"
            className="hidden"
            onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
          />
          <p className="text-xs text-gray-600 mt-4">Max 20MB · Files are securely deleted after processing</p>
        </div>
      )}

      {uploading && (
        <div className="bg-surface border border-white/[0.07] rounded-2xl p-8">
          <div className="flex items-center gap-5">
            <Loader2 size={32} className="text-brand-500 animate-spin shrink-0" />
            <div className="min-w-0">
              <div className="font-semibold text-white truncate">{filename}</div>
              <div className="text-sm text-gray-400 mt-1">{status}</div>
            </div>
          </div>
          <p className="text-xs text-gray-600 mt-5">
            {status === "Analysis complete!" ? "✓ Done" : "This typically takes 30–60 seconds"}
          </p>
        </div>
      )}

      {error && (
        <div className="mt-4 p-4 rounded-xl bg-risk-high/10 border border-risk-high/20 text-sm text-red-400">
          {error}
        </div>
      )}
    </div>
  );
}
