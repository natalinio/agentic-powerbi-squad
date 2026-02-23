# Skill: Physical Model & TMDL Development

## Prerequisites — MANDATORY
Before writing ANY TMDL code:
1. **Read** `.github/references/tmdl-syntax-reference.md` — contains validated syntax templates.
2. **Read** `.github/references/naming-conventions.md` — contains naming rules for all objects.
3. **Read** `.github/references/pbip-folder-structure.md` — defines output folder structure.
4. **Verify** any uncertain syntax using `microsoft_docs_search` MCP tool with query: `"TMDL <object_type> definition syntax"`.

## TMDL Syntax Critical Rules

TMDL is **whitespace-sensitive**. Violations cause Power BI Desktop parsing failures.

### Indentation
- Use **single TAB** for each indentation level. Do NOT use spaces.
- Level 1: Object declaration (table, relationship) — NO indentation (root level).
- Level 2: Object properties — ONE tab indent.
- Level 3: Multi-line expressions — TWO tabs indent.

### Object Hierarchy (no indentation required at root)
These objects are root-level (no indentation):
- `model`, `table`, `relationship`, `expression`, `role`, `culture`, `perspective`, `database`

### Property Delimiters
- Colon (`:`) for non-expression properties: `dataType: int64`
- Equals (`=`) for expressions and default properties: `measure Sales = SUM(...)`

### Naming
- Object names with spaces, dots, equals, or colons MUST be enclosed in single quotes: `'Sales Amount'`
- Single quotes in names are escaped by doubling: `'Customer''s Name'`

## File Generation Rules

Generate the following TMDL files inside `PBIP/<ProjectName>.SemanticModel/definition/`:

### 1. `database.tmdl`
```tmdl
database <ProjectName>
	compatibilityLevel: 1567
```

### 2. `model.tmdl`
```tmdl
model Model
	culture: en-US

ref table Dim_Date
ref table Dim_Customer
ref table Fact_Sales
ref table _Measures
```

### 3. `tables/<TableName>.tmdl` (one file per table)

#### Dimension Table Template:
```tmdl
/// Date dimension for time intelligence analysis
table Dim_Date
	lineageTag: <generate-guid>

	column DateKey
		dataType: int64
		isKey
		isHidden
		sourceColumn: DateKey
		summarizeBy: none
		lineageTag: <generate-guid>

	column Date
		dataType: dateTime
		formatString: yyyy-MM-dd
		sourceColumn: Date
		summarizeBy: none
		lineageTag: <generate-guid>

	column Year
		dataType: string
		sourceColumn: Year
		summarizeBy: none
		lineageTag: <generate-guid>

	partition Dim_Date = m
		mode: import
		source =
			let
				Source = Csv.Document(File.Contents("<absolute-path-to-data>/dim_date.csv"), [Delimiter = ",", Columns = 12, Encoding = 65001, QuoteStyle = QuoteStyle.None]),
				PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
				ChangedTypes = Table.TransformColumnTypes(PromotedHeaders, {{"DateKey", Int64.Type}, {"Date", type datetime}})
			in
				ChangedTypes
```

#### Fact Table Template:
```tmdl
/// Sales transactions at daily grain per customer
table Fact_Sales
	lineageTag: <generate-guid>

	column SalesKey
		dataType: int64
		isHidden
		sourceColumn: SalesKey
		summarizeBy: none
		lineageTag: <generate-guid>

	column DateKey
		dataType: int64
		isHidden
		sourceColumn: DateKey
		summarizeBy: none
		lineageTag: <generate-guid>

	column CustomerKey
		dataType: int64
		isHidden
		sourceColumn: CustomerKey
		summarizeBy: none
		lineageTag: <generate-guid>

	column 'Sales Amount LC'
		dataType: decimal
		formatString: #,##0.00
		sourceColumn: SalesAmountLC
		summarizeBy: sum
		lineageTag: <generate-guid>

	partition Fact_Sales = m
		mode: import
		source =
			let
				Source = Csv.Document(File.Contents("<absolute-path-to-data>/fact_sales.csv"), [Delimiter = ",", Columns = 8, Encoding = 65001, QuoteStyle = QuoteStyle.None]),
				PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
				ChangedTypes = Table.TransformColumnTypes(PromotedHeaders, {{"SalesKey", Int64.Type}, {"DateKey", Int64.Type}, {"SalesAmountLC", type number}})
			in
				ChangedTypes
```

