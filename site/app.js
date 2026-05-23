// ContractLens — Shared Client
// Requires config.js to be loaded BEFORE this file

const supabaseClient = supabase.createClient(CONFIG.SUPABASE_URL, CONFIG.SUPABASE_ANON_KEY);

// ── Stripe ──
function subscribe(tier) {
  const url = CONFIG.STRIPE_LINKS[tier];
  if (!url) { showToast("Plan not available yet", "error"); return; }
  window.location.href = url;
}

// ── Auth helpers ──

async function signUp(email, password) {
  const { data, error } = await supabaseClient.auth.signUp({ email, password });
  if (error) throw error;
  return data;
}

async function signIn(email, password) {
  const { data, error } = await supabaseClient.auth.signInWithPassword({ email, password });
  if (error) throw error;
  return data;
}

async function signInMagicLink(email) {
  const { data, error } = await supabaseClient.auth.signInWithOtp({
    email,
    options: { emailRedirectTo: window.location.origin + "/dashboard.html" }
  });
  if (error) throw error;
  return data;
}

async function signOut() {
  await supabaseClient.auth.signOut();
  window.location.href = "/index.html";
}

async function getUser() {
  const { data: { user } } = await supabaseClient.auth.getUser();
  return user;
}

// ── UI helpers ──

function showEl(id) { const el = document.getElementById(id); if (el) el.classList.remove('hidden'); }
function hideEl(id) { const el = document.getElementById(id); if (el) el.classList.add('hidden'); }

function setHTML(id, html) {
  const el = document.getElementById(id);
  if (el) el.innerHTML = html;
}

function showToast(msg, type = 'success') {
  const toast = document.getElementById('toast') || (() => {
    const t = document.createElement('div');
    t.id = 'toast';
    t.style.cssText = 'position:fixed;bottom:2rem;right:2rem;padding:1rem 1.5rem;border-radius:10px;font-weight:600;z-index:9999;transition:opacity 0.3s;';
    document.body.appendChild(t);
    return t;
  })();
  const colors = { success: '#16a34a', error: '#dc2626', info: '#2563eb' };
  toast.style.background = colors[type] || colors.info;
  toast.style.color = '#fff';
  toast.textContent = msg;
  toast.style.opacity = '1';
  setTimeout(() => { toast.style.opacity = '0'; }, 4000);
}

// ── Auth state observer ──

let _authReady = false;
let _pageLoadTime = Date.now();

supabaseClient.auth.onAuthStateChange((event, session) => {
  // Ignore all events during the first 2 seconds (prevents navigation loops)
  const pageAge = Date.now() - _pageLoadTime;
  if (pageAge < 2000 && (event === 'SIGNED_IN' || event === 'INITIAL_SESSION')) {
    _authReady = !!session;
    return;
  }

  if (event === 'INITIAL_SESSION') {
    _authReady = true;
    return;
  }

  if (event === 'SIGNED_IN') {
    _authReady = true;
    if (!window.location.pathname.includes('dashboard')) {
      window.location.href = '/dashboard.html';
    }
  }

  if (event === 'SIGNED_OUT') {
    _authReady = false;
    if (!window.location.pathname.includes('index.html')) {
      window.location.href = '/index.html';
    }
  }
});
