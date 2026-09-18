## Context

See [proposal.md](proposal.md) for why. Layer 2 today is pins and layout: `python.md` names `backend/src/`, `backend/.venv`, uv, sync Gradio `ChatInterface`, and sync MiniMax via `OpenAI()`; `testing.md` names pytest units, no network, and a Playwright slot. Neither file names module shape. Observed `chat()` in `backend/src/app.py` still sequences email extract-plus-record, firewall, Turn A I/O, parse, lead-ack vs canned (three copies), then Turn B and the tool loop. Units invert a module-global `openai` with `@patch("app.openai.chat.completions.create")`. `capture_typed_email` already exists and is unused by `chat()`. Specs are skipped (`skip_specs: true`). This design is Agent OS only; do not edit `backend/src/**`. Aligning the app is a separate change (`refactor-thin-chat-orchestrator`).

## Goals / Non-Goals

**Goals:**

- Make thin-`chat()` the operational default apply reads from Layer 2, without a new skill invoke.
- Point the constitution at that Layer 2 read before `backend/src` edits; keep the pointer one sentence.
- Add OpenSpec design and task rules that catch MiniMax I/O landing in `chat()`.

**Non-Goals:**

- Design-level restatement of proposal scope. Also: no product specs, no `backend/src/**` edits, no test rewrites, no new skill, no README dump, no archive in this change.

## Decisions

1. **Thicken existing Layer 2 files; do not add a skill or a fourth standard.**
   Shape rules live in `ai-specs/standards/python.md` and `ai-specs/standards/testing.md` so apply already loads them with the stack. Do not add `ai-specs/skills/` for this. Do not add `ai-specs/standards/shape.md` or always-apply `.cursor/rules/` that paste the bullets.
   Alternative: a project skill agents must invoke — rejected (proposal: first apply must see the default without an extra invoke).
   Alternative: always-apply Cursor rules that paste Layer 2 — rejected (second source of truth; constitution already forbids dumping standards).

2. **Add a Layer 2 subsection, not a Layer 3 and not a coding-target block.**
   Keep `## Layer 2 — Twin stack` (python) and `## Layer 2 — Twin` (testing). Add a short heading under each (module shape / MiniMax in units) so pins stay findable. Do not put shape under `## LLM protocol (targets only)`: that section is “do not implement in an OS-only change.” Shape is the default for the next change that *does* edit `backend/src`.
   Alternative: fold shape into the existing pin bullets — rejected (Layer 2 would stay “pins and layout” and the new default would hide).
   Alternative: mark shape as target-only like JSON/`output_type` — rejected (that is what produced a fat first `chat()`).

3. **`python.md` names functions and anti-patterns, not a file tree.**
   Operational default, in this vocabulary:

   | Name | Role |
   | --- | --- |
   | `chat()` | Gradio `(message, history) -> str`. Sequences only. |
   | `classify(message, client)` | Turn A I/O. Omits `tools`. Returns a result (`allowed_for_turn_b` plus reason: `in_scope` / `out_of_scope` / `unparseable` / `error`). No visitor strings. |
   | `complete(message, history, client)` | Turn B and the tool loop. |
   | `fail_closed_reply(email)` | Lead-ack vs canned. Used only after Turn A. Firewall plus typed email stays canned. |

   Also encode: inject the MiniMax client into `chat()` as an optional kwarg (Gradio still calls two arguments); no shared MiniMax helper that could put `tools=` on Turn A; KISS, YAGNI, and DRY win over a class tree or Protocols for one implementation. Do not name new modules or mandate `ScopeLabel` / Pydantic in this OS change — those are apply choices for a later product or refactor change.
   Alternative: prescribe `classifier.py` / `app.py` splits here — rejected (this change must not design the refactor; `refactor-thin-chat-orchestrator` owns file placement).
   Alternative: one `call_minimax(...)` helper — rejected (`tools=` leakage onto Turn A).

