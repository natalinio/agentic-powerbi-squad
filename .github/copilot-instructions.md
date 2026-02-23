````instructions
# Global Copilot Instructions — AI Semantic Layer Builder

This repository contains a **GitHub Copilot Custom Agent** (`@semantic-modeler`) that builds Power BI semantic models in **PBIP format with TMDL** from functional specifications.

## Repository Structure

```
aisemanticlayer/
├── .github/                           ← Agentic system core (universal, project-agnostic)
│   ├── copilot-instructions.md        ← You are here (global instructions)
│   ├── agents/
│   │   └── semantic-modeler.agent.md  ← Main invocable agent (@semantic-modeler)
│   ├── skills/                        ← Step-by-step execution skills (7 files)
│   ├── references/                    ← TMDL, DAX, PBIP reference material (7 files)
│   │   ├── tmdl-syntax-reference.md
│   │   ├── naming-conventions.md
│   │   ├── pbip-folder-structure.md
│   │   ├── dax-patterns.md
│   │   ├── relationship-patterns.md
│   │   ├── dax-optimization-framework.md
│   │   └── bpa-rules-reference.md
│   ├── scripts/                       ← Universal tools (project-agnostic)
│   │   ├── fix_lineage_tags.py        ← GUID lineageTag regeneration
│   │   ├── remove_tmdl_comments.py    ← TMDL comment removal
│   │   └── run_tests.py              ← Automated test execution engine
│   └── prompts/                       ← Reusable prompt files
├── .gitignore
├── .venv/                             ← Python virtual environment (root-level)
├── requirements.txt                   ← Python dependencies for all steps
└── <ProjectName>/                     ← Project folder (1 per project)
    ├── PBIP/                          ← Power BI files ONLY (canvas)
    │   ├── <ProjectName>.pbip
    │   ├── <ProjectName>.SemanticModel/
    │   │   └── definition/            ← TMDL files go here
    │   │       ├── model.tmdl
    │   │       ├── database.tmdl
    │   │       ├── tables/
    │   │       ├── relationships.tmdl
    │   │       └── expressions.tmdl
    │   └── <ProjectName>.Report/
    ├── data/                          ← Generated CSV mock data (Step 05)
    ├── scripts/                       ← Project-specific scripts
    │   └── generate_mock_data.py      ← Faker-based data generation
    ├── tests/                         ← Functional test artifacts (Step 07)
    │   ├── tests_definition.json      ← Test case definitions
    │   ├── tests_definition.md        ← Manual test guide
    │   ├── tests_execution.md         ← Test results report
    │   └── tests_execution_raw.json   ← Raw test results
    └── input/                         ← User specifications & inputs
        └── <spec_file>.md
```

## Prerequisites

Before using the `@semantic-modeler` agent, ensure the following are installed and configured:

### 1. Python 3.10+ (Required for Steps 05 and 07)
```powershell
python --version   # Must be 3.10 or higher
```

### 2. Python Virtual Environment
The `.venv/` environment at the repository root is shared across all projects:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Power BI Desktop (December 2025 or later)
- Enable preview features:
  - **Power BI Project (.pbip) save option**
  - **Store semantic model using TMDL format**
- Used for: creating the PBIP canvas, refreshing data, visual validation

### 4. PBIP Canvas (per project)
Each project requires an empty PBIP canvas created via Power BI Desktop:
1. Open Power BI Desktop → Create blank report
2. File → Save As → Power BI Project (.pbip)
3. Save in: `<ProjectName>/PBIP/<ProjectName>.pbip`
4. Close Power BI Desktop

### 5. Optional Tools
- **DAX Studio**: For discovering Analysis Services port (Step 07)
- **Tabular Editor**: For BPA rule validation
- **TMDL VS Code Extension**: `analysis-services.TMDL` for syntax highlighting

## Key Rules

