"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";
import Nav from "@/components/Nav";
import UploadZone from "@/components/UploadZone";
import ScanHistory from "@/components/ScanHistory";
import UsageRing from "@/components/UsageRing";
import { ScanRecord } from "@/lib/types";
import { getUsage } from "@/lib/api";

export default function DashboardPage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [scans, setScans] = useState<ScanRecord[]>([]);
  const [usage, setUsage] = useState({
    scans_used_this_month: 0,
    scans_limit: 5,
    subscription_tier: "free",
    can_scan: true,
  });

  // Fetch server-authoritative usage
  async function refreshUsage() {
    if (!user?.id) return;
    const u = await getUsage(user.id);
    setUsage(u);
  }

  useEffect(() => {
    if (!loading && !user) {
      const params = new URLSearchParams(window.location.search);
      if (params.get("signup") === "true") {
        router.push("/?auth=signup");
      } else {
        router.push("/");
      }
    }
  }, [user, loading, router]);

  // Fetch usage on mount
  useEffect(() => {
    if (user?.id) refreshUsage();
  }, [user?.id]);

  useEffect(() => {
    const stored = localStorage.getItem("contractlens_scans");
    if (stored) {
      try {
        setScans(JSON.parse(stored));
      } catch {}
    }
  }, []);

  function handleUploadComplete() {
    const stored = localStorage.getItem("contractlens_scans");
    if (stored) {
      try {
        setScans(JSON.parse(stored));
      } catch {}
    }
    refreshUsage();
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-brand-500/30 border-t-brand-500 rounded-full animate-spin" />
      </div>
    );
  }

  if (!user) return null;

  const scansRemaining = usage.scans_limit - usage.scans_used_this_month;

  return (
    <div className="min-h-screen">
      <Nav />
      <div className="max-w-6xl mx-auto px-4 py-8 grid lg:grid-cols-[280px_1fr] gap-6 items-start">
        {/* Sidebar */}
        <aside className="flex flex-col gap-4">
          <UsageRing used={usage.scans_used_this_month} limit={usage.scans_limit} />
          <div className="bg-surface border border-white/[0.07] rounded-xl p-5">
            <div className="text-sm font-bold text-white mb-1">Side Hustler</div>
            <div className="text-xs text-gray-500 mb-3">5 scans/month</div>
            <button
              onClick={() => router.push("/?scroll=pricing")}
              className="w-full py-2 rounded-lg text-xs font-semibold border border-white/[0.1] text-gray-300 hover:bg-white/[0.04] transition"
            >
              Upgrade plan
            </button>
          </div>
        </aside>

        {/* Main */}
        <main className="flex flex-col gap-6">
          <UploadZone onComplete={handleUploadComplete} email={user?.email || ""} userId={user?.id} canScan={usage.can_scan} scansRemaining={scansRemaining} />
          <ScanHistory scans={scans} />
        </main>
      </div>
    </div>
  );
}
