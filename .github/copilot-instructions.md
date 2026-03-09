# Global Copilot Instructions — AI Semantic Layer Builder

This repo hosts a GitHub Copilot Custom Agent (`@semantic-modeler`) that builds **Power BI semantic models** in **PBIP + TMDL** from functional specifications.

## MUST / MUST NOT (highest priority)

### Safety / Governance
- MUST refuse requests that: expose secrets/credentials; bypass security controls; disable auditing/logging; weaken authentication/authorization.
- MUST use placeholders for sensitive values (examples: `<<TENANT_ID>>`, `<<WORKSPACE_NAME>>`, `<<SQL_SERVER>>`, `<<API_TOKEN>>`).

### Hallucination control
- MUST NOT invent repository files, table/column/measure names, or Power BI/TMDL syntax.
- MUST ground model syntax in one of:
  - `.github/references/*` (local ground truth), or
  - Microsoft official docs via MCP tools (`microsoft_docs_search` / `microsoft_docs_fetch`).
- If required info is missing/ambiguous: ask targeted questions and STOP.

### Workflow control (approval gates)
- MUST follow the 8-step workflow defined in `.github/skills/`.
- MUST STOP after every step and wait for explicit user approval (e.g., “Proceed”, “Approved”, “OK”) before moving to the next step.

Note: The approval-gated workflow refers to **Steps 1–8**. Preliminary checks/bootstrap (e.g., Skill 00 project initialization) may run automatically before Step 1.

### Project isolation
- MUST keep artifacts isolated per `<ProjectName>/` and MUST NOT mix objects, data, or tests across projects.

## Language policy

- Conversation language: follow the user.
- Generated artifacts MUST be in English (TMDL, DAX, M, scripts, file names, table/column/measure names).
- Descriptions inside TMDL: may follow user language if explicitly requested in the spec.

## Non-negotiable modeling & TMDL rules

- MUST model as **Kimball Star Schema** (facts at center, dimensions around).
- MUST follow naming rules in `.github/references/naming-conventions.md`.
- TMDL formatting:
  - MUST use **TAB indentation** (not spaces).
  - MUST NOT include comments of any kind in TMDL (no `//`, `/* */`, `///`, `<!-- -->`).
  - If comments exist, use `.github/scripts/remove_tmdl_comments.py <ProjectName>`.
- Lineage tags:
  - After generating/updating TMDL, MUST run `.github/scripts/fix_lineage_tags.py <ProjectName>` to ensure globally-unique UUID v4 `lineageTag` values.
- Relationships:
  - Default `securityFilteringBehavior` to `oneDirection` unless an explicit RLS requirement exists.
  - MUST prevent ambiguous paths: between any two tables there must be exactly one active relationship path.
- Compatibility:
  - MUST verify `compatibilityLevel` and other model-level settings against `.github/skills/03-physical-model-tmdl.md` and the user’s Power BI Desktop version.
- Fact table columns:
  - MUST set `summarizeBy: none` to force explicit DAX measures (BPA rule).
- Time intelligence with dynamic parameters:
  - MUST NOT use time-intel functions that require constant year-end parameters when inputs are dynamic (see `.github/skills/04-dax-development.md`).
- Functional testing:
  - MUST introspect the model from TMDL before writing tests/queries (never guess object names).

## Project prerequisites (minimal)

- Python 3.10+ is required for mock data generation and tests.
- Use the repo-level virtual environment:
  - `python -m venv .venv`
  - `.\.venv\Scripts\Activate.ps1`
  - `pip install -r requirements.txt`
- Each project MUST have a PBIP scaffold present:
  - `<ProjectName>/PBIP/<ProjectName>.pbip`
  - `<ProjectName>/PBIP/<ProjectName>.Report/definition.pbir`
  - `<ProjectName>/PBIP/<ProjectName>.SemanticModel/definition.pbism`
  - `<ProjectName>/PBIP/<ProjectName>.SemanticModel/definition/`

If the PBIP scaffold is missing, the agent can bootstrap it via `.github/skills/00-project-initialization.md`.
Power BI Desktop is still used later to open the project, configure data sources, refresh, and visually validate.

## Where to look (do not duplicate content)

- Agent definition: `.github/agents/semanti-modeler.agent.md`
- Step-by-step execution: `.github/skills/01-requirements-analysis.md` … `.github/skills/08-report-design.md`
- Reference ground truth:
  - `.github/references/tmdl-syntax-reference.md`
  - `.github/references/relationship-patterns.md`
  - `.github/references/dax-patterns.md`
  - `.github/references/dax-optimization-framework.md`
  - `.github/references/bpa-rules-reference.md`
  - `.github/references/report-design-visualization-best-practices.md`

## Response format (when implementing changes)

Every response that proposes or applies changes MUST include:
1) Scope (what is / is not changing)
2) Files touched (paths)
3) Verification (commands or checks)
4) Open questions / assumptions (if any)

## Output limits

- MUST NOT dump full files unless explicitly requested.
- Prefer small, reviewable diffs and point to the exact file location for details.

