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
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "4096"))
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
        Parsed analysis dict with 6 danger zones.

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
    return _parse_llm_json(content)


def _parse_llm_json(raw: str) -> dict:
    """Parse LLM response with multiple fallback strategies.

    Handles: markdown code fences, greedy regex, unescaped control chars,
    and common LLM output quirks.
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

    raise ValueError(
        f"Failed to parse LLM response as JSON after 5 strategies. "
        f"Response preview: {text[:300]}..."
    )
