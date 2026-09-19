## 1. Setup

- [x] 1.1 Create and switch to `feature/refactor-thin-chat-orchestrator` from the revision that already has live Layer 2 (do not apply on an Agent OS-only branch) and verify `git branch --show-current` prints that name.

## 2. fail_closed_reply

- [x] 2.1 Add failing units in `backend/tests/unit/test_refusal.py` for `fail_closed_reply(None)` → canned and `fail_closed_reply(email)` → lead-ack, run them from `backend/` with `.venv/bin/python -m pytest tests/unit/test_refusal.py`, and verify they fail because the function is missing.
- [x] 2.2 Add `fail_closed_reply(email)` in `backend/src/refusal.py` (lead-ack vs canned only; no firewall path) and verify `tests/unit/test_refusal.py` passes.

## 3. classify (Turn A I/O, not in chat)

- [x] 3.1 Add failing units in `backend/tests/unit/test_classifier.py` that call `classify(message, client)` with an explicit fake client (in_scope / out_of_scope / unparseable / error; no `tools=` on create; no visitor strings) and verify they fail because `classify` is missing.
- [x] 3.2 Add `classify(message, client)` plus a small result dataclass in `backend/src/classifier.py` (required `client`, existing prompt builder + parse, `except Exception` → reason `error`), move `MODEL_NAME` there, re-export it from `app.py` so current ingress imports still resolve, and verify `tests/unit/test_classifier.py` passes and `chat()` still contains no `classify` I/O.

## 4. complete (Turn B I/O, not in chat)

- [x] 4.1 Add a failing unit in `backend/tests/unit/test_complete.py` that calls `complete(message, history, client)` with an explicit fake client for the existing one-shot (no tool-calls) path and asserts `tools=` and `MODEL_NAME`, and verify it fails because `complete` is missing.
- [x] 4.2 Add `backend/src/complete.py` with `complete(message, history, client)` (required `client`; copy the current Turn B `while` loop bit-identical; no shared MiniMax helper) and verify `tests/unit/test_complete.py` passes and that I/O was not added inside `chat()`.

## 5. Ingress seams and thin chat()

- [x] 5.1 Rewrite `backend/tests/unit/test_chat_ingress.py` to pass a fake client into `chat()` and to `@patch("email_capture.record_user_details")` (same assertions as today) and verify those tests fail on the current `chat()` signature and record import path.
- [x] 5.2 Thin `chat(message, history, client=None)` in `backend/src/app.py` to sequence only: `capture_typed_email`, firewall, `classify`, then `fail_closed_reply` or `complete` (no MiniMax `create` in `chat()`) and verify `tests/unit/test_chat_ingress.py` passes with no network.

## 6. Verify (no spec invention, no archive)

- [x] 6.1 From `backend/`, run `.venv/bin/python -m pytest tests/unit` and verify all units pass with no network.
- [x] 6.2 Confirm `openspec/specs/prompt-firewall` and `openspec/specs/scope-classifier` were not edited, and verify no files exist under `openspec/changes/refactor-thin-chat-orchestrator/specs/`.
- [x] 6.3 Run `openspec validate refactor-thin-chat-orchestrator --type change` from Twin and verify it succeeds with `skip_specs: true`.
- [x] 6.4 Confirm no Capturer/Pusher, no `ScopeLabel`, no `pydantic` pin, and no `openspec archive` was run.
