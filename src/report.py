"""Generate HTML reports from contract analysis results.

Produces a card-based, glanceable report that works in both
light and dark email clients via CSS custom properties.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

RISK_COLORS = {
    "low": "#22c55e",
    "medium": "#f59e0b",
    "high": "#ef4444",
    "unknown": "#6b7280",
}

RISK_EMOJI = {
    "low": "🟢",
    "medium": "🟡",
    "high": "🔴",
    "unknown": "⚪",
}

ZONE_NAMES = {
    "payment_terms": ("💰", "Payment Terms"),
    "ip_ownership": ("🔒", "IP & Ownership"),
    "non_compete": ("🚫", "Non-Compete"),
    "termination": ("⏰", "Termination"),
    "indemnification": ("🛡️", "Indemnification"),
    "liability_caps": ("⚖️", "Liability Caps"),
}

# ── Shared CSS ─────────────────────────────────────────────────────────────

CSS = """
  :root {
    --bg: #ffffff;
    --surface: #f8fafc;
    --surface-hover: #f1f5f9;
    --text: #1e293b;
    --text-heading: #0f172a;
    --text-muted: #64748b;
    --border: #e2e8f0;
    --clause-bg: #f1f5f9;
    --clause-text: #475569;
    --footer-text: #94a3b8;
    --disclaimer-bg: #fef2f2;
    --disclaimer-border: #fecaca;
    --disclaimer-text: #991b1b;
    --score-bg: #e2e8f0;
    --card-shadow: 0 1px 3px rgba(0,0,0,0.06);
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #0b1120;
      --surface: #111827;
      --surface-hover: #1a2332;
      --text: #d1d5db;
      --text-heading: #f3f4f6;
      --text-muted: #9ca3af;
      --border: #1f2937;
      --clause-bg: #0f172a;
      --clause-text: #9ca3af;
      --footer-text: #6b7280;
      --disclaimer-bg: #3b1010;
      --disclaimer-border: #5c1a1a;
      --disclaimer-text: #fca5a5;
      --score-bg: #1f2937;
      --card-shadow: 0 1px 3px rgba(0,0,0,0.3);
    }
  }
  * { margin:0; padding:0; box-sizing:border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
    padding: 1.5rem;
  }
  .container { max-width: 720px; margin: 0 auto; }

  /* ── Header ── */
  .report-header {
    text-align: center;
    padding: 2rem 1rem 1.5rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.5rem;
  }
  .report-header .logo {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--text-muted);
    letter-spacing: 0.05em;
    margin-bottom: 1rem;
  }
  .report-header h1 {
    font-size: 1.5rem;
    color: var(--text-heading);
    margin-bottom: 0.25rem;
  }
  .report-header .doc-name {
    color: var(--text-muted);
    font-size: 0.9rem;
    margin-bottom: 1rem;
  }

  /* ── Risk Badge ── */
  .risk-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.4rem 1.2rem;
    border-radius: 999px;
    font-weight: 700;
    font-size: 0.9rem;
    letter-spacing: 0.03em;
  }
  .risk-pill.low    { background: #22c55e18; border:1.5px solid #22c55e55; color:#16a34a; }
  .risk-pill.medium { background: #f59e0b18; border:1.5px solid #f59e0b55; color:#d97706; }
  .risk-pill.high   { background: #ef444418; border:1.5px solid #ef444455; color:#dc2626; }
  @media (prefers-color-scheme: dark) {
    .risk-pill.low    { color:#4ade80; }
    .risk-pill.medium { color:#fbbf24; }
    .risk-pill.high   { color:#f87171; }
  }

  /* ── Disclaimer ── */
  .disclaimer {
    background: var(--disclaimer-bg);
    border: 1px solid var(--disclaimer-border);
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin-bottom: 1.5rem;
    color: var(--disclaimer-text);
    font-size: 0.8rem;
    text-align: center;
  }

  /* ── Meta Card ── */
  .meta-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin-bottom: 1.25rem;
    box-shadow: var(--card-shadow);
  }
  .meta-row {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem 2rem;
  }
  .meta-item { min-width: 120px; }
  .meta-item .label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-muted);
    margin-bottom: 0.15rem;
  }
  .meta-item .value {
    font-weight: 600;
    color: var(--text);
    font-size: 0.9rem;
  }

  /* ── Executive Summary ── */
  .exec-summary {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.25rem;
    margin-bottom: 1.5rem;
    box-shadow: var(--card-shadow);
  }
  .exec-summary h2 {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-muted);
    margin-bottom: 0.75rem;
  }
  .exec-summary .big-number {
    font-size: 2.5rem;
    font-weight: 800;
    line-height: 1;
    letter-spacing: -0.02em;
  }
  .exec-summary .highlight-boxes {
    display: flex;
    gap: 0.5rem;
    margin-top: 0.75rem;
    flex-wrap: wrap;
  }
  .highlight-chip {
    padding: 0.3rem 0.75rem;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 600;
  }
  .highlight-chip.high   { background: #ef444415; color: #dc2626; }
  .highlight-chip.medium { background: #f59e0b15; color: #d97706; }
  .highlight-chip.low    { background: #22c55e15; color: #16a34a; }
  @media (prefers-color-scheme: dark) {
    .highlight-chip.high   { color: #f87171; }
    .highlight-chip.medium { color: #fbbf24; }
    .highlight-chip.low    { color: #4ade80; }
  }

  /* ── Scoreboard Grid ── */
  .scoreboard {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 0.75rem;
    margin-bottom: 1.5rem;
  }
  .score-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem;
    border-left: 3px solid var(--border);
    box-shadow: var(--card-shadow);
    text-decoration: none;
    color: inherit;
    display: block;
  }
  .score-card.risk-low    { border-left-color: #22c55e; }
  .score-card.risk-medium { border-left-color: #f59e0b; }
  .score-card.risk-high   { border-left-color: #ef4444; }
  .score-card .sc-icon  { font-size: 1.2rem; margin-bottom: 0.3rem; }
  .score-card .sc-name  { font-weight: 700; font-size: 0.9rem; color: var(--text-heading); margin-bottom: 0.15rem; }
  .score-card .sc-risk  { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; margin-bottom: 0.4rem; }
  .score-card .sc-risk.low    { color: #16a34a; }
  .score-card .sc-risk.medium { color: #d97706; }
  .score-card .sc-risk.high   { color: #dc2626; }
  .score-card .sc-tldr {
    font-size: 0.8rem;
    color: var(--text-muted);
    line-height: 1.4;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  @media (prefers-color-scheme: dark) {
    .score-card .sc-risk.low    { color: #4ade80; }
    .score-card .sc-risk.medium { color: #fbbf24; }
    .score-card .sc-risk.high   { color: #f87171; }
  }

  /* ── Zone Detail Cards ── */
  .section-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: var(--text-muted);
    margin-bottom: 0.75rem;
  }
  .zone-detail {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.25rem;
    margin-bottom: 0.75rem;
    box-shadow: var(--card-shadow);
  }
  .zone-detail .zd-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.75rem;
  }
  .zone-detail .zd-title {
    font-weight: 700;
    font-size: 1rem;
    color: var(--text-heading);
  }
  .zone-detail .zd-summary {
    color: var(--text);
    font-size: 0.9rem;
    margin-bottom: 0.75rem;
    line-height: 1.5;
  }
  .zone-detail .zd-clauses {
    margin-bottom: 0.75rem;
  }
  .clause-block {
    background: var(--clause-bg);
    border-radius: 6px;
    padding: 0.75rem;
    margin-bottom: 0.4rem;
    font-family: 'SF Mono', ui-monospace, monospace;
    font-size: 0.78rem;
    color: var(--clause-text);
    border-left: 3px solid var(--border);
    line-height: 1.45;
  }
  .clause-block strong {
    display: block;
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    font-size: 0.8rem;
    margin-bottom: 0.25rem;
  }
  .zone-detail .zd-recs {
    background: var(--clause-bg);
    border-radius: 6px;
    padding: 0.75rem 1rem;
  }
  .zone-detail .zd-recs h4 {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-muted);
    margin-bottom: 0.4rem;
  }
  .zone-detail .zd-recs li {
    font-size: 0.85rem;
    margin-left: 1.2rem;
    margin-bottom: 0.2rem;
    color: var(--text);
  }

  /* ── Footer ── */
  .report-footer {
    text-align: center;
    padding: 2rem 1rem 1rem;
    color: var(--footer-text);
    font-size: 0.75rem;
    border-top: 1px solid var(--border);
    margin-top: 1.5rem;
  }
"""


def generate_html_report(analysis: dict, metadata: dict) -> str:
    """Generate a card-based, glanceable HTML report."""

    overall_risk = _compute_overall_risk(analysis)
    risk_counts = _count_risks(analysis)
    summary_text = _build_executive_summary(analysis, overall_risk)
    scoreboard = _render_scoreboard(analysis)
    details = _render_details(analysis)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="color-scheme" content="light dark">
<title>ContractLens — {_esc(metadata.get('title', 'Contract Review'))}</title>
<style>{CSS}</style>
</head>
<body>
<div class="container">

  <!-- HEADER -->
  <div class="report-header">
    <div class="logo">📋 ContractLens</div>
    <h1>Contract Analysis Report</h1>
    <p class="doc-name">{_esc(metadata.get('title', 'Contract Review'))}</p>
    <span class="risk-pill {overall_risk}">
      {RISK_EMOJI.get(overall_risk, '⚪')} Overall Risk: {overall_risk.upper()}
    </span>
  </div>

  <!-- DISCLAIMER -->
  <div class="disclaimer">
    ⚠️ <strong>Not legal advice.</strong> AI-generated analysis for informational purposes only.
    Consult a qualified attorney before signing.
  </div>

  <!-- META -->
  <div class="meta-card">
    <div class="meta-row">
      <div class="meta-item">
        <div class="label">Parties</div>
        <div class="value">{_esc(', '.join(metadata.get('parties', ['Unknown']))[:80])}</div>
      </div>
      <div class="meta-item">
        <div class="label">Date</div>
        <div class="value">{metadata.get('date') or 'Not found'}</div>
      </div>
      <div class="meta-item">
        <div class="label">Pages</div>
        <div class="value">~{metadata.get('page_estimate', '?')}</div>
      </div>
      <div class="meta-item">
        <div class="label">Analyzed</div>
        <div class="value">{datetime.now().strftime('%b %d, %Y')}</div>
      </div>
    </div>
  </div>

  <!-- EXECUTIVE SUMMARY -->
  <div class="exec-summary">
    <h2>📊 Executive Summary</h2>
    <div class="big-number" style="color:{RISK_COLORS.get(overall_risk, RISK_COLORS['unknown'])}">
      {risk_counts['high']}<span style="font-size:1rem;font-weight:400;color:var(--text-muted);">/6 high-risk zones</span>
    </div>
    <p style="margin-top:0.5rem;font-size:0.9rem;color:var(--text);">{summary_text}</p>
    <div class="highlight-boxes">
      <span class="highlight-chip high">{risk_counts['high']} High Risk</span>
      <span class="highlight-chip medium">{risk_counts['medium']} Medium</span>
      <span class="highlight-chip low">{risk_counts['low']} Low</span>
    </div>
  </div>

  <!-- SCOREBOARD -->
  <div class="section-label">At a Glance</div>
  <div class="scoreboard">
    {scoreboard}
  </div>

  <!-- DETAILS -->
  <div class="section-label">Detailed Analysis</div>
  {details}

  <!-- FOOTER -->
  <div class="report-footer">
    <p>ContractLens — AI-powered contract analysis</p>
    <p>This is not legal advice. Consult a lawyer before signing.</p>
  </div>

</div>
</body>
</html>"""


# ── Helpers ─────────────────────────────────────────────────────────────────

def _build_executive_summary(analysis: dict, overall_risk: str) -> str:
    """Build a 2-3 sentence executive summary."""
    high_zones = [ZONE_NAMES[k][1] for k, v in analysis.items()
                  if isinstance(v, dict) and v.get("risk") == "high"]
    medium_zones = [ZONE_NAMES[k][1] for k, v in analysis.items()
                    if isinstance(v, dict) and v.get("risk") == "medium"]

    if overall_risk == "high":
        parts = [f"This contract has {len(high_zones)} high-risk areas that need attention: "
                 f"{', '.join(high_zones[:3])}."]
        if medium_zones:
            parts.append(f" {len(medium_zones)} more zones have moderate concerns ({', '.join(medium_zones[:2])}).")
        parts.append(" Several clauses should be renegotiated before signing.")
        return "".join(parts)
    elif overall_risk == "medium":
        parts = [f"This contract has some areas to watch: {', '.join(high_zones + medium_zones[:2])}."]
        parts.append(" Most terms are manageable with minor adjustments. Review the flagged sections below.")
        return "".join(parts)
    else:
        return "This contract looks reasonable overall. No major red flags. Review the details below for minor suggestions."


def _count_risks(analysis: dict) -> dict:
    """Count risk levels."""
    counts = {"high": 0, "medium": 0, "low": 0}
    for v in analysis.values():
        if isinstance(v, dict):
            counts[v.get("risk", "low")] = counts.get(v.get("risk", "low"), 0) + 1
    return counts


def _render_scoreboard(analysis: dict) -> str:
    """Render the at-a-glance scoreboard grid."""
    cards = []
    for zone_key in ["payment_terms", "ip_ownership", "non_compete",
                      "termination", "indemnification", "liability_caps"]:
        data = analysis.get(zone_key, {})
        if not isinstance(data, dict):
            continue
        icon, name = ZONE_NAMES.get(zone_key, ("❓", zone_key))
        risk = data.get("risk", "unknown")
        # One-liner tldr from the summary
        tldr = data.get("summary", "")[:120]

        cards.append(f"""<div class="score-card risk-{risk}">
    <div class="sc-icon">{icon}</div>
    <div class="sc-name">{_esc(name)}</div>
    <div class="sc-risk {risk}">{risk}</div>
    <div class="sc-tldr">{_esc(tldr)}</div>
  </div>""")

    return "\n".join(cards)


def _render_details(analysis: dict) -> str:
    """Render detailed zone cards with clauses and recommendations."""
    sections = []
    for zone_key in ["payment_terms", "ip_ownership", "non_compete",
                      "termination", "indemnification", "liability_caps"]:
        data = analysis.get(zone_key, {})
        if not isinstance(data, dict):
            continue
        icon, name = ZONE_NAMES.get(zone_key, ("❓", zone_key))
        risk = data.get("risk", "unknown")
        summary = data.get("summary", "No analysis available.")

        # Clauses
        clauses_html = ""
        for clause in data.get("key_clauses", []):
            if isinstance(clause, dict):
                clauses_html += f"""<div class="clause-block">
    <strong>{_esc(clause.get('title', 'Clause'))}</strong>
    {_esc(clause.get('text', '')[:500])}
  </div>"""

        # Recommendations
        recs_html = ""
        recs = data.get("recommendations", [])
        if recs:
            items = "".join(f"<li>{_esc(r)}</li>" for r in recs)
            recs_html = f"""<div class="zd-recs">
    <h4>💡 What to do</h4>
    <ul>{items}</ul>
  </div>"""

        sections.append(f"""<div class="zone-detail">
    <div class="zd-header">
      <span class="zd-title">{icon} {_esc(name)}</span>
      <span class="risk-pill {risk}">{risk.upper()}</span>
    </div>
    <div class="zd-summary">{_esc(summary)}</div>
    <div class="zd-clauses">{clauses_html}</div>
    {recs_html}
  </div>""")

    return "\n".join(sections)


def _compute_overall_risk(analysis: dict) -> str:
    risks = [v.get("risk", "unknown") for v in analysis.values()
             if isinstance(v, dict)]
    h, m = risks.count("high"), risks.count("medium")
    if h >= 2: return "high"
    if h == 1 or m >= 3: return "medium"
    return "low"


def _esc(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))


def save_report(html: str, output_dir: str | Path,
                filename: str = "report.html") -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / filename
    filepath.write_text(html, encoding="utf-8")
    return filepath
