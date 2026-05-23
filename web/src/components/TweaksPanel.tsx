"use client";

import { useEffect, useState } from "react";
import { Settings } from "lucide-react";
import type { Theme, Density, AccentColor } from "@/lib/types";

const ACCENTS: AccentColor[] = ["indigo", "purple", "rose", "emerald"];

const ACCENT_COLORS: Record<AccentColor, string> = {
  indigo: "#6366f1",
  purple: "#a855f7",
  rose: "#f43f5e",
  emerald: "#10b981",
};

export default function TweaksPanel() {
  const [open, setOpen] = useState(false);
  const [theme, setTheme] = useState<Theme>("dark");
  const [density, setDensity] = useState<Density>("comfortable");
  const [accent, setAccent] = useState<AccentColor>("indigo");

  useEffect(() => {
    const t = localStorage.getItem("cl-theme") as Theme | null;
    const d = localStorage.getItem("cl-density") as Density | null;
    const a = localStorage.getItem("cl-accent") as AccentColor | null;
    if (t) setTheme(t);
    if (d) setDensity(d);
    if (a) setAccent(a);
  }, []);

  useEffect(() => {
    document.documentElement.className = theme;
    localStorage.setItem("cl-theme", theme);
  }, [theme]);

  useEffect(() => {
    document.documentElement.style.setProperty("--accent", ACCENT_COLORS[accent]);
    localStorage.setItem("cl-accent", accent);
  }, [accent]);

  return (
    <>
      <button
        onClick={() => setOpen(!open)}
        className="fixed bottom-5 right-5 z-50 w-11 h-11 rounded-full bg-surface border border-white/[0.08] flex items-center justify-center text-gray-400 hover:text-white hover:border-white/[0.15] transition shadow-lg"
        aria-label="Tweaks"
      >
        <Settings size={18} />
      </button>

      {open && (
        <div className="fixed bottom-20 right-5 z-50 bg-surface border border-white/[0.08] rounded-xl p-5 w-56 shadow-2xl space-y-5">
          {/* Theme */}
          <div>
            <div className="text-[11px] font-semibold uppercase tracking-wider text-gray-500 mb-2">Theme</div>
            <div className="flex gap-1.5">
              {(["dark", "light"] as Theme[]).map((t) => (
                <button
                  key={t}
                  onClick={() => setTheme(t)}
                  className={`flex-1 py-1.5 rounded-lg text-xs font-medium transition ${
                    theme === t
                      ? "bg-brand-500 text-white"
                      : "bg-white/[0.04] text-gray-400 hover:text-white"
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          {/* Density */}
          <div>
            <div className="text-[11px] font-semibold uppercase tracking-wider text-gray-500 mb-2">Density</div>
            <div className="flex gap-1.5">
              {(["comfortable", "compact"] as Density[]).map((d) => (
                <button
                  key={d}
                  onClick={() => setDensity(d)}
                  className={`flex-1 py-1.5 rounded-lg text-xs font-medium transition ${
                    density === d
                      ? "bg-brand-500 text-white"
                      : "bg-white/[0.04] text-gray-400 hover:text-white"
                  }`}
                >
                  {d}
                </button>
              ))}
            </div>
          </div>

          {/* Accent */}
          <div>
            <div className="text-[11px] font-semibold uppercase tracking-wider text-gray-500 mb-2">Accent</div>
            <div className="flex gap-1.5">
              {ACCENTS.map((a) => (
                <button
                  key={a}
                  onClick={() => setAccent(a)}
                  className={`w-9 h-9 rounded-lg transition ${
                    accent === a ? "ring-2 ring-white ring-offset-2 ring-offset-surface" : ""
                  }`}
                  style={{ backgroundColor: ACCENT_COLORS[a] }}
                  aria-label={a}
                />
              ))}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
