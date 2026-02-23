# Best Practice Analyzer (BPA) Rules Reference

**Purpose**: Comprehensive reference for Tabular Editor Best Practice Analyzer rules. These rules must be followed when generating TMDL and DAX code to ensure production-quality semantic models.

**Integration Strategy**:
- **Preventive** (Skills 03, 04): Guidelines to follow BEFORE writing TMDL/DAX
- **Detective** (Skill 06): Validation checklist to verify AFTER writing

**Severity Levels**:
- **Error (3)**: ❌ Critical issues that will cause model failures or incorrect results
- **Warning (2)**: ⚠️ Important issues that impact performance or maintainability
- **Info (1)**: ℹ️ Recommendations for best practices and consistency

---

## Category 1: DAX Expressions

### Rule: DAX_FULLY_QUALIFIED_COLUMNS
**ID**: `DAX_FULLY_QUALIFIED_COLUMNS`  
**Severity**: Error (3)  
**Description**: Column references in DAX MUST be fully qualified with table name

**Why**: Unqualified columns can cause ambiguity errors if multiple tables have columns with the same name.

**❌ DON'T** (Anti-pattern):
```dax
measure 'Total Sales' = 
	SUM([SalesAmount])  // ❌ Unqualified column
```

**✅ DO** (Best practice):
```dax
measure 'Total Sales' = 
	SUM(Fact_Sales[SalesAmount])  // ✅ Fully qualified
```

**TMDL Context**: Applies to all measure definitions
```tmdl
measure 'Total Sales' =
	expression:
		```
		SUM(Fact_Sales[SalesAmount])
		```
```

**MCP Verification**: Search `microsoft_docs_search("DAX column reference fully qualified syntax")`

---

### Rule: DAX_DIVISION_COLUMNS
**ID**: `DAX_DIVISION_COLUMNS`  
**Severity**: Error (3)  
**Description**: Division operations MUST use DIVIDE() function, never "/" operator

**Why**: Direct division with "/" throws errors when denominator is zero. DIVIDE() handles division by zero gracefully.

**❌ DON'T** (Anti-pattern):
```dax
measure 'Profit Margin' = 
	SUM(Fact_Sales[Profit]) / SUM(Fact_Sales[Revenue])  // ❌ Unsafe division
```

**✅ DO** (Best practice):
```dax
measure 'Profit Margin' = 
	VAR TotalProfit = SUM(Fact_Sales[Profit])
	VAR TotalRevenue = SUM(Fact_Sales[Revenue])
	RETURN DIVIDE(TotalProfit, TotalRevenue, 0)  // ✅ Safe division with default
```

**MCP Verification**: Search `microsoft_docs_search("DAX DIVIDE function syntax examples")`

---

### Rule: DAX_UNQUALIFIED_MEASURES
**ID**: `DAX_UNQUALIFIED_MEASURES`  
**Severity**: Warning (2)  
**Description**: Measure references in DAX SHOULD be unqualified (no table prefix)

**Why**: Measures are model-level objects, not table-specific. Unqualified syntax improves readability.

**❌ DON'T** (Anti-pattern):
```dax
measure 'Sales YTD' = 
	CALCULATE([Metrics].[Total Sales], DATESYTD(Dim_Date[Date]))  // ❌ Qualified measure
```

**✅ DO** (Best practice):
```dax
measure 'Sales YTD' = 
	CALCULATE([Total Sales], DATESYTD(Dim_Date[Date]))  // ✅ Unqualified measure
```

**MCP Verification**: Search `microsoft_docs_search("DAX measure reference syntax best practices")`

---

### Rule: DAX_TODO_COMMENTS
**ID**: `DAX_TODO_COMMENTS`  
**Severity**: Warning (2)  
**Description**: DAX expressions SHOULD NOT contain TODO/FIXME comments in production

**Why**: TODO comments indicate incomplete implementation. All measures must be production-ready before deployment.

**❌ DON'T** (Anti-pattern):
```dax
measure 'Sales Forecast' = 
	// TODO: Implement forecasting algorithm
	SUM(Fact_Sales[SalesAmount])
```

