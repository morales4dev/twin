## 1. Pins and test dependencies

- [ ] 1.1 Install pytest and Playwright into `backend/.venv` using that venv's pip and verify both import (`python -c "import pytest, playwright"`).
- [ ] 1.2 Record installed pytest and Playwright versions from `backend/.venv` (`pip show pytest playwright`) and write them as pins in `backend/requirements-dev.txt`; verify the file lists only test deps (no runtime packages from `requirements.txt`).
- [ ] 1.3 Pin direct runtime deps in `backend/requirements.txt` to `gradio==6.26.0`, `openai==3.8.0`, `pypdf==6.17.0`, `python-dotenv==1.2.3`, `requests==2.34.2` and verify unused transitives (fastapi, uvicorn, httpx) are absent.

## 2. Agent constitution and standards

- [ ] 2.1 Resolve Context7 library IDs for the pinned packages (at least gradio 6.26.0 and openai 3.8.0) and record the IDs for use in `ai-specs/standards/context7.md`; verify each ID came from a resolve pass, not a guessed string.
- [ ] 2.2 Write `ai-specs/standards/python.md` (Python 3.12.12, Gradio ChatInterface, MiniMax via OpenAI-compatible client, runtime pins, no unused transitives) and verify it names the same pins as `backend/requirements.txt`.
- [ ] 2.3 Write `ai-specs/standards/testing.md` (pytest units under `backend/tests/unit/`; Playwright drives Gradio chat, not a live MiniMax suite in v1; test deps in `requirements-dev.txt`) and verify it names the pytest/Playwright pins from `backend/requirements-dev.txt`.
- [ ] 2.4 Write `ai-specs/standards/context7.md` (resolve library IDs, pass pinned versions, do not pin a hosted MCP URL, no `.vscode/mcp.json`) and verify it includes the IDs from 2.1.
- [ ] 2.5 Write `ai-specs/AGENTS.md` as the constitution (English; pointer to `ai-specs/standards/python.md`, `testing.md`, `context7.md`; repo English / user Spanish in chat) and verify `ai-specs/.gitkeep` is gone once real files exist.
- [ ] 2.6 Write a thin root `AGENTS.md` that only points agents to read `ai-specs/AGENTS.md` first; verify `.github/copilot-instructions.md` is not created.

## 3. OpenSpec project context

- [ ] 3.1 Fill `openspec/config.yaml` `context` and `rules` (Python 3.12.12, Gradio ChatInterface, MiniMax via OpenAI-compatible client, pytest, Playwright-on-Gradio, full `ai-specs/` paths; proposal/design stay twin-native; tasks stay small and do not invent product specs), set `githubCopilot.cloudAgent: false`, keep `schema: spec-driven`, and verify no custom schema is introduced.
- [ ] 3.2 Delete `.github/workflows/copilot-setup-steps.yml` and verify the file is gone.

## 4. Test layout

- [ ] 4.1 Add `backend/pytest.ini` with `testpaths = tests` and `pythonpath = src` (do not add `pyproject.toml`) and verify pytest from `backend/` collects tests under `tests/`.
- [ ] 4.2 Add a no-network unit smoke under `backend/tests/unit/` that imports existing `src` modules and verify `pytest tests/unit` from `backend/` passes.
- [ ] 4.3 Add a Playwright e2e placeholder under `backend/tests/e2e/` (skip marker or placeholder module documenting Gradio `ChatInterface` as the future target; do not call MiniMax) and verify the file exists and is skipped or does not hit the network.

## 5. Operator onboarding

- [ ] 5.1 Add root `.env.example` with names only: `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `PUSHOVER_USER`, `PUSHOVER_TOKEN`; verify no secret values and that `.env` remains gitignored.
- [ ] 5.2 Update `.vscode/settings.json` so `python.defaultInterpreterPath` is `${workspaceFolder}/backend/.venv/bin/python` and only the `backend` Python project remains; verify `${workspaceFolder:twin}` and the extra project on `.` are gone.
- [ ] 5.3 Update `.vscode/launch.json` to use `${workspaceFolder}/backend/...` for program, python, and cwd, set `"envFile": "${workspaceFolder}/.env"`, and verify `${workspaceFolder:twin}` is gone.
- [ ] 5.4 Replace stub root `README.md` with English onboarding (what twin is, stack/pins via `requirements*.txt`, `backend/.venv`, copy `.env.example` → `.env`, run `backend/src/app.py`, pytest from `backend/`, `ai-specs/` vs `openspec/specs/`) and verify it does not paste the full constitution.

## 6. Validate

- [ ] 6.1 Run `openspec validate add-aidev-bootstrap --type change` and verify it succeeds.
- [ ] 6.2 Confirm OpenSpec skills remain under `.github/skills/` (not moved into `ai-specs`) and that `backend/src/app.py` product behavior is unchanged (`git diff -- backend/src/app.py` empty of chat-loop edits).
