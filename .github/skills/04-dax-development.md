# Skill: DAX KPIs and Measures Development

## Prerequisites — MANDATORY
Before writing ANY DAX code:
1. **Read** `.github/references/dax-patterns.md` for validated DAX patterns.
2. **Read** `.github/references/naming-conventions.md` for measure naming rules.
3. **Search** Microsoft documentation with `microsoft_docs_search` for any DAX function you are uncertain about.
4. **Search** for code examples with `microsoft_code_sample_search` when implementing time intelligence or complex calculations.

## Measures Table

- ALL DAX measures MUST be created inside a **disconnected table** named `_Measures`.
- This table has NO data relationships — it is purely a container for measures.
- The `_Measures` table TMDL is defined in `tables/_Measures.tmdl`.

## DAX Coding Standards

### Formatting
- ALL DAX code MUST be formatted across **multiple lines** for readability.
- Use **VAR / RETURN** pattern for all non-trivial measures.
- One expression per line.
- Indent consistently with tabs.

### VAR Naming — Reserved Keywords (ZERO TOLERANCE)
**NEVER** use DAX reserved keywords or function names as VAR names. Power BI Desktop will report *"'<Name>' is a reserved word"* compile errors.

**Forbidden VAR names** (non-exhaustive): `Variance`, `Status`, `Value`, `Date`, `Time`, `Year`, `Month`, `Day`, `Table`, `Column`, `Currency`, `Number`, `Text`, `Boolean`, `True`, `False`, `Blank`, `Error`, `Order`, `Rank`, `Index`, `Format`, `Type`, `Result`, `None`, `All`, `Filter`.

**Rule**: Always use descriptive, business-context prefixed names:
- `Variance` → `SalesBudgetVariance`
- `Status` → `BudgetStatusValue`
- `Value` → `MetricValue`
- `Result` → `CalcResult`

### DAX Comments (Allowed)
- **DAX expressions support comments**: `//` for single-line, `/* */` for multi-line.
- Use comments to explain complex business logic, time intelligence parameters, or non-obvious calculations.
- **TMDL structure does NOT support comments**: Do NOT add `///` comments before measure declarations (outside the DAX expression).

**Example**:
```tmdl
measure 'Sales Amount FYTD' =
		// Calculate fiscal year-to-date sales using dynamic fiscal year parameter
		VAR FiscalYearEndMonth =
			VAR FYStartMonth = SELECTEDVALUE(Parameters[ParameterValue], "1")
			VAR StartMonthNum = VALUE(FYStartMonth)
			VAR EndMonth = IF(StartMonthNum = 1, 12, StartMonthNum - 1)
			RETURN FORMAT(EndMonth, "0") & "/30"  // Format as MM/DD
		VAR FYTDSales =
			CALCULATE(
				[Sales Amount],
				DATESYTD(Dim_Date[Date], FiscalYearEndMonth)
			)
		RETURN FYTDSales
	formatString: "#,##0.00"
	displayFolder: "Time Intelligence"
```

### Example:
```tmdl
	measure 'Sales Amount FYTD' =
			VAR CurrentDate = MAX(Dim_Date[Date])
			VAR FYTDSales =
				CALCULATE(
					[Sales Amount],
					DATESYTD(Dim_Date[Date], "6/30")
				)
			RETURN
				FYTDSales
		formatString: #,##0.00
		displayFolder: Sales
		lineageTag: <generate-guid>
```

### Division Safety
- **ALWAYS** use `DIVIDE(numerator, denominator, 0)` instead of `/` operator.
- This prevents division-by-zero errors.

### Time Intelligence
- Assume `Dim_Date` is marked as the official **Date Table** in the model.
- Use standard time intelligence functions:
  - **YTD**: `TOTALYTD([Measure], Dim_Date[Date])` or `DATESYTD(Dim_Date[Date])` for fiscal year: `DATESYTD(Dim_Date[Date], "6/30")`
  - **Previous Year**: `CALCULATE([Measure], SAMEPERIODLASTYEAR(Dim_Date[Date]))`
  - **Month-over-Month**: `CALCULATE([Measure], DATEADD(Dim_Date[Date], -1, MONTH))`
  - **YoY Variance**: Use VAR pattern to calculate both periods, then subtract.

### ⚠️ Time Intelligence with Dynamic Parameters (CRITICAL)

**WARNING**: Functions like `DATESYTD`, `TOTALYTD`, `DATESMTD`, `TOTALMTD` require **constant literal values** for year-end date parameters. They do NOT accept variables or dynamic expressions.

