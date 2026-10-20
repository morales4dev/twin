# Python

## Layer 1 — generic small Python

- Type hints on new and changed public functions.
- Pydantic at **non-LLM** Python boundaries (config objects, parsed JSON after you already have a string, future non-LLM APIs). Pattern only: do not add `pydantic` to `backend/requirements.txt` in an OS-only change. First product import pins it.
- Do not invent APIs, SDK methods, or library behavior. If it is not in the pin or Context7, do not guess.
- SOLID, DRY, PEP 8.
- Named errors; do not swallow with bare `except`.
- Validate input at boundaries.
- Structured logs (event + fields), not ad-hoc print for new operational logging.
- Early return; keep the happy path unindented.
- Secrets stay in env (`.env` gitignored). `.env.example` lists secret names only (blank values). Typed LLM settings may show their defaults. Never commit secrets.

## Layer 2 — Twin stack

- Layout: app under `backend/src/`, venv `backend/.venv`, install with uv.
- Create the venv with `uv venv`. Install packages with `uv pip install --python backend/.venv/bin/python`. Never bare `pip install`.
- Pin only direct runtime deps in `backend/requirements.txt`. Do not pin unused transitives (fastapi, uvicorn, httpx, openai). Do not add unpinned agent SDKs.
- Runtime: Python 3.12.12 (documented; not a pip pin).
- App: Gradio `ChatInterface` under `backend/src/`.
- Model I/O: sync LiteLLM via `llm.completion` (primary then fallback). Chat stays sync. Do not document or rewrite the loop as async. Do not import `openai` or `anthropic` in `backend/src`.
- Current runtime pins:

```
gradio==6.26.0
litellm==1.106.1
pydantic-settings==2.16.1
pypdf==6.17.0
python-dotenv==1.2.3
requests==2.34.2
```

- Do not change visitor-facing chat or migrate `backend/src/**` unless a product change says so.

### Module shape

Operational default for any change that edits `backend/src`. Current `backend/src` may not match yet; do not “fix” it in an OS-only change.

| Name | Role |
| --- | --- |
| `chat()` | Gradio `(message, history) -> str`. Sequences only. |
| `classify(message, llm_completion)` | Turn A I/O. Omits `tools=`. Returns `allowed_for_turn_b` plus reason (`in_scope` / `out_of_scope` / `unparseable` / `error`). No visitor strings. |
| `complete(message, history, llm_completion)` | Turn B and the tool loop. |
| `llm.completion(messages, *, tools=None)` | Primary-then-fallback LiteLLM call. Passes tools through only when the caller supplied them. |
| `fail_closed_reply(email)` | Lead-ack vs canned. Used only after Turn A. |

- Input guardrail plus typed email stays canned.
- Inject `llm_completion` into `chat()` as an optional kwarg (Gradio still calls two arguments). `classify` and `complete` require it (no default).
- The shared helper must pass tools through. It must not add `tools=` to a call that omitted them.
- KISS, YAGNI, and DRY win over a class tree or Protocols for one implementation.
- Do not name new modules or mandate `ScopeLabel` / Pydantic here. File placement and those types belong to a later product or refactor change.

## LLM protocol (targets only)

These are coding targets for a later **product** change. Do not implement them in `backend/src/**` in an OS-only change.

- Structured model output: put `model_json_schema()` in the prompt, parse JSON in Python, then `model_validate`. Do not trust `output_type` / constrained decoding as validation.
- Tools: typed function + docstring + SDK decorator. Do not migrate week-1 hand-written tool JSON until a product change says so.
