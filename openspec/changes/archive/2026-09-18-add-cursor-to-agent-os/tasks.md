## 1. Setup

- [x] 1.1 Create and switch to `feature/add-cursor-to-agent-os` from Twin's default branch and verify `git branch --show-current` prints that name.
- [x] 1.2 Record that `.github/skills/openspec-*/SKILL.md`, `.github/prompts/opsx-*.prompt.md`, and `.github/agents/openspec.agent.md` exist, and verify no `.cursor/` tree exists yet.

## 2. Cursor delivery

- [x] 2.1 From Twin root, run `openspec init --tools cursor` (do not pass `--no-copilot-cloud`, do not pass `github-copilot`, do not hand-copy) and verify the command exits 0 in extend mode.
- [x] 2.2 Confirm `.cursor/skills/openspec-explore`, `openspec-propose`, `openspec-apply-change`, `openspec-update-change`, `openspec-sync-specs`, and `openspec-archive-change` each have a `SKILL.md`, and verify those six directories exist.
- [x] 2.3 Confirm `.cursor/commands/opsx-explore.md`, `opsx-propose.md`, `opsx-apply.md`, `opsx-update.md`, `opsx-sync.md`, and `opsx-archive.md` exist, and verify they use Cursor `/opsx-*` frontmatter (not Copilot `.prompt.md`).
- [x] 2.4 Confirm Copilot files from 1.2 still exist and were not deleted, and verify no new `.github/workflows/copilot-setup-steps.yml` appeared.
- [x] 2.5 Delete `.cursor/mcp.json` if `openspec init` created it, and verify neither `.cursor/mcp.json` nor `.vscode/mcp.json` is present. Do not add `.cursor/rules/` that paste the constitution.

## 3. Constitution and OpenSpec rules

- [x] 3.1 Update `ai-specs/AGENTS.md` Canonical OS tree and Load skills so Copilot loads `.github/skills/` and Cursor loads `.cursor/skills/`, keep project skills in `ai-specs/skills/` on demand, and verify OpenSpec skills are still forbidden from `ai-specs/` and root `AGENTS.md` is still only the thin pointer plus English.
- [x] 3.2 Update `openspec/config.yaml` design rules so OpenSpec CLI skills are named under both `.github/skills/` and `.cursor/skills/`, optionally add one `context` line that Copilot and Cursor are both delivery surfaces, and verify `schema: spec-driven` and `githubCopilot.cloudAgent: false` remain.

## 4. Operator docs

- [x] 4.1 Update root `README.md` Run so it says Cursor uses the same `.vscode` launch config `Twin backend` and interpreter, and verify it does not paste the constitution or an `/opsx-*` list.

## 5. Verify (no product rewrite)

- [x] 5.1 Run `git diff -- backend/src` and verify it is empty.
- [x] 5.2 Confirm `openspec/specs/prompt-firewall` and `openspec/specs/scope-classifier` were not edited, and verify no files exist under `openspec/changes/add-cursor-to-agent-os/specs/`.
- [x] 5.3 From `backend/`, run `.venv/bin/python -m pytest tests/unit` and verify the existing unit smoke still passes with no network.
- [x] 5.4 Run `openspec validate add-cursor-to-agent-os --type change` from Twin and verify it succeeds with `skip_specs: true`.
- [x] 5.5 Note that Cursor may need an IDE restart before `/opsx-propose` appears, and verify no `openspec archive` was run.