#### Measures Table Template (disconnected):
```tmdl
/// Disconnected table for DAX measures
table _Measures

	measure 'Placeholder' = 0
		lineageTag: <generate-guid>

	partition _Measures = m
		mode: import
		source =
			let
				Source = #table({"MeasuresColumn"}, {{""}})
			in
				Source
```

### 4. `relationships.tmdl`
```tmdl
relationship <generate-guid>
	fromColumn: Fact_Sales.DateKey
	toColumn: Dim_Date.DateKey

relationship <generate-guid>
	fromColumn: Fact_Sales.CustomerKey
	toColumn: Dim_Customer.CustomerKey
```

### 5. `expressions.tmdl` (if needed for shared M expressions/parameters)
```tmdl
expression DataPath = "<absolute-path-to-data>" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true]
```

## Relationship Rules
- ALL relationships: **Single-directional** (Dimension filters Fact). 
- Direction: `fromColumn` is the FK in the Fact table, `toColumn` is the PK in the Dimension table.
- Use **bi-directional** ONLY if explicitly required for RLS scenarios (add `crossFilteringBehavior: bothDirections`).
- Cardinality: Always **Many-to-One** (Fact to Dim). Add `fromCardinality: many` and `toCardinality: one` only when not default.

## Data Type Mapping
| Spec Type | TMDL dataType | Power Query Type |
|-----------|---------------|-----------------|
| Integer / ID / Key | `int64` | `Int64.Type` |
| Decimal / Currency | `decimal` | `type number` |
| String / Text | `string` | `type text` |
| Date | `dateTime` | `type datetime` |
| Boolean | `boolean` | `type logical` |
| Percentage | `double` | `type number` |

## GUID Generation
- For `lineageTag` properties, generate a new random GUID for each object.
- For relationship names, use a GUID as the relationship identifier.

## BPA Compliance Guidelines (Preventive)

**CRITICAL**: Before writing ANY TMDL code, review the following Best Practice Analyzer rules from `.github/references/bpa-rules-reference.md`. These guidelines ensure production-quality semantic models.

### Metadata Rules (Error Severity)

1. **AVOID_FLOAT_DATATYPE** (Error): Use `dataType: decimal` for ALL numeric columns (amounts, quantities). NEVER use `dataType: double` (causes rounding errors in financial calculations).

```tmdl
✅ DO:
column SalesAmount
	dataType: decimal  // Precise for finance
	summarizeBy: none
	formatString: "$#,##0.00"

❌ DON'T:
column SalesAmount
	dataType: double  // Floating-point precision issues
```

2. **SUMMARIZEBY_SHOULD_BE_NONE** (Warning): ALL columns SHOULD have `summarizeBy: none` to prevent accidental aggregations. Force users to use explicit measures.

```tmdl
✅ DO:
column SalesAmount
	dataType: decimal
	summarizeBy: none  // Prevents accidental SUM in visuals

❌ DON'T:
column SalesAmount
	dataType: decimal
	summarizeBy: sum  // Users might drag column directly
```

### Model Layout Rules (Warning Severity)

3. **HIDE_FOREIGN_KEY_COLUMNS** (Warning): ALL foreign key columns in fact tables MUST have `isHidden: true`. Users should interact with dimension attributes, not numeric FKs.

```tmdl
✅ DO:
column ProductKey
	dataType: int64
	isKey: true
	isHidden: true  // Hidden from field list
	isAvailableInMDX: false
	summarizeBy: none

❌ DON'T:
column ProductKey
	dataType: int64
	isKey: true
	// Missing isHidden, users see FK numbers
```

4. **DISABLE_ATTRIBUTE_HIERARCHIES** (Info): Foreign key columns SHOULD have `isAvailableInMDX: false` to hide from MDX queries and reduce field list clutter.

5. **OBJECTS_WITH_NO_FORMAT_STRING_COLUMNS** (Warning): Numeric columns SHOULD have `formatString` property for consistent display.

```tmdl
✅ DO:
column SalesAmount
	dataType: decimal
	summarizeBy: none
	formatString: "$#,##0.00"  // Currency format

column 'Profit Margin'
	dataType: decimal
	summarizeBy: none
	formatString: "0.00%"  // Percentage format
```

**Common Format Strings**:
- Currency: `"$#,##0.00"` or `"€#,##0.00"`
- Percentage: `"0.00%"`
- Integer: `"#,##0"`
- Decimal: `"#,##0.00"`
- Date: `"yyyy-MM-dd"`

### Naming Convention Rules

6. **TABLE_NAME_MUST_START_WITH_PREFIX** (Warning): Tables MUST use prefixes `Fact_`, `Dim_`, `Bridge_`. See `.github/references/naming-conventions.md`.

