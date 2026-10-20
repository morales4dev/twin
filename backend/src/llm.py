from typing import Any

import litellm
from pydantic_settings import BaseSettings, SettingsConfigDict

if hasattr(litellm, "telemetry"):
    litellm.telemetry = False


class LLMSettings(BaseSettings):
    model_config = SettingsConfigDict(env_ignore_empty=True, extra="ignore")

    PRIMARY_MODEL: str = "MiniMax-M2.5"
    FALLBACK_MODEL: str = "claude-haiku-4-5-20251001"
    LLM_TIMEOUT: int = 30
    LLM_RETRIES: int = 2
    OPENAI_API_KEY: str | None = None
    OPENAI_BASE_URL: str | None = None
    ANTHROPIC_API_KEY: str | None = None


def get_settings() -> LLMSettings:
    return LLMSettings()


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
            f"openai/{settings.PRIMARY_MODEL}",
            messages,
            tools=tools,
            timeout=settings.LLM_TIMEOUT,
            retries=settings.LLM_RETRIES,
            api_key=settings.OPENAI_API_KEY,
            api_base=settings.OPENAI_BASE_URL,
        )
    except Exception:
        return _call(
            settings.FALLBACK_MODEL,
            messages,
            tools=tools,
            timeout=settings.LLM_TIMEOUT,
            retries=settings.LLM_RETRIES,
            api_key=settings.ANTHROPIC_API_KEY,
            api_base=None,
        )