**✅ DO** (Best practice):
```dax
measure 'Sales Forecast' = 
	VAR HistoricalSales = CALCULATE(SUM(Fact_Sales[SalesAmount]), DATESINPERIOD(...))
	VAR GrowthRate = 0.15
	RETURN HistoricalSales * (1 + GrowthRate)
```

**Detection**: Grep search for `TODO|FIXME|HACK|TEMPORARY` in all measure expressions

---

## Category 2: Formatting

### Rule: OBJECTS_WITH_NO_FORMAT_STRING_COLUMNS
**ID**: `OBJECTS_WITH_NO_FORMAT_STRING_COLUMNS`  
**Severity**: Warning (2)  
**Description**: Numeric columns SHOULD have formatString property defined

**Why**: Format strings ensure consistent display in reports (currency, percentages, decimals).

**❌ DON'T** (Anti-pattern):
```tmdl
column SalesAmount
	dataType: decimal
	summarizeBy: sum
	// ❌ Missing formatString
```

**✅ DO** (Best practice):
```tmdl
column SalesAmount
	dataType: decimal
	summarizeBy: sum
	formatString: "$#,##0.00"  // ✅ Currency format
	
column 'Profit Margin'
	dataType: decimal
	summarizeBy: none
	formatString: "0.00%"  // ✅ Percentage format
```

**Common Format Strings**:
- Currency: `"$#,##0.00"` or `"€#,##0.00"`
- Percentage: `"0.00%"`
- Integer: `"#,##0"`
- Decimal: `"#,##0.00"`

---

### Rule: OBJECTS_WITH_NO_FORMAT_STRING_MEASURES
**ID**: `OBJECTS_WITH_NO_FORMAT_STRING_MEASURES`  
**Severity**: Warning (2)  
**Description**: All measures MUST have formatString property defined

**Why**: Measures represent KPIs that users consume directly. Format strings are mandatory for usability.

**❌ DON'T** (Anti-pattern):
```tmdl
measure 'Total Sales' =
	expression: ```SUM(Fact_Sales[SalesAmount])```
	// ❌ Missing formatString
```

**✅ DO** (Best practice):
```tmdl
measure 'Total Sales' =
	expression: ```SUM(Fact_Sales[SalesAmount])```
	formatString: "$#,##0.00"  // ✅ Currency format
	displayFolder: "Sales Metrics"
```

**MCP Verification**: Search `microsoft_docs_search("Power BI format string syntax DAX")`

---

## Category 3: Metadata

### Rule: SUMMARIZEBY_SHOULD_BE_NONE
**ID**: `SUMMARIZEBY_SHOULD_BE_NONE`  
**Severity**: Warning (2)  
**Description**: Most columns SHOULD have `summarizeBy: none` to prevent accidental aggregations

**Why**: Only measure columns intended for aggregation should allow automatic summarization. Prevents user errors.

**❌ DON'T** (Anti-pattern):
```tmdl
column SalesAmount
	dataType: decimal
	summarizeBy: sum  // ❌ Allows accidental aggregation in visuals
```

**✅ DO** (Best practice):
```tmdl
column SalesAmount
	dataType: decimal
	summarizeBy: none  // ✅ Force users to use explicit measures
	formatString: "$#,##0.00"
	
measure 'Total Sales' =
	expression: ```SUM(Fact_Sales[SalesAmount])```  // ✅ Explicit measure for aggregation
```

**Exceptions**: Columns in dimension tables (Name, Category) can use `summarizeBy: none` always. Fact table numeric columns MUST use `summarizeBy: none`.

---

### Rule: AVOID_FLOAT_DATATYPE
**ID**: `AVOID_FLOAT_DATATYPE`  
**Severity**: Error (3)  
**Description**: Numeric columns MUST use `dataType: decimal`, never `dataType: double`

**Why**: Double (floating-point) introduces rounding errors. Decimal is precise for financial calculations.

**❌ DON'T** (Anti-pattern):
```tmdl
column SalesAmount
	dataType: double  // ❌ Floating-point precision issues
```

**✅ DO** (Best practice):
```tmdl
column SalesAmount
	dataType: decimal  // ✅ Precise for financial data
	summarizeBy: none
	formatString: "$#,##0.00"
```

**Exception**: Scientific data with very large/small values may require `double`, but this is rare in business intelligence.

