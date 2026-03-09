# Skill: Functional Testing & Calculation Validation

## Purpose
Execute a comprehensive functional testing suite to validate that ALL DAX measures produce correct, consistent results aligned with business specifications. This phase ensures the semantic model's **logic correctness**, **calculation accuracy**, and **parameter behavior** before production deployment.

## Scope
This skill covers:
1. **Unit Tests**: Validation of individual measure calculations
2. **Integration Tests**: Cross-measure dependencies and relationships
3. **Scenario Tests**: Parameter variations (fiscal year, filters)
4. **Edge Case Tests**: BLANK values, zero divisions, empty filters
5. **Performance Tests**: Query response time validation
6. **Business Rule Tests**: Consistency with functional specifications
7. **Security Tests (if applicable)**: Validation of Row-Level Security behavior per role/user

## Prerequisites — MANDATORY
Before starting the testing phase:
1. ✅ **Model loads successfully** in Power BI Desktop without errors or warnings
2. ✅ **Mock data imported** — All CSV files successfully loaded into tables
3. ✅ **Parameters configured** — `Parameters` table with `ParameterName` and `ParameterValue` columns
4. ✅ **Date table marked** — `Dim_Date` marked as Date Table with `Date` column as key
5. ✅ **Relationships active** — All 9 relationships visible in Model View
6. 📋 **Test plan documented** — Specification file available for expected results comparison

If (and ONLY if) RLS is implemented, also reference `.github/references/security-rls-best-practices.md` to align validation scenarios (least privilege, explicit deny-by-default, auditable rules).

Context optimization: if RLS is NOT implemented, skip this reference entirely.

---

## RLS Testing Addendum (if applicable)

**Goal**: Validate that each RLS role restricts data as expected and does not accidentally grant broader access.

**Minimum manual checks (Power BI Desktop)**:
1. Use **View as** to test each role with representative identities.
2. Validate that restricted users can still see expected totals where permitted (and see blanks/empty results where not permitted).
3. Validate that unexpected/unknown users do NOT get full access (deny-by-default expectation).
4. If bi-directional security propagation is used, validate it is limited to the specific relationships justified by RLS requirements.

---

## Testing Modes

### Mode A: Manual Testing (Interactive)
**Use Case**: User executes tests manually in Power BI Desktop, documents results in `.github/test-results.md`  
**Duration**: ~90 minutes  
**Best for**: Small models (<30 measures), exploratory testing, visual validation  
**See**: "Testing Methodology" section below for detailed test suites

### Mode B: Agent-Assisted Automated Testing (Recommended) 🤖
**Use Case**: Agent analyzes requirements, generates test definitions, executes DAX queries automatically  
**Duration**: ~20 minutes (agent execution) + ~10 minutes (user review)  
**Best for**: Large models (30+ measures), regression testing, CI/CD integration  
**Output Files**:
- `<ProjectName>/tests/tests_definition.json` — Critical test cases definition
- `<ProjectName>/tests/tests_execution.md` — Test results with pass/fail status and recommendations

**Workflow**:
1. **Agent analyzes** functional specifications + generated DAX measures
2. **Agent generates** `tests_definition.json` with critical test cases (formula, expected behavior, validation queries)
3. **User approves** test plan
4. **Agent executes** DAX queries against semantic model (via Python + `pyadomd` connection to local Power BI Desktop Analysis Services)
5. **Agent generates** `tests_execution.md` with results and fix recommendations

**See**: "Agent-Assisted Testing Workflow" section below for detailed steps

---

## Agent-Assisted Testing Workflow (Mode B)

### ⛔ Step B.0: Model Introspection (MANDATORY — MUST EXECUTE FIRST)

**Purpose**: Before generating ANY test definition or DAX query, the agent MUST read the actual TMDL model structure to extract real object names (tables, columns, measures). This prevents test failures caused by incorrect object references.

**Root Cause (Historical Error)**: In previous executions, the agent generated DAX queries using assumed column names with spaces (e.g., `Dim_Area[Area Name]`, `Dim_Customer[Customer Name]`) instead of the actual PascalCase names without spaces defined in the model (e.g., `Dim_Area[AreaName]`, `Dim_Customer[CustomerName]`). This caused 100% of dimensional and derived tests to fail with "Column not found" errors.

**Agent Actions (ALL MANDATORY)**:
1. **List** all TMDL table files: `<ProjectName>/PBIP/<ProjectName>.SemanticModel/definition/tables/*.tmdl`
2. **Read** each table TMDL file and extract:
   - **Table name** (exact `table` declaration)
   - **Column names** (exact `column` declarations — these are the TMDL object names used in DAX)
   - **Column types** (dataType property)
   - **Hidden columns** (isHidden property — FK columns typically hidden)
   - **sourceColumn** values (CSV column mapping)
3. **Read** `_Measures.tmdl` and extract:
   - **Measure names** (exact `measure` declarations — these are the DAX references)
   - **Display folders** (displayFolder property)
   - **Format strings** (formatString property)
4. **Read** `relationships.tmdl` and extract:
   - **Relationship pairs** (fromColumn → toColumn)
   - **Cardinality and direction** (crossFilteringBehavior)
5. **Build Model Object Registry** — Internal lookup table:

```
=== MODEL OBJECT REGISTRY ===

TABLES:
  Dim_Area: columns=[AreaKey, AreaName]
  Dim_Country: columns=[CountryKey, CountryName, AreaKey]
  Dim_Customer: columns=[CustomerKey, CustomerName, CountryKey, IndustryKey]
  Dim_Industry: columns=[IndustryKey, IndustryName]
  Dim_Date: columns=[DateKey, Date, Year, Month, FiscalYear, FiscalMonth, ...]
  Fact_Sales: columns=[SalesKey, DateKey, CustomerKey, SalespersonKey, SalesAmountLC, ...]
  Fact_Budget: columns=[BudgetKey, DateKey, CustomerKey, BudgetAmountLC, ...]
  _Measures: measures=[Sales Amount, Budget Amount, Adjusted Profit, ...]
  Parameters: columns=[ParameterName, ParameterValue]

RELATIONSHIPS:
  Fact_Sales.DateKey → Dim_Date.DateKey
  Fact_Sales.CustomerKey → Dim_Customer.CustomerKey
  ...
```

6. **Validate** all DAX queries in test definitions use ONLY names from this registry

**CRITICAL RULES**:
- ⛔ NEVER assume column names — ALWAYS read from TMDL files
- ⛔ NEVER add spaces to PascalCase column names (e.g., `AreaName` NOT `Area Name`)
- ⛔ Column names in DAX queries (`Table[ColumnName]`) must match EXACTLY the TMDL `column` declaration name
- ⛔ Measure names in DAX queries (`[Measure Name]`) must match EXACTLY the TMDL `measure` declaration name
- ✅ Cross-reference `.github/references/naming-conventions.md` — columns use PascalCase, measures use natural language with spaces

**Output**: Model Object Registry (agent memory — used as source of truth for all subsequent steps)

**STOP** — Do NOT proceed to Step B.1 until Model Object Registry is built.

