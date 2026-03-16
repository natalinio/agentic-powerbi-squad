---
name: powerbi-report-quality-validation
description: Verify PBIR syntax and semantic consistency between report visuals and the semantic model.
---

# Skill: Report Quality Validation (Final Reconciliation)

## Purpose
Provide a structured verification methodology for the PBIR artifacts generated in Step 9, ensuring:
- **syntactic correctness** of PBIR files (`page.json`, `visual.json`, schema, structure), and
- **semantic coherence** between visual field bindings and the semantic model (TMDL tables, columns, measures, relationships).

This step is the final quality gate before opening the PBIP project in Power BI Desktop.

## Prerequisites — MANDATORY
Before starting report quality validation:
1. ✅ Step 9 completed and approved — PBIR page and visual files exist in `<ProjectName>/PBIP/<ProjectName>.Report/definition/pages/`.
2. ✅ Report blueprint exists — `<ProjectName>/spec/report_blueprint.json` on disk.
3. ✅ Semantic Model exists — `<ProjectName>/PBIP/<ProjectName>.SemanticModel/definition/` contains valid TMDL files.

## Step Contract

> Governance: `.github/references/workflow-core.md` — context flushing, checkpointing, and stop/approval gate apply automatically.

| | |
|---|---|
| **Reads** | `workflow_state.json` (verify Steps 01-09 completed), `spec/report_blueprint.json`, all TMDL files, PBIR page/visual files |
| **Writes** | `<ProjectName>/tests/report_validation_execution.md` |

> **Performance Rule**: Load the full PBIR payload into context only when strictly necessary. Run `.github/scripts/validate_pbir_report.py <ProjectName>` for bulk validation first; inspect raw PBIR files individually only for targeted remediation.

**In scope**: PBIR syntax and structural validation, visual binding cross-check, blueprint coherence, validation report with PASS/WARNING/FAIL outcomes.
**Out of scope**: redesigning report UX, adding visuals/pages, changing business requirements, broad model redesign.

## Validation Methodology (MANDATORY)

Apply validation in this exact order to reduce false positives and speed root-cause identification:

0. **Automated Bulk Validation Layer**
   - Run the shared validator script first to generate deterministic summary artifacts on disk.
   - Use the generated Markdown and JSON summaries as the primary inspection surface.
   - Fall back to direct PBIR file reads only for targeted diagnosis.

1. **Structural & Syntax Layer**
   - Validate file presence, JSON parseability, required schema properties, and folder hierarchy.
   - Stop early on blocking syntax errors before semantic checks.

2. **Semantic Binding Layer**
   - Validate every `Entity` and `Property` used in PBIR against TMDL object registry.
   - Validate filter bindings and multi-table visuals against active relationship reachability.

3. **Blueprint Consistency Layer**
   - Validate that generated pages/visuals/types/counts align with Step 8 blueprint intent.
   - Flag mismatches as implementation drift (WARNING/FAIL based on impact).

4. **Readiness Layer**
   - Consolidate issues with severity and actionable remediation order.
   - Output deterministic report so results are reproducible across runs.

---

## Step 10 Procedure

### 10.0 Run the Shared PBIR Validator (MANDATORY)

Run the repository-wide validator:

```powershell
python .github/scripts/validate_pbir_report.py <ProjectName>
```

Expected outputs:
- `<ProjectName>/tests/report_validation_execution.md`
- `<ProjectName>/tests/report_validation_execution.json`

The agent MUST treat these generated files as the primary validation artifacts for Step 10.

If the validator fails to run:
- report the execution error,
- inspect only the minimum required PBIR files to diagnose the failure,
- and avoid opening large portions of the report definition unless necessary.

### 10.1 Build Validation Context

Load the three data sources needed for cross-validation:

