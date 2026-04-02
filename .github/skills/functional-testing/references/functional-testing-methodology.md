# Functional Testing Methodology

**Type**: Reference — load this file when building test suites (Mode A) or implementing Mode B technical details. Not loaded at skill start unless explicitly needed.

---

## RLS Testing Addendum (if applicable)

**Goal**: Validate that each RLS role restricts data as expected without accidentally granting broader access.

**Minimum manual checks (Power BI Desktop)**:
1. Use **View as** to test each role with representative identities.
2. Validate restricted users see expected totals where permitted (and blanks/empty where not permitted).
3. Validate unknown users do NOT get full access (deny-by-default).
4. If bi-directional security propagation is used, confirm it is limited to relationships justified by RLS requirements.

---

## Mode A: Manual Testing — Phase Catalog

### Phase 1: Base Measure Validation (Unit Tests)

**Objective**: Verify simple aggregation measures calculate correctly without filters.

#### Test Suite 1.1 — Sum Aggregations

| Test ID | Measure Name | Test Description |
|---|---|---|
| T1.1.1 | `Sales Amount` | Verify SUM(Fact_Sales[SalesAmountLC]) returns correct total |
| T1.1.2 | `Budget Amount` | Verify SUM(Fact_Budget[BudgetAmountLC]) returns correct total |
| T1.1.3 | `Adjusted Profit` | Verify SUM(Fact_Sales[AdjustedProfitLC]) returns correct total |

**Method**: Create Card visuals in a "Test Suite" page. Compare with CSV totals (Python/Excel cross-check).
**Pass criteria**: All values match CSV sum within 0.01 tolerance.

#### Test Suite 1.2 — Count Aggregations

| Test ID | Measure Name | Test Description |
|---|---|---|
| T1.2.1 | `# Transactions` | COUNTROWS(Fact_Sales) must match row count in `fact_sales.csv` |
| T1.2.2 | `# Customers` | DISTINCTCOUNT(CustomerKey) must match unique customers in CSV |

---

### Phase 2: Time Intelligence Validation

**Objective**: Verify FYTD calculations work correctly for the fiscal-calendar design actually implemented in the model.

Choose one mode before building tests:

- **Mode TI-A — Parameterized fiscal start**: use when the semantic model exposes a `Parameters` table and DAX reads `Parameters[ParameterValue]`.
- **Mode TI-B — Fixed fiscal calendar**: use when DAX hardcodes a fiscal year end or start month and no runtime parameter table exists.

#### Test Suite 2.1 — FYTD Base Measures

| Test ID | Measure | Fiscal Mode Input | Test Description |
|---|---|---|---|
| T2.1.1 | `Sales Amount FYTD` | Mode TI-A: FY Start = 1 (Jan) | FYTD accumulates Jan-to-selected-month in calendar year |
| T2.1.2 | `Sales Amount FYTD` | Mode TI-A: FY Start = 7 (Jul) | FYTD accumulates Jul-to-selected-month in fiscal year |
| T2.1.3 | `Budget Amount FYTD` | Mode TI-A: FY Start = 1 | Budget FYTD logic mirrors Sales FYTD |
| T2.1.4 | `Adjusted Profit FYTD` | Mode TI-A: FY Start = 7 | Profit FYTD logic mirrors Sales FYTD |
| T2.1.5 | `Sales Amount FYTD` | Mode TI-B: Representative boundary dates | Validate the hardcoded fiscal definition at four dates across the fiscal year |

**Method for T2.1.1 (Mode TI-A)**:
1. Set `Parameters[ParameterValue]` = `"1"` (January)
2. Date slicer to March 2024
3. Table visual: Rows = `Dim_Date[FiscalMonth]`, Values = `Sales Amount`, `Sales Amount FYTD`
4. Expected: each row cumulates from Jan — March value = Jan + Feb + Mar

**Method for T2.1.2 (Mode TI-A)**:
Same visual, change parameter to `"7"`, date to October 2024.
Expected: FY2025 starts Jul 2024. FYTD for Oct = Jul + Aug + Sep + Oct sales.

