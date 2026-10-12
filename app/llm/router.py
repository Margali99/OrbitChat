import os
from typing import Generator, List, Dict, Any
import litellm
from app.config import settings

litellm.suppress_debug_info = True

def get_provider_for_model(model: str) -> str:
    m = model.lower()
    if "gemini" in m: return "gemini"
    if m.startswith("claude") or m.startswith("anthropic"): return "anthropic"
    if m.startswith("grok") or m.startswith("xai"): return "xai"
    return "gemini"

def _clean_key(key: str) -> str:
    """Strip BOM/non-ASCII chars that break HTTP headers."""
    return key.encode("ascii", errors="ignore").decode("ascii").strip()

def stream_llm_response(messages, model, api_key=None, tools=None):
    provider = get_provider_for_model(model)
    target_model = f"gemini/{model}" if provider == "gemini" and not model.startswith("gemini/") else model

    effective_key = api_key or (settings.gemini_api_key or os.getenv("GEMINI_API_KEY", "") if provider == "gemini" else None)
    if effective_key:
        effective_key = _clean_key(effective_key)
    if provider == "gemini" and effective_key:
        os.environ["GEMINI_API_KEY"] = effective_key

    kwargs = {"model": target_model, "messages": messages, "stream": True}
    if effective_key: kwargs["api_key"] = effective_key
    if tools: kwargs["tools"] = tools

    for chunk in litellm.completion(**kwargs):
        if not chunk.choices: continue
        delta = getattr(chunk.choices[0], "delta", None)
        if not delta: continue
        yield {"token": getattr(delta, "content", None) or "", "tool_calls": getattr(delta, "tool_calls", None)}