#### A) Model Object Registry
Read all TMDL files and build the registry (same as Steps 7 and 9):
- **Tables**: All table names
- **Columns**: All column names per table (PascalCase)
- **Measures**: All measure names from `_Measures.tmdl` (natural language with spaces)
- **Relationships**: All relationship pairs
- **Field parameter metadata**: detect parameter tables, visible parameter columns, hidden metadata columns, and allowed target objects
- **Context compatibility metadata**: for measure-parameter visuals, collect allowed context dimensions from the blueprint and compare them with model reachability

#### B) Blueprint Registry
Parse `report_blueprint.json` and extract:
- **Pages**: List of `pageId` values and their `displayName`
- **Visuals per page**: Count of visuals per page, including slicers
- **Fields used**: All measure names and column references across all visuals
- **Visual types**: List of visual types used

#### C) PBIR File Registry
Use the validator outputs as the primary PBIR registry and inspect raw PBIR files only when needed. Extract or confirm:
- **Page folders**: List of folders in `pages/`
- **Visual folders per page**: Count of visual subfolders in each page's `visuals/` folder
- **Visual JSON content**: Parse each `visual.json` to extract:
  - `Entity` references (table names)
  - `Property` references (column/measure names)
  - `visualType` values
   - `queryState.<Role>.fieldParameters[]` references (when present)
   - `filterConfig.filters[].field` references (when present)
  - Title text

---

### 10.2 Cross-Reference Field Validation (CRITICAL)

**Objective**: Verify that every `query` or `select` in the `visual.json` files points to a column or measure that actually exists in the TMDL semantic model.

#### Checks to Perform

For EACH `visual.json` file:

1. **Entity Validation**: Every `SourceRef.Entity` value MUST match a table name in the TMDL model.
   - **PASS**: Entity `"Dim_Date"` exists as `table Dim_Date` in TMDL.
   - **FAIL**: Entity `"DateDimension"` does not match any TMDL table name.

2. **Property Validation (Columns)**: Every `Column.Property` value MUST match a column declared in the corresponding TMDL table file.
   - **PASS**: Property `"FiscalYear"` exists as `column FiscalYear` in `Dim_Date.tmdl`.
   - **FAIL**: Property `"Fiscal Year"` (with space) does not match PascalCase column name.

3. **Property Validation (Measures)**: Every `Measure.Property` value MUST match a measure declared in `_Measures.tmdl`.
   - **PASS**: Property `"Sales Amount FYTD"` exists as `measure 'Sales Amount FYTD'` in `_Measures.tmdl`.
   - **FAIL**: Property `"SalesAmountFYTD"` does not match the natural language measure name.

4. **Relationship Reachability**: For visuals that combine fields from multiple tables, verify that the tables are connected through active relationships in `relationships.tmdl`.
   - **WARNING**: Visual uses fields from `Dim_Area` and `Fact_Sales`, but no direct or indirect relationship exists.

5. **FilterConfig Validation**: When `filterConfig` is present, validate `filterConfig.filters[].field` using the same Entity/Property rules above.
   - **PASS**: `filterConfig` references only valid columns/measures.
   - **FAIL**: `filterConfig` contains unknown field references.

6. **Field Parameter Binding Validation**: When a visual uses `queryState.<Role>.fieldParameters[]`, validate that:
   - the referenced parameter table exists in TMDL,
   - the parameter display column exists,
   - the target role also contains at least one concrete projection compatible with the current selection baseline,
   - and the parameter table metadata on the model side is present.

7. **Field Parameter Default Selection Validation**: When a field-parameter slicer defines `visual.objects.general[].properties.filter`, validate that the filter targets the hidden object-reference column and that the literal value matches one of the allowed `NAMEOF(...)` entries from the parameter table.

8. **Measure Parameter Context Validation**: When a visual uses a measure parameter, validate that every non-parameter grouping field in the same visual is semantically safe for all selectable measures:
   - the grouping dimension is reachable through active relationships from every fact table or measure lineage involved,
   - the dimension is declared in the blueprint as an allowed context dimension,
   - and the resulting filter context does not become partial or misleading for one or more selectable measures.

#### Output Format for Field Validation