**MCP Verification**: Search `microsoft_docs_search("Power BI decimal vs double data type precision")`

---

### Rule: DISABLE_ATTRIBUTE_HIERARCHIES
**ID**: `DISABLE_ATTRIBUTE_HIERARCHIES`  
**Severity**: Info (1)  
**Description**: Foreign key columns SHOULD have `isAvailableInMDX: false` to hide from field list

**Why**: Hidden FK columns reduce clutter in Power BI field list. Users should use dimension attributes, not FK integers.

**❌ DON'T** (Anti-pattern):
```tmdl
column ProductKey
	dataType: int64
	isKey: true
	// ❌ Visible in field list, users might drag FK by mistake
```

**✅ DO** (Best practice):
```tmdl
column ProductKey
	dataType: int64
	isKey: true
	isAvailableInMDX: false  // ✅ Hidden from Power BI field list
	summarizeBy: none
```

**Pattern**: Apply to ALL foreign key columns in fact tables.

---

## Category 4: Model Layout

### Rule: HIDE_FOREIGN_KEY_COLUMNS
**ID**: `HIDE_FOREIGN_KEY_COLUMNS`  
**Severity**: Warning (2)  
**Description**: Foreign key columns MUST have `isHidden: true` to hide from report visuals

**Why**: Users should interact with dimension attributes (Product Name), not numeric foreign keys (ProductKey = 1023).

**❌ DON'T** (Anti-pattern):
```tmdl
column ProductKey
	dataType: int64
	isKey: true
	// ❌ Visible, users might accidentally use FK in visuals
```

**✅ DO** (Best practice):
```tmdl
column ProductKey
	dataType: int64
	isKey: true
	isHidden: true  // ✅ Hidden from users
	isAvailableInMDX: false
	summarizeBy: none
```

**Pattern**: Apply to ALL foreign key columns in fact tables. Primary key columns in dimension tables should remain visible if they are natural keys (e.g., ProductCode).

---

### Rule: ORGANIZE_MEASURES_IN_DISPLAY_FOLDERS
**ID**: `ORGANIZE_MEASURES_IN_DISPLAY_FOLDERS`  
**Severity**: Info (1)  
**Description**: Measures SHOULD have `displayFolder` property for logical grouping

**Why**: Display folders organize measures into categories (Sales, Finance, Inventory) for easier discovery.

**❌ DON'T** (Anti-pattern):
```tmdl
measure 'Total Sales' =
	expression: ```SUM(Fact_Sales[SalesAmount])```
	formatString: "$#,##0.00"
	// ❌ No displayFolder, measure appears at root level

measure 'Sales YTD' =
	expression: ```...```
	// ❌ No grouping with related measures
```

**✅ DO** (Best practice):
```tmdl
measure 'Total Sales' =
	expression: ```SUM(Fact_Sales[SalesAmount])```
	formatString: "$#,##0.00"
	displayFolder: "Sales Metrics"  // ✅ Grouped with related measures

measure 'Sales YTD' =
	expression: ```...```
	displayFolder: "Sales Metrics\\Time Intelligence"  // ✅ Nested folders
```

**Common Folder Patterns**:
- `"Sales Metrics"`
- `"Finance\\Profitability"`
- `"Inventory\\Stock Levels"`
- `"Time Intelligence"`

---

### Rule: PROVIDE_DESCRIPTIONS_FOR_MEASURES
**ID**: `PROVIDE_DESCRIPTIONS_FOR_MEASURES`  
**Severity**: Info (1)  
**Description**: Complex measures SHOULD have `description` property explaining business logic

**Why**: Descriptions appear as tooltips in Power BI, helping users understand measure calculations.

**❌ DON'T** (Anti-pattern):
```tmdl
measure 'Sales Same Period Last Year' =
	expression: 
		```
		CALCULATE([Total Sales], SAMEPERIODLASTYEAR(Dim_Date[Date]))
		```
	// ❌ No description, users don't understand time intelligence logic
```

**✅ DO** (Best practice):
```tmdl
measure 'Sales Same Period Last Year' =
	description: "Total sales for the same period in the previous year. Uses SAMEPERIODLASTYEAR time intelligence function."
	expression: 
		```
		CALCULATE([Total Sales], SAMEPERIODLASTYEAR(Dim_Date[Date]))
		```
	formatString: "$#,##0.00"
	displayFolder: "Sales Metrics\\Time Intelligence"
```