**Method for T2.1.5 (Mode TI-B)**:
1. Pick at least four representative dates that cross the active fiscal boundaries, for example first fiscal month end, quarter boundary, mid-year, and fiscal year end.
2. Evaluate the FYTD measure at each date with `TREATAS({ DATE(...) }, Dim_Date[Date])` or an equivalent date-context query.
3. Compare each actual value to a CSV-derived expected total for the fixed fiscal window.

**Pass criteria**:
- Mode TI-A: FYTD increases monotonically within each fiscal year, resets at FY boundary, and parameter change recalculates dynamically.
- Mode TI-B: FYTD matches the expected fixed fiscal windows at each boundary date and shows no hidden dependency on a missing parameter table.

#### Test Suite 2.2 — Year-over-Year Measures

| Test ID | Measure | Test Description |
|---|---|---|
| T2.2.1 | `Sales Amount PY` | Previous year sales = SAMEPERIODLASTYEAR result |
| T2.2.2 | `Sales YOY %` | YoY % = (Current - PY) / PY, handled by DIVIDE |

---

### Phase 3: Percentage & Derived Measures

**Objective**: Verify DIVIDE() usage and zero/BLANK handling.

#### Test Suite 3.1 — Profitability Percentages

| Test ID | Measure | Test Description |
|---|---|---|
| T3.1.1 | `Adjusted Profit %` | = Adjusted Profit / Sales Amount — use DIVIDE |
| T3.1.2 | `Item Profit %` | = Item Profit / Sales Amount |
| T3.1.3 | `Resource Profit %` | = Resource Profit / Sales Amount |
| T3.1.4 | `Item Discount %` | = Discount Amount / Sales Amount |

**Edge case verification**: Filter to a customer with Sales Amount = 0 → all percentage measures must return BLANK (not `#DIV/0!` or ∞).

#### Test Suite 3.2 — Budget Variance

| Test ID | Measure | Test Description |
|---|---|---|
| T3.2.1 | `Sales vs Budget` | = Sales Amount FYTD − Budget Amount FYTD |
| T3.2.2 | `Sales vs Budget %` | = Variance / Budget Amount FYTD |
| T3.2.3 | `Budget Status` | SWITCH logic: Above / Close / Below target thresholds |

**Method for T3.2.3**: Create table by Area dimension (exact column name from TMDL). Verify SWITCH conditions against thresholds defined in spec.

#### Test Suite 3.3 — Average Monthly Sales

| Test ID | Measure | Test Description |
|---|---|---|
| T3.3.1 | `Average Monthly Sales` | = Sales Amount FYTD / distinct month count in FY period |

Validate: Q1 2024 (3 months) with Jan FY start → Average = FYTD Sales / 3.

---

### Phase 4: Relationship & Filter Context Validation

**Objective**: Verify all relationship paths propagate filters correctly.

#### Test Suite 4.1 — Dimensional Drill-Down

| Test ID | Path | Test Description |
|---|---|---|
| T4.1.1 | Area → Country → Customer | Hierarchy totals aggregate correctly, no duplicates |
| T4.1.2 | Industry → Customer | Industry slicer filters Sales and Budget facts |
| T4.1.3 | Salesperson | Salesperson filter propagates to sales fact |
| T4.1.4 | Date → FiscalYear/Month | Date filters reach both Fact_Sales and Fact_Budget |

**Method for T4.1.1**: Matrix visual with geographic hierarchy using exact TMDL column names (e.g., `Dim_Area[AreaName]`, `Dim_Country[CountryName]`, `Dim_Customer[CustomerName]`). Verify: Area total = SUM of its countries.

#### Test Suite 4.2 — Parameter Scenarios

Test FYTD measures with all four common fiscal year starts:

