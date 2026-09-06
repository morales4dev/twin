## Context

See [proposal.md](proposal.md) for why. Twin already has the v1 Agent OS from archived `add-aidev-bootstrap`: thin `ai-specs/AGENTS.md`, pin-and-path standards (`python.md`, `testing.md`, `context7.md`), `backend/.venv` + pinned `requirements*.txt`, pytest unit smoke, Playwright e2e slot. Product code lives under `backend/src/**` (sync Gradio `ChatInterface`, MiniMax via sync `OpenAI()`, week-1 tool JSON, and the rest of that tree). `openspec/specs/` has no product capabilities. Specs are skipped (`skip_specs: true`). This design is document layout and skill placement; do not edit `backend/src/**`.

## Goals / Non-Goals

**Goals:**

- One constitution plus three existing standard files that encode the locked Layer 1 (generic small Python) and Layer 2 (Twin / OpenSpec / LLM protocol) titles, without adding new standard filenames unless a title cannot fit.
- Project skill `adversarial-review` under `ai-specs/skills/`; OpenSpec CLI skills remain under `.github/skills/`.
- LLM JSON parse and tool-decorator written as **targets**, not as `backend/src` rewrites.
- Tighten `openspec/config.yaml` rules so later OS-only work keeps `skip_specs` and does not invent product specs.

**Non-Goals:**

- Design-level restatement of proposal scope. Also: no product specs, no `backend/src/**` edits, no pydantic or agent-SDK pin, no CI, no archive in this change.

## Decisions

1. **Keep the v1 file set; thicken in place.**
   Constitution stays `ai-specs/AGENTS.md` with a thin root pointer. Standards stay `ai-specs/standards/{python,testing,context7}.md`. Do not add `ai-specs/specs/`. Do not split Layer 1 vs Layer 2 into separate files (agents would miss one). Inside each file, use short headings so Layer 1 rules are reusable and Layer 2 is Twin-specific.
   Alternative: one mega `AGENTS.md` — rejected (OpenSpec `context` already points at the three standard files).

2. **Where each locked title lives.**

   | File | Owns |
   | --- | --- |
   | `ai-specs/AGENTS.md` | Small steps/diffs; TDD pointer; load skills; canonical OS tree (`ai-specs/` vs `openspec/specs/` vs `.github/skills/`); English repo+chat; constitution points to standards; do not change product behavior without an OpenSpec change; product docs vs OS docs; update affected docs; OS edits need proposal + explicit user yes; artifacts then code then verify; archive only after explicit user approval; branches/review/local quality gate (pytest + `openspec validate`, no new CI). |
   | `ai-specs/standards/python.md` | Existing pins/layout **plus** type hints; Pydantic at **non-LLM** Python boundaries (pattern, not a new pin); do not invent APIs; SOLID; DRY; PEP 8; named errors; validate input; structured logs; early return; secrets/env; Layer 2: `backend/` + `backend/.venv` + uv; installs via `uv pip install --python backend/.venv/bin/python` (never bare `pip install`); pin direct deps; MiniMax via **sync** `OpenAI()`; Gradio `ChatInterface`; chat stays sync; do not add unpinned agent SDKs; LLM JSON **target** (`model_json_schema()` in prompt, parse JSON in Python, `model_validate`); tool **target** (typed fn + docstring + SDK decorator); do not migrate `backend/src/**` without a product change. |
   | `ai-specs/standards/testing.md` | Existing layout/pins **plus** TDD; AAA/categories; mock I/O; no network in units; Playwright slot, no live MiniMax. |
   | `ai-specs/standards/context7.md` | Unchanged policy and resolved IDs unless a resolve pass at apply shows drift. |

   Alternative: new `llm.md` / `process.md` — rejected (proposal said thicken existing files).

3. **Pydantic is a coding rule, not a dependency change.**
   Layer 1 requires Pydantic for new non-LLM structured boundaries (env-ish config objects, parsed tool results after JSON, future non-LLM APIs). Do **not** add `pydantic` to `backend/requirements.txt` in this change. If a later product change needs a first-party import, that change pins it. Do not tell agents that constrained decoding / `output_type` is trusted.
   Alternative: pin pydantic now — rejected (no app code uses it yet; proposal forbids pin churn).

4. **LLM structured output and tools are standards targets.**
   Document the desired protocol next to the stack facts. Current week-1 tool JSON and `chat.completions.create(..., tools=tools)` stay until a **product** change migrates them. Apply of this change must leave `git diff -- backend/src` empty.
   Alternative: migrate tools in this change — rejected (visitor-facing / product behavior).