**Pattern**: Mandatory for time intelligence measures, optional for simple SUM/COUNT measures.

---

### Rule: CREATE_PERSPECTIVES_FOR_ROLE_SEPARATION
**ID**: `CREATE_PERSPECTIVES_FOR_ROLE_SEPARATION`  
**Severity**: Info (1)  
**Description**: Large models SHOULD define perspectives for different user roles

**Why**: Perspectives simplify field list by showing only relevant tables/measures for specific roles (Sales, Finance).

**TMDL Example**:
```tmdl
perspective Sales =
	table Fact_Sales
	table Dim_Customer
	table Dim_Product
	table Dim_Date
	measure 'Total Sales'
	measure 'Sales YTD'

perspective Finance =
	table Fact_Sales
	table Fact_Budget
	table Dim_Date
	measure 'Total Revenue'
	measure 'Budget Variance'
```

**When to Use**: Models with 10+ tables or multiple user personas.

**MCP Verification**: Search `microsoft_docs_search("Power BI perspectives TMDL definition syntax")`

---

### Rule: PROVIDE_TRANSLATIONS_FOR_GLOBAL_MODELS
**ID**: `PROVIDE_TRANSLATIONS_FOR_GLOBAL_MODELS`  
**Severity**: Info (1)  
**Description**: Multi-language models SHOULD define `culture` and translations

**Why**: Translations enable localized table/column names for international users.

**TMDL Example**:
```tmdl
culture it-IT =
	translation
		table Dim_Product = "Prodotti"
		column Dim_Product.ProductName = "Nome Prodotto"
		measure 'Total Sales' = "Vendite Totali"

culture de-DE =
	translation
		table Dim_Product = "Produkte"
		column Dim_Product.ProductName = "Produktname"
		measure 'Total Sales' = "Gesamtumsatz"
```

**When to Use**: Models deployed to multi-region organizations.

**MCP Verification**: Search `microsoft_docs_search("Power BI translations culture TMDL syntax")`

---

### Rule: USE_LINEAGE_TAG_FOR_VERSION_CONTROL
**ID**: `USE_LINEAGE_TAG_FOR_VERSION_CONTROL`  
**Severity**: Info (1)  
**Description**: All objects SHOULD have `lineageTag` for PBIP version control

**Why**: Lineage tags enable Git to track object changes across commits.

**TMDL Example**:
```tmdl
table Fact_Sales
	lineageTag: a1b2c3d4-e5f6-7890-abcd-ef1234567890
	
	column SalesAmount
		lineageTag: f9e8d7c6-b5a4-3210-9876-543210fedcba
```

**Pattern**: Power BI Desktop auto-generates lineage tags when saving PBIP. Do NOT manually modify.

---

### Rule: ORGANIZE_COLUMNS_IN_DISPLAY_FOLDERS
**ID**: `ORGANIZE_COLUMNS_IN_DISPLAY_FOLDERS`  
**Severity**: Info (1)  
**Description**: Dimension tables with many columns SHOULD use displayFolder for grouping

**Why**: Display folders organize attributes into logical groups (Demographics, Geography, Financial).

**TMDL Example**:
```tmdl
table Dim_Customer
	
	column 'Customer Name'
	column 'Customer Type'
	// ❌ No grouping
	
	column 'Street Address'
		displayFolder: "Geography"  // ✅ Grouped
	column City
		displayFolder: "Geography"
	column Country
		displayFolder: "Geography"
	
	column 'Birth Date'
		displayFolder: "Demographics"
	column Gender
		displayFolder: "Demographics"
```

**When to Use**: Dimension tables with 15+ columns.

---

## Category 5: Naming Conventions

### Rule: TABLE_NAME_MUST_START_WITH_PREFIX
**ID**: `TABLE_NAME_MUST_START_WITH_PREFIX`  
**Severity**: Warning (2)  
**Description**: Tables SHOULD use prefixes: `Fact_`, `Dim_`, `Bridge_`

