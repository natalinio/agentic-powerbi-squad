# Skill: Report Quality Validation (Final Reconciliation)

## Purpose
Perform a comprehensive validation and reconciliation between the report design blueprint (`report_blueprint.json`) and the physical PBIR report files generated in Step 9. This is the final quality gate before the user opens the PBIP project in Power BI Desktop.

## Prerequisites — MANDATORY
Before starting report quality validation:
1. ✅ Step 9 completed and approved — PBIR page and visual files exist in `<ProjectName>/PBIP/<ProjectName>.Report/definition/pages/`.
2. ✅ Report blueprint exists — `<ProjectName>/spec/report_blueprint.json` on disk.
3. ✅ Semantic Model exists — `<ProjectName>/PBIP/<ProjectName>.SemanticModel/definition/` contains valid TMDL files.

## Context Flushing Rule

When starting this step, the agent MUST:
- **READ** `<ProjectName>/workflow_state.json` to verify Steps 01-09 are completed.
- **READ** `<ProjectName>/spec/report_blueprint.json` from disk.
- **READ** all `page.json` and `visual.json` files from the PBIR report definition.
- **READ** TMDL files from disk for field cross-referencing.
- **DO NOT** rely on chat history for any data from previous steps.

---

## Step 10 Procedure

### 10.1 Build Validation Context

Load the three data sources needed for cross-validation:

#### A) Model Object Registry
Read all TMDL files and build the registry (same as Steps 7 and 9):
- **Tables**: All table names
- **Columns**: All column names per table (PascalCase)
- **Measures**: All measure names from `_Measures.tmdl` (natural language with spaces)
- **Relationships**: All relationship pairs

#### B) Blueprint Registry
Parse `report_blueprint.json` and extract:
- **Pages**: List of `pageId` values and their `displayName`
- **Visuals per page**: Count of visuals per page, including slicers
- **Fields used**: All measure names and column references across all visuals
- **Visual types**: List of visual types used

#### C) PBIR File Registry
Scan the PBIR report definition folder and extract:
- **Page folders**: List of folders in `pages/`
- **Visual folders per page**: Count of visual subfolders in each page's `visuals/` folder
- **Visual JSON content**: Parse each `visual.json` to extract:
  - `Entity` references (table names)
  - `Property` references (column/measure names)
  - `visualType` values
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

#### Output Format for Field Validation

```
## Field Cross-Reference Validation

| # | Page | Visual | Entity | Property | Type | Status | Details |
|---|------|--------|--------|----------|------|--------|---------|
| 1 | Page1 | visual_01 | _Measures | Sales Amount FYTD | Measure | ✅ PASS | Exists in _Measures.tmdl |
| 2 | Page1 | visual_02 | Dim_Date | FiscalYear | Column | ✅ PASS | Exists in Dim_Date.tmdl |
| 3 | Page1 | visual_03 | Dim_Area | Area Name | Column | ❌ FAIL | Column not found. Did you mean 'AreaName'? |
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

---

## Validation Gate — STOP

Before declaring Step 10 complete:
- [ ] Validation report has been saved to `<ProjectName>/tests/report_validation_execution.md`
- [ ] All FAIL items have been resolved (or acknowledged by the user)
- [ ] Overall status is ✅ PASS or ⚠️ WARNINGS (with user acceptance)

---

## Artifact Checkpointing (MANDATORY)

**BEFORE presenting results to the user**, the agent MUST:

1. **SAVE** the validation report to `<ProjectName>/tests/report_validation_execution.md`.
2. **UPDATE** `<ProjectName>/workflow_state.json`:
   - Set `pendingStep` to Step 10 completed.
   - Add artifact path `<ProjectName>/tests/report_validation_execution.md`.
   - If this is the final step, set `currentStep: 10` and mark workflow as complete.
3. **CONFIRM** to the user that the validation report has been saved.

Present the validation report summary and **STOP here**. Await user approval. Upon approval, the workflow is **COMPLETE**.

---

## Final Deliverable

After Step 10 approval, the user has a fully validated PBIP project:
- ✅ Semantic Model (TMDL) — validated in Steps 3-7
- ✅ Report Design (Blueprint) — validated in Step 8
- ✅ Report Implementation (PBIR) — generated in Step 9
- ✅ Report Quality — validated in Step 10

The user can now open `<ProjectName>/PBIP/<ProjectName>.pbip` in Power BI Desktop, refresh data, and use the report.