5. **Project skills vs OpenSpec CLI skills.**
   Add `ai-specs/skills/adversarial-review/SKILL.md` as a Twin-owned file. Keep the verification-window, independent-reviewer intent. Do not include foreign product examples, mandatory curl/E2E gates, or always-apply rules from another project. Do **not** symlink outside this repo (Twin must be self-contained). Do **not** move `.github/skills/` OpenSpec CLI skills.
   Alternative: symlink to a skill outside this repo — rejected (clone would break; other-project rules would leak).

6. **`openspec/config.yaml`: tighten rules, do not invent specs.**
   Keep `schema: spec-driven` and existing twin-native `context`. Add rules that (a) OS-only changes set `skip_specs: true` and must not invent product specs, (b) project skills live under `ai-specs/skills/`, OpenSpec skills stay `.github/skills/`, (c) archive only after explicit user approval. Do not add mandatory curl/E2E task templates Twin does not have.
   Alternative: import another project's `openspec/config.yaml` — rejected (wrong stack, invents product-test gates Twin does not have).

7. **README / operator docs.**
   Root README already points at `ai-specs/` vs `openspec/specs/`. Apply adds one sentence that standards are coding rules plus pins, not pins only, and that package installs use `uv pip install --python backend/.venv/bin/python` (not bare `pip install`). Do not paste Layer 1/2 lists into README. Do not add `CONTRIBUTING.md`.

8. **Installs are `uv pip install`, not `pip install`.**
   Encode the rule in `ai-specs/standards/python.md` (Layer 2). README Setup already uses `uv venv` / `uv pip install`; keep that as how-to-start. At apply, grep Twin docs/OS for bare `pip install` and fix those files. Do not edit `backend/src/**`.
   Alternative: extra how-to-contribute file — rejected (README is enough).

9. **Quality gate without CI.**
   Layer 1 “branches/review/quality gate” means: work on a feature branch; verify with existing `backend` pytest (units, no network) and `openspec validate improve-aidev-bootstrap --type change`; do not add GitHub Actions in this change.

**Apply order:**

1. Feature branch `feature/improve-aidev-bootstrap` from the Twin default branch (docs-only; still isolate from other work).
2. Thicken `ai-specs/AGENTS.md`, then `python.md`, then `testing.md`; leave `context7.md` unless IDs drifted.
3. Create Twin-owned `ai-specs/skills/adversarial-review/SKILL.md` (verification before archive; no foreign product gates).
4. Tighten `openspec/config.yaml` rules (OS-only `skip_specs`; project skills `ai-specs/skills/`; OpenSpec skills `.github/skills/`; archive only after explicit user approval).
5. README: coding-rules-plus-pins one-liner and `uv pip install` (not bare `pip install`); no `CONTRIBUTING.md`.
6. Grep Twin docs/OS for bare `pip install` and replace with `uv pip install` where it means installing packages.
7. Verify: `git diff -- backend/src` empty; pytest units still pass; `openspec validate improve-aidev-bootstrap --type change`; `adversarial-review` exists under `ai-specs/skills/` and OpenSpec skills remain under `.github/skills/`.

## Risks / Trade-offs

- [Agents treat LLM JSON / decorator targets as an order to rewrite `backend/src/**`] → Mitigation: constitution + python.md say “target only; no migrate without a product change”; apply verification is empty `git diff -- backend/src`.
- [Pydantic documented but not pinned → agents run unpinned installs] → Mitigation: python.md says do not add the pin in this OS change; first product use pins it; installs go through `uv pip install --python backend/.venv/bin/python`.
- [adversarial-review text pulls in foreign curl/Jira/alwaysApply] → Mitigation: Twin-owned skill only; no symlink; drop other-project gates.
- [Thick constitution ignored because Copilot only loads root `AGENTS.md`] → Mitigation: keep the thin root pointer; do not duplicate the constitution.
- [Layer 1 vs Layer 2 mixed in one file → agents apply Gradio rules to generic Python] → Mitigation: explicit Layer 1 / Layer 2 headings.
- [Other-project OpenSpec mandatory steps leak into Twin apply] → Mitigation: Twin `openspec/config.yaml` and this design forbid curl/E2E gates Twin does not have; Twin tasks stay small + verification.

## Migration Plan

No production deploy. Apply is git-only documentation and a Twin-owned `adversarial-review` skill. Rollback: revert the change commit(s). Do not uninstall venv packages (pins unchanged). Do not archive until a later explicit user request.
