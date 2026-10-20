## Context

See [proposal.md](proposal.md) for why. Requirements live in the delta specs (`input-guardrail` ADDED, `prompt-firewall` REMOVED, `scope-classifier` name-only).

Today the gate is already the right Python deny-list: `backend/src/firewall.py` `matches_firewall(message) -> bool` over `DENY_PATTERNS`. `chat()` in `backend/src/app.py` sequences `capture_typed_email` → `matches_firewall` → `classify` → `fail_closed_reply` / `complete`. Units lock that order in `backend/tests/unit/test_firewall.py` and the firewall cases in `test_chat_ingress.py`. Layer 2 in `ai-specs/standards/python.md` still says “Firewall plus typed email stays canned.”

Constraints: Python 3.12.12, existing `backend/.venv` + `backend/requirements.txt` (no new pin), units under `backend/tests/unit/` with no network. Archive is not part of apply.

## Goals / Non-Goals

**Goals:**

- Rename the gate identifiers so code, tests, and the Layer 2 sentence match the product name `input-guardrail`.
- Keep `chat()` as sequencer only. Do not move MiniMax I/O into `chat()`. `classify`, `complete`, `fail_closed_reply`, and `capture_typed_email` stay as they are.

**Non-Goals:**

- Design-level restatement of proposal scope. Also: no `guardrails/` package, no exception type, no compatibility alias for `matches_firewall`, no live-spec rewrite during apply, no archive.

## Decisions

### 1. Same module shape, new names only

`git mv` the existing module and rename the boolean. Keep one function, one file, the same regex list.

| Current | After |
| --- | --- |
| `backend/src/firewall.py` | `backend/src/input_guardrail.py` |
| `matches_firewall(message: str) -> bool` | `matches_input_guardrail(message: str) -> bool` |
| `DENY_PATTERNS` | unchanged (not a firewall name) |

`chat()` stays: `capture_typed_email` → `matches_input_guardrail` → `classify` → `fail_closed_reply` or `complete`. Import in `app.py` follows the new module. Type hint on the renamed public function stays `str -> bool`.

A `guardrails/` package, an exception type, or extra layers (moderation, PII, output filter) would change call shape. Keep one boolean function and the same `DENY_PATTERNS`.

Alternative: `matches_guardrail` — rejected; the capability path is `input-guardrail`, and “guardrail” alone is ambiguous once an output filter exists later.
Alternative: keep `matches_firewall` as a re-export — rejected (YAGNI; this is not a published library API).
Alternative: a `guardrails/` package — rejected (proposal lock; one implementation, no class tree).

### 2. Tests keep assertions; identifiers follow the rename

| Current | After |
| --- | --- |
| `backend/tests/unit/test_firewall.py` | `backend/tests/unit/test_input_guardrail.py` |
| `test_firewall_*` | `test_input_guardrail_*` |
| Ingress `test_firewall_match_*` / `test_firewall_typed_email_*` | `test_input_guardrail_match_*` / `test_input_guardrail_typed_email_*` |

Parametrized deny-family strings, career miss, history-not-in-latest, canned refusal, silent typed-email record, and `create.assert_not_called()` stay bit-identical. Units still must not hit the network. TDD: point tests at the new names first (they fail), then rename the module and function.

Alternative: leave test names as `test_firewall_*` after the import change — rejected; the live name would still be wrong in the test suite.

### 3. One Layer 2 sentence; live specs wait for archive

Change only this line in `ai-specs/standards/python.md`:

- From: `Firewall plus typed email stays canned.`
- To: `Input guardrail plus typed email stays canned.`

Do not thicken constitution, testing.md, or skills. Do not edit archives, sibling change proposals, `docs/backlog-draft.md`, or README pin lists.

The proposal’s “live spec path goes away after apply” is timing, not apply work. Constitution: archive only after a later explicit user request; do not archive in apply. Apply implements code, tests, and the Layer 2 sentence. Deltas already sit under this change. `openspec/specs/input-guardrail/` appears and `openspec/specs/prompt-firewall/` goes away when this change is archived, not during apply. Do not hand-edit live specs in apply.

`scope-classifier` scenario titles are renamed in the live spec during planning (`Input guardrail already blocked` / `Input guardrail did not match`) so the `MODIFIED` delta can use the same headings. OpenSpec `MODIFIED` will not drop a scenario the live spec still names. Live WHEN/THEN for those two scenarios still say “prompt firewall” until archive. No apply task.

### 4. Apply order and quality gate

Work on the current feature branch. No new pin. No CI. Verify with existing `backend/.venv`: from `backend/`, `.venv/bin/python -m pytest tests/unit`, and `openspec validate rename-firewall-to-input-guardrail --type change`.

**Apply order:**

1. Point `test_input_guardrail.py` (renamed from `test_firewall.py`) and ingress firewall cases at `matches_input_guardrail`; tests fail on the missing name.
2. `git mv` `firewall.py` → `input_guardrail.py`, rename the function, update the `app.py` import and `chat()` call.
3. Update the Layer 2 sentence in `python.md`.
4. Verify units (no network) and `openspec validate`; no archive.

## Risks / Trade-offs

- [Rename of `chat()` import breaks ingress while assertions stay] → Mitigation: keep the same reply/record/`create` assertions; run the full unit folder after `app.py` is updated.
- [A `guardrails/` package or exception type changes behavior] → Mitigation: one boolean function; same `DENY_PATTERNS`; no moderation/PII/output filter.
- [Compatibility alias leaves the old name live] → Mitigation: no `matches_firewall` re-export; grep `backend/src` and `backend/tests` for `firewall` after the rename.
- [Hand-editing live specs during apply drifts from archive] → Mitigation: apply touches code, tests, and the one Layer 2 line only; spec tree updates at archive.
- [Renaming `MODIFIED` scenario titles without updating the live spec fails validate] → Mitigation: live `scope-classifier` headings already match the delta; apply does not touch live specs.

## Migration Plan

- Feature branch; no API versioning (same Gradio `ChatInterface`).
- Deploy is process restart of the Gradio app after the rename lands.
- Rollback: revert the rename commit. `matches_firewall` is not kept as an alias, so rollback is git, not a dual-name period.
- No data migration. No runtime dependency change.

## Open Questions

None. Identifier names, apply vs archive, and the `scope-classifier` scenario titles are decided above.
