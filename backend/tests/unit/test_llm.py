"""llm.completion primary-then-fallback. No network."""

from unittest.mock import patch

import pytest


@pytest.fixture
def llm_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-openai")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://example.test/v1")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-anthropic")


@patch("litellm.completion")
def test_primary_success_does_not_call_fallback(mock_completion, llm_env) -> None:
    from llm import completion

    mock_completion.return_value = "primary-ok"
    messages = [{"role": "user", "content": "hi"}]

    result = completion(messages)

    assert result == "primary-ok"
    assert mock_completion.call_count == 1
    kwargs = mock_completion.call_args.kwargs
    assert kwargs["messages"] == messages
    assert kwargs["model"] == "openai/MiniMax-M2.5"
    assert kwargs["api_base"] == "https://example.test/v1"
    assert kwargs["api_key"] == "sk-test-openai"
    assert kwargs["timeout"] == 30
    assert kwargs["num_retries"] == 2
    assert "tools" not in kwargs
    assert "fallbacks" not in kwargs


@patch("litellm.completion")
def test_primary_raise_then_fallback_success(mock_completion, llm_env) -> None:
    from llm import completion

    mock_completion.side_effect = [RuntimeError("primary down"), "fallback-ok"]
    messages = [{"role": "user", "content": "hi"}]

    result = completion(messages)

    assert result == "fallback-ok"
    assert mock_completion.call_count == 2
    primary_kwargs = mock_completion.call_args_list[0].kwargs
    fallback_kwargs = mock_completion.call_args_list[1].kwargs
    assert primary_kwargs["model"] == "openai/MiniMax-M2.5"
    assert primary_kwargs["timeout"] == 30
    assert primary_kwargs["num_retries"] == 2
    assert fallback_kwargs["model"] == "claude-haiku-4-5-20251001"
    assert fallback_kwargs["api_key"] == "sk-test-anthropic"
    assert "api_base" not in fallback_kwargs
    assert fallback_kwargs["timeout"] == 30
    assert fallback_kwargs["num_retries"] == 2
    assert "tools" not in fallback_kwargs


@patch("litellm.completion")
def test_both_models_raise(mock_completion, llm_env) -> None:
    from llm import completion

    mock_completion.side_effect = [RuntimeError("primary down"), RuntimeError("fallback down")]

    with pytest.raises(RuntimeError, match="fallback down"):
        completion([{"role": "user", "content": "hi"}])

    assert mock_completion.call_count == 2


@patch("litellm.completion")
def test_tools_passed_through_when_provided(mock_completion, llm_env) -> None:
    from llm import completion

    mock_completion.return_value = "ok"
    tools = [{"type": "function", "function": {"name": "record_user_details"}}]

    completion([{"role": "user", "content": "hi"}], tools=tools)

    assert mock_completion.call_count == 1
    assert mock_completion.call_args.kwargs["tools"] == tools


@patch("litellm.completion")
def test_blank_llm_env_uses_defaults(mock_completion, llm_env, monkeypatch: pytest.MonkeyPatch) -> None:
    from llm import completion

    monkeypatch.setenv("LLM_TIMEOUT", "")
    monkeypatch.setenv("LLM_RETRIES", "")
    monkeypatch.setenv("PRIMARY_MODEL", "")
    monkeypatch.setenv("FALLBACK_MODEL", "")
    mock_completion.side_effect = [RuntimeError("primary down"), "fallback-ok"]

    result = completion([{"role": "user", "content": "hi"}])

    assert result == "fallback-ok"
    primary_kwargs = mock_completion.call_args_list[0].kwargs
    fallback_kwargs = mock_completion.call_args_list[1].kwargs
    assert primary_kwargs["timeout"] == 30
    assert primary_kwargs["num_retries"] == 2
    assert primary_kwargs["model"] == "openai/MiniMax-M2.5"
    assert fallback_kwargs["model"] == "claude-haiku-4-5-20251001"
    assert fallback_kwargs["timeout"] == 30
    assert fallback_kwargs["num_retries"] == 2


@patch("litellm.completion")
def test_invalid_timeout_fails_before_provider_call(
    mock_completion, llm_env, monkeypatch: pytest.MonkeyPatch
) -> None:
    from llm import completion

    monkeypatch.setenv("LLM_TIMEOUT", "abc")

    with pytest.raises(Exception, match="LLM_TIMEOUT"):
        completion([{"role": "user", "content": "hi"}])

    mock_completion.assert_not_called()
