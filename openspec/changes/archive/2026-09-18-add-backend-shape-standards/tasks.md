## 1. Setup

- [x] 1.1 Create and switch to `feature/add-backend-shape-standards` from Twin's default branch (do not apply on the same branch as `refactor-thin-chat-orchestrator`) and verify `git branch --show-current` prints that name.

## 2. Layer 2 standards

- [x] 2.1 Under `## Layer 2 — Twin stack` in `ai-specs/standards/python.md`, add a short module-shape heading (not Layer 3, not under `## LLM protocol (targets only)`) that names `chat()` as sequences only, `classify(message, client)` as Turn A I/O that omits `tools=` and returns `allowed_for_turn_b` plus reason (`in_scope` / `out_of_scope` / `unparseable` / `error`) with no visitor strings, `complete(message, history, client)` as Turn B plus the tool loop, and `fail_closed_reply(email)` as lead-ack vs canned used only after Turn A, and verify those four names appear under Layer 2 while existing pin/layout bullets and the LLM-protocol target heading stay intact.
- [x] 2.2 In that same python.md Layer 2 subsection, encode the anti-patterns: firewall plus typed email stays canned; inject the MiniMax client into `chat()` as an optional kwarg; no shared MiniMax helper that could put `tools=` on Turn A; KISS, YAGNI, and DRY win over a class tree or Protocols for one implementation; do not name new modules or mandate `ScopeLabel` / Pydantic, and verify those rules are present and no new file exists under `ai-specs/skills/` or `ai-specs/standards/shape.md`.
- [x] 2.3 Under `## Layer 2 — Twin` in `ai-specs/standards/testing.md`, add a short MiniMax-in-units heading that says units that need MiniMax take a fake client on `chat()` / `classify` / `complete` or call `classify` / `complete` directly, and that patching `app.openai` is not the design, and verify the existing pytest/Playwright pins and “no network” rule remain and `backend/tests/unit/test_chat_ingress.py` was not edited.

## 3. OpenSpec rules and constitution pointer

- [x] 3.1 Add an `openspec/config.yaml` design rule that a change that touches `backend/src` names `chat()` vs the I/O functions (`classify`, `complete`, …) and a tasks rule that a task that adds MiniMax I/O does not put that I/O in `chat()`, and verify `schema: spec-driven`, twin-native `context`, and `githubCopilot.cloudAgent: false` remain.
- [x] 3.2 Add one load sentence under `## Stack and testing` in `ai-specs/AGENTS.md` that before editing `backend/src` the agent reads `python.md` Layer 2 and `testing.md` Layer 2, and verify the constitution does not paste the function table or anti-patterns and root `AGENTS.md` is still only the thin pointer plus English.

## 4. Verify (no product rewrite)

- [x] 4.1 Run `git diff -- backend/src` and verify it is empty.
- [x] 4.2 Confirm `openspec/specs/prompt-firewall` and `openspec/specs/scope-classifier` were not edited, and verify no files exist under `openspec/changes/add-backend-shape-standards/specs/`.
- [x] 4.3 From `backend/`, run `.venv/bin/python -m pytest tests/unit` and verify the existing units still pass with no network.
- [x] 4.4 Run `openspec validate add-backend-shape-standards --type change` from Twin and verify it succeeds with `skip_specs: true`.
- [x] 4.5 Confirm no project skill, no `ai-specs/standards/shape.md`, and no always-apply `.cursor/rules/` that paste Layer 2 were added, and verify no `openspec archive` was run.
