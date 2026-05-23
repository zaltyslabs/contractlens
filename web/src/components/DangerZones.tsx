import { DollarSign, Lock, AlertTriangle, Clock, Shield, Scale } from "lucide-react";

const ZONES = [
  { icon: DollarSign, name: "Payment Terms", key: "pay", question: "When & how do you get paid? Net-30 or Net-90? Late fees?", tags: ["Net terms", "Late fees", "Holdbacks"] },
  { icon: Lock, name: "IP & Ownership", key: "ip", question: "Who owns your work? Portfolio rights?", tags: ["Work-for-hire", "Portfolio", "Assignment"] },
  { icon: AlertTriangle, name: "Non-Compete", key: "nc", question: "Can you work for competitors? For how long?", tags: ["Duration", "Scope", "Geography"] },
  { icon: Clock, name: "Termination", key: "term", question: "How can you exit? Notice period?", tags: ["Notice", "Auto-renewal", "Exit fees"] },
  { icon: Shield, name: "Indemnification", key: "indem", question: "Who covers legal costs if something goes wrong?", tags: ["Mutual", "One-sided", "Legal fees"] },
  { icon: Scale, name: "Liability Caps", key: "liab", question: "How much can you lose if something breaks?", tags: ["Cap amount", "Carve-outs", "Uncapped"] },
];

const BORDER_COLORS: Record<string, string> = {
  pay: "border-l-green-500",
  ip: "border-l-blue-500",
  nc: "border-l-red-500",
  term: "border-l-amber-500",
  indem: "border-l-orange-500",
  liab: "border-l-purple-500",
};

export default function DangerZones() {
  return (
    <section className="max-w-6xl mx-auto px-4 py-20">
      <div className="text-center mb-12">
        <span className="text-xs font-semibold tracking-widest uppercase text-brand-500 mb-3 block">
          What We Check
        </span>
        <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-4">
          6 danger zones. Zero surprises.
        </h2>
        <p className="text-gray-400 max-w-xl mx-auto">
          Every contract gets analyzed across these six areas. We flag what matters — not the boilerplate.
        </p>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-px bg-white/[0.06] border border-white/[0.06] rounded-xl overflow-hidden">
        {ZONES.map((z) => (
          <div
            key={z.key}
            className={`bg-surface p-6 border-l-[3px] ${BORDER_COLORS[z.key]} hover:bg-surface-hover transition cursor-default`}
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2.5">
                <z.icon size={16} className="text-gray-400" />
                <h3 className="font-bold text-white text-sm">{z.name}</h3>
              </div>
            </div>
            <p className="text-sm text-gray-400 italic mb-3">{z.question}</p>
            <div className="flex flex-wrap gap-1.5">
              {z.tags.map((t) => (
                <span key={t} className="text-[11px] text-gray-500 bg-white/[0.04] border border-white/[0.06] rounded px-2 py-0.5">
                  {t}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