4. **`testing.md` Layer 2: fake client or direct I/O functions; patching `app.openai` is not the design.**
   Units that need MiniMax take a fake client on `chat()` / `classify` / `complete`, or call `classify` / `complete` directly. Keep “no network” and the existing pytest/Playwright pins. Do not rewrite `backend/tests/unit/test_chat_ingress.py` in this change; those patches stay until the refactor lands.
   Alternative: require ingress tests to stop patching in this OS change — rejected (would edit tests without the injection seam).

5. **Constitution gets one load sentence, not the bullets.**
   Under `## Stack and testing` in `ai-specs/AGENTS.md`, add that before editing `backend/src` the agent reads `python.md` Layer 2 and `testing.md` Layer 2. Do not paste the table or anti-patterns into the constitution. Leave root `AGENTS.md` thin.
   Alternative: paste the shape rules into the constitution — rejected (silently thickens process; standards are the home).

6. **`openspec/config.yaml` rules, not a new schema.**
   Keep `schema: spec-driven`, twin-native `context`, and `githubCopilot.cloudAgent: false`. Add a **design** rule: a change that touches `backend/src` names `chat()` vs the I/O functions (`classify`, `complete`, …). Add a **tasks** rule: a task that adds MiniMax I/O does not put that I/O in `chat()`. Do not invent product specs or a `cursor:` key.
   Alternative: only thicken standards and skip config — rejected (propose/apply would not be reminded at artifact time).

7. **Current `backend/src` mismatch is expected and out of this apply.**
   After this change, Layer 2 describes a shape the app does not yet have. That is allowed. Do not “fix” `app.py` here. The sibling change `refactor-thin-chat-orchestrator` should challenge its own design against these live Layer 2 rules after this apply, not restated in that proposal.
   Alternative: apply shape to `app.py` in the same change — rejected (constitution: do not mix Agent OS edits with product behavior).

8. **Quality gate without CI.**
   Feature branch `feature/add-backend-shape-standards`. Verify with existing `backend` pytest units (no network) and `openspec validate add-backend-shape-standards --type change`. Confirm `git diff -- backend/src` is empty and no files exist under this change’s `specs/`. Do not add GitHub Actions.

**Apply order:**

1. Feature branch `feature/add-backend-shape-standards` from Twin's default branch (docs-only; isolate from `refactor-thin-chat-orchestrator` apply).
2. Thicken `ai-specs/standards/python.md` Layer 2 with the module-shape subsection (functions + anti-patterns from decision 3).
3. Thicken `ai-specs/standards/testing.md` Layer 2 with the fake-client / direct-I/O rule (decision 4).
4. Add the design and task rules to `openspec/config.yaml` (decision 6).
5. Add the one load sentence under `ai-specs/AGENTS.md` Stack and testing (decision 5). Leave root `AGENTS.md` thin.
6. Verify: empty `git diff -- backend/src`; no change-local specs; product specs untouched; pytest units; `openspec validate add-backend-shape-standards --type change`; no archive.

## Risks / Trade-offs

- [Agents treat new Layer 2 as an order to refactor `chat()` in this change] → Mitigation: proposal, this design, and tasks say OS-only; apply verification is empty `git diff -- backend/src`.
- [Standards describe a shape the app lacks → agents “fix” `app.py` on the next unrelated edit] → Mitigation: constitution still forbids `backend/src` edits without a product/refactor change; the sibling change is the named align pass.
- [Layer 2 becomes a second constitution] → Mitigation: short subsection + table of four names; no class tree; no file-tree mandate.
- [A later apply dumps I/O into `chat()` because config rules stayed pin-only] → Mitigation: design rule names `chat()` vs I/O functions; task rule forbids MiniMax I/O in `chat()`.
- [Agents add a `Chat` / `Classifier` class tree to “do SOLID”] → Mitigation: Layer 2 says KISS, YAGNI, and DRY win over a class tree or Protocols for one implementation.
- [Existing ingress patches are read as the blessed test design] → Mitigation: `testing.md` says patching `app.openai` is not the design; this change does not rewrite those tests.

## Migration Plan

No production deploy. Apply is git-only Agent OS files. Rollback: revert the change commit(s). Do not uninstall venv packages (pins unchanged). Do not archive until a later explicit user request.
