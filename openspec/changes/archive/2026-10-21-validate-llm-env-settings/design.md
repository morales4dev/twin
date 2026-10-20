## Context

See [proposal.md](proposal.md) for why. Requirements live in the `primary-fallback` delta.

Today `backend/src/llm.py` builds a frozen dataclass with `os.getenv(..., default)` then `int(...)`. A present-but-blank env value skips the default. `app.py` already `load_dotenv(override=True)` into `os.environ`. Units patch `litellm.completion` and use `llm_env` to delete blank timeout/model keys so the suite can pass.

Layer 1 already allows Pydantic at non-LLM config boundaries; this is the first product pin. `chat()` stays sequencer only. `classify` / `complete` still take `llm_completion`.

## Goals / Non-Goals

**Goals:**

- Replace the dataclass `int(os.getenv)` path with a typed settings read in `llm.py` that treats blank as unset and names the field on parse failure.
- Keep `completion()` primary-then-fallback and its call signature.
- Point `.env.example` and one `python.md` sentence at the secrets-vs-typed-defaults rule.

**Non-Goals:**

- Design-level restatement of proposal scope. Also: no new module, no second dotenv path, no Pushover settings, no `chat()` change, no archive.

## Decisions

### 1. `pydantic-settings` in `llm.py`; blank is unset

Replace the frozen dataclass with a `BaseSettings` subclass that stays in `backend/src/llm.py`. Enable `env_ignore_empty=True` so `LLM_TIMEOUT=` uses the field default. Do not set `env_file`; keep reading process env after the existing `load_dotenv` in `app.py`. Confirm field-to-env mapping against the pinned docs at apply (Context7).

Keep `get_settings()` as the read. `completion()` still calls it once per LLM call (no sticky settings cache). Let the settings library’s validation error propagate; do not wrap it. Units assert the error text names `LLM_TIMEOUT` and that `litellm.completion` was not called.

Alternative: a two-line `or default` helper around `os.getenv` — rejected. It fixes blank ints but still gives `ValueError` for `LLM_TIMEOUT=abc` with no field name.

Alternative: `env_file` pointed at the repo-root `.env` — rejected. Twin already loads dotenv in `app.py`; a second path from `backend/` cwd is easy to get wrong. Tests keep using `monkeypatch.setenv`.

### 2. Field names match the env keys; defaults stay as specified

Use the env names as fields so a validation error names `LLM_TIMEOUT`, not a private attribute:

| Field | Default |
| --- | --- |
| `PRIMARY_MODEL` | `MiniMax-M2.5` |
| `FALLBACK_MODEL` | `claude-haiku-4-5-20251001` |
| `LLM_TIMEOUT` | `30` |
| `LLM_RETRIES` | `2` |
| `OPENAI_API_KEY` | `None` |
| `OPENAI_BASE_URL` | `None` |
| `ANTHROPIC_API_KEY` | `None` |

`completion()` reads those attributes (`settings.LLM_TIMEOUT`, …). Extra env keys are ignored.

Alternative: keep lowercase dataclass names plus aliases — rejected. The spec wants the error to name `LLM_TIMEOUT`.

### 3. Pin at apply; retarget `test_llm.py`; one standards sentence

Pin current stable `pydantic-settings` in `backend/requirements.txt` (resolve at apply). If production code imports `pydantic` directly (for example `ValidationError`), pin `pydantic` as a direct dep too. Do not pin unused transitives. Install with uv into `backend/.venv`.

`test_llm.py`: drop the `delenv` loop. Cover blank `LLM_TIMEOUT=` / `LLM_RETRIES=` / model names still produce timeout 30, retries 2, and the default model ids; cover `LLM_TIMEOUT=abc` raises and `litellm.completion` is not called. Existing primary / fallback / tools cases stay. No network.

Root `.env.example`: secrets stay `KEY=`; typed LLM keys get the table defaults. `ai-specs/standards/python.md`: “names only” applies to secrets; typed LLM settings in `.env.example` may show their defaults.

**Apply order:**

1. Pin and install.
2. Failing settings units (blank uses default; invalid names the field; no provider call).
3. Replace `LLMSettings` / `get_settings()`; wire `completion()` to the new attributes.
4. `.env.example` + `python.md`.
5. From `backend/`: `.venv/bin/python -m pytest tests/unit`. `openspec validate validate-llm-env-settings --type change`. No archive.

## Risks / Trade-offs

- [Existing machine `.env` still has `LLM_TIMEOUT=`] → Mitigation: `env_ignore_empty=True`; units set the key to `""` and assert the default.
- [Validation error is treated as a primary raise and trips fallback] → Mitigation: fail in `get_settings()` before `_call`. Units assert zero provider calls on `LLM_TIMEOUT=abc`.
- [Forgotten pydantic pin; first import is undeclared] → Mitigation: pin the package we import; install with uv.
- [Settings class grows into a process-wide bag] → Mitigation: only the seven LLM fields; Pushover stays in `tools.py`.

## Migration Plan

No production API version. Operators can keep a blank `LLM_TIMEOUT=` or write `30`. Restart `src/app.py`. Rollback: revert the change commit(s) and reinstall `backend/requirements.txt` into `backend/.venv`. Do not archive until a later explicit user request.