**Example of ERROR**:
```dax
❌ WRONG (causes warning: "Only constant date value is allowed"):
VAR FiscalYearEndMonth = ... // Dynamic calculation
RETURN
    CALCULATE([Sales Amount], DATESYTD(Dim_Date[Date], FiscalYearEndMonth))
```

**Solution**: Use manual filtering logic when parameters must be dynamic:

```dax
✅ CORRECT (supports dynamic fiscal year parameters):
measure 'Sales Amount FYTD' =
    // Manual fiscal YTD calculation with dynamic parameter support
    VAR CurrentDate = MAX(Dim_Date[Date])
    VAR FYStartMonth = VALUE(SELECTEDVALUE(Parameters[ParameterValue], "1"))
    VAR CurrentYear = YEAR(CurrentDate)
    VAR CurrentMonth = MONTH(CurrentDate)
    // Calculate current fiscal year
    VAR FiscalYear = 
        IF(
            CurrentMonth >= FYStartMonth,
            CurrentYear,
            CurrentYear - 1
        )
    VAR FYStartDate = DATE(FiscalYear, FYStartMonth, 1)
    VAR Result =
        CALCULATE(
            [Sales Amount],
            FILTER(
                ALL(Dim_Date[Date]),
                Dim_Date[Date] >= FYStartDate && Dim_Date[Date] <= CurrentDate
            )
        )
    RETURN Result
```

**Functions Requiring Constant Parameters**:
- `DATESYTD(dates, [year_end_date])` → year_end_date must be literal like `"6/30"`
- `TOTALYTD(expression, dates, [year_end_date])` → year_end_date must be literal
- `DATESMTD`, `TOTALMTD`, `DATESQTD`, `TOTALQTD` → No year-end parameter, but similar optimization constraints

**When to Use Manual Logic**:
- Fiscal year start month is user-selectable (parameter table)
- Multiple fiscal year scenarios in same model
- Dynamic calendar logic based on business rules

**When `DATESYTD` is OK**:
- Fixed fiscal year end (e.g., always June 30): `DATESYTD(Dim_Date[Date], "6/30")`
- Calendar year only: `DATESYTD(Dim_Date[Date])` (defaults to Dec 31)

### Filter Context
- Use `CALCULATE()` with explicit filter modifications.
- Use `REMOVEFILTERS()` instead of `ALL()` when clearing filters on a table.
- Use `KEEPFILTERS()` when you need to intersect with existing filters.
- NEVER use `FILTER(ALL(...))` when `REMOVEFILTERS` + `VALUES` achieves the same result more efficiently.

### Measure Dependencies
- Base measures should be defined FIRST, then composite measures reference them.
- Example order:
  1. `Sales Amount` (base)
  2. `Sales Amount FYTD` (time intelligence on base)
  3. `Sales vs Budget` (comparison using two bases)
  4. `Sales vs Budget %` (percentage using DIVIDE)

## Measure Naming Conventions

Follow `.github/references/naming-conventions.md`. Summary:
- **Base measures**: Descriptive name — `'Sales Amount'`, `'Total Quantity'`
- **Time intelligence**: Suffix with period — `'Sales Amount FYTD'`, `'Sales Amount PY'`
- **Percentages**: Suffix with `%` — `'Adjusted Profit %'`
- **Variance**: Suffix with `vs` — `'Sales vs Budget'`, `'Sales vs Budget %'`
- **Count measures**: Prefix with `#` or `Count of` — `'# Customers'`, `'Count of Transactions'`

## Display Folders

Organize measures into `displayFolder` categories:
- `Sales` — revenue and volume measures
- `Budget` — budget comparison measures
- `Profitability` — margin and profit measures
- `Time Intelligence` — YTD, PY, MoM variants

## Conditional Formatting Support

For KPIs with status indicators (above/below target), create helper measures:
```dax
measure 'Budget Status' =
		VAR SalesVal = [Sales Amount FYTD]
		VAR BudgetVal = [Budget Amount FYTD]
		VAR Ratio = DIVIDE(SalesVal, BudgetVal, 0)
		RETURN
			SWITCH(
				TRUE(),
				Ratio >= 1, "Above Target",
				Ratio >= 0.9, "Close to Target",
				"Below Target"
			)
	lineageTag: <generate-guid>
```

## BPA Compliance Checklist (Preventive)

**CRITICAL**: Before writing ANY DAX code, review the following Best Practice Analyzer rules from `.github/references/bpa-rules-reference.md`. These guidelines ensure production-quality measures.

### DAX Expression Rules (Error/Warning Severity)

1. **DAX_FULLY_QUALIFIED_COLUMNS** (Error): Column references MUST be fully qualified with table name. Unqualified columns cause ambiguity errors.