7. **AVOID_RESERVED_KEYWORDS** (Error): Object names MUST NOT use DAX/SQL reserved keywords (`Date`, `Table`, `Value`, `Column`, `Year`, `Month`, etc.). Use prefixes/suffixes to avoid collisions.

```tmdl
✅ DO:
table Dim_Date  // Prefix avoids reserved keyword
	column DateKey
	column DateValue

❌ DON'T:
table Date  // Reserved keyword
	column Date  // Reserved keyword
	column Value  // Reserved keyword
```

8. **DATE_COLUMN_NAMED_DATE** (Warning): Date dimension MUST have a column named `Date` (dataType: dateTime) for Power BI time intelligence functions.

```tmdl
✅ DO:
table Dim_Date
	column DateKey  // Surrogate key (int64)
		dataType: int64
		isKey: true
		isHidden: true
	
	column Date  // Natural key for time intelligence
		dataType: dateTime
		formatString: "yyyy-MM-dd"
```

### Performance Rules

9. **AVOID_CALCULATED_COLUMNS_IN_LARGE_FACTS** (Warning): Large fact tables (> 1M rows) SHOULD NOT contain calculated columns. Use measures instead (computed at query time, not materialized at refresh).

```tmdl
❌ DON'T (in Large Fact):
column 'Profit Margin'  // Calculated column
	dataType: decimal
	expression: [Profit] / [Revenue]

✅ DO (as Measure):
measure 'Profit Margin' =
	VAR TotalProfit = SUM(Fact_Sales[Profit])
	VAR TotalRevenue = SUM(Fact_Sales[Revenue])
	RETURN DIVIDE(TotalProfit, TotalRevenue)
```

10. **MINIMIZE_BIDIRECTIONAL_RELATIONSHIPS** (Warning): Relationships SHOULD be single-directional (`crossFilteringBehavior: oneDirection`) unless required for RLS.

```tmdl
✅ DO:
relationship
	fromColumn: Fact_Sales.ProductKey
	toColumn: Dim_Product.ProductKey
	crossFilteringBehavior: oneDirection  // Default, best performance

❌ DON'T:
relationship
	fromColumn: Fact_Sales.ProductKey
	toColumn: Dim_Product.ProductKey
	crossFilteringBehavior: bothDirections  // Only for RLS scenarios
```

### Template Compliance Checklist

Before writing TMDL tables, ensure templates include:

**Dimension Table Column Template**:
```tmdl
column <AttributeName>
	dataType: <string|int64|dateTime|decimal>
	summarizeBy: none  // BPA: Prevent accidental aggregation
	formatString: "<format>"  // BPA: Required for numeric columns
	sourceColumn: <AttributeName>
	lineageTag: <guid>
```

**Fact Table Foreign Key Template**:
```tmdl
column <DimensionKey>
	dataType: int64
	isHidden: true  // BPA: Hide FK from field list
	isAvailableInMDX: false  // BPA: Disable attribute hierarchy
	summarizeBy: none  // BPA: Prevent aggregation
	sourceColumn: <DimensionKey>
	lineageTag: <guid>
```

**Fact Table Measure Column Template**:
```tmdl
column <MeasureColumn>
	dataType: decimal  // BPA: Use decimal not double
	formatString: "$#,##0.00"  // BPA: Required formatString
	summarizeBy: none  // BPA: Force explicit measures
	sourceColumn: <MeasureColumn>
	lineageTag: <guid>
```

**MCP Verification**: Before finalizing TMDL code, search `microsoft_docs_search("Power BI TMDL column properties syntax dataType formatString")` to verify property names and syntax.

---

## Validation Before Output
- [ ] All TMDL files use TAB indentation (not spaces)
- [ ] All object names follow naming conventions
- [ ] All surrogate keys are `int64` with `summarizeBy: none`
- [ ] All fact columns that are FKs are `isHidden` and `isAvailableInMDX: false` (BPA)
- [ ] All numeric columns use `dataType: decimal` not `double` (BPA)
- [ ] All columns have `summarizeBy: none` (BPA)
- [ ] All numeric columns have `formatString` property (BPA)
- [ ] All relationships are single-directional unless RLS required (BPA)
- [ ] No calculated columns in large fact tables (BPA)
- [ ] No reserved keywords in object names (BPA)
- [ ] All partition sources point to correct CSV file paths
- [ ] Relationship `fromColumn`/`toColumn` reference existing columns
- [ ] `Dim_Date` has `isKey` on `DateKey` AND column named `Date` for time intelligence (BPA)

**STOP here. Await user validation before proceeding to Step 4.**