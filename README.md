# twin

Digital twin: a Gradio chat app that answers career questions as a personal AI twin.

## Stack

Python 3.12.12. Pins are in `backend/requirements.txt` (runtime) and `backend/requirements-dev.txt` (pytest, Playwright). Do not copy pin lists into this README by hand after that.

App entry: `backend/src/app.py` (`gr.ChatInterface`, MiniMax-M2.5 via the OpenAI-compatible client).

## Setup

```bash
cd backend
uv venv .venv --python 3.12.12
uv pip install --python .venv/bin/python -r requirements.txt
uv pip install --python .venv/bin/python -r requirements-dev.txt
```

Copy `.env.example` to `.env` at the **repo root** and fill values. `.env` is gitignored.

## Run

From `backend/`:

```bash
.venv/bin/python src/app.py
```

VS Code launch config `Twin backend` uses `${workspaceFolder}/backend` and loads `${workspaceFolder}/.env`.

## Test

From `backend/`:

```bash
.venv/bin/python -m pytest
```

Units: `backend/tests/unit/`. Playwright E2E against Gradio chat is a later slot under `backend/tests/e2e/` (not a live MiniMax suite in v1).

## Agent OS vs product specs

- Agent constitution: `ai-specs/AGENTS.md` (standards in `ai-specs/standards/`).
- Product specs: `openspec/specs/`.
