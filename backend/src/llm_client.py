"""Model-agnostic LLM client for contract analysis.

Works with any OpenAI-compatible API (DeepSeek, OpenAI, Groq,
OpenRouter, Ollama, etc.). Configure via environment variables:
  LLM_BASE_URL — API base URL (default: https://api.deepseek.com/v1)
  LLM_API_KEY  — API key
  LLM_MODEL    — model name (default: deepseek-chat)

Enforces JSON output via response_format where supported (deepseek,
openai, groq), falls back to prompt-level enforcement for others.
"""

from __future__ import annotations

import json
import os
import re

import httpx

from .config import LLM_MODEL
from .analyze import load_prompt


# ── Configuration (env-driven, no hardcoded provider) ──────────────────────

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1")
LLM_API_KEY = os.getenv(
    "LLM_API_KEY",
    os.getenv("DEEPSEEK_API_KEY", os.getenv("OPENAI_API_KEY", "")),
)
LLM_MODEL_NAME = os.getenv("LLM_MODEL", LLM_MODEL)
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "120"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "8192"))
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))

# Providers that natively support response_format: json_object
_JSON_MODE_PROVIDERS = {"deepseek", "openai", "groq", "together", "fireworks"}


def _supports_json_mode() -> bool:
    base = LLM_BASE_URL.lower()
    return any(p in base for p in _JSON_MODE_PROVIDERS)


