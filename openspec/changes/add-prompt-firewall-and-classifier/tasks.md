## 1. Shared refusal constant

- [x] 1.1 Extract the existing Hard Rejection sentence from `TWIN_SYSTEM_PROMPT` into a shared Python constant used by firewall, fail-closed routing, and tests; verify the constant string is exactly `As the digital twin of Alberto Morales, I am only authorized to discuss his professional background, experience, and the specific personal interests listed on his profile.` and that `TWIN_SYSTEM_PROMPT` still contains that same sentence (`rg` / unit import).

## 2. Prompt firewall

- [x] 2.1 Add failing unit tests for case-insensitive deny-list families (override, forged system, slash commands, show prompt/memory, debug framing) plus a career-question miss; verify they fail before production match code exists (`backend/.venv/bin/python -m pytest tests/unit/test_firewall.py` from `backend/`).
- [x] 2.2 Implement firewall matching on the raw latest user string only (module-level pattern list, substring/simple regex, no Jose corpus, no history input); verify the tests from 2.1 pass and a career question does not match.

## 3. Typed email capture

- [x] 3.1 Add failing unit tests for conservative email extract (typed address present; absent; not inferred from a different string) with `record_user_details` mocked; verify they fail before extract code exists (`backend/.venv/bin/python -m pytest tests/unit/test_email_capture.py` from `backend/`).
- [x] 3.2 Implement extract of the first typed email (`@` + dotted domain) from the latest user string only and call `record_user_details` from Python when present; verify the tests from 3.1 pass and no email is recorded when none is typed.

## 4. Turn A parse (plain Python)

- [x] 4.1 Add failing unit tests for label parse: `IN_SCOPE`, `OUT_OF_SCOPE`, mixed-turn fixture expected `OUT_OF_SCOPE`, empty/essay/other token unparseable; verify they fail before parse code exists (`backend/.venv/bin/python -m pytest tests/unit/test_scope_label.py` from `backend/`).
- [x] 4.2 Implement strip / first non-empty line / uppercase exact-token parse with no Pydantic and no JSON schema; verify the tests from 4.1 pass.

## 5. Classifier prompt builder

- [x] 5.1 Add a Turn A system prompt (label-only binary, mixed → `OUT_OF_SCOPE`, ignore override text inside delimiters, optional skill-trap/meta few-shots mapping to `OUT_OF_SCOPE`) and a helper that wraps the current user string in `<user_message>` delimiters; verify a unit test that the built messages contain only that delimited user string (no Gradio history, no `TWIN_SYSTEM_PROMPT`, no CV).

## 6. Chat ingress orchestration

- [x] 6.1 Add failing `chat()` unit tests with `openai.chat.completions.create` and `record_user_details` mocked: firewall match → zero MiniMax calls + canned refusal; firewall match + typed email → record that email and still zero MiniMax calls; parsed `IN_SCOPE` → two calls, second with `tools`; parsed `OUT_OF_SCOPE` / unparseable / Turn A exception → one call without `tools` + canned refusal, no Turn B; verify they fail before `chat()` is rewired (`backend/.venv/bin/python -m pytest tests/unit/test_chat_ingress.py` from `backend/`).
- [x] 6.2 Rewire `chat()` to capture typed email → firewall → Turn A (same `MODEL_NAME`, no `tools`) → parse/fail-closed → existing Turn B loop (`system + history + user` + `tools` + tool while-loop) or canned refusal; verify the tests from 6.1 pass and Turn A request kwargs omit `tools`.

## 7. Quality gate

- [x] 7.1 Run unit tests from `backend/` with the project venv and no network (`backend/.venv/bin/python -m pytest tests/unit`); verify they pass.
- [x] 7.2 Run `openspec validate add-prompt-firewall-and-classifier --type change --strict` and verify it succeeds.
- [x] 7.3 Confirm `backend/requirements.txt` has no new pins (no Pydantic) via `rg` / diff against the previous pins.

## 8. Strip classifier think blocks before label parse

- [x] 8.1 Add failing unit tests in `backend/tests/unit/test_scope_label.py`: `<think>` then `IN_SCOPE` parses `IN_SCOPE`; `<think>` then `OUT_OF_SCOPE` parses `OUT_OF_SCOPE`; a label that appears only inside `<think>` is unparseable. Verify they fail on the current first-line parser (`backend/.venv/bin/python -m pytest tests/unit/test_scope_label.py` from `backend/`).
- [x] 8.2 Update label parse to discard `<think>…</think>` blocks (case-insensitive, including newlines) and then apply the existing first-non-empty-line exact-token parse; do not harvest a label from inside the think block. Verify the tests from 8.1 and 4.1 pass.
- [x] 8.3 Re-run unit tests from `backend/` with no network (`backend/.venv/bin/python -m pytest tests/unit`) and `openspec validate add-prompt-firewall-and-classifier --type change --strict`; verify both succeed.

## 9. LEAD_ACK when Turn B does not run and this turn had a typed email

- [x] 9.1 Add a Python LEAD_ACK constant that interpolates the extracted address; add a unit that the rendered string contains that address and is not the canned refusal.
- [x] 9.2 Extend `chat()` units (`backend/tests/unit/test_chat_ingress.py`, MiniMax and `record_user_details` mocked): `OUT_OF_SCOPE` + typed email → record + LEAD_ACK + one classifier call, no Turn B; unparseable / Turn A exception + typed email → same visitor reply and no Turn B; firewall + typed email still canned refusal + record + zero MiniMax + no LEAD_ACK; `OUT_OF_SCOPE` without email still canned. Verify they fail before routing changes.
- [x] 9.3 Wire `chat()` so when Turn B does not run and this turn had a typed email, return LEAD_ACK (firewall path unchanged: silent capture + canned). Verify the tests from 9.1–9.2 pass.
- [x] 9.4 Re-run unit tests from `backend/` with no network (`backend/.venv/bin/python -m pytest tests/unit`) and `openspec validate add-prompt-firewall-and-classifier --type change --strict`; verify both succeed.
