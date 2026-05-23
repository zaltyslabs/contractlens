// ContractLens Configuration — copy this to config.js and fill in real values
// NEVER commit config.js to git!

const CONFIG = {
  // Supabase (public keys — from Supabase Dashboard > Settings > API)
  SUPABASE_URL: "https://YOUR_PROJECT.supabase.co",
  SUPABASE_ANON_KEY: "sb_publishable_YOUR_KEY",

  // Stripe (public key — from Stripe Dashboard > Developers > API keys)
  STRIPE_PK: "pk_test_YOUR_KEY",

  // Stripe Payment Links (created via Stripe Dashboard or API)
  STRIPE_LINKS: {
    side_hustler:     "https://buy.stripe.com/test_XXXX",
    power_freelancer: "https://buy.stripe.com/test_XXXX",
    agency:           "https://buy.stripe.com/test_XXXX",
  }
};
