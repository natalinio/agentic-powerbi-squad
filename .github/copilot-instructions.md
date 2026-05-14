# AI Coding Agent Instructions

## Purpose

This document defines how AI coding agents should operate in this repository.

It has two goals:

1. Provide a clear overview of the project structure and repository operating model.
2. Define response and implementation rules for safe, efficient, and effective agentic development.

These instructions apply to AI assistants working in this repository, including Copilot, ChatGPT, Cursor, and similar tools.

---

## 1. Repository Overview

### 1.1 Project Model

This repository uses a multi-agent architecture for Power BI solution development.

Agents are domain specialists that can work:
- independently on focused tasks
- or under orchestration for end-to-end delivery workflows

The repository is organized so that:
- agents define role-specific behavior
- skills provide reusable domain knowledge
- shared references capture cross-cutting conventions and standards

### 1.2 Agents

| Agent | Domain | When to Use |
|---|---|---|
| `delivery-lead` | End-to-end workflow orchestration | When the user requests a full project build or multi-step coordinated delivery |
| `business-data-analyst` | Requirements and KPI analysis | When extracting KPIs, dimensions, business rules, and analytical requirements |
| `pbi-semantic-model` | Semantic model design (TMDL/DAX) | When designing models, authoring TMDL, and creating DAX measures |
| `data-generator` | Mock data generation | When generating CSV datasets or sample data from a model schema |
| `pbi-qa` | Quality assurance | When validating models, testing outputs, and reviewing report quality |
| `pbi-report` | Report design and PBIR implementation | When designing layouts and generating PBIR pages and visuals |

Agent definitions live in:

``
.github/agents/<agent-name>.agent.md
``

### 1.3 Skills

Skills are domain knowledge packages consumed by agents. Each skill is a self-contained folder:

```text
.github/skills/<skill-name>/
├── SKILL.md              # Procedural knowledge with YAML frontmatter
├── references/           # Domain-specific reference documents
└── scripts/              # Domain-specific utility scripts
```

| Skill | Domain | Purpose |
|---|---|---|
| `report-design` | Report design | Storyboard layout, UX, information architecture, and blueprint generation |
| `report-implementation` | Report implementation | Generate PBIR page and visual JSON files from blueprint specifications |
| `svg-visuals` | Report visuals | Inline SVG micro-charts via DAX measures for tables, matrices, image visuals, and compact layouts |
| `html-visuals` | Report visuals | Full-frame HTML and SVG generated via DAX measures for the `htmlContent` custom visual |
| `deneb-visuals` | Report visuals | Vega and Vega-Lite chart specifications for Deneb custom visuals |
| `theme-customization` | Report themes | Create, modify, and validate Power BI report themes |

### 1.4 Shared References

Cross-cutting references used by multiple agents live in:

``
.github/references/
``

Current shared references include:
- `naming-conventions.md` — naming standards for semantic model and report objects
- `pbip-folder-structure.md` — PBIP workspace layout and folder conventions
- `security-rls-best-practices.md` — row-level security guidance and patterns

### 1.5 Repository Operating Assumption

Agents must treat repository files as the source of truth.

Do not assume:
- model object names
- measure names
- table names
- PBIR structures
- TMDL aliases
- report wiring details
- custom visual bindings

Always read the relevant files, skills, and references before proposing or generating changes.

---

## 2. Core Working Principles for AI Agents

When working in this repository, AI agents must follow these principles.

### 2.1 Read Before Writing

Before proposing or generating implementation changes:
1. identify the relevant agent
2. read the relevant skill documentation
3. read repository references related to the task
4. inspect the actual files to be changed

Do not generate TMDL, DAX, PBIR, theme JSON, or report wiring based only on assumptions or generic patterns.

### 2.2 Prefer Existing Patterns Over Invention

Use the repository’s existing conventions, structures, naming, and implementation patterns.

Prefer:
- existing folder structures
- existing JSON shapes
- existing TMDL conventions
- existing DAX naming style
- existing report composition patterns
- existing visual templates and references

Avoid introducing new patterns unless the task explicitly requires them.

### 2.3 Make Minimal, Targeted Changes

Keep changes narrow and intentional.

Prefer:
- small diffs
- local changes
- minimal surface area
- compatibility with existing structure

Avoid broad rewrites unless explicitly requested.

### 2.4 State Assumptions Explicitly

If something is missing, ambiguous, or inferred, say so clearly.

Examples:
- missing file path
- uncertain visual binding
- absent measure definition
- unclear naming convention
- incomplete business rule

Do not hide uncertainty behind confident wording.

### 2.5 Validate Before Declaring Completion

Before presenting work as complete, verify:
- impacted files are correctly identified
- implementation matches repository patterns
- edge cases were considered
- validation steps are proposed or executed where possible

Completion claims must be evidence-based.

---

## 3. Safety and Governance Rules

### 3.1 Secrets and Sensitive Data

Never output:
- credentials
- API keys
- access tokens
- client secrets
- connection strings
- tenant-specific secrets
- private endpoints not already intentionally documented in the repository

Use placeholders when needed:
- `<TENANT_ID>`
- `<CLIENT_ID>`
- `<CLIENT_SECRET>`
- `<KEY_VAULT_NAME>`

### 3.2 Human Review Is Mandatory

