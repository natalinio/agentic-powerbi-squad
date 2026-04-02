# DAX Patterns Reference — Best Practices

> Validated DAX patterns for common Power BI semantic model scenarios.
> Use `microsoft_docs_search` or `microsoft_code_sample_search` MCP tools to verify
> any pattern before generating DAX code.

---

## 1. Coding Standards

### VAR / RETURN Pattern (MANDATORY)
All non-trivial measures MUST use the VAR/RETURN pattern:
```dax
measure 'Sales Amount FYTD' =
		VAR CurrentSales =
			CALCULATE(
				[Sales Amount],
				DATESYTD(Dim_Date[Date], "6/30")
			)
		RETURN
			CurrentSales
```

**Why**: Improves readability, debuggability, and performance (VARs are evaluated once).

### VAR Naming — Reserved Keywords (MANDATORY)
**NEVER** use DAX reserved keywords or function names as VAR names. The DAX engine will reject them with a compile error: `'<Name>' is a reserved word`.

**Forbidden VAR names** (non-exhaustive): `Variance`, `Status`, `Value`, `Date`, `Time`, `Year`, `Month`, `Day`, `Table`, `Column`, `Currency`, `Number`, `Text`, `Boolean`, `True`, `False`, `Blank`, `Error`, `Order`, `Rank`, `Index`, `Format`, `Type`, `Result`, `None`, `All`, `Filter`.

**Rule**: Always use descriptive, context-specific names:
- `Variance` → `SalesBudgetVariance` or `YoYVariance`
- `Status` → `BudgetStatusValue` or `CurrentStatus`
- `Value` → `SalesValue` or `MetricValue`
- `Result` → `CalcResult` or `FinalAmount`

### DIVIDE() Function (MANDATORY)
ALWAYS use `DIVIDE()` instead of the `/` operator:
```dax
-- CORRECT
DIVIDE([Sales Amount], [Budget Amount], 0)

-- WRONG (will error on zero denominator)
[Sales Amount] / [Budget Amount]
```

### CALCULATE Best Practices
- Use `REMOVEFILTERS()` instead of `ALL()` for clearing filter context:
```dax
CALCULATE([Sales Amount], REMOVEFILTERS(Dim_Area))
```
- Use `KEEPFILTERS()` when intersecting with existing context.
- Never combine CALCULATE with ambiguous filter arguments.

---

## 2. Base Aggregation Measures

### SUM
```dax
measure 'Sales Amount' = 
		SUM(Fact_Sales[Sales Amount LC])
```

### COUNT / DISTINCTCOUNT
```dax
measure '# Customers' = 
		DISTINCTCOUNT(Fact_Sales[CustomerKey])

measure '# Transactions' = 
		COUNTROWS(Fact_Sales)
```

### AVERAGE
```dax
measure 'Avg Sales Amount' = 
		AVERAGE(Fact_Sales[Sales Amount LC])
```

---

## 3. Time Intelligence Patterns

### IMPORTANT: Prerequisites
- `Dim_Date` MUST be marked as the Date Table in the model.
- All time intelligence functions reference `Dim_Date[Date]`.
- For fiscal year ending June 30, use `"6/30"` as the year-end date.

### Year-to-Date (YTD)
```dax
measure 'Sales Amount YTD' =
		TOTALYTD(
			[Sales Amount],
			Dim_Date[Date]
		)
```

### Fiscal Year-to-Date (FYTD)
```dax
measure 'Sales Amount FYTD' =
		CALCULATE(
			[Sales Amount],
			DATESYTD(Dim_Date[Date], "6/30")
		)
```

### Previous Year (PY)
```dax
measure 'Sales Amount PY' =
		CALCULATE(
			[Sales Amount],
			SAMEPERIODLASTYEAR(Dim_Date[Date])
		)
```

### Previous Year YTD
```dax
measure 'Sales Amount PYTD' =
		CALCULATE(
			[Sales Amount FYTD],
			SAMEPERIODLASTYEAR(Dim_Date[Date])
		)
```

### Year-over-Year Variance
```dax
measure 'Sales YoY Variance' =
		VAR CurrentYear = [Sales Amount FYTD]
		VAR PreviousYear = [Sales Amount PYTD]
		RETURN
			CurrentYear - PreviousYear
```

