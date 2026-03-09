# Skill: Quality Review & TMDL Validation

## Purpose
Perform a comprehensive cross-check of ALL generated artifacts before the user opens the PBIP project in Power BI Desktop. Catching errors here prevents time-consuming troubleshooting outside VS Code.

## Prerequisites — MANDATORY
Before starting the review:
1. **Read** `.github/references/tmdl-syntax-reference.md` for syntax validation rules.
2. **Read** `.github/references/naming-conventions.md` for naming compliance.
3. If (and ONLY if) RLS is implemented, **read** `.github/references/security-rls-best-practices.md` and validate the model follows least-privilege, explicit allow/deny behavior, and auditable security logic.
4. **Load** all generated TMDL files from `<ProjectName>/PBIP/<ProjectName>.SemanticModel/definition/`.
5. **Load** the CSV mock data files from `<ProjectName>/data/`.
6. **Verify** any uncertain TMDL syntax using `microsoft_docs_search` or `microsoft_docs_fetch` MCP tool.

## Review Checklist

### 1. TMDL Syntax Validation
- [ ] **Indentation**: ALL TMDL files use TAB characters (not spaces). Verify by checking for `\t`.
- [ ] **Root-level objects**: `table`, `relationship`, `expression`, `model`, `database` have NO indentation.
- [ ] **Properties**: Indented ONE tab from their parent object.
- [ ] **Multi-line expressions**: Indented TWO tabs from the parent object declaration.
- [ ] **Blank lines**: Used to separate sibling objects (measures, columns) but NOT between a property and its parent.
- [ ] **Colons** (`:`) used for non-expression properties only.
- [ ] **Equals** (`=`) used for expressions/default properties only.
- [ ] **Object names**: Enclosed in single quotes if containing spaces, dots, equals, colons, or single quotes.
- [ ] **No trailing whitespace** on any line.
- [ ] **No mixed indentation** (tabs and spaces mixed on same line).

### 2. Structural Integrity
- [ ] `model.tmdl` contains `ref table` entries for ALL tables defined in `tables/` folder.
- [ ] **CRITICAL**: `model.tmdl` contains `defaultPowerBIDataSourceVersion: powerBI_V3` property. Without it, Power BI Desktop throws *"A data model with version 3 of metadata is required"* and all refresh operations fail.
- [ ] `database.tmdl` exists with correct `compatibilityLevel` matching Power BI Desktop version (1600 for December 2025, 1567 for September 2024).
- [ ] `relationships.tmdl` contains entries for ALL FK-PK relationships.
- [ ] One `.tmdl` file per table exists in `tables/` folder.
- [ ] `_Measures.tmdl` table file exists with at least one measure.
- [ ] `expressions.tmdl` exists if shared M parameters are used.

### 3. Relationship Validation
For EACH relationship in `relationships.tmdl`:
- [ ] `fromColumn` references an existing column in an existing Fact table.
- [ ] `toColumn` references an existing column in an existing Dimension table (must have `isKey`).
- [ ] Relationship is **single-directional** (unless explicitly bi-directional for RLS).
- [ ] **CRITICAL**: `securityFilteringBehavior: oneDirection` for ALL relationships (unless specific RLS requirement). Max 1 `bothDirections` per table.
- [ ] `crossFilteringBehavior: oneDirection` for standard Star Schema (Dim → Fact).
- [ ] No **duplicate relationships** between the same column pairs.
- [ ] No **circular dependency** chains (A→B→C→A).
- [ ] FK columns in Fact tables are marked `isHidden`.
- [ ] **CRITICAL: No ambiguous paths** — For EACH pair of tables, verify there is ONLY ONE active relationship path. Common ambiguities:
  - [ ] Fact_Sales → Dim_Country (direct) AND Fact_Sales → Dim_Customer → Dim_Country (indirect)
  - [ ] Fact_Sales → Dim_Area (direct) AND Fact_Sales → Dim_Customer → Dim_Country → Dim_Area (indirect)
  - [ ] Fact_Sales → Dim_Industry (direct) AND Fact_Sales → Dim_Customer → Dim_Industry (indirect)
  - **Fix**: Remove redundant direct relationships from fact tables. Keep only the path through the most granular dimension.

### 4. Data Type Consistency
For EACH column across all tables:
- [ ] `dataType` matches expected type (int64 for keys, decimal for amounts, string for text, dateTime for dates).
- [ ] `sourceColumn` matches the actual column name in the CSV file header.
- [ ] `summarizeBy` is set to `none` for keys and non-additive columns.
- [ ] `formatString` is appropriate (currency formats for amounts, percentage for ratios, date format for dates).

