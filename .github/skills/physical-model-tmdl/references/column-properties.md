# Column Properties Reference

Complete reference for column properties in TMDL files, including valid values, rules, and common patterns.

## Property Reference

### dataType

Specifies the column's data type. Required for data columns.

| Value | Description | When to Use |
|-------|-------------|-------------|
| `string` | Text values | Names, codes, descriptions, categories |
| `int64` | 64-bit integer | Keys, counts, year numbers, integer quantities |
| `double` | Double-precision floating point | Calculated values, ratios, percentages |
| `decimal` | Fixed-point decimal | Currency amounts, precise financial values |
| `dateTime` | Date and time | Date columns, timestamps |
| `boolean` | True/False | Flag columns, indicators |
| `binary` | Binary data | Rarely used in analytical models |

### summarizeBy

Controls the default aggregation behavior when the column is used in a visual without an explicit measure. This is a metadata property that affects the Power BI UI, not DAX calculations.

| Value | Description | When to Use |
|-------|-------------|-------------|
| `none` | No default aggregation | Keys, attributes, dates, text, non-additive numbers |
| `sum` | Default to SUM | Additive numeric facts (amounts, quantities) |
| `count` | Default to COUNT | Rarely used; prefer explicit measures |
| `min` | Default to MIN | Rarely used |
| `max` | Default to MAX | Rarely used |
| `average` | Default to AVERAGE | Rarely used |
| `distinctCount` | Default to DISTINCT COUNT | Rarely used; prefer explicit measures |

#### summarizeBy Decision Rules

**Use `none` for:**
- All key columns (surrogate keys, natural keys, foreign keys)
- All text/string columns (names, codes, types, descriptions)
- All date/dateTime columns
- All boolean columns
- Non-additive numeric columns (rates, percentages, ratios, rankings)
- Numeric columns that serve as sort keys (e.g., MonthNumber for sorting MonthName)
- Year number columns

**Use `sum` for:**
- Additive fact columns (sales amount, quantity, line total)
- Columns where implicit SUM makes business sense

**General rule:** When in doubt, use `none`. Users should create explicit measures for aggregation.

### isHidden

Flag property (no value) that hides the column from report authors:

```tmdl
column CustomerKey
	dataType: int64
	isHidden
	sourceColumn: CustomerKey
	summarizeBy: none
	lineageTag: abc-123
```

**When to hide:**
- Surrogate key columns (used only in relationships)
- Foreign key columns in fact tables
- Technical columns not relevant to report authors
- Columns superseded by a hierarchy

### isKey

Flag property marking the column as the table's primary key:

```tmdl
column DateKey
	dataType: int64
	isKey
	isHidden
	sourceColumn: DateKey
	summarizeBy: none
	lineageTag: abc-123
```

Only one column per table should have `isKey`. Required for the Date table (`dataCategory: Time`).

### displayFolder

Organizes columns into folders in the Power BI field list:

```tmdl
column CustomerName
	dataType: string
	displayFolder: Customer Attributes
	sourceColumn: CustomerName
	summarizeBy: none
	lineageTag: abc-123
```

**Nesting:** Use backslash for subfolder nesting: `Sales\Time Intelligence`

### sourceColumn

References the Power Query output column that feeds this column:

```tmdl
column CustomerName
	dataType: string
	sourceColumn: CustomerName
	summarizeBy: none
	lineageTag: abc-123
```

When `isNameInferred` is present, the column name was automatically derived from the source and `sourceColumn` uses bracket notation: `sourceColumn: [CustomerName]`.

### sortByColumn

Specifies another column to use for sorting:

```tmdl
column MonthName
	dataType: string
	sourceColumn: MonthName
	summarizeBy: none
	sortByColumn: MonthNumber
	lineageTag: abc-123
```

The sort column must be in the same table and should have a one-to-one or many-to-one relationship with the sorted column.

### lineageTag

A GUID that uniquely identifies the column across model versions. **Never change an existing lineageTag** — it would break report bindings.

When adding a new column, generate a fresh GUID.

## formatString Patterns

### Numeric Formats

| Pattern | Description | Example Output |
|---------|-------------|----------------|
| `#,##0` | Integer with thousands separator | 1,234 |
| `#,##0.00` | Two decimal places | 1,234.56 |
| `#,##0.0` | One decimal place | 1,234.6 |
| `0` | Integer, no thousands separator | 1234 |
| `0.00` | Two decimals, no thousands separator | 1234.56 |

### Percentage Formats

| Pattern | Description | Example Output |
|---------|-------------|----------------|
| `0.0%` | One decimal percentage | 85.0% |
| `0.00%` | Two decimal percentage | 85.00% |
| `#,##0%` | Integer percentage | 85% |

### Currency Formats

| Pattern | Description | Example Output |
|---------|-------------|----------------|
| `$#,##0` | USD integer | $1,234 |
| `$#,##0.00` | USD with cents | $1,234.56 |
| `#,##0.00 €` | Euro with symbol after | 1,234.56 € |

### Date Formats

| Pattern | Description | Example Output |
|---------|-------------|----------------|
| `mm/dd/yyyy` | US date | 01/15/2024 |
| `dd/mm/yyyy` | EU date | 15/01/2024 |
| `yyyy-mm-dd` | ISO date | 2024-01-15 |

### Where to Apply formatString

- **Measures:** Apply `formatString` to the measure definition (most common)
- **Columns:** Apply `formatString` to the column definition (for date display columns, currency amounts)

## PBI_FormatHint Annotation

Power BI Desktop automatically adds `PBI_FormatHint` annotations when a `formatString` is set through the UI:

```tmdl
annotation PBI_FormatHint = {"isGeneralNumber":true}
```

| Hint | Meaning |
|------|---------|
| `{"isGeneralNumber":true}` | General numeric format |
| `{"isDecimal":true}` | Decimal format |
| `{"isDateTimeCustom":true}` | Custom date/time format |
| `{"currencyCulture":"en-US"}` | Currency with culture |

**Rule:** Do not fight this annotation. Power BI re-adds it automatically. When setting `formatString` in TMDL directly, leave any existing `PBI_FormatHint` in place.

## Annotation Syntax

Annotations are key-value pairs at the same indentation level as properties, separated from properties by a blank line:

```tmdl
column 'Sales Amount LC'
	dataType: decimal
	formatString: #,##0.00
	sourceColumn: SalesAmountLC
	summarizeBy: sum
	lineageTag: abc-123

	annotation SummarizationSetBy = Automatic

	annotation PBI_FormatHint = {"isGeneralNumber":true}
```

**Rules:**
- Blank line before the first annotation (separating it from properties)
- Blank line between annotations
- Same indentation depth as properties
- Format: `annotation <Name> = <Value>`

### Common Annotations

| Annotation | Purpose |
|---|---|
| `SummarizationSetBy = Automatic` | Indicates summarizeBy was inferred by Power BI |
| `SummarizationSetBy = User` | Indicates summarizeBy was explicitly set |
| `PBI_FormatHint = {...}` | Format type hint (auto-generated by PBI Desktop) |
| `PBI_NavigationStepName = Navigation` | Internal navigation metadata (leave as-is) |
| `PBI_ResultType = Table` | M expression result type (leave as-is) |