---

### Step B.1: Requirements & Measures Analysis

**Agent Actions**:
1. **Read** functional specification file (e.g., `<ProjectName>/spec/spec_sales_overview_fytd.md`)
2. **Extract** KPIs, measures, and business rules:
   - Primary KPIs (e.g., "Sales vs Budget FYTD", "Adjusted Profit %")
   - Dimensions (Area, Customer, Industry, Date)
   - Expected behaviors (e.g., "FYTD recalculates with fiscal year parameter")
3. **Read** generated DAX measures from `tables/_Measures.tmdl` (already loaded in Step B.0)
4. **Map** specifications to implemented measures — use Model Object Registry for correct names
5. **Identify** critical test scenarios:
   - Base aggregations (Sales Amount, Budget Amount)
   - Time intelligence with parameters (Sales Amount FYTD)
   - Derived calculations (Sales vs Budget %, Adjusted Profit %)
   - Edge cases (zero division, BLANK handling)
6. **Cross-validate** that all referenced objects exist in Model Object Registry

**Output**: Internal analysis summary (agent memory, not saved to file)

---

### Step B.2: Generate Test Definitions

**Agent Actions**:
1. **Create** folder structure: `<ProjectName>/tests/`
2. **Generate** `tests_definition.json` with critical test cases

**Test Definition Schema**:

⛔ **CRITICAL**: All `daxQuery` values MUST use object names from the **Model Object Registry** (Step B.0). 
Column names in DAX references (`Table[Column]`) MUST match the exact TMDL `column` declaration name (PascalCase, NO spaces).
Measure names in DAX references (`[Measure Name]`) MUST match the exact TMDL `measure` declaration name (natural language with spaces).

**Example — Correct vs Incorrect DAX references**:
- ✅ `Dim_Area[AreaName]` — matches TMDL: `column AreaName`
- ❌ `Dim_Area[Area Name]` — WRONG: spaces added to column name, will cause "Column not found" error
- ✅ `Dim_Customer[CustomerName]` — matches TMDL: `column CustomerName`
- ❌ `Dim_Customer[Customer Name]` — WRONG: spaces added
- ✅ `[Sales Amount FYTD]` — matches TMDL: `measure 'Sales Amount FYTD'`
- ✅ `[Adjusted Profit %]` — matches TMDL: `measure 'Adjusted Profit %'`

**Rule**: Column names are PascalCase (no spaces). Measure names use natural language (with spaces). NEVER confuse the two.

```json
{
  "projectName": "<FROM MODEL>",
  "modelVersion": "1.0.0",
  "generatedDate": "<CURRENT_DATE>",
  "modelObjectRegistry": {
    "NOTE": "All table/column/measure names below MUST be read from actual TMDL files in Step B.0",
    "tables": ["<read from TMDL>"],
    "columns": {"<TableName>": ["<read from TMDL column declarations>"]},
    "measures": ["<read from _Measures.tmdl measure declarations>"]
  },
  "testSuites": [
    {
      "suiteId": "TS01",
      "suiteName": "Base Aggregations",
      "priority": "HIGH",
      "tests": [
        {
          "testId": "T01.01",
          "testName": "Sales Amount Total",
          "measureName": "Sales Amount",
          "testType": "Unit Test",
          "description": "Verify Sales Amount equals SUM of corresponding fact column",
          "daxQuery": "EVALUATE { [Sales Amount] }",
          "expectedBehavior": "Returns numeric value matching CSV total",
          "validationMethod": "Compare with CSV source column total",
          "passThreshold": "Difference < 0.01 (rounding tolerance)"
        }
      ]
    },
    {
      "suiteId": "TS02",
      "suiteName": "Time Intelligence with Dynamic Parameters",
      "priority": "CRITICAL",
      "tests": [
        {
          "testId": "T02.01",
          "testName": "Sales Amount FYTD - Calendar Year",
          "measureName": "Sales Amount FYTD",
          "testType": "Integration Test",
          "description": "Verify FYTD calculation with FY Start = January",
          "daxQuery": "EVALUATE SUMMARIZECOLUMNS(<Dim_Date column from registry>, \"Sales FYTD\", [Sales Amount FYTD], \"Sales\", [Sales Amount])",
          "NOTE": "Replace <Dim_Date column> with actual column name from Model Object Registry (e.g., Dim_Date[FiscalMonth])"
        }
      ]
    },
    {
      "suiteId": "TS03",
      "suiteName": "Derived Calculations & Percentages",
      "priority": "HIGH",
      "tests": [
        {
          "testId": "T03.01",
          "testName": "Budget Variance by Dimension",
          "measureName": "Sales vs Budget",
          "testType": "Integration Test",
          "description": "Verify variance = Sales FYTD - Budget FYTD grouped by dimension",
          "daxQuery": "EVALUATE SUMMARIZECOLUMNS(<dimension column from registry>, \"Sales FYTD\", [Sales Amount FYTD], \"Budget FYTD\", [Budget Amount FYTD], \"Variance\", [Sales vs Budget])",
          "NOTE": "Replace <dimension column> with actual column name from Model Object Registry (e.g., Dim_Area[AreaName])"
        }
      ]
    },
    {
      "suiteId": "TS04",
      "suiteName": "Edge Cases & Error Handling",
      "priority": "MEDIUM",
      "tests": [
        {
          "testId": "T04.01",
          "testName": "Zero Division Handling",
          "measureName": "Adjusted Profit %",
          "testType": "Edge Case Test",
          "description": "Verify measure returns BLANK when Sales Amount = 0",
          "daxQuery": "EVALUATE FILTER(SUMMARIZECOLUMNS(<customer_name_column from registry>, \"Sales\", [Sales Amount], \"Profit %\", [Adjusted Profit %]), [Sales] = 0)",
          "NOTE": "Replace <customer_name_column> with actual column name from Model Object Registry (e.g., Dim_Customer[CustomerName])"
        }
      ]
    }
  ]
}
```

**File Location**: `<ProjectName>/tests/tests_definition.json`

**Agent outputs**: 
- **Console message**: "Test definition file created with X test cases (Y CRITICAL, Z HIGH priority)"
- **User prompt**: "Review tests_definition.json and approve to proceed with automated execution"

**STOP** — Await user approval before Step B.3

---

### Step B.3: Automated Test Execution

**Prerequisites**:
- ✅ User approved test definition
- ✅ **Power BI Desktop is OPEN** with PBIP project loaded
- ✅ Model loaded successfully (no errors)