### 5. DAX Measures Validation
For EACH measure in `_Measures.tmdl`:
- [ ] Uses **VAR / RETURN** pattern for non-trivial measures.
- [ ] **VAR names do NOT use DAX reserved keywords** (`Variance`, `Status`, `Value`, `Date`, `Time`, `Year`, `Month`, `Day`, `Table`, `Column`, `Measure`, `Name`, `Count`, `Sum`, `Average`, `Min`, `Max`, `Result`, `Error`, `Number`, `Text`, `True`, `False`, `Blank`, `If`, `And`, `Or`, `Not`, `In`, `Order`, `Filter`). Use descriptive prefixes instead (e.g., `SalesBudgetVariance`, `BudgetStatusValue`).
- [ ] Uses **DIVIDE()** for ALL division operations (no `/` operator).
- [ ] ALL referenced columns exist in the model with correct `Table[Column]` syntax.
- [ ] ALL referenced measures exist and are not self-referential or circular.
- [ ] Time intelligence functions reference `Dim_Date[Date]` (the Date Table column).
- [ ] `displayFolder` is assigned to each measure.
- [ ] `lineageTag` is present and is a valid GUID.
- [ ] `formatString` is appropriate for the measure type.

### 6. Dim_Date Validation
- [ ] `Dim_Date` table has `isKey` on the `DateKey` column.
- [ ] A `Date` column with `dataType: dateTime` exists.
- [ ] Fiscal year/month/quarter columns are present if fiscal periods are referenced in specs.
- [ ] The generated date range covers the full reporting period.

### 7. CSV Mock Data Validation
- [ ] ALL CSV files exist in `<ProjectName>/data/` folder.
- [ ] Files are comma-delimited and UTF-8 encoded.
- [ ] Column names in CSV headers EXACTLY match `sourceColumn` values in TMDL.
- [ ] ALL FK values in Fact table CSVs exist as PK values in corresponding Dimension CSVs (referential integrity).
- [ ] No NULL values in PK or FK columns.
- [ ] Numeric fields contain valid decimal numbers (no text in numeric columns).
- [ ] Date fields use a consistent, parseable format.

### 8. Naming Convention Compliance
- [ ] Fact table names: `Fact_<BusinessProcess>` PascalCase.
- [ ] Dimension table names: `Dim_<Entity>` PascalCase.
- [ ] Measures table: `_Measures`.
- [ ] Key columns: `<Entity>Key` PascalCase.
- [ ] Attribute columns: PascalCase with descriptive names.
- [ ] Measure names: Descriptive, following patterns in naming-conventions.md.
- [ ] CSV file names: lowercase with underscores (e.g., `fact_sales.csv`, `dim_date.csv`).
- [ ] TMDL file names: PascalCase matching table name (e.g., `Fact_Sales.tmdl`, `Dim_Date.tmdl`).

### 9. Partition Expression Validation
For EACH table's partition:
- [ ] M expression uses valid Power Query syntax.
- [ ] `File.Contents()` path points to correct CSV file location.
- [ ] `Columns` count in `Csv.Document` matches actual CSV column count.
- [ ] `Encoding` is `65001` (UTF-8).
- [ ] `Table.PromoteHeaders` is used to read CSV headers.
- [ ] `Table.TransformColumnTypes` maps types correctly (Int64.Type for integers, type number for decimals, type text for strings, type datetime for dates).

### 10. RLS Validation (if applicable)
- [ ] RLS role files exist in `roles/` subfolder.
- [ ] `tablePermission` filter expressions reference ONLY Dimension tables (never Fact tables directly).
- [ ] Filter expressions use valid DAX syntax.
- [ ] RLS logic does NOT have overly permissive fallbacks (e.g., `TRUE()` for unknown users). Prefer explicit deny-by-default behavior.
- [ ] Bi-directional cross-filtering is enabled on relationships filtered by RLS roles.

### 11. BPA Rules Validation (Detective Quality Assurance)

**Purpose**: Validate ALL generated TMDL and DAX code against Tabular Editor Best Practice Analyzer rules. This is the final quality gate before user opens PBIP in Power BI Desktop.

**Reference**: `.github/references/bpa-rules-reference.md` contains all 27+ BPA rules with examples.

#### 11.1 DAX Expression Rules (Error Severity)

**Critical Rules - ZERO TOLERANCE**:

- [ ] **DAX_FULLY_QUALIFIED_COLUMNS**: ALL column references in DAX use `Table[Column]` syntax (no unqualified `[Column]`)
  - **Validation**: Grep search all measures for `\[[A-Za-z]+\]` pattern without table prefix
  - **Fix**: Replace `[Column]` with `Table[Column]`

