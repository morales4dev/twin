## Context

See [proposal.md](proposal.md) for why. Layer 2 module shape and MiniMax-in-units rules are live in `ai-specs/standards/python.md` and `ai-specs/standards/testing.md`; this design cites them and does not restate the function table.

Today `backend/src/app.py` `chat(message, history)` inlines extract-plus-record, firewall, Turn A I/O, parse, the lead-ack vs canned fork, and the Turn B tool loop. Units invert MiniMax with `@patch("app.openai.chat.completions.create")` and record with `@patch("app.record_user_details")`. `capture_typed_email` already exists and is unused by `chat()`. `MODEL_NAME` lives in `app.py` next to a module-global `OpenAI()`. Specs are skipped (`skip_specs: true`).

Constraints: Python 3.12.12, sync `OpenAI()` client, existing `backend/.venv` + `backend/requirements.txt` (no new pin), units under `backend/tests/unit/` with no network.

## Goals / Non-Goals

**Goals:**

- Name `chat()` vs the I/O functions (`classify`, `complete`, `fail_closed_reply`) and put each in a home so MiniMax I/O is not added inside `chat()`.
- Wire the locked seams: optional `client` only on `chat()`; required `client` on `classify` / `complete`; ingress fake client; record patch on `email_capture.record_user_details`.

**Non-Goals:**

- Design-level restatement of proposal scope. Also: no new modules beyond the homes below, no Capturer/Pusher, no `ScopeLabel`, no Pydantic, no tool-loop rewrite, no archive in this change.

## Decisions

1. **Homes: existing modules plus one Turn B helper.**

   | Function | Home |
   | --- | --- |
   | `fail_closed_reply(email)` | `backend/src/refusal.py` (already owns canned + lead-ack) |
   | `classify(message, client)` | `backend/src/classifier.py` (Turn A prompt builder stays; this adds I/O + a small result dataclass) |
   | `complete(message, history, client)` | `backend/src/complete.py` (new Turn B helper; keeps the tool loop out of `app.py`) |
   | `chat(message, history, client=None)` | `backend/src/app.py` (sequences only) |

   `chat()` becomes: `capture_typed_email` → firewall → `classify` → `fail_closed_reply` or `complete`. Type hints on these changed public functions. `classify` result is a dataclass (`allowed_for_turn_b` plus reason). Reasons stay `in_scope` / `out_of_scope` / `unparseable` / `error` as Layer 2 names them. `chat()` branches only on `allowed_for_turn_b`.

   Move `MODEL_NAME` into `classifier.py` so `complete.py` and tests can import it without a circular `app` import and without a one-constant module.

   Alternative: keep `classify` / `complete` in `app.py` — rejected (a task that adds MiniMax I/O would still land next to `chat()`).
   Alternative: new `model_name.py` — rejected (YAGNI).
   Alternative: `ScopeLabel` enum or Pydantic result — rejected (proposal lock).

2. **Client seam: optional only on `chat()`.**

   `chat(..., client=None)` does `client = client or openai` and passes that client down. Gradio still calls two arguments. `classify` and `complete` require `client` (no default) so a forgotten unit cannot construct `OpenAI()`. Each function calls `client.chat.completions.create` itself. No shared MiniMax helper.

   Alternative: default `client=None` then `OpenAI()` inside `classify` / `complete` — rejected (`testing.md`: units must not hit the network).
   Alternative: a Protocol for the client — rejected (Layer 2: no Protocols for one implementation).

3. **Test seams: fake MiniMax client; retarget the record patch.**

   Ingress (`backend/tests/unit/test_chat_ingress.py`) still drives `chat()` and keeps the same assertions. Replace `@patch("app.openai.chat.completions.create")` with a fake client passed into `chat()`. A small helper in that test module builds the fake (`create` on the same attribute path the production code calls). Replace `@patch("app.record_user_details")` with `@patch("email_capture.record_user_details")`. New units call `classify` / `complete` with an explicit fake. Do not add “the helper was called” tests as a substitute for ingress.

   Alternative: leave `app.openai` patches because `client or openai` would still honor them — rejected (proposal: that is not the MiniMax test design).
   Alternative: inject a Capturer / Pusher — rejected (proposal; the function chain is enough).

4. **Do not “fix” Layer 1 while extracting.**

   Keep `except Exception` around Turn A I/O inside `classify` (reason `error`). That is the fail-closed contract ingress already locks. Copy the Turn B `while` loop into `complete()` bit-identical. Do not change classifier prompt, parse, firewall patterns, visitor strings, or tool JSON.

   Alternative: named MiniMax errors only — rejected (behavior change).
   Alternative: clean up `handle_tool_calls` or add tool-loop units that rewrite the loop — rejected (untested path; extract only).

5. **TDD, then thin `chat()`, quality gate without CI.**

   Failing tests before production code. Apply on feature branch `feature/refactor-thin-chat-orchestrator` (do not mix with Agent OS commits). Verify with existing `backend/.venv`: from `backend/`, `.venv/bin/python -m pytest tests/unit`, and `openspec validate refactor-thin-chat-orchestrator --type change`. No new pin. No archive.

**Apply order:**

1. Feature branch `feature/refactor-thin-chat-orchestrator` from the revision that already has live Layer 2.
2. Failing `fail_closed_reply` units; add the function in `refusal.py`.
3. Failing `classify` units with an explicit fake client; add `classify` + result dataclass in `classifier.py`; move `MODEL_NAME` there.
4. Failing `complete` unit for the existing one-shot (no tool-calls) path; add `complete.py` with the current loop copied bit-identical.
5. Rewrite ingress tests to the fake client + `email_capture.record_user_details` patch (fail on current `chat()`).
6. Thin `chat()`: optional `client`, `capture_typed_email`, firewall, `classify`, `fail_closed_reply` / `complete`.
7. Verify pytest units (no network) and `openspec validate`; no archive.

## Risks / Trade-offs

- [Ingress rewrite plus extract in one change breaks the visitor contract] → Mitigation: keep the same assertions; run the full ingress file after `chat()` is thinned; golden rule is bit-identical strings.
- [Wrong record patch target hits Pushover] → Mitigation: patch `email_capture.record_user_details`; units must not hit the network.
- [Forgotten fake on `classify` / `complete` opens a real client] → Mitigation: required `client` parameter; no `OpenAI()` default in those functions.
- [Shared MiniMax helper puts `tools=` on Turn A] → Mitigation: two separate `create` calls; ingress still asserts Turn A has no `tools`.
- [Bit-identical `complete()` loop has no multi-round unit] → Mitigation: copy the `while` block verbatim; this change does not add tool-loop tests or rewrite tools.
- [Circular import when moving `MODEL_NAME`] → Mitigation: `MODEL_NAME` lives in `classifier.py`; `app` and `complete` import it; `classifier` does not import `app`.
- [Agents treat this as permission to add a class tree] → Mitigation: proposal + Layer 2 + this design forbid it.

## Migration Plan

No production API version. Apply is git-only on the feature branch. Rollback: revert the change commit(s). Do not uninstall venv packages (pins unchanged). Do not archive until a later explicit user request.
