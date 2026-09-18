## Context

See [proposal.md](proposal.md) for why. Twin already has the Agent OS from archived `improve-aidev-bootstrap`: constitution `ai-specs/AGENTS.md`, standards, project skill `ai-specs/skills/adversarial-review/`, thin root `AGENTS.md`. OpenSpec CLI skills and `/opsx-*` prompts live only under `.github/`. Cursor 1.12.0 discovers skills from `.cursor/skills/` (and `.agents/skills/`), not `.github/skills/`. There is no `.cursor/` tree today. Product specs `prompt-firewall` and `scope-classifier` exist and must not be touched. Specs are skipped (`skip_specs: true`). This design is OS delivery and discovery; do not edit `backend/src/**`.

OpenSpec CLI on this machine is **1.12.0**. `openspec update` has `--force` only; it refreshes **already configured** tools. `--tools` belongs to `openspec init`, not `update`.

## Goals / Non-Goals

**Goals:**

- Generate Cursor OpenSpec skills and commands with the official CLI, beside the existing Copilot files.
- Name both IDE skill roots in the constitution and in `openspec/config.yaml` design rules.
- Keep one constitution and the existing Copilot cloud-agent off switch.

**Non-Goals:**

- Design-level restatement of proposal scope. Also: no product specs, no `backend/src/**` edits, no MCP files, no second constitution, no archive in this change.

## Decisions

1. **Generate Cursor with `openspec init --tools cursor`, not `openspec update --tools cursor`.**
   On 1.12.0, `update --tools` does not exist. `update` only rewrites tools it already detects as configured. Cursor is not configured until `.cursor/` exists. `init --tools cursor` is non-interactive and, because `openspec/` already exists, runs in extend mode.
   Alternative: hand-copy `.github/skills/` and rewrite prompts into `.cursor/commands/` — rejected (forks the official adapter; Cursor uses flat `/opsx-*` command files, not Copilot `.prompt.md`).
   Alternative: `openspec init --tools github-copilot,cursor --no-copilot-cloud` — rejected for apply. It would refresh Copilot generated files in the same pass. Dual-tool here means **leave Copilot bytes alone** unless a later change is about upgrading both.

2. **Do not pass `--no-copilot-cloud` on the Cursor-only init.**
   That flag is ignored (and warns) when `github-copilot` is not in the selected tool list. Cloud-agent policy stays the existing `githubCopilot.cloudAgent: false`. After init, verify no new `.github/workflows/copilot-setup-steps.yml` or other cloud-agent files appeared.
   Alternative: include `github-copilot` in `--tools` just to pass the flag — rejected (touches Copilot files).

3. **Constitution names both load paths; project skills stay `ai-specs/skills/`.**
   Update Canonical OS tree and Load skills in `ai-specs/AGENTS.md` so Copilot loads `.github/skills/` and Cursor loads `.cursor/skills/`. Keep “do not move OpenSpec CLI skills into `ai-specs`.” Do not add a thin Cursor skill that only points at `adversarial-review`; load project skills on demand as today.
   Alternative: move OpenSpec skills into `ai-specs/skills/` — rejected (constitution already forbids it; Cursor and Copilot would both break until adapters change).
   Alternative: symlink `.cursor/skills` → `.github/skills` — rejected (Cursor command frontmatter and paths differ; OpenSpec owns both trees).

4. **One constitution. No `.cursor/rules/` dump.**
   Root `AGENTS.md` already always-applies in Cursor and points at `ai-specs/AGENTS.md`. Do not copy the constitution into `.cursor/rules/*.mdc` and do not add a second `AGENTS.md`. Optional later glob rules that only point at `python.md` / `testing.md` stay out of this change.
   Alternative: always-apply `.cursor/rules/agents.mdc` with the full constitution — rejected (two sources of truth).

5. **`openspec/config.yaml` rules, not a new Cursor config block.**
   Keep `schema: spec-driven`, twin-native `context`, and `githubCopilot.cloudAgent: false`. Extend the design rule that today says OpenSpec CLI skills stay under `.github/skills/` so it also names `.cursor/skills/`. Do not invent a `cursor:` key the CLI does not already use here. Optional one line in `context` that Copilot and Cursor are both delivery surfaces is enough.
   Alternative: drop the Copilot YAML block — rejected (user chose dual-tool).

6. **MCP stays out of git.**
   `ai-specs/standards/context7.md` forbids committing `.vscode/mcp.json` and hosted MCP URLs. Apply must not add `.cursor/mcp.json` either. If `openspec init` writes one, delete it before finishing apply.
   Alternative: commit a Cursor MCP pin so Context7 “just works” — rejected (same policy as VS Code).

7. **README: one launch sentence, not an OS dump.**
   Run today mentions the VS Code launch config `Twin backend`. Add that Cursor uses the same `.vscode` launch config and interpreter. Do not paste constitution or `/opsx-*` lists into README.

8. **Quality gate without CI.**
   Feature branch `feature/add-cursor-to-agent-os`. Verify with existing `backend` pytest units (no network) and `openspec validate add-cursor-to-agent-os --type change`. Confirm `.github/` Copilot files still exist and `.cursor/skills/` plus `.cursor/commands/opsx-*.md` exist for the core workflows. Do not add GitHub Actions.

**Apply order:**

1. Feature branch `feature/add-cursor-to-agent-os` from Twin's default branch.
2. Snapshot `.github/skills/`, `.github/prompts/`, `.github/agents/` (they must still exist after generate).
3. Run `openspec init --tools cursor` from the Twin root (extend mode). Do not hand-copy if it fails.
4. Confirm `.cursor/skills/openspec-*/SKILL.md` and `.cursor/commands/opsx-*.md` for explore, propose, apply, update, sync, archive. Remove any `.cursor/mcp.json` if the CLI wrote one.
5. Update `ai-specs/AGENTS.md` Canonical OS tree + Load skills for both IDE paths. Leave root `AGENTS.md` thin.
6. Update `openspec/config.yaml` design rule (and a short `context` line if needed). Keep `githubCopilot.cloudAgent: false`.
7. README Run: Cursor uses the same `.vscode` launch/interpreter.
8. Verify: `git diff -- backend/src` empty; no MCP json committed; Copilot files still present; pytest units; `openspec validate add-cursor-to-agent-os --type change`.

## Risks / Trade-offs

- [`openspec init --tools cursor` rewrites or deletes Copilot files] → Mitigation: snapshot `.github/` first; abort apply if skills, prompts, or `openspec.agent.md` disappear; do not pass `github-copilot` in `--tools`.
- [Init writes extra Cursor files (MCP, rules, cloud leftovers)] → Mitigation: allow only `.cursor/skills/` and `.cursor/commands/`; delete `.cursor/mcp.json` if created; verify no new Copilot cloud-agent workflow.
- [Agents load the wrong skill tree] → Mitigation: constitution says Copilot → `.github/skills/`, Cursor → `.cursor/skills/`; project skills stay `ai-specs/skills/` on demand.
- [Cursor needs an IDE restart to see new commands] → Mitigation: `cursor` tool marks `requiresIdeRestart`; mention restart in the apply verify note, not in README process dumps.
- [A later `openspec update` refreshes only detected tools and drifts one adapter] → Mitigation: after this change both trees exist, so `openspec update` can refresh both; this apply does not run a Copilot refresh.

## Migration Plan

No production deploy. Apply is git-only OS delivery files plus constitution/config/README pointers. Rollback: revert the change commit(s). Do not uninstall venv packages (pins unchanged). Do not archive until a later explicit user request.
