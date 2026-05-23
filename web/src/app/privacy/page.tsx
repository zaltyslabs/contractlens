import Nav from "@/components/Nav";

export default function PrivacyPage() {
  return (
    <>
      <Nav />
      <main className="max-w-2xl mx-auto px-4 py-16">
        <h1 className="text-3xl font-extrabold text-white mb-8">Privacy Policy</h1>
        <div className="prose prose-invert prose-sm max-w-none space-y-4 text-gray-300 leading-relaxed">
          <p><strong>Last updated:</strong> May 2026</p>
          <p>
            ContractLens (&quot;we&quot;, &quot;our&quot;, or &quot;us&quot;) is committed to protecting your privacy. This policy explains how we handle your data.
          </p>
          <h2 className="text-lg font-bold text-white mt-8 mb-3">1. Information We Collect</h2>
          <p>
            <strong>Account information:</strong> When you sign up, we collect your email address and authentication credentials via Supabase.<br />
            <strong>Contract files:</strong> When you upload a contract for analysis, the file is temporarily stored for processing.<br />
            <strong>Usage data:</strong> We track the number of scans you perform to enforce plan limits.
          </p>
          <h2 className="text-lg font-bold text-white mt-8 mb-3">2. How We Use Your Data</h2>
          <p>
            Contract files are processed solely for generating your analysis report. Files are automatically deleted after processing (typically within minutes). Extracted text is used only for the AI analysis and is not retained after the report is generated.
          </p>
          <h2 className="text-lg font-bold text-white mt-8 mb-3">3. Data Storage</h2>
          <p>
            Authentication data is stored by Supabase (our infrastructure provider). Contract files are processed on our secure servers and deleted after analysis. We do not maintain a permanent archive of your contracts.
          </p>
          <h2 className="text-lg font-bold text-white mt-8 mb-3">4. Third-Party Services</h2>
          <p>
            We use the following third-party services: Supabase (authentication and database), Stripe (payment processing), and an AI provider (contract analysis). Each of these services has its own privacy policy.
          </p>
          <h2 className="text-lg font-bold text-white mt-8 mb-3">5. Your Rights</h2>
          <p>
            You can delete your account at any time by contacting us. Upon deletion, your account data is removed from our systems within 30 days.
          </p>
          <h2 className="text-lg font-bold text-white mt-8 mb-3">6. Contact</h2>
          <p>
            Privacy questions? Contact us at <a href="mailto:support@contractlens.io" className="text-brand-500 hover:underline">support@contractlens.io</a>.
          </p>
        </div>
      </main>
    </>
  );
}
