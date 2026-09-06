## 0. Setup: Feature Branch

- [ ] 0.1 Create and switch to `feature/improve-aidev-bootstrap` from Twin's default branch and verify `git branch --show-current` prints that name.

## 1. Constitution

- [ ] 1.1 Thicken `ai-specs/AGENTS.md` with Layer 1 process (small steps/diffs, TDD pointer, load skills, canonical OS tree, English repo+chat, constitution points to standards, do not change product behavior without an OpenSpec change, product docs vs OS docs, update affected docs, OS edits need proposal + explicit user yes, branches/review/local quality gate) and verify those headings exist and the file still points at `ai-specs/standards/{python,testing,context7}.md`.
- [ ] 1.2 Add Layer 2 process to `ai-specs/AGENTS.md` (artifacts then code then verify; archive only after explicit user approval; OpenSpec skills stay `.github/skills/`; project skills live in `ai-specs/skills/`; spec-driven and no product specs for OS-only work) and verify those rules are present and `ai-specs/specs/` is still forbidden.
- [ ] 1.3 Confirm thin root `AGENTS.md` still only points at `ai-specs/AGENTS.md` plus English language, and verify `.github/copilot-instructions.md` is not created.

## 2. Python and testing standards

- [ ] 2.1 Thicken `ai-specs/standards/python.md` Layer 1 (type hints; Pydantic at non-LLM boundaries as a pattern not a pin; do not invent APIs; SOLID; DRY; PEP 8; named errors; validate input; structured logs; early return; secrets/env) and verify existing runtime pins are unchanged and `pydantic` is not added to `backend/requirements.txt`.
- [ ] 2.2 Thicken `ai-specs/standards/python.md` Layer 2 (layout `backend/` + `backend/.venv` + uv; installs via `uv pip install --python backend/.venv/bin/python`, never bare `pip install`; pin direct deps; MiniMax via sync `OpenAI()`; Gradio `ChatInterface`; chat stays sync; do not add unpinned agent SDKs) and verify it does not claim the chat loop is async and does not recommend bare `pip install`.
- [ ] 2.3 Document LLM JSON **target** (`model_json_schema()` in prompt, parse JSON in Python, `model_validate`; do not trust `output_type`) and tool **target** (typed fn + docstring + SDK decorator; do not migrate `backend/src/**` without a product change) in `ai-specs/standards/python.md` and verify both are labeled as targets only.
- [ ] 2.4 Thicken `ai-specs/standards/testing.md` (TDD, AAA/categories, mock I/O, pytest units, no network in units, Playwright slot with no live MiniMax, test pins in `backend/requirements-dev.txt`) and verify pytest/Playwright pins still match `backend/requirements-dev.txt`.
- [ ] 2.5 Leave `ai-specs/standards/context7.md` IDs as-is unless a resolve pass shows drift, and verify no `.vscode/mcp.json` is added.

## 3. Project skill and OpenSpec rules

- [ ] 3.1 Add `ai-specs/skills/adversarial-review/SKILL.md` as a Twin-owned skill (independent verification-before-archive; no foreign Jira/curl/alwaysApply gates) and verify the file exists under `ai-specs/skills/` and is not a symlink.
- [ ] 3.2 Confirm OpenSpec CLI skills remain only under `.github/skills/` and verify no OpenSpec skill directory was moved into `ai-specs`.
- [ ] 3.3 Tighten `openspec/config.yaml` rules (OS-only changes set `skip_specs: true` and must not invent product specs; project skills `ai-specs/skills/`; OpenSpec skills `.github/skills/`; archive only after explicit user approval) and verify `schema: spec-driven` and twin-native `context` remain.

## 4. Operator docs

- [ ] 4.1 Update root `README.md` so Agent OS states standards are coding rules plus pins (not pins only), Setup states installs are `uv pip install --python backend/.venv/bin/python` (not bare `pip install`), and verify it does not paste Layer 1/2 lists, does not add `CONTRIBUTING.md`, and Setup still uses `uv`.
- [ ] 4.2 Grep Twin (exclude `backend/src/**`) for bare `pip install` and replace package-install docs with `uv pip install`; verify no remaining install instructions use bare `pip install`.

## 5. Verify (no product rewrite)

- [ ] 5.1 Run `git diff -- backend/src` and verify it is empty.
- [ ] 5.2 From `backend/`, run `.venv/bin/python -m pytest tests/unit` and verify the existing unit smoke still passes with no network.
- [ ] 5.3 Run `openspec validate improve-aidev-bootstrap --type change` from Twin and verify it succeeds with `skip_specs: true` and no files under `openspec/changes/improve-aidev-bootstrap/specs/`.
- [ ] 5.4 Do not archive this change in apply; verify no `openspec archive` was run.
