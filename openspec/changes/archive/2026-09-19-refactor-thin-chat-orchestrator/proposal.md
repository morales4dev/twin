## Why

`chat()` is the Gradio adapter and the design: it extracts email, records it, runs the firewall, performs Turn A I/O, parses the label, picks lead-ack vs canned, then runs Turn B and the tool loop. Tests invert a module-global `OpenAI()` with patches. That thickness is a smell. This change improves the design of the existing code.

## What Changes

This change is a **refactor**. Golden rule: **do not change behavior** of the twin or of its components (classifier, firewall, email capture, refusals, tools, Turn A / Turn B). Visitor-facing strings stay bit-identical. Ingress **assertions** stay the contract (same replies, same Turn A / Turn B / `tools=` checks). Specs are skipped (`skip_specs: true`).

Align `backend/src` to the live Layer 2 module shape and MiniMax-in-units rules in `ai-specs/standards/python.md` and `ai-specs/standards/testing.md`. Design and tasks cite those standards; they do not restate the function table.

This change also locks:

- Use existing `capture_typed_email` instead of inlining extract-plus-record in `chat()`. Ingress retargets the record patch to `email_capture.record_user_details` so units do not call Pushover. Do not keep `@patch("app.record_user_details")` after that switch.
- `chat(message, history, client=None)` is the only optional client. Gradio still calls two arguments. Launch uses the real client. `classify` and `complete` require `client` (no default) so a unit cannot construct `OpenAI()` by accident.
- Ingress tests migrate to a fake client passed into `chat()`. Patching `app.openai` is not the MiniMax test design. New units call `classify` / `complete` with an explicit fake.
- No `ScopeLabel` enum. No Pydantic and no `pydantic` pin. A `classify` result stays a small dataclass or equivalent.
- Keep fail-closed-on-any-exception (`except Exception`) as the product contract. Extract `complete()` bit-identical; do not rewrite the tool loop.

**Non-goals**

- Product capability specs under `openspec/specs/` (existing `prompt-firewall` and `scope-classifier` stay untouched; none will be invented).
- Changing visitor-facing copy, firewall deny patterns, classifier prompt or parse rules, or tool behavior.
- Tightening exception handling or rewriting the Turn B tool loop while extracting.
- Agent OS edits (`ai-specs/`, `openspec/config.yaml`, OpenSpec CLI skills). Those belong to `add-backend-shape-standards` (already applied).
- A `Chat` / `Classifier` / `Firewall` class tree, a Capturer or Pusher interface, Protocols for one implementation, FastAPI, or an async rewrite of chat.
- A `ScopeLabel` enum, a Pydantic model, or a first `pydantic` pin.
- Replacing ingress tests with “the helper was called.” Ingress tests still drive `chat()`.
- Keeping `@patch("app.openai...")` as the MiniMax inversion after the injection seam exists, or keeping `@patch("app.record_user_details")` after `chat()` uses `capture_typed_email`.
- Archiving this change (archive only after a later explicit user request).

No **BREAKING** API or Gradio UX change.

## Capabilities

### New Capabilities

- None. This change does not introduce product behavior. `skip_specs: true` is set on the change.

### Modified Capabilities

- None. Existing `prompt-firewall` and `scope-classifier` requirements do not change.

## Impact

- **App code:** `backend/src/app.py` and small collaborators next to the existing modules (`classifier`, `refusal`, `email_capture`, and a Turn B helper). No visitor-facing string changes.
- **Tests:** `backend/tests/unit/test_chat_ingress.py` keeps the same assertions and still drives `chat()`. Those tests pass a fake client instead of patching `app.openai`, and patch `email_capture.record_user_details` instead of `app.record_user_details`. New units call `classify` / `complete` with an explicit fake. Units still must not hit the network.
- **Agent OS:** no required edits. Layer 2 is already live; design and tasks cite it.
- **OpenSpec:** change metadata `skip_specs: true`.
- **Dependencies:** no pin changes (no `pydantic`).
- **Out of impact:** product specs, operator README dump, live MiniMax E2E, MCP config, CI.
