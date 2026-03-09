# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- 📄 **Step 8: Report Design** skill (`.github/skills/08-report-design.md`) — now outputs `report_blueprint.json` (structured JSON) instead of chat-only text
- 📄 **Step 9: Report Implementation** skill (`.github/skills/09-report-implementation.md`) — generates physical PBIR page/visual files from the blueprint
- 📄 **Step 10: Report Quality Validation** skill (`.github/skills/10-report-quality-validation.md`) — cross-references PBIR files against TMDL model and blueprint
- 📚 **Report design best practices** reference (`.github/references/report-design-visualization-best-practices.md`)
- 📚 **PBIR visual templates** reference (`.github/references/pbir-visual-templates.md`) — validated JSON templates for 8 visual types (card, bar, column, line, matrix, table, slicer, donut)
- 📚 **Workflow state management** reference (`.github/references/workflow-state-management.md`) — disk-based state tracking protocol with `workflow_state.json`
- 🔄 **Disk-based state management**: All steps now persist artifacts to disk and read from disk (not chat history), enabling workflow resumability
- 🔄 **Artifact checkpointing**: Every skill file now includes mandatory checkpointing and context flushing sections

### Changed
- 🤖 **Agent renamed**: `@semantic-modeler` → `@powerbi-AI-developer` (file: `powerbi-AI-developer.agent.md`) — reflects full-stack Power BI role (semantic model + report visuals)
- 🤖 **Project renamed**: "AI Semantic Layer Builder" → "Power BI AI Developer"
- 🤖 **Workflow expanded from 8 to 10 steps** with full report generation and validation
- 📋 **Agent definition** updated with Workflow State Management section, Steps 9-10, and context flushing protocol
- 📋 **All skill files (01-08)** updated with Artifact Checkpointing and Context Flushing Rule sections

### Planned
- Advanced report features (bookmarks, drill-through, conditional formatting)
- Advanced DAX patterns (statistical functions, predictive measures)
- Azure integration (Azure SQL, Azure Data Lake)
- CI/CD pipelines (Azure DevOps, GitHub Actions)

---

## [1.0.0] - 2026-02-23

### Added
- 🤖 **Custom GitHub Copilot Agent** (`@powerbi-AI-developer`) for semantic model and report automation
- 📋 **7-Step Agentic Workflow** with mandatory approval gates:
  1. Requirements Analysis
  2. Logical Data Model (Mermaid ER diagram)
  3. Physical Model & TMDL generation
  4. DAX Development (optimized measures)
  5. Mock Data Generation (Python/Faker)
  6. Quality Review (BPA compliance)
  7. Functional Testing (automated DAX validation)
- 📚 **Comprehensive Reference Files**:
  - `tmdl-syntax-reference.md` — TMDL syntax templates and examples
  - `naming-conventions.md` — Table, column, measure naming rules
  - `pbip-folder-structure.md` — PBIP project structure guide
  - `dax-patterns.md` — Common DAX patterns and best practices
  - `relationship-patterns.md` — Advanced relationship patterns (role-playing, many-to-many, self-referencing)
  - `dax-optimization-framework.md` — Performance optimization framework
  - `bpa-rules-reference.md` — Best Practice Analyzer rules (27+ rules, 6 categories)
- 🛡️ **Anti-Hallucination Protocol**:
  - MCP tools integration (`microsoft_docs_search`, `microsoft_docs_fetch`, `microsoft_code_sample_search`)
  - Syntax verification against official Microsoft documentation
- 🧰 **Universal Python Scripts**:
  - `fix_lineage_tags.py` — GUID lineageTag regeneration (UUID v4)
  - `remove_tmdl_comments.py` — TMDL comment removal (unsupported syntax)
  - `run_tests.py` — Automated DAX test execution engine
- 📁 **Project Folder Structure** template:
  - `PBIP/` — Power BI Project canvas + TMDL definition files
  - `data/` — Generated CSV mock data
  - `scripts/` — Project-specific Python scripts
  - `tests/` — Functional test artifacts (JSON/MD)
  - `spec/` — User specification files
- 🧪 **Automated Functional Testing**:
  - Model introspection (exact column/measure names)
  - Base aggregation tests (cross-validated with CSV)
  - Time intelligence tests (FYTD with dynamic fiscal year parameters)
  - Derived calculation tests (budget variance, profit %)
  - Edge case tests (zero division, BLANK handling)
  - Dimensional filtering tests (relationship propagation)
  - Performance benchmarks
- 📝 **Complete Open-Source Documentation**:
  - README.md — Quick start, architecture, usage guide
  - CONTRIBUTING.md — Contributor guidelines and standards
  - LICENSE — MIT License
  - CODE_OF_CONDUCT.md — Contributor Covenant v2.0
  - PUBLISHING.md — GitHub publication and branch management guide
  - Issue templates (bug report, feature request)
  - Pull request template
- 🌍 **Multilingual Support**:
  - Italian and English communication
  - Code always generated in English (TMDL, DAX, Python)

### Features
- **Kimball Methodology Enforcement**: Star Schema, dimension tables, fact tables, surrogate keys
- **TMDL Accuracy**: Tab-indented, whitespace-sensitive syntax with validation
- **DAX Optimization**: VAR/RETURN pattern, DIVIDE() function, time intelligence functions
- **BPA Compliance**: Preventive guidelines (during generation) + detective validation (during review)
- **Dynamic Fiscal Year Support**: Parameter-driven FYTD calculations with manual date filtering
- **Ambiguous Path Detection**: Prevention of redundant relationships in fact tables
- **LineageTag Safety**: Cryptographically unique UUID v4 GUIDs for all model objects

### Known Limitations
- TMDL comments NOT supported (removed during generation)
- Time intelligence functions (DATESYTD, TOTALYTD) require constant parameters (not dynamic variables)
- Requires Power BI Desktop December 2025 or later (compatibilityLevel 1600)

---

## Version History

| Version | Release Date | Description |
|---------|--------------|-------------|
| [1.0.0] | 2026-02-23 | Initial public release |

---

## Legend

- `Added` — New features
- `Changed` — Changes in existing functionality
- `Deprecated` — Soon-to-be removed features
- `Removed` — Removed features
- `Fixed` — Bug fixes
- `Security` — Vulnerability fixes

---

[Unreleased]: https://github.com/natalinio/aisemanticlayer/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/natalinio/aisemanticlayer/releases/tag/v1.0.0
