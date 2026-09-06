## Context

See proposal.md (Why / What Changes) and the delta specs for `prompt-firewall` and `scope-classifier`.

Today `backend/src/app.py` `chat(message, history)` builds `system + history + user` and calls MiniMax once with `tools`. There is no ingress gate. The canned refusal already exists in `TWIN_SYSTEM_PROMPT` (Hard Rejection phrase). `record_user_details` in `backend/src/tools.py` is model-invoked and posts to Pushover.

Constraints: Python 3.12.12, sync OpenAI-compatible client, no new runtime libraries, units under `backend/tests/unit/` with I/O mocked, no live MiniMax in units.

## Goals / Non-Goals

**Goals:**

- Insert a Python ingress pipeline in front of the existing Turn B loop without changing the Gradio `ChatInterface`.
- Keep classify vs answer as two different MiniMax completions (Turn A never answers).
- Enforce firewall, label parse, and typed-email capture in Python so MiniMax cannot skip them.
- Stay on the current sync `OpenAI()` client and current pins.

**Non-Goals:**

- Output filter, retrieval, history hygiene, PII stripping, prompt/CV similarity filter, five-class Turn A (see proposal).
- Tool-schema allowlisting or capping the Turn B tool loop.
- Rewriting `TWIN_SYSTEM_PROMPT` / CV sandbox.
- New runtime dependencies (including Pydantic; parse the two labels with plain Python).
- Automated Jose battery as a test suite.

## Decisions

### 1. Ingress pipeline inside `chat()`, small helpers beside it

`chat()` becomes: capture typed email (keep the extracted address in Python) → firewall → Turn A → parse/fail-closed → Turn B, canned refusal, or LEAD_ACK.

Helpers live in small modules under `backend/src/` (firewall match, Turn A prompt + parse, email extract, LEAD_ACK copy). `app.py` stays the Gradio entry and owns the MiniMax calls.

Visitor-facing reply after extract (see diagram below):

- Firewall match → canned refusal. If an email was recorded this turn, capture is **silent** (no LEAD_ACK).
- Parsed `IN_SCOPE` → existing Turn B loop (unchanged).
- Turn B does not run (`OUT_OF_SCOPE` or fail-closed) **and** this turn had a typed email → Python LEAD_ACK interpolating that extracted address. No Turn B.
- Turn B does not run and this turn had no typed email → canned refusal.

```text
                    latest user string
                            │
                            ▼
                 extract typed email?
                    │ yes: record + keep address
                    ▼
                 firewall match?
                    │
         yes ───────┴─────── no
          │                  │
          ▼                  ▼
     canned refusal      Turn A (no tools)
     (silent capture     parse label in Python
      if email)              │
                    IN_SCOPE ┤
                             │ else (OUT_OF_SCOPE / fail-closed)
                             ▼
                      typed email this turn?
                       │ yes          │ no
                       ▼              ▼
                    LEAD_ACK     canned refusal
                    (no Turn B)   (no Turn B)

                    IN_SCOPE → Turn B (twin + tools + history)
```

Alternative considered: all logic in `app.py`. Rejected; the loop would mix matching, prompting, and the tool while-loop.

Alternative considered: middleware outside Gradio. Rejected; there is no HTTP API, only `ChatInterface`.

### 2. Deny-list is configured pattern families, not the Jose corpus

Implement case-insensitive matching against the families in backlog item 6 / the firewall spec (override, forged system, slash commands, show prompt/memory, debug framing). Keep patterns in one module-level list so tests can assert family hits without importing Jose transcripts.

Matching: substring / simple regex over the raw latest user string. No tokenizer, no extra library.

Alternative considered: LLM-only jailbreak detection. Rejected; firewall must skip MiniMax entirely on match.

### 3. Typed email: Python extract + existing `record_user_details`

Before the firewall result is returned, scan the latest user string with a conservative email regex (must contain `@` and a dot in the domain; no display-name RFC parser). If one or more addresses match, call `record_user_details` from Python with the first typed address. Do not read history or the sandbox.

Turn B tools stay as they are (allowlisting is out of scope). An in-scope turn that also contains a typed email may therefore Pushover twice if the model also calls the tool. Accepted for v1; blocked/out-of-scope turns still record the typed address without a model.

Firewall + typed email: record in Python, return the canned refusal, do **not** acknowledge the address (silent capture). A lead ack on a deny-list hit would confirm the capture channel to an injector.

When Turn B does not run and this turn had a typed email (`OUT_OF_SCOPE` or fail-closed: unparseable label or Turn A exception), Python returns LEAD_ACK. Fail-closed with an email is treated like `OUT_OF_SCOPE`, not like the firewall: the deny-list did not fire and the address is already recorded. Interpolate only the **extracted** address; MiniMax MUST NOT write this reply. Do not start Turn B because the message contained an email.

LEAD_ACK copy (Python constant; interpolate `{email}` with the extracted address):

> Thanks — I have recorded {email} so Alberto can follow up. I can still only discuss his professional background, experience, and the interests on his profile. What would you like to know about that?

Alternative considered: Gradio email form. Out of v1 (backlog item 12).

