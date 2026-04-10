# Contributing

## Contribution Model

This repository uses a **fork-first** contribution model.

- Create a fork of the repository.
- Create a feature branch in your fork.
- Open a pull request back to the upstream repository.
- Do not expect direct push access to the upstream repository.

## Non-Overwrite Rules

To keep the agent system stable, contributors must not overwrite repository-native guidance wholesale.

- Do not replace `.github/agents`, `.github/skills`, `.github/prompts`, `.github/references`, or `.github/copilot-instructions.md` with generated scaffolds.
- Do not run external setup commands that mutate repository-owned agent assets. This includes `pbir setup` or similar bootstrap commands from third-party tools.
- Prefer targeted edits that preserve the existing architecture, naming, and workflow boundaries.
- If you need a materially different behavior model, implement it in your fork first and propose a scoped pull request.

## Change Expectations

- Keep changes minimal and aligned with existing patterns.
- Preserve attribution and notice files.
- Do not commit secrets, credentials, tenant-specific identifiers, local paths, or generated local state.
- Update documentation when behavior, folder structure, or workflow changes.

## Pull Request Checklist

- The change is scoped and explained clearly.
- Repository docs remain accurate.
- New local or generated artifacts are not committed.
- Existing agent and skill boundaries are preserved.
- Third-party notices remain accurate when adapted material is touched.

## Review Notes

Maintainers may reject pull requests that:

- bypass the fork-first model
- introduce secrets or organization-specific data
- replace curated repository guidance with opaque generated output
- broaden scope far beyond the stated change