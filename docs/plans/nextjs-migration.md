# Next.js Frontend Migration — Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Replace the vanilla HTML/JS frontend with a Next.js 14+ TypeScript app, keeping the Python/FastAPI backend unchanged.

**Architecture:** Next.js App Router with server components for static pages and client components for interactive features (auth, upload, dashboard). Communicates with existing FastAPI backend at `https://contractlens-zi1v.onrender.com`. Supabase handles auth only — all business logic stays in Python.

**Tech Stack:** Next.js 14, TypeScript, Tailwind CSS 3, Supabase JS client, React Hook Form + Zod, shadcn/ui (optional).

**Key principle:** Backend is untouchable. The Python API at `/api/upload` and `/api/health` stays exactly as-is. We're only rebuilding the presentation layer.

---

## File Structure (target)

```
contractlens/
├── backend/              ← UNCHANGED (Python/FastAPI)
├── frontend-old/         ← renamed from frontend/ (keep for reference)
├── web/                  ← NEW Next.js app
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx          ← root layout (nav, providers)
│   │   │   ├── page.tsx            ← landing page
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx        ← dashboard (protected)
│   │   │   ├── tos/
│   │   │   │   └── page.tsx        ← terms (static)
│   │   │   └── privacy/
│   │   │       └── page.tsx        ← privacy (static)
│   │   ├── components/
│   │   │   ├── Nav.tsx             ← sticky nav with auth state
│   │   │   ├── Hero.tsx            ← landing hero + analysis preview
│   │   │   ├── DangerZones.tsx     ← 6-zone grid
│   │   │   ├── Pricing.tsx         ← 4-tier pricing
│   │   │   ├── Pipeline.tsx        ← 1→2→3 steps
│   │   │   ├── AuthModal.tsx       ← sign in/up modal
│   │   │   ├── UploadZone.tsx      ← drag-drop upload
│   │   │   ├── ScanHistory.tsx     ← scan list
│   │   │   ├── UsageRing.tsx       ← SVG usage ring
│   │   │   ├── ReportModal.tsx     ← report viewer
│   │   │   └── TweaksPanel.tsx     ← theme/density/accent
│   │   ├── lib/
│   │   │   ├── api.ts              ← backend API client
│   │   │   ├── supabase.ts         ← Supabase client
│   │   │   └── types.ts            ← shared TypeScript types
│   │   └── styles/
│   │       └── globals.css         ← Tailwind + design tokens
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── next.config.js
│   └── package.json
├── supabase/              ← UNCHANGED
├── docs/                  ← UNCHANGED
├── Project.md             ← UPDATE with web/ structure
└── render.yaml            ← UNCHANGED
```

---

## Design System (carried over)

```css
/* Design tokens — same as current frontend */
--accent:       #6366f1 (indigo)
--accent-alt-1: #a855f7 (purple)
--accent-alt-2: #ec4899 (rose)
--bg:           #030712 (dark) / #ffffff (light)
--surf:         #0d1117 (dark) / #f6f8fa (light)
--high:         #ef4444 (red)
--med:          #f59e0b (amber)
--low:          #22c55e (green)
```

---

## Tasks

### Task 1: Scaffold Next.js app

**Objective:** Create the Next.js project with TypeScript and Tailwind

**Files:**
- Create: `web/` directory via `create-next-app`

**Step 1: Run scaffolding**

```bash
cd /Users/justasza/contractlens
npx create-next-app@latest web --typescript --tailwind --eslint --app --src-dir --no-import-alias
```

**Step 2: Install additional dependencies**

```bash
cd web
npm install @supabase/supabase-js @hookform/resolvers zod react-hook-form lucide-react
```

**Step 3: Configure Tailwind with design tokens**

