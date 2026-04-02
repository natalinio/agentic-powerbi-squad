# Extension Measures Reference

Extension measures are DAX expressions stored in a thin report's `reportExtensions.json`. They execute in the report context, not the semantic model.

## When to Use Extension Measures

Use for **report-specific formatting or rendering**:

| Use Case | Example |
|---|---|
| Conditional formatting | Return theme tokens: `"good"`, `"bad"`, `"neutral"` |
| Label latest data point | Return value only for most recent period, `BLANK()` otherwise |
| Conditional rendering | Show/hide values based on slicer context |
| SVG inline graphics | Return `data:image/svg+xml;utf8,...` with `dataCategory: ImageUrl` |
| Report-specific calculations | Metrics unique to this report's storytelling |

**Promote to semantic model** when the measure is reusable across reports or represents core business logic.

## reportExtensions.json Structure

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/reportExtensions/1.0.0/schema.json",
  "entities": {
    "_Measures": {
      "measures": [
        {
          "name": "Revenue Color",
          "expression": "IF([Total Revenue] >= [Target Revenue], \"good\", \"bad\")",
          "dataType": "string"
        },
        {
          "name": "Revenue vs Target",
          "expression": "VAR _gap = [Total Revenue] - [Target Revenue] RETURN FORMAT(_gap, \"+#,##0;-#,##0\")",
          "dataType": "string"
        }
      ]
    },
    "_SVG": {
      "measures": [
        {
          "name": "Trend Arrow",
          "expression": "VAR _gap = [Total Revenue] - [Target Revenue] VAR _color = IF(_gap >= 0, \"#2B7A78\", \"#D4602E\") RETURN \"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='24' height='24'><polygon points='12,4 20,16 4,16' fill='\" & _color & \"'/></svg>\"",
          "dataType": "string",
          "dataCategory": "ImageUrl"
        }
      ]
    }
  }
}
```

### Structure Rules

- **entities**: Object where each key is a table name (use `_Measures`, `_Fmt`, `_SVG` by convention)
- **measures**: Array of measure definitions within each table
- **name**: Measure name (appears in field list alongside model measures)
- **expression**: DAX expression (double-escape quotes: `\"`)
- **dataType**: `string`, `int64`, `double`, `boolean`, `dateTime`
- **dataCategory** (optional): `ImageUrl` for SVG measures
- **formatString** (optional): e.g., `"#,##0"`, `"0.0%"`

## Binding Extension Measures in Visuals

Extension measures use `"Schema": "extension"` in the SourceRef:

```json
{
  "field": {
    "Measure": {
      "Expression": {
        "SourceRef": {
          "Schema": "extension",
          "Entity": "_Measures"
        }
      },
      "Property": "Revenue Color"
    }
  },
  "queryRef": "_Measures.Revenue Color",
  "nativeQueryRef": "Revenue Color"
}
```

## Common Patterns

### Conditional Formatting Token

```dax
Revenue Color =
IF([Total Revenue] >= [Target Revenue], "good",
IF([Total Revenue] >= [Target Revenue] * 0.8, "neutral", "bad"))
```

### Latest Data Point Label

```dax
Revenue Latest Label =
IF(SELECTEDVALUE('Date'[Date]) = MAX('Date'[Date]), [Total Revenue], BLANK())
```

### Conditional Render (Single Selection)

```dax
Share If Single =
IF(HASONEVALUE('Product'[Category]),
  DIVIDE([Total Revenue], CALCULATE([Total Revenue], ALL('Product'[Category]))),
  BLANK())
```

### Variance with Format

```dax
Revenue vs Target =
VAR _actual = [Total Revenue]
VAR _target = [Target Revenue]
VAR _gap = _actual - _target
RETURN FORMAT(_gap, "+#,##0;-#,##0") & " (" & FORMAT(DIVIDE(_gap, _target), "+0.0%;-0.0%") & ")"
```

## Naming Conventions

- Use dedicated table names: `_Measures`, `_Fmt`, `_SVG`, `_Report`
- Prefix by purpose: `Revenue Color`, `Status Icon`, `Latest Label`
- Keep names descriptive — they appear in the field list alongside model measures

## DAX Verification

**Never invent or assume DAX function names.** Verify against https://dax.guide before using in extension measures. Common pitfalls:
- `LAMBDA` — not available in all engines
- `MAXA` vs `MAX` — different signatures
- Custom format strings override display unit settings — be explicit
