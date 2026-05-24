"use client";

import { useEffect, useState } from "react";
import Nav from "@/components/Nav";
import Hero from "@/components/Hero";
import DangerZones from "@/components/DangerZones";
import Pipeline from "@/components/Pipeline";
import Pricing from "@/components/Pricing";
import AuthModal from "@/components/AuthModal";

export default function Home() {
  const [authOpen, setAuthOpen] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);

    if (params.get("auth") === "signup" || params.get("auth") === "signin") {
      setAuthOpen(true);
      // Clean up URL without reload
      const url = new URL(window.location.href);
      url.searchParams.delete("auth");
      window.history.replaceState({}, "", url.toString());
    }

    if (params.get("scroll") === "pricing") {
      const el = document.getElementById("pricing");
      if (el) {
        el.scrollIntoView({ behavior: "smooth" });
      }
      const url = new URL(window.location.href);
      url.searchParams.delete("scroll");
      window.history.replaceState({}, "", url.toString());
    }
  }, []);

  return (
    <>
      <Nav />
      <Hero />
      <Pipeline />
      <DangerZones />
      <Pricing />
      <footer className="border-t border-white/[0.06] py-10 text-center text-xs text-gray-600">
        <div className="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <span>© 2026 ContractLens. Not legal advice.</span>
          <div className="flex gap-6">
            <a href="/tos" className="hover:text-gray-400 transition">Terms</a>
            <a href="/privacy" className="hover:text-gray-400 transition">Privacy</a>
            <a href="mailto:support@contractlens.io" className="hover:text-gray-400 transition">Contact</a>
          </div>
        </div>
      </footer>
      <AuthModal open={authOpen} onClose={() => setAuthOpen(false)} />
    </>
  );
}
