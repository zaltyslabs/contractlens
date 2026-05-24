"use client";

import Link from "next/link";
import { useAuth } from "./AuthProvider";
import { useState } from "react";
import { Menu, X, ChevronDown } from "lucide-react";

export default function Nav() {
  const { user, signOut } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <nav className="sticky top-0 z-50 border-b border-white/[0.07] bg-gray-950/80 backdrop-blur-xl">
      <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between gap-4">
        <Link href="/" className="flex items-center gap-2.5 text-base font-bold text-white tracking-tight">
          📋 ContractLens
        </Link>

        {/* Desktop */}
        <div className="hidden sm:flex items-center gap-2">
          {user ? (
            <>
              <Link
                href="/dashboard"
                className="text-sm text-gray-400 hover:text-white transition px-3 py-2 rounded-lg hover:bg-white/[0.04]"
              >
                Dashboard
              </Link>
              <button
                onClick={signOut}
                className="text-sm text-gray-400 hover:text-white transition px-3 py-2 rounded-lg hover:bg-white/[0.04]"
              >
                Sign Out
              </button>
            </>
          ) : (
            <Link
              href="/dashboard?signup=true"
              className="px-4 py-2 rounded-lg text-sm font-semibold text-white bg-brand-500 hover:bg-brand-600 transition"
            >
              Get Started Free
            </Link>
          )}
        </div>

        {/* Mobile */}
        <button
          className="sm:hidden p-2 text-gray-400"
          onClick={() => setMobileOpen(!mobileOpen)}
          aria-label="Menu"
        >
          {mobileOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {mobileOpen && (
        <div className="sm:hidden border-t border-white/[0.07] px-4 py-3 flex flex-col gap-2 bg-gray-950">
          {user ? (
            <>
              <Link
                href="/dashboard"
                className="text-sm text-gray-300 py-2"
                onClick={() => setMobileOpen(false)}
              >
                Dashboard
              </Link>
              <button
                onClick={() => { signOut(); setMobileOpen(false); }}
                className="text-sm text-gray-400 py-2 text-left"
              >
                Sign Out
              </button>
            </>
          ) : (
            <Link
              href="/dashboard?signup=true"
              className="text-sm font-semibold text-brand-500 py-2"
              onClick={() => setMobileOpen(false)}
            >
              Get Started Free
            </Link>
          )}
        </div>
      )}
    </nav>
  );
}
