# DAX Optimization Framework — Performance Best Practices

> Comprehensive framework for analyzing, optimizing, and validating DAX formulas.
> Use `microsoft_code_sample_search` MCP tool to find validated optimization patterns.

---

## 1. Performance Analysis Checklist

Before finalizing ANY DAX measure, perform this 4-category analysis:

### A. Context Transition Analysis

**Problem**: Excessive row context → filter context transitions slow down calculations.

**Detection Patterns**:
```dax
-- ❌ BAD: Row-by-row calculation in SUMX
measure 'Slow Margin' =
	SUMX(
		Fact_Sales,
		Fact_Sales[SalesAmount] - 
		CALCULATE(SUM(Fact_Cost[Cost]))  -- Context transition EVERY row
	)

-- ✅ GOOD: Single context transition
measure 'Fast Margin' =
	VAR TotalSales = SUM(Fact_Sales[SalesAmount])
	VAR TotalCost = SUM(Fact_Cost[Cost])
	VAR Margin = TotalSales - TotalCost
	RETURN
		Margin
```

**Optimization Rules**:
- ✅ Minimize `CALCULATE()` inside iterator functions (SUMX, FILTER, etc.)
- ✅ Use `CALCULATETABLE()` once, then iterate over the result
- ✅ Prefer measures over calculated columns in iterators
- ❌ Avoid nested `CALCULATE()` in `SUMX`/`FILTER` when possible

---

### B. Variable Usage Optimization

**Problem**: Repeated calculations cause redundant work.

**Detection Patterns**:
```dax
-- ❌ BAD: Same calculation repeated 3 times
measure 'Inefficient Ratio' =
	IF(
		SUM(Sales[Amount]) > 0,
		DIVIDE(
			SUM(Sales[Amount]) - SUM(Cost[Amount]),
			SUM(Sales[Amount])  -- Repeated calculation
		),
		BLANK()
	)

-- ✅ GOOD: Calculate once, reuse via VAR
measure 'Efficient Ratio' =
	VAR TotalSales = SUM(Sales[Amount])
	VAR TotalCost = SUM(Cost[Amount])
	VAR Margin = TotalSales - TotalCost
	VAR MarginPct = DIVIDE(Margin, TotalSales)
	RETURN
		IF(TotalSales > 0, MarginPct, BLANK())
```

**Optimization Rules**:
- ✅ Store expensive `CALCULATE()` results in VARs
- ✅ Store intermediate calculations for reuse
- ✅ Use VARs for complex filter expressions
- ✅ Store table expressions (`FILTER`, `CALCULATETABLE`) in VARs
- ❌ Don't create VARs for trivial single-use expressions

**Variable Naming Convention**:
```dax
measure 'Optimized Sales YoY %' =
	-- Descriptive variable names explain business logic
	VAR CurrentYearSales = [Sales Amount]
	VAR PreviousYearSales = 
		CALCULATE(
			[Sales Amount],
			SAMEPERIODLASTYEAR(Dim_Date[Date])
		)
	VAR YoYGrowth = CurrentYearSales - PreviousYearSales
	VAR YoYGrowthPct = DIVIDE(YoYGrowth, PreviousYearSales)
	RETURN
		YoYGrowthPct
	formatString: 0.00%
```

---

### C. Filter Efficiency Analysis

**Problem**: Inefficient filter expressions cause slow queries.

**Detection Patterns**:
```dax
-- ❌ BAD: Row-by-row filtering
measure 'Slow High Value Sales' =
	SUMX(
		FILTER(
			Fact_Sales,
			Fact_Sales[SalesAmount] > 1000  -- Scans every row
		),
		Fact_Sales[SalesAmount]
	)

-- ✅ GOOD: Use CALCULATE with filter argument
measure 'Fast High Value Sales' =
	CALCULATE(
		SUM(Fact_Sales[SalesAmount]),
		Fact_Sales[SalesAmount] > 1000  -- Filter pushdown
	)
```

**Optimization Rules**:

