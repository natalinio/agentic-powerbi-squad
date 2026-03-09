# Build Semantic Model from Specifications

You are starting the **AI Semantic Layer Builder** workflow using the `@semantic-modeler` custom agent.

## Instructions

1. Read the functional specifications document provided by the user (Markdown or pasted text).
2. **Preliminary check**: Verify that a PBIP scaffold exists in the project folder (`<ProjectName>/PBIP/<ProjectName>.pbip`, Report + SemanticModel folders). If missing, run **Step 00** (`.github/skills/00-project-initialization.md`) to bootstrap it programmatically (do NOT block on Power BI Desktop canvas creation).
3. **Prerequisites check**: Verify Python 3.10+ is available and `.venv` exists at repository root. If not, guide setup.
4. Follow the 8-step workflow defined in `.github/agents/semanti-modeler.agent.md` **exactly and sequentially**.
5. At each step, use the corresponding skill from `.github/skills/`.
6. **STOP after each step** and wait for user approval before proceeding.
7. Reference `.github/references/` for TMDL syntax, naming conventions, DAX patterns, and PBIP structure.
8. Use `.github/scripts/` universal tools (lineage fix, comment removal, test runner) where required.
9. Use MCP tools (`microsoft_docs_search`, `microsoft_docs_fetch`, `microsoft_code_sample_search`) to verify TMDL and DAX syntax before generating code.

## Quick Start

Please provide your functional specifications document. You can:
- Reference a `.md` file in the project spec folder (e.g., `<ProjectName>/spec/spec_sales_overview.md`)
- Paste the spec content directly in the chat
- Provide a Word document converted to text

I will analyze the specifications and begin **Step 1: Requirements Analysis**.
