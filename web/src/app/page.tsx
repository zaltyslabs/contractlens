import Nav from "@/components/Nav";
import Hero from "@/components/Hero";
import DangerZones from "@/components/DangerZones";
import Pipeline from "@/components/Pipeline";
import Pricing from "@/components/Pricing";

export default function Home() {
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
    </>
  );
}
