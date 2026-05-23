"use client";

import Link from "next/link";
import { Shield, DollarSign, Lock, Clock, AlertTriangle, Scale, FileText } from "lucide-react";

const ZONES = [
  { key: "payment_terms", icon: DollarSign, name: "Payment Terms", question: "When and how do you get paid?", color: "border-l-green-500" },
  { key: "ip_ownership", icon: Lock, name: "IP & Ownership", question: "Who owns your work?", color: "border-l-blue-500" },
  { key: "non_compete", icon: AlertTriangle, name: "Non-Compete", question: "Can you work for competitors?", color: "border-l-red-500" },
  { key: "termination", icon: Clock, name: "Termination", question: "How can you exit?", color: "border-l-amber-500" },
  { key: "indemnification", icon: Shield, name: "Indemnification", question: "Who covers legal costs?", color: "border-l-orange-500" },
  { key: "liability_caps", icon: Scale, name: "Liability Caps", question: "How much can you lose?", color: "border-l-purple-500" },
];

export default function Hero() {
  return (
    <section className="max-w-6xl mx-auto px-4 pt-20 pb-16 grid lg:grid-cols-2 gap-14 items-center">
      <div>
        <span className="inline-flex items-center gap-2 bg-brand-500/10 border border-brand-500/20 rounded-full px-3 py-1 text-xs font-semibold text-brand-500 mb-5">
          <FileText size={14} /> AI-powered contract review
        </span>
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight leading-tight mb-5">
          <span className="gradient-text">Understand Every Contract</span>
          <br />
          <span className="text-white">You Sign</span>
        </h1>
        <p className="text-lg text-gray-400 max-w-md mb-8 leading-relaxed">
          Upload any contract. Get a plain-English summary of what you&apos;re actually signing — in minutes, not hours. No lawyer required.
        </p>
        <div className="flex gap-3 flex-wrap items-center">
          <Link
            href="/dashboard"
            className="px-6 py-3 rounded-xl text-sm font-semibold text-white bg-brand-500 hover:bg-brand-600 transition shadow-lg shadow-brand-500/20"
          >
            Analyze a contract free
          </Link>
          <span className="text-sm text-gray-500">No credit card required</span>
        </div>
      </div>

      {/* Preview card */}
      <div className="bg-surface border border-white/[0.07] rounded-2xl overflow-hidden shadow-2xl shadow-black/40">
        <div className="px-5 py-3.5 border-b border-white/[0.07] bg-surface-hover flex items-center justify-between">
          <div className="flex items-center gap-2.5 text-sm font-semibold text-gray-300">
            <FileText size={16} className="text-gray-500" />
            contractor_agreement.pdf
          </div>
          <span className="risk-badge risk-high text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-risk-high/10 text-risk-high">
            High Risk
          </span>
        </div>
        <div className="divide-y divide-white/[0.05]">
          {ZONES.map((z) => (
            <div key={z.key} className="flex items-start gap-3 px-5 py-3 hover:bg-white/[0.02] transition cursor-default">
              <z.icon size={16} className="text-gray-500 mt-0.5 shrink-0" />
              <div className="min-w-0 flex-1">
                <div className="text-xs font-semibold text-gray-300 uppercase tracking-wide">{z.name}</div>
                <div className="text-xs text-gray-500 mt-0.5">Checked for risks</div>
              </div>
              <span className="w-2 h-2 rounded-full bg-risk-medium shrink-0 mt-1.5" />
            </div>
          ))}
        </div>
        <div className="px-5 py-3 border-t border-white/[0.07] bg-surface-hover flex items-center justify-between">
          <span className="text-[11px] text-gray-500">6 danger zones analyzed</span>
          <span className="text-xs font-semibold text-brand-500">View report →</span>
        </div>
      </div>
    </section>
  );
}