- [ ] **DAX_DIVISION_COLUMNS**: ALL division operations use `DIVIDE()` function, NO `/` operator
  - **Validation**: Grep search all measures for `/` operator in expressions
  - **Fix**: Replace `[Numerator] / [Denominator]` with `DIVIDE([Numerator], [Denominator], 0)`

- [ ] **AVOID_RESERVED_KEYWORDS**: Object names do NOT use DAX/SQL reserved keywords (Date, Table, Value, Column, Year, etc.)
  - **Validation**: Check table/column names against reserved keyword list
  - **Fix**: Add prefix/suffix (e.g., `Date` → `Dim_Date`, `Value` → `DateValue`)

- [ ] **DAX_VAR_RESERVED_KEYWORDS**: VAR names inside DAX expressions do NOT use reserved keywords (`Variance`, `Status`, `Value`, `Date`, `Time`, `Year`, `Month`, `Day`, `Table`, `Column`, etc.)
  - **Validation**: For each `VAR <name>` in measure expressions, check `<name>` against forbidden keyword list
  - **Fix**: Use descriptive prefixed names (e.g., `VAR Variance` → `VAR SalesBudgetVariance`, `VAR Status` → `VAR BudgetStatusValue`)

#### 11.2 DAX Expression Rules (Warning Severity)

- [ ] **DAX_UNQUALIFIED_MEASURES**: Measure references are unqualified (use `[Measure]` not `Table[Measure]`)
  - **Validation**: Grep search for `\[_Measures\]\.` or `Table\.` before measure names
  - **Fix**: Remove table prefix from measure references

- [ ] **DAX_TODO_COMMENTS**: No TODO/FIXME/HACK comments in measures
  - **Validation**: Grep search for `TODO|FIXME|HACK|TEMPORARY` in measure expressions
  - **Fix**: Complete implementation or remove comment if measure is production-ready

#### 11.3 Formatting Rules (Warning Severity)

- [ ] **OBJECTS_WITH_NO_FORMAT_STRING_COLUMNS**: Numeric columns have `formatString` property
  - **Validation**: Check all columns with `dataType: decimal|double|int64` (except hidden FKs)
  - **Fix**: Add `formatString: "$#,##0.00"` for currency, `"0.00%"` for percentage, `"#,##0"` for integers

- [ ] **OBJECTS_WITH_NO_FORMAT_STRING_MEASURES**: ALL measures have `formatString` property
  - **Validation**: Check all measures in `_Measures.tmdl`
  - **Fix**: Add appropriate `formatString` based on measure type

#### 11.4 Metadata Rules (Error/Warning Severity)

- [ ] **AVOID_FLOAT_DATATYPE** (Error): Numeric columns use `dataType: decimal` NOT `double`
  - **Validation**: Grep search for `dataType: double` in all table TMDL files
  - **Fix**: Replace `double` with `decimal`

- [ ] **SUMMARIZEBY_SHOULD_BE_NONE** (Warning): ALL columns have `summarizeBy: none`
  - **Validation**: Check all columns (dimension attributes and fact measures)
  - **Fix**: Add or change to `summarizeBy: none`

- [ ] **DISABLE_ATTRIBUTE_HIERARCHIES** (Info): Foreign key columns have `isAvailableInMDX: false`
  - **Validation**: Check all FK columns in fact tables
  - **Fix**: Add `isAvailableInMDX: false`

#### 11.5 Model Layout Rules (Warning Severity)

- [ ] **HIDE_FOREIGN_KEY_COLUMNS** (Warning): ALL FK columns in fact tables have `isHidden: true`
  - **Validation**: Check all columns with `Key` suffix in fact tables
  - **Fix**: Add `isHidden: true`

- [ ] **ORGANIZE_MEASURES_IN_DISPLAY_FOLDERS** (Info): Measures have `displayFolder` property
  - **Validation**: Check all measures in `_Measures.tmdl`
  - **Fix**: Add `displayFolder: "Category\\Subcategory"` for logical grouping

- [ ] **PROVIDE_DESCRIPTIONS_FOR_MEASURES** (Info): Complex measures (time intelligence, statistical) have `description` property
  - **Validation**: Check measures with CALCULATE, DATESYTD, SAMEPERIODLASTYEAR, etc.
  - **Fix**: Add `description: "Business logic explanation"`

- [ ] **ORGANIZE_COLUMNS_IN_DISPLAY_FOLDERS** (Info): Dimension tables with 15+ columns use `displayFolder` for attribute grouping
  - **Validation**: Count columns per dimension table
  - **Fix**: Add `displayFolder: "Geography"` for location attributes, `"Demographics"` for personal attributes

