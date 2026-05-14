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

| Skill | Domain | Purpose |
|---|---|---|
| `report-design` | Report design | Storyboard layout, UX, information architecture, and blueprint generation |
| `report-implementation` | Report implementation | Generate PBIR page/visual JSON files from blueprint |
| `svg-visuals` | Report visuals | Inline SVG micro-charts via DAX measures for tables, matrices, and image visuals |
| `html-visuals` | Report visuals | Full-frame HTML/SVG via DAX measures for htmlContent custom visual |
| `deneb-visuals` | Report visuals | Vega / Vega-Lite custom charts embedded in Deneb visuals |
| `theme-customization` | Report themes | Create, modify, and validate Power BI report themes |

## Shared References

Cross-cutting references used by multiple agents live in `.github/references/`:
- `naming-conventions.md` — naming standards for all objects
- `pbip-folder-structure.md` — PBIP workspace folder layout
- `security-rls-best-practices.md` — Row-level security patterns

## Persistence Model

This repository uses two distinct persistence models:

- `workflow_state.json` — used only for end-to-end workflows orchestrated by `delivery-lead`
- `agent_session_state.json` — optional compact continuity state for direct standalone specialist-agent tasks

Rules:

- `delivery-lead` is the only owner allowed to update `workflow_state.json`
- specialist agents must not write `workflow_state.json` directly
- specialist agents may read or write `agent_session_state.json` only in standalone mode and only when continuity materially improves correctness or resumability
- `agent_session_state.json` must remain compact: open items plus the last 10 relevant persisted standalone tasks
- append-only logs are not the default working-memory format for standalone continuity

## Agent Model Assignment

This repository assigns AI models per agent instead of relying on one shared default model.

Rules:

- agent-level `model` in `.github/agents/*.agent.md` is the preferred control point for model routing
- use only model identifiers supported by the active client and enabled by the organization or enterprise policy
- if a configured model is no longer available in the tenant, replace it with the nearest model in the same family rather than removing the `model` property

Current assignments:

- `delivery-lead` -> `claude-sonnet-4.6`
- `business-data-analyst` -> `claude-sonnet-4.6`
- `pbi-semantic-model` -> `claude-sonnet-4.6`
- `pbi-report` -> `claude-sonnet-4.6`
- `pbi-qa` -> `claude-sonnet-4.6`
- `data-generator` -> `claude-haiku-4.5`

Fallback guidance:

- orchestration and deep analysis agents should use `claude-sonnet-4.6` by default in this repository; if a future client release recognizes `claude-opus-*`, prefer that family for `delivery-lead`
- code-centric implementation or review agents should fall back first to `claude-sonnet-4.6`; if the client later recognizes OpenAI coding models, prefer the latest enabled `*-codex` model
- lightweight executor agents should fall back first to `claude-haiku-4.5`

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
- Running `pbir setup` or installing external PBIR agent plugins into this repository; use `pbir` only as an optional command backend, never as a source of agent/skill definitions

---

# 5. Expected AI Output Quality

A good AI response should:
- Reference repository paths clearly
- Respect architecture and security constraints
- Keep output concise and implementation-ready
- Surface assumptions and validation steps explicitly
- Preserve human decision authority