## Why

The deny-list gate on the latest visitor message is an input guardrail. The live name `firewall` / `prompt-firewall` does not say that, and it reads like a network control. The implementation is already the right gate; only the name is wrong.

## What Changes

Rename the existing gate. **Do not change behavior.** Deny patterns, canned refusal, silent typed-email capture, skip Turn A / Turn B on match, and `chat()` order stay bit-identical. Visitor-facing strings stay bit-identical.

- Replace the product name `firewall` / `prompt-firewall` with `input-guardrail` in live product specs, `backend/src` identifiers, unit test names, and the Layer 2 sentence in `ai-specs/standards/python.md` that says “Firewall plus typed email stays canned.”
- Retire the live capability path `prompt-firewall`. Its four requirements move to `input-guardrail` with the same SHALL/MUST meaning; only the vocabulary changes (`firewall` → `input guardrail`).
- Update `scope-classifier` wording that names “the prompt firewall” so it points at the input guardrail. Classify, parse, fail-closed, and Turn B requirements do not change.

No **BREAKING** API or Gradio UX change.

**Non-goals**

- Changing deny-list patterns, canned refusal text, LEAD_ACK, or silent email-on-block.
- Adding moderation, PII blocking, or an output filter.
- New modules for a class tree, a `guardrails/` package, LiteLLM, timeouts, retries, caches, or conversation windowing.
- Editing archived OpenSpec changes.
- Archiving this change (archive only after a later explicit user request).

## Capabilities

### New Capabilities

- `input-guardrail`: Code-side deny-list on the latest visitor message so jailbreak, override, slash-command, prompt/memory dump, and debug-framing turns never reach MiniMax. Same four requirements as today’s `prompt-firewall`.

### Modified Capabilities

- `prompt-firewall`: Retired. Requirements move to `input-guardrail`. No visitor-facing behavior change.
- `scope-classifier`: Name-only. Requirements that say “prompt firewall” now say “input guardrail.” Turn A / fail-closed / Turn B stay as specified.

## Impact

- **Code:** `backend/src/firewall.py` and `matches_firewall` (and the `app.py` import / `chat()` call). Same regex, same boolean, new names. `chat()` still sequences capture → input guardrail → `classify` → `fail_closed_reply` / `complete`.
- **Tests:** `backend/tests/unit/test_firewall.py` and firewall cases in `test_chat_ingress.py`. Assertions stay; identifiers follow the rename. Units still must not hit the network.
- **Specs:** new live spec `openspec/specs/input-guardrail/`; `openspec/specs/prompt-firewall/` goes away after apply. `scope-classifier` cross-references update.
- **Agent OS:** one Layer 2 line in `ai-specs/standards/python.md` (typed email plus input guardrail stays canned).
- **Dependencies:** none.
- **Out of impact:** classifier prompt and parse, tools, visitor copy, live MiniMax E2E, archives, README pin lists.
