# AI Semantic Layer Builder

> **Build production-ready Power BI semantic models (PBIP/TMDL) from functional specifications using GitHub Copilot Custom Agent**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Power BI](https://img.shields.io/badge/Power%20BI-December%202025+-yellow)](https://powerbi.microsoft.com)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)

---

## 🎯 What is AI Semantic Layer Builder?

**AI Semantic Layer Builder** is a **GitHub Copilot Custom Agent** (`@semantic-modeler`) that automates the creation of Power BI semantic models in **PBIP format with TMDL** (Tabular Model Definition Language) from natural language functional specifications.

Instead of manually building data models, writing DAX measures, and configuring relationships in Power BI Desktop, you provide a specification document (in Markdown), and the agent generates:

- ✅ **Dimensional data model** (Kimball Star Schema)
- ✅ **TMDL files** (tables, relationships, measures)
- ✅ **Optimized DAX measures** (time intelligence, KPIs, aggregations)
- ✅ **Mock data** (Python/Faker-based CSV generation)
- ✅ **Automated functional tests** (DAX validation with pass/fail reports)
- ✅ **Quality assurance** (BPA rules compliance, syntax validation)

### Key Features

- 🤖 **Agentic Workflow**: 7-step methodology with mandatory approval gates
- 🛡️ **Anti-Hallucination**: MCP tools verify TMDL/DAX syntax against Microsoft official documentation
- 📐 **Best Practices Enforced**: Kimball methodology, naming conventions, DAX optimization framework, BPA rules (27+)
- 🔄 **Iterative & Auditable**: Each step requires user validation before proceeding
- 🌍 **Multilingual**: Communicate in your language (Italian, English), code always in English
- 🧪 **Test-Driven**: Automated DAX test execution via Python scripts

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites

1. **Power BI Desktop** (December 2025 or later)
   - Enable preview features:
     - ✅ Power BI Project (.pbip) save option
     - ✅ Store semantic model using TMDL format

2. **Python 3.10+** with virtual environment:
   ```powershell
   python --version  # Must be 3.10+
   ```

3. **GitHub Copilot** with Custom Agent support enabled

### Step 1: Clone the Repository

```bash
git clone https://github.com/natalinio/aisemanticlayer.git
cd aisemanticlayer
```

### Step 2: Set Up Python Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Step 3: Create PBIP Canvas

1. Open Power BI Desktop
2. Create a blank report
3. File → Save As → **Power BI Project**
4. Save in: `<ProjectName>/PBIP/<ProjectName>.pbip`
5. Close Power BI Desktop

### Step 4: Prepare Specifications

Create a Markdown file with your requirements:

```
<ProjectName>/input/spec_your_project.md
```

**Example Template**: See [[ProjectName]/input/sample_spec.md]([ProjectName]/input/sample_spec.md) — Sales Overview FYTD specification (demonstrates required structure and detail level)

### Step 5: Invoke the Agent

Open GitHub Copilot Chat in VS Code and type:

```
@semantic-modeler <ProjectName>/input/spec_your_project.md
```

The agent will execute a 7-step workflow:
1. **Requirements Analysis**
2. **Logical Data Model** (Mermaid ER diagram)
3. **Physical Model & TMDL** (code generation)
4. **DAX Development** (optimized measures)
5. **Mock Data Generation** (Python/Faker)
6. **Quality Review** (BPA compliance)
7. **Functional Testing** (automated DAX validation)

Each step requires your approval before proceeding.

### Step 6: Open in Power BI Desktop

```powershell
# Navigate to project folder
cd <ProjectName>/PBIP
# Double-click <ProjectName>.pbip to open in Power BI Desktop
```

Refresh the data → Validate model visually → Build reports!

---

## 📂 Repository Structure

```
aisemanticlayer/
├── .github/                           # Agentic system core (universal, project-agnostic)
│   ├── copilot-instructions.md        # Global instructions for GitHub Copilot
│   ├── agents/
│   │   └── semantic-modeler.agent.md  # Main invocable agent (@semantic-modeler)
│   ├── skills/                        # Step-by-step execution skills (7 files)
│   │   ├── 01-requirements-analysis.md
│   │   ├── 02-logical-model.md
│   │   ├── 03-physical-model-tmdl.md
│   │   ├── 04-dax-development.md
│   │   ├── 05-mock-data-generation.md
│   │   ├── 06-code-review.md
│   │   └── 07-functional-testing.md
│   ├── references/                    # TMDL, DAX, PBIP reference material (7 files)
│   │   ├── tmdl-syntax-reference.md
│   │   ├── naming-conventions.md
│   │   ├── pbip-folder-structure.md
│   │   ├── dax-patterns.md
│   │   ├── relationship-patterns.md
│   │   ├── dax-optimization-framework.md
│   │   └── bpa-rules-reference.md
│   └── scripts/                       # Universal tools (project-agnostic)
│       ├── fix_lineage_tags.py        # GUID lineageTag regeneration
│       ├── remove_tmdl_comments.py    # TMDL comment removal
│       └── run_tests.py               # Automated test execution engine
├── .venv/                             # Python virtual environment (root-level)
├── requirements.txt                   # Python dependencies for all steps
└── <ProjectName>/                     # Project folder (1 per project)
    ├── PBIP/                          # Power BI files ONLY (canvas)
    │   ├── <ProjectName>.pbip
    │   ├── <ProjectName>.SemanticModel/
    │   │   └── definition/            # TMDL files go here
    │   │       ├── model.tmdl
    │   │       ├── database.tmdl
    │   │       ├── tables/
    │   │       ├── relationships.tmdl
├── [ProjectName]/                     # Template folder (example structure, see [ProjectName]/README.md)
└── <ProjectName>/                     # Your project folders (create one per semantic model
    │   └── <ProjectName>.Report/
    ├── data/                          # Generated CSV mock data (Step 05)
    ├── scripts/                       # Project-specific scripts
    │   └── generate_mock_data.py      # Faker-based data generation
    ├── tests/                         # Functional test artifacts (Step 07)
    │   ├── tests_definition.json      # Test case definitions
    │   ├── tests_definition.md        # Manual test guide
    │   ├── tests_execution.md         # Test results report
    │   └── tests_execution_raw.json   # Raw test results
    └── input/                         # User specifications & inputs
        └── <spec_file>.md
```

### 📌 About `<ProjectName>` Placeholder

Throughout this documentation, **`<ProjectName>`** is a **placeholder** representing your actual project name.

**Examples of real project names:**
- `SalesOverview`
- `FinanceReportFYTD`
- `CustomerAnalytics`
- `InventoryDashboard`

**Template Folder:**
The repository includes a **`[ProjectName]`** folder as a **template/example** demonstrating the expected structure. This is NOT a working project — it's a blueprint for creating your own projects.

**To create a new project:**
1. Create a folder with your project name at repository root (e.g., `SalesOverview/`)
2. Create subfolders: `PBIP/`, `data/`, `scripts/`, `tests/`, `input/`
3. Create PBIP canvas in Power BI Desktop → Save as `SalesOverview/PBIP/SalesOverview.pbip`
4. Add your specifications in `SalesOverview/input/spec_your_requirements.md`
5. Invoke agent: `@semantic-modeler SalesOverview/input/spec_your_requirements.md`

**See `[ProjectName]/README.md` for detailed template instructions.**

---

## 🏗️ Architecture

### Agentic System Design

The system follows a **composable agentic architecture**:

```
User Specification (Markdown)
        ↓
@semantic-modeler (Custom Agent)
        ↓
┌───────────────────────────────────────────────────┐
│  Workflow Orchestrator (.github/agents/)          │
│  ├─ 01-requirements-analysis.md                   │
│  ├─ 02-logical-model.md                           │
│  ├─ 03-physical-model-tmdl.md                     │
│  ├─ 04-dax-development.md                         │
│  ├─ 05-mock-data-generation.md                    │
│  ├─ 06-code-review.md                             │
│  └─ 07-functional-testing.md                      │
└───────────────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────────────┐
│  Knowledge Base (.github/references/)             │
│  ├─ TMDL Syntax Reference                         │
│  ├─ DAX Patterns & Optimization                   │
│  ├─ Naming Conventions                            │
│  ├─ Relationship Patterns                         │
│  └─ BPA Rules (27+ rules)                         │
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

### Anti-Hallucination Strategy

The agent uses **MCP tools** to verify syntax before code generation:

- **`microsoft_docs_search`**: Search Microsoft documentation for TMDL/DAX syntax
- **`microsoft_docs_fetch`**: Fetch full documentation pages when needed
- **`microsoft_code_sample_search`**: Find DAX code examples for time intelligence

This ensures **100% accuracy** in TMDL syntax (whitespace-sensitive, tab-indented, YAML-like structure).

---

## 📖 Documentation

- **[Copilot Instructions](.github/copilot-instructions.md)**: Global rules for the agent
- **[Skills](.github/skills/)**: Step-by-step execution guides
- **[References](.github/references/)**: TMDL/DAX/BPA knowledge base
- **[Feature Specs](specs/)**: Functional requirements for new features
- **[Contributing](CONTRIBUTING.md)**: How to contribute to this project

---

## 🛠️ Advanced Usage

### Custom Project Initialization

```
@semantic-modeler <ProjectName>/input/spec_custom_project.md
```

### Manual Script Execution

#### Fix LineageTags (After TMDL Generation)
```powershell
python .github/scripts/fix_lineage_tags.py <ProjectName>
```

#### Remove TMDL Comments (If Parsing Errors)
```powershell
python .github/scripts/remove_tmdl_comments.py <ProjectName>
```

#### Run Functional Tests
```powershell
python .github/scripts/run_tests.py <ProjectName> --port 12345 --verbose
```

### Extending the System

1. **Add new DAX patterns**: Edit `.github/references/dax-patterns.md`
2. **Add BPA rules**: Edit `.github/references/bpa-rules-reference.md`
3. **Add relationship patterns**: Edit `.github/references/relationship-patterns.md`
4. **Customize agent behavior**: Edit `.github/agents/semantic-modeler.agent.md`

---

## 🧪 Example Output

### Input: Functional Specification
```markdown
# Sales Overview FYTD Report

## KPIs:
- Sales vs Budget (FYTD)
- Adjusted Profit %
- Average Monthly Sales

## Dimensions:
- Time (Fiscal Year, Fiscal Month)
- Area, Country, Customer
- Industry, Salesperson
```

### Output: Generated Artifacts

| Step | Output |
|------|--------|
| **Step 1** | Requirements table (KPIs, dimensions, relationships) |
| **Step 2** | Mermaid ER diagram (Star Schema) |
| **Step 3** | TMDL files (model.tmdl, tables/, relationships.tmdl) |
| **Step 4** | DAX measures in `_Measures` table (TOTALYTD, DIVIDE, etc.) |
| **Step 5** | CSV mock data (referential integrity preserved) |
| **Step 6** | BPA compliance report (27+ rules validated) |
| **Step 7** | Automated test results (✅ PASS / ❌ FAIL for each measure) |

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

- [ ] **v1.0** (Current): PBIP/TMDL semantic model generation
- [ ] **v1.1**: Report generation (Power BI Report definition)
- [ ] **v1.2**: Advanced DAX patterns (statistical functions, predictive measures)
- [ ] **v1.3**: Azure integration (Azure SQL, Azure Data Lake)
- [ ] **v1.4**: CI/CD pipelines (Azure DevOps, GitHub Actions)
- [ ] **v2.0**: Multi-model support (Azure Analysis Services, SQL Server)

---

## ⭐ Star History

If you find this project useful, please consider giving it a star! ⭐

---

**Built with ❤️ by [Andrea Natali](https://github.com/natalinio)**