AI-generated output is advisory.

All generated changes must:
- be reviewed by a human
- be validated against repository expectations
- pass relevant checks before being considered complete
- never be treated as production-ready without verification

### 3.3 Safe Delivery Rule

Do not imply that generated output is safe to deploy without validation.

Always preserve:
- human decision authority
- review checkpoints
- explicit validation expectations

---

## 4. Response Style for Agentic Development

Responses should be concise, implementation-ready, and grounded in repository evidence.

### 4.1 Preferred Response Structure

For implementation-oriented responses, use this structure when relevant:

1. Scope  
   State what is in scope and out of scope.

2. Impacted Components  
   List affected files using full repository paths.

3. Change Description  
   Explain what changes are needed and why.

4. Edge Cases  
   Review null handling, empty states, compatibility, performance, and security where relevant.

5. Verification Plan  
   Propose targeted checks, validations, or review steps.

### 4.2 Output Constraints

To reduce noise and token usage:
- avoid pasting full files unless explicitly requested
- avoid large code dumps
- prefer patch-oriented guidance
- use short snippets only when necessary
- reference repository paths clearly

Preferred concise format:
- File: `<path>`
- Change: `<what changes>`
- Why: `<reason>`
- Validation: `<how to verify>`

### 4.3 Quality Standard for Good Responses

A good response in this repository should:
- reference real repository paths
- align with the multi-agent architecture
- respect security and governance constraints
- stay concise and actionable
- surface assumptions explicitly
- propose verification steps
- avoid fabricated implementation details

---

## 5. Repository-Specific Guardrails

These rules are especially important in this repository.

### 5.1 Power BI Implementation Guardrails

Do not:
- guess PBIR JSON structures
- invent visual container wiring
- invent report section or visual identifiers
- invent TMDL aliases
- invent column or measure names
- infer semantic model relationships without reading model files

Always inspect repository files first.

### 5.2 Skill-First Rule for Specialized Work

Before performing specialized work, read the relevant skill and supporting references.

Examples:
- report layout and blueprint work -> read `report-design`
- PBIR page or visual generation -> read `report-implementation`
- inline SVG micro-charts -> read `svg-visuals`
- full-frame HTML/SVG for custom visual tiles -> read `html-visuals`
- Deneb chart authoring -> read `deneb-visuals`
- theme work -> read `theme-customization`

### 5.3 Tooling Boundary Rule

Do not:
- install external PBIR agent plugins into this repository
- treat external tools as the source of truth for repository design
- use generated assumptions in place of repository files and references

If `pbir` is used, treat it only as an optional command backend, not as a source of agent or skill definitions.

### 5.4 Orchestrator Boundary Rule

Do not invoke `delivery-lead` for narrowly scoped specialist work.

Use `delivery-lead` only when:
- the task is end-to-end
- multiple specialist agents must be coordinated
- workflow state management is required

Use specialist agents directly for focused domain tasks.

---

## 6. Orchestration and State Management

This repository supports two different persistence models.

### 6.1 Workflow State

`workflow_state.json` is reserved for end-to-end workflows orchestrated by `delivery-lead`.

Rules:
- only `delivery-lead` may update `workflow_state.json`
- specialist agents must not write to `workflow_state.json` directly

### 6.2 Specialist Session State

`agent_session_state.json` is optional and may be used for direct specialist-agent continuity when it materially improves correctness or resumability.

Rules:
- use it only in standalone specialist mode
- keep it compact
- store only currently relevant continuity information
- do not use append-only logs as the default continuity mechanism
- limit persisted history to open items plus the most recent relevant standalone tasks

---

## 7. Operational Model Routing

This repository assigns models per agent instead of relying on one shared default model.

### 7.1 Current Agent Model Assignments

- `delivery-lead` -> `claude-sonnet-4.6`
- `business-data-analyst` -> `claude-sonnet-4.6`
- `pbi-semantic-model` -> `claude-sonnet-4.6`
- `pbi-report` -> `claude-sonnet-4.6`
- `pbi-qa` -> `claude-sonnet-4.6`
- `data-generator` -> `claude-haiku-4.5`

### 7.2 Routing Guidance

- agent-level `model` in `.github/agents/*.agent.md` is the preferred control point
- use only models supported by the active client and enabled by organization or enterprise policy
- if a configured model becomes unavailable, replace it with the nearest supported model in the same family rather than removing the `model` property

### 7.3 Fallback Guidance

- orchestration and deep-analysis agents should default to `claude-sonnet-4.6`
- code-centric implementation and review agents should fall back first to `claude-sonnet-4.6`
- lightweight executor agents should fall back first to `claude-haiku-4.5`
- if future client support enables stronger repository-approved coding models, prefer the latest approved equivalent in the same operational role

---

## 8. Minimal Prompting Template for Fast Tasking

For faster and safer delivery, user requests to AI agents should include:

- Goal: the feature, fix, or deliverable
- Scope: allowed files, folders, or components
- Constraints: security, compatibility, performance, or style requirements
- Validation: tests, checks, or acceptance criteria

Recommended compact tasking template:
1. Update `<file or area>` to achieve `<goal>`.
2. Keep changes minimal and aligned with existing repository patterns.
3. Handle null, empty, and error paths where relevant.
4. Propose or run targeted validation and summarize the result.