# TMDL Syntax Reference — Validated Templates

> This file contains **verified TMDL syntax** extracted from official Microsoft documentation.
> Source: https://learn.microsoft.com/analysis-services/tmdl/tmdl-overview
> 
> **ALWAYS cross-reference this file before generating TMDL code.**

---

## ⛔ CRITICAL: Comments NOT Supported in TMDL

**TMDL does NOT support comments of any kind:**
- ❌ **NO** triple-slash comments: `/// This is a comment`
- ❌ **NO** double-slash comments: `// This is a comment`
- ❌ **NO** block comments: `/* This is a comment */`
- ❌ **NO** XML-style comments: `<!-- This is a comment -->`

**ANY comment in a TMDL file will cause Power BI Desktop to fail loading the model with parsing errors.**

**Historical Context**: Early documentation examples showed `///` comments before object declarations (tables, columns). These examples were INCORRECT and caused model load failures. If you need to document your model:
- ✅ Use separate documentation files (Markdown, Word)
- ✅ Use self-documenting naming conventions
- ✅ Create a separate `README.md` in the PBIP folder

**Error Message Example**:
```
Failed to load project: Unexpected token '/' at line 72
```

---

## 1. Indentation Rules (CRITICAL)

TMDL uses **strict whitespace indentation** with **TAB characters** (not spaces).

### Three Indentation Levels:
| Level | Usage | Example |
|-------|-------|---------|
| Level 1 (no indent) | Object declaration | `table Sales` |
| Level 2 (1 tab) | Object properties | `⇥dataType: int64` |
| Level 3 (2 tabs) | Multi-line expressions | `⇥⇥var result = SUMX(...)` |

### Root-level objects (NO indentation):
- `database`, `model`, `table`, `relationship`, `expression`, `role`, `culture`, `perspective`

### Important: 
- Blank lines separate sibling objects (columns, measures) within a table.
- Multi-line expressions must start on the line AFTER the `=` sign, indented one level deeper than properties.
- Trailing blank lines in expressions are stripped.
- **Violation of indentation rules produces a parsing error in Power BI Desktop.**

---

## 2. Property Delimiters

| Delimiter | Usage | Example |
|-----------|-------|---------|
| Colon (`:`) | Non-expression property values | `dataType: int64` |
| Equals (`=`) | Expressions and default properties | `measure Sales = SUM(...)` |

---

## 3. Object Naming

- Names with spaces, dots, equals, colons, or single quotes → **enclose in single quotes**: `'Sales Amount'`
- Single quotes in names → **escape by doubling**: `'Customer''s Revenue'`
- TMDL serializer uses **camelCase** by default for keywords and enum values.
- On deserialization, TMDL is **case-insensitive**.

---

## 4. Database Definition

### CompatibilityLevel Version Mapping

**CRITICAL**: The `compatibilityLevel` must match the Power BI Desktop version. Mismatches cause load failures.

| CompatibilityLevel | Power BI Desktop Version | Release Date | Status |
|--------------------|--------------------------|--------------|--------|
| **1600** | December 2025 (2.150.x) | December 2025 | **Current** |
| 1567 | September 2024 (2.133.x) | September 2024 | Legacy |
| 1550 | June 2024 (2.130.x) | June 2024 | Deprecated |
| 1520 | March 2023 | March 2023 | Obsolete |
| 1500 | September 2021 | September 2021 | Obsolete |

**Rule**: Always use the compatibility level that matches the installed Power BI Desktop version. For new models created in December 2025 or later, use **1600**.

**Error Messages**:
- "CompatibilityLevel downgrade not supported": TMDL file has lower level than existing database → increase TMDL level
- "CompatibilityLevel not supported": TMDL file has higher level than Power BI Desktop supports → upgrade Power BI Desktop or decrease TMDL level

### Syntax

```tmdl
database MyProject
	compatibilityLevel: 1600
```

---

## 5. Relationship Definition

### Full Property List

```tmdl
relationship <unique-guid>
	fromColumn: <TableName>.<ColumnName>
	toColumn: <TableName>.<ColumnName>
	fromCardinality: many
	toCardinality: one
	isActive: true
	securityFilteringBehavior: oneDirection
	relyOnReferentialIntegrity: false
	crossFilteringBehavior: oneDirection
```

**Note**: `fromColumn` is the foreign key (Many side), `toColumn` is the primary key (One side). `securityFilteringBehavior` controls RLS filter propagation (max 1 bothDirections per table).

### Property Descriptions

| Property | Values | Default | Purpose |
|----------|--------|---------|--------|
| `fromColumn` | `Table.Column` | Required | Foreign key (Many side) |
| `toColumn` | `Table.Column` | Required | Primary key (One side) |
| `fromCardinality` | `many`, `one`, `none` | `many` | Source table cardinality |
| `toCardinality` | `many`, `one`, `none` | `one` | Target table cardinality |
| `isActive` | `true`, `false` | `true` | Relationship active status |
| `securityFilteringBehavior` | `oneDirection`, `bothDirections` | `oneDirection` | **RLS filter propagation** (max 1 bothDirections per table) |
| `relyOnReferentialIntegrity` | `true`, `false` | `false` | Assume referential integrity (DirectQuery only) |
| `crossFilteringBehavior` | `oneDirection`, `bothDirections`, `automatic` | `automatic` | **Query filter propagation** |

