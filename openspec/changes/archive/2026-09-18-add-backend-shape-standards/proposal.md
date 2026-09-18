## Why

Twin's Python and testing standards already name SOLID, DRY, Pydantic, and mocked I/O, but Layer 2 is pins and layout, not module shape. First apply of a user story still dumps MiniMax I/O, parse, and visitor copy into `chat()`, then needs a later refactor. Agents need an operational default so the first apply already writes a thin orchestrator.

## What Changes

This change is Agent OS only. It does **not** change visitor-facing twin behavior and does **not** edit `backend/src/**`. Specs are skipped (`skip_specs: true`).

- Thicken `ai-specs/standards/python.md` Layer 2 with Twin module shape and anti-patterns: `chat()` sequences only; MiniMax I/O lives in functions (`classify`, `complete`, …); `classify` returns a result (allowed-for-Turn-B plus reason), not visitor strings; fail-closed reply is one function and is used only after Turn A; firewall plus typed email stays canned; inject the MiniMax client into `chat()` (optional kwarg); no shared MiniMax helper that could put `tools=` on Turn A; KISS, YAGNI, and DRY win over a class tree.
- Thicken `ai-specs/standards/testing.md` Layer 2: units that need MiniMax take a fake client or call `classify` / `complete` directly; patching `app.openai` is not the design.
- Add `openspec/config.yaml` design and task rules: a change that touches `backend/src` names `chat()` vs the I/O functions; a task that adds MiniMax I/O does not put that I/O in `chat()`.
- Add one load sentence to `ai-specs/AGENTS.md` under Stack: before editing `backend/src`, read `python.md` Layer 2 and `testing.md` Layer 2. Do not paste those standards into the constitution.
- Do not add a project skill. Shape rules stay in standards so apply loads them without an extra invoke.
- Current `backend/src` may not yet match Layer 2. Aligning the app is a separate change (`refactor-thin-chat-orchestrator`). This change does not perform that refactor.

**Non-goals**

- Product capability specs under `openspec/specs/` (existing `prompt-firewall` and `scope-classifier` stay untouched; none will be invented).
- Visitor-facing Gradio chat, `backend/src/**`, pins, or tests.
- Implementing the thin-`chat()` refactor (that is `refactor-thin-chat-orchestrator`).
- A new project skill, a second constitution, or always-apply `.cursor/rules/` that paste standards.
- Mandating a class hierarchy, Protocols for one implementation, FastAPI, or an async rewrite of chat.
- Changing canned refusal or `LEAD_ACK` text.
- Archiving this change (archive only after a later explicit user request).

No **BREAKING** API or Gradio UX change.

## Capabilities

### New Capabilities

- None. This change does not introduce product behavior. `skip_specs: true` is set on the change.

### Modified Capabilities

- None. Existing `prompt-firewall` and `scope-classifier` requirements do not change.

## Impact

- **Agent OS:** `ai-specs/standards/python.md` Layer 2, `ai-specs/standards/testing.md` Layer 2, one load sentence in `ai-specs/AGENTS.md`. Root `AGENTS.md` stays thin. Project skills stay under `ai-specs/skills/`.
- **OpenSpec:** change metadata `skip_specs: true`; design and task rules in `openspec/config.yaml`.
- **App code:** no required change to `backend/src/**`.
- **Dependencies:** no pin changes.
- **Docs:** standards and constitution load rule only. Do not dump the constitution into README.
- **Out of impact:** visitor chat, firewall/classifier specs, live MiniMax E2E, MCP config, CI.
