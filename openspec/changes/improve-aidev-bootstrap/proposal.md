## Why

The archived `add-aidev-bootstrap` change gave Twin a thin Agent OS: pins, paths, Context7 IDs, and a constitution that points at empty-ish standards. Agents still invent APIs, skip TDD, mix product work with OS edits, and treat week-1 tool JSON as the long-term protocol. This change thickens the constitution and standards from the locked Layer 1 (generic small Python) and Layer 2 (Twin / OpenSpec / LLM protocol) lists so later product work has a real coding OS.

## What Changes

This change is Agent OS documentation and project-skill placement. It does **not** change visitor-facing twin behavior. Specs are skipped (`skip_specs: true`).

- Thicken `ai-specs/AGENTS.md` as the constitution: small steps, TDD, load skills, canonical OS tree, English for repo and chat, pointer to standards, product vs OS docs, do not change product behavior without an OpenSpec change, OS edits need a proposal plus explicit user yes, artifacts-then-code-then-verify, archive only after explicit user approval.
- Thicken `ai-specs/standards/python.md` with Layer 1 software rules (type hints, Pydantic at non-LLM boundaries, do not invent APIs, SOLID, DRY, PEP 8, named errors, validate input, structured logs, early return, secrets/env) plus Layer 2 Twin stack (layout/venv/uv, `uv pip install` not bare `pip install`, pin direct deps, MiniMax via sync `OpenAI()`, Gradio `ChatInterface`, chat stays sync, do not add unpinned agent SDKs).
- Thicken `ai-specs/standards/testing.md` with Layer 1 test rules (TDD, AAA/categories, mock I/O) plus Layer 2 Twin test layout (pytest units, no network in units, Playwright slot with no live MiniMax, test pins in `backend/requirements-dev.txt`).
- Keep `ai-specs/standards/context7.md` as the Context7 ID policy (resolve IDs, pass pins, no `.vscode/mcp.json`).
- Document Layer 2 LLM protocol **targets** in standards, not as app rewrites: structured output is `model_json_schema()` in the prompt, parse JSON in Python, `model_validate`; tools are typed functions plus docstring plus SDK decorator. Do not migrate `backend/src/**` without a separate product change.
- Add project skill `adversarial-review` under `ai-specs/skills/`. Keep OpenSpec CLI skills under `.github/skills/`; do not move them.
- Keep schema `spec-driven`. Do not invent product specs for this OS-only change. Tighten `openspec/config.yaml` rules so later OS work stays twin-native and skip-specs when there is no product behavior change.
- Update operator docs that this change makes stale (constitution pointers, README Agent OS section if it still describes pins-only standards). README Setup stays the how-to-start page: `uv pip install --python backend/.venv/bin/python`; do not add `CONTRIBUTING.md`. Do not rewrite product docs for visitor chat.

**Non-goals**

- Product capability specs under `openspec/specs/` (none exist; none will be invented).
- Visitor-facing Gradio chat, `backend/src/**` migration.
- Prompt firewall / classifier (`add-prompt-firewall-and-classifier` stays a separate change).
- Async rewrite of `chat`.
- Implementing schema-in-prompt JSON parse or tool-decorator in application code (document as targets only).
- Moving OpenSpec CLI skills from `.github/skills/` into `ai-specs`.
- `.vscode/mcp.json`, hosted MCP URL pin, CI, live MiniMax E2E.
- Changing runtime or test pins already recorded in `backend/requirements.txt` and `backend/requirements-dev.txt`.
- Archiving this change (archive only after a later explicit user request).

No **BREAKING** API or Gradio UX change.

## Capabilities

### New Capabilities

- None. This change does not introduce product behavior. `skip_specs: true` is set on the change.

### Modified Capabilities

- None. `openspec/specs/` has no existing capabilities, and none should be invented for validation.

## Impact

- **Agent OS:** `ai-specs/AGENTS.md`, `ai-specs/standards/python.md`, `ai-specs/standards/testing.md`, `ai-specs/standards/context7.md` (keep policy; no ID churn expected), new `ai-specs/skills/adversarial-review/`.
- **OpenSpec:** change metadata `skip_specs: true`; tighten `openspec/config.yaml` rules. Skills for OpenSpec CLI stay under `.github/skills/`.
- **App code:** no required change to `backend/src/**`.
- **Dependencies:** no pin changes.
- **Docs:** constitution/standards, README Agent OS (coding rules plus pins), README Setup (`uv pip install`, no `CONTRIBUTING.md`).
- **Out of impact:** visitor chat, firewall change, live MiniMax E2E, Copilot cloud agent, MCP config.