Alternative considered: block Turn B from calling `record_user_details`. That is tool allowlisting; out of scope.

Alternative considered: third Turn A label `LEAD`. Rejected; duplicates the regex and lets the model lie.

Alternative considered: run Turn B whenever an email is present. Rejected; that reopens tool abuse on off-topic turns.

### 4. Turn A request shape

Same `MODEL_NAME` (`MiniMax-M2.5`). Messages: classifier system prompt + one user message wrapping the current string in delimiters (e.g. `<user_message>…</user_message>`). No `tools` argument. No `history`. No `TWIN_SYSTEM_PROMPT`. No CV.

Classifier system prompt: label-only, binary, mixed → `OUT_OF_SCOPE`, ignore override text inside delimiters, optional few-shot skill-trap/meta examples that map to `OUT_OF_SCOPE`.

Alternative considered: five-class Turn A. Rejected in proposal.

Alternative considered: JSON object output. Rejected; two tokens, parse in Python, no new deps.

### 5. Parse fail-closed in Python

MiniMax-M2.5 may wrap chain-of-thought in `<think>…</think>` before the label. Python owns that noise.

Normalize Turn A `message.content`:

1. If content is None, unparseable.
2. Remove every `<think>…</think>` block (case-insensitive; blocks may span newlines). Do not read tokens inside those blocks.
3. Strip whitespace on what remains, take the first non-empty line, uppercase.
4. If that token is exactly `IN_SCOPE` or `OUT_OF_SCOPE`, use it.

Anything else (None, empty after strip, extra prose, JSON, tool_calls, unexpected finish, a label that appears only inside `<think>`) → no Turn B; visitor reply is LEAD_ACK if this turn had a typed email, otherwise the canned refusal.

Do not search the original string for `IN_SCOPE` / `OUT_OF_SCOPE`: the think text already names those tokens and can pick the wrong one.

Alternative considered: regex-search the raw completion for the first `IN_SCOPE|OUT_OF_SCOPE`. Rejected; MiniMax reasons about both labels inside `<think>`.

Classifier API exceptions → no Turn B; same visitor-reply split as unparseable output (LEAD_ACK if typed email this turn, else canned). Do not retry Turn A in v1.

Visitor-facing **canned refusal** is the exact Hard Rejection sentence already in `context.py`. Put it in one shared constant so firewall, no-email fail-closed, and tests compare the same string. LEAD_ACK is a second Python constant (with `{email}` interpolation). Do not import the full twin prompt into the firewall. MiniMax MUST NOT generate either string.

### 6. Turn B is the current loop unchanged

On parsed `IN_SCOPE`, call the existing `messages = system + history + user` + `tools` + tool while-loop. History still includes earlier refusals.

### 7. Tests first, MiniMax mocked

Units in `backend/tests/unit/`: firewall family hits/misses, email extract (present / absent / not invented), label parse (including a `<think>` wrapper then a label, and a label only inside `<think>`), fail-closed (bad token, empty, exception), mixed-turn expected label for the parser (fixture string `OUT_OF_SCOPE` → no Turn B), LEAD_ACK copy interpolates the extracted address, and `chat()` orchestration with a mocked `openai.chat.completions.create` (firewall match → zero calls + canned; firewall match + typed email → record + canned, no LEAD_ACK; `IN_SCOPE` → two calls, second with tools; `OUT_OF_SCOPE` / unparseable / Turn A exception without email → one call without tools + canned, no Turn B; same three without Turn B **with** typed email → record + LEAD_ACK). No network.

## Risks / Trade-offs

- **Paraphrase bypass of the deny-list** → Firewall is a cheap first hop only; Turn A still fail-closes unknown/meta/mixed. Iterate patterns later; do not copy Jose.
- **Classifier injection / essay instead of a label** → Delimited data + Python exact-token parse after stripping `<think>` blocks; fail closed. Do not harvest a label from inside the think block.
- **False `IN_SCOPE` on a skill trap** → Mixed and skill-trap few-shots in Turn A; v1 still has no output filter (known residual).
- **False firewall hits on recruiter phrasing** → Keep families tight (slash commands, forged SYSTEM, explicit dump/debug). Do not add bare `grep` as a lone token unless tests show it is required; prefer “show your prompt/memory” and debug framing.
- **Double Pushover on in-scope + typed email** → Accepted until tool allowlisting.
- **LEAD_ACK vs canned on fail-closed + email** → Acknowledge: deny-list did not fire; silent capture is reserved for firewall hits.
- **LEAD_ACK echoes the typed address** → Interpolate only the regex extract from this turn; never invent or pull from history.
- **Extra latency/cost on every unblocked turn** → One short Turn A before maybe Turn B; firewall matches pay zero model cost.
- **Turn B still has full history (crescendo)** → Explicit non-goal; Turn A stays stateless anyway.

## Migration Plan

- Feature branch; no API versioning (same Gradio app).
- Deploy is process restart of the Gradio app.
- Rollback: revert the ingress in `chat()` to the current single completion with tools.
- No data migration.

## Open Questions

None that block specs or this approach. Pattern-list wording can be tuned at apply time inside the families above without changing requirements.