**Agent Actions**:
1. **Detect** local Analysis Services workspace:
   - Windows: Check `$env:LOCALAPPDATA\Microsoft\Power BI Desktop\AnalysisServicesWorkspaces\`
   - Identify active workspace port (e.g., `localhost:12345`)
2. **Generate** Python test execution script: `<ProjectName>/tests/run_tests.py`

   **NOTE**: A universal test runner is available at `.github/scripts/run_tests.py`. The agent should reference this universal tool instead of generating a new script for each project. Invoke it with:
   ```powershell
   python .github/scripts/run_tests.py <ProjectName> --port <port> --verbose
   ```
3. **Execute** DAX queries via Python `pyadomd` library:
   ```python
   import pyodbc
   import json
   import pandas as pd
   from datetime import datetime
   
   # Load test definitions
   with open('tests_definition.json', 'r') as f:
       test_plan = json.load(f)
   
   # Connect to local Power BI Desktop Analysis Services
   conn_str = "Provider=MSOLAP;Data Source=localhost:12345;Initial Catalog=<ModelName>;"
   conn = pyodbc.connect(conn_str, autocommit=True)
   
   test_results = []
   
   for suite in test_plan['testSuites']:
       for test in suite['tests']:
           try:
               # Execute DAX query
               query = test['daxQuery']
               cursor = conn.cursor()
               cursor.execute(query)
               result = cursor.fetchall()
               
               # Log result
               test_results.append({
                   'testId': test['testId'],
                   'testName': test['testName'],
                   'status': 'PASS',  # Preliminary
                   'actualValue': result[0][0] if result else None,
                   'queryExecutionTime': cursor.execution_time
               })
           except Exception as e:
               test_results.append({
                   'testId': test['testId'],
                   'testName': test['testName'],
                   'status': 'FAIL',
                   'error': str(e)
               })
   
   # Save results
   with open('tests_execution_raw.json', 'w') as f:
       json.dump(test_results, f, indent=2)
   ```

4. **Cross-validate** results:
   - For base aggregation tests: Compare DAX query result with CSV totals (using pandas)
   - For FYTD tests: Verify cumulative pattern (current >= previous month)
   - For percentage tests: Verify ratio matches (numerator / denominator)
   - For edge case tests: Verify BLANK/error handling

5. **Assign test status**:
   - ✅ **PASS**: Result matches expected behavior within tolerance
   - ⚠️ **WARNING**: Result correct but performance issue (query > 5 sec)
   - ❌ **FAIL**: Result incorrect or error thrown

6. **Generate** `tests_execution.md` with detailed results and recommendations

**Output File**: `<ProjectName>/tests/tests_execution.md`

---

### Step B.4: Generate Test Execution Report

**Agent Actions**:
1. **Create** markdown report with structured results
2. **Include** for each test:
   - Test ID, Name, Status (✅⚠️❌)
   - Expected vs Actual values
   - Query execution time
   - Fix recommendations (if FAIL)
3. **Summarize** overall test status
4. **Provide** actionable recommendations

**Test Execution Report Template**:

```markdown
# Test Execution Report — Sales Overview FYTD

**Execution Date**: 2026-02-23 15:30:00  
**Model**: SalesOverviewFYTD/PBIP/SalesOverviewFYTD.SemanticModel  
**Test Plan**: tests_definition.json (v1.0.0)  
**Execution Mode**: Automated (Python + pyadomd)  
**Analysis Services**: localhost:12345

---

## Executive Summary

| Suite | Priority | Total Tests | ✅ Passed | ⚠️ Warnings | ❌ Failed | Status |
|---|---|---:|---:|---:|---:|---|
| TS01: Base Aggregations | HIGH | 6 | 6 | 0 | 0 | ✅ PASS |
| TS02: Time Intelligence | CRITICAL | 4 | 3 | 1 | 0 | ⚠️ WARNING |
| TS03: Derived Calculations | HIGH | 3 | 3 | 0 | 0 | ✅ PASS |
| TS04: Edge Cases | MEDIUM | 1 | 1 | 0 | 0 | ✅ PASS |
| **TOTAL** | — | **14** | **13** | **1** | **0** | **⚠️ WARNINGS EXIST** |

**Overall Status**: ⚠️ Model passed all critical tests. 1 performance warning requires attention.

---

## Detailed Test Results

### TS01: Base Aggregations (Priority: HIGH)

#### ✅ T01.01 — Sales Amount Total
- **Measure**: `Sales Amount`
- **DAX Query**: `EVALUATE { [Sales Amount] }`
- **Expected**: Matches SUM of Fact_Sales.csv[Sales Amount LC]
- **Actual Result**: `1,234,567.89`
- **CSV Total**: `1,234,567.89` (verified with pandas)
- **Difference**: `0.00` (within tolerance 0.01)
- **Query Time**: 0.12 sec
- **Status**: ✅ **PASS**

#### ✅ T01.02 — Budget Amount Total
- **Measure**: `Budget Amount`
- **Actual Result**: `1,200,000.00`
- **CSV Total**: `1,200,000.00`
- **Difference**: `0.00`
- **Query Time**: 0.08 sec
- **Status**: ✅ **PASS**

[... additional T01.03-T01.06 results ...]

---

### TS02: Time Intelligence (Priority: CRITICAL)

#### ✅ T02.01 — Sales Amount FYTD - Calendar Year
- **Measure**: `Sales Amount FYTD`
- **Parameter Context**: Fiscal Year Start = `"1"` (January)
- **Date Filter**: Q1 2024 (Jan-Mar)
- **DAX Query**:
  ```dax
  EVALUATE 
  SUMMARIZECOLUMNS(
      Dim_Date[FiscalMonth], 
      "Sales FYTD", [Sales Amount FYTD], 
      "Sales", [Sales Amount]
  ) 
  ORDER BY Dim_Date[FiscalMonth]
  ```
- **Actual Results**:
  | FiscalMonth | Sales | Sales FYTD |
  |---|---:|---:|
  | 2024-01 | 50,000 | 50,000 |
  | 2024-02 | 60,000 | 110,000 |
  | 2024-03 | 55,000 | 165,000 |
- **Validation**: ✅ Cumulative pattern correct (FYTD increases each month)
- **Query Time**: 0.45 sec
- **Status**: ✅ **PASS**

#### ⚠️ T02.02 — Sales Amount FYTD - Fiscal Year (Jul Start)
- **Measure**: `Sales Amount FYTD`
- **Parameter Context**: Fiscal Year Start = `"7"` (July)
- **Date Filter**: Q4 2024 (Oct-Dec)
- **Actual Results**:
  | FiscalMonth | Sales FYTD |
  |---|---:|
  | 2024-10 | 220,000 |
  | 2024-11 | 275,000 |
  | 2024-12 | 340,000 |
- **Validation**: ✅ Fiscal year boundary correct (FY 2025 started Jul 2024)
- **Query Time**: 5.2 sec ⚠️ **EXCEEDS 5 SEC TARGET**
- **Status**: ⚠️ **WARNING** — Result correct, but performance issue detected
- **Recommendation**:
  1. Check if `FILTER(ALL(Dim_Date[Date]))` is causing full table scan
  2. Consider adding calculated column `IsFYTD` in Dim_Date to pre-filter fiscal year boundaries
  3. Review DAX optimization framework: `.github/references/dax-optimization-framework.md`
  4. Alternative: Use `CALCULATETABLE` instead of `FILTER` for better query plan

---

### TS03: Derived Calculations (Priority: HIGH)

