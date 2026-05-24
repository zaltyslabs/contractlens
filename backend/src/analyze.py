"""LLM-powered contract analysis.

This module is designed to be called from a Hermes cron job. It reads the
analysis prompt template, injects the contract text, and expects Hermes to
process the LLM call.

When running inside Hermes: the cron job's prompt is the analysis call.
When running standalone: use the CLI via pipeline.py.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

from .config import PROMPTS_DIR, MAX_CONTRACT_CHARS


def load_prompt() -> str:
    """Load the contract analysis prompt template."""
    prompt_file = PROMPTS_DIR / "contract_analysis.md"
    if not prompt_file.exists():
        raise FileNotFoundError(
            f"Analysis prompt not found at {prompt_file}. "
            "Make sure prompts/contract_analysis.md exists."
        )
    return prompt_file.read_text(encoding="utf-8")


def build_analysis_prompt(contract_text: str) -> str:
    """Build the full analysis prompt with contract text injected.

    Truncates contract text if it exceeds MAX_CONTRACT_CHARS.
    """
    prompt_template = load_prompt()

    if len(contract_text) > MAX_CONTRACT_CHARS:
        contract_text = (
            contract_text[:MAX_CONTRACT_CHARS]
            + f"\n\n[... truncated {len(contract_text) - MAX_CONTRACT_CHARS} characters]"
        )

    return f"""{prompt_template}

---

## CONTRACT TEXT TO ANALYZE

{contract_text}

---

Now analyze the contract above according to the framework. Output ONLY valid JSON."""


def parse_analysis_response(response: str) -> dict:
    """Parse the LLM's JSON response into a structured dict.

    Handles cases where the LLM wraps JSON in markdown code blocks.

    Raises:
        ValueError: If the response cannot be parsed as JSON.
            This often happens when the LLM response was truncated
            due to token limits.
    """
    # Strip markdown code fences if present
    text = response.strip()
    if text.startswith("```"):
        # Remove opening fence
        text = text.split("\n", 1)[-1] if "\n" in text else text[3:]
        # Remove closing fence
        if text.endswith("```"):
            text = text[:-3]

    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to extract JSON object from the response
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        raise ValueError(
            "Failed to parse LLM response as JSON. "
            "The response may have been truncated due to token limits. "
            "Try reducing contract length or increasing LLM_MAX_TOKENS. "
            f"Response preview: {text[:300]}..."
        )


def validate_analysis(analysis: dict) -> list[str]:
    """Validate the analysis has all required danger zones.

    Returns list of warnings (empty means valid).
    """
    required_zones = {
        "payment_terms",
        "ip_ownership",
        "non_compete",
        "termination",
        "indemnification",
        "liability_caps",
    }
    warnings = []

    for zone in required_zones:
        if zone not in analysis:
            warnings.append(f"Missing danger zone: {zone}")
        elif not isinstance(analysis[zone], dict):
            warnings.append(f"Invalid format for danger zone: {zone}")
        else:
            zone_data = analysis[zone]
            if "risk" not in zone_data:
                warnings.append(f"Missing 'risk' in {zone}")
            if "summary" not in zone_data:
                warnings.append(f"Missing 'summary' in {zone}")

    return warnings


def format_analysis_for_display(analysis: dict) -> str:
    """Format the analysis as a readable text summary (for CLI output)."""
    lines = []

    # Show warnings about truncation or JSON repair
    if analysis.get("_truncated"):
        lines.append("⚠️  WARNING: Response was truncated by token limit.")
        if analysis.get("_warning"):
            lines.append(f"   {analysis['_warning']}")
        lines.append("")

    if analysis.get("_repaired"):
        lines.append("🔧 NOTE: This analysis was recovered from a partial JSON response.")
        lines.append("   Some zones may be incomplete.")
        lines.append("")

    zone_names = {
        "payment_terms": "💰 Payment Terms",
        "ip_ownership": "🔒 IP & Ownership",
        "non_compete": "🚫 Non-Compete & Restrictions",
        "termination": "⏰ Termination & Exit",
        "indemnification": "🛡️ Indemnification",
        "liability_caps": "⚖️ Liability & Damages",
    }

    for zone_key, name in zone_names.items():
        data = analysis.get(zone_key, {})
        if not isinstance(data, dict):
            continue
        risk = data.get("risk", "unknown").upper()
        summary = data.get("summary", "No summary")
        recs = data.get("recommendations", [])

        lines.append(f"\n{'='*60}")
        lines.append(f"{name}  [{risk}]")
        lines.append(f"{'='*60}")
        lines.append(f"\n{summary}")

        if recs:
            lines.append(f"\n💡 Recommendations:")
            for r in recs:
                lines.append(f"  • {r}")

    return "\n".join(lines)