```
## Field Cross-Reference Validation

| # | Page | Visual | Entity | Property | Type | Status | Details |
|---|------|--------|--------|----------|------|--------|---------|
| 1 | Page1 | visual_01 | _Measures | Sales Amount FYTD | Measure | ✅ PASS | Exists in _Measures.tmdl |
| 2 | Page1 | visual_02 | Dim_Date | FiscalYear | Column | ✅ PASS | Exists in Dim_Date.tmdl |
| 3 | Page1 | visual_03 | Dim_Area | Area Name | Column | ❌ FAIL | Column not found. Did you mean 'AreaName'? |
| 4 | Page2 | visual_01 | Dimension | Dimension | FieldParameter | ✅ PASS | Parameter table and display column exist |
```

---

### 10.3 Blueprint Compliance Validation

**Objective**: Verify that the number of pages and visuals created in PBIR matches exactly what was defined in `report_blueprint.json`.

#### Checks to Perform

1. **Page Count**: Number of page folders in PBIR = Number of pages in blueprint.
   - **PASS**: Blueprint defines 2 pages, PBIR has 2 page folders.
   - **FAIL**: Blueprint defines 3 pages, PBIR has 2 page folders — `Page3` missing.

2. **Page Names**: Each page's `displayName` in `page.json` matches the blueprint's `displayName`.
   - **WARNING**: Blueprint says `"Sales Overview"`, `page.json` says `"Sales_Overview"`.

3. **Visual Count per Page**: Number of visual folders per page = Number of visuals + slicers defined in blueprint for that page.
   - **PASS**: Blueprint defines 4 visuals + 2 slicers for Page1, PBIR has 6 visual folders.
   - **FAIL**: Blueprint defines 5 visuals for Page2, PBIR has 3 visual folders — 2 missing.

4. **Visual Types**: Each visual's `visualType` in `visual.json` matches the expected type from the blueprint (after mapping).
   - **PASS**: Blueprint says `"card"`, PBIR says `"cardVisual"`.
   - **PASS**: Blueprint says `"clusteredBarChart"`, PBIR says `"clusteredBarChart"`.
   - **FAIL**: Blueprint says `"line"`, PBIR says `"clusteredColumnChart"`.

5. **Measure Coverage**: Every measure referenced in the blueprint's `visuals[].measures[]` appears in at least one `visual.json`.
   - **WARNING**: Measure `"Budget Amount FYTD"` is in the blueprint but not found in any visual.

#### Output Format for Blueprint Compliance

```
## Blueprint Compliance Report

| # | Check | Expected | Actual | Status | Details |
|---|-------|----------|--------|--------|---------|
| 1 | Page Count | 2 | 2 | ✅ PASS | |
| 2 | Page1 Visual Count | 6 | 6 | ✅ PASS | 4 visuals + 2 slicers |
| 3 | Page2 Visual Count | 3 | 3 | ✅ PASS | |
| 4 | Measure Coverage | 12 | 12 | ✅ PASS | All measures mapped |
| 5 | Visual Type Match | All | All | ✅ PASS | |
```

---

### 10.4 Accessibility and Best Practice Validation

**Objective**: Verify basic accessibility and performance best practices.

#### Checks to Perform

1. **Visual Count per Page**:
   - **PASS**: Page has ≤ 8 visuals (including slicers).
   - **WARNING**: Page has 9-12 visuals — may impact performance.
   - **FAIL**: Page has > 12 visuals — will likely cause performance issues.

2. **Title Presence**:
   - **PASS**: Visual title is present either via `visual.visualContainerObjects.title` or handled by default visual caption.
   - **WARNING**: Visual `visual_03` on `Page1` has no explicit custom title configuration.

3. **Slicer Cardinality**:
   - **PASS**: Slicers reference low-cardinality dimension columns (< 100 unique values).
   - **WARNING**: Slicer on `Dim_Customer[CustomerName]` may have high cardinality (100+ values).