async def analyze_contract(contract_text: str) -> dict:
    """Send contract text to the configured LLM for analysis.

    Works with any OpenAI-compatible chat completions API.

    Returns:
        Parsed analysis dict with 6 danger zones. May include metadata
        fields: _truncated (bool), _warning (str), _repaired (bool).

    Raises:
        ValueError: If LLM_API_KEY is not configured.
        RuntimeError: If the API call fails or returns a bad status.
    """
    if not LLM_API_KEY:
        raise ValueError(
            "LLM_API_KEY not configured. Set it in .env or environment."
        )

    system_prompt = load_prompt()
    user_message = (
        "## CONTRACT TEXT TO ANALYZE\n\n"
        f"{contract_text}\n\n"
        "---\n\n"
        "Now analyze the contract above according to the framework. "
        "Output ONLY valid JSON."
    )

    payload: dict = {
        "model": LLM_MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": LLM_TEMPERATURE,
        "max_tokens": LLM_MAX_TOKENS,
    }

    if _supports_json_mode():
        payload["response_format"] = {"type": "json_object"}

    print(f"Calling {LLM_MODEL_NAME} via {LLM_BASE_URL}...")

    try:
        async with httpx.AsyncClient(timeout=LLM_TIMEOUT) as client:
            response = await client.post(
                f"{LLM_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {LLM_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
    except httpx.TimeoutException:
        raise RuntimeError(
            f"LLM API timed out after {LLM_TIMEOUT}s. "
            "Try increasing LLM_TIMEOUT or using a faster model."
        )
    except httpx.HTTPStatusError as e:
        raise RuntimeError(
            f"LLM API returned {e.response.status_code}: {e.response.text[:200]}"
        )

    data = response.json()
    content = data["choices"][0]["message"]["content"]
    finish_reason = data["choices"][0].get("finish_reason", "")

    result = _parse_llm_json(content)

    # Warn if the API truncated the response
    if finish_reason == "length":
        result["_truncated"] = True
        result["_warning"] = (
            "Response was truncated by token limit. "
            "Some analysis may be incomplete. "
            "Consider reducing contract length or increasing LLM_MAX_TOKENS "
            f"(currently {LLM_MAX_TOKENS})."
        )

    return result


def _parse_llm_json(raw: str) -> dict:
    """Parse LLM response with multiple fallback strategies.

    Handles: markdown code fences, greedy regex, unescaped control chars,
    truncated JSON repair, and common LLM output quirks.
    """
    text = raw.strip()

    # Strategy 1: Strip markdown code fences
    if text.startswith("```"):
        text = text.split("\n", 1)[-1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
    text = text.strip()

    # Strategy 2: Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Strategy 3: Non-greedy regex extraction
    match = re.search(r"\{.*?\}(?=\s*$)", text, re.DOTALL)
    if not match:
        match = re.search(r"\{.*\}", text, re.DOTALL)

    if match:
        candidate = match.group()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            # Strategy 4: Sanitize common control character issues
            sanitized = (
                candidate
                .replace("\t", "\\t")
                .replace("\r", "")
            )
            try:
                return json.loads(sanitized)
            except json.JSONDecodeError:
                pass

    # Strategy 5: Try to find the outermost braces manually
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass

    # Strategy 6: JSON repair for truncated output
    repaired = _repair_truncated_json(text)
    if repaired is not None:
        repaired["_repaired"] = True
        return repaired

    raise ValueError(
        "Failed to parse LLM response as JSON after 6 strategies. "
        "The LLM response may have been truncated due to token limits. "
        f"Try reducing contract length or increasing LLM_MAX_TOKENS "
        f"(currently {LLM_MAX_TOKENS}). "
        f"Response preview: {text[:300]}..."
    )


def _repair_truncated_json(text: str) -> dict | None:
    """Attempt to repair truncated JSON by closing unclosed structures.

    When the LLM response is cut off mid-generation, this function
    tries to salvage as much valid JSON as possible by:
    1. Finding the last complete value boundary
    2. Closing any unclosed strings, arrays, and objects
    3. Trying progressively shorter truncations

    Returns parsed dict on success, None on failure.
    """
    start = text.find("{")
    if start < 0:
        return None

    # Approach: find the last "safe" position — a comma or colon that
    # represents a complete key:value boundary. Then truncate there,
    # close any unclosed strings/arrays/objects, and try to parse.

    brace_depth = 0
    bracket_depth = 0
    in_string = False
    escape_next = False
    last_safe = start  # Always at least keep the opening brace

    for i in range(start, len(text)):
        ch = text[i]

        if escape_next:
            escape_next = False
            continue

        if ch == "\\" and in_string:
            escape_next = True
            continue

        if ch == '"' and not escape_next:
            in_string = not in_string
            # If we just closed a string, mark as safe
            if not in_string:
                last_safe = i + 1
            continue

        if in_string:
            continue

        if ch == "{":
            brace_depth += 1
        elif ch == "}":
            brace_depth -= 1
            if brace_depth >= 0:
                last_safe = i + 1
        elif ch == "[":
            bracket_depth += 1
        elif ch == "]":
            bracket_depth -= 1
            if bracket_depth >= 0:
                last_safe = i + 1
        elif ch == "," and brace_depth > 0 and bracket_depth == 0:
            # Comma separating object keys — safe truncation point
            # (but only at top level of current brace depth, not inside nested arrays)
            last_safe = i
        elif ch in ("t", "f", "n", "-") and brace_depth > 0:
            # Could be start of true/false/null/number — mark previous safe
            pass

    # Build repaired JSON by truncating at last safe position, then
    # closing any remaining open structures
    truncated = text[start:last_safe]

    # In case last_safe was at a comma, strip the trailing comma
    truncated = truncated.rstrip()

    # Close any unclosed structures
    if in_string:
        truncated += '"'

    truncated += "]" * max(0, bracket_depth)
    truncated += "}" * max(0, brace_depth)

    # Try parsing
    try:
        return json.loads(truncated)
    except json.JSONDecodeError:
        pass

    # Fallback: try removing more aggressively — strip back to last comma
    # and try again with clean closure
    last_comma = truncated.rfind(",")
    if last_comma > 0:
        shorter = truncated[:last_comma].rstrip()
        if in_string:
            shorter += '"'
        shorter += "]" * max(0, bracket_depth)
        shorter += "}" * max(0, brace_depth)

        try:
            return json.loads(shorter)
        except json.JSONDecodeError:
            pass

    # Last resort: just try closing from the original text start
    # without any smart truncation
    raw_from_start = text[start:]
    # Close string if needed
    if in_string:
        raw_from_start += '"'
    # Try to find and strip trailing garbage
    last_brace = raw_from_start.rfind("}")
    if last_brace >= 0:
        raw_from_start = raw_from_start[:last_brace + 1]
    raw_from_start += "]" * max(0, bracket_depth)
    raw_from_start += "}" * max(0, brace_depth)

    try:
        return json.loads(raw_from_start)
    except json.JSONDecodeError:
        pass

    return None
