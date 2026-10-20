## 1. Pin pydantic-settings

- [x] 1.1 In `backend/requirements.txt`, pin current stable `pydantic-settings` from PyPI (and `pydantic` too if apply will import it directly; do not pin unused transitives), install with `uv pip install --python backend/.venv/bin/python -r backend/requirements.txt` from the repo root, and verify `backend/.venv/bin/python -c "import pydantic_settings"` succeeds.

## 2. Failing settings units

- [x] 2.1 In `backend/tests/unit/test_llm.py`, add units that set `LLM_TIMEOUT=`, `LLM_RETRIES=`, `PRIMARY_MODEL=`, and `FALLBACK_MODEL=` (do not delete those keys) and assert `completion()` still uses timeout 30, retries 2, primary `openai/MiniMax-M2.5`, and fallback `claude-haiku-4-5-20251001`; add a unit that sets `LLM_TIMEOUT=abc` and asserts the settings read fails with an error that names `LLM_TIMEOUT` and that `litellm.completion` is not called; drop the `llm_env` `delenv` loop; run from `backend/` with `.venv/bin/python -m pytest tests/unit/test_llm.py`; and verify the new cases fail on the current `int(os.getenv)` path.

## 3. Typed settings in llm.py (I/O stays out of chat)

- [x] 3.1 In `backend/src/llm.py`, replace the dataclass `get_settings()` with a `pydantic-settings` `BaseSettings` object (`env_ignore_empty=True`, no `env_file`, extra env ignored, the seven LLM fields and defaults from the design), wire `completion()` to those attributes, leave the primary-then-fallback `_call` loop unchanged, and do not put this read in `chat()`; run from `backend/` with `.venv/bin/python -m pytest tests/unit/test_llm.py`; and verify those units pass with no network.

## 4. Example env and standards

- [x] 4.1 In root `.env.example`, keep secret keys blank and set `PRIMARY_MODEL=MiniMax-M2.5`, `FALLBACK_MODEL=claude-haiku-4-5-20251001`, `LLM_TIMEOUT=30`, `LLM_RETRIES=2`; in `ai-specs/standards/python.md` change “names only” so it applies to secrets and allows typed LLM defaults in `.env.example`; and verify those files contain the defaults and no secret values.

## 5. Verify (no chat() I/O, no archive)

- [x] 5.1 From `backend/`, run `.venv/bin/python -m pytest tests/unit` and verify all units pass with no network, including unchanged ingress and conversation-window cases.
- [x] 5.2 Confirm `chat()` in `backend/src/app.py` still sequences only `capture_typed_email` → `matches_input_guardrail` → `classify` → `fail_closed_reply` / `complete`, `complete.py` and `classifier.py` were not edited, and no process-wide settings bag or Pushover validation was added.
- [x] 5.3 Run `openspec validate validate-llm-env-settings --type change` from Twin, verify it succeeds, and confirm no `openspec archive` was run and no live spec under `openspec/specs/` was hand-edited.
