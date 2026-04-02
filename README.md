# Agentic Power BI Squad

> **Build complete Power BI projects — semantic models (TMDL) and reports (PBIR) — from functional specifications using a multi-agent system powered by GitHub Copilot.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Power BI](https://img.shields.io/badge/Power%20BI-PBIP%20Format-yellow)](https://powerbi.microsoft.com)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)

---

## What Is This?

**Agentic Power BI Squad** is a **multi-agent system** for Power BI development that runs inside VS Code with GitHub Copilot. Instead of a single monolithic agent, it uses a team of **6 domain-specific agents** coordinated by an orchestrator, each backed by **15 modular skills** containing procedural knowledge, reference materials, and examples.

You provide a functional specification in Markdown. The squad produces:

- **Dimensional data model** (Kimball Star Schema) with TMDL files
- **Optimized DAX measures** (time intelligence, KPIs, variances)
- **Mock CSV datasets** for local development
- **Automated functional tests** with pass/fail reports
- **Report blueprint** (design system, page layouts, visual specs)
- **PBIR report files** (pages, visuals, slicers) ready for Power BI Desktop
- **Custom visuals** via SVG inline graphics and Deneb (Vega/Vega-Lite)
- **Report themes** with full formatting hierarchy
- **Quality validation** at every step

The output is a complete **PBIP project** that opens directly in Power BI Desktop.

---

## Architecture

### Agents

| Agent | Domain | Description |
|---|---|---|
| `delivery-lead` | Orchestration | End-to-end workflow management, phase transitions, user approvals |
| `business-data-analyst` | Requirements | Analyzes specs, extracts KPIs, dimensions, grain, constraints |
| `pbi-semantic-model` | Semantic Model | Designs logical models, writes TMDL, develops DAX measures |
| `data-generator` | Mock Data | Generates realistic CSV datasets from model schema |
| `pbi-report` | Report Design & Implementation | Designs layouts, generates PBIR visuals, SVG graphics, Deneb charts, themes |
| `pbi-qa` | Quality Assurance | Validates models (BPA), runs tests, reviews reports, checks SVG/Deneb/design quality |

### Skills (15)

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
| `svg-visuals` | pbi-report | Inline SVG graphics via DAX (sparklines, bars, KPI indicators) |
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

### Two Operating Modes

#### 1. Workflow Mode (Full Project)

Use the `delivery-lead` agent to build a complete project from a specification.

```
@delivery-lead Build a Power BI project from spec/sample_spec.md
```

The orchestrator coordinates all agents through a 10-step workflow:

| Step | Agent | Action |
|---|---|---|
| 00 | delivery-lead | Bootstrap PBIP project structure |
| 01 | business-data-analyst | Analyze specification, extract requirements |
| 02 | pbi-semantic-model | Design logical model (star schema, ER diagram) |
| 03 | pbi-semantic-model | Generate TMDL physical model |
| 04 | pbi-semantic-model | Develop DAX measures |
| 05 | data-generator | Generate mock CSV datasets |
| 06 | pbi-qa | Code review + BPA compliance |
| 07 | pbi-qa | Run functional tests |
| 08 | pbi-report | Design report blueprint |
| 09 | pbi-report | Implement PBIR visuals |
| 10 | pbi-qa | Validate report quality |

Each step has **mandatory approval gates** — the orchestrator presents results and waits for your approval before proceeding.

#### 2. Standalone Mode (Individual Tasks)

Invoke any agent directly for specific tasks:

```
@pbi-semantic-model Add a YTD measure for Sales Amount to the SalesOverview project

@pbi-report Add a clustered bar chart showing Sales by Area to Page 1

@pbi-report Create a Deneb heatmap for monthly sales by region

@pbi-report Create an SVG sparkline measure for revenue trend

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

## Getting Started

1. **Clone the repository**:
   ```bash
   git clone https://github.com/natalinio/agentic-powerbi-squad.git
   cd agentic-powerbi-squad
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Open in VS Code** with GitHub Copilot enabled.

4. **Start with a specification** — use `spec/sample_spec.md` as a template, or write your own.

5. **Choose your mode**:
   - **Full project**: `@delivery-lead Build from spec/sample_spec.md`
   - **Single task**: `@pbi-semantic-model Create a logical model for <requirements>`

6. **Open the result** in Power BI Desktop: open the `.pbip` file from the `PBIP/` folder.

---

## Sample Project: SalesOverview

The repository includes a complete example project (`SalesOverview/`) built from a sales analytics specification. It demonstrates:

- 7 TMDL tables (5 dimensions + 2 facts)
- DAX measures with fiscal year time intelligence
- Mock datasets with referential integrity
- 3-page PBIR report with KPI cards, charts, slicers, and matrix visuals
- Functional test definitions and execution results
- Report validation results

Use it as a reference for understanding the output format and project structure.

---

## Attribution

This project builds upon domain knowledge from the **[Goblin Power BI Agentic Development](https://github.com/data-goblins)** project by Data Goblins. Several skills — particularly SVG visuals, Deneb visuals, theme customization, report design patterns, and PBIR reference material — were developed using Goblin's published skill resources as a knowledge source and adapted for this multi-agent architecture.

Per the Goblin project's license terms:

> *Use or re-use of these skills: These skills are intended for free community use. You do not have the license to copy and incorporate them into your own products, trainings, courses, or tools. If you copy these skills — manually or by using an agent to rewrite them — you must include attribution and a link to this original project.*

**Original project**: [https://github.com/data-goblins](https://github.com/data-goblins)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.