#### ✅ T03.01 — Adjusted Profit Percentage
- **Measure**: `Adjusted Profit %`
- **Actual Result**: `0.1555` (15.55%)
- **Manual Validation**: 
  - Sales Amount: 1,234,567.89
  - Adjusted Profit: 192,000.00
  - Expected %: 192,000 / 1,234,567.89 = 0.1555 ✅
- **DIVIDE Function Check**: ✅ Uses `DIVIDE([Adjusted Profit], [Sales Amount], BLANK())`
- **Query Time**: 0.18 sec
- **Status**: ✅ **PASS**

#### ✅ T03.02 — Sales vs Budget Variance
- **Measure**: `Sales vs Budget`
- **Test Context**: By Area
- **Actual Results**:
  | Area | Sales FYTD | Budget FYTD | Variance | Calculated Variance |
  |---|---:|---:|---:|---:|
  | EMEA | 500,000 | 450,000 | 50,000 | 50,000 ✅ |
  | Americas | 400,000 | 420,000 | -20,000 | -20,000 ✅ |
  | APAC | 334,567.89 | 330,000 | 4,567.89 | 4,567.89 ✅ |
- **Validation**: ✅ All variances match: Sales - Budget
- **Query Time**: 0.32 sec
- **Status**: ✅ **PASS**

---

### TS04: Edge Cases (Priority: MEDIUM)

#### ✅ T04.01 — Zero Division Handling
- **Measure**: `Adjusted Profit %`
- **Test Context**: Filter to customers with Sales = 0
- **DAX Query**:
  ```dax
  EVALUATE 
  FILTER(
      SUMMARIZECOLUMNS(
          Dim_Customer[Customer Name], 
          "Sales", [Sales Amount], 
          "Profit %", [Adjusted Profit %]
      ), 
      [Sales] = 0
  )
  ```
- **Actual Result**: 
  | Customer Name | Sales | Profit % |
  |---|---:|---|
  | Customer_ZeroSales | 0.00 | (empty) |
