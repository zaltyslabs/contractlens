"use client";

import Link from "next/link";

const STRIPE_LINKS: Record<string, string> = {
  "Side Hustler": process.env.NEXT_PUBLIC_STRIPE_SIDE_HUSTLER || "",
  "Power Freelancer": process.env.NEXT_PUBLIC_STRIPE_POWER_FREELANCER || "",
  Agency: process.env.NEXT_PUBLIC_STRIPE_AGENCY || "",
};

const TIERS = [
  {
    name: "Free",
    price: 0,
    scansCount: 1,
    scans: "1 scan, ever",
    features: ["Full 6-zone analysis", "Risk levels per zone", "HTML report by email", "Key clause quotes"],
    cta: "Try free scan",
    href: "/dashboard",
    variant: "outline" as const,
  },
  {
    name: "Side Hustler",
    price: 12,
    scansCount: 5,
    scans: "5 scans per month",
    features: ["Everything in Free", "Scan history & dashboard", "Priority processing"],
    cta: "Subscribe — $12/mo",
    popular: true,
    variant: "primary" as const,
  },
  {
    name: "Power Freelancer",
    price: 25,
    scansCount: 20,
    scans: "20 scans per month",
    features: ["Everything in Side Hustler", "Redline suggestions", "Compare mode", "Contract templates"],
    cta: "Subscribe — $25/mo",
    variant: "outline" as const,
  },
  {
    name: "Agency",
    price: 49,
    scansCount: 50,
    scans: "50 scans per month",
    features: ["Everything in Power", "Team members (up to 5)", "Bulk upload", "Export to PDF/CSV"],
    cta: "Subscribe — $49/mo",
    variant: "outline" as const,
  },
];

const btnClass = (variant: "primary" | "outline") =>
  `w-full py-2.5 rounded-lg text-sm font-semibold transition text-center block ${
    variant === "primary"
      ? "bg-brand-500 hover:bg-brand-600 text-white shadow-lg shadow-brand-500/20"
      : "border border-white/[0.1] text-gray-300 hover:bg-white/[0.04]"
  }`;

export default function Pricing() {
  return (
    <section id="pricing" className="max-w-6xl mx-auto px-4 py-20 border-t border-white/[0.06]">
      <div className="text-center mb-14">
        <span className="text-xs font-semibold tracking-widest uppercase text-brand-500 mb-3 block">
          Pricing
        </span>
        <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-3">
          Simple, flat pricing
        </h2>
        <p className="text-gray-400 max-w-md mx-auto">
          No contracts. Cancel anytime. Designed for freelancers who sign agreements regularly.
        </p>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-px bg-white/[0.06] border border-white/[0.06] rounded-xl overflow-hidden">
        {TIERS.map((t) => (
          <div
            key={t.name}
            className={`bg-surface p-7 flex flex-col relative ${
              t.popular ? "bg-brand-500/[0.04]" : ""
            }`}
          >
            {t.popular && (
              <span className="absolute top-3 right-3 bg-brand-500 text-white text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full">
                Popular
              </span>
            )}
            <span className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">
              {t.name}
            </span>
            <div className="text-4xl font-extrabold text-white tracking-tight mb-1">
              ${t.price}
            </div>
            <span className="text-sm text-gray-500 mb-4">{t.scans}</span>
            <div className="w-full h-px bg-white/[0.06] mb-5" />
            <ul className="space-y-2 flex-1 mb-6">
              {t.features.map((f) => (
                <li key={f} className="text-sm text-gray-400 flex gap-2">
                  <span className="text-brand-500 font-bold shrink-0">–</span> {f}
                </li>
              ))}
            </ul>
            {t.href ? (
              <Link href={t.href} className={btnClass(t.variant)}>
                {t.cta}
              </Link>
            ) : (
              <a
                href={STRIPE_LINKS[t.name] || "#"}
                className={btnClass(t.variant)}
                onClick={(e) => {
                  if (!STRIPE_LINKS[t.name]) {
                    e.preventDefault();
                    alert("Payment link not configured yet.");
                    return;
                  }
                }}
              >
                {t.cta}
              </a>
            )}
            {t.price > 0 && (
              <div className="text-[11px] text-gray-600 text-center mt-3">
                ${(t.price / t.scansCount).toFixed(2)} per scan
              </div>
            )}
          </div>
        ))}
      </div>

      <p className="text-xs text-gray-600 text-center mt-6">
        All plans include the full 6-zone analysis, plain-English summaries, and email delivery. Not legal advice.
      </p>
    </section>
  );
}
