# Fields and Bindings Reference

How field bindings work in PBIR visual JSON — field types, data roles, queryState structure.

## Field Types: Column vs Measure

Every field binding has a type that determines the JSON key. **Using the wrong type causes runtime errors** ("something is wrong with one or more fields") even though JSON validates.

### Column Binding

```json
{
  "field": {
    "Column": {
      "Expression": {
        "SourceRef": {
          "Entity": "Date"
        }
      },
      "Property": "Calendar Year"
    }
  },
  "queryRef": "Date.Calendar Year",
  "nativeQueryRef": "Calendar Year"
}
```

### Measure Binding

```json
{
  "field": {
    "Measure": {
      "Expression": {
        "SourceRef": {
          "Entity": "Sales"
        }
      },
      "Property": "Total Revenue"
    }
  },
  "queryRef": "Sales.Total Revenue",
  "nativeQueryRef": "Total Revenue"
}
```

### Extension Measure Binding

Extension measures (from `reportExtensions.json`) use `Schema: "extension"`:

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

## QueryState Structure

Each visual's `query.queryState` maps data roles to field projections:

```json
"query": {
  "queryState": {
    "Category": {
      "projections": [
        { "field": { "Column": { ... } }, "queryRef": "...", "nativeQueryRef": "..." }
      ]
    },
    "Y": {
      "projections": [
        { "field": { "Measure": { ... } }, "queryRef": "...", "nativeQueryRef": "..." }
      ]
    }
  }
}
```

### Key Rules

- `Entity` must match the TMDL table name **exactly** (case-sensitive)
- `Property` must match the TMDL column/measure name **exactly**
- `queryRef` format: `Table.Field` (no quotes)
- `nativeQueryRef` format: just the field name (no table prefix)
- Multiple fields in same role: add to the `projections` array
- **Always read TMDL files first** to build the field registry before binding

## Data Roles by Visual Type

| Visual Type | Primary Roles | Notes |
|---|---|---|
| `cardVisual` | `Data` | New card visual |
| `card` | `Values` | Legacy card |
| `lineChart` | `Category`, `Y` | Optional: `Legend`, `SmallMultiples` |
| `barChart` / `columnChart` | `Category`, `Y` | Optional: `Legend`, `SmallMultiples` |
| `clusteredBarChart` / `clusteredColumnChart` | `Category`, `Y` | Optional: `Legend` |
| `lineClusteredColumnComboChart` | `Category`, `ColumnY`, `LineY` | Optional: `Legend` |
| `lineStackedColumnComboChart` | `Category`, `ColumnY`, `LineY` | Optional: `Legend` |
| `tableEx` | `Values` | All fields in one role |
| `pivotTable` (matrix) | `Values` | Also: `Rows`, `Columns` |
| `advancedSlicerVisual` | `Values` | New slicer |
| `slicer` | `Values` | Legacy slicer |
| `donutChart` / `pieChart` | `Category`, `Values` | Optional: `Legend` |
| `scatterChart` | `X`, `Y` | Optional: `Category`, `Size`, `Legend` |
| `treemap` | `Category`, `Values` | Optional: `Details` |
| `gauge` | `Value` | Optional: `TargetValue`, `MinValue`, `MaxValue` |
| `kpi` | `Indicator` | Optional: `Goal`, `TrendLine` |
| `waterfallChart` | `Category`, `Y` | Optional: `Breakdown` |
| `image` | — | No data roles; uses `image.sourceField` in objects |
| `textbox` | — | No data roles; text in `general.paragraphs` |

## Sort Definition

Sorting is defined in the `query.sortDefinition` block:

```json
"query": {
  "queryState": { ... },
  "sortDefinition": {
    "sort": [
      {
        "field": {
          "Measure": {
            "Expression": { "SourceRef": { "Entity": "Sales" } },
            "Property": "Total Revenue"
          }
        },
        "direction": "Descending"
      }
    ]
  }
}
```

Directions: `"Ascending"`, `"Descending"`.