```typescript
// web/tailwind.config.ts
import type { Config } from "tailwindcss"

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        brand: {
          50:  "#eef2ff",
          100: "#e0e7ff",
          500: "#6366f1",
          600: "#4f46e5",
          700: "#4338ca",
        },
        surface: {
          DEFAULT: "#0d1117",
          hover:   "#161b22",
          border:  "rgba(255,255,255,0.07)",
        },
        risk: {
          high:   "#ef4444",
          medium: "#f59e0b",
          low:    "#22c55e",
        },
      },
    },
  },
  plugins: [],
}
export default config
```

**Step 4: Add global CSS with design tokens**

```css
/* web/src/styles/globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --accent:       #6366f1;
  --accent-hover: #4f46e5;
  --accent-dim:   rgba(99,102,241,0.12);
  --accent-glow:  rgba(99,102,241,0.25);
  --accent-text:  #818cf8;
}

.gradient-text {
  background: linear-gradient(135deg, #6366f1, #a855f7, #ec4899);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
```

**Step 5: Verify**

```bash
cd web && npm run dev
# Open http://localhost:3000 — should show Next.js default page
```

**Step 6: Commit**

```bash
git add web/
git commit -m "feat: scaffold Next.js app with TypeScript and Tailwind"
```

---

### Task 2: Create TypeScript types and API client

**Objective:** Define shared types matching the backend response + typed API client

**Files:**
- Create: `web/src/lib/types.ts`
- Create: `web/src/lib/api.ts`

**Step 1: Define backend response types**

```typescript
// web/src/lib/types.ts

export interface ContractZone {
  risk: "low" | "medium" | "high";
  summary: string;
}

export interface UploadResponse {
  success: boolean;
  risk: "low" | "medium" | "high";
  zones: Record<string, ContractZone>;
  report_url: string;
  recommendations: string[];
  emailed: boolean;
  metadata: {
    title: string;
    page_estimate: number;
    char_count: number;
  };
}

export interface PricingTier {
  name: string;
  price: number;
  scans: number;
  features: string[];
  popular?: boolean;
  stripeKey: "side_hustler" | "power_freelancer" | "agency";
}

export interface ScanRecord {
  id: string;
  filename: string;
  date: string;
  risk: "low" | "medium" | "high" | "pending";
  status: "pending" | "processing" | "done" | "failed";
  reportData?: UploadResponse;
}

export type AccentColor = "indigo" | "purple" | "rose" | "emerald";
export type Density = "comfortable" | "compact";
```

**Step 2: Create typed API client**

```typescript
// web/src/lib/api.ts

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8123";

export async function uploadContract(
  file: File,
  email: string,
  userId?: string
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("email", email);
  if (userId) formData.append("user_id", userId);

  const res = await fetch(`${API_URL}/api/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Upload failed");
  }

  return res.json();
}

export async function healthCheck(): Promise<{ status: string; version: string }> {
  const res = await fetch(`${API_URL}/api/health`);
  return res.json();
}
```

**Step 3: Verify**

```bash
# The types file should have zero TypeScript errors
cd web && npx tsc --noEmit
```

**Step 4: Commit**

```bash
git add web/src/lib/
git commit -m "feat: add TypeScript types and API client"
```

---

### Task 3: Build Supabase auth provider

**Objective:** Create Supabase client + React context for auth state

**Files:**
- Create: `web/src/lib/supabase.ts`
- Create: `web/src/components/AuthProvider.tsx`

**Step 1: Supabase client**

```typescript
// web/src/lib/supabase.ts
import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
```

**Step 2: Auth context provider**

Create `AuthProvider.tsx` — wraps the app, provides `user`, `signIn`, `signUp`, `signOut`, `loading`.

**Step 3: Add env vars to `.env.local`**

```
NEXT_PUBLIC_SUPABASE_URL=https://twqrvznvedfbzobutwcb.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=sb_publishable_QrEmI14c8K4p0XanRlbX3A_HygK_dM1
NEXT_PUBLIC_API_URL=https://contractlens-zi1v.onrender.com
```

**Step 4: Verify**

```bash
cd web && npm run dev
# Open browser console — Supabase client should initialize without errors
```

**Step 5: Commit**

```bash
git add web/src/lib/supabase.ts web/src/components/AuthProvider.tsx web/.env.example
git commit -m "feat: add Supabase auth provider and client"
```

---

### Task 4: Root layout with nav

**Objective:** Build the root layout with sticky nav and auth state

**Files:**
- Modify: `web/src/app/layout.tsx`
- Create: `web/src/components/Nav.tsx`

**Step 1: Root layout**

```tsx
// web/src/app/layout.tsx
import type { Metadata } from "next"
import { AuthProvider } from "@/components/AuthProvider"
import Nav from "@/components/Nav"
import "@/styles/globals.css"

