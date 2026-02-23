# TMDL Syntax Reference — Validated Templates

> This file contains **verified TMDL syntax** extracted from official Microsoft documentation.
> Source: https://learn.microsoft.com/analysis-services/tmdl/tmdl-overview
> 
> **ALWAYS cross-reference this file before generating TMDL code.**

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

```tmdl
database MyProject
	compatibilityLevel: 1567
```

---

## 5. Model Definition

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

### Dimension Table
```tmdl
/// Customer dimension with geographic attributes
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
/// Sales transactions at daily grain
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
/// Disconnected table to store all DAX measures
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
| `description` (`///`) | text | Documentation |

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

## 12. Descriptions (Triple-slash)

```tmdl
/// This is the table description
/// It can span multiple lines
table Dim_Customer

	/// Customer full name
	column CustomerName
		dataType: string
```

---

## 13. Date Table Marking

To mark `Dim_Date` as the official Date Table, the table must have a column of type `dateTime` marked with `isKey`. In TMDL/TOM, the Date Table behavior is established via annotations or through Power BI Desktop UI after loading the model.

---

## 14. Common Errors to Avoid

| Error | Cause | Fix |
|-------|-------|-----|
| Parsing error on load | Space indentation instead of TABs | Replace all spaces with TABs |
| "Column not found" | `sourceColumn` doesn't match CSV header | Match CSV header exactly |
| Relationship error | `fromColumn`/`toColumn` typo | Verify column exists in referenced table |
| Circular dependency | Bi-directional chains | Keep single-direction unless RLS requires it |
| Measure error | Referencing non-existent column | Verify `Table[Column]` names match TMDL |
| formatString ignored | Wrong placement (inside expression block) | Place formatString at property level (1 tab) |