### Critical Constraint

**POWER BI RULE**: A table can have **only ONE relationship** with `securityFilteringBehavior: bothDirections`.

**Example Violation:**

**Note**: The following TMDL configuration is INVALID because Dim_Customer appears in 2 relationships with `bothDirections`:

```tmdl
relationship x
	fromColumn: Dim_Customer.CountryKey
	toColumn: Dim_Country.CountryKey
	securityFilteringBehavior: bothDirections

relationship y
	fromColumn: Fact_Sales.CustomerKey
	toColumn: Dim_Customer.CustomerKey
	securityFilteringBehavior: bothDirections
```

**Error Message:**
```
Table 'Dim_Customer' already has a relationship where Security Filtering Behavior 
is set to Both. Only one relationship per table with this setting is allowed.
```

**Fix:**

**Note**: The correct TMDL configuration uses `oneDirection` for all relationships:

```tmdl
relationship x
	fromColumn: Dim_Customer.CountryKey
	toColumn: Dim_Country.CountryKey
	securityFilteringBehavior: oneDirection

relationship y
	fromColumn: Fact_Sales.CustomerKey
	toColumn: Dim_Customer.CustomerKey
	securityFilteringBehavior: oneDirection
```

### Security vs Cross-Filtering Behavior

| Aspect | securityFilteringBehavior | crossFilteringBehavior |
|--------|---------------------------|------------------------|
| **Purpose** | Row-Level Security (RLS) propagation | DAX query filter propagation |
| **Use Case** | Security context in RLS roles | Measure calculation filtering |
| **Constraint** | Max 1 `bothDirections` per table | No limit |
| **Error if violated** | Model load fails | No error (ambiguous paths) |
| **Star Schema default** | `oneDirection` (all) | `oneDirection` (all) |
| **When to use Both** | Bidirectional RLS (rare) | Many-to-many bridges, role-playing |

---

## 6. Model Definition

```tmdl
model Model
	culture: en-US

ref table Dim_Date
ref table Dim_Customer
ref table Fact_Sales
ref table _Measures
```

### `ref` keyword rules:
- Defines collection ordering for source control stability.
- Objects referenced but missing are ignored on deserialization.
- Objects present but not referenced are appended at the end.
- Blank lines are NOT emitted between `ref` statements of the same type.

---

## 6. Table Definition

**Note**: Example tables below show structure only. Do NOT add comments in actual TMDL files.

### Dimension Table
```tmdl
table Dim_Customer
	lineageTag: a1b2c3d4-e5f6-7890-abcd-ef1234567890

	column CustomerKey
		dataType: int64
		isKey
		isHidden
		sourceColumn: CustomerKey
		summarizeBy: none
		lineageTag: b2c3d4e5-f6a7-8901-bcde-f12345678901

	column CustomerName
		dataType: string
		sourceColumn: CustomerName
		summarizeBy: none
		lineageTag: c3d4e5f6-a7b8-9012-cdef-123456789012

	column Country
		dataType: string
		sourceColumn: Country
		summarizeBy: none
		lineageTag: d4e5f6a7-b8c9-0123-defa-234567890123

	partition Dim_Customer = m
		mode: import
		source =
			let
				Source = Csv.Document(File.Contents("C:\path\data\dim_customer.csv"), [Delimiter = ",", Columns = 3, Encoding = 65001, QuoteStyle = QuoteStyle.None]),
				PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
				ChangedTypes = Table.TransformColumnTypes(PromotedHeaders, {{"CustomerKey", Int64.Type}, {"CustomerName", type text}, {"Country", type text}})
			in
				ChangedTypes
```

### Fact Table
```tmdl
table Fact_Sales
	lineageTag: e5f6a7b8-c9d0-1234-efab-345678901234

	column SalesKey
		dataType: int64
		isHidden
		sourceColumn: SalesKey
		summarizeBy: none
		lineageTag: f6a7b8c9-d0e1-2345-fabc-456789012345

	column DateKey
		dataType: int64
		isHidden
		sourceColumn: DateKey
		summarizeBy: none
		lineageTag: a7b8c9d0-e1f2-3456-abcd-567890123456

	column CustomerKey
		dataType: int64
		isHidden
		sourceColumn: CustomerKey
		summarizeBy: none
		lineageTag: b8c9d0e1-f2a3-4567-bcde-678901234567

	column 'Sales Amount LC'
		dataType: decimal
		formatString: #,##0.00
		sourceColumn: SalesAmountLC
		summarizeBy: sum
		lineageTag: c9d0e1f2-a3b4-5678-cdef-789012345678

	partition Fact_Sales = m
		mode: import
		source =
			let
				Source = Csv.Document(File.Contents("C:\path\data\fact_sales.csv"), [Delimiter = ",", Columns = 4, Encoding = 65001, QuoteStyle = QuoteStyle.None]),
				PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
				ChangedTypes = Table.TransformColumnTypes(PromotedHeaders, {{"SalesKey", Int64.Type}, {"DateKey", Int64.Type}, {"CustomerKey", Int64.Type}, {"SalesAmountLC", type number}})
			in
				ChangedTypes
```

