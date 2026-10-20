## Why

`get_settings()` does `int(os.getenv("LLM_TIMEOUT", "30"))`. A names-only `.env` sets `LLM_TIMEOUT=` (present but blank), so the default is skipped and `int("")` raises. The same happens for `LLM_RETRIES`. Units only stay green because `llm_env` deletes those keys. A live call with a copied `.env.example` still crashes before LiteLLM runs, with no field name in the error.

## What Changes

Read the existing LLM settings through a small typed settings object (Pydantic at the config boundary; first pin). Blank values count as unset and use the field default. Invalid values fail before the LLM call with a field-level error (for example `LLM_TIMEOUT` is not an integer), not `int("")`.

`.env.example` follows one rule: leave a key empty only when it is optional (secrets). For required strings and ints, write Twin’s default or omit the line.

- Secrets stay blank: `OPENAI_API_KEY=`, `OPENAI_BASE_URL=`, `ANTHROPIC_API_KEY=`, `PUSHOVER_USER=`, `PUSHOVER_TOKEN=`.
- Typed LLM keys get Twin defaults: `PRIMARY_MODEL=MiniMax-M2.5`, `FALLBACK_MODEL=claude-haiku-4-5-20251001`, `LLM_TIMEOUT=30`, `LLM_RETRIES=2`.
- An existing machine `.env` that still has `LLM_TIMEOUT=` MUST keep booting with 30. Blank is unset, not an error.
- `chat()`, `classify()`, `complete()`, the conversation window, tools, deny-list, and visitor copy stay as they are.

No **BREAKING** Gradio UX change. Defaults stay 30 / 2 / MiniMax / Haiku.

**Non-goals**

- Changing timeout, retry, or model defaults.
- A process-wide settings bag, extra env names, or Pushover validation.
- A `/health` endpoint or fail-closed-on-missing-keys.
- Changing LiteLLM Router, `fallbacks=`, the window cap, or `chat()` sequence.
- Archiving this change (archive only after a later explicit user request).

## Capabilities

### New Capabilities

- None. This is settings hygiene for the existing primary-then-fallback call.

### Modified Capabilities

- `primary-fallback`: Blank `PRIMARY_MODEL`, `FALLBACK_MODEL`, `LLM_TIMEOUT`, and `LLM_RETRIES` use the same defaults the spec already names. A value that cannot parse as the field type MUST fail that LLM settings read with a field-level error before the provider call. Missing API keys remain allowed (boot still works).

## Impact

- **Code:** `backend/src/llm.py` `LLMSettings` / `get_settings()` only. `completion()` still calls primary then fallback. MiniMax I/O stays out of `chat()`.
- **Tests:** `backend/tests/unit/test_llm.py` — blank timeout/retries/models use defaults without deleting env keys; `LLM_TIMEOUT=abc` raises a field-level error. Units still must not hit the network.
- **Docs:** root `.env.example` as above. One sentence in `ai-specs/standards/python.md` so “names only” applies to secrets, not to typed LLM defaults.
- **Dependencies:** first pin of `pydantic-settings` (and `pydantic` if it is a direct import) in `backend/requirements.txt`. Install with uv into `backend/.venv`.
- **Out of impact:** Gradio transcript, conversation-window, input-guardrail, classifier prompt, tools JSON, archives.
