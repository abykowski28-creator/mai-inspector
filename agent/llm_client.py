from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
ANTHROPIC_MESSAGES_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_API_VERSION = "2023-06-01"

ANTHROPIC_SYSTEM_PROMPT = (
    "You are MAI Agent v0.1. Return valid JSON only. "
    "Do not include Markdown code fences, explanations, or any text outside the JSON object."
)


class LLMError(RuntimeError):
    pass


# OpenAI

def call_openai_json(prompt: str, model: str | None = None, timeout: int = 120) -> dict[str, Any]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise LLMError("OPENAI_API_KEY is not set")

    payload = {
        "model": model or os.environ.get("MAI_OPENAI_MODEL", "gpt-5.4-mini"),
        "input": prompt,
        "temperature": 0.1,
        "text": {"format": {"type": "json_object"}},
    }
    request = urllib.request.Request(
        OPENAI_RESPONSES_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise LLMError(f"OpenAI API error {exc.code}: {detail}") from exc
    except Exception as exc:
        raise LLMError(f"OpenAI API call failed: {exc}") from exc

    return _parse_json(_extract_openai_text(data))


def _extract_openai_text(response: dict[str, Any]) -> str:
    if isinstance(response.get("output_text"), str):
        return response["output_text"]
    chunks: list[str] = []
    for item in response.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and content.get("text"):
                chunks.append(content["text"])
    if chunks:
        return "\n".join(chunks)
    raise LLMError("No text content found in OpenAI response")


# Anthropic

def call_anthropic_json(prompt: str, model: str | None = None, timeout: int = 180) -> dict[str, Any]:
    """Call Anthropic Messages API and return parsed JSON.

    Default model: claude-sonnet-4-6 (override with MAI_ANTHROPIC_MODEL env var).
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise LLMError("ANTHROPIC_API_KEY is not set")

    payload = {
        "model": model or os.environ.get("MAI_ANTHROPIC_MODEL", "claude-sonnet-4-6"),
        "max_tokens": 8192,
        "temperature": 0.1,
        "system": ANTHROPIC_SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": prompt}],
    }
    request = urllib.request.Request(
        ANTHROPIC_MESSAGES_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "x-api-key": api_key,
            "anthropic-version": ANTHROPIC_API_VERSION,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise LLMError(f"Anthropic API error {exc.code}: {detail}") from exc
    except Exception as exc:
        raise LLMError(f"Anthropic API call failed: {exc}") from exc

    return _parse_json(_extract_anthropic_text(data))


def _extract_anthropic_text(response: dict[str, Any]) -> str:
    for block in response.get("content", []):
        if block.get("type") == "text" and block.get("text"):
            return block["text"]
    raise LLMError("No text content found in Anthropic response")


# Provider-agnostic entry point

def call_llm_json(
    prompt: str,
    provider: str | None = None,
    model: str | None = None,
    timeout: int = 180,
) -> dict[str, Any]:
    """Call the configured LLM and return parsed JSON.

    Provider resolution order:
      1. provider argument
      2. MAI_LLM_PROVIDER env var
      3. Auto-detect: Anthropic if ANTHROPIC_API_KEY set, else OpenAI
    """
    resolved = provider or os.environ.get("MAI_LLM_PROVIDER", "").lower() or _auto_detect_provider()
    if resolved == "anthropic":
        return call_anthropic_json(prompt, model=model, timeout=timeout)
    if resolved == "openai":
        return call_openai_json(prompt, model=model, timeout=timeout)
    raise LLMError(f"Unknown provider: '{resolved}'. Use 'anthropic' or 'openai'.")


def _auto_detect_provider() -> str:
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    raise LLMError("No API key found. Set ANTHROPIC_API_KEY or OPENAI_API_KEY.")


# Shared helpers

def _parse_json(text: str) -> dict[str, Any]:
    """Strip optional Markdown fences and parse JSON."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise LLMError(f"Model did not return valid JSON: {text[:1000]}") from exc