#### 11.6 Naming Convention Rules

- [ ] **TABLE_NAME_MUST_START_WITH_PREFIX** (Warning): Tables use `Fact_`, `Dim_`, `Bridge_` prefixes
  - **Validation**: Check all table names in `model.tmdl` ref entries
  - **Fix**: Rename tables with correct prefix

- [ ] **USE_PASCALCASE_FOR_OBJECTS** (Info): Tables, columns, measures use PascalCase (no spaces, no snake_case)
  - **Validation**: Check for `column_name` or `columnname` patterns
  - **Fix**: Convert to `ColumnName` PascalCase

- [ ] **DATE_COLUMN_NAMED_DATE** (Warning): Date dimension has column named `Date` (dataType: dateTime)
  - **Validation**: Check `Dim_Date.tmdl` for column `Date`
  - **Fix**: Rename date column to `Date` or add new column

- [ ] **AVOID_PLURAL_TABLE_NAMES** (Info): Tables use singular names (`Dim_Product` not `Dim_Products`)
  - **Validation**: Check for table names ending in `s` (except `Sales`, `Transactions`)
  - **Fix**: Rename to singular form

- [ ] **MEASURE_NAMING_DESCRIPTIVE** (Info): Measure names are descriptive business terms, not abbreviations
  - **Validation**: Check for measures like `SA`, `M1`, `Calc_Rev`
  - **Fix**: Rename to `Total Sales`, `Revenue`, etc.

#### 11.7 Performance Rules (Warning Severity)

- [ ] **AVOID_CALCULATED_COLUMNS_IN_LARGE_FACTS** (Warning): Large fact tables (> 1M rows) have NO calculated columns
  - **Validation**: Check fact table TMDL files for column `expression:` property
  - **Fix**: Convert calculated column to measure

- [ ] **MINIMIZE_BIDIRECTIONAL_RELATIONSHIPS** (Warning): Relationships are single-directional unless RLS required
  - **Validation**: Grep search `relationships.tmdl` for `crossFilteringBehavior: bothDirections`
  - **Fix**: Change to `crossFilteringBehavior: oneDirection` or document RLS justification

- [ ] **AVOID_MEASURES_REFERENCING_CALCULATED_COLUMNS** (Warning): Measures reference physical columns, not calculated columns
  - **Validation**: Cross-check measure column references against calculated columns in tables
  - **Fix**: Rewrite measure to calculate directly from physical columns

- [ ] **USE_VARIABLES_TO_AVOID_RECALCULATION** (Info): Measures use VAR to store repeated expressions
  - **Validation**: Check for repeated expressions in IF, SWITCH, arithmetic operations
  - **Fix**: Extract to VAR before RETURN

#### 11.8 BPA Validation Output Format

Present BPA validation results as a **severity-graded report**:

```
## BPA Rules Validation Report

### Severity Summary
- ❌ **Errors (3)**: 0 found — ZERO TOLERANCE, must fix before deployment
- ⚠️ **Warnings (2)**: 2 found — Should fix, impacts performance/maintainability
- ℹ️ **Info (1)**: 5 found — Recommendations, optional for MVP

### Error Findings (Critical)
| Rule ID | File | Object | Issue | Status |
|---------|------|--------|-------|--------|
| — | — | — | No errors found | ✅ PASS |

### Warning Findings (Important)
| Rule ID | File | Object | Issue | Fix |
|---------|------|--------|-------|-----|
| OBJECTS_WITH_NO_FORMAT_STRING_MEASURES | tables/_Measures.tmdl | 'Sales YTD' | Missing formatString | Add `formatString: "$#,##0.00"` |
| HIDE_FOREIGN_KEY_COLUMNS | tables/Fact_Sales.tmdl | ProductKey | Missing isHidden | Add `isHidden: true` |

### Info Findings (Recommendations)
| Rule ID | File | Object | Issue | Recommendation |
|---------|------|--------|-------|----------------|
| PROVIDE_DESCRIPTIONS_FOR_MEASURES | tables/_Measures.tmdl | 'Sales SPLY' | No description | Add tooltip for time intelligence |
| ORGANIZE_MEASURES_IN_DISPLAY_FOLDERS | tables/_Measures.tmdl | 'Total Quantity' | No displayFolder | Group in "Sales Metrics" |
| ... | ... | ... | ... | ... |

### Overall BPA Status: ✅ PASS / ⚠️ WARNINGS / ❌ FAIL

**Decision**: 
- ✅ PASS → User can open PBIP in Power BI Desktop
- ⚠️ WARNINGS → Fix critical warnings, document exceptions
- ❌ FAIL → STOP, fix all errors before proceeding
```

