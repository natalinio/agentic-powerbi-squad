# Build Power BI Project (End-to-End)

You are starting the **Power BI AI Developer** end-to-end workflow using the `@powerbi-AI-developer` custom agent.

This workflow builds a **complete Power BI solution** from a functional specification:
- **Semantic model** (TMDL tables, relationships, DAX measures)
- **Mock data** (Python/Faker CSV generation)
- **Quality assurance** (BPA compliance, functional testing)
- **Report visuals** (PBIR pages, visual.json files)
- **Final validation** (cross-reference PBIR ↔ TMDL ↔ blueprint)

## Instructions

1. Read the functional specifications document provided by the user (Markdown or pasted text).
2. **Preliminary check**: Verify that a PBIP scaffold exists in the project folder (`<ProjectName>/PBIP/<ProjectName>.pbip`, Report + SemanticModel folders). If missing, run **Step 00** (`.github/skills/00-project-initialization.md`) to bootstrap it programmatically.
3. **Prerequisites check**: Verify Python 3.10+ is available and `.venv` exists at repository root. If not, guide setup.
4. Follow the **10-step workflow** defined in `.github/agents/powerbi-AI-developer.agent.md` **exactly and sequentially**:
   - Steps 1-2: Requirements analysis + Logical data model
   - Step 3: Physical TMDL generation
   - Step 4: DAX measures development
   - Step 5: Mock data generation (Python/Faker)
   - Step 6: Quality review (BPA rules)
   - Step 7: Functional testing (automated DAX validation)
   - Step 8: Report design (blueprint JSON)
   - Step 9: Report implementation (PBIR visual generation)
   - Step 10: Report quality validation (final reconciliation)
5. At each step, **read previous artifacts from disk** (not from chat history) and **update `workflow_state.json`** after completion.
6. At each step, use the corresponding skill from `.github/skills/`.
7. **STOP after each step** and wait for user approval before proceeding.
8. Reference `.github/references/` for TMDL syntax, naming conventions, DAX patterns, PBIP structure, PBIR visual templates, and workflow state management.
9. Use `.github/scripts/` universal tools (lineage fix, comment removal, test runner) where required.
10. Use MCP tools (`microsoft_docs_search`, `microsoft_docs_fetch`, `microsoft_code_sample_search`) to verify TMDL/DAX/PBIR syntax before generating code.

## Quick Start

Please provide your functional specifications document. You can:
- Reference a `.md` file in the project spec folder (e.g., `<ProjectName>/spec/spec_sales_overview.md`)
- Paste the spec content directly in the chat
- Provide a Word document converted to text

I will analyze the specifications and begin **Step 1: Requirements Analysis**.
