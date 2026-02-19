# AI Semantic Layer Generation Platform Constitution

## Core Principles

### I. Compiler, Not Chatbot
The product is a deterministic “Semantic Model Compiler” orchestrated by LLMs: given explicit inputs, it must produce deployable artifacts (TMDL/BIM) plus a QA report. Conversational UX is allowed (e.g., Teams), but the contract is inputs → outputs, not open-ended chat.

### II. Contract-First I/O
All capabilities must be exposed behind a stable, versioned contract:
- Inputs: table schema (DDL/JSON), KPI glossary, mode (Direct Lake/Import), RLS requirements.
- Outputs: proposed star schema, relationships + directions, date dimension strategy, documented DAX measures, deployable TMDL/BIM, validation report.
The contract must support a machine-readable format (JSON) and a human-readable format.

### III. Quality Gates Are Non-Negotiable
No model artifact is “done” unless it passes automated checks at minimum:
- relationship validity (keys, cardinality, filter direction),
- naming convention compliance,
- KPI/DAX coverage against the glossary,
- RLS presence/shape when requested,
- basic model hygiene (required dimensions, date strategy declared).
If checks fail, output must be an explicit failure with actionable diagnostics.

### IV. Minimal, Standardized Architecture (MVP)
Phase 1 targets standardized tabular patterns over breadth:
- star schema by default,
- central date dimension strategy,
- KPI glossary-driven measures,
- optional RLS scaffolding.
Advanced DAX performance tuning, legacy refactoring, dashboard generation, and large-scale change impact analysis are explicitly out of scope for MVP.

### V. Safety, Traceability, and Human Approval
Every generation must be traceable:
- store inputs, prompts/agent decisions (or summaries), and outputs with a correlation id,
- produce a QA report that explains what was validated and what was assumed.
Deployment must be gated: automated generation may prepare artifacts, but a human approval step is required before deploying to a Fabric workspace.

## Constraints (MVP Requirements)

### Scope
- In scope: generating semantic model artifacts from schema + KPI glossary; basic validation; RLS scaffolding; multi-agent orchestration; Teams-based collaboration.
- Out of scope: automatic refactoring of complex legacy models; advanced DAX optimization; automatic dashboards; enterprise-wide impact analysis.

### Technology Boundaries
- Orchestration: Azure AI Studio / Foundry (or equivalent) may be used, but orchestration must remain replaceable (no hard lock-in assumptions in the core compiler).
- Interface: Teams is the primary interface for MVP; core compiler must be runnable headlessly (CI-friendly).

### Security & Compliance
- Do not persist customer data beyond what is necessary for traceability and troubleshooting; prefer redaction/minimization.
- Separate secrets/config from code; never log secrets.
- Treat generated artifacts as code: reviewable, diffable, and suitable for source control.

## Development Workflow

### Definition of Done
- Input/output contract documented.
- Automated quality gates implemented and running in CI.
- Generated artifacts are reproducible for the same inputs (within a defined tolerance for LLM variability; if non-deterministic, the output must include the exact run metadata).
- Human approval step is enforced prior to any deployment action.

### Testing
- Unit tests for parsing, transformation, naming rules, and validators.
- Integration tests for end-to-end generation from a small sample schema + glossary to TMDL/BIM + QA report.
- Regression tests for KPI glossary changes (golden outputs for representative scenarios).

### Versioning
- Version the I/O contract and the KPI glossary schema.
- Breaking changes require a migration note and explicit version bump.

## Governance

### Operational Guardrails
- Multi-agent roles must remain explicit (Architect/Modeler/DAX/Governance/Reviewer) and produce auditable intermediate outputs.
- Reviewer/QA step cannot be bypassed.
- Any “assumption” made by the system must be listed in the QA report.

### Change Control
- Amendments to this constitution require: rationale, impact assessment (MVP vs later phases), and an update to tests/quality gates.

**Version**: 0.1.0 | **Ratified**: 2026-02-19 | **Last Amended**: 2026-02-19
