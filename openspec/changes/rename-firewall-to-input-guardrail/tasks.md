## 1. Failing deny-list units

- [x] 1.1 Rename `backend/tests/unit/test_firewall.py` to `test_input_guardrail.py`, import `matches_input_guardrail` from `input_guardrail`, rename `test_firewall_*` to `test_input_guardrail_*` (same parametrized strings, career miss, and history-not-in-latest assertions), run from `backend/` with `.venv/bin/python -m pytest tests/unit/test_input_guardrail.py`, and verify the tests fail because `input_guardrail` / `matches_input_guardrail` is missing.

## 2. Rename the gate and keep chat() a sequencer

- [x] 2.1 `git mv` `backend/src/firewall.py` to `backend/src/input_guardrail.py`, rename `matches_firewall` to `matches_input_guardrail` (keep `DENY_PATTERNS` and the regex list bit-identical; no `guardrails/` package, no exception, no `matches_firewall` alias), and verify `tests/unit/test_input_guardrail.py` passes.
- [x] 2.2 Update `backend/src/app.py` so `chat()` imports and calls `matches_input_guardrail` and still sequences only `capture_typed_email` → input guardrail → `classify` → `fail_closed_reply` / `complete` (no MiniMax `create` in `chat()`), and verify `rg -n "matches_firewall|from firewall" backend/src` prints nothing.
- [x] 2.3 Rename the three ingress cases in `backend/tests/unit/test_chat_ingress.py` from `test_firewall_*` to `test_input_guardrail_*` (same canned / silent-email / `create.assert_not_called()` assertions), run from `backend/` with `.venv/bin/python -m pytest tests/unit/test_chat_ingress.py`, and verify those tests pass with no network.

## 3. Layer 2 sentence

- [x] 3.1 In `ai-specs/standards/python.md` Layer 2, change “Firewall plus typed email stays canned.” to “Input guardrail plus typed email stays canned.” and verify that is the only edit in that file and that `ai-specs/AGENTS.md`, `ai-specs/standards/testing.md`, and `ai-specs/skills/` were not edited.

## 4. Verify (no live-spec rewrite, no archive)

- [x] 4.1 From `backend/`, run `.venv/bin/python -m pytest tests/unit` and verify all units pass with no network.
- [x] 4.2 Grep `backend/src` and `backend/tests` for `firewall` / `matches_firewall` and verify no live identifier remains (no `firewall.py`, no `test_firewall.py`, no `matches_firewall` re-export).
- [x] 4.3 Confirm `openspec/specs/prompt-firewall` and `openspec/specs/scope-classifier` were not hand-edited (live spec tree updates at archive), run `openspec validate rename-firewall-to-input-guardrail --type change` from Twin, and verify it succeeds.
- [x] 4.4 Confirm no `guardrails/` package, no new pin, no visitor-string change, and no `openspec archive` was run.
