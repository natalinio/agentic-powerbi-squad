# Build Semantic Model from Specifications

You are starting the **AI Semantic Layer Builder** workflow using the `@semantic-modeler` custom agent.

## Instructions

1. Read the functional specifications document provided by the user (Markdown or pasted text).
2. **Preliminary check**: Verify that a PBIP canvas exists in the root folder (PBIP/*.pbip). If not, STOP and instruct the user to create it first.
3. Follow the 6-step workflow defined in `.github/agents/semantic-modeler.agent.md` **exactly and sequentially**.
4. At each step, use the corresponding skill from `.github/skills/`.
5. **STOP after each step** and wait for user approval before proceeding.
6. Reference `.github/references/` for TMDL syntax, naming conventions, DAX patterns, and PBIP structure.
7. Use MCP tools (`microsoft_docs_search`, `microsoft_docs_fetch`, `microsoft_code_sample_search`) to verify TMDL and DAX syntax before generating code.

## Quick Start

Please provide your functional specifications document. You can:
- Reference a `.md` file in the `PBIP/` folder (e.g., `PBIP/spec_sales_overview_fytd.md`)
- Paste the spec content directly in the chat
- Provide a Word document converted to text

I will analyze the specifications and begin **Step 1: Requirements Analysis**.