| FY Start | Month | Expected FYTD period (for Oct 2024 context) |
|---|---|---|
| 1 (Jan) | January | Jan 2024 – Oct 2024 |
| 4 (Apr) | April | Apr 2024 – Oct 2024 |
| 7 (Jul) | July | Jul 2024 – Oct 2024 |
| 10 (Oct) | October | Oct 2024 only |

**Pass criteria**: Parameter change recalculates all FYTD measures dynamically; no hardcoded calendar year assumptions.

---

### Phase 5: Edge Case & Error Handling

**Important**: when a measure uses `ISINSCOPE`, `HASONEVALUE`, or row suppression behavior, a plain slicer-style `CALCULATE(..., TREATAS(...))` query is not enough. Reproduce the visual row context with `SUMMARIZECOLUMNS` and assert either the resulting row value or the fact that the row is suppressed.

#### Test Suite 5.1 — BLANK and Zero Values

| Test ID | Scenario | Expected Result |
|---|---|---|
| T5.1.1 | Customer with no transactions | Sales Amount = BLANK or 0 |
| T5.1.2 | Period with no budget records | Budget Amount FYTD = BLANK |
| T5.1.3 | Sales Amount = 0 | All profit % measures = BLANK (DIVIDE protection) |
| T5.1.4 | No date filters applied | Measures calculate grand total |

**Visual-row-context example**:

```dax
EVALUATE
ROW(
    "Actual",
    ISEMPTY(
        SUMMARIZECOLUMNS(
            Dim_Staff[SalespersonName],
            FILTER(ALL(Dim_Staff[SalespersonName]), Dim_Staff[SalespersonName] = "Andrea Henson"),
            "Metric",
            [Budget Amount]
        )
    )
)
```

Use this pattern when the expected behavior is "the row disappears because the measure is blank at row scope".

#### Test Suite 5.2 — Extreme Date Ranges

| Test ID | Range | Expected |
|---|---|---|
| T5.2.1 | Single day | FYTD = sum from FY start to that day |
| T5.2.2 | Full fiscal year | FYTD = full year total |
| T5.2.3 | Multi-year selection | YoY measures compare periods correctly |

---

### Phase 6: Performance Benchmarks (Power BI Desktop Performance Analyzer)

**Enable**: View → Performance Analyzer → Start Recording. Interact with visuals, review query durations.

| Benchmark | Target |
|---|---|
| Single Card visual | < 1 sec |
| Table (5 columns, 100 rows) | < 2 sec |
| Matrix with 3-level hierarchy | < 3 sec |
| Full page refresh | < 5 sec |

If any query exceeds 5 seconds, investigate using `.github/references/dax-optimization-framework.md`.

---

## Mode B: Technical Implementation Notes

### Python Dependencies

```
pandas>=2.0.0
pyodbc>=4.0.39
python-dateutil>=2.8.2
```

### Detecting the Analysis Services Port

```powershell
Get-ChildItem "$env:LOCALAPPDATA\Microsoft\Power BI Desktop\AnalysisServicesWorkspaces" -Recurse -Filter "msmdsrv.port.txt" | Get-Content
```

**Operational note**: recent Power BI Desktop builds commonly store the active port file under `AnalysisServicesWorkspace_<id>\Data\msmdsrv.port.txt`, not only at the workspace root. Any automated detector must support both layouts and should log the resolved file path.

### Python Execution Pattern (ADOMD.NET + Assertion Validation)

```python
import json
import pandas as pd

with open('tests_definition.json', 'r') as f:
    test_plan = json.load(f)

# Connect with ADOMD.NET or another tabular-compatible client.
test_results = []

for suite in test_plan['testSuites']:
    for test in suite['tests']:
        try:
            result = execute_dax(test['daxQuery'])
            assertion = evaluate_assertion(test, result)
            test_results.append({
                'testId': test['testId'],
                'testName': test['testName'],
                'status': assertion['status'],
                'actualValue': assertion['actualValue'],
                'expectedValue': assertion['expectedValue'],
                'delta': assertion['delta']
            })
        except Exception as e:
            test_results.append({
                'testId': test['testId'],
                'testName': test['testName'],
                'status': 'FAIL',
                'error': str(e)
            })
```