- **Validation**: ✅ No error displayed. Profit % returns BLANK (not #DIV/0!)
- **DIVIDE Check**: ✅ Verified measure uses DIVIDE with BLANK() as 3rd parameter
- **Query Time**: 0.22 sec
- **Status**: ✅ **PASS**

---

## Issues & Recommendations

### ⚠️ Issue #1: Performance Warning on FYTD Fiscal Year Query
- **Test ID**: T02.02
- **Symptom**: Query execution time 5.2 seconds (exceeds 5 sec target)
- **Root Cause**: `FILTER(ALL(Dim_Date[Date]))` likely causing full date table scan for FYTD calculation
- **Impact**: User experience may be slow when changing fiscal year parameter slicer

**Recommended Fix Options**:

**Option A: Add Fiscal YTD Flag Column (Preferred)**
```dax
// In Dim_Date table, add calculated column:
IsFYTD = 
VAR FYStart = VALUE(SELECTEDVALUE(Parameters[ParameterValue], "1"))
VAR CurrentDate = Dim_Date[Date]
VAR FiscalYear = 
    IF(
        MONTH(CurrentDate) >= FYStart, 
        YEAR(CurrentDate), 
        YEAR(CurrentDate) - 1
    )
VAR FYStartDate = DATE(FiscalYear, FYStart, 1)
RETURN
    CurrentDate >= FYStartDate && CurrentDate <= TODAY()
```

Then simplify measure:
```dax
Sales Amount FYTD = 
CALCULATE(
    [Sales Amount],
    Dim_Date[IsFYTD] = TRUE
)
```

**Option B: Optimize FILTER with CALCULATETABLE**
```dax
Sales Amount FYTD = 
VAR CurrentDate = MAX(Dim_Date[Date])
VAR FYStartMonth = VALUE(SELECTEDVALUE(Parameters[ParameterValue], "1"))
VAR FiscalYear = IF(MONTH(CurrentDate) >= FYStartMonth, YEAR(CurrentDate), YEAR(CurrentDate) - 1)
VAR FYStartDate = DATE(FiscalYear, FYStartMonth, 1)
RETURN
    CALCULATE(
        [Sales Amount],
        CALCULATETABLE(  // More efficient than FILTER
            Dim_Date,
            Dim_Date[Date] >= FYStartDate,
            Dim_Date[Date] <= CurrentDate
        )
    )
```

**Option C: Pre-filter with KEEPFILTERS**
```dax
Sales Amount FYTD = 
CALCULATE(
    [Sales Amount],
    KEEPFILTERS(
        Dim_Date[Date] >= [FY Start Date] &&
        Dim_Date[Date] <= MAX(Dim_Date[Date])
    )
)
```

**Next Steps**:
1. Choose optimization approach (recommend Option A for best performance)
2. Update measure in `tables/_Measures.tmdl`
3. Reload model in Power BI Desktop
4. Re-run T02.02 to verify query time < 5 sec

---

## Cross-Validation Summary

### CSV Data Totals (Python pandas validation)

| Source File | Column | Expected Total | Model Total | Match |
|---|---|---:|---:|---|
| Fact_Sales.csv | Sales Amount LC | 1,234,567.89 | 1,234,567.89 | ✅ |
| Fact_Sales.csv | Adjusted Profit LC | 192,000.00 | 192,000.00 | ✅ |
| Fact_Budget.csv | Budget Amount LC | 1,200,000.00 | 1,200,000.00 | ✅ |

**Validation Method**: 
```python
import pandas as pd

# Load CSV files
fact_sales = pd.read_csv('<ProjectName>/data/fact_sales.csv')
fact_budget = pd.read_csv('<ProjectName>/data/fact_budget.csv')

# Calculate totals
sales_total = fact_sales['Sales Amount LC'].sum()
profit_total = fact_sales['Adjusted Profit LC'].sum()
budget_total = fact_budget['Budget Amount LC'].sum()

print(f"CSV Sales Total: {sales_total}")
print(f"CSV Profit Total: {profit_total}")
print(f"CSV Budget Total: {budget_total}")
```

---

## Performance Summary

| Test Category | Avg Query Time | Max Query Time | Performance Status |
|---|---|---|---|
| Base Aggregations | 0.10 sec | 0.12 sec | ✅ Excellent |
| Time Intelligence | 2.83 sec | 5.2 sec | ⚠️ One query slow |
| Derived Calculations | 0.25 sec | 0.32 sec | ✅ Excellent |
| Edge Cases | 0.22 sec | 0.22 sec | ✅ Excellent |

**Overall Performance**: ⚠️ Good with 1 optimization opportunity (FYTD fiscal year query)

---

## Sign-Off

**Test Execution Status**: ⚠️ **PASSED WITH WARNINGS**  
**Critical Tests**: ✅ All passed (13/13 CRITICAL + HIGH priority tests)  
**Warnings**: 1 performance issue (non-blocking)  
**Failures**: 0

**Recommendation**: 
- ✅ **Model is functionally correct** and ready for report development
- ⚠️ **Optimize FYTD measure** to improve performance (optional, non-blocking)
- ✅ Proceed to Step 8: Documentation or begin building report visuals

**Next Actions**:
1. Review performance warning for T02.02
2. Decide if optimization is needed before production
3. If optimization applied, re-run test suite to validate improvement
4. Proceed with confidence — all calculations validated! 🎉

---

## Appendix: Test Artifacts

- **Test Definition**: `<ProjectName>/tests/tests_definition.json`
- **Test Runner**: `.github/scripts/run_tests.py` (universal)
- **Raw Results**: `<ProjectName>/tests/tests_execution_raw.json`
- **This Report**: `<ProjectName>/tests/tests_execution.md`
```

**File Location**: `<ProjectName>/tests/tests_execution.md`

---

### Step B.5: User Review & Action

**Agent presents summary**:
- Overall status (PASS / WARNING / FAIL)
- Count of passed vs failed tests
- List of recommendations

**User actions**:
1. **If all tests PASS**: ✅ Mark Step 7 complete, proceed to documentation
2. **If warnings exist**: Review recommendations, decide if optimization needed
3. **If tests FAIL**: Agent provides fix guidance, user applies changes, re-run tests

---

## Technical Implementation Notes (Mode B)

### Python Dependencies
Agent generates `requirements.txt` for test execution:
```
pandas>=2.0.0
pyodbc>=4.0.39
python-dateutil>=2.8.2
```

### Analysis Services Connection
**Challenge**: Detecting local Power BI Desktop workspace port  
**Solution**: 
1. Scan `$env:LOCALAPPDATA\Microsoft\Power BI Desktop\AnalysisServicesWorkspaces\` for active folders
2. Read `msmdsrv.port.txt` to get port number
3. Connection string: `Provider=MSOLAP;Data Source=localhost:{port};`

**Alternative**: User provides workspace port manually if auto-detection fails

### DAX Query Execution
**Method**: Python `pyodbc` with OLEDB provider for Analysis Services  
**Query Format**: DAX queries using `EVALUATE` statement  
**Result Parsing**: Fetch results as pandas DataFrame for easy validation

### CSV Cross-Validation
**Method**: Load CSV files with `pandas.read_csv()`, calculate expected totals, compare with DAX query results  
**Tolerance**: Allow 0.01 difference for floating-point rounding

---

## Prerequisites

---

## Testing Methodology

### Phase 1: Base Measure Validation (Unit Tests)

**Objective**: Verify that simple aggregation measures calculate correctly without filters.

#### Test Suite 1.1: Sum Aggregations

| Test ID | Measure Name | Test Type | Test Description |
|---|---|---|---|
| T1.1.1 | `Sales Amount` | Unit Test | Verify SUM(Fact_Sales[Sales Amount LC]) returns correct total |
| T1.1.2 | `Budget Amount` | Unit Test | Verify SUM(Fact_Budget[Budget Amount LC]) returns correct total |
| T1.1.3 | `Adjusted Profit` | Unit Test | Verify SUM(Fact_Sales[Adjusted Profit LC]) returns correct total |
| T1.1.4 | `Item Profit` | Unit Test | Verify SUM(Fact_Sales[Item Profit LC]) returns correct total |
| T1.1.5 | `Resource Profit` | Unit Test | Verify SUM(Fact_Sales[Resource Profit LC]) returns correct total |
| T1.1.6 | `Discount Amount` | Unit Test | Verify SUM(Fact_Sales[Discount Amount LC]) returns correct total |

**Execution Method**:
1. In Power BI Desktop, go to **Data** view
2. Select table `_Measures`
3. Click on each measure and verify **value displayed** in the formula bar status area
4. Create a **Card visual** for each measure to verify totals
5. Compare with expected totals from CSV data analysis

**Expected Results**:
- All measures show numeric values (not BLANK or error)
- Values match sum of corresponding CSV column (validate with Python/Excel cross-check)

**Pass Criteria**: ✅ All 6 measures return correct totals within 0.01 tolerance (rounding)

---

#### Test Suite 1.2: Count Aggregations

| Test ID | Measure Name | Test Type | Test Description |
|---|---|---|---|
| T1.2.1 | `# Transactions` | Unit Test | Verify COUNTROWS(Fact_Sales) matches CSV row count |
| T1.2.2 | `# Customers` | Unit Test | Verify DISTINCTCOUNT(CustomerKey) matches unique customers |

**Execution Method**:
1. Create Card visuals for both measures
2. Compare with CSV metadata:
   - `# Transactions`: Count rows in `Fact_Sales.csv`
   - `# Customers`: Count unique values in `CustomerKey` column

**Pass Criteria**: ✅ Both measures match CSV metadata exactly

---

### Phase 2: Time Intelligence Validation

**Objective**: Verify fiscal year-to-date (FYTD) calculations work correctly with dynamic fiscal year parameter.

#### Test Suite 2.1: FYTD Base Measures

| Test ID | Measure Name | Test Type | Test Description |
|---|---|---|---|
| T2.1.1 | `Sales Amount FYTD` | Integration Test | Verify FYTD calculation with FY start = January (calendar year) |
| T2.1.2 | `Sales Amount FYTD` | Integration Test | Verify FYTD calculation with FY start = July (fiscal year) |
| T2.1.3 | `Budget Amount FYTD` | Integration Test | Verify FYTD budget calculation matches sales FYTD logic |
| T2.1.4 | `Adjusted Profit FYTD` | Integration Test | Verify FYTD profit calculation matches sales FYTD logic |

**Execution Method**:

**Test Case 2.1.1: Calendar Year (FY Start = January)**
1. Set `Parameters[ParameterValue]` = `"1"` (January)
2. Add slicer with `Dim_Date[Date]` — select a date in **March 2024**
3. Create Table visual:
   - Rows: `Dim_Date[FiscalMonth]`
   - Values: `Sales Amount`, `Sales Amount FYTD`
4. **Expected behavior**: 
   - `Sales Amount FYTD` for March 2024 = SUM(Jan 2024 + Feb 2024 + Mar 2024)
   - Each month shows cumulative YTD
5. Verify manually:
   ```
   FYTD(March) = SUM(Sales Amount for Jan, Feb, Mar)
   ```

**Test Case 2.1.2: Fiscal Year (FY Start = July)**
1. Change `Parameters[ParameterValue]` = `"7"` (July)
2. Date slicer: Select date in **October 2024**
3. Same Table visual as above
4. **Expected behavior**: 
   - Fiscal Year 2025 starts July 2024
   - `Sales Amount FYTD` for Oct 2024 = SUM(Jul 2024 + Aug 2024 + Sep 2024 + Oct 2024)
5. Verify manually:
   ```
   FY 2025 = Jul 2024 to Jun 2025
   FYTD(Oct 2024) = SUM(Sales Amount for Jul, Aug, Sep, Oct 2024)
   ```

**Pass Criteria**: 
✅ FYTD measures accumulate correctly within fiscal year boundaries  
✅ Changing parameter updates fiscal year logic dynamically  
✅ Values reset at new fiscal year start

---

#### Test Suite 2.2: Year-over-Year (YoY) Measures

| Test ID | Measure Name | Test Type | Test Description |
|---|---|---|---|
| T2.2.1 | `Sales Amount PY` | Integration Test | Verify previous year sales calculation with SAMEPERIODLASTYEAR |
| T2.2.2 | `Sales YOY %` | Integration Test | Verify YoY variance percentage calculation |

**Execution Method**:
1. Create Table visual:
   - Rows: `Dim_Date[FiscalYear]`, `Dim_Date[FiscalMonth]`
   - Values: `Sales Amount`, `Sales Amount PY`, `Sales YOY %`
2. Filter to **2024-2025** fiscal years
3. **Expected behavior**: 
   - For Jan 2025, `Sales Amount PY` = Sales Amount of Jan 2024
   - `Sales YOY %` = (2025 Sales - 2024 Sales) / 2024 Sales
4. Verify manually with CSV data for matching months

**Pass Criteria**: ✅ Previous year values shift correctly, YoY % formula accurate

---

### Phase 3: Percentage & Derived Measures Validation

**Objective**: Verify percentage calculations use DIVIDE() correctly and handle zero/BLANK gracefully.

#### Test Suite 3.1: Profitability Percentages

| Test ID | Measure Name | Test Type | Test Description |
|---|---|---|---|
| T3.1.1 | `Adjusted Profit %` | Unit Test | Verify Adjusted Profit / Sales Amount ratio |
| T3.1.2 | `Item Profit %` | Unit Test | Verify Item Profit / Sales Amount ratio |
| T3.1.3 | `Resource Profit %` | Unit Test | Verify Resource Profit / Sales Amount ratio |
| T3.1.4 | `Item Discount %` | Unit Test | Verify Discount Amount / Sales Amount ratio |

**Execution Method**:
1. Create Matrix visual:
   - Rows: Dimension column from model (e.g., `Dim_Customer[CustomerName]` — verify exact name in TMDL)
   - Values: `Sales Amount`, `Adjusted Profit`, `Adjusted Profit %`
2. **Expected behavior**: 
   - `Adjusted Profit %` = `Adjusted Profit` / `Sales Amount`
   - Format displays as percentage (e.g., 15.50%)
3. Manual validation example:
   ```
   Customer A: Sales = 10,000, Profit = 1,500
   Adjusted Profit % = 1,500 / 10,000 = 0.15 = 15.00%
   ```
4. Test edge case: Filter to customer with ZERO sales
   - **Expected**: `Adjusted Profit %` returns BLANK (not #ERROR or ∞)

**Pass Criteria**: 
✅ All percentage measures show correct ratios  
✅ DIVIDE() handles zero denominator (returns BLANK)  
✅ Format displays as percentage with 2 decimals

---

#### Test Suite 3.2: Budget Variance Measures

| Test ID | Measure Name | Test Type | Test Description |
|---|---|---|---|
| T3.2.1 | `Sales vs Budget` | Integration Test | Verify Sales FYTD - Budget FYTD variance amount |
| T3.2.2 | `Sales vs Budget %` | Integration Test | Verify variance percentage calculation |
| T3.2.3 | `Budget Status` | Integration Test | Verify conditional logic (Above/Close/Below target) |

**Execution Method**:

**Test Case 3.2.1-3.2.2: Variance Calculations**
1. Create Table visual:
   - Rows: Dimension column from model (e.g., `Dim_Area[AreaName]` — verify exact name in TMDL)
   - Values: `Sales Amount FYTD`, `Budget Amount FYTD`, `Sales vs Budget`, `Sales vs Budget %`
2. **Expected behavior**: 
   - `Sales vs Budget` = `Sales Amount FYTD` - `Budget Amount FYTD`
   - `Sales vs Budget %` = Variance / Budget Amount FYTD
3. Manual validation example:
   ```
   Area: EMEA
   Sales FYTD = 500,000
   Budget FYTD = 450,000
   Sales vs Budget = 500,000 - 450,000 = 50,000
   Sales vs Budget % = 50,000 / 450,000 = 0.1111 = 11.11%
   ```

**Test Case 3.2.3: Budget Status Logic**
1. Add column `Budget Status` to table above
2. **Expected behavior** (verify thresholds in measure definition):
   - If `Sales / Budget` >= 1.05 → **"Above target"**
   - If `Sales / Budget` between 0.95 and 1.05 → **"Close to target"**
   - If `Sales / Budget` < 0.95 → **"Below target"**
3. Verify logic with controlled data:
   - Create filter: `Sales vs Budget % > 5%` → Should show "Above target" only

**Pass Criteria**: 
✅ Variance amounts and percentages calculate correctly  
✅ Budget Status text matches specification thresholds  
✅ Conditional logic responds to parameter changes

---

#### Test Suite 3.3: Average Monthly Sales

| Test ID | Measure Name | Test Type | Test Description |
|---|---|---|---|
| T3.3.1 | `Average Monthly Sales` | Integration Test | Verify FYTD sales / month count calculation |

**Execution Method**:
1. Set `Parameters[ParameterValue]` = `"1"` (Calendar year)
2. Date slicer: Select **Q1 2024** (Jan-Mar)
3. Create Card visual with `Average Monthly Sales`
4. **Expected behavior**: 
   - FYTD Sales for Q1 = SUM(Jan + Feb + Mar Sales)
   - Month Count = 3
   - Average = FYTD Sales / 3
5. Manual validation:
   ```
   Jan 2024 Sales: 50,000
   Feb 2024 Sales: 60,000
   Mar 2024 Sales: 55,000
   FYTD Total = 165,000
   Average Monthly = 165,000 / 3 = 55,000
   ```

**Pass Criteria**: ✅ Average calculates correctly, adjusts with fiscal year parameter changes

---

### Phase 4: Relationship & Filter Context Validation

**Objective**: Verify dimensional filtering works correctly through all relationship paths.

#### Test Suite 4.1: Dimensional Drill-Down

| Test ID | Dimension Path | Test Type | Test Description |
|---|---|---|---|
| T4.1.1 | Area → Country → Customer | Integration Test | Verify drill-down hierarchy filters correctly |
| T4.1.2 | Industry → Customer | Integration Test | Verify industry filter propagates to sales |
| T4.1.3 | Salesperson | Integration Test | Verify salesperson filter works correctly |
| T4.1.4 | Date → Fiscal Year/Month | Integration Test | Verify date filters propagate correctly |

**Execution Method**:

**Test Case 4.1.1: Geographic Drill-Down**
1. Create Matrix visual:
   - Rows: Geographic hierarchy from model (e.g., `Dim_Area[AreaName]` → `Dim_Country[CountryName]` → `Dim_Customer[CustomerName]` — verify exact names in TMDL)
   - Values: `Sales Amount`, `Budget Amount`
2. Expand hierarchy levels
3. **Expected behavior**: 
   - Totals at Area level = SUM of all countries in that area
   - Totals at Country level = SUM of all customers in that country
   - No missing or duplicated values
4. Apply slicer filter: Area dimension = "EMEA"
   - **Expected**: Matrix shows ONLY EMEA countries and customers

**Test Case 4.1.2: Industry Filter**
1. Add slicer: Industry dimension column from model (e.g., `Dim_Industry[IndustryName]` — verify exact name in TMDL)
2. Select **"Technology"**
3. **Expected behavior**: 
   - All visuals filter to customers in Technology industry
   - Sales amounts reflect only Technology customers
   - Budget amounts reflect only Technology-related budget records

**Pass Criteria**: 
✅ All dimensional filters propagate correctly to fact tables  
✅ No cross-filter issues (e.g., selecting a country also shows wrong areas)  
✅ Totals aggregate correctly at each hierarchy level

---

#### Test Suite 4.2: Parameter Interaction

| Test ID | Parameter Test | Test Type | Test Description |
|---|---|---|---|
| T4.2.1 | FY Start = 1 (Jan) | Scenario Test | Verify all FYTD measures align to calendar year |
| T4.2.2 | FY Start = 4 (Apr) | Scenario Test | Verify all FYTD measures align to Apr-Mar fiscal year |
| T4.2.3 | FY Start = 7 (Jul) | Scenario Test | Verify all FYTD measures align to Jul-Jun fiscal year |
| T4.2.4 | FY Start = 10 (Oct) | Scenario Test | Verify all FYTD measures align to Oct-Sep fiscal year |

**Execution Method**:
1. Create Table visual:
   - Rows: `Dim_Date[Date]` (date granularity)
   - Values: `Sales Amount FYTD`, `Budget Amount FYTD`, `Average Monthly Sales`
2. Change `Parameters[ParameterValue]` sequentially: `"1"`, `"4"`, `"7"`, `"10"`
3. **Expected behavior** for each parameter change:
   - FYTD measures **recalculate** fiscal year boundaries
   - Values reset at fiscal year start month
   - Average Monthly Sales adjusts month count accordingly

**Example Validation**:
- **FY Start = 7 (July)**:
  - Date: 2024-10-15 (October 2024)
  - Fiscal Year 2025 spans: Jul 2024 - Jun 2025
  - FYTD period: Jul 2024 - Oct 2024 (4 months)
  - `Sales Amount FYTD` = SUM(Jul + Aug + Sep + Oct 2024 sales)
  - `Average Monthly Sales` = FYTD Sales / 4 months

**Pass Criteria**: 
✅ All 4 parameter scenarios produce correct fiscal year logic  
✅ Visual updates automatically when parameter changes  
✅ No hardcoded calendar year assumptions

---

### Phase 5: Edge Case & Error Handling Tests

**Objective**: Verify measures handle edge cases gracefully without errors.

#### Test Suite 5.1: BLANK and Zero Values

| Test ID | Edge Case | Test Type | Test Description |
|---|---|---|---|
| T5.1.1 | No sales data | Edge Case | Filter to customer with zero transactions → Measures return BLANK |
| T5.1.2 | No budget data | Edge Case | Filter to period with no budget records → Budget FYTD = BLANK |
| T5.1.3 | Zero denominator | Edge Case | Filter to sales = 0 → Profit % returns BLANK (not #DIV/0!) |
| T5.1.4 | Empty date filter | Edge Case | Clear all date filters → Measures calculate grand total |

**Execution Method**:
1. Create test scenarios by applying restrictive filters
2. **Test Case 5.1.1**: 
   - Filter: Customer dimension name column = (customer with no sales in mock data — verify column name in TMDL)
   - Check: `Sales Amount`, `Sales Amount FYTD` → Should show BLANK or 0
3. **Test Case 5.1.3**: 
   - Filter: `Sales Amount` = 0 (use advanced filter)
   - Check: `Adjusted Profit %` → Should show BLANK (verified by DIVIDE function)
4. Verify NO error messages appear in Power BI Desktop

**Pass Criteria**: 
✅ All measures return BLANK (not errors) for missing data  
✅ DIVIDE() function prevents division by zero errors  
✅ No visual rendering issues with BLANK values

---

#### Test Suite 5.2: Extreme Date Ranges

| Test ID | Date Range | Test Type | Test Description |
|---|---|---|---|
| T5.2.1 | Single day | Edge Case | Filter to single date → FYTD calculates from FY start to that day |
| T5.2.2 | Full year | Edge Case | Select complete fiscal year → FYTD = total for that year |
| T5.2.3 | Multi-year | Edge Case | Select 2+ years → YoY measures compare correctly |

**Execution Method**:
1. Use date slicer with precise date ranges
2. Verify FYTD logic handles boundaries correctly
3. Verify no data duplication or missing periods

**Pass Criteria**: ✅ Date filtering produces correct aggregations at all granularities

---

### Phase 6: Performance Validation

**Objective**: Ensure query response times are acceptable for end-user experience.

#### Test Suite 6.1: Query Performance Benchmarks

| Test ID | Visual Type | Test Type | Performance Target |
|---|---|---|---|
| T6.1.1 | Card (single measure) | Performance | < 1 second |
| T6.1.2 | Table (5 columns, 100 rows) | Performance | < 2 seconds |
| T6.1.3 | Matrix (3 levels drill-down) | Performance | < 3 seconds |
| T6.1.4 | Full dashboard refresh | Performance | < 5 seconds |

**Execution Method**:
1. Use **Performance Analyzer** in Power BI Desktop:
   - View → Performance Analyzer → Start Recording
2. Interact with visuals (click, filter, refresh)
3. Stop recording and review query durations
4. **Targets**:
   - Simple aggregations (Card): < 1 sec
   - Tables with < 100 rows: < 2 sec
   - Complex hierarchies: < 3 sec
   - Full page refresh: < 5 sec

**Pass Criteria**: 
✅ All query times meet or exceed targets  
⚠️ If any query > 5 seconds, initiate DAX optimization review (see `.github/references/dax-optimization-framework.md`)

---

## Test Execution Workflow

### Step 1: Setup Test Environment
1. Open the `<ProjectName>/PBIP/<ProjectName>.pbip` file in Power BI Desktop
2. Verify model loads without errors (Check Step 6 completion)
3. Create new report page named **"Test Suite"**
4. Enable **Performance Analyzer** (View ribbon)

### Step 2: Execute Test Suites Sequentially
Follow the order:
1. **Phase 1**: Base Measures (15 min)
2. **Phase 2**: Time Intelligence (20 min)
3. **Phase 3**: Percentages & Derived (20 min)
4. **Phase 4**: Relationships & Filters (15 min)
5. **Phase 5**: Edge Cases (10 min)
6. **Phase 6**: Performance (10 min)

**Total estimated time**: ~90 minutes

### Step 3: Document Test Results

Create a test results table in Markdown format:

```markdown
## Test Results Summary

| Phase | Test ID | Measure/Component | Status | Notes |
|---|---|---|---|---|
| Phase 1 | T1.1.1 | Sales Amount | ✅ PASS | Total: 1,234,567.89 (verified) |
| Phase 1 | T1.1.2 | Budget Amount | ✅ PASS | Total: 1,200,000.00 (verified) |
| Phase 2 | T2.1.1 | Sales Amount FYTD (FY=Jan) | ✅ PASS | Cumulative logic correct |
| Phase 2 | T2.1.2 | Sales Amount FYTD (FY=Jul) | ⚠️ WARNING | Minor rounding difference (0.02) |
| Phase 3 | T3.1.1 | Adjusted Profit % | ✅ PASS | DIVIDE handles zeros correctly |
| Phase 4 | T4.1.1 | Area → Country hierarchy | ✅ PASS | Drill-down works, totals match |
| Phase 5 | T5.1.3 | Zero denominator | ✅ PASS | Returns BLANK (no error) |
| Phase 6 | T6.1.4 | Full dashboard refresh | ⚠️ WARNING | 5.2 seconds (slightly over target) |
```

### Step 4: Triage Failures
For any ❌ FAIL or ⚠️ WARNING results:
1. Document the failure in detail (screenshot, error message, expected vs actual)
2. Investigate root cause:
   - DAX logic error? → Fix measure formula
   - Relationship issue? → Check Model View
   - Data quality issue? → Verify CSV mock data
3. Apply fix and re-run affected test
4. Update test results table

### Step 5: Sign-Off
Once ALL tests pass (✅ PASS):
1. Export test results table to `.github/test-results.md`
2. Create summary report for stakeholders
3. Mark **Step 7: Functional Testing** as ✅ COMPLETE

---

## Critical Testing Rules

### ⛔ MANDATORY: Model Introspection Before Test Generation (Mode B)
- ALWAYS execute Step B.0 (Model Introspection) BEFORE generating any test definitions
- ALWAYS read ALL TMDL table files to extract exact column names (PascalCase, no spaces)
- ALWAYS read `_Measures.tmdl` to extract exact measure names (natural language with spaces)
- NEVER assume or guess object names — column names in TMDL follow PascalCase convention without spaces
- NEVER add spaces to column names in DAX queries (e.g., `AreaName` NOT `Area Name`)
- Build a **Model Object Registry** and validate ALL DAX queries against it before execution
- If a column/measure name is not in the registry, it does NOT exist in the model — do NOT use it

### ⛔ MANDATORY: Test with Multiple Parameter Values
- NEVER test FYTD measures with only one fiscal year start month
- ALWAYS test at minimum: Jan (1), Apr (4), Jul (7), Oct (10)
- Verify parameter changes propagate to ALL dependent measures

### ⛔ MANDATORY: Test Edge Cases
- ALWAYS test what happens when filters return no data (BLANK handling)
- ALWAYS test zero division scenarios (verify DIVIDE function usage)
- ALWAYS test extreme date ranges (single day, multi-year)

### ⛔ MANDATORY: Cross-Validation with Source Data
- For base measures (Sales Amount, Budget Amount), ALWAYS cross-validate totals with source CSV files
- Use Python/Excel to calculate expected totals independently
- Document any discrepancies (rounding, data type conversion)

### ⛔ MANDATORY: Regression Testing
- If ANY measure is modified after testing, RE-RUN all tests that depend on it
- Example: If `Sales Amount FYTD` is changed, re-run T2.1.1, T2.1.2, T3.2.1, T3.2.2, T3.3.1

---

## Anti-Patterns to Avoid

### ❌ DON'T: Generate DAX queries without reading the model first
**Problem**: Column names in TMDL use PascalCase without spaces (e.g., `AreaName`), but the agent may assume names with spaces (e.g., `Area Name`). This causes 100% of tests referencing those columns to fail with "Column not found" errors.
**Solution**: ALWAYS execute Step B.0 (Model Introspection) to build a Model Object Registry. ALL DAX queries must reference ONLY names found in the registry. Cross-reference with `.github/references/naming-conventions.md`.

### ❌ DON'T: Test only with default parameter values
**Problem**: FYTD measures might work for calendar year (Jan start) but fail for fiscal year (Jul start)  
**Solution**: Test all common fiscal year scenarios (Jan, Apr, Jul, Oct)

### ❌ DON'T: Test only with full date ranges
**Problem**: Edge cases (single day, month boundary) might expose FYTD calculation bugs  
**Solution**: Test granular date selections and fiscal year boundaries

### ❌ DON'T: Assume DIVIDE prevents all errors
**Problem**: DIVIDE returns BLANK for zero denominator, but upstream measures might still cause errors  
**Solution**: Test entire measure chain with missing/zero data scenarios

### ❌ DON'T: Skip performance testing
**Problem**: Model works correctly but has unacceptable query times (>10 seconds)  
**Solution**: Always run Performance Analyzer and document query durations

---

## Test Automation (Optional — Advanced)

For large-scale testing or CI/CD integration, consider using **DAX Studio** for automated query execution:

### DAX Studio Test Script Example

```dax
-- Test Script: Validate Sales Amount FYTD for Calendar Year
-- Expected: FYTD for March 2024 = SUM(Jan + Feb + Mar 2024)

EVALUATE
CALCULATETABLE(
    SUMMARIZECOLUMNS(
        Dim_Date[FiscalMonth],
        "Sales Amount", [Sales Amount],
        "Sales Amount FYTD", [Sales Amount FYTD]
    ),
    Dim_Date[Date] >= DATE(2024, 1, 1) && Dim_Date[Date] <= DATE(2024, 3, 31),
    Parameters[ParameterName] = "Fiscal Year Start Month",
    Parameters[ParameterValue] = "1"
)
```

**Benefits**:
- Repeatable test execution
- Export results to CSV for automated comparison
- Faster iteration for regression testing

**Limitations**:
- Requires DAX Studio installation and PBIX file export
- Does NOT test visual interactions (drill-down, slicers)
- Best for unit tests, NOT integration tests

---

## Completion Checklist

Before marking **Step 7: Functional Testing** as complete:

- [ ] All Phase 1 tests (Base Measures) executed and passed
- [ ] All Phase 2 tests (Time Intelligence) executed and passed with 4+ parameter scenarios
- [ ] All Phase 3 tests (Percentages) executed and passed, DIVIDE handling verified
- [ ] All Phase 4 tests (Relationships) executed and passed, drill-down works correctly
- [ ] All Phase 5 tests (Edge Cases) executed and passed, no errors on BLANK/zero data
- [ ] All Phase 6 tests (Performance) executed, query times documented
- [ ] Test results table documented in `.github/test-results.md`
- [ ] Any failures triaged, root cause identified, and fixes applied
- [ ] Regression tests executed for all modified measures
- [ ] Stakeholder sign-off obtained (if required)

**Upon completion**: The semantic model is **validated for correctness** and ready for production deployment or report development. Proceed to Step 8: Documentation or hand off to report authors.

---

## References

- **Specification**: `<ProjectName>/spec/<spec_file>.md` — Business requirements and KPI definitions
- **DAX Patterns**: `.github/references/dax-patterns.md` — Measure formula templates
- **DAX Optimization**: `.github/references/dax-optimization-framework.md` — Performance tuning guidance
- **BPA Rules**: `.github/references/bpa-rules-reference.md` — Best practice compliance validation
- **Mock Data**: `<ProjectName>/data/*.csv` — Source data for cross-validation
- **Test Runner**: `.github/scripts/run_tests.py` — Universal automated test execution engine