**Why**: Prefixes instantly identify table role in Star Schema. Critical for maintainability.

**❌ DON'T** (Anti-pattern):
```tmdl
table Sales  // ❌ Missing Fact_ prefix
table Products  // ❌ Missing Dim_ prefix
```

**✅ DO** (Best practice):
```tmdl
table Fact_Sales  // ✅ Fact table
table Dim_Product  // ✅ Dimension table
table Bridge_StudentCourse  // ✅ Bridge/junction table
```

**Official Pattern**: See `.github/references/naming-conventions.md` for full rules.

---

### Rule: USE_PASCALCASE_FOR_OBJECTS
**ID**: `USE_PASCALCASE_FOR_OBJECTS`  
**Severity**: Info (1)  
**Description**: Tables, columns, measures SHOULD use PascalCase (no spaces)

**Why**: Consistency improves readability. Spaces require quoting in DAX ('Table Name').

**❌ DON'T** (Anti-pattern):
```tmdl
table Dim_Product
	column product name  // ❌ Lowercase with space
	column Product_Code  // ❌ Snake_case
```

**✅ DO** (Best practice):
```tmdl
table Dim_Product
	column ProductName  // ✅ PascalCase
	column ProductCode  // ✅ PascalCase
	
measure 'TotalSales' =  // ✅ PascalCase (spaces allowed for measures if needed)
```

**Exception**: Measures can use spaces for readability in Power BI visuals ('Total Sales' instead of 'TotalSales').

---

### Rule: AVOID_RESERVED_KEYWORDS
**ID**: `AVOID_RESERVED_KEYWORDS`  
**Severity**: Error (3)  
**Description**: Object names MUST NOT use DAX/SQL reserved keywords

**Why**: Reserved keywords cause parsing errors. Examples: `Date`, `Table`, `Column`, `Value`, `Index`.

**❌ DON'T** (Anti-pattern):
```tmdl
table Date  // ❌ Reserved keyword
	column Date  // ❌ Reserved keyword
	column Value  // ❌ Reserved keyword
```

**✅ DO** (Best practice):
```tmdl
table Dim_Date  // ✅ Prefix avoids collision
	column DateKey  // ✅ Suffix avoids collision
	column DateValue  // ✅ Descriptive alternative
```

**Common Reserved Keywords**: `Date`, `Time`, `Year`, `Month`, `Table`, `Column`, `Value`, `Key`, `Index`, `User`, `Group`

**MCP Verification**: Search `microsoft_docs_search("DAX reserved keywords list")`

---

### Rule: DATE_COLUMN_NAMED_DATE
**ID**: `DATE_COLUMN_NAMED_DATE`  
**Severity**: Warning (2)  
**Description**: Date dimension SHOULD have column named `Date` (not `DateKey` or `FullDate`)

**Why**: Power BI time intelligence functions require a column named `Date` in the date table.

**❌ DON'T** (Anti-pattern):
```tmdl
table Dim_Date
	column DateKey  // ❌ Wrong name for date column
		dataType: dateTime
```

**✅ DO** (Best practice):
```tmdl
table Dim_Date
	column DateKey  // Surrogate key (int64)
		dataType: int64
		isKey: true
		isHidden: true
	
	column Date  // ✅ Actual date column for time intelligence
		dataType: dateTime
		isKey: false
```

**Pattern**: Date table MUST have both DateKey (int64 surrogate) AND Date (dateTime natural key).

**MCP Verification**: Search `microsoft_docs_search("Power BI date table requirements time intelligence")`

---

### Rule: MEASURE_NAMING_DESCRIPTIVE
**ID**: `MEASURE_NAMING_DESCRIPTIVE`  
**Severity**: Info (1)  
**Description**: Measure names SHOULD be descriptive business terms, not technical abbreviations

**Why**: Users consume measures directly in visuals. Names must be self-explanatory.

**❌ DON'T** (Anti-pattern):
```tmdl
measure 'SA' =  // ❌ Unclear abbreviation
measure 'M1' =  // ❌ Non-descriptive
measure 'Calc_Rev_YTD' =  // ❌ Technical prefix
```

**✅ DO** (Best practice):
```tmdl
measure 'Total Sales' =  // ✅ Clear business term
measure 'Revenue YTD' =  // ✅ Descriptive with context
measure 'Profit Margin %' =  // ✅ Includes unit indicator
```