1. **Prefer CALCULATE filters over FILTER function**:
```dax
-- ✅ BETTER
CALCULATE([Measure], Table[Column] = "Value")

-- ❌ SLOWER
CALCULATE([Measure], FILTER(Table, Table[Column] = "Value"))
```

2. **Use Table Expressions for Complex Filters**:
```dax
measure 'Optimized Multi-Filter' =
	VAR FilteredTable = 
		CALCULATETABLE(
			Fact_Sales,
			Fact_Sales[SalesAmount] > 1000,
			Dim_Customer[CustomerType] = "Premium",
			Dim_Date[Year] = 2024
		)
	VAR Result = 
		SUMX(FilteredTable, Fact_Sales[SalesAmount])
	RETURN
		Result
```

3. **Leverage Relationships Over Manual Filters**:
```dax
-- ✅ GOOD: Uses relationship
measure 'Category Sales' =
	CALCULATE(
		SUM(Fact_Sales[SalesAmount]),
		Dim_Product[Category] = "Electronics"
	)

-- ❌ SLOWER: Manual join
measure 'Slow Category Sales' =
	SUMX(
		FILTER(
			Fact_Sales,
			RELATED(Dim_Product[Category]) = "Electronics"
		),
		Fact_Sales[SalesAmount]
	)
```

4. **Use REMOVEFILTERS Over ALL**:
```dax
-- ✅ CLEAR and PERFORMANT
CALCULATE([Measure], REMOVEFILTERS(Dim_Area))

-- ❌ AMBIGUOUS (removes filters AND returns table)
CALCULATE([Measure], ALL(Dim_Area))
```

---

### D. Function Selection Optimization

**Problem**: Using suboptimal functions for the task.

**Optimization Table**:

| Instead of... | Use... | Why |
|---------------|--------|-----|
| `COUNT(Column)` | `COUNTROWS(Table)` | Faster, counts all rows |
| `VALUES(Column)` (when expecting single value) | `SELECTEDVALUE(Column)` | Returns BLANK on multiple values |
| `Column1 / Column2` | `DIVIDE(Column1, Column2, 0)` | Handles zero denominator |
| `IF(ISBLANK(X), 0, X)` | `X + 0` | Simpler, converts BLANK to 0 |
| `CALCULATE(SUM, Table)` | `SUMX(Table, Column)` | When iterating is necessary |
| `FILTER(ALL(Table), ...)` | `CALCULATETABLE(Table, ...)` | Clearer filter context |

**Function Performance Examples**:

```dax
-- ❌ SLOWER: COUNT ignores blanks, more complex
measure 'Customer Count' = COUNT(Dim_Customer[CustomerKey])

-- ✅ FASTER: COUNTROWS counts all rows
measure 'Customer Count' = COUNTROWS(Dim_Customer)

-- ❌ SLOWER: VALUES + Nested IF
measure 'Selected Region' =
	VAR RegionValues = VALUES(Dim_Region[Region])
	VAR Result = 
		IF(
			COUNTROWS(RegionValues) = 1,
			MINX(RegionValues, Dim_Region[Region]),
			"Multiple Regions"
		)
	RETURN
		Result

-- ✅ FASTER: SELECTEDVALUE
measure 'Selected Region' =
	SELECTEDVALUE(Dim_Region[Region], "Multiple Regions")
```

---

## 2. Iterator Function Optimization Patterns

### SUMX, FILTER, ADDCOLUMNS Performance

**Pattern 1: Pre-Filter Before Iteration**
```dax
-- ❌ BAD: Filters inside iterator
measure 'Slow Premium Sales' =
	SUMX(
		FILTER(
			Fact_Sales,
			RELATED(Dim_Customer[CustomerType]) = "Premium" &&
			Fact_Sales[SalesAmount] > 1000
		),
		Fact_Sales[SalesAmount]
	)

-- ✅ GOOD: Use CALCULATETABLE to filter, then iterate
measure 'Fast Premium Sales' =
	VAR FilteredSales = 
		CALCULATETABLE(
			Fact_Sales,
			Dim_Customer[CustomerType] = "Premium",
			Fact_Sales[SalesAmount] > 1000
		)
	VAR Result = SUMX(FilteredSales, Fact_Sales[SalesAmount])
	RETURN
		Result
```