4. **Schema URLs**:
   - **PASS**: All JSON files reference valid Microsoft `$schema` URLs.
   - **FAIL**: `page.json` is missing `$schema` property.

5. **Position Validation**:
   - **PASS**: All visuals fit within the page dimensions (width ≤ page width, height ≤ page height).
   - **WARNING**: Visual `visual_05` extends beyond page boundaries.

6. **Duplicate Visual IDs**:
   - **PASS**: No duplicate `name` values within a page.
   - **FAIL**: Two visuals share `name: "visual_01"` on Page1.

#### Output Format for Accessibility/Best Practice

```
## Accessibility & Best Practice Report

| # | Check | Page | Status | Details |
|---|-------|------|--------|---------|
| 1 | Visual count ≤ 8 | Page1 | ✅ PASS | 6 visuals |
| 2 | Visual count ≤ 8 | Page2 | ✅ PASS | 3 visuals |
| 3 | All titles present | Page1 | ✅ PASS | 6/6 have titles |
| 4 | No high-cardinality slicers | Page1 | ⚠️ WARNING | Slicer on CustomerName |
| 5 | Schema URLs valid | All | ✅ PASS | |
| 6 | Positions within bounds | All | ✅ PASS | |
| 7 | No duplicate IDs | All | ✅ PASS | |
```

---

### 10.5 Generate Validation Report

Combine all validation results into a single report file.

**File**: `<ProjectName>/tests/report_validation_execution.md`

**Report Structure**:

```markdown
# Report Quality Validation — <ProjectName>

**Generated**: <ISO 8601 timestamp>
**Blueprint**: <ProjectName>/spec/report_blueprint.json
**Report Path**: <ProjectName>/PBIP/<ProjectName>.Report/definition/

## Overall Status: ✅ PASS / ⚠️ WARNINGS / ❌ FAIL

## Summary
- Pages validated: X/X
- Visuals validated: Y/Y
- Fields cross-referenced: Z/Z
- Warnings: W
- Errors: E

---

## 1. Field Cross-Reference Validation
<table from 10.2>

## 2. Blueprint Compliance
<table from 10.3>

## 3. Accessibility & Best Practices
<table from 10.4>

---

## Recommendations
<List of recommended fixes for any WARNING or FAIL items>

## Conclusion
<Final assessment: Ready for Power BI Desktop / Requires fixes>
```

---

## Error Resolution

If **FAIL** items are found:

1. **Field not found**: Correct the `visual.json` file to use the exact TMDL name. Apply the fix and re-validate.
2. **Missing pages/visuals**: Generate the missing PBIR files by re-running the relevant part of Step 9.
3. **Wrong visual type**: Update the `visualType` in the `visual.json` file.
4. **Schema issues**: Add or correct the `$schema` URL in the affected JSON file.

The agent SHOULD propose auto-fixes for all FAIL items. Upon user approval, apply fixes and re-run validation.

When re-running validation after fixes:
- re-run the shared validator script first,
- compare the new summary against the previous summary,
- and read only the specific PBIR files implicated by any remaining FAIL or WARNING items.

---

## Validation Gate — STOP

Before declaring Step 10 complete:
- [ ] Validation report has been saved to `<ProjectName>/tests/report_validation_execution.md`
- [ ] All FAIL items have been resolved (or acknowledged by the user)
- [ ] Overall status is ✅ PASS or ⚠️ WARNINGS (with user acceptance)

---

**STOP. Save validation report → update `workflow_state.json` (mark workflow complete) → await user approval. Upon approval, the workflow is COMPLETE.**

---

## Final Deliverable

After Step 10 approval, the user has a fully validated PBIP project:
- ✅ Semantic Model (TMDL) — validated in Steps 3-7
- ✅ Report Design (Blueprint) — validated in Step 8
- ✅ Report Implementation (PBIR) — generated in Step 9
- ✅ Report Quality — validated in Step 10

The user can now open `<ProjectName>/PBIP/<ProjectName>.pbip` in Power BI Desktop, refresh data, and use the report.
