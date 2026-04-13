# PBIR CLI Integration Policy

This repository may use the local `pbir` CLI as an **optional execution backend** for local PBIR report operations.

## Design Intent

`pbir` is used only for packaged commands where it improves speed, repeatability, or safety for PBIR report work.

The repository remains the source of truth for:
- agent behavior
- skill procedures
- fallback logic
- validation rules
- PBIR implementation conventions

The CLI is an implementation aid, not a replacement for repository knowledge.

## Hard Boundaries

1. Do **NOT** run `pbir setup` in this repository.
2. Do **NOT** install external agent plugins, hooks, skills, or instructions that could overwrite or conflict with `.github/agents`, `.github/skills`, `.github/prompts`, or `.github/copilot-instructions.md`.
3. Do **NOT** treat CLI-generated conventions as authoritative if they conflict with repository references or validated Microsoft documentation.
4. Do **NOT** make `pbir` a mandatory prerequisite for the overall multi-agent system.
5. Do **NOT** rely on a previously active `pbir` connection from another repository, project, or terminal session.
6. Do **NOT** hand-edit PBIR report JSON files (`visual.json`, `page.json`, `pages.json`, theme JSON) for routine report mutations when `pbir` can express the change.

## Active Connection Rule

Before any `pbir` command that inspects or mutates a local report:
1. identify the current real project folder and ignore the placeholder `[ProjectName]/`
2. point `pbir` to the report under `<ProjectName>/PBIP/<PbipBaseName>.Report`
3. clear or replace any stale active connection first

Recommended sequence:

```powershell
pbir connect --clear
pbir connect "<Report.Report>"
pbir connect
```

Notes:
- Treat `<ProjectName>` as a variable token, never as the literal bracketed placeholder folder name.
- If the project folder name contains PowerShell metacharacters such as `[` or `]`, use literal-path semantics for shell navigation, or connect with an explicit report path that escapes the brackets.
- If `pbir connect` shows a different base directory than the current project, stop and reconnect before running `pbir ls`, `pbir cat`, `pbir validate`, or any mutation command.

## Allowed Usage Pattern

Use `pbir` only when all of the following are true:
1. the target artifact is a **local PBIR report**
2. the command maps cleanly to the requested operation
3. the repository skill already defines the desired behavior
4. the CLI improves execution but does not replace validation or design reasoning

## Preferred Command Families

Safe read-mostly commands:
- `pbir ls`
- `pbir tree`
- `pbir find`
- `pbir model`
- `pbir get`
- `pbir cat`
- `pbir schema types`
- `pbir schema containers`
- `pbir schema describe`

Useful local mutation commands:
- `pbir add`
- `pbir pages`
- `pbir visuals`
- `pbir set`
- `pbir fields`
- `pbir filters`
- `pbir bookmarks`
- `pbir dax`
- `pbir theme`

Safety and lifecycle commands:
- `pbir backup`
- `pbir restore`
- `pbir validate`
- `pbir open`

## High-Risk Commands

The following commands require stronger guardrails and should be used only when the user explicitly asks for them or the active workflow clearly includes them:
- `pbir rm -f`
- `pbir report rebind`
- `pbir report convert`
- `pbir report merge`
- `pbir report split-pages`
- `pbir report split-from-thick`
- `pbir download`
- `pbir publish`
- `pbir batch run`

For these commands:
1. create a backup first when working locally
2. prefer preview/inspection modes where available
3. validate afterwards
4. stop if the command would broaden scope beyond the user request

## Fallback Rules

If `pbir` is unavailable, unsupported for the operation, or produces ambiguous output:
1. fall back to the repository's existing skill-guided file/template workflow
2. preserve blueprint-first and reference-first behavior
3. continue using repository validators and Microsoft documentation as the final authority
4. when fallback implies direct JSON edits on existing report artifacts, require explicit approval and include rationale in the task summary

If `pbir` fails with a missing Python dependency inside the uv-managed tool environment:
1. verify the tool path with `Get-Command pbir`
2. prefer reinstalling the tool with `uv tool install --reinstall pbir-cli`
3. if the error persists and the missing package is `pygments`, reinstall with `uv tool install --reinstall pbir-cli --with pygments`
4. re-run `pbir --version` and a safe read command such as `pbir connect` or `pbir ls` before resuming report work

If `pbir cat` still fails after the dependency fix while other commands such as `pbir ls` work:
1. treat it as a command-specific runtime bug in the current `pbir-cli` build
2. avoid blocking the workflow on `pbir cat`
3. prefer `pbir ls`, `pbir tree`, `pbir get`, repository validators, or direct file reads instead
4. keep `pbir cat` out of critical-path automation until the upstream tool fixes the packaged runtime

If `pbir` and repository references disagree:
1. prefer Microsoft official documentation when available
2. otherwise prefer repository-validated templates and guardrails
3. treat the CLI output as a hint to investigate, not a silent override

## Default Safety Loop

For local report edits, prefer this sequence:
1. inspect with `pbir tree` or `pbir ls -v`
2. back up with `pbir backup` before risky edits
3. mutate with the narrowest command possible
4. run `pbir validate`
5. run repository validator when the skill requires it (for report QA: `python .github/skills/report-quality-validation/scripts/validate_pbir_report.py <ProjectName>`)

## Schema Placement Guardrails (Desktop-Critical)

Always enforce these before Desktop open:
- `visualContainerObjects` inside `visual`.
- `drillFilterOtherVisuals` inside `visual`.
- visual filters in top-level `filterConfig.filters`, never `visual.filters`.

If any of these are violated, treat as blocking defect and fix before continuing.