**Pattern 2: Avoid Calculated Column References in Iterators**
```dax
-- ❌ SLOW: Calculated column evaluated per row
-- Calculated Column: Margin = Sales[Amount] - Sales[Cost]
measure 'Slow Total Margin' =
	SUMX(Fact_Sales, Fact_Sales[Margin])  -- Recalculates column

-- ✅ FASTER: Direct column references
measure 'Fast Total Margin' =
	SUMX(
		Fact_Sales,
		Fact_Sales[SalesAmount] - Fact_Sales[CostAmount]
	)

-- ✅✅ FASTEST: Avoid iteration when possible
measure 'Fastest Total Margin' =
	VAR TotalSales = SUM(Fact_Sales[SalesAmount])
	VAR TotalCost = SUM(Fact_Sales[CostAmount])
	RETURN
		TotalSales - TotalCost
```

**Pattern 3: CALCULATE Inside SUMX (Use Sparingly)**
```dax
-- ⚠️ ACCEPTABLE: When necessary for row-level logic
measure 'Sales with Dynamic Discount' =
	SUMX(
		Fact_Sales,
		VAR CurrentAmount = Fact_Sales[SalesAmount]
		VAR CustomerType = RELATED(Dim_Customer[CustomerType])
		VAR DiscountRate = 
			CALCULATE(
				SELECTEDVALUE(Dim_Discount[Rate]),
				Dim_Discount[CustomerType] = CustomerType
			)
		VAR DiscountedAmount = CurrentAmount * (1 - DiscountRate)
		RETURN
			DiscountedAmount
	)
```

---

## 3. Time Intelligence Optimization

### Pattern: Pre-Calculate Base Measure
```dax
-- ❌ INEFFICIENT: Base calculation repeated
measure 'Sales FYTD' =
	CALCULATE(
		SUM(Fact_Sales[SalesAmount]),  -- Repeated
		DATESYTD(Dim_Date[Date], "6/30")
	)

measure 'Sales PY' =
	CALCULATE(
		SUM(Fact_Sales[SalesAmount]),  -- Repeated
		SAMEPERIODLASTYEAR(Dim_Date[Date])
	)

-- ✅ EFFICIENT: Base measure referenced
measure 'Total Sales' =
	SUM(Fact_Sales[SalesAmount])

measure 'Sales FYTD' =
	VAR FYTDSales = 
		CALCULATE(
			[Total Sales],  -- Reuses base measure
			DATESYTD(Dim_Date[Date], "6/30")
		)
	RETURN
		FYTDSales

measure 'Sales PY' =
	VAR PYSales = 
		CALCULATE(
			[Total Sales],  -- Reuses base measure
			SAMEPERIODLASTYEAR(Dim_Date[Date])
		)
	RETURN
		PYSales
```

### Pattern: Avoid FILTER with Date Functions
```dax
-- ❌ SLOW: Manual filtering
measure 'YTD Sales Slow' =
	VAR MaxDate = MAX(Dim_Date[Date])
	VAR YearStart = DATE(YEAR(MaxDate), 1, 1)
	VAR FilteredDates = 
		FILTER(
			ALL(Dim_Date[Date]),
			Dim_Date[Date] >= YearStart && Dim_Date[Date] <= MaxDate
		)
	VAR Result = 
		CALCULATE([Total Sales], FilteredDates)
	RETURN
		Result

-- ✅ FAST: Use built-in time intelligence
measure 'YTD Sales Fast' =
	TOTALYTD([Total Sales], Dim_Date[Date])
```

---

## 4. Error Handling Optimization