export const metadata: Metadata = {
  title: "ContractLens — Understand Every Contract You Sign",
  description: "AI-powered contract analysis for freelancers",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="bg-gray-950 text-gray-200 min-h-screen antialiased">
        <AuthProvider>
          <Nav />
          {children}
        </AuthProvider>
      </body>
    </html>
  )
}
```

**Step 2: Nav component**

Sticky, transparent bg with backdrop-blur. Shows logo, Sign In / Dashboard (based on auth state), Sign Out.

**Step 3: Verify**

```bash
cd web && npm run dev
# Landing page at localhost:3000 should show nav bar
```

**Step 4: Commit**

```bash
git add web/src/app/layout.tsx web/src/components/Nav.tsx
git commit -m "feat: add root layout with sticky nav and auth state"
```

---

### Task 5: Landing page (Hero + Danger Zones + Pipeline + Pricing)

**Objective:** Build the landing page with all sections

**Files:**
- Create: `web/src/app/page.tsx`
- Create: `web/src/components/Hero.tsx`
- Create: `web/src/components/DangerZones.tsx`
- Create: `web/src/components/Pipeline.tsx`
- Create: `web/src/components/Pricing.tsx`

**Sections to build (in order):**
1. **Hero** — gradient headline ("Understand Every Contract You Sign"), value prop, CTA, live analysis preview card with 6 zones
2. **Pipeline** — 3-step visual: Upload → Analyze → Get Report
3. **Danger Zones** — 2-column grid, each card has icon, risk color left border, description
4. **Pricing** — 4-tier grid, "Popular" badge on Side Hustler, per-scan cost
5. **Footer** — logo, links (TOS, Privacy, Contact)

Use the actual copy from the current `frontend/index.html`. No placeholder text.

**Step 5: Verify**

```bash
cd web && npm run dev
# Landing page should match the current design but cleaner
```

**Step 6: Commit**

```bash
git add web/src/app/page.tsx web/src/components/Hero.tsx web/src/components/DangerZones.tsx web/src/components/Pipeline.tsx web/src/components/Pricing.tsx
git commit -m "feat: build landing page with hero, zones, pipeline, pricing"
```

---

### Task 6: Dashboard page (protected)

**Objective:** Build the authenticated dashboard with upload, history, and usage

**Files:**
- Create: `web/src/app/dashboard/page.tsx`
- Create: `web/src/components/UploadZone.tsx`
- Create: `web/src/components/ScanHistory.tsx`
- Create: `web/src/components/UsageRing.tsx`

**Dashboard layout:** 2-column (sidebar + main). Sidebar: usage ring, plan badge, upgrade CTA. Main: upload zone, scan history list with risk indicators.

**Upload flow:**
1. User drags/drops or clicks to select file
2. Shows loading state: "Extracting text…" → "Checking 6 danger zones…" → "Generating report…"
3. Calls `uploadContract()` from `api.ts`
4. Shows result or error toast
5. Refreshes scan history

**Step 5: Verify**

```bash
cd web && npm run dev
# Sign in, navigate to /dashboard — should show upload zone and empty history
```

**Step 6: Commit**

```bash
git add web/src/app/dashboard/ web/src/components/UploadZone.tsx web/src/components/ScanHistory.tsx web/src/components/UsageRing.tsx
git commit -m "feat: build dashboard with upload, history, and usage ring"
```

---

### Task 7: Auth modal

**Objective:** Build sign in / sign up modal with Supabase

**Files:**
- Create: `web/src/components/AuthModal.tsx`

**Features:**
- Toggle between Sign In and Sign Up modes
- Email + password fields with validation (Zod)
- Error and success states
- Magic link option
- Calls actual Supabase auth functions

**Step 3: Verify**

```bash
# Sign up a test user through the modal → should redirect to dashboard
# Sign in with existing user → should redirect to dashboard
```

**Step 4: Commit**

```bash
git add web/src/components/AuthModal.tsx
git commit -m "feat: add auth modal with sign in/up and magic link"
```

---

### Task 8: Report modal

**Objective:** Build the analysis report viewer

**Files:**
- Create: `web/src/components/ReportModal.tsx`

**Features:**
- Overall risk badge at top
- 3×2 scoreboard grid (zone name + risk badge + finding summary)
- Numbered recommended actions
- Disclaimer footer
- Close on Escape or backdrop click

**Step 3: Verify**

```bash
# Upload a contract → click "View" on a completed scan → report modal opens
```

**Step 4: Commit**

```bash
git add web/src/components/ReportModal.tsx
git commit -m "feat: add report viewer modal with scoreboard and actions"
```

---

### Task 9: Tweaks panel

**Objective:** Build the design customization panel from the redesign artifact

**Files:**
- Create: `web/src/components/TweaksPanel.tsx`

**Controls:**
- Theme: dark / light
- Density: comfortable / compact  
- Accent: indigo / purple / rose / emerald
- Persist preferences in localStorage

**Step 3: Verify**

```bash
# Click gear icon → panel opens → change theme → page updates
# Refresh → preferences persist
```

**Step 4: Commit**

```bash
git add web/src/components/TweaksPanel.tsx
git commit -m "feat: add tweaks panel with theme, density, and accent controls"
```

---

### Task 10: Static pages + final polish

**Objective:** Add TOS, privacy pages, rename old frontend, update docs

**Files:**
- Create: `web/src/app/tos/page.tsx`
- Create: `web/src/app/privacy/page.tsx`
- Modify: `Project.md` (update structure)
- Rename: `frontend/` → `frontend-old/`

**Step 4: Verify full app**

```bash
cd web && npm run build
# Should build without errors
npm run dev
# Manual QA:
# - Landing page renders
# - Sign up works
# - Dashboard shows after auth
# - Upload triggers API call
# - Report modal works
# - Tweaks panel works
# - TOS and privacy pages render
# - Mobile responsive at 375px width
```

**Step 5: Commit**

```bash
git add web/src/app/tos/ web/src/app/privacy/ Project.md
git mv frontend frontend-old
git commit -m "feat: add static pages, rename old frontend, finalize migration"
```

---

## Migration Checklist

- [ ] Next.js app builds without errors (`npm run build`)
- [ ] Landing page matches current design quality
- [ ] Auth flow works (sign up → dashboard, sign in, sign out)
- [ ] Upload calls real backend and displays results
- [ ] Report modal shows all 6 danger zones
- [ ] Tweaks panel persists preferences
- [ ] Mobile responsive (test at 375px)
- [ ] TOS and privacy pages accessible without auth
- [ ] Old `frontend/` renamed to `frontend-old/` for reference
- [ ] `Project.md` updated with new structure
- [ ] Environment variables documented in `.env.example`

---

## What Stays Unchanged

- `backend/` — Python/FastAPI, zero changes
- `supabase/` — schema, edge functions, zero changes
- `render.yaml` — still deploys backend from `backend/`
- `docs/plans/` — existing plans preserved

---

## Deployment

**Frontend (Next.js):** Deploy to Vercel (free) or Hostinger. 
```bash
cd web && npm run build
# Deploy the `.next/` output
```

**Backend (Python):** Already deployed at `https://contractlens-zi1v.onrender.com` — no changes needed.
