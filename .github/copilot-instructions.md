````instructions
# Global Copilot Instructions — AI Semantic Layer Builder

This repository contains a **GitHub Copilot Custom Agent** (`@semantic-modeler`) that builds Power BI semantic models in **PBIP format with TMDL** from functional specifications.

## Repository Structure

```
aisemanticlayer/
├── .github/
│   ├── copilot-instructions.md       ← You are here (global instructions)
│   ├── agents/
│   │   └── semantic-modeler.agent.md ← Main invocable agent (@semantic-modeler)
│   ├── skills/                        ← Step-by-step execution skills (6 files)
│   ├── references/                    ← TMDL, DAX, PBIP reference material (7 files)
│   │   ├── tmdl-syntax-reference.md
│   │   ├── naming-conventions.md
│   │   ├── pbip-folder-structure.md
│   │   ├── dax-patterns.md
│   │   ├── relationship-patterns.md   ← NEW: Advanced relationship patterns
│   │   ├── dax-optimization-framework.md ← NEW: DAX performance optimization
│   │   └── bpa-rules-reference.md     ← NEW: Best Practice Analyzer rules
│   └── prompts/                       ← Reusable prompt files
├── PBIP/                              ← Power BI project output folder
│   ├── <ProjectName>.SemanticModel/
│   │   └── definition/                ← TMDL files go here
│   │       ├── model.tmdl
│   │       ├── database.tmdl
│   │       ├── tables/
│   │       ├── relationships.tmdl
│   │       └── expressions.tmdl
│   ├── <ProjectName>.Report/          ← Empty report canvas (user-created)
│   └── data/                          ← Generated CSV mock data
└── .venv/                             ← Python virtual environment (gitignored)
```

## Key Rules

1. **Language**: All agent conversations follow the user's language. All generated code, TMDL, DAX, and file content **must be in English**.
2. **Methodology**: Strictly follow Kimball dimensional modeling (Star Schema). Reference `.github/references/` for syntax and patterns.
3. **Anti-Hallucination**: Before generating any TMDL or DAX code, the agent MUST verify syntax against Microsoft official documentation using the `microsoft_docs_search` or `microsoft_docs_fetch` MCP tools.
4. **TMDL Accuracy**: TMDL is whitespace-sensitive (tab-indented, YAML-like). Any indentation error causes parsing failures in Power BI Desktop. Always cross-reference with `.github/references/tmdl-syntax-reference.md`.
5. **Naming Conventions**: Follow `.github/references/naming-conventions.md` strictly for all tables, columns, measures, and relationships.
6. **Relationship Design**: Reference `.github/references/relationship-patterns.md` for role-playing dimensions, many-to-many, self-referencing hierarchies.
7. **DAX Optimization**: Apply `.github/references/dax-optimization-framework.md` for performance-optimized measures.
8. **BPA Compliance**: Apply `.github/references/bpa-rules-reference.md` Best Practice Analyzer rules for production-quality models (preventive guidelines + detective validation).

## How to Use the Agent

Invoke the custom agent in GitHub Copilot Chat:

```
@semantic-modeler PBIP/spec_sales_overview_fytd.md
```

The agent will execute a 6-step workflow with mandatory approval gates, leveraging skills and references for anti-hallucination.

## What's New

**Recent Additions** (Priority: HIGH):
- ✅ **relationship-patterns.md**: Advanced patterns for role-playing dimensions, many-to-many, self-referencing hierarchies, troubleshooting
- ✅ **dax-optimization-framework.md**: Comprehensive DAX performance optimization framework with testing patterns
- ✅ **bpa-rules-reference.md**: Best Practice Analyzer rules (27+ rules, 6 categories) for preventive guidelines and detective validation

These references enhance the agent's capability to handle complex scenarios and generate production-quality optimized DAX code following industry-standard best practices from Tabular Editor.
````
