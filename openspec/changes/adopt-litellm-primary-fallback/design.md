## Context

See [proposal.md](proposal.md) for why. Requirements live in the `primary-fallback` spec and the `input-guardrail` / `scope-classifier` deltas.

Today `classify` and `complete` call `client.chat.completions.create` on one hardcoded `MODEL_NAME` (`MiniMax-M2.5`). `app.py` constructs `OpenAI()` and injects it into `chat()`. Turn A wraps that `create` in `except Exception` and fail-closes; Turn B lets the exception through. Units fake `client.chat.completions.create`. There is no timeout, no retry, and no second model.

estimador-cag has the same setting names (`PRIMARY_MODEL`, `FALLBACK_MODEL`, `LLM_TIMEOUT`) and a LiteLLM wrapper, but its live path calls primary only. Twin implements the two-model rule here; do not copy Instructor, Router, cache, or cost tables.

Constraints: Python 3.12.12, sync Gradio `ChatInterface`, `backend/.venv` + `backend/requirements.txt`, units under `backend/tests/unit/` with no network. `chat()` stays sequencer only. `add-conversation-window` and the other in-flight proposals are not edited.

## Goals / Non-Goals

**Goals:**

- One LiteLLM I/O helper that `classify` and `complete` call, with primary-then-fallback, timeout, and same-model transport retries.
- Replace the `OpenAI()` injection seam with that helper. No `openai` or `anthropic` imports in `backend/src`.
- Retarget units to the new seam. Rename MiniMax-named test helpers.
- Update Agent OS, `openspec/config.yaml`, live spec Purpose lines, and the operator README so they say primary / fallback / LLM call.

**Non-Goals:**

- Design-level restatement of proposal scope. Also: no LiteLLM `Router`, no `completion(..., fallbacks=...)`, no pydantic-settings, no structured-output retries, no cache, no wait UI, no archive.

## Decisions

### 1. New `backend/src/llm.py` owns settings and the call

Add `llm.py` with a frozen settings dataclass (env + defaults) and one sync function:

```python
def completion(messages: list, *, tools: list | None = None) -> object:
```

Settings (names in `.env.example` only):

| Name | Default |
| --- | --- |
| `PRIMARY_MODEL` | `MiniMax-M2.5` |
| `FALLBACK_MODEL` | `claude-haiku-4-5-20251001` |
| `LLM_TIMEOUT` | `30` |
| `LLM_RETRIES` | `2` |
| `OPENAI_API_KEY` / `OPENAI_BASE_URL` | kept (primary) |
| `ANTHROPIC_API_KEY` | added (fallback) |

Read env at call time via a small `get_settings()` (existing `python-dotenv` in `app.py` is enough). Do not add Pydantic or `pydantic-settings`.

`MODEL_NAME` in `classifier.py` goes away. `classify` and `complete` do not choose a model.

Alternative: keep settings next to `MODEL_NAME` in `classifier.py` — rejected; complete and tests would keep importing classifier for model config.

Alternative: `pydantic-settings` like estimador-cag — rejected; first pydantic pin is not needed for six env values.

### 2. Own the primary → fallback switch; pass timeout and retries into each LiteLLM call

`llm.completion` tries primary, then fallback. Each attempt is `litellm.completion(...)` (sync). Per LiteLLM input docs, pass `timeout` and `num_retries` on that call. `LLM_RETRIES=2` is LiteLLM `num_retries=2` (two tenacity retries on that model). After the primary call raises, try fallback with the same `timeout` / `num_retries`. After fallback raises, the helper raises and that LLM call has failed.