1. **Language**: All agent conversations follow the user's language. All generated code, TMDL, DAX, and file content **must be in English**.
2. **Methodology**: Strictly follow Kimball dimensional modeling (Star Schema). Reference `.github/references/` for syntax and patterns.
3. **Anti-Hallucination**: Before generating any TMDL or DAX code, the agent MUST verify syntax against Microsoft official documentation using the `microsoft_docs_search` or `microsoft_docs_fetch` MCP tools.
4. **TMDL Accuracy**: TMDL is whitespace-sensitive (tab-indented, YAML-like). Any indentation error causes parsing failures in Power BI Desktop. Always cross-reference with `.github/references/tmdl-syntax-reference.md`.
5. **Naming Conventions**: Follow `.github/references/naming-conventions.md` strictly for all tables, columns, measures, and relationships.
6. **Relationship Design**: Reference `.github/references/relationship-patterns.md` for role-playing dimensions, many-to-many, self-referencing hierarchies.
7. **DAX Optimization**: Apply `.github/references/dax-optimization-framework.md` for performance-optimized measures.
8. **BPA Compliance**: Apply `.github/references/bpa-rules-reference.md` Best Practice Analyzer rules for production-quality models (preventive guidelines + detective validation).
9. **LineageTag Safety**: After generating TMDL files (Step 03), ALWAYS run `.github/scripts/fix_lineage_tags.py <ProjectName>` to ensure all GUIDs are cryptographically unique.
10. **Project Isolation**: Each project lives in its own `<ProjectName>/` folder. Never mix artifacts across projects.

## How to Use the Agent

Invoke the custom agent in GitHub Copilot Chat:

```
@semantic-modeler <ProjectName>/input/spec_sales_overview_fytd.md
```

The agent will execute a 7-step workflow with mandatory approval gates, leveraging skills and references for anti-hallucination.

## Universal Scripts (.github/scripts/)

These tools are project-agnostic and are invoked by skills during the workflow:

| Script | Purpose | Invoked by |
|--------|---------|------------|
| `fix_lineage_tags.py <ProjectName>` | Regenerate all lineageTag GUIDs with unique UUID v4 | Skill 03 (Physical Model) |
| `remove_tmdl_comments.py <ProjectName>` | Remove unsupported TMDL comments | Skill 03 (Physical Model) |
| `run_tests.py <ProjectName> [--port N]` | Execute automated DAX tests | Skill 07 (Functional Testing) |

## What's New

**Architecture** (Priority: CRITICAL):
- ✅ **New project folder structure**: `<ProjectName>/` with `PBIP/`, `data/`, `scripts/`, `tests/`, `input/` subfolders
- ✅ **Universal scripts**: `.github/scripts/` contains project-agnostic tools (lineage fix, comment removal, test runner)
- ✅ **Root requirements.txt**: Single Python dependency file for all workflow steps
- ✅ **Prerequisites**: Documented in copilot-instructions.md (Python, PBI Desktop, canvas)

**References** (Priority: HIGH):
- ✅ **relationship-patterns.md**: Advanced patterns for role-playing dimensions, many-to-many, self-referencing hierarchies, troubleshooting
- ✅ **dax-optimization-framework.md**: Comprehensive DAX performance optimization framework with testing patterns
- ✅ **bpa-rules-reference.md**: Best Practice Analyzer rules (27+ rules, 6 categories) for preventive guidelines and detective validation
- ✅ **07-functional-testing.md**: Comprehensive functional testing methodology with mandatory Model Introspection

## Critical Lessons Learned (Historical Errors — MUST AVOID)

Over multiple iterations, the following critical errors were identified and fixed. **ALWAYS verify these before generating TMDL files**:

### 1. ⛔ TMDL Comments NOT Supported
**Error**: Agent added `///` and `//` comments to TMDL files, causing parsing failures  
**Root Cause**: Assumed TMDL supported comments like DAX does  
**Fix**: TMDL does NOT support ANY comment syntax (`///`, `//`, `/* */`, `<!-- -->`). Comments cause "Unexpected token" errors.  
**Prevention**: See "⛔ COMMENTS NOT SUPPORTED" section in `.github/skills/03-physical-model-tmdl.md`

