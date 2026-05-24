import { Upload, Search, Monitor } from "lucide-react";

const STEPS = [
  { icon: Upload, title: "Upload", desc: "Drop your PDF, DOCX, or TXT file. We extract the text locally and securely." },
  { icon: Search, title: "Analyze", desc: "Our AI reads every clause across 6 danger zones. Plain English, no legalese." },
  { icon: Monitor, title: "View Report", desc: "Your report appears instantly. Interactive, color-coded, ready to act on." },
];

export default function Pipeline() {
  return (
    <section className="max-w-6xl mx-auto px-4 py-20 border-t border-white/[0.06]">
      <div className="text-center mb-14">
        <span className="text-xs font-semibold tracking-widest uppercase text-brand-500 mb-3 block">
          How It Works
        </span>
        <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          Three steps to clarity
        </h2>
      </div>

      <div className="grid sm:grid-cols-3 gap-0 relative">
        {/* Connector line — desktop only */}
        <div className="hidden sm:block absolute top-8 left-[16%] right-[16%] h-px bg-white/[0.08]" />

        {STEPS.map((s, i) => (
          <div key={i} className="relative z-10 text-center px-4">
            <div className="w-16 h-16 rounded-full bg-surface border border-white/[0.08] flex items-center justify-center mx-auto mb-5">
              <s.icon size={22} className="text-brand-500" />
            </div>
            <span className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-2 block">
              Step {i + 1}
            </span>
            <h3 className="text-lg font-bold text-white mb-2">{s.title}</h3>
            <p className="text-sm text-gray-400 leading-relaxed">{s.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