Primary kwargs: `model=f"openai/{PRIMARY_MODEL}"`, `api_key=OPENAI_API_KEY`, `api_base=OPENAI_BASE_URL`. The `openai/` prefix is how LiteLLM routes a custom OpenAI-compatible endpoint ([OpenAI-compatible endpoints](https://docs.litellm.ai/docs/providers/openai_compatible)). Fallback kwargs: `model=FALLBACK_MODEL`, `api_key=ANTHROPIC_API_KEY`, no custom `api_base`.

Pass `tools=` only when the caller supplied them. Turn A calls `llm_completion(messages)`; Turn B calls `llm_completion(messages, tools=tools)`.

Do not import `openai` or `anthropic` in `backend/src`. Pin `litellm` in `backend/requirements.txt` (resolve the current stable at apply; PyPI stable on 2026-10-20 was `1.106.1`). Drop the direct `openai==3.8.0` pin. Do not pin LiteLLM transitives.

Disable LiteLLM telemetry at process start using the documented flag on the pinned version (commonly `litellm.telemetry = False`). Confirm against the pin at apply; do not invent a second telemetry API.

Alternative: LiteLLM `Router` — rejected (proposal non-goal; adds deployment health/cooldowns Twin does not need).

Alternative: one `litellm.completion(..., fallbacks=[FALLBACK_MODEL])` — rejected. LiteLLM tries each fallback entry once and does not document combining that list with per-model `num_retries` the way the spec requires (retries on primary, then the same retry rule on fallback).

Alternative: a Python retry loop with `num_retries=0` — rejected; LiteLLM already implements same-model retries. Units assert we pass `timeout` and `num_retries`, and that a raised primary call is followed by one fallback call.

### 3. Injectable callable, not an OpenAI-shaped client

Layer 2 today injects `client` with `client.chat.completions.create`. That shape is the old SDK. Replace it:

| Function | Seam |
| --- | --- |
| `chat(message, history, llm_completion=None)` | optional; `llm_completion = llm_completion or llm.completion` |
| `classify(message, llm_completion)` | required |
| `complete(message, history, llm_completion)` | required |

Gradio still calls two arguments. `classify` keeps `except Exception` → reason `error` (both-fail is now “the helper raised”). `complete` still does not catch; Turn B both-fail still surfaces to Gradio.

Each `complete()` tool-loop iteration calls `llm_completion` again, so it starts at primary. No sticky model.

Alternative: keep `client.chat.completions.create` and wrap LiteLLM in a duck-typed client — rejected; tests and standards would keep pretending the vendor SDK is the architecture.

Alternative: default `llm_completion=llm.completion` on `classify` / `complete` — rejected; a forgotten unit would hit the network.

### 4. Tests fake `llm_completion` or `litellm.completion`, not `OpenAI()`

- `llm.py` units: patch `litellm.completion`. Cover primary success (no fallback call), primary raise → fallback success, both raise, `timeout` / `num_retries` passed, `openai/` + `api_base` on primary, no `tools` key when omitted, `tools` present when passed.
- `classify` / `complete` / ingress: pass a fake callable. Ingress still asserts Turn A omits tools, Turn B sends tools, guardrail makes zero LLM calls, fail-closed strings unchanged. Move `MODEL_NAME` assertions into `llm.py` units. Rename helpers/tests that say `minimax` (`skips_minimax` → `skips_llm`, error fixtures that say “minimax down”).
- Units still must not hit the network. No Playwright live-model suite.

TDD: failing `llm.py` units first, then the helper; then retarget classify/complete/chat tests; then production signature changes.

### 5. Agent OS, config, README, live Purpose — vocabulary only plus the new seam

At apply, edit these so they match the code:

- `ai-specs/standards/python.md`: model I/O is sync LiteLLM via `llm.completion`; inject `llm_completion`; pin table swaps `openai` for `litellm`; module table uses the new signatures; drop “no shared MiniMax helper” in favor of “shared helper must pass tools through.”
- `ai-specs/standards/testing.md`: fake `llm_completion` / patch `litellm.completion`; “LLM in units”, not “MiniMax in units”; Playwright slot still not a live-model suite.
- `ai-specs/standards/context7.md`: resolve the LiteLLM Context7 ID at apply and replace the `openai` row.
- `openspec/config.yaml`: context/rules say primary / fallback / LLM call, not MiniMax-as-architecture.
- Live `openspec/specs/input-guardrail/spec.md` and `scope-classifier/spec.md` Purpose lines (deltas cannot carry Purpose).
- Root `README.md` stack sentence (operator onboarding; constitution: update docs this change makes stale).

Do not edit `add-conversation-window` or other in-flight change markdown. The proposal still says `prompt-firewall`; leave that file unless a later update pass retitles it to `input-guardrail` (the delta already uses the live path).

**Apply order:**

1. Pin `litellm`, drop `openai`, install into `backend/.venv` with uv.
2. Failing `llm.py` units; add `llm.py` (settings + `completion`).
3. Failing retarget of `test_classifier.py` / `test_complete.py` / `test_chat_ingress.py` to the callable seam; update `classify` / `complete` / `chat()`.
4. `.env.example` names; Agent OS + `openspec/config.yaml` + live Purpose + README.
5. From `backend/`: `.venv/bin/python -m pytest tests/unit`. `openspec validate adopt-litellm-primary-fallback --type change`. No archive.

## Risks / Trade-offs

- [LiteLLM `num_retries` plus our fallback is two layers] → Mitigation: helper makes one LiteLLM call per model and does not implement a second retry loop. Units assert kwargs and the primary→fallback switch, not tenacity internals.
- [Shared helper puts `tools=` on Turn A] → Mitigation: omit the `tools` key unless the caller passed tools; classify never passes it; ingress still asserts the omit.
- [Forgotten fake on `classify` / `complete` opens a live call] → Mitigation: required `llm_completion` parameter; no default.
- [Tool-loop message objects from LiteLLM differ from the OpenAI SDK] → Mitigation: keep reading `choices[0].message` / `finish_reason` / `tool_calls` (LiteLLM `ModelResponse` is OpenAI-shaped). If append-to-messages breaks, normalize at the helper boundary; do not rewrite `handle_tool_calls` or tool JSON.
- [Custom MiniMax endpoint is mis-routed as OpenAI-hosted] → Mitigation: always call primary as `openai/{PRIMARY_MODEL}` with `api_base=OPENAI_BASE_URL`.
- [LiteLLM telemetry or extra network on import] → Mitigation: disable telemetry at process start; unit smoke must still not hit the network.
- [Visitor wait grows: retries then fallback, up to ~3 minutes worst case] → Mitigation: accepted; no wait UI (non-goal). Timeout stays 30s per attempt.
- [Turn B both-fail is still an uncaught Gradio error] → Mitigation: unchanged; fail-closed canned/LEAD_ACK is Turn A only.
- [Malicious historical LiteLLM wheels] → Mitigation: do not pin `1.82.7` or `1.82.8`; pin current stable at apply.

## Migration Plan

No production API version. Operators add `ANTHROPIC_API_KEY` (and optional overrides) to root `.env`; existing `OPENAI_API_KEY` / `OPENAI_BASE_URL` keep working for primary. Restart `src/app.py`. Rollback: revert the change commit(s) and reinstall `backend/requirements.txt` into `backend/.venv`. Do not archive until a later explicit user request.
