# Agentic Power BI Squad

> **Build complete Power BI projects — semantic models (TMDL) and reports (PBIR) — from functional specifications using a multi-agent system powered by GitHub Copilot.**

[![Power BI](https://img.shields.io/badge/Power%20BI-PBIP%20Format-yellow)](https://powerbi.microsoft.com)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)

---

## What Is This?

**Agentic Power BI Squad** is a **multi-agent system** for Power BI development that runs inside VS Code with GitHub Copilot. Instead of a single monolithic agent, it uses a team of **6 domain-specific agents** coordinated by an orchestrator, each backed by **16 modular skills** containing procedural knowledge, reference materials, and examples.

![Agent squad Power BI Architecture](.github/docs/architecture.png)

You provide a functional specification in Markdown. The squad produces:

- **Dimensional data model** (Kimball Star Schema) with TMDL files
- **Optimized DAX measures** (time intelligence, KPIs, variances)
- **Mock CSV datasets** for local development
- **Automated functional tests** with pass/fail reports
- **Report blueprint** (design system, page layouts, visual specs)
- **PBIR report files** (pages, visuals, slicers) ready for Power BI Desktop
- **Custom visuals** via SVG inline graphics, HTML custom visual (full-frame), and Deneb (Vega/Vega-Lite)
- **Report themes** with full formatting hierarchy
- **Quality validation** at every step

The output is a complete **PBIP project** that opens directly in Power BI Desktop.

### Two Ways to Work

The squad supports **two operating modes**:

| Mode | How it works | When to use |
|---|---|---|
| **Workflow Mode** | The `delivery-lead` orchestrator coordinates all 6 agents through a structured 7-phase workflow with approval gates at each phase | Building a complete project from a specification end-to-end |
| **Standalone Mode** | Invoke any agent directly (e.g., `@pbi-semantic-model`, `@pbi-report`, `@pbi-qa`) for a specific task | Adding a measure, creating a visual, running tests, or any targeted change |

Both modes share the same agents, skills, and project structure — the difference is whether you want full orchestration or direct control.

### Installation Options

| Method | When to use |
|--------|-------------|
| **CLI** (recommended) | Install agents and skills into your workspace from the terminal — no fork or clone required |
| **Fork / Clone** | For contributors who want to modify the agent system itself |

#### Option 1: CLI (npx)

```bash
# Install everything
npx pbi-agent-squad install --all

# Install only specific agents (dependencies auto-resolved)
npx pbi-agent-squad install --agent pbi-report --agent pbi-qa

# Install only specific skills
npx pbi-agent-squad install --skill dax-development --skill svg-visuals

# Install all agents (with their skill dependencies)
npx pbi-agent-squad install --agents

# List available components
npx pbi-agent-squad list

# Check what's installed
npx pbi-agent-squad status

# Update installed components
npx pbi-agent-squad update --all

# Uninstall a component
npx pbi-agent-squad uninstall skill:dax-development
```

The CLI copies components into your workspace's `.github/` folder. GitHub Copilot automatically discovers the installed agents and skills.

A lock file (`.github/.pbi-agent-squad.lock.json`) tracks installed components. User-modified files are never overwritten unless you pass `--force`.

#### Option 2: Fork (for contributors)

- Use a **fork** for experimentation, adaptation, and contributions
- Submit changes back through **pull requests**
- Do **not** use external setup tools or generated scaffolds to overwrite the repository-native `.github/agents`, `.github/skills`, `.github/prompts`, or instruction files
- Review [LICENSE](LICENSE), [CONTRIBUTING.md](CONTRIBUTING.md), and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) before reusing adapted material outside your fork

---

## Architecture

### Agents Squad

| Agent | Domain | Description |
|---|---|---|
| `delivery-lead` | Orchestration | End-to-end workflow management, phase transitions, user approvals |
| `business-data-analyst` | Requirements | Analyzes specs, extracts KPIs, dimensions, grain, constraints |
| `pbi-semantic-model` | Semantic Model | Designs logical models, writes TMDL, develops DAX measures |
| `data-generator` | Mock Data | Generates realistic CSV datasets from model schema |
| `pbi-report` | Report Design & Implementation | Designs layouts, generates PBIR visuals, SVG graphics, Deneb charts, themes |
| `pbi-qa` | Quality Assurance | Validates models (BPA), runs tests, reviews reports, checks SVG/Deneb/design quality |

### Skills (16)

Skills are self-contained knowledge packages consumed by agents. Each skill has procedural instructions (`SKILL.md`), reference files, and examples.

| Skill | Agent(s) | Purpose |
|---|---|---|
| `requirements-analysis` | business-data-analyst | Extract KPIs, dimensions, grain from specs |
| `logical-model` | pbi-semantic-model | Star schema design, ER diagrams |
| `physical-model-tmdl` | pbi-semantic-model | Generate TMDL files from logical model |
| `dax-development` | pbi-semantic-model | DAX measure authoring with patterns and pitfalls |
| `mock-data-generation` | data-generator | CSV dataset generation with referential integrity |
| `report-design` | pbi-report | Layout, storytelling, chart selection, design system |
| `report-implementation` | pbi-report | PBIR JSON generation from blueprint |
| `svg-visuals` | pbi-report | Inline SVG micro-charts via DAX (sparklines, bars, KPI indicators) in table/matrix/card visuals |
| `html-visuals` | pbi-report | Full-frame HTML and SVG visuals via DAX for the `htmlContent` custom visual (trend charts, comparison tables, narrative panels) |
| `deneb-visuals` | pbi-report | Vega/Vega-Lite custom charts with PBIR integration |
| `theme-customization` | pbi-report | Theme authoring, formatting hierarchy, visual-type overrides |
| `code-review` | pbi-qa | TMDL quality, BPA compliance, naming conventions |
| `functional-testing` | pbi-qa | Automated DAX measure testing against expected values |
| `report-quality-validation` | pbi-qa | PBIR validation, SVG/Deneb review, design quality checks |
| `project-initialization` | delivery-lead | PBIP project scaffolding |
| `workflow-orchestration` | delivery-lead | Phase management, state tracking, decision ledger |

### Shared References

Cross-cutting references in `.github/references/`:
- `naming-conventions.md` — naming standards for all objects
- `pbip-folder-structure.md` — PBIP workspace folder layout
- `security-rls-best-practices.md` — Row-level security patterns

---

## How to Use

### Prerequisites

- **VS Code** with **GitHub Copilot** (Chat + Agents enabled)
- **Power BI Desktop** (December 2025+ for PBIR support)
- **Python 3.10+** (for mock data generation and test execution)

```bash
pip install -r requirements.txt
```

#### Optional: `pbir-cli`

The local `pbir` CLI enhances report mutation workflows (faster visual/page operations, built-in validation). It is **not required** — all agents fall back to skill-guided file editing when the CLI is unavailable.

To install (optional):
```bash
uv tool install pbir-cli
```

When `pbir` is detected, agents prefer it for report mutations and validation. When absent, they work normally via direct JSON editing.

### Two Operating Modes

#### 1. Workflow Mode (Full Project)

Use the `delivery-lead` agent to build a complete project from a specification.

```
@delivery-lead Build a Power BI project from spec/sample_spec.md
```

The orchestrator coordinates all agents through a 7-phase workflow:

| Phase | Agent | Action |
|---|---|---|
| 1 | delivery-lead | Initialize the real project folder and PBIP scaffold |
| 2 | business-data-analyst | Analyze specification, extract KPIs, grain, constraints, and clarifications |
| 3 | pbi-semantic-model | Develop the semantic model: logical design, TMDL, and DAX measures |
| 4 | data-generator | Generate mock CSV datasets and align local partitions |
| 5 | pbi-qa | Run model QA: code review, BPA checks, and functional tests |
| 6 | pbi-report | Design the report blueprint and implement PBIR artifacts |
| 7 | pbi-qa | Validate report quality and report/render consistency |

Each step has **mandatory approval gates** — the orchestrator presents results and waits for your approval before proceeding.

Within a phase, the orchestrator may coordinate multiple specialist activities, but workflow progression is tracked at the phase level in `workflow_state.json`.

### Report Mutation Policy

For modifications to an existing PBIR report, the repository now follows a **CLI-first mutation path**:

- prefer the local `pbir` CLI for visual, page, and theme mutations when the command surface supports the requested change
- do not hand-edit `visual.json`, `page.json`, `pages.json`, or theme JSON for routine report mutations
- allow direct JSON edits only for documented CLI capability gaps, followed by dual validation
- close report work only after both `pbir validate --all` and the repository report validator succeed

#### 2. Standalone Mode (Individual Tasks)

Invoke any agent directly for specific tasks:

```
@pbi-semantic-model Add a YTD measure for Sales Amount to the SalesOverview project

@pbi-report Add a clustered bar chart showing Sales by Area to Page 1

@pbi-report Create a Deneb heatmap for monthly sales by region

@pbi-report Create an SVG sparkline measure for revenue trend

@pbi-report Create an HTML custom visual with a YoY trend chart comparing current vs previous year

@pbi-report Create an HTML narrative panel showing top/worst performers

@pbi-report Create a custom theme with blue/orange palette and enterprise formatting

@pbi-qa Validate the PBIR report structure for SalesOverview

@pbi-qa Review SVG measures for correctness

@data-generator Generate mock data for the SalesOverview semantic model
```

Each agent automatically discovers the project context (TMDL files, existing visuals, blueprint) before acting.

---

## Project Structure

```
<ProjectName>/
├── spec/                          # Specifications and blueprints
│   ├── spec_<name>.md             # Functional specification (input)
│   ├── requirements_summary.md    # Extracted requirements
│   ├── er_diagram.md              # Logical model diagram
│   └── report_blueprint.json      # Report design blueprint
├── data/                          # Mock CSV datasets
├── PBIP/                          # Power BI Project (PBIP format)
│   ├── <Name>.pbip                # Project entry point
│   ├── <Name>.SemanticModel/
│   │   └── definition/
│   │       ├── model.tmdl
│   │       ├── relationships.tmdl
│   │       ├── expressions.tmdl
│   │       └── tables/            # One .tmdl per table
│   └── <Name>.Report/
│       └── definition/
│           ├── report.json
│           ├── reportExtensions.json  # Extension measures
│           ├── pages/
│           │   ├── pages.json
│           │   └── <pageId>/
│           │       ├── page.json
│           │       └── visuals/
│           │           └── <visualId>/
│           │               └── visual.json
│           └── StaticResources/
│               └── SharedResources/
│                   └── BaseThemes/    # Report themes
├── tests/                         # Test definitions and results
├── scripts/                       # Data generation scripts
└── workflow_state.json            # Orchestrator state (workflow mode)
```

---

## Workflow Observability

The agentic workflow is observable through a combination of repository artifacts and local VS Code session logs.

### Repository-Native Sources

- `<ProjectName>/workflow_state.json` is the authoritative workflow state for orchestrated runs. It records current phase, approvals, decisions, assigned agent, and key artifacts.
- `<ProjectName>/spec/`, `<ProjectName>/tests/`, `<ProjectName>/data/`, and `<ProjectName>/PBIP/` provide the artifact trail of what each specialist produced.
- `agent_session_state.json`, when present, is only for standalone specialist continuity. It is not the source of truth for end-to-end workflow progression.

### Local VS Code Session Sources

- VS Code Copilot transcripts under the local `workspaceStorage/.../GitHub.copilot-chat/transcripts/` folder show user prompts, assistant messages, and tool execution events.
- `chat-session-resources/` stores captured tool outputs referenced by the transcript.
- These local files are useful for reconstructing the coordinator's execution flow during a session.

### Current Limits

- The current setup does not provide first-class per-sub-agent telemetry with dedicated start/stop events, token usage, or cost accounting for each delegated worker.
- In practice, structured understanding of the workflow comes from combining `workflow_state.json`, produced artifacts, and the local session transcript.
- If deeper observability is needed, add a repository-level execution log for delegated tasks rather than relying only on editor-local debug traces.

---

## Getting Started

### Quick Start (CLI)

1. **Install the toolkit** into your target workspace:
   ```bash
   npx pbi-agent-squad install --all
   ```
2. **Install Python dependencies** (for data generation and testing):
   ```bash
   pip install -r .github/skills/functional-testing/scripts/requirements.txt
   ```
3. **Open VS Code** with GitHub Copilot enabled on your Power BI project
4. **Start with a specification** — use `[ProjectName]/spec/specification_template.md` as the template
5. **Choose your mode**:
   - **Full project**: `@delivery-lead Build from spec/my_spec.md`
   - **Single task**: `@pbi-semantic-model Create a logical model for <requirements>`
6. **Open the result** in Power BI Desktop: open the `.pbip` file from the `PBIP/` folder

### Getting Started (Contributors / Fork)

1. **Fork the repository** on GitHub.

2. **Clone your fork**:
   ```bash
   git clone <your-fork-url>
   cd agentic-powerbi-development
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Open in VS Code** with GitHub Copilot enabled.

5. **Start with a specification** — use `spec/specification_template.md` as the template and `spec/sample_spec.md` as a worked example.

6. **Choose your mode**:
   - **Full project**: `@delivery-lead Build from spec/sample_spec.md`
   - **Single task**: `@pbi-semantic-model Create a logical model for <requirements>`

7. **Open the result** in Power BI Desktop: open the `.pbip` file from the `PBIP/` folder.

---

## Reference Assets

The repository includes reusable templates only. Use these assets as the starting point:

- `[ProjectName]/` for expected project folder layout
- `spec/specification_template.md` for the empty specification template
- `spec/sample_spec.md` for a completed example specification

Generated semantic model, report, data, and test artifacts are created when you run the workflow or the specialist agents against your own project folder.

For local-only experiments, client prototypes, and generated project artifacts that must not be published, keep them under ignored folders such as `_local/`, `local-experiments/`, or `sandbox/`.

---

## Attribution

This repository includes original material plus adapted domain knowledge derived from the **[Goblin Power BI Agentic Development](https://github.com/data-goblins)** project by Data Goblins. The most relevant adapted areas are documented in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

If you reuse or adapt material influenced by that project, preserve attribution and review the upstream reuse terms before distributing it outside a fork-based workflow.

**Original project**: [https://github.com/data-goblins](https://github.com/data-goblins)

---

---

## Custom Visual Deployment Note

The `html-visuals` skill and the `deneb-visuals` skill produce visuals that require the Power BI HTML custom visual or Deneb custom visual. When publishing to **Power BI Service**, a tenant admin must enable custom visuals:

> **Admin portal → Tenant settings → Custom visuals → Allow visuals created using the Power BI SDK**

Without this setting, custom visuals render as blank tiles in the cloud. The `pbi-report` agent will remind you of this after completing any HTML or Deneb visual task.

---

## Contributing

This repository accepts changes through a **fork + pull request** flow only. See [CONTRIBUTING.md](CONTRIBUTING.md) for the contribution model and non-overwrite rules.

## Security

See [SECURITY.md](SECURITY.md) for vulnerability reporting and secret-handling guidance.

## Code of Conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for participation expectations.

## License

Repository use is governed by the fork-first terms in [LICENSE](LICENSE). Third-party attribution and additional reuse notes are documented in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
