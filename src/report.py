"""Generate HTML reports from contract analysis results."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Optional


RISK_COLORS = {
    "low": "#22c55e",       # green
    "medium": "#f59e0b",    # amber
    "high": "#ef4444",      # red
    "unknown": "#6b7280",   # gray
}

RISK_EMOJI = {
    "low": "🟢",
    "medium": "🟡",
    "high": "🔴",
    "unknown": "⚪",
}


def generate_html_report(analysis: dict, metadata: dict) -> str:
    """Generate a beautiful HTML report from the analysis results.

    Args:
        analysis: Dict with keys matching DANGER_ZONES, each containing
                  {summary, risk, key_clauses, recommendations}.
        metadata: Dict from get_contract_metadata().

    Returns:
        Complete HTML string.
    """
    zones_html = ""
    for zone_key, zone_data in analysis.items():
        if not isinstance(zone_data, dict):
            continue
        risk = zone_data.get("risk", "unknown")
        zones_html += _render_zone(zone_key, zone_data, risk)

    overall_risk = _compute_overall_risk(analysis)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ContractLens Analysis — {metadata.get('title', 'Contract Review')}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #0f172a;
    color: #e2e8f0;
    line-height: 1.6;
    padding: 2rem;
  }}
  .container {{ max-width: 800px; margin: 0 auto; }}
  .header {{
    text-align: center;
    padding: 3rem 1rem;
    border-bottom: 1px solid #1e293b;
    margin-bottom: 2rem;
  }}
  .header h1 {{
    font-size: 2rem;
    color: #f8fafc;
    margin-bottom: 0.5rem;
  }}
  .header .subtitle {{ color: #94a3b8; font-size: 0.9rem; }}
  .overall-risk {{
    display: inline-block;
    padding: 0.5rem 1.5rem;
    border-radius: 9999px;
    font-weight: 700;
    font-size: 1.1rem;
    margin-top: 1rem;
    background: {RISK_COLORS.get(overall_risk, RISK_COLORS['unknown'])}22;
    border: 2px solid {RISK_COLORS.get(overall_risk, RISK_COLORS['unknown'])};
    color: {RISK_COLORS.get(overall_risk, RISK_COLORS['unknown'])};
  }}
  .meta {{
    background: #1e293b;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 2rem;
  }}
  .meta-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
  }}
  .meta-item .label {{ color: #64748b; font-size: 0.8rem; text-transform: uppercase; }}
  .meta-item .value {{ color: #e2e8f0; font-weight: 600; }}
  .zone {{
    background: #1e293b;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    border-left: 4px solid #334155;
  }}
  .zone.risk-low {{ border-left-color: {RISK_COLORS['low']}; }}
  .zone.risk-medium {{ border-left-color: {RISK_COLORS['medium']}; }}
  .zone.risk-high {{ border-left-color: {RISK_COLORS['high']}; }}
  .zone-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }}
  .zone-header h2 {{ font-size: 1.25rem; color: #f1f5f9; }}
  .risk-badge {{
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
  }}
  .risk-badge.low {{ background: {RISK_COLORS['low']}22; color: {RISK_COLORS['low']}; }}
  .risk-badge.medium {{ background: {RISK_COLORS['medium']}22; color: {RISK_COLORS['medium']}; }}
  .risk-badge.high {{ background: {RISK_COLORS['high']}22; color: {RISK_COLORS['high']}; }}
  .zone-summary {{ color: #cbd5e1; margin-bottom: 1rem; font-size: 0.95rem; }}
  .clauses {{ margin-bottom: 1rem; }}
  .clause {{
    background: #0f172a;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 0.5rem;
    font-family: 'SF Mono', 'Fira Code', monospace;
    font-size: 0.85rem;
    color: #94a3b8;
    border-left: 3px solid #334155;
  }}
  .clause.high {{ border-left-color: {RISK_COLORS['high']}; }}
  .clause.medium {{ border-left-color: {RISK_COLORS['medium']}; }}
  .recommendations {{
    background: #0f172a;
    border-radius: 8px;
    padding: 1rem;
  }}
  .recommendations h4 {{
    color: #64748b;
    font-size: 0.8rem;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
  }}
  .recommendations li {{
    color: #94a3b8;
    margin-left: 1.5rem;
    margin-bottom: 0.25rem;
    font-size: 0.9rem;
  }}
  .footer {{
    text-align: center;
    padding: 3rem 1rem 1rem;
    color: #475569;
    font-size: 0.8rem;
  }}
  .disclaimer {{
    background: #451a1a;
    border: 1px solid #7f1d1d;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 2rem;
    color: #fca5a5;
    font-size: 0.85rem;
    text-align: center;
  }}
  .score-bar {{
    display: flex;
    gap: 4px;
    margin-top: 0.5rem;
  }}
  .score-segment {{
    height: 6px;
    border-radius: 3px;
    flex: 1;
  }}
  .score-segment.high {{ background: {RISK_COLORS['high']}; }}
  .score-segment.medium {{ background: {RISK_COLORS['medium']}; }}
  .score-segment.low {{ background: {RISK_COLORS['low']}; }}
</style>
</head>
<body>
<div class="container">

  <div class="header">
    <h1>📋 ContractLens Analysis</h1>
    <p class="subtitle">{metadata.get('title', 'Contract Review')}</p>
    <div class="overall-risk">
      {RISK_EMOJI.get(overall_risk, '⚪')} Overall Risk: {overall_risk.upper()}
    </div>
    <div class="score-bar" style="margin-top:1rem; max-width:300px; margin-left:auto; margin-right:auto;">
      {_render_score_bar(analysis)}
    </div>
  </div>

  <div class="disclaimer">
    ⚠️ <strong>Not legal advice.</strong> This analysis is AI-generated and for informational
    purposes only. Always consult a qualified attorney before signing any contract.
  </div>

  <div class="meta">
    <div class="meta-grid">
      <div class="meta-item">
        <div class="label">Document</div>
        <div class="value">{_escape(metadata.get('title', 'Untitled')[:50])}</div>
      </div>
      <div class="meta-item">
        <div class="label">Parties</div>
        <div class="value">{_escape(', '.join(metadata.get('parties', ['Unknown']))[:60])}</div>
      </div>
      <div class="meta-item">
        <div class="label">Date</div>
        <div class="value">{metadata.get('date') or 'Not found'}</div>
      </div>
      <div class="meta-item">
        <div class="label">Est. Pages</div>
        <div class="value">{metadata.get('page_estimate', '?')}</div>
      </div>
      <div class="meta-item">
        <div class="label">Analyzed</div>
        <div class="value">{datetime.now().strftime('%B %d, %Y at %H:%M')}</div>
      </div>
    </div>
  </div>

  <h2 style="color:#94a3b8; font-size:1rem; text-transform:uppercase; margin-bottom:1rem;">
    Danger Zone Analysis
  </h2>

  {zones_html}

  <div class="footer">
    <p>ContractLens v{__import__('src').__version__} — AI-powered contract analysis</p>
    <p>This is not legal advice. Consult a lawyer.</p>
  </div>

</div>
</body>
</html>"""
    return html


