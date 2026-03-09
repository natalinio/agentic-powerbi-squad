# AI Coding Agent Instructions

## Purpose
This document defines operational rules for AI coding assistants (Copilot, ChatGPT, Cursor, etc.) working in this repository.

Goals:
- Reduce token consumption
- Maintain architectural consistency
- Keep security and compliance constraints explicit
- Accelerate safe feature development and bug fixing

---

# 1. Global Response Rules

## Language
All generated code comments and docstrings must be in English.

## Chat Output Constraints
To reduce noise and token usage, AI assistants must:
- Avoid pasting full files
- Avoid large code blocks
- Prefer patch-style guidance
- Use minimal snippets (<= 20 lines) only when strictly necessary

Preferred format:
- File: `<path>`
- Section: `<logical area>`
- Change: `<what and why>`

## Secrets & Security
The AI must never output credentials, API keys, tokens, secrets, or connection strings.

Use placeholders only:
- `<TENANT_ID>`
- `<CLIENT_ID>`
- `<CLIENT_SECRET>`
- `<KEY_VAULT_NAME>`

## Human Review Rule
AI-generated output is advisory and must:
- Be reviewed by a human
- Pass repository CI/CD checks
- Never be deployed directly without validation

---

# 2. AI Implementation Playbook

Use this structure in implementation responses.
- 1 Scope: State in-scope and out-of-scope items.
- 2 Impacted Components: List affected files with full repository paths.
- 3 Change Description: Explain logic, responsibilities, and interactions.
- 4 Edge Cases: Always review data quality, null handling, performance, compatibility, and security.
- 5 Verification Plan: Propose unit/integration checks, pipeline validation, and data validation.

---

# 3. Development Fast-Track (Copilot)

For faster and safer delivery, ask Copilot with this minimal context:
- Goal: feature or bug objective
- Scope: allowed folders/files
- Constraints: security/performance/backward compatibility
- Validation: tests or commands to run

Recommended request template:
1. "Update `<file>` to `<goal>`"
2. "Keep changes minimal and aligned with existing patterns"
3. "Include edge-case handling for null/empty/error paths"
4. "Run targeted validation and summarize results"

---

# 4. Common Pitfalls to Avoid

- Hardcoding credentials, secrets, or environment values
- Bypassing metadata-driven configuration
- Adding logic to deprecated Function App V1 endpoints
- Using unversioned or duplicated Databricks logic
- Producing large chat code dumps instead of patch-focused guidance

---

# 5. Expected AI Output Quality

A good AI response should:
- Reference repository paths clearly
- Respect architecture and security constraints
- Keep output concise and implementation-ready
- Surface assumptions and validation steps explicitly
- Preserve human decision authority