### Disconnected Measures Table
```tmdl
table _Measures

	measure 'Sales Amount' = SUM(Fact_Sales[Sales Amount LC])
		formatString: #,##0.00
		displayFolder: Sales
		lineageTag: d0e1f2a3-b4c5-6789-defa-890123456789

	partition _Measures = m
		mode: import
		source =
			let
				Source = #table({"Value"}, {{""}})
			in
				Source
```

---

## 7. Column Properties

| Property | Type | Description |
|----------|------|-------------|
| `dataType` | enum | `int64`, `string`, `decimal`, `double`, `dateTime`, `boolean` |
| `isKey` | boolean (shortcut) | Marks column as primary key |
| `isHidden` | boolean (shortcut) | Hides column from report view |
| `sourceColumn` | string | CSV/source column name mapping |
| `summarizeBy` | enum | `none`, `sum`, `count`, `min`, `max`, `average` |
| `formatString` | string | Display format (e.g., `#,##0.00`, `yyyy-MM-dd`, `0.00%`) |
| `lineageTag` | GUID | Unique identifier for source control stability |
| `sortByColumn` | reference | Column used for sort order |

**Note**: `isKey` and `isHidden` can be used as boolean shortcuts (omit `: true`).

### Boolean shortcut:
```tmdl
	column DateKey
		isKey
		isHidden
```
Is equivalent to:
```tmdl
	column DateKey
		isKey: true
		isHidden: true
```

---

## 8. Measure Properties

| Property | Type | Description |
|----------|------|-------------|
| Expression (default) | DAX | The measure formula, after `=` |
| `formatString` | string | Display format |
| `displayFolder` | string | Folder grouping in field list |
| `lineageTag` | GUID | Unique identifier |

**Note**: DAX expressions support comments (`//` and `/* */`), but TMDL property definitions do NOT.

### Single-line measure:
```tmdl
	measure 'Sales Amount' = SUM(Fact_Sales[Sales Amount LC])
		formatString: #,##0.00
```

### Multi-line measure:
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
```

---

## 9. Relationships

```tmdl
relationship 12345678-abcd-ef01-2345-6789abcdef01
	fromColumn: Fact_Sales.DateKey
	toColumn: Dim_Date.DateKey
```

### Relationship Properties:
| Property | Values | Default |
|----------|--------|---------|
| `fromCardinality` | `many`, `one` | `many` |
| `toCardinality` | `many`, `one` | `one` |
| `crossFilteringBehavior` | `oneDirection`, `bothDirections` | `oneDirection` |
| `isActive` | boolean | `true` |
| `securityFilteringBehavior` | `oneDirection`, `bothDirections` | `oneDirection` |

### Bi-directional (only for RLS):
```tmdl
relationship 12345678-abcd-ef01-2345-6789abcdef02
	fromColumn: Fact_Sales.AreaKey
	toColumn: Dim_Area.AreaKey
	crossFilteringBehavior: bothDirections
	securityFilteringBehavior: bothDirections
```

### Inactive relationship (role-playing dimension):
```tmdl
relationship 12345678-abcd-ef01-2345-6789abcdef03
	fromColumn: Fact_Sales.ShipDateKey
	toColumn: Dim_Date.DateKey
	isActive: false
```

---

## 10. Expressions (Shared M Parameters)

```tmdl
expression DataPath = "C:\path\to\data" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true]

expression Server = "localhost" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true]
```

---

## 11. Roles (RLS)

```tmdl
role SalesManager
	modelPermission: read

	tablePermission Dim_Area = Dim_Area[AreaName] = "North"
```

---

## 12. Date Table Marking

To mark `Dim_Date` as the official Date Table, the table must have a column of type `dateTime` marked with `isKey`. In TMDL/TOM, the Date Table behavior is established via annotations or through Power BI Desktop UI after loading the model.

---

## 13. Common Errors to Avoid

| Error | Cause | Fix |
|-------|-------|-----|
| **Parsing error: "Unexpected token"** | **Comments (///, //, /* */) in TMDL file** | **Remove ALL comments** |
| Parsing error on load | Space indentation instead of TABs | Replace all spaces with TABs |
| "Column not found" | `sourceColumn` doesn't match CSV header | Match CSV header exactly |
| Relationship error | `fromColumn`/`toColumn` typo | Verify column exists in referenced table |
| Circular dependency | Bi-directional chains | Keep single-direction unless RLS requires it |
| Measure error | Referencing non-existent column | Verify `Table[Column]` names match TMDL |
| formatString ignored | Wrong placement (inside expression block) | Place formatString at property level (1 tab) |
