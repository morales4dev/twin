## Why

Turn B sends the entire Gradio `history` to MiniMax on every in-scope turn (`system + history + current user`). That list grows without a cap. A recruiter chat does not need the full thread in the model; it needs a bounded window so context cost stays predictable. This is history hygiene for Turn B: drop oldest, no summarization.

## What Changes

On Turn B only, drop the oldest prior turns until at most **8 turns** remain in the MiniMax payload. A turn is one user+assistant pair. The current user string is always appended after that window and is never dropped.

- `chat()` still receives Gradio’s full `history` and still passes that list through. The ChatInterface transcript does not change.
- The window is applied when building the Turn B messages: **system + windowed history + current user**. If history has 8 turns or fewer, MiniMax still sees all of it. If it has more, MiniMax sees only the newest 8.
- Do not mutate Gradio’s `history` list. Window from a copy or slice.
- The current-turn tool loop is unchanged. Turn A stays stateless (no history).
- Units must cover both sides of the cap: history shorter than 8 turns (everything is sent) and history longer than 8 turns (oldest pairs are absent from the MiniMax `messages`, newest 8 plus the current user are present). Drive `complete()` (and ingress if it asserts Turn B kwargs). Units still must not hit the network.

No **BREAKING** Gradio UX change. The visitor still sees every prior bubble.

**Non-goals**

- Summarization, anchors, or a metadata extractor.
- Changing Gradio `ChatInterface`, clearing or rewriting the on-screen transcript, or mutating `history` in place.
- Giving Turn A memory.
- Changing deny-list / input-guardrail behavior, canned refusal text, LEAD_ACK, classifier prompt, or tools.
- LiteLLM, timeouts, retries, caches.
- Archiving this change (archive only after a later explicit user request).

## Capabilities

### New Capabilities

- `conversation-window`: Turn B sends at most the newest 8 prior turns (user+assistant pairs) plus the current user message. Older pairs are dropped from the MiniMax payload only. Gradio history and the visible chat stay complete.

### Modified Capabilities

- `scope-classifier`: The Turn B requirement that sends “the current Gradio chat history (including earlier refusals)” and marks history hygiene out of scope is replaced. Turn B still uses the same model, twin system prompt, and tools. History sent to MiniMax is the window above. An earlier canned refusal reaches Turn B only when it still sits inside those 8 turns. Turn A stays stateless.

## Impact

- **Code:** Turn B message build in `backend/src/complete.py` (or a small helper it calls). `chat()` sequence stays capture → input gate → `classify` → `fail_closed_reply` / `complete`. MiniMax I/O stays out of `chat()`.
- **Tests:** new or extended units under `backend/tests/unit/` for `< 8` and `> 8` history turns. Assert the Turn B `messages` payload. Existing ingress assertions (Turn A without tools, Turn B with tools, fail-closed) stay. `llm_env` in `test_llm.py` deletes blank `LLM_TIMEOUT` / `LLM_RETRIES` / `PRIMARY_MODEL` / `FALLBACK_MODEL` so a names-only `.env` does not fail the unit suite. Production `get_settings()` is unchanged.
- **Specs:** new `openspec/specs/conversation-window/`; delta on `scope-classifier`.
- **Dependencies:** none.
- **Out of impact:** firewall/input-guardrail patterns, visitor copy, live MiniMax E2E, archives, pins.