### Year-over-Year Variance %
```dax
measure 'Sales YoY Variance %' =
		VAR CurrentYear = [Sales Amount FYTD]
		VAR PreviousYear = [Sales Amount PYTD]
		RETURN
			DIVIDE(
				CurrentYear - PreviousYear,
				PreviousYear,
				0
			)
```

### Month-over-Month
```dax
measure 'Sales Amount PM' =
		CALCULATE(
			[Sales Amount],
			DATEADD(Dim_Date[Date], -1, MONTH)
		)
```

### Monthly Average
```dax
measure 'Avg Monthly Sales' =
		VAR TotalSales = [Sales Amount FYTD]
		VAR MonthCount =
			CALCULATE(
				DISTINCTCOUNT(Dim_Date[Month]),
				DATESYTD(Dim_Date[Date], "6/30")
			)
		RETURN
			DIVIDE(TotalSales, MonthCount, 0)
```

---

## 4. Comparison Patterns

### Actual vs Budget
```dax
measure 'Sales vs Budget' =
		VAR Actual = [Sales Amount FYTD]
		VAR Budget = [Budget Amount FYTD]
		RETURN
			Actual - Budget
```

### Actual vs Budget %
```dax
measure 'Sales vs Budget %' =
		VAR Actual = [Sales Amount FYTD]
		VAR Budget = [Budget Amount FYTD]
		RETURN
			DIVIDE(
				Actual - Budget,
				Budget,
				0
			)
```

---

## 5. Profitability Patterns

### Profit Percentage
```dax
measure 'Adjusted Profit %' =
		VAR Sales = [Sales Amount]
		VAR Profit = [Adjusted Profit]
		RETURN
			DIVIDE(Profit, Sales, 0)
```

---

## 6. Status / Conditional Patterns

### Budget Status Indicator
```dax
measure 'Budget Status' =
		VAR Actual = [Sales Amount FYTD]
		VAR Budget = [Budget Amount FYTD]
		VAR Ratio = DIVIDE(Actual, Budget, 0)
		RETURN
			SWITCH(
				TRUE(),
				Ratio >= 1, "Above Target",
				Ratio >= 0.9, "Close to Target",
				"Below Target"
			)
```

### Status Color (for conditional formatting)
```dax
measure 'Budget Status Color' =
		VAR Status = [Budget Status]
		RETURN
			SWITCH(
				Status,
				"Above Target", "#2ECC71",
				"Close to Target", "#F39C12",
				"Below Target", "#E74C3C",
				"#95A5A6"
			)
```

---

## 7. TMDL Integration

When writing measures in TMDL, follow this exact format:

### Single-line measure:
```tmdl
	measure 'Sales Amount' = SUM(Fact_Sales[Sales Amount LC])
		formatString: #,##0.00
		displayFolder: Sales
		lineageTag: <guid>
```

### Multi-line measure (VAR/RETURN):
```tmdl
	measure 'Sales Amount FYTD' =
			VAR CurrentSales =
				CALCULATE(
					[Sales Amount],
					DATESYTD(Dim_Date[Date], "6/30")
				)
			RETURN
				CurrentSales
		formatString: #,##0.00
		displayFolder: Time Intelligence
		lineageTag: <guid>
```

### Key formatting rules in TMDL:
- Measure declaration at **1 tab** indent (inside table).
- Multi-line DAX expression at **2 tabs** indent.
- Properties (`formatString`, `displayFolder`) back to **2 tabs** indent (aligned with expression start? NO — at **property level = 2 tabs from table, but since measure is 1 tab child, properties are 2 tabs**).

**CORRECTION**: In TMDL, the hierarchy is:
- `table` (level 0, root)
  - `measure` (level 1, 1 tab)
    - Expression lines (level 2, 2 tabs)
  - `formatString` (level 2, 2 tabs — SAME level as expression)

---

## 8. Anti-Patterns (AVOID)

| Anti-Pattern | Better Pattern |
|-------------|---------------|
| `Sales / Budget` | `DIVIDE(Sales, Budget, 0)` |
| `CALCULATE(SUM(...), ALL(Table))` | `CALCULATE(SUM(...), REMOVEFILTERS(Table))` |
| `FILTER(ALL(Table), ...)` for simple filters | Use `CALCULATE` with direct filter |
| Nested CALCULATE without VAR | Use VAR to store intermediate results |
| Hardcoded table references in TIME functions | Always use `Dim_Date[Date]` |
| Using `EARLIER()` | Use VAR instead |
| `IF(condition, value, BLANK())` | `IF(condition, value)` — BLANK is default |
