## Context

See [proposal.md](proposal.md) for why. Requirements live in the `conversation-window` spec and the `scope-classifier` delta.

Today `complete()` builds Turn B as `system + history + current user` with no cap. `chat()` sequences `capture_typed_email` → `matches_input_guardrail` → `classify` → `fail_closed_reply` / `complete` and passes Gradio’s `history` through unchanged. Gradio 6.26 `ChatInterface` already gives `fn` a list of OpenAI-style `{role, content}` dicts for **prior** turns only; the current user string is the first argument and is not in that list. After `fn` returns, Gradio appends the user bubble and the assistant reply to the on-screen transcript.

This change is drop-oldest only. Do not add a session store, summarization, anchors, or a metadata extractor.

Constraints: Python 3.12.12, sync Gradio `ChatInterface`, `backend/.venv` + `backend/requirements.txt` (no new pin), units under `backend/tests/unit/` with no network. `chat()` stays sequencer only. MiniMax I/O stays in `classify` / `complete` / `llm.completion`.

## Goals / Non-Goals

**Goals:**

- Apply the 8-turn cap once, when `complete()` builds the first Turn B `messages` list, from a slice/copy of `history`.
- Keep the current-turn tool loop appending to that already-windowed list.
- Lock both sides of the cap (and that `history` is not mutated) in `complete()` units.

**Non-Goals:**

- Design-level restatement of proposal scope. Also: no new module, no env-configurable window size, no session store / summarization / anchors / metadata extractor, no `chat()` sequence change, no archive.

## Decisions

### 1. Window inside `complete()`, not `chat()`

`chat()` still receives Gradio’s full `history` and still passes that same list into `complete()`. The visible transcript stays Gradio’s job. Windowing is Turn B message construction only:

```python
messages = system + window_history(history) + [{"role": "user", "content": message}]
```

The existing `while finish_reason == "tool_calls"` loop is unchanged: it appends the assistant tool-call message and tool results onto that `messages` list. It does not re-read `history` and does not restore dropped turns.

Alternative: window in `chat()` before calling `complete()` — rejected. That would make the sequencer own payload shape, and a later `complete()` caller could skip the cap. Layer 2 keeps MiniMax message build in `complete()`.

Alternative: window again on every tool-loop iteration — rejected. The spec keeps the same windowed prior turns for the current turn; re-slicing would only matter if the loop grew prior history, which it does not.

### 2. Small helper in `complete.py`; 8 turns is 16 history messages

Keep the helper next to `complete()` in `backend/src/complete.py`. A prior turn is one user dict plus the assistant dict that follows it. Gradio’s completed `history` is even-length pairs, so the window is the newest `8 * 2` messages:

```python
MAX_WINDOW_TURNS = 8

def window_history(history: list) -> list:
    return history[-(MAX_WINDOW_TURNS * 2):]
```

A Python slice is a new list. Do not `del`, `pop`, or assign back into the caller’s `history`. `MAX_WINDOW_TURNS` is a module constant, not an env setting.

If `history` is shorter than 16 messages, the slice returns all of it. The current user string is appended after the slice and is never part of the cap.

Alternative: new `conversation_window.py` — rejected (YAGNI; one slice).

Alternative: pair-walking that inspects `role` and repairs odd-length lists — rejected. Gradio 6.26 always appends user then assistant after each turn. Units build well-formed pairs. Do not add a parser for a shape the UI does not produce.

Alternative: env-configurable cap — rejected. The spec hard-codes 8.

### 3. Units drive `complete()`; ingress stays on the existing contract

Extend `backend/tests/unit/test_complete.py`. Fake `llm_completion`. No network.

| Case | Arrange | Assert on first `llm_completion` `messages` |
| --- | --- | --- |
| Under cap | 8 prior turns or fewer | every history message present; current user last |
| Over cap | more than 8 prior turns | oldest pair absent; newest 8 pairs present; current user last; no summary/anchor/metadata message |
| No mutate | over-cap list | the `history` object still has every prior turn after `complete()` returns |
| Tool loop | over-cap history; first call returns `tool_calls`, second `stop` | both calls keep the same windowed prior turns; dropped turns stay absent |

A canned-refusal assistant string inside the newest 8 pairs is just another history message (present). The same string older than the newest 8 is absent. No separate production branch.

`test_chat_ingress.py` still asserts Turn A omits tools, Turn B sends tools, fail-closed strings, and zero LLM calls on the guardrail. It does not need to grow Turn B `messages` assertions; those belong on `complete()`. `classify` stays stateless.

TDD: failing `complete()` units first, then `window_history` + the one-line change in `complete()`.

A names-only `.env` sets `LLM_TIMEOUT=` (and the other numeric/model names) to empty strings. `get_settings()` then does `int("")` and the unit suite fails. This change does not fix production settings. `llm_env` in `test_llm.py` deletes those keys so `getenv` uses the defaults. A later change owns env validation.

**Apply order:**

1. Failing window units in `test_complete.py`.
2. Add `MAX_WINDOW_TURNS` + `window_history` in `complete.py`; use the slice when building `messages`.
3. Isolate blank timeout/model env in `llm_env`; then from `backend/`: `.venv/bin/python -m pytest tests/unit`. `openspec validate add-conversation-window --type change`. No archive.

## Risks / Trade-offs

- [Oldest recruiter facts fall out of the model after 8 turns] → Mitigation: accepted. Recruiter chats are short; the spec is drop-oldest, not summarize. The visitor still sees the full thread.
- [Mutating `history` would drop bubbles from Gradio] → Mitigation: slice only. Units assert the input list is unchanged. Gradio 6.26 also passes `list(history)` into `fn`, but `complete()` must still be safe when tests call it directly.
- [Windowing in `chat()` would hide the cap from other `complete()` callers] → Mitigation: the cap lives in `complete()` only.
- [Adding summarization or a session store would add LLM I/O and state Twin does not have] → Mitigation: drop-oldest only; no summary, anchors, metadata, or process-local store.
- [Odd-length or tuple-format history would slice mid-pair] → Mitigation: Gradio 6.26 `ChatInterface` history is OpenAI-style dict pairs; units build that shape. Do not add a compatibility converter.
- [Names-only `.env` blanks fail `test_llm.py` and block the quality gate] → Mitigation: delete those keys in `llm_env` only. Do not change production `get_settings()`.

## Migration Plan

No production API version and no new pin. Apply is git-only. Restart `src/app.py` after merge so the running ChatInterface picks up `complete()`. Rollback: revert the change commit(s). Do not archive until a later explicit user request.