### Pattern: Defensive Checks Without Performance Penalty
```dax
-- ❌ SLOW: Multiple nested IFs
measure 'Slow Safe Division' =
	IF(
		NOT(ISBLANK([Denominator])),
		IF(
			[Denominator] <> 0,
			[Numerator] / [Denominator],
			BLANK()
		),
		BLANK()
	)

-- ✅ FAST: DIVIDE handles all cases
measure 'Fast Safe Division' =
	DIVIDE([Numerator], [Denominator])
```

### Pattern: VAR for Error Detection
```dax
measure 'Sales Growth with Validation' =
	VAR CurrentSales = [Total Sales]
	VAR PreviousSales = [Total Sales PY]
	VAR HasValidData = 
		NOT(ISBLANK(CurrentSales)) && 
		NOT(ISBLANK(PreviousSales)) &&
		PreviousSales <> 0
	VAR Growth = 
		DIVIDE(CurrentSales - PreviousSales, PreviousSales)
	RETURN
		IF(HasValidData, Growth, BLANK())
	formatString: 0.00%
```

---

## 5. Testing and Validation Framework

### Step 1: Baseline Performance Test
```dax
-- Create test measure that returns immediately
measure 'Baseline Test' = 
	"OK"  -- Returns static value, no calculation
```

**Usage**: Compare visual refresh time with baseline to isolate measure performance.

### Step 2: Incremental Optimization Test
```dax
-- Version 1: Original (slow)
measure 'Sales V1 - Original' =
	SUMX(
		FILTER(Fact_Sales, Fact_Sales[Amount] > 1000),
		Fact_Sales[Amount]
	)

-- Version 2: With VAR (test improvement)
measure 'Sales V2 - With VAR' =
	VAR FilteredSales = 
		FILTER(Fact_Sales, Fact_Sales[Amount] > 1000)
	VAR Result = SUMX(FilteredSales, Fact_Sales[Amount])
	RETURN
		Result

-- Version 3: With CALCULATE (test further improvement)
measure 'Sales V3 - With CALCULATE' =
	CALCULATE(
		SUM(Fact_Sales[Amount]),
		Fact_Sales[Amount] > 1000
	)
```

**Usage**: Test each version side-by-side using Performance Analyzer in Power BI Desktop.

### Step 3: Edge Case Validation
```dax
-- Test with sample data that includes:
-- 1. BLANK values in numerator/denominator
-- 2. Zero values in denominators
-- 3. No data (empty filter context)
-- 4. Single row vs multiple rows
-- 5. Extreme values (very large/small numbers)

measure 'Robust Calculation' =
	VAR Numerator = [Sales Amount]
	VAR Denominator = [Budget Amount]
	VAR HasData = 
		NOT(ISBLANK(Numerator)) && NOT(ISBLANK(Denominator))
	VAR Result = DIVIDE(Numerator, Denominator)
	RETURN
		IF(HasData, Result, BLANK())
```

---

## 6. Performance Tuning Workflow

**For Each Measure, Follow This Process**:

### Phase 1: Write Initial Version
- Focus on correctness first
- Use clear VARs for readability
- Document business logic with comments

### Phase 2: Optimize for Performance
1. **Identify Bottlenecks**:
   - Look for repeated calculations → add VARs
   - Look for CALCULATE in iterators → refactor
   - Look for complex filters → use CALCULATETABLE

2. **Apply Optimization Patterns**:
   - Replace inefficient functions (see table above)
   - Reduce context transitions
   - Leverage relationships over manual filters

3. **Test with Performance Analyzer**:
   - Create visual with measure
   - Run Performance Analyzer
   - Compare "DAX query" time before/after
   - Target: <100ms for simple aggregations, <500ms for complex calculations

### Phase 3: Validate Edge Cases
- Test with no data
- Test with single row
- Test with BLANK values
- Test with filters that return no results
- Test with extreme date ranges (fiscal year edge cases)

---

