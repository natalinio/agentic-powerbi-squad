# Skill: Report Design (Layout, UX, Navigation)

## Purpose
Design the Power BI report experience (pages, layout, visuals, interactions, navigation) based on:
- the functional specification (`<ProjectName>/spec/*.md`), and
- the finalized semantic model (`<ProjectName>/PBIP/<ProjectName>.SemanticModel/definition/`).

This step produces a **design blueprint** only. It does NOT implement PBIP report artifacts.

## Context Window Management (CRITICAL)
- Load only the minimum needed inputs for this step: the spec + the semantic model object names.
- Use `.github/references/report-design-visualization-best-practices.md` **only when needed** (e.g., choosing a chart type, defining cross-filtering rules, accessibility checks). Do NOT preload it if the spec already dictates the visual choices.
- NEVER invent measure/field names: always read them from TMDL.

## Prerequisites — MANDATORY
Before starting report design:
1. ✅ The semantic model exists and is valid (Steps 3–7 completed).
2. ✅ The specification describes report goals (audience, questions, KPIs, navigation expectations). If missing, ask targeted questions and STOP.
3. ✅ Model introspection is possible by reading TMDL files.

## Step 8 Procedure

### 8.1 Inputs to Read
1. Functional spec: `<ProjectName>/spec/<spec>.md`
2. Semantic model TMDL:
   - `<ProjectName>/PBIP/<ProjectName>.SemanticModel/definition/model.tmdl`
   - `<ProjectName>/PBIP/<ProjectName>.SemanticModel/definition/tables/*.tmdl`
   - `<ProjectName>/PBIP/<ProjectName>.SemanticModel/definition/relationships.tmdl`

### 8.2 Build a Visual Design Field Registry (MANDATORY)
Create an internal registry of report-usable objects by reading TMDL (same anti-hallucination principle as Step 7):
- **Measures**: from `_Measures.tmdl` (exact display names)
- **Date table**: confirm the Date table and main Date column
- **Dimensions**: user-facing attributes (prefer non-hidden descriptive columns)
- **Facts**: avoid exposing technical keys; prefer measures

**CRITICAL RULES**:
- NEVER guess object names.
- If the spec uses business labels that don't map 1:1 to model objects, ask clarifying questions and STOP.

### 8.3 Derive Report Information Architecture
From the spec, define:
- Primary KPIs (what must be seen immediately)
- Secondary analysis (trends, comparisons, breakdowns)
- Tertiary controls (slicers/filters/navigation)

Default to the simplest structure that satisfies the spec:
- If the spec is summary-only → single-page layout.
- If the spec includes drill-down needs → summary page + detail page.

### 8.4 Produce the Report Design Blueprint (OUTPUT)
Provide the design as a structured blueprint with:

#### A) Page List
For each page:
- **PageName** (English)
- **Goal / questions answered**
- **Target audience/persona** (if stated)
- **Slicers/filters** (fields from the registry)
- **Visuals** (max 6–8 per page unless spec requires otherwise), each with:
  - Visual type (card, line, clustered bar, matrix, etc.)
  - Measures used
  - Axis/breakdown fields
  - Sorting + default granularity (e.g., Month)
  - Tooltip / drillthrough usage (only if required)
- **Interactions**: cross-filter vs highlight decisions

#### B) Navigation & UX
- Navigation model (tabs/buttons/bookmarks) **only if specified**
- Drillthrough pages (only if required)
- Accessibility notes (contrast, labels, avoiding color-only encoding)

#### C) Performance Guardrails
- Avoid high-cardinality slicers unless required
- Avoid too many visuals on a page
- Prefer measures over implicit aggregations

### 8.5 Validation Gate (STOP)
Before declaring Step 8 complete:
- [ ] Every measure/field referenced exists in the Visual Design Field Registry
- [ ] Report pages/visuals match the spec (no invented extra pages)
- [ ] Interactions are defined (or explicitly “default interactions”)
- [ ] Accessibility and performance considerations are stated

Present the blueprint and **STOP here**. Await user approval before any implementation step.

## Reference (load only if needed)
- `.github/references/report-design-visualization-best-practices.md`
