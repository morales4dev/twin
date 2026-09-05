# Twin agent constitution

Read this file first. Product specs live in `openspec/specs/`. Agent standards live under `ai-specs/standards/` (never `ai-specs/specs/`).

## Language

- Repo content (code, docs, issues, commits): English.
- Chat with the user: English.

## Stack

See `ai-specs/standards/python.md`. Python 3.12.12, Gradio `ChatInterface`, MiniMax via OpenAI-compatible client. Pins are in `backend/requirements.txt` and `backend/requirements-dev.txt`; do not invent unpinned stacks.

## Testing

See `ai-specs/standards/testing.md`. Pytest units under `backend/tests/unit/`. Playwright targets Gradio chat, not a live MiniMax suite in v1.

## Docs lookup

See `ai-specs/standards/context7.md`. Resolve Context7 library IDs, then query with pinned versions. No hosted MCP URL pin. No `.vscode/mcp.json`.

## OpenSpec

Schema stays `spec-driven`. Do not invent product specs for tooling-only changes. Keep `.github/skills/` OpenSpec skills in place; do not move them into `ai-specs`.