## 7. Common Anti-Patterns to Avoid

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| `SUMX(Table, [Measure])` | Evaluates measure per row | `CALCULATE([Measure], Table)` or direct `SUMX(Table, Table[Column])` |
| `FILTER(ALL(Table), ...)` everywhere | Clears all filters unnecessarily | `CALCULATETABLE(Table, ...)` or `REMOVEFILTERS()` |
| Calculated columns in large fact tables | Slow refresh, memory intensive | Use measures or Power Query |
| `RELATED()` in SUMX over millions of rows | Slow relationship traversal per row | Pre-filter with CALCULATETABLE |
| No VARs in complex measures | Repeated calculations, hard to debug | Add VARs for intermediate results |
| Division with `/` operator | Errors on zero division | Always use `DIVIDE()` |
| `IF(ISBLANK(X), 0, X)` | Verbose | `X + 0` converts BLANK to 0 |
| Multiple `ALL(Table[Column])` in same measure | Redundant filter removal | Use `REMOVEFILTERS()` once |

---

## 8. MCP Verification Workflow

Before finalizing any optimized DAX:

1. **Search for Validated Patterns**:
```
microsoft_code_sample_search: "DAX time intelligence TOTALYTD"
microsoft_code_sample_search: "DAX SUMX optimization"
microsoft_code_sample_search: "DAX CALCULATE filter context"
```

2. **Verify Function Syntax**:
```
microsoft_docs_search: "DAX CALCULATETABLE function"
microsoft_docs_search: "DAX REMOVEFILTERS vs ALL"
```

3. **Check Best Practices**:
```
microsoft_docs_search: "DAX performance optimization"
microsoft_docs_search: "DAX variables VAR RETURN"
```

---

## 9. Optimization Decision Tree

```
Start: Need to create DAX measure
│
├─ Is it a simple aggregation? (SUM, COUNT, AVG)
│  ├─ YES → Use base aggregation, add formatString
│  └─ NO → Continue
│
├─ Does it involve time intelligence?
│  ├─ YES → Use built-in functions (TOTALYTD, SAMEPERIODLASTYEAR)
│  └─ NO → Continue
│
├─ Does it require iteration? (row-by-row calculation)
│  ├─ YES → Can you avoid iteration?
│  │  ├─ YES → Refactor to CALCULATE
│  │  └─ NO → Pre-filter with CALCULATETABLE, then iterate
│  └─ NO → Continue
│
├─ Does it have repeated calculations?
│  ├─ YES → Extract to VARs
│  └─ NO → Continue
│
├─ Does it involve division?
│  ├─ YES → Use DIVIDE() function
│  └─ NO → Continue
│
└─ Final: Format, add to Display Folder, test with Performance Analyzer
```

---

## 10. Measure Optimization Template

Use this template for all complex measures:

```dax
measure 'Measure Name' =
	// STEP 1: Document business logic
	-- This measure calculates [business purpose]
	-- Dependencies: [list base measures or tables]
	-- Edge cases: [BLANK handling, zero division, no data]
	
	// STEP 2: Declare variables for intermediate calculations
	VAR BaseValue = [Base Measure]
	VAR ComparisionValue = 
		CALCULATE(
			[Base Measure],
			[Filter Logic]
		)
	
	// STEP 3: Perform calculations
	VAR Delta = BaseValue - ComparisionValue
	VAR DeltaPct = DIVIDE(Delta, ComparisionValue)
	
	// STEP 4: Handle edge cases
	VAR HasValidData = 
		NOT(ISBLANK(BaseValue)) && NOT(ISBLANK(ComparisionValue))
	
	// STEP 5: Return result
	RETURN
		IF(HasValidData, DeltaPct, BLANK())
	
	// STEP 6: Add metadata
	formatString: 0.00%
	displayFolder: Performance
	lineageTag: <generate-guid>
```

---

**Remember**: Optimization is about balance. Prioritize:
1. **Correctness** - Accurate business logic
2. **Readability** - Maintainable code with VARs and comments
3. **Performance** - Fast execution with optimized patterns

Always verify optimizations don't change calculation results!