### 2. ⛔ Duplicate LineageTags (GUID Collision)
**Error**: Power BI rejected model with "lineage-tag already exists" error  
**Root Cause**: Used deterministic GUID patterns (d1e2f3a4-..., e2f3a4b5-...) instead of random UUID v4  
**Fix**: Always use `uuid.uuid4()` or equivalent cryptographic randomness for ALL lineageTags  
**Prevention**: Every `lineageTag` property MUST have a globally unique value across ALL objects in the model

### 3. ⛔ CompatibilityLevel Mismatch
**Error**: "Tabular databases do not support CompatibilityLevel downgrade" error  
**Root Cause**: Used outdated compatibilityLevel (1567 for Sept 2024) instead of matching installed Power BI Desktop version (1600 for Dec 2025)  
**Fix**: ALWAYS verify Power BI Desktop version and use correct compatibilityLevel mapping table in `.github/skills/03-physical-model-tmdl.md`  
**Prevention**: Default to **1600** for December 2025 and later versions unless user specifies otherwise

### 4. ⛔ Security Filtering Behavior Constraint Violation
**Error**: "Already has a relationship where Security Filtering Behavior is set to Both" error  
**Root Cause**: Confused `securityFilteringBehavior` (RLS propagation, max 1 bothDirections per table) with `crossFilteringBehavior` (query filtering, no limit)  
**Fix**: Use `securityFilteringBehavior: oneDirection` for ALL relationships by default, UNLESS specific RLS requirement exists  
**Prevention**: See relationship property documentation in `.github/references/relationship-patterns.md`

### 5. ⛔ Ambiguous Relationship Paths (CRITICAL)
**Error**: "There are ambiguous paths between 'Fact_Sales' and 'Dim_Country'" error  
**Root Cause**: Created redundant Foreign Keys in Fact table (CustomerKey, CountryKey, AreaKey) when Customer already links to Country and Country links to Area, creating multiple paths to same dimension  
**Fix**: Remove redundant direct relationships. Fact tables should connect ONLY to the most granular dimension in a hierarchy  
**Example**: If `Fact_Sales → Dim_Customer` and `Dim_Customer → Dim_Country`, then do NOT create direct `Fact_Sales → Dim_Country`  
**Prevention**: 
- See "⛔ CRITICAL: Ambiguous Path Detection" in `.github/skills/02-logical-model.md`
- See "⛔ CRITICAL: Ambiguous Path Prevention" in `.github/skills/03-physical-model-tmdl.md`
- See "7. Ambiguous Paths (Critical Anti-Pattern)" in `.github/references/relationship-patterns.md`
- ALWAYS trace relationship paths before generating `relationships.tmdl` to detect redundancies

**Design Rule**: Between any two tables, there must be EXACTLY ONE active relationship path. If a dimension is reachable through another dimension, do NOT create a direct FK in the fact table.

### 6. ⛔ SummarizeBy Property Misuse (BPA Violation)
**Error**: Fact table measure columns had `summarizeBy: sum` or `summarizeBy: average` instead of `none`  
**Root Cause**: Assumed that numeric measure columns should have natural aggregation behavior enabled  
**Fix**: ALL columns (including measures in fact tables) MUST have `summarizeBy: none` to force users to use explicit DAX measures  
**Example**: Column `'Sales Amount LC'` had `summarizeBy: sum` → changed to `summarizeBy: none`  
**Prevention**: 
- See "SUMMARIZEBY_SHOULD_BE_NONE" BPA rule in `.github/references/bpa-rules-reference.md`
- See template in `.github/skills/03-physical-model-tmdl.md` (Fact Table Measure Column Template)
- ALWAYS set `summarizeBy: none` for ALL columns in fact tables to prevent accidental drag-and-drop aggregations