---

### Rule: AVOID_PLURAL_TABLE_NAMES
**ID**: `AVOID_PLURAL_TABLE_NAMES`  
**Severity**: Info (1)  
**Description**: Table names SHOULD be singular, not plural

**Why**: Dimensional modeling convention. Each row represents ONE entity (Product, not Products).

**❌ DON'T** (Anti-pattern):
```tmdl
table Dim_Products  // ❌ Plural
table Fact_Sales  // ✅ Exception: "Sales" is aggregate noun
```

**✅ DO** (Best practice):
```tmdl
table Dim_Product  // ✅ Singular
table Dim_Customer  // ✅ Singular
table Fact_Sales  // ✅ Acceptable exception
```

**Exception**: Fact tables often use aggregate nouns (Sales, Orders, Transactions) which are plural by nature.

---

## Category 6: Performance

### Rule: AVOID_CALCULATED_COLUMNS_IN_LARGE_FACTS
**ID**: `AVOID_CALCULATED_COLUMNS_IN_LARGE_FACTS`  
**Severity**: Warning (2)  
**Description**: Large fact tables SHOULD NOT contain calculated columns

**Why**: Calculated columns are materialized at refresh time. In large facts (millions of rows), this increases model size and refresh time.

**❌ DON'T** (Anti-pattern):
```tmdl
table Fact_Sales
	
	column SalesAmount
		dataType: decimal
	
	column 'Profit Margin'  // ❌ Calculated column in large fact
		dataType: decimal
		expression: [Profit] / [Revenue]
```

**✅ DO** (Best practice):
```tmdl
table Fact_Sales
	
	column SalesAmount
		dataType: decimal
	
measure 'Profit Margin' =  // ✅ Measure (computed at query time)
	VAR TotalProfit = SUM(Fact_Sales[Profit])
	VAR TotalRevenue = SUM(Fact_Sales[Revenue])
	RETURN DIVIDE(TotalProfit, TotalRevenue)
```

**Exception**: Calculated columns acceptable in dimension tables (< 100K rows) for grouping/filtering.

**MCP Verification**: Search `microsoft_docs_search("Power BI calculated columns vs measures performance")`

---

### Rule: MINIMIZE_BIDIRECTIONAL_RELATIONSHIPS
**ID**: `MINIMIZE_BIDIRECTIONAL_RELATIONSHIPS`  
**Severity**: Warning (2)  
**Description**: Bidirectional relationships SHOULD be avoided unless required for RLS

**Why**: Bidirectional filters create ambiguous filter propagation paths and slow down queries.

**❌ DON'T** (Anti-pattern):
```tmdl
relationship
	fromColumn: Fact_Sales.ProductKey
	toColumn: Dim_Product.ProductKey
	crossFilteringBehavior: bothDirections  // ❌ Bidirectional without RLS justification
```

**✅ DO** (Best practice):
```tmdl
relationship
	fromColumn: Fact_Sales.ProductKey
	toColumn: Dim_Product.ProductKey
	crossFilteringBehavior: oneDirection  // ✅ Single direction (Dim → Fact)
```

**Exception**: Bidirectional acceptable for Row-Level Security scenarios (security table → dimension).

**Reference**: See `.github/references/relationship-patterns.md` Section 4.3 for troubleshooting.

---

### Rule: AVOID_MEASURES_REFERENCING_CALCULATED_COLUMNS
**ID**: `AVOID_MEASURES_REFERENCING_CALCULATED_COLUMNS`  
**Severity**: Warning (2)  
**Description**: Measures SHOULD reference physical columns, not calculated columns

**Why**: Calculated columns are materialized. Referencing them in measures forces context transitions.

**❌ DON'T** (Anti-pattern):
```tmdl
table Fact_Sales
	column 'Extended Price'  // Calculated column
		dataType: decimal
		expression: [Quantity] * [Unit Price]

measure 'Total Extended Price' =  // ❌ References calculated column
	SUM(Fact_Sales[Extended Price])
```

