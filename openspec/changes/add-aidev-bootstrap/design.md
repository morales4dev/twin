## Context

See [proposal.md](proposal.md) for why. Twin is a single Python Gradio app under `backend/src/` (`ChatInterface`, MiniMax-M2.5 via `OpenAI()`). `ai-specs/` is empty, `openspec/config.yaml` has no twin context, runtime deps are unpinned, there are no tests, root `README.md` is a stub, and `.vscode` still uses `${workspaceFolder:twin}`. Specs are skipped (`skip_specs: true`). This design is file layout and apply order only; chat behavior in `backend/src/app.py` stays as-is.

## Goals / Non-Goals

**Goals:**

- One constitution path agents actually load, plus twin-native OpenSpec context/rules.
- Pinned runtime and test deps, with test deps out of production `requirements.txt`.
- A pytest-importable `backend/tests/` tree and a Playwright slot that is not a live MiniMax suite.
- Operator onboarding: `.env.example`, single-folder `.vscode`, real `README.md`.
- Drop unused Copilot cloud-agent leftovers.

**Non-Goals:**

- Design-level restatement of proposal scope. Also: no product specs, no custom OpenSpec schema, no `.vscode/mcp.json`, no CI, no live MiniMax E2E, no extra OpenSpec skills.

## Decisions

1. **Canon in `ai-specs/AGENTS.md`; thin root `AGENTS.md`.**
   Copilot loads root `AGENTS.md`. Root file is a pointer (read `ai-specs/AGENTS.md` first; language: repo English / user Spanish in chat). Do not add `.github/copilot-instructions.md` unless apply proves Copilot ignores `AGENTS.md`.
   Alternative: duplicate the constitution in `.github/copilot-instructions.md` now — rejected (two sources of truth).

2. **Agent standards live under `ai-specs/standards/`; product specs stay `openspec/specs/`.**
   v1 files (English, short): `python.md` (stack, MiniMax, pins, no unused transitives), `testing.md` (pytest units; Playwright drives Gradio chat, not a live MiniMax suite in v1), `context7.md` (resolve library IDs; pass pinned versions; do not pin a hosted MCP URL). Always write those full paths in constitution and `config.yaml`.
   Alternative: one mega `AGENTS.md` — rejected (harder to point OpenSpec `context` at).

3. **`openspec/config.yaml`: fill `context` + `rules`; `githubCopilot.cloudAgent: false`; delete `.github/workflows/copilot-setup-steps.yml`.**
   Context names Python 3.12.12, Gradio ChatInterface, MiniMax via OpenAI-compatible client, pytest, Playwright-on-Gradio, `ai-specs/` paths. Rules: proposal/design stay twin-native; tasks stay small and do not invent product specs. Schema stays `spec-driven`.
   Alternative: keep `cloudAgent: true` and expand the workflow — rejected (no cloud coding agent in use).

4. **Context7 is a constitution policy, not MCP plumbing.**
   Standards say: resolve the correct library ID, then query with the pinned package version (gradio 6.26.0, openai 3.8.0, etc.). Exact Context7 ID strings are filled at apply after a resolve pass.
   Alternative: commit `.vscode/mcp.json` — rejected (proposal non-goal).

5. **Pin runtime in `backend/requirements.txt`; test deps in `backend/requirements-dev.txt`.**
   Runtime pins from current venv: `gradio==6.26.0`, `openai==3.8.0`, `pypdf==6.17.0`, `python-dotenv==1.2.3`, `requests==2.34.2`. Python 3.12.12 is documented, not a pip pin. Apply **first** installs pytest + Playwright into `backend/.venv`, reads installed versions, then writes `requirements-dev.txt` and only then writes constitution/standards that name those pins. Do not pin unused transitives (fastapi, uvicorn, httpx).
   Alternative: extras in `pyproject.toml` — rejected (repo is already pip + `requirements.txt`).

