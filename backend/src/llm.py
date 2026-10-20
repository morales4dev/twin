from dataclasses import dataclass
import os
from typing import Any

import litellm

if hasattr(litellm, "telemetry"):
    litellm.telemetry = False


@dataclass(frozen=True)
class LLMSettings:
    primary_model: str
    fallback_model: str
    timeout: int
    retries: int
    openai_api_key: str | None
    openai_base_url: str | None
    anthropic_api_key: str | None


def get_settings() -> LLMSettings:
    return LLMSettings(
        primary_model=os.getenv("PRIMARY_MODEL", "MiniMax-M2.5"),
        fallback_model=os.getenv("FALLBACK_MODEL", "claude-haiku-4-5-20251001"),
        timeout=int(os.getenv("LLM_TIMEOUT", "30")),
        retries=int(os.getenv("LLM_RETRIES", "2")),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_base_url=os.getenv("OPENAI_BASE_URL"),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
    )


def _call(
    model: str,
    messages: list,
    *,
    tools: list | None,
    timeout: int,
    retries: int,
    api_key: str | None,
    api_base: str | None,
) -> object:
    kwargs: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "timeout": timeout,
        "num_retries": retries,
        "api_key": api_key,
    }
    if api_base is not None:
        kwargs["api_base"] = api_base
    if tools is not None:
        kwargs["tools"] = tools
    return litellm.completion(**kwargs)


def completion(messages: list, *, tools: list | None = None) -> object:
    settings = get_settings()
    try:
        return _call(
            f"openai/{settings.primary_model}",
            messages,
            tools=tools,
            timeout=settings.timeout,
            retries=settings.retries,
            api_key=settings.openai_api_key,
            api_base=settings.openai_base_url,
        )
    except Exception:
        return _call(
            settings.fallback_model,
            messages,
            tools=tools,
            timeout=settings.timeout,
            retries=settings.retries,
            api_key=settings.anthropic_api_key,
            api_base=None,
        )
