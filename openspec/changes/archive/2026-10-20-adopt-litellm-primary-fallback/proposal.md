## Why

Turn A and Turn B talk to one hardcoded model through the OpenAI SDK (`OpenAI()`, `MiniMax-M2.5`). Specs and standards treat that vendor as the architecture. If the call fails, Turn A fail-closes and the visitor gets canned even when another provider could answer. Twin needs a provider-agnostic client, a second model, and a deadline.

## What Changes

Replace direct OpenAI SDK calls with **LiteLLM**. Do not import OpenAI or Anthropic SDKs in `backend/src`. Primary first; fallback if that **call** fails.

- **Primary** is an OpenAI-compatible model (today’s default id stays `MiniMax-M2.5`, via `OPENAI_API_KEY` + `OPENAI_BASE_URL`). It is not “the OpenAI model” and not “the MiniMax architecture.”
- **Fallback** is Anthropic (default id `claude-haiku-4-5-20251001`, via `ANTHROPIC_API_KEY`).
- **Trigger:** the LLM call raises (timeout, provider/network error). Then try fallback. `OUT_OF_SCOPE`, unparseable labels, and canned refusals do **not** trigger fallback.
- **Turn A and Turn B** both use that rule. Each call is independent (A may land on fallback, B on primary).
- **Fail-closed** (no Turn B / canned or LEAD_ACK as today) only when **both** primary and fallback fail on Turn A, or when the label is out-of-scope / unparseable. A successful fallback classify is a normal `IN_SCOPE` / `OUT_OF_SCOPE`.
- **Timeout** `LLM_TIMEOUT=30` and **transport retries** `LLM_RETRIES=2` on the same model, then fallback. Not schema re-prompts.
- Vocabulary in live specs and Agent OS: say **primary / fallback / LLM call**, not MiniMax. `chat()` still sequences only; I/O stays in `classify` / `complete`. The injectable seam is the LiteLLM client, not `OpenAI()`. Turn B still sends `tools=`; Turn A still omits them.
- Env (names only in `.env.example`): keep `OPENAI_API_KEY` / `OPENAI_BASE_URL`; add `ANTHROPIC_API_KEY`, `PRIMARY_MODEL`, `FALLBACK_MODEL`, `LLM_TIMEOUT`, `LLM_RETRIES`.

No **BREAKING** Gradio UX. A primary outage may now yield a real classify/answer instead of canned.

**Non-goals**

- A LiteLLM Router class, structured-output retries, caches, or a flashy wait UI.
- Sticky model for the whole Gradio turn.
- Fallback on bad labels or out-of-scope.
- Changing deny-list patterns, canned text, LEAD_ACK, classifier prompt, tools JSON, or conversation-window (that is `add-conversation-window`).
- Editing the other in-flight proposals.
- Archiving this change (archive only after a later explicit user request).

## Capabilities

### New Capabilities

- `primary-fallback`: LiteLLM-only LLM I/O. Primary is OpenAI-compatible; fallback is Anthropic. On a raised call, retry the same model up to `LLM_RETRIES`, then try fallback. Deadline `LLM_TIMEOUT`. Applies to Turn A and Turn B independently. Tools stay on Turn B only.

### Modified Capabilities

- `prompt-firewall`: “Must not call MiniMax” becomes must not call the LLM (primary or fallback). Deny-list, canned refusal, and silent email stay.
- `scope-classifier`: Drop “same MiniMax model” / “MiniMax completion.” Classify and answer stay separate LLM calls through LiteLLM. Turn A error fail-closed means both primary and fallback failed, not “the first create raised.” Unparseable / `OUT_OF_SCOPE` still fail-closed with no fallback. Turn B still uses the twin prompt and tools.

## Impact

- **Code:** `classify` / `complete` (and the optional `chat()` client) go through LiteLLM. `MODEL_NAME` becomes settings (`PRIMARY_MODEL` / `FALLBACK_MODEL`). Primary needs `api_base` from `OPENAI_BASE_URL`.
- **Tests:** fake the LiteLLM seam, not `OpenAI()`. Cover primary success, primary fail → fallback success, both fail → Turn A fail-closed. Units still must not hit the network. Rename test helpers that say `minimax`.
- **Agent OS:** `ai-specs/standards/python.md` and `testing.md` (client + “MiniMax in units”); `openspec/config.yaml` context/rules that say MiniMax.
- **Dependencies:** pin `litellm` in `backend/requirements.txt`. Drop the direct `openai` pin if nothing imports it.
- **Out of impact:** visitor copy, deny patterns, archives, Playwright live-model E2E, the other open changes’ markdown until those changes are updated.
