# ContractLens UGC & Distribution Strategy

> Created: 2026-05-24 | Status: planning

---

## TL;DR

No paid ads yet. You don't know CAC/LTV, conversion rates, or even if the product resonates. Paid ads at this stage = burning cash to learn things you could learn for free. The play: **free tier as distribution channel + build-in-public + SEO**.

---

## UGC Strategy: 3 Phases

### Phase 1: Producer-Generated Content (Now — $0 revenue)

You create all the content. This isn't "UGC" in the traditional sense — it's you showing the product's value through real demonstrations, not marketing fluff.

| Channel | Content Type | Frequency | Goal |
|---------|-------------|-----------|------|
| **X/Twitter** | Build-in-public threads, contract red flag breakdowns | 3-5x/week | Top-of-funnel awareness |
| **Reddit** | Value posts in r/freelance, r/Upwork, r/contracts | 1-2x/week | Targeted niche reach |
| **Indie Hackers** | Product launch, milestone posts, revenue updates | 1x/week (milestones) | Peer validation, early adopters |
| **Blog (site)** | SEO articles: "NDA red flags freelancers miss", "How to read a contractor agreement", etc. | 1x/week | Long-tail search traffic |
| **GitHub** | README polish, changelog, open-source the pipeline? | As shipped | Technical credibility |

### Phase 2: Early Adopter Testimonials ($0-$500 MRR)

First 10-20 users. Incentivize feedback with free scans or extended trials. Turn their real words into content.

| Source | How to get it | Format |
|--------|--------------|--------|
| First free scan users | Post-scan email: "Was this useful? Reply with one sentence." | Quote card for landing page |
| Power users (3+ scans) | Personal email asking for a 2-min Loom video | Video testimonial |
| Reddit/IH commenters | Screenshot positive comments | Social proof collage |
| Twitter DMs | DM anyone who engages: "Can I quote you?" | Quote tweet |

### Phase 3: Organic UGC ($500-$5K MRR)

Paying users create content without being asked. This only happens when the product is genuinely useful and users want to share.

| Triggers | Expected Content |
|----------|-----------------|
| User catches a bad clause that would've cost them $ | Tweet/Reddit post: "ContractLens just saved me..." |
| Agency owner scans 10+ contracts/month | LinkedIn recommendation |
| Freelancer community word-of-mouth | Mentioned in freelance Slack/Discord communities |

---

## Content Calendar: Phase 1 (First 30 Days)

### X/Twitter Content (3-5x/week)

**Thread 1: Build-in-Public Launch**
```
Day 1: "I'm building ContractLens — an AI that reads contracts so freelancers don't get screwed. Here's why:"
  → Stats on how many freelancers sign bad contracts
  → My own story of signing a bad NDA as a freelancer
  → What ContractLens does (problem → solution)
  → Screenshot of the tool analyzing a real contract
  → Call to action: "First scan is free. Link in bio."

Day 3: "Just ran a real Upwork contract through ContractLens. Here's what it found:"
  → Screenshot of the report (anonymized)
  → Highlight the 3 worst clauses
  → "A lawyer would charge $300-800 to tell you this."

Day 5: "Building the landing page. Here's the design..."
  → Screenshot of landing page
  → Ask for feedback
  → Transparency builds trust

Day 7: "First paying customer. $12/mo. Here's how it happened:"
  → Story of how they found it
  → What they needed
  → Revenue milestone

Day 10: "The tech stack behind ContractLens:"
  → Python, PyMuPDF, Supabase, Stripe
  → Why no framework
  → Total cost to build: $X

Day 14: "5 contract clauses every freelancer should reject:"
  → Educational thread (high engagement potential)
  → Each clause: what it says, what it means, why it's bad
  → "ContractLens catches all of these automatically."
```

**Ongoing posts (2-3x/week):**
- Screenshots of interesting report sections
- User feedback quotes
- New feature announcements
- Competitor comparisons (honest, not bitter)
- Freelancer contract horror stories (from Reddit, anonymized)
- Revenue milestone updates

### Reddit Content (1-2x/week)

**Rules:** Reddit hates self-promotion. Add value first, mention ContractLens as a sidenote.

**Subreddits:**
- r/freelance (primary — 500K+ members)
- r/Upwork
- r/contracts
- r/smallbusiness
- r/SaaS (milestone posts only)

**Post templates:**

```
Title: "PSA: 5 red flags in freelance contracts that cost me $15K"

Body: [Detailed breakdown of 5 real clauses, what they mean, what happened]

Last paragraph: "I got tired of this and built a tool that scans contracts for this stuff automatically. 
Called ContractLens — first scan is free if you want to try it. Not linking directly to avoid self-promo, 
but it's in my profile."
```

```
Title: "Just had an Upwork client try to sneak a 2-year non-compete into a $500 project"

Body: [Story, clause quote, why it's insane, what you did about it]

Comment replies: When people ask "how do I check for this?" → mention ContractLens naturally.
```

### Blog Content (1x/week — SEO-focused)

**Target keywords (long-tail, low competition):**
- "non compete clause in freelance contract red flags"
- "how to review a contractor agreement as a freelancer"
- "indemnification clause explained freelancers"
- "intellectual property ownership freelance contract"
- "termination clause freelance contract notice period"
- "liability cap freelancer contract"
- "NDA red flags freelancers"
- "AI contract review freelancer"