**✅ DO** (Best practice):
```tmdl
measure 'Total Extended Price' =  // ✅ Calculates directly from physical columns
	SUMX(Fact_Sales, Fact_Sales[Quantity] * Fact_Sales[UnitPrice])
```

**Exception**: Calculated columns acceptable for filtering/grouping (e.g., `AgeGroup = IF([Age] < 18, "Child", "Adult")`).

**Reference**: See `.github/references/dax-optimization-framework.md` Section 2 for iterator optimization.

---

### Rule: USE_VARIABLES_TO_AVOID_RECALCULATION
**ID**: `USE_VARIABLES_TO_AVOID_RECALCULATION`  
**Severity**: Info (1)  
**Description**: Measures SHOULD use VAR to store intermediate results

**Why**: Variables are computed once. Reusing expressions without VAR causes multiple evaluations.

**❌ DON'T** (Anti-pattern):
```dax
measure 'Sales vs Target' = 
	IF(
		SUM(Fact_Sales[SalesAmount]) > SUM(Fact_Target[TargetAmount]),  // ❌ Computed twice
		SUM(Fact_Sales[SalesAmount]) - SUM(Fact_Target[TargetAmount]),
		0
	)
```

**✅ DO** (Best practice):
```dax
measure 'Sales vs Target' = 
	VAR ActualSales = SUM(Fact_Sales[SalesAmount])  // ✅ Computed once
	VAR TargetSales = SUM(Fact_Target[TargetAmount])  // ✅ Computed once
	RETURN IF(ActualSales > TargetSales, ActualSales - TargetSales, 0)
```

**Pattern**: Mandatory VAR/RETURN for all measures with repeated expressions.

**Reference**: See `.github/references/dax-optimization-framework.md` Section 1.2 for variable optimization.

---

## Quick Reference Table

| Rule ID | Category | Severity | Preventive File | Detective File | Description |
|---------|----------|----------|-----------------|----------------|-------------|
| `DAX_FULLY_QUALIFIED_COLUMNS` | DAX | Error (3) | 04 | 06 | Columns must be fully qualified |
| `DAX_DIVISION_COLUMNS` | DAX | Error (3) | 04 | 06 | Use DIVIDE() not "/" |
| `DAX_UNQUALIFIED_MEASURES` | DAX | Warning (2) | 04 | 06 | Measures should be unqualified |
| `DAX_TODO_COMMENTS` | DAX | Warning (2) | 04 | 06 | No TODO in production code |
| `OBJECTS_WITH_NO_FORMAT_STRING_COLUMNS` | Formatting | Warning (2) | 03 | 06 | Columns need formatString |
| `OBJECTS_WITH_NO_FORMAT_STRING_MEASURES` | Formatting | Warning (2) | 04 | 06 | Measures need formatString |
| `SUMMARIZEBY_SHOULD_BE_NONE` | Metadata | Warning (2) | 03 | 06 | Use summarizeBy: none |
| `AVOID_FLOAT_DATATYPE` | Metadata | Error (3) | 03 | 06 | Use decimal not double |
| `DISABLE_ATTRIBUTE_HIERARCHIES` | Metadata | Info (1) | 03 | 06 | FK needs isAvailableInMDX: false |
| `HIDE_FOREIGN_KEY_COLUMNS` | Layout | Warning (2) | 03 | 06 | FK needs isHidden: true |
| `ORGANIZE_MEASURES_IN_DISPLAY_FOLDERS` | Layout | Info (1) | 04 | 06 | Measures need displayFolder |
| `PROVIDE_DESCRIPTIONS_FOR_MEASURES` | Layout | Info (1) | 04 | 06 | Complex measures need description |
| `CREATE_PERSPECTIVES_FOR_ROLE_SEPARATION` | Layout | Info (1) | 03 | 06 | Large models need perspectives |
| `PROVIDE_TRANSLATIONS_FOR_GLOBAL_MODELS` | Layout | Info (1) | 03 | 06 | Multi-language needs translations |
| `USE_LINEAGE_TAG_FOR_VERSION_CONTROL` | Layout | Info (1) | 03 | 06 | Objects need lineageTag |
| `ORGANIZE_COLUMNS_IN_DISPLAY_FOLDERS` | Layout | Info (1) | 03 | 06 | Columns need displayFolder |
| `TABLE_NAME_MUST_START_WITH_PREFIX` | Naming | Warning (2) | 03 | 06 | Tables need Fact_/Dim_ prefix |
| `USE_PASCALCASE_FOR_OBJECTS` | Naming | Info (1) | 03, 04 | 06 | Use PascalCase naming |
| `AVOID_RESERVED_KEYWORDS` | Naming | Error (3) | 03 | 06 | No DAX reserved words |
| `DATE_COLUMN_NAMED_DATE` | Naming | Warning (2) | 03 | 06 | Date table needs "Date" column |
| `MEASURE_NAMING_DESCRIPTIVE` | Naming | Info (1) | 04 | 06 | Measures need business names |
| `AVOID_PLURAL_TABLE_NAMES` | Naming | Info (1) | 03 | 06 | Use singular table names |
| `AVOID_CALCULATED_COLUMNS_IN_LARGE_FACTS` | Performance | Warning (2) | 03 | 06 | No calc columns in big facts |
| `MINIMIZE_BIDIRECTIONAL_RELATIONSHIPS` | Performance | Warning (2) | 03 | 06 | Avoid bidirectional filters |
| `AVOID_MEASURES_REFERENCING_CALCULATED_COLUMNS` | Performance | Warning (2) | 04 | 06 | Measures use physical columns |
| `USE_VARIABLES_TO_AVOID_RECALCULATION` | Performance | Info (1) | 04 | 06 | Use VAR for repeated logic |

