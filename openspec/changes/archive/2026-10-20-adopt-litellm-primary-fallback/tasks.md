## 1. Pin LiteLLM

- [x] 1.1 In `backend/requirements.txt`, pin current stable `litellm` from PyPI (resolve at apply; do not pin `1.82.7` or `1.82.8`; do not pin transitives), remove the direct `openai==3.8.0` pin, install with `uv pip install --python backend/.venv/bin/python -r backend/requirements.txt` from the repo root, and verify `backend/.venv/bin/python -c "import litellm"` succeeds and `openai` is gone from `backend/requirements.txt`.

## 2. llm.completion helper

- [x] 2.1 Add failing units in `backend/tests/unit/test_llm.py` that patch `litellm.completion` and cover: primary success (no second call), primary raise then fallback success, both raise, `timeout` and `num_retries` passed on each call, primary `model` is `openai/{PRIMARY_MODEL}` with `api_base` and `OPENAI_API_KEY`, fallback uses `FALLBACK_MODEL` and `ANTHROPIC_API_KEY` without a custom `api_base`, `tools` omitted when not passed and present when passed; run from `backend/` with `.venv/bin/python -m pytest tests/unit/test_llm.py`; and verify they fail because `llm.py` is missing.
- [x] 2.2 Add `backend/src/llm.py` with `get_settings()` defaults (`PRIMARY_MODEL=MiniMax-M2.5`, `FALLBACK_MODEL=claude-haiku-4-5-20251001`, `LLM_TIMEOUT=30`, `LLM_RETRIES=2`) and sync `completion(messages, *, tools=None)` that calls `litellm.completion` for primary then fallback (no `Router`, no `fallbacks=`), disables LiteLLM telemetry using the documented flag on the pinned version, and does not import `openai` or `anthropic`; run from `backend/` with `.venv/bin/python -m pytest tests/unit/test_llm.py`; and verify those units pass with no network.

## 3. classify (Turn A I/O stays out of chat)

- [x] 3.1 Rewrite `backend/tests/unit/test_classifier.py` so `classify(message, llm_completion)` takes a required fake callable (in_scope / out_of_scope / unparseable / error; one call; no `tools` kwarg; no visitor strings; rename the “minimax down” fixture), run from `backend/` with `.venv/bin/python -m pytest tests/unit/test_classifier.py`, and verify the tests fail on the current `client` signature.
- [x] 3.2 Change `classify(message, llm_completion)` in `backend/src/classifier.py` to call `llm_completion(messages)` (no default, drop `MODEL_NAME`, keep `except Exception` → reason `error`, keep the existing prompt builder and parse), and verify `tests/unit/test_classifier.py` passes and `chat()` still contains no classify I/O.

## 4. complete (Turn B I/O stays out of chat)

- [x] 4.1 Rewrite `backend/tests/unit/test_complete.py` so `complete(message, history, llm_completion)` takes a required fake callable for the existing one-shot path and asserts `tools=` is passed (no `MODEL_NAME` assert), run from `backend/` with `.venv/bin/python -m pytest tests/unit/test_complete.py`, and verify the test fails on the current `client` signature.
- [x] 4.2 Change `complete(message, history, llm_completion)` in `backend/src/complete.py` to call `llm_completion(messages, tools=tools)` on each loop iteration (required callable, no default, keep the current tool loop and do not catch), and verify `tests/unit/test_complete.py` passes and that I/O was not added inside `chat()`.

## 5. chat() seam and ingress

- [x] 5.1 Rewrite `backend/tests/unit/test_chat_ingress.py` to pass a fake `llm_completion` into `chat()` (same visitor assertions as today: guardrail → zero calls + canned; in-scope → two calls, Turn A omits tools, Turn B sends tools; out-of-scope / unparseable / raise → one call, no tools, canned or LEAD_ACK), rename `skips_minimax` and “minimax down” names to LLM wording, run from `backend/` with `.venv/bin/python -m pytest tests/unit/test_chat_ingress.py`, and verify those tests fail on the current `client` signature.
- [x] 5.2 Change `chat(message, history, llm_completion=None)` in `backend/src/app.py` to sequence only `capture_typed_email` → `matches_input_guardrail` → `classify` → `fail_closed_reply` / `complete`, default `llm_completion` to `llm.completion`, remove `from openai import OpenAI` and the module-global client, and verify `tests/unit/test_chat_ingress.py` passes with no network and `chat()` still contains no LiteLLM call.

## 6. Env, Agent OS, and stale docs

- [x] 6.1 Add `ANTHROPIC_API_KEY`, `PRIMARY_MODEL`, `FALLBACK_MODEL`, `LLM_TIMEOUT`, and `LLM_RETRIES` to root `.env.example` (keep `OPENAI_API_KEY` / `OPENAI_BASE_URL`; names only, no secrets) and verify those names appear and no secret values were added.
- [x] 6.2 Update `ai-specs/standards/python.md` (LiteLLM via `llm.completion`, inject `llm_completion`, pin table swaps `openai` for `litellm`, module table uses the new signatures, shared helper must pass tools through), `testing.md` (fake `llm_completion` / patch `litellm.completion`; “LLM in units”; Playwright is not a live-model suite), and `context7.md` (resolve the LiteLLM Context7 ID at apply and replace the `openai` row), and verify those files no longer treat MiniMax/`OpenAI()` as the architecture.
- [x] 6.3 Update `openspec/config.yaml` context/rules, the Purpose lines in live `openspec/specs/input-guardrail/spec.md` and `openspec/specs/scope-classifier/spec.md`, root `README.md` stack sentence, `backend/tests/unit/test_imports.py` (import `llm`, no `openai` in `app`), and the e2e placeholder wording in `backend/tests/e2e/test_gradio_chat_placeholder.py`, and verify they say primary / fallback / LLM call and that `add-conversation-window` was not edited.

## 7. Verify (no archive)

- [x] 7.1 From `backend/`, run `.venv/bin/python -m pytest tests/unit` and verify all units pass with no network.
- [x] 7.2 Confirm `backend/src` has no `openai` or `anthropic` imports, `chat()` still sequences only, deny-list / canned / LEAD_ACK / classifier prompt / tools JSON were not changed, and no LiteLLM `Router` or `fallbacks=` was added.
- [x] 7.3 Run `openspec validate adopt-litellm-primary-fallback --type change` from Twin, verify it succeeds, and confirm no `openspec archive` was run.