**Article structure:**
1. Target keyword in title and H1
2. Personal story or real example (200 words)
3. Break down the clause type (plain English, no legal jargon)
4. Show examples of bad vs acceptable clauses
5. How ContractLens helps (subtle CTA, not aggressive)
6. FAQ section (snag featured snippets)

### Indie Hackers (1x/week — milestone posts)

- Product launch post
- "First $100 MRR" post
- "My stack: Python + vanilla JS + Supabase" post
- Revenue update posts (even $0 — honesty builds following)
- "What I learned shipping in 2 weeks" post

---

## Where to Upload Content

| Content Type | Tool | Upload Method |
|-------------|------|---------------|
| Blog posts | `site/blog/` directory + Markdown | Write locally, push to GitHub, deploy to Vercel |
| X/Twitter posts | `xurl` CLI | Need to set up first: `xurl auth apps add` + `xurl auth oauth2` |
| Reddit posts | Manual (or automation later) | Browser — DON'T automate, Reddit will ban you |
| Indie Hackers | Manual | Browser |
| Landing page updates | `claude-design` skill or Claude Code | Delegate to Claude Code, push to GitHub |
| Email newsletters | SMTP via `src/emailer.py` | Extend pipeline to send marketing emails |

### Blog Setup (Minimal)

```
site/blog/
├── index.html          (blog listing page)
├── post-template.html   (reusable template)
├── 2026-05-28-nda-red-flags.html
├── 2026-06-04-non-compete-guide.html
└── ...
```

Add `<link rel="canonical">` tags for SEO. Add `<meta name="description">` for each post. Use semantic HTML — `<article>`, `<h1>-<h6>`, `<time>`.

---

## Do We Need Paid Ads?

**No. Not yet. Here's the math:**

Paid ads only make sense when:
1. **You know your CAC** — how much does it cost to acquire a paying customer?
2. **You know your LTV** — how much revenue does a customer generate over their lifetime?
3. **LTV > 3x CAC** — the basic SaaS viability threshold
4. **Your conversion funnel works** — free → signup → scan → paid conversion rates are measured

At ContractLens's stage:
- No conversion data
- No churn data
- No LTV data
- No organic traffic baseline

**Running ads now = data you can't interpret + money you won't recover.**

### When to start considering ads:

| Milestone | Action |
|-----------|--------|
| 50 paying customers | Calculate CAC from organic/word-of-mouth |
| 3+ months retention data | Calculate LTV |
| Conversion funnel measured | Know free→paid % |
| $500+ MRR | Can fund $100-200/mo ad experiments |

### First ad channels (when ready):
1. **Google Ads** — target "contract review for freelancers" keywords (high intent)
2. **Reddit Ads** — target r/freelance specifically
3. **X/Twitter Ads** — promote viral threads that already perform well organically

### What NOT to do:
- Facebook/Instagram ads (wrong demographic for B2B tool)
- TikTok ads (same issue)
- LinkedIn ads (too expensive at $5-10 CPC for unproven product)
- Any ad channel where you can't target "freelancer + signing a contract soon"

---

## Tools & Setup Required

| Tool | Status | Action |
|------|--------|--------|
| `xurl` (X/Twitter) | Not configured | Install + OAuth setup (manual, user must do) |
| Blog infrastructure | Not built | Create `site/blog/` with index + template |
| SEO meta tags | Partially done | Audit landing page meta tags |
| Google Search Console | Not set up | Add site, submit sitemap |
| Analytics (privacy-friendly) | Not set up | Plausible or Umami (self-hosted, no cookie banner needed) |
| Email capture | Not done | Add email signup to landing page (ConvertKit free tier or MailerLite) |
| Reddit account | Check | Needs a dedicated account? |
| Product Hunt upcoming page | Not created | Create when 1-2 weeks from launch |

---

## Immediate Next Actions (This Week)

1. **Set up X/Twitter** — `xurl` installation + OAuth (user runs this, then we can post from Hermes)
2. **Write 3 blog posts** — NDA red flags, non-compete guide, payment terms breakdown
3. **Create blog infrastructure** — `site/blog/index.html` + first post template
4. **Audit landing page SEO** — title tags, meta descriptions, schema markup
5. **Build-in-public thread #1** — write and queue the launch thread
6. **Set up email capture** — ConvertKit free tier or just a Google Form for now
7. **Post on Indie Hackers** — product intro post

---

## KPIs to Track (30/60/90 Days)

| KPI | 30 Days | 60 Days | 90 Days |
|-----|---------|---------|---------|
| Twitter followers | 100 | 300 | 500 |
| Blog organic traffic | 10/week | 50/week | 200/week |
| Email subscribers | 20 | 100 | 300 |
| Free scans run | 30 | 100 | 300 |
| Paying customers | 5 | 15 | 30 |
| MRR | $60 | $200 | $500 |
| Reddit post upvotes (avg) | 20 | 50 | 100 |

---

## Anti-Patterns to Avoid

- **"Follow for more"** — no one cares. End threads with value, not begging.
- **"Link in bio"** when the link doesn't work — test everything before posting.
- **Posting and ghosting** — reply to EVERY comment. Engagement drives reach.
- **Overpolished content** — raw screenshots with arrows beat designed graphics.
- **Hiding the product** — show the actual tool, actual reports, actual UI. No mockups.
- **Waiting for "perfect"** — ship the blog with 1 post. Add more later.
- **Buying followers/engagement** — kills your algorithmic reach permanently.
