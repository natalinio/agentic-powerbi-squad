# Power BI AI Developer

> **Build complete Power BI projects — semantic models (PBIP/TMDL) and report visuals (PBIR) — from functional specifications using a GitHub Copilot Custom Agent**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Power BI](https://img.shields.io/badge/Power%20BI-December%202025+-yellow)](https://powerbi.microsoft.com)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)

---

## 🎯 What is Power BI AI Developer?

**Power BI AI Developer** is a **GitHub Copilot Custom Agent** (`@powerbi-AI-developer`) that automates the creation of Power BI semantic models in **PBIP format with TMDL** (Tabular Model Definition Language) and report visuals in **PBIR format** from natural language functional specifications.

Instead of manually building data models, writing DAX measures, and configuring relationships in Power BI Desktop, you provide a specification document (in Markdown), and the agent generates:

- ✅ **Dimensional data model** (Kimball Star Schema)
- ✅ **TMDL files** (tables, relationships, measures)
- ✅ **Optimized DAX measures** (time intelligence, KPIs, aggregations)
- ✅ **Mock data** (Python/Faker-based CSV generation)
- ✅ **Automated functional tests** (DAX validation with pass/fail reports)
- ✅ **Quality assurance** (BPA rules compliance, syntax validation)
- ✅ **Report implementation** (PBIR visual generation from blueprint)
- ✅ **End-to-end validation** (cross-reference PBIR ↔ TMDL ↔ blueprint)

### Key Features

- 🤖 **Agentic Workflow**: 10-step methodology (plus Step 00 bootstrap) with mandatory approval gates, disk-based state management, and explicit decision-point tracking
- 🧭 **Deterministic State**: Canonical `workflow_state.json` shape, decision ledger, and resumability-safe transitions
- 🚦 **Contract Gates**: Input/Output artifact validation before starting or completing each step
- 🪟 **Scoped Context Loading**: The agent loads only the current step skill and required references/artifacts (no future-step preloading unless strictly needed)
- 🛡️ **Anti-Hallucination**: MCP tools verify TMDL/DAX syntax against Microsoft official documentation
- 📐 **Best Practices Enforced**: Kimball methodology, naming conventions, DAX optimization framework, BPA rules (27+)
- 🔄 **Iterative & Auditable**: Each step requires user validation before proceeding
- 🌍 **Multilingual**: Communicate in your language (Italian, English), code always in English
- 🧪 **Test-Driven**: Automated DAX test execution via Python scripts

---

## 🚀 Quick Start (5 Minutes)

This section is intentionally explicit and copy/paste friendly.

### 0) Prerequisites (check once)

1. **Power BI Desktop** (December 2025 or later)
        - Enable preview features:
          - ✅ Power BI Project (.pbip) save option
          - ✅ Store semantic model using TMDL format
2. **Python 3.10+**
3. **VS Code + GitHub Copilot Chat** (Custom Agent enabled)

Quick checks:

```powershell
python --version
code --version
```

### 1) Clone repository

```bash
git clone https://github.com/natalinio/PowerBI-AI-FullStack-Developer.git
cd PowerBI-AI-FullStack-Developer
```

### 2) Create and activate Python environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Expected result: no installation errors.

### 3) Create your project folder

Choose a project name (example: `SalesOverview`) and create at least `spec/`:

```powershell
mkdir SalesOverview
mkdir SalesOverview\spec
```

Note: `data/`, `scripts/`, `tests/`, and PBIP scaffold are created automatically by the agent if missing.

### 4) Create the functional specification

Copy the template and rename it:

```powershell
Copy-Item spec\specification_template.md SalesOverview\spec\spec_sales_overview.md
```

Then fill **all sections** in `SalesOverview/spec/spec_sales_overview.md`.

Reference files:
- Template: [spec/specification_template.md](spec/specification_template.md)
- Full example: [spec/sample_spec.md](spec/sample_spec.md)

### 5) Open in VS Code and run the agent

1. Open the repository folder in VS Code.
2. Open GitHub Copilot Chat.
3. Run one of the following:

Option A (recommended):

```
@powerbi-AI-developer SalesOverview/spec/spec_sales_overview.md
```

Option B (`/build` prompt):

1. Type `/` in Copilot Chat
2. Select `build`
3. Provide spec path: `SalesOverview/spec/spec_sales_overview.md`

### 6) Approve the workflow step by step

The agent executes:

1. Requirements Analysis
2. Logical Data Model
3. Physical Model & TMDL
4. DAX Development
5. Mock Data Generation
6. Quality Review
7. Functional Testing
8. Report Design
9. Report Implementation
10. Report Quality Validation

After each step, approve explicitly (for example: `Approved` / `Proceed`).

### 7) Open the generated PBIP in Power BI Desktop

```powershell
cd SalesOverview\PBIP
```

Open `SalesOverview.pbip` in Power BI Desktop and click **Refresh**.

### 8) Quick troubleshooting (most common)

- `gh` / tooling not found: restart terminal and verify installation paths.
- Python import errors: re-activate `.venv` and run `pip install -r requirements.txt` again.
- PBIP open error: ensure Desktop preview features are enabled and files are not blocked by OneDrive sync locks.
- Invalid model objects in tests/visuals: rerun from the last approved step; workflow state is persisted in `workflow_state.json`.

---

## 📂 Repository Structure

```
PowerBI-AI-FullStack-Developer/
├── .github/                           # Agentic system core (universal, project-agnostic)
│   ├── copilot-instructions.md        # Global instructions for GitHub Copilot
│   ├── agents/
│   │   └── powerbi-AI-developer.agent.md  # Main invocable agent
│   ├── skills/                        # Step-by-step execution skills (11 files: Step 00 + Steps 01-10)
│   │   ├── 00-project-initialization.md
│   │   ├── 01-requirements-analysis.md
│   │   ├── 02-logical-model.md
│   │   ├── 03-physical-model-tmdl.md
│   │   ├── 04-dax-development.md
│   │   ├── 05-mock-data-generation.md
│   │   ├── 06-code-review.md
│   │   ├── 07-functional-testing.md
│   │   ├── 08-report-design.md
│   │   ├── 09-report-implementation.md
│   │   └── 10-report-quality-validation.md
│   ├── references/                    # TMDL, DAX, PBIP reference material
│   │   ├── workflow-core.md           # Centralized per-step governance (context flushing, checkpointing, stop gate)
│   │   ├── tmdl-syntax-reference.md
│   │   ├── naming-conventions.md
│   │   ├── pbip-folder-structure.md
│   │   ├── dax-patterns.md
│   │   ├── relationship-patterns.md
│   │   ├── dax-optimization-framework.md
│   │   ├── security-rls-best-practices.md
│   │   ├── bpa-rules-reference.md
│   │   ├── functional-testing-methodology.md  # Testing phase catalog, Python runner, anti-patterns
│   │   ├── report-design-visualization-best-practices.md
│   │   ├── pbir-visual-templates.md
│   │   └── workflow-state-management.md
│   ├── docs/                          # Interactive HTML documentation tools
│   │   ├── architecture.html          # Workflow lane view + Agent Explorer tab
│   │   └── agent-explorer.html        # Graph explorer: Agent → Skills → References/Scripts
│   ├── scripts/                       # Universal tools (project-agnostic)
│   │   ├── fix_lineage_tags.py        # GUID lineageTag regeneration
│   │   ├── remove_tmdl_comments.py    # TMDL comment removal
│   │   └── run_tests.py               # Automated test execution engine
│   └── prompts/                       # Reusable prompt files
│       └── build.prompt.md            # End-to-end project builder prompt (/build)
│
├── .gitignore                         # Git ignore rules
├── .venv/                             # Python virtual environment (shared by all projects)
├── requirements.txt                   # Python dependencies for all workflow steps
├── CHANGELOG.md                       # Version history and release notes
├── CODE_OF_CONDUCT.md                 # Project code of conduct
├── CONTRIBUTING.md                    # Contribution guidelines
├── LICENSE                            # MIT License
├── PUBLISHING.md                      # Publishing and release guidelines
├── README.md                          # This file
├── SECURITY.md                        # Security policy
├── STRUCTURE_VERIFICATION.md          # Repository structure validation
├── spec/                              # 📋 Global specification templates/examples
│   ├── specification_template.md       # EMPTY TEMPLATE (start here)
│   └── sample_spec.md                  # COMPLETE EXAMPLE (Sales Overview FYTD)
│
├── [ProjectName]/                     # 📌 TEMPLATE FOLDER (example structure)
│   ├── README.md                      # Template usage instructions
│   ├── spec/                          # Project specification folder (example)
│   ├── PBIP/                          # (empty - created by user in Power BI Desktop)
│   ├── data/                          # (empty - populated by Step 05)
│   ├── scripts/                       # (empty - populated by Step 05)
│   └── tests/                         # (empty - populated by Step 07)
│
└── <YourProjectName>/                 # 🚀 YOUR PROJECT FOLDERS (create one per semantic model)
        ├── spec/
        │   └── spec_your_requirements.md  # Your functional specifications
        ├── PBIP/
        │   ├── <YourProjectName>.pbip
        │   ├── <YourProjectName>.SemanticModel/
        │   │   └── definition/            # TMDL files generated by agent
        │   │       ├── model.tmdl
        │   │       ├── database.tmdl
        │   │       ├── tables/
        │   │       │   ├── Dim_*.tmdl
        │   │       │   ├── Fact_*.tmdl
        │   │       │   └── _Measures.tmdl
        │   │       ├── relationships.tmdl
        │   │       └── expressions.tmdl
        │   └── <YourProjectName>.Report/
        │       └── definition/
        │           └── pages/             # PBIR report pages (Step 09)
        │               ├── <pageId>/
        │               │   ├── page.json
        │               │   └── visuals/
        │               │       └── <visualId>/
        │               │           └── visual.json
        │               └── ...
        ├── data/                          # Generated CSV mock data (Step 05)
        │   ├── Dim_*.csv
        │   └── Fact_*.csv
        ├── scripts/                       # Project-specific scripts
        │   └── generate_mock_data.py      # Faker-based data generation
        ├── tests/                         # Functional test artifacts (Steps 07, 10)
        │   ├── tests_definition.json      # Test case definitions
        │   ├── tests_definition.md        # Manual test guide
        │   ├── tests_execution.md         # Test results report
        │   ├── tests_execution_raw.json   # Raw test results
        │   ├── report_validation_execution.md  # Report quality validation (Step 10)
        │   └── lessons-learned.md         # Incident log (created only for user-reported defects)
        └── workflow_state.json            # Workflow progress tracker + decision/audit ledger
```

### 📌 About Project Names

**`[ProjectName]`** (with square brackets) = **Template folder** in this repository
- Located at repository root: `[ProjectName]/`
- Contains the expected folder structure (including an example `spec/` folder) and empty implementation folders (`PBIP/`, `data/`, `scripts/`, `tests/`).
- Purpose: Reference structure for creating new projects
- **Do NOT use this folder for real projects**

**`<YourProjectName>`** (with angle brackets) = **Your actual project folders**
- Create at repository root with your project name (e.g., `SalesOverview/`, `FinanceReportFYTD/`)
- Each project is independent and isolated

**Examples of real project names:**
- `SalesOverview`
- `FinanceReportFYTD`
- `CustomerAnalytics`
- `InventoryDashboard`

**To create a new project:**
1. Create a folder with your project name at repository root (e.g., `SalesOverview/`)
2. Create subfolders: `spec/` (the agent can create the others during initialization)
3. **Copy specification template** from `spec/specification_template.md` to `SalesOverview/spec/`
4. **Fill in the specification** with your requirements (rename to `spec_sales_overview.md`)
5. Invoke agent: `@powerbi-AI-developer SalesOverview/spec/spec_sales_overview.md` (it will bootstrap the PBIP scaffold via Step 00 if missing)
6. (Optional) Create PBIP manually in Power BI Desktop → File → Save As → Power BI Project
7. Save as: `SalesOverview/PBIP/SalesOverview.pbip`

**See [`[ProjectName]/README.md`]([ProjectName]/README.md) for detailed template instructions.**

---

## 🏗️ Architecture

### Agentic System Design

![Power BI AI Developer Architecture](.github/docs/architecture.png)

The system follows a **composable agentic architecture**:

```
User Specification (Markdown)
        ↓
@powerbi-AI-developer (Custom Agent)
        ↓
┌───────────────────────────────────────────────────┐
│  Workflow Orchestrator (.github/agents/)          │
│  ├─ 01-requirements-analysis.md                   │
│  ├─ 02-logical-model.md                           │
│  ├─ 03-physical-model-tmdl.md                     │
│  ├─ 04-dax-development.md                         │
│  ├─ 05-mock-data-generation.md                    │
│  ├─ 06-code-review.md                             │
│  ├─ 07-functional-testing.md                      │
│  ├─ 08-report-design.md                           │
│  ├─ 09-report-implementation.md                   │
│  └─ 10-report-quality-validation.md               │
└───────────────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────────────┐
│  Knowledge Base (.github/references/)             │
│  ├─ Workflow Core (governance: context, gate, checkpoint) │
│  ├─ TMDL Syntax Reference                         │
│  ├─ DAX Patterns & Optimization                   │
│  ├─ Naming Conventions                            │
│  ├─ Relationship Patterns                         │
│  ├─ BPA Rules (27+ rules)                         │
│  ├─ PBIR Visual Templates                         │
│  ├─ Functional Testing Methodology                │
│  └─ Workflow State Management                     │
└───────────────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────────────┐
│  Universal Tools (.github/scripts/)               │
│  ├─ fix_lineage_tags.py (GUID regeneration)       │
│  ├─ remove_tmdl_comments.py (syntax cleanup)      │
│  └─ run_tests.py (automated DAX testing)          │
└───────────────────────────────────────────────────┘
        ↓
Power BI Semantic Model (PBIP/TMDL)
```

Execution model: **single orchestrator as the only workflow state owner**, with optional specialist workers invoked inside a step (for example TMDL linting, DAX checks, PBIR validation). Workers do not mutate `workflow_state.json` directly.

### 🎯 The Specification: Your Sacred Grail

The **functional specification** is the **single most critical input** to the agentic workflow. The quality, completeness, and clarity of your specification **directly determines** the quality of the generated semantic model.

**Why the specification is critical:**
- 🎯 **Source of Truth**: All KPIs, relationships, and business logic derive from it
- 🔍 **Anti-Hallucination**: Prevents the agent from making assumptions about undefined requirements
- 📐 **Design Decisions**: Guides data modeling choices (star schema, granularity, hierarchies)
- 🧪 **Test Foundation**: Automated tests validate against specification requirements
- 📝 **Documentation**: Becomes living documentation for the semantic model

**Required Structure** (use `specification_template.md`):
1. **Report Objective & Audience** → Defines scope and use cases
2. **KPI Definitions** (functional, not technical) → Drives DAX measure generation
3. **Data Groupings & Segmentations** → Defines dimension hierarchies
4. **Filter Dimensions** → Determines dimension table design
5. **Visualization Structure** → Informs relationship optimization
6. **Data Schema with Sample Values** → Defines physical table structure
7. **Logical Relationships** → Ensures correct cardinality and cross-filtering
8. **RLS Requirements** → Security architecture
9. **Functional Requirements** → **CRITICAL**: Refresh strategy (frequency, storage mode, incremental refresh, data volumes), time intelligence, performance
10. **Additional Constraints** → Technical limitations, business rules

**⚠️ Section 9 (Refresh Strategy) is MANDATORY:**
- Without refresh frequency → Agent cannot determine Import vs DirectQuery
- Without data volumes → Agent cannot configure incremental refresh
- Without audit fields → Agent cannot set up incremental refresh partitions
- Incomplete refresh strategy = Suboptimal or incorrect physical model design

**Without a complete specification, the agent CANNOT:**
- Generate accurate DAX measures
- Design optimal relationships
- Create appropriate dimension hierarchies
- Validate functional correctness
- Ensure security requirements

**📖 See the template**: [spec/specification_template.md](spec/specification_template.md)

### Anti-Hallucination Strategy

The agent uses **MCP tools** to verify syntax before code generation:

- **`microsoft_docs_search`**: Search Microsoft documentation for TMDL/DAX syntax
- **`microsoft_docs_fetch`**: Fetch full documentation pages when needed
- **`microsoft_code_sample_search`**: Find DAX code examples for time intelligence

This ensures **100% accuracy** in TMDL syntax (whitespace-sensitive, tab-indented, YAML-like structure).

---

## 📖 Documentation

- **[Agent Definition](.github/agents/powerbi-AI-developer.agent.md)**: Core agent orchestrator (10-step workflow)
- **[Build Prompt](.github/prompts/build.prompt.md)**: Reusable prompt for end-to-end project invocation (`/build`)
- **[Copilot Instructions](.github/copilot-instructions.md)**: Global rules for GitHub Copilot
- **[Skills](.github/skills/)**: Step-by-step execution guides (Steps 00-10)
- **[References](.github/references/)**: TMDL/DAX/BPA/PBIR knowledge base
- **[Architecture Explorer](.github/docs/architecture.html)**: Interactive workflow lane view with dynamic skill descriptions + Agent Explorer tab (open locally in browser)
- **[Agent Explorer](.github/docs/agent-explorer.html)**: Graph view of the Agent → Skills → References/Scripts hierarchy with Reload and Raw/Rendered preview
- **[Specification Templates](spec/)**: Templates and examples for writing project specifications
- **[Contributing](CONTRIBUTING.md)**: How to contribute to this project

---

## 🛠️ Advanced Usage

### Custom Project Initialization

```
@powerbi-AI-developer <YourProjectName>/spec/spec_custom_project.md
```

**Example:**
```
@powerbi-AI-developer FinanceReportFYTD/spec/spec_finance_report.md
```

### Manual Script Execution

#### Fix LineageTags (After TMDL Generation)
```powershell
python .github/scripts/fix_lineage_tags.py <YourProjectName>
```

**Example:**
```powershell
python .github/scripts/fix_lineage_tags.py SalesOverview
```

#### Remove TMDL Comments (If Parsing Errors)
```powershell
python .github/scripts/remove_tmdl_comments.py <YourProjectName>
```

**Example:**
```powershell
python .github/scripts/remove_tmdl_comments.py SalesOverview
```

#### Run Functional Tests
```powershell
python .github/scripts/run_tests.py <YourProjectName> --port 12345 --verbose
```

**Example:**
```powershell
python .github/scripts/run_tests.py SalesOverview --port 54321 --verbose
```

### Extending the System

1. **Add new DAX patterns**: Edit `.github/references/dax-patterns.md`
2. **Add BPA rules**: Edit `.github/references/bpa-rules-reference.md`
3. **Add relationship patterns**: Edit `.github/references/relationship-patterns.md`
4. **Customize agent behavior**: Edit `.github/agents/powerbi-AI-developer.agent.md`

---

## 🧪 Example Output

### Generated Artifacts

| Step | Output |
|------|--------|
| **Step 1** | Requirements table (KPIs, dimensions, relationships) |
| **Step 2** | Mermaid ER diagram (Star Schema) |
| **Step 3** | TMDL files (model.tmdl, tables/, relationships.tmdl) |
| **Step 4** | DAX measures in `_Measures` table (TOTALYTD, DIVIDE, etc.) |
| **Step 5** | CSV mock data (referential integrity preserved) |
| **Step 6** | BPA compliance report (27+ rules validated) |
| **Step 7** | Automated test results (✅ PASS / ❌ FAIL for each measure) |
| **Step 8** | Report design blueprint (`report_blueprint.json`) |
| **Step 9** | PBIR report files (page.json, visual.json per page/visual) |
| **Step 10** | Report quality validation report (field cross-reference, compliance) |

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- How to set up development environment
- Coding standards and best practices
- Pull request process
- Issue templates (bug reports, feature requests)

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

**Copyright © 2026 Andrea Natali**

You are free to use, modify, and distribute this software, provided you include the copyright notice and license terms.

---

## 🙏 Acknowledgments

- **Microsoft Power BI Team**: For PBIP/TMDL format specification
- **Kimball Group**: For dimensional modeling methodology
- **GitHub Copilot Team**: For custom agent framework
- **Open Source Community**: For Python libraries (pandas, faker, pytest)

---

## 📧 Contact

- **Author**: Andrea Natali
- **GitHub**: [@natalinio](https://github.com/natalinio)
- **Email**: andrea.natali@avanade.com

---

## 🗺️ Roadmap

- [ ] **v1.0** (Current): PBIP/TMDL semantic model generation + PBIR report implementation
- [ ] **v1.1**: Advanced report features (bookmarks, drill-through, conditional formatting)
- [ ] **v1.2**: Advanced DAX patterns (statistical functions, predictive measures)
- [ ] **v1.3**: Azure integration (Azure SQL, Azure Data Lake)
- [ ] **v1.4**: CI/CD pipelines (Azure DevOps, GitHub Actions)
- [ ] **v2.0**: Multi-model support (Azure Analysis Services, SQL Server)

---

## ⭐ Star History

If you find this project useful, please consider giving it a star! ⭐

---

**Built with ❤️ by [Andrea Natali](https://github.com/natalinio)**