**Design Rule**: `summarizeBy: none` forces users to use explicit measures, ensuring correct aggregation logic and preventing calculation errors from auto-summarization.

### 7. ⛔ DATESYTD Dynamic Parameter Limitation (DAX Engine Constraint)
**Error**: DATESYTD function showed warning "Only constant date value is allowed as a year end date argument" when using variable parameter  
**Root Cause**: Attempted to pass a dynamic variable (`FiscalYearEndMonth` calculated from `SELECTEDVALUE(Parameters[ParameterValue])`) as second parameter to `DATESYTD`, which requires a literal string constant for query optimization  
**Fix**: Replace `DATESYTD` with manual fiscal YTD logic using `CALCULATE` + `FILTER` over `ALL(Dim_Date[Date])`  
**Example**: 
```dax
// ❌ WRONG (causes warning):
CALCULATE([Sales Amount], DATESYTD(Dim_Date[Date], FiscalYearEndMonth))

// ✅ CORRECT (dynamic parameter support):
VAR CurrentDate = MAX(Dim_Date[Date])
VAR FYStartMonth = VALUE(SELECTEDVALUE(Parameters[ParameterValue], "1"))
VAR CurrentYear = YEAR(CurrentDate)
VAR CurrentMonth = MONTH(CurrentDate)
VAR FiscalYear = IF(CurrentMonth >= FYStartMonth, CurrentYear, CurrentYear - 1)
VAR FYStartDate = DATE(FiscalYear, FYStartMonth, 1)
RETURN
    CALCULATE(
        [Sales Amount],
        FILTER(
            ALL(Dim_Date[Date]),
            Dim_Date[Date] >= FYStartDate && Dim_Date[Date] <= CurrentDate
        )
    )
```
**Prevention**: 
- See "Time Intelligence with Dynamic Parameters" warning in `.github/skills/04-dax-development.md`
- Time intelligence functions requiring constant parameters: `DATESYTD`, `TOTALYTD`, `DATESMTD`, `TOTALMTD`, `DATESQTD`, `TOTALQTD`
- Use manual filtering logic when parameters must be dynamic

**Design Rule**: DAX time intelligence functions optimize query plans by requiring constant year-end dates. For dynamic fiscal calendars, implement manual date filtering using `CALCULATE` + `FILTER` + `ALL(Dim_Date[Date])`.

### 8. ⛔ Test Query Object Name Mismatch (Model Introspection Failure)
**Error**: 10 out of 22 automated functional tests failed with "Column not found" errors  
**Root Cause**: Agent generated DAX test queries using assumed column names with spaces (e.g., `Dim_Area[Area Name]`, `Dim_Customer[Customer Name]`) instead of reading the actual PascalCase column names from TMDL files (e.g., `Dim_Area[AreaName]`, `Dim_Customer[CustomerName]`). Also used SQL `OR` syntax instead of DAX `||` operator.  
**Fix**: Added mandatory **Step B.0: Model Introspection** to `.github/skills/07-functional-testing.md`. Before generating ANY test definition or DAX query, the agent MUST:
  1. Read ALL TMDL table files to extract exact column names
  2. Read `_Measures.tmdl` to extract exact measure names
  3. Build a **Model Object Registry** (internal lookup table)
  4. Validate ALL DAX queries against the registry  
**Prevention**:
- See "⛔ Step B.0: Model Introspection" in `.github/skills/07-functional-testing.md`
- See `.github/references/naming-conventions.md` — columns use PascalCase (no spaces), measures use natural language (with spaces)
- NEVER assume or guess object names — ALWAYS read from TMDL files first
- NEVER add spaces to PascalCase column names in DAX queries
- Use DAX logical operators (`||`, `&&`) NOT SQL operators (`OR`, `AND`)

**Design Rule**: Column names in TMDL and DAX follow the naming conventions defined in `.github/references/naming-conventions.md`. The agent must ALWAYS introspect the actual model structure before generating any DAX queries to prevent object reference errors.
````