6. **Tests: `backend/tests/unit/` + `backend/tests/e2e/`; pytest config in `backend/`.**
   `backend/pytest.ini` (or `pyproject.toml` only if we would otherwise add one — we will not) sets `testpaths = tests` and `pythonpath = src` so tests can import existing modules without packaging the app. v1 unit smoke: import-level / no network. v1 e2e: placeholder module or skip marker documenting Gradio `ChatInterface` as the future target — **do not** call MiniMax. Playwright is a pinned dep and a standard, not a green suite in v1.
   Alternative: tests at repo root — rejected (venv and app live under `backend/`).

7. **`.env.example` at repo root; launch loads it via VS Code `envFile`.**
   Names only: `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `PUSHOVER_USER`, `PUSHOVER_TOKEN`. Matches the existing gitignored root `.env`. `app.py` / `tools.py` keep `load_dotenv()` as-is (no chat-loop change). `.vscode/launch.json` sets `"envFile": "${workspaceFolder}/.env"` so debug works with a single-folder workspace even when `cwd` is `backend`.
   Alternative: move example under `backend/` or change `load_dotenv` path — rejected (root `.env` already exists; proposal said no required product change to `app.py`).

8. **`.vscode` for a single-folder workspace.**
   `settings.json`: `python.defaultInterpreterPath` = `${workspaceFolder}/backend/.venv/bin/python`; only the `backend` Python project. `launch.json`: program/python/cwd use `${workspaceFolder}/backend/...`. Drop `${workspaceFolder:twin}` and the extra project on `.`.
   Alternative: keep the `twin` folder name in variables — rejected (breaks when this repo is the workspace root).

9. **Root `README.md` is the human onboarding page; constitution is the agent onboarding page.**
   README (English): what twin is, stack/pins, create/use `backend/.venv`, copy `.env.example` → `.env`, run `backend/src/app.py`, run pytest from `backend/`, pointer to `ai-specs/` vs `openspec/specs/`. Do not dump the full constitution into README.
   Alternative: README-only, skip `ai-specs/AGENTS.md` — rejected (agents would still have no canon).

10. **OpenSpec skills stay in `.github/skills/`.**
    Do not move them into `ai-specs`. No new OpenSpec skills in v1.

**Apply order (so pins in docs match the venv):**

1. Install pytest + Playwright into `backend/.venv`; record versions; write `requirements-dev.txt`; pin `requirements.txt`.
2. Write `ai-specs/AGENTS.md`, `ai-specs/standards/*`, thin root `AGENTS.md`.
3. `openspec/config.yaml`; delete `copilot-setup-steps.yml`.
4. `backend/pytest.ini` + `backend/tests/...` smoke/placeholder.
5. `.env.example`, `.vscode`, `README.md`.
6. `openspec validate add-aidev-bootstrap --type change`.

## Risks / Trade-offs

- [Copilot ignores root `AGENTS.md`] → Mitigation: apply ships only `AGENTS.md`; if ignored, a follow-up adds `.github/copilot-instructions.md` as a pointer, not a second constitution.
- [pytest cannot import `backend/src` modules] → Mitigation: `pythonpath = src` in `backend/pytest.ini`; smoke test is the check.
- [Playwright install is heavy / unused in v1] → Mitigation: pin it and document the e2e slot; do not run a browser suite against MiniMax.
- [`.env` at root vs `load_dotenv()` from `backend` cwd] → Mitigation: VS Code `envFile`; README states copy-to-root `.env`; no silent write of secrets.
- [Context7 IDs guessed wrong] → Mitigation: resolve at apply; constitution states the policy even if a given ID is filled later.
- [Thin README vs constitution drift] → Mitigation: README points at `ai-specs/`; pins are listed once in `requirements*.txt` and referenced, not rewritten by hand in three places after apply.

## Migration Plan

No production deploy. Apply is git-only on this repo. Rollback: revert the change commit(s). `backend/.venv` already exists; apply mutates it by installing test deps — rollback of docs does not uninstall packages (acceptable; pins remain in `requirements-dev.txt` if the commit is kept).

## Open Questions

- Exact Context7 library ID strings (filled at apply after resolve).
- Exact pytest and Playwright versions (filled after install into `backend/.venv`).