### CSV Cross-Validation

```python
fact_sales = pd.read_csv('<ProjectName>/data/fact_sales.csv')
fact_budget = pd.read_csv('<ProjectName>/data/fact_budget.csv')

sales_total = fact_sales['SalesAmountLC'].sum()   # use exact CSV column name
budget_total = fact_budget['BudgetAmountLC'].sum()

# Compare with DAX query result; tolerance: abs difference < 0.01
```

### Machine-Readable Assertions

New test definitions should include explicit assertion metadata instead of relying only on prose:

```json
{
    "testId": "T01.01",
    "testName": "[Sales Amount] total",
    "daxQuery": "EVALUATE ROW(\"Actual\", [Sales Amount])",
    "assertionType": "numeric_tolerance",
    "expectedValue": 1234567.89,
    "tolerance": 0.01,
    "expectedBehavior": "Matches SUM of source CSV column within 0.01 tolerance"
}
```

Supported assertion styles:

| Assertion Type | Use Case |
|---|---|
| `numeric_tolerance` | scalar numeric comparisons with tolerance |
| `exact` | exact string, boolean, or integer matches |
| `blank` | BLANK result expected |
| `row_numeric_tolerance` | one-row, multi-column results such as Sales and Budget in the same query |

Legacy definitions can be interpreted heuristically, but that should be treated as backward compatibility only, not as the target standard.

---

## Test Execution Report Template

```markdown
# Test Execution Report — <ProjectName>

**Date**: <ISO timestamp>
**Model**: <ProjectName>/PBIP/<ProjectName>.SemanticModel
**Execution Mode**: Automated (Python + pyadomd) / Manual
**Analysis Services**: localhost:<port>

---

## Executive Summary

| Suite | Priority | Total | ✅ | ⚠️ | ❌ | Status |
|---|---|---:|---:|---:|---:|---|
| TS01 Base Aggregations | HIGH | N | N | 0 | 0 | ✅ PASS |
| TS02 Time Intelligence | CRITICAL | N | N | N | N | ... |
| ... | ... | ... | ... | ... | ... | ... |
| **TOTAL** | — | **N** | **N** | **N** | **N** | **status** |

---

## Detailed Results

### ✅ T01.01 — Sales Amount Total
- **DAX**: `EVALUATE { [Sales Amount] }`
- **Actual**: 1,234,567.89
- **CSV Total**: 1,234,567.89 (pandas verified)
- **Delta**: 0.00 ✅
- **Query Time**: 0.12 sec
- **Status**: ✅ PASS

### ⚠️ T02.02 — Sales Amount FYTD (FY Start = Jul)
- **Status**: ⚠️ WARNING — Result correct, query time 5.2 sec exceeds 5 sec target
- **Recommendation**: Replace `FILTER(ALL(Dim_Date[Date]))` with `CALCULATETABLE` or pre-computed fiscal flag column. See `.github/references/dax-optimization-framework.md`.

---

## Issues & Recommendations

### ⚠️ Issue #1: Performance — FYTD Fiscal Year Query
**Symptom**: 5.2 sec (exceeds target). **Root Cause**: Full date table scan in FILTER.

**Fix Option A — Pre-computed flag column**:
```dax
// Add calculated column to Dim_Date:
IsFYTD =
VAR FYStart = VALUE(SELECTEDVALUE(Parameters[ParameterValue], "1"))
VAR FYStartDate = DATE(IF(MONTH([Date]) >= FYStart, YEAR([Date]), YEAR([Date])-1), FYStart, 1)
RETURN [Date] >= FYStartDate && [Date] <= TODAY()
```

**Fix Option B — CALCULATETABLE instead of FILTER**:
```dax
Sales Amount FYTD =
VAR FYStartMonth = VALUE(SELECTEDVALUE(Parameters[ParameterValue], "1"))
VAR FYStartDate = DATE(IF(MONTH(MAX(Dim_Date[Date])) >= FYStartMonth, YEAR(MAX(Dim_Date[Date])), YEAR(MAX(Dim_Date[Date]))-1), FYStartMonth, 1)
RETURN CALCULATE([Sales Amount], CALCULATETABLE(Dim_Date, Dim_Date[Date] >= FYStartDate, Dim_Date[Date] <= MAX(Dim_Date[Date])))
```

---

## CSV Cross-Validation Summary

| Source | Column | Expected | Actual | Match |
|---|---|---:|---:|---|
| fact_sales.csv | SalesAmountLC | 1,234,567.89 | 1,234,567.89 | ✅ |
| fact_budget.csv | BudgetAmountLC | 1,200,000.00 | 1,200,000.00 | ✅ |

---

## Performance Summary

| Category | Avg | Max | Status |
|---|---|---|---|
| Base Aggregations | 0.10 sec | 0.12 sec | ✅ |
| Time Intelligence | 2.8 sec | 5.2 sec | ⚠️ |
| Derived Calculations | 0.25 sec | 0.32 sec | ✅ |

**Recommendation**: Model is functionally correct. Optimize FYTD measure if performance is a priority.
```

