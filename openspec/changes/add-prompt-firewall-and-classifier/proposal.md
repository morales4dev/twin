## Why

Today every Gradio turn in `backend/src/app.py` is sent straight to MiniMax with tools. Scope and jailbreak rules live only in `TWIN_SYSTEM_PROMPT`, so the model can still teach CV technologies, follow `/exit` or `/resume`, dump memory, or talk about itself. Red-team evidence in `docs/01_jose_evaluation.md` shows those failures. We need a Python gate plus a cheap binary classifier so out-of-scope turns never generate a career answer.

## What Changes

Each Gradio turn runs a Python pipeline. Classify and answer are never the same MiniMax completion.

1. **Typed email (Python).** If the latest user string contains a typed email, record it in Python even if the rest of the turn is later blocked or out of scope. The model must not invent an email.
2. **Prompt firewall (Python).** Scan the raw latest user string **before** any MiniMax call. Deny-list strings are **not** copied from the Jose battery; they follow the generic patterns in backlog item 6 (override, fake system, slash commands, show prompt/memory, debug framing). A match returns the existing canned twin refusal and **skips Turn A and Turn B** (no classifier, no career completion).
3. **Turn A classifier** (same MiniMax model, only if the firewall did not match). A **stateless** call: no memory. It receives only the **current** user string as delimited **data**, not as instructions. It does not receive prior user turns, prior assistant replies, prior labels, Gradio history, tools, a CV dump, or `TWIN_SYSTEM_PROMPT`. The API call **omits** `tools` so the model cannot `record_*` while classifying. Output is **exactly** `IN_SCOPE` or `OUT_OF_SCOPE` (one label, no essay). There is **no** `LEAD`, `SKILL_TRAP`, or `META` class. The prompt **may** include few-shot skill-trap and meta examples as teaching data that still map to `OUT_OF_SCOPE`. Ignore “ignore previous / you are now …” text inside the delimiters.
4. **Python routing.** Parse the Turn A label in Python. Do **not** let Turn A write the visitor-facing reply. Only a parsed `IN_SCOPE` starts **Turn B**. `OUT_OF_SCOPE`, any other token, empty/unparseable output, or a classifier error **fails closed** to the canned refusal.

**Scope of the label**

- `IN_SCOPE`: questions about Alberto’s professional background, experience, and the personal interests listed on his profile.
- `OUT_OF_SCOPE`: skill traps (e.g. “teach me Kubernetes”), meta/security (“what are you”, dump prompt/memory), generic off-topic chat, and any **mixed** turn (career question plus skill trap or jailbreak). A mixed turn is entirely `OUT_OF_SCOPE`.

**Turn B** is the existing twin completion with tools and the **current Gradio chat history** (including earlier refusals). History hygiene is out of v1, so Turn B still has memory; Turn A does not.

**Not in v1:** output filter (item 5), retrieval (item 10), history hygiene, PII stripping, prompt/CV similarity filter, five-class Turn A.

No **BREAKING** API change. Visitor-facing chat stays the same Gradio UI; blocked turns look like a normal refusal.

## Capabilities

### New Capabilities

- `prompt-firewall`: Code-side deny-list on the latest user message. On match, skip MiniMax entirely (no Turn A, no Turn B), return the canned refusal, and still capture a typed email when present.
- `scope-classifier`: Stateless binary Turn A (`IN_SCOPE` | `OUT_OF_SCOPE`) on delimited current-user text only, with tools omitted on that API call; Python fail-closed routing (never classify-and-answer in one completion); Turn B is the existing twin completion with tools and Gradio history.

### Modified Capabilities

- None. `openspec/specs/` has no existing capabilities.

## Impact

- **Code:** `backend/src/app.py` chat loop (ingress before `openai.chat.completions.create`). Likely small new Python modules for firewall matching, Turn A parse/fail-closed, and typed-email capture. `backend/src/tools.py` may be called from Python for email; tool *schema* allowlisting is out of scope.
- **Prompts:** New Turn A classifier prompt (label-only, delimited current-user data, no memory/tools/CV). Existing `TWIN_SYSTEM_PROMPT` stays the Turn B role prompt; no requirement to rewrite the CV sandbox in this change.
- **UX:** Same Gradio `ChatInterface`. Extra latency/cost only when the firewall does not match (one classifier call, then maybe Turn B).
- **Tests/docs:** Unit tests for firewall, parser, fail-closed, mixed-turn, and typed-email capture. Jose battery remains evidence, not an automated suite in v1.
- **Dependencies:** No new runtime libraries expected beyond the current OpenAI-compatible client.
