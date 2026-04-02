# AI Coding Agent Instructions

## Purpose
This document defines operational rules for AI coding assistants (Copilot, ChatGPT, Cursor, etc.) working in this repository.

Goals:
- Reduce token consumption
- Maintain architectural consistency
- Keep security and compliance constraints explicit
- Accelerate safe feature development and bug fixing

---

# 1. Repository Architecture — Multi-Agent System

This repository uses a **multi-agent architecture** for Power BI development. Agents are domain-specific experts that can operate independently or be coordinated by an orchestrator.

## Agents

| Agent | Domain | When to Use |
|---|---|---|
| `delivery-lead` | E2E workflow orchestration | User requests a full project build from spec |
| `business-data-analyst` | Requirements analysis | Analyze specs, extract KPIs, dimensions, constraints |
| `pbi-semantic-model` | Semantic model (TMDL/DAX) | Design models, write TMDL, develop DAX measures |
| `data-generator` | Mock data generation | Generate CSV datasets from model schema |
| `pbi-qa` | Quality assurance | Validate models, run tests, review report quality |
| `pbi-report` | Report design & PBIR | Design layouts, generate PBIR visuals |

Agent definitions: `.github/agents/<agent-name>.agent.md`

## Skills

Skills are domain knowledge packages consumed by agents. Each skill is a self-contained folder:

```
.github/skills/<skill-name>/
├── SKILL.md              # Procedural knowledge with YAML frontmatter
├── references/           # Domain-specific reference documents
└── scripts/              # Domain-specific utility scripts
```

## Shared References

Cross-cutting references used by multiple agents live in `.github/references/`:
- `naming-conventions.md` — naming standards for all objects
- `pbip-folder-structure.md` — PBIP workspace folder layout
- `security-rls-best-practices.md` — Row-level security patterns

---

# 2. Global Response Rules

## Language
All generated code comments and docstrings must be in English.

## Chat Output Constraints
To reduce noise and token usage, AI assistants must:
- Avoid pasting full files
- Avoid large code blocks
- Prefer patch-style guidance
- Use minimal snippets (<= 20 lines) only when strictly necessary

Preferred format:
- File: `<path>`
- Section: `<logical area>`
- Change: `<what and why>`

## Secrets & Security
The AI must never output credentials, API keys, tokens, secrets, or connection strings.

Use placeholders only:
- `<TENANT_ID>`
- `<CLIENT_ID>`
- `<CLIENT_SECRET>`
- `<KEY_VAULT_NAME>`

## Human Review Rule
AI-generated output is advisory and must:
- Be reviewed by a human
- Pass repository CI/CD checks
- Never be deployed directly without validation

---

# 2. AI Implementation Playbook

Use this structure in implementation responses.
- 1 Scope: State in-scope and out-of-scope items.
- 2 Impacted Components: List affected files with full repository paths.
- 3 Change Description: Explain logic, responsibilities, and interactions.
- 4 Edge Cases: Always review data quality, null handling, performance, compatibility, and security.
- 5 Verification Plan: Propose unit/integration checks, pipeline validation, and data validation.

---

# 3. Development Fast-Track (Copilot)

For faster and safer delivery, ask Copilot with this minimal context:
- Goal: feature or bug objective
- Scope: allowed folders/files
- Constraints: security/performance/backward compatibility
- Validation: tests or commands to run

Recommended request template:
1. "Update `<file>` to `<goal>`"
2. "Keep changes minimal and aligned with existing patterns"
3. "Include edge-case handling for null/empty/error paths"
4. "Run targeted validation and summarize results"

---

# 4. Common Pitfalls to Avoid

- Hardcoding credentials, secrets, or environment values
- Bypassing metadata-driven configuration
- Producing large chat code dumps instead of patch-focused guidance
- Invoking the `delivery-lead` orchestrator for standalone domain tasks
- Writing TMDL, DAX, PBIR code without first reading the relevant skill and references
- Guessing PBIR JSON structures instead of using templates from `.github/skills/report-implementation/references/`
- Inventing column/measure names without reading TMDL files from disk

---

# 5. Expected AI Output Quality

A good AI response should:
- Reference repository paths clearly
- Respect architecture and security constraints
- Keep output concise and implementation-ready
- Surface assumptions and validation steps explicitly
- Preserve human decision authority