---

## Anti-Patterns

### ❌ Generate DAX queries without reading the model first
**Problem**: Column names in TMDL use PascalCase without spaces (`AreaName`). Assuming `Area Name` causes 100% column-not-found failures.
**Solution**: Always execute B.0 Model Introspection. Validate every `Table[Column]` reference against the registry.

### ❌ Mark tests as PASS when the query only executes
**Problem**: A query can execute successfully while still validating the wrong business behavior.
**Solution**: Require machine-readable assertions and fail the run when actual values do not satisfy `expectedValue` or `expectedRow`.

### ❌ Force a `Parameters` table for every fiscal model
**Problem**: Some models hardcode the fiscal year in DAX and do not expose a runtime parameter table.
**Solution**: Detect whether the model is parameterized or fixed-fiscal before building TS02 and choose the matching scenario set.

### ❌ Test `ISINSCOPE` logic with slicer-only filters
**Problem**: `ISINSCOPE` depends on row grouping, not just filter context, so slicer-style tests can produce false positives or false negatives.
**Solution**: Use `SUMMARIZECOLUMNS` or an equivalent row-context query shape for visual-row edge cases.

### ❌ Test only with one fiscal year start value
**Problem**: FYTD may appear correct for calendar year (Jan) but fail for Jul start.
**Solution**: Always test Jan, Apr, Jul, Oct as minimum scenarios.

### ❌ Test only with full date ranges
**Problem**: Edge cases at month/year boundaries can expose FYTD reset bugs.
**Solution**: Test single-day, month boundary, and multi-year selections.

### ❌ Assume DIVIDE prevents all errors
**Problem**: DIVIDE protects against division by zero but upstream measures may still cause errors.
**Solution**: Test the full measure chain with zero/missing data at each level.

### ❌ Skip performance testing
**Problem**: Model may be functionally correct but unusable (>10 sec queries).
**Solution**: Always run Performance Analyzer and document durations before sign-off.

---

## DAX Studio Automation (Optional)

For CI/CD or large regression suites, use DAX Studio for repeatable query execution:

```dax
-- Validate Sales Amount FYTD for Calendar Year (Jan start)
EVALUATE
CALCULATETABLE(
    SUMMARIZECOLUMNS(
        Dim_Date[FiscalMonth],
        "Sales Amount", [Sales Amount],
        "Sales Amount FYTD", [Sales Amount FYTD]
    ),
    Dim_Date[Date] >= DATE(2024,1,1) && Dim_Date[Date] <= DATE(2024,3,31),
    Parameters[ParameterName] = "Fiscal Year Start Month",
    Parameters[ParameterValue] = "1"
)
```

**Limitations**: Requires PBIX file (not PBIP directly). Best for unit tests; does not test visual interactions.
