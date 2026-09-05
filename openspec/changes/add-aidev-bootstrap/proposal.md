## Why

Twin is a Python Gradio digital twin, but it has no agent constitution: `ai-specs/` is empty, `openspec/config.yaml` has no project context, and runtime deps in `backend/requirements.txt` are unpinned. Agents then invent the wrong stack and unversioned Context7 docs. We need a self-contained agent OS before more product work.

## What Changes

This change is tooling, constitution, and OpenSpec project context. It does **not** change visitor-facing twin behavior. Specs are skipped (`skip_specs: true`).

- Add a coder-agnostic constitution at `ai-specs/AGENTS.md` and a thin root `AGENTS.md` that points Copilot at it. Language: English for repo content and for chat with the user. Do not add a duplicate `.github/copilot-instructions.md` unless Copilot ignores `AGENTS.md`.
- Add agent standards under `ai-specs/standards/` (never `ai-specs/specs/`). Product specs stay in `openspec/specs/`. Always use those full paths.
- Fill `openspec/config.yaml` `context` and `rules` with twin-native constraints: Python 3.12, Gradio ChatInterface, MiniMax via OpenAI-compatible client, pytest units, pytest+Playwright driving the Gradio chat UI. Set `githubCopilot.cloudAgent` to `false`. Delete `.github/workflows/copilot-setup-steps.yml` (unused leftover; no Copilot cloud coding agent). Do **not** invent a custom OpenSpec schema.
- Encode a Context7 **library-ID policy** in constitution/standards: resolve the correct library IDs and pass pinned versions. Do **not** add `.vscode/mcp.json` in v1. Do not lock a hosted MCP server URL.
- Pin direct runtime deps from the current `backend/.venv` (do not pin unused transitives): Python 3.12.12, gradio 6.26.0, openai 3.8.0, pypdf 6.17.0, python-dotenv 1.2.3, requests 2.34.2.
- At **apply** (not in this proposal): install pytest and Playwright into `backend/.venv`, pin the installed versions, then write constitution/standards that name those pins. Keep test deps out of production `requirements.txt` (separate file or extra).
- Add a test layout under `backend/tests/`: unit tests next to pytest, and a place for Playwright Gradio chat E2E. Layout and a smoke/placeholder only; no product suite and no live MiniMax E2E in v1.
- Add a committed `.env.example` (names only, no secrets) covering `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `PUSHOVER_USER`, and `PUSHOVER_TOKEN`. `.env` stays gitignored.
- Point `.vscode/settings.json` and `.vscode/launch.json` at a single-folder workspace: `${workspaceFolder}` and only the `backend` Python project (drop `${workspaceFolder:twin}` and the extra project on `.`).
- Replace the stub root `README.md` with a real English README: what twin is, stack/pins, venv, env vars, how to run, how to test, and where agent OS vs product specs live.
- Keep `.github/skills` OpenSpec skills in place; do not move them into `ai-specs`.

**Non-goals (v1)**

- Product capability specs.
- Custom OpenSpec schema.
- `.vscode/mcp.json` / MCP server availability plumbing.
- CI.
- Live MiniMax E2E.
- Extra OpenSpec skills beyond those already under `.github/skills`.

No **BREAKING** API or Gradio UX change.

## Capabilities

### New Capabilities

- None. This change does not introduce product behavior. `skip_specs: true` is set on the change.

### Modified Capabilities

- None. `openspec/specs/` has no existing capabilities, and none should be invented for validation.

## Impact

- **Agent OS:** `ai-specs/AGENTS.md`, `ai-specs/standards/`, thin root `AGENTS.md`. `ai-specs/.gitkeep` is replaced by real files.
- **OpenSpec:** `openspec/config.yaml` context + rules, and `githubCopilot.cloudAgent: false`. Delete `.github/workflows/copilot-setup-steps.yml`. Change metadata `skip_specs: true`. Skills stay under `.github/skills`.
- **Dependencies:** pin `backend/requirements.txt`; add a test-deps file/extra after pytest and Playwright are installed at apply.
- **Env/IDE:** `.env.example`; `.vscode` paths for a single-folder workspace.
- **App code:** no required change to `backend/src/app.py` product behavior. Playwright E2E standards will target the existing Gradio `ChatInterface` in later apply/test work.
- **Docs/tests:** constitution and standards in v1; real root `README.md`; `backend/tests/` layout (units + Playwright slot). Exact Context7 library ID strings and pytest/Playwright versions are apply-time fill-ins, not proposal blockers.
- **Out of impact:** hosted MCP server pin, CI, live MiniMax E2E.