#### 11.9 BPA Auto-Fix Workflow

If BPA validation finds issues:

1. **Errors (Severity 3)**: MANDATORY fixes. Propose corrections and apply automatically upon approval.
2. **Warnings (Severity 2)**: Present list, ask user: "Fix all?" or "Fix selected?" or "Document exceptions?"
3. **Info (Severity 1)**: Present recommendations, user can defer to post-MVP.

**Auto-Fix Example**:
```
Found 3 issues:
1. [ERROR] DAX_DIVISION_COLUMNS in measure 'Profit Margin' — use DIVIDE()
2. [WARNING] HIDE_FOREIGN_KEY_COLUMNS in Fact_Sales.ProductKey — add isHidden
3. [INFO] ORGANIZE_MEASURES_IN_DISPLAY_FOLDERS in measure 'Total Sales' — add displayFolder

Proposed fixes:
- File: tables/_Measures.tmdl
  Line: measure 'Profit Margin'
  Change: SUM(Fact_Sales[Profit]) / SUM(Fact_Sales[Revenue])
  To: DIVIDE(SUM(Fact_Sales[Profit]), SUM(Fact_Sales[Revenue]), 0)

Apply all fixes? (yes/no/selective)
```

#### 11.10 BPA Validation Checklist

**Prerequisites**:
- [ ] Read `.github/references/bpa-rules-reference.md` (all 27+ rules)
- [ ] Load all TMDL files (database, model, tables, relationships, measures)
- [ ] Load all CSV mock data files

**Validation Sequence**:
1. Run Error (3) validations → STOP if any found, fix before proceeding
2. Run Warning (2) validations → Document or fix
3. Run Info (1) validations → Present recommendations
4. Generate severity-graded report
5. Propose auto-fixes for errors and critical warnings
6. Apply fixes upon user approval

**MCP Verification** (for uncertain rules):
```
microsoft_docs_search("Power BI DIVIDE function DAX best practices")
microsoft_docs_search("TMDL formatString syntax examples")
microsoft_docs_fetch(<url-from-search-results>)
```

---

## Output Format

Present the review as a structured report:

```
## Quality Review Report

### Overall Status: ✅ PASS / ⚠️ WARNINGS / ❌ FAIL

| # | Category | Status | Details |
|---|----------|--------|---------|
| 1 | TMDL Syntax | ✅ | All files use correct TAB indentation |
| 2 | Structural Integrity | ✅ | All required files present |
| 3 | Relationships | ✅ | 5/5 relationships validated |
| 4 | Data Types | ✅ | All types consistent |
| 5 | DAX Measures | ✅ | 12/12 measures validated |
| 6 | Dim_Date | ✅ | Fiscal year configured correctly |
| 7 | CSV Data | ✅ | Referential integrity verified |
| 8 | Naming Conventions | ✅ | All objects compliant |
| 9 | Partition Expressions | ✅ | All M expressions valid |
| 10 | RLS | N/A | No RLS requirements |
```

### Error Detail
For each ⚠️ or ❌ finding, provide:
1. **File**: Which TMDL file contains the issue.
2. **Location**: Object name and approximate line.
3. **Issue**: Clear description of what is wrong.
4. **Fix**: Exact corrected TMDL/DAX code snippet.

## Auto-Fix Proposal
If errors are found:
1. Present each error with the proposed correction.
2. Ask the user for permission to apply all fixes.
3. Apply fixes directly to the TMDL files upon approval.

## Artifact Checkpointing (MANDATORY)

**BEFORE presenting results to the user**, the agent MUST:

1. **SAVE** the quality review report to disk as `<ProjectName>/tests/quality_review.md`.
   - The file must contain the full review checklist with PASS/WARNING/FAIL status.
   - Include BPA severity-graded report.
   - Include all error details and proposed fixes.
2. **UPDATE** `<ProjectName>/workflow_state.json`:
   - Set `pendingStep` to Step 06 completed.
   - Add artifact path `<ProjectName>/tests/quality_review.md`.
3. **CONFIRM** to the user that the artifact file has been saved.

## Context Flushing Rule

When starting this step, the agent MUST:
- **READ** `<ProjectName>/workflow_state.json` to verify Steps 03-05 are completed.
- **READ** TMDL files and CSV files from disk (NOT from chat memory).
- **DO NOT** rely on chat history for any data from previous steps.

**Present the complete report and await user validation.**