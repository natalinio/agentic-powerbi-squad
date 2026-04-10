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
5. still complete repository-specific validation when the skill requires it