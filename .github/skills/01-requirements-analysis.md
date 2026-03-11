---
name: powerbi-requirements-analysis
description: Extract KPIs, dimensions, grain, and constraints from functional specifications.
---

# Skill: Requirements Analysis and Specification Extraction

## Input Handling

- **Markdown files** (`.md`): Read the file content directly.
- **Word documents** (`.docx`): Ask the user to paste or convert the content. Do NOT attempt binary parsing.
- Detect the input language (Italian or English) and communicate in that language throughout the session.

## Step Scope & I/O Gate Alignment (MANDATORY)

- This skill is step-scoped: execute it only for **Step 01**. Do NOT preload Step 08/09/10 (or any other future-step skill) unless explicitly needed for a blocking clarification.
- Input gate: verify prerequisite artifacts from previous completed step(s) exist and are readable.
- Output gate: before completion, verify `<ProjectName>/spec/requirements_summary.md` exists, is non-empty, and is registered in `workflow_state.json`.

## Extraction Procedure

When analyzing the functional specifications document, perform the following extractions systematically:

### 1. Identify Metrics (Facts / KPIs)
- List ALL required quantitative metrics with their specific aggregation rules (SUM, AVERAGE, COUNT, etc.).
- For each KPI, specify:
  - **Name** (in English for code, original language for descriptions)
  - **Aggregation type** (additive, semi-additive, non-additive)
  - **Formula or calculation logic** (if provided)
  - **Format** (currency, percentage, integer, etc.)
  - **Time intelligence requirements** (YTD, PY, MoM, etc.)

### 2. Identify Dimensions
- List ALL qualitative attributes used for filtering or grouping.
- For each dimension, identify:
  - **Attributes** (columns for filtering/grouping)
  - **Hierarchies** (drill-down paths, e.g., Area → Country → Customer)
  - **Cardinality estimate** (high/medium/low)
  - **Whether it's shared** across multiple fact tables (conformed dimension per Kimball)

### 3. Determine Granularity (Grain)
- Explicitly state the **lowest level of detail** (grain) for each Fact table.
- Example: "One row per sales transaction per day per customer" vs. "One row per month per area".
- If the specs are ambiguous about grain, **flag it and ask the user**.

### 4. Extract RLS Rules
- Map out any **Row-Level Security** requirements:
  - Which user roles exist
  - Which dimension tables each role filters
  - The DAX filter expression logic
- If (and ONLY if) RLS is in scope, reference `.github/references/security-rls-best-practices.md` to ensure:
  - Least privilege and explicit allow/deny behavior is specified
  - The identity mechanism is clear (e.g., `USERNAME()`, `USERPRINCIPALNAME()`, `CUSTOMDATA()`)
  - RLS is designed to filter Dimensions (with propagation to Facts) rather than filtering Facts directly
- Context optimization: if RLS is NOT mentioned/required, do NOT load security references.
- If no RLS is mentioned, explicitly note: "No RLS requirements detected."

### 5. Identify Fact Table Separation
- Determine if facts should be in **separate tables** (e.g., Sales Fact vs. Budget Fact).
- Identify the grain of each fact table independently.
- Note any many-to-many relationships that may require bridge tables.

## Validation Gate

Before declaring Step 1 complete, check:
- [ ] All KPIs have clear aggregation rules
- [ ] All dimensions have defined attributes
- [ ] Grain is explicitly defined for each fact table
- [ ] Data types are specified or inferrable for all fields
- [ ] RLS requirements are documented (or explicitly none)
- [ ] Time/period calculation requirements are clear (calendar/period boundary definitions, ordering, label semantics)

If ANY of these are missing or ambiguous, **flag them explicitly and ask the user** before proceeding.

## Critical Clarification Gate (MANDATORY)

For this workflow, the following clarifications are **blocking** and cannot remain implicit:

1. Period and calendar semantics used by cumulative or comparative calculations.
2. Numeric threshold/classification semantics for status-driven KPIs (including inclusive/exclusive boundaries).
3. Grain reconciliation semantics when metrics compare entities at different detail levels.

Required behavior:

- If one or more critical clarifications are unresolved, DO NOT accept Step 1 completion.
- If the user replies with generic approval (for example: "Proceed") without answering, ask targeted follow-up questions and keep the step pending.
- Only proceed when each critical clarification has either:
  - a concrete user answer, or
  - an explicit user-approved assumption recorded in `workflow_state.json` decision tracking.

## Output Format

Present the analysis as a structured table:

```
### KPIs Identified
| # | KPI Name | Aggregation | Formula | Format | Time Intelligence |
|---|----------|------------|---------|--------|-------------------|

### Dimensions Identified
| # | Dimension | Key Attributes | Hierarchy | Shared? |
|---|-----------|---------------|-----------|---------|

### Fact Tables
| # | Fact Table | Grain | Related Dimensions |
|---|-----------|-------|-------------------|

### RLS Rules
| Role | Filtered Dimension | Filter Logic |
|------|-------------------|-------------|
```

## Artifact Checkpointing (MANDATORY)

**BEFORE presenting results to the user**, the agent MUST:

1. **SAVE** the full requirements analysis to disk as `<ProjectName>/spec/requirements_summary.md`.
   - The file must contain ALL tables from the Output Format above (KPIs, Dimensions, Fact Tables, RLS Rules).
   - Include any flagged ambiguities or missing requirements at the end of the file.
2. **UPDATE** `<ProjectName>/workflow_state.json`:
   - Set `pendingStep` to Step 01 completed.
   - Add artifact path `<ProjectName>/spec/requirements_summary.md`.
3. **CONFIRM** to the user that the artifact file has been saved.

## Context Flushing Rule

When starting this step, the agent MUST:
- **READ** `<ProjectName>/workflow_state.json` to verify Step 00 is completed.
- **READ** any existing artifacts from previous steps from disk (NOT from chat memory).
- **DO NOT** rely on chat history for any data from previous steps.

**STOP here. Await user validation before proceeding to Step 2.**