def _render_zone(zone_key: str, data: dict, risk: str) -> str:
    """Render a single danger zone section."""
    zone_names = {
        "payment_terms": "💰 Payment Terms",
        "ip_ownership": "🔒 IP & Ownership",
        "non_compete": "🚫 Non-Compete & Restrictions",
        "termination": "⏰ Termination & Exit",
        "indemnification": "🛡️ Indemnification",
        "liability_caps": "⚖️ Liability & Damages",
    }
    name = zone_names.get(zone_key, zone_key.replace("_", " ").title())
    summary = data.get("summary", "No summary available.")

    clauses_html = ""
    for clause in data.get("key_clauses", []):
        if isinstance(clause, dict):
            clause_risk = clause.get("risk", "low")
            clauses_html += f"""
    <div class="clause {clause_risk}">
      <strong>{_escape(clause.get('title', 'Clause'))}</strong>
      <p style="margin-top:0.25rem;">{_escape(clause.get('text', '')[:500])}</p>
    </div>"""

    recs_html = ""
    recs = data.get("recommendations", [])
    if recs:
        recs_html = "<ul>" + "".join(f"<li>{_escape(r)}</li>" for r in recs) + "</ul>"

    return f"""
  <div class="zone risk-{risk}">
    <div class="zone-header">
      <h2>{name}</h2>
      <span class="risk-badge {risk}">{risk}</span>
    </div>
    <p class="zone-summary">{_escape(summary)}</p>
    <div class="clauses">{clauses_html}</div>
    {f'<div class="recommendations"><h4>💡 Recommendations</h4>{recs_html}</div>' if recs else ''}
  </div>"""


def _compute_overall_risk(analysis: dict) -> str:
    """Compute overall risk from zone-level risks."""
    risks = []
    for data in analysis.values():
        if isinstance(data, dict):
            risks.append(data.get("risk", "unknown"))

    high_count = risks.count("high")
    medium_count = risks.count("medium")

    if high_count >= 2:
        return "high"
    elif high_count == 1 or medium_count >= 3:
        return "medium"
    return "low"


def _render_score_bar(analysis: dict) -> str:
    """Render a visual risk distribution bar."""
    risks = []
    for data in analysis.values():
        if isinstance(data, dict):
            risks.append(data.get("risk", "unknown"))
    parts = []
    for risk in sorted(risks):
        parts.append(f'<div class="score-segment {risk}"></div>')
    return "".join(parts)


def _escape(text: str) -> str:
    """Basic HTML escaping."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def save_report(html: str, output_dir: str | Path, filename: str = "report.html") -> Path:
    """Save the HTML report to disk."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / filename
    filepath.write_text(html, encoding="utf-8")
    return filepath