---

## MCP Verification Workflow

Before writing any TMDL or DAX code, verify syntax against Microsoft official documentation:

```
1. microsoft_docs_search("Power BI TMDL column properties syntax")
2. microsoft_docs_search("DAX DIVIDE function examples")
3. microsoft_docs_search("Power BI format string currency percentage")
4. microsoft_docs_fetch(<url>) // when search returns specific article
```

**Critical Verification Points**:
- TMDL property names (formatString vs format-string)
- DAX function signatures (DIVIDE third parameter)
- Relationship crossFilteringBehavior values
- Date table requirements for time intelligence

---

## Implementation Checklist

**Preventive (Before Writing)**:
- [ ] Review BPA rules for relevant category (DAX/Metadata/Naming)
- [ ] Cross-reference with naming-conventions.md
- [ ] MCP verify unfamiliar syntax
- [ ] Apply BPA-compliant property defaults

**Detective (After Writing)**:
- [ ] Run validation checklist in Skill 06
- [ ] Check all Error (3) rules (zero tolerance)
- [ ] Review Warning (2) rules (fix critical ones)
- [ ] Document Info (1) exceptions with justification

---

## Anti-Patterns Summary

| ❌ DON'T | ✅ DO | Rule |
|----------|-------|------|
| `SUM([Column])` | `SUM(Table[Column])` | DAX_FULLY_QUALIFIED_COLUMNS |
| `[Profit] / [Revenue]` | `DIVIDE([Profit], [Revenue])` | DAX_DIVISION_COLUMNS |
| `dataType: double` | `dataType: decimal` | AVOID_FLOAT_DATATYPE |
| `summarizeBy: sum` | `summarizeBy: none` | SUMMARIZEBY_SHOULD_BE_NONE |
| `table Products` | `table Dim_Product` | TABLE_NAME_MUST_START_WITH_PREFIX |
| Calculated column in Fact | Measure instead | AVOID_CALCULATED_COLUMNS_IN_LARGE_FACTS |
| `crossFilteringBehavior: bothDirections` | `crossFilteringBehavior: oneDirection` | MINIMIZE_BIDIRECTIONAL_RELATIONSHIPS |
| Missing formatString | `formatString: "$#,##0.00"` | OBJECTS_WITH_NO_FORMAT_STRING |

---

## Version Control

**File**: `.github/references/bpa-rules-reference.md`  
**Created**: 2026-02-22  
**Purpose**: Comprehensive BPA rules reference for semantic model quality assurance  
**Dependencies**: 
- Tabular Editor BPA rules (`<ProjectName>/PBIP/BPARules-standard.json`)
- `.github/references/naming-conventions.md`
- `.github/references/dax-optimization-framework.md`
- `.github/references/relationship-patterns.md`