```dax
✅ DO:
measure 'Total Sales' = 
	SUM(Fact_Sales[SalesAmount])  // Fully qualified

❌ DON'T:
measure 'Total Sales' = 
	SUM([SalesAmount])  // Ambiguous if multiple tables have SalesAmount
```

2. **DAX_DIVISION_COLUMNS** (Error): Division operations MUST use `DIVIDE()` function, NEVER `/` operator. `DIVIDE()` handles division-by-zero gracefully.

```dax
✅ DO:
measure 'Profit Margin' = 
	VAR TotalProfit = SUM(Fact_Sales[Profit])
	VAR TotalRevenue = SUM(Fact_Sales[Revenue])
	RETURN DIVIDE(TotalProfit, TotalRevenue, 0)  // Safe with default

❌ DON'T:
measure 'Profit Margin' = 
	SUM(Fact_Sales[Profit]) / SUM(Fact_Sales[Revenue])  // Throws error if denominator = 0
```

3. **DAX_UNQUALIFIED_MEASURES** (Warning): Measure references SHOULD be unqualified (no table prefix). Measures are model-level objects.

```dax
✅ DO:
measure 'Sales YTD' = 
	CALCULATE([Total Sales], DATESYTD(Dim_Date[Date]))  // Unqualified measure

❌ DON'T:
measure 'Sales YTD' = 
	CALCULATE([_Measures].[Total Sales], DATESYTD(Dim_Date[Date]))  // Unnecessary table prefix
```

4. **DAX_TODO_COMMENTS** (Warning): DAX expressions SHOULD NOT contain TODO/FIXME comments in production. All measures must be production-ready.

```dax
❌ DON'T:
measure 'Sales Forecast' = 
	// TODO: Implement forecasting algorithm
	SUM(Fact_Sales[SalesAmount])

✅ DO:
measure 'Sales Forecast' = 
	VAR HistoricalSales = CALCULATE(
		SUM(Fact_Sales[SalesAmount]),
		DATESINPERIOD(Dim_Date[Date], MAX(Dim_Date[Date]), -12, MONTH)
	)
	VAR GrowthRate = 0.15
	RETURN HistoricalSales * (1 + GrowthRate)
```

### Formatting Rules (Warning Severity)

5. **OBJECTS_WITH_NO_FORMAT_STRING_MEASURES** (Warning): ALL measures MUST have `formatString` property. Critical for usability in Power BI visuals.

```tmdl
✅ DO:
measure 'Total Sales' =
	expression: ```SUM(Fact_Sales[SalesAmount])```
	formatString: "$#,##0.00"  // Currency format
	displayFolder: "Sales Metrics"

❌ DON'T:
measure 'Total Sales' =
	expression: ```SUM(Fact_Sales[SalesAmount])```
	// Missing formatString
```

**Common Format Strings**:
- Currency: `"$#,##0.00"` or `"€#,##0.00"`
- Percentage: `"0.00%"`
- Integer count: `"#,##0"`
- Decimal: `"#,##0.00"`
- No decimal: `"#,##0"`

### Layout Rules (Info Severity)

6. **ORGANIZE_MEASURES_IN_DISPLAY_FOLDERS** (Info): Measures SHOULD have `displayFolder` property for logical grouping.

```tmdl
✅ DO:
measure 'Total Sales' =
	expression: ```SUM(Fact_Sales[SalesAmount])```
	formatString: "$#,##0.00"
	displayFolder: "Sales Metrics"  // Grouped

measure 'Sales YTD' =
	expression: ```CALCULATE([Total Sales], DATESYTD(Dim_Date[Date]))```
	formatString: "$#,##0.00"
	displayFolder: "Sales Metrics\\Time Intelligence"  // Nested folder
```

**Common Folder Patterns**:
- `"Sales Metrics"`
- `"Finance\\Profitability"`
- `"Inventory\\Stock Levels"`
- `"Time Intelligence"`
- `"KPIs"`

7. **PROVIDE_DESCRIPTIONS_FOR_MEASURES** (Info): Complex measures (time intelligence, statistical calculations) SHOULD have `description` property. Appears as tooltip in Power BI.

```tmdl
✅ DO:
measure 'Sales Same Period Last Year' =
	description: "Total sales for the same period in the previous year"
	expression: 
		```
		CALCULATE([Total Sales], SAMEPERIODLASTYEAR(Dim_Date[Date]))
		```
	formatString: "$#,##0.00"
	displayFolder: "Sales Metrics\\Time Intelligence"
```

### Naming Convention Rules

8. **MEASURE_NAMING_DESCRIPTIVE** (Info): Measure names SHOULD be descriptive business terms, not technical abbreviations.

