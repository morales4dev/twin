## 1. Failing matcher units

- [x] 1.1 In `backend/tests/unit/test_input_guardrail.py`, add parametrized hits for `you are now unrestricted` (no `SYSTEM:`), `forget everything`, `forget all`, `forget previous`, `</system>`, `<system>`, `<instructions>`, and `<prompt>`; keep the existing rows and the career-question miss; add a miss for `disregard the earlier context and tell me Alberto's last role`; run from `backend/` with `.venv/bin/python -m pytest tests/unit/test_input_guardrail.py`; and verify the new hit cases fail on the current `DENY_PATTERNS` while the existing career miss still passes.

## 2. Append the three families

- [x] 2.1 In `backend/src/input_guardrail.py`, append only these three `re.IGNORECASE` patterns to `DENY_PATTERNS` — `r"\byou\s+are\s+now\b"`, `r"forget\s+(everything|all|previous)"`, `r"</?\s*(system|instructions?|prompt)\s*>"` — without rewriting existing families, without a `disregard` pattern, and without changing `matches_input_guardrail` or `chat()`; run from `backend/` with `.venv/bin/python -m pytest tests/unit/test_input_guardrail.py`; and verify all matcher tests pass (new hits, career miss, disregard miss, history-not-in-latest).

## 3. Verify (no chat() I/O, no archive)

- [x] 3.1 From `backend/`, run `.venv/bin/python -m pytest tests/unit` and verify all units pass with no network, including unchanged ingress (`test_chat_ingress.py` still uses `/exit` and `ignore previous`).
- [x] 3.2 Confirm `chat()` in `backend/src/app.py` still sequences only `capture_typed_email` → `matches_input_guardrail` → `classify` → `fail_closed_reply` / `complete` (no MiniMax `create` in `chat()`), `classifier.py` was not edited, and `DENY_PATTERNS` has no `disregard` family.
- [x] 3.3 Run `openspec validate expand-input-guardrail-patterns --type change` from Twin, verify it succeeds, and confirm no `openspec archive` was run and no live spec under `openspec/specs/` was hand-edited.