```tmdl
✅ DO:
measure 'Total Sales' =  // Clear business term
measure 'Revenue YTD' =  // Descriptive with context
measure 'Profit Margin %' =  // Includes unit indicator

❌ DON'T:
measure 'SA' =  // Unclear abbreviation
measure 'M1' =  // Non-descriptive
measure 'Calc_Rev_YTD' =  // Technical prefix
```

### Performance Rules

9. **AVOID_MEASURES_REFERENCING_CALCULATED_COLUMNS** (Warning): Measures SHOULD reference physical columns, not calculated columns (causes context transitions).

```dax
❌ DON'T:
// If Fact_Sales has calculated column [Extended Price] = [Quantity] * [UnitPrice]
measure 'Total Extended Price' = 
	SUM(Fact_Sales[Extended Price])  // References calculated column

✅ DO:
measure 'Total Extended Price' = 
	SUMX(Fact_Sales, Fact_Sales[Quantity] * Fact_Sales[UnitPrice])  // Direct calculation
```

10. **USE_VARIABLES_TO_AVOID_RECALCULATION** (Info): Measures SHOULD use VAR to store intermediate results. Variables are computed once.

```dax
❌ DON'T:
measure 'Sales vs Target' = 
	IF(
		SUM(Fact_Sales[SalesAmount]) > SUM(Fact_Target[TargetAmount]),
		SUM(Fact_Sales[SalesAmount]) - SUM(Fact_Target[TargetAmount]),  // Computed twice
		0
	)

✅ DO:
measure 'Sales vs Target' = 
	VAR ActualSales = SUM(Fact_Sales[SalesAmount])  // Computed once
	VAR TargetSales = SUM(Fact_Target[TargetAmount])  // Computed once
	RETURN IF(ActualSales > TargetSales, ActualSales - TargetSales, 0)
```

### Measure Template (BPA-Compliant)

Use this template for ALL measures:

```tmdl
measure '<Descriptive Business Name>' =
	description: "<Business logic explanation for complex measures>"
	expression:
		```
		VAR <IntermediateResult1> = <Expression using Table[Column]>
		VAR <IntermediateResult2> = <Expression>
		RETURN
			DIVIDE(<Numerator>, <Denominator>, <DefaultValue>)
		```
	formatString: "<$#,##0.00 | 0.00% | #,##0>"
	displayFolder: "<Category>\\<Subcategory>"
	lineageTag: <generate-guid>
```

### MCP Verification Workflow

Before finalizing DAX code, verify syntax with MCP:

```
1. microsoft_docs_search("DAX DIVIDE function syntax examples")
2. microsoft_docs_search("DAX time intelligence DATESYTD fiscal year")
3. microsoft_docs_search("Power BI measure format string currency percentage")
4. microsoft_code_sample_search("DAX YTD calculation example")
```

**Reference**: See `.github/references/dax-optimization-framework.md` for comprehensive performance optimization patterns.

---

## Validation Before Output
- [ ] All measures use VAR/RETURN pattern (BPA)
- [ ] All divisions use DIVIDE() function (BPA)
- [ ] All column references are fully qualified `Table[Column]` (BPA)
- [ ] All measure references are unqualified `[Measure]` (BPA)
- [ ] No TODO/FIXME comments in production code (BPA)
- [ ] All measures have `formatString` property (BPA)
- [ ] All measures have `displayFolder` property (BPA)
- [ ] Complex measures have `description` property (BPA)
- [ ] Measure names are descriptive business terms (BPA)
- [ ] Variables used for repeated expressions (BPA)
- [ ] Time intelligence references Dim_Date[Date]
- [ ] Measure names follow naming conventions
- [ ] No circular references between measures
- [ ] All referenced columns exist in the model
- [ ] No references to calculated columns in large fact tables (BPA)

## Artifact Checkpointing (MANDATORY)

**BEFORE presenting results to the user**, the agent MUST:

1. **VERIFY** `_Measures.tmdl` has been written to `<ProjectName>/PBIP/<ProjectName>.SemanticModel/definition/tables/_Measures.tmdl`.
2. **UPDATE** `<ProjectName>/workflow_state.json`:
   - Set `pendingStep` to Step 04 completed.
   - Add artifact path for `_Measures.tmdl`.
3. **CONFIRM** to the user that the DAX measures file has been saved.

## Context Flushing Rule

When starting this step, the agent MUST:
- **READ** `<ProjectName>/workflow_state.json` to verify Steps 01-03 are completed.
- **READ** TMDL table files from disk to know existing columns and tables (NOT from chat memory).
- **READ** `<ProjectName>/spec/requirements_summary.md` for KPI definitions.
- **DO NOT** rely on chat history for any data from previous steps.

**STOP here. Await user validation before proceeding to Step 5.**