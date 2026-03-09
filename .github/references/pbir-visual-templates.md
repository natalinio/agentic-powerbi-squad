# PBIR Visual Templates Reference

## Purpose
This document provides validated starter templates for Power BI Report (PBIR) `visual.json` files used in Step 9.

**Primary docs**:
- https://learn.microsoft.com/power-bi/developer/projects/projects-report
- https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.5.0/schema.json

## Critical Rules

1. Never invent properties not present in the schema.
2. Keep all visual references aligned with TMDL object names (`Entity`, `Property`).
3. Use minimal valid payload first (`visualType`, `query`, `objects`) and add optional formatting only after validation.
4. In the current Desktop baseline, use `visualContainer/2.5.0` and set `drillFilterOtherVisuals` inside `visual`.
5. For cards, use `visualType: "cardVisual"` and `queryState.Data` (not `card` + `Values`).
6. `filterConfig` is optional and can be omitted for handcrafted minimal payloads; Desktop can add it on save.

---

## Common Visual Structure (Minimal, Safe Baseline)

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.5.0/schema.json",
  "name": "<visual_id>",
  "position": {
    "x": 0,
    "y": 0,
    "z": 0,
    "width": 300,
    "height": 200,
    "tabOrder": 0
  },
  "visual": {
    "visualType": "<visual_type>",
    "query": {
      "queryState": {
        "Data": {
          "projections": [
            {
              "field": {
                "Measure": {
                  "Expression": {
                    "SourceRef": {
                      "Entity": "_Measures"
                    }
                  },
                  "Property": "<MeasureName>"
                }
              },
              "queryRef": "_Measures.<MeasureName>",
              "nativeQueryRef": "<MeasureName>"
            }
          ]
        }
      }
    },
    "objects": {},
    "drillFilterOtherVisuals": true
  }
}
```

---

## Optional Container Config (Inside `visual`)

Use this block only after base visual validation succeeds:

```json
"visualContainerObjects": {
  "title": [
    {
      "properties": {
        "show": { "expr": { "Literal": { "Value": "true" } } },
        "text": { "expr": { "Literal": { "Value": "'<Title>'" } } }
      }
    }
  ]
},
"drillFilterOtherVisuals": true
```

---

## Field Reference Patterns

### Measure Reference

```json
{
  "field": {
    "Measure": {
      "Expression": {
        "SourceRef": { "Entity": "_Measures" }
      },
      "Property": "Sales Amount FYTD"
    }
  },
  "queryRef": "_Measures.Sales Amount FYTD",
  "nativeQueryRef": "Sales Amount FYTD"
}
```

### Column Reference

```json
{
  "field": {
    "Column": {
      "Expression": {
        "SourceRef": { "Entity": "Dim_Date" }
      },
      "Property": "FiscalYear"
    }
  },
  "queryRef": "Dim_Date.FiscalYear",
  "nativeQueryRef": "FiscalYear"
}
```

---

## Visual Templates

### Card

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.5.0/schema.json",
  "name": "<visual_id>",
  "position": { "x": 0, "y": 0, "z": 0, "width": 200, "height": 100, "tabOrder": 0 },
  "visual": {
    "visualType": "cardVisual",
    "query": {
      "queryState": {
        "Data": {
          "projections": [
            {
              "field": {
                "Measure": {
                  "Expression": { "SourceRef": { "Entity": "_Measures" } },
                  "Property": "<MeasureName>"
                }
              },
              "queryRef": "_Measures.<MeasureName>",
              "nativeQueryRef": "<MeasureName>"
            }
          ]
        }
      }
    },
    "drillFilterOtherVisuals": true
  }
}
```

### Slicer (Dropdown)

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.5.0/schema.json",
  "name": "<slicer_id>",
  "position": { "x": 0, "y": 0, "z": 0, "width": 200, "height": 60, "tabOrder": 0 },
  "visual": {
    "visualType": "slicer",
    "query": {
      "queryState": {
        "Values": {
          "projections": [
            {
              "field": {
                "Column": {
                  "Expression": { "SourceRef": { "Entity": "<DimensionTable>" } },
                  "Property": "<SlicerColumn>"
                }
              },
              "queryRef": "<DimensionTable>.<SlicerColumn>",
              "nativeQueryRef": "<SlicerColumn>"
            }
          ]
        }
      }
    },
    "objects": {
      "data": [
        {
          "properties": {
            "mode": {
              "expr": {
                "Literal": {
                  "Value": "'Dropdown'"
                }
              }
            }
          }
        }
      ]
    },
    "drillFilterOtherVisuals": true
  }
}
```

### Clustered Bar Chart

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.5.0/schema.json",
  "name": "<visual_id>",
  "position": { "x": 0, "y": 0, "z": 0, "width": 500, "height": 300, "tabOrder": 0 },
  "visual": {
    "visualType": "clusteredBarChart",
    "query": {
      "queryState": {
        "Category": {
          "projections": [
            {
              "field": {
                "Column": {
                  "Expression": { "SourceRef": { "Entity": "<DimensionTable>" } },
                  "Property": "<CategoryColumn>"
                }
              },
              "queryRef": "<DimensionTable>.<CategoryColumn>",
              "nativeQueryRef": "<CategoryColumn>"
            }
          ]
        },
        "Y": {
          "projections": [
            {
              "field": {
                "Measure": {
                  "Expression": { "SourceRef": { "Entity": "_Measures" } },
                  "Property": "<MeasureName>"
                }
              },
              "queryRef": "_Measures.<MeasureName>",
              "nativeQueryRef": "<MeasureName>"
            }
          ]
        }
      }
    },
    "drillFilterOtherVisuals": true
  }
}
```

### Table (`tableEx`)

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.5.0/schema.json",
  "name": "<visual_id>",
  "position": { "x": 0, "y": 0, "z": 0, "width": 600, "height": 300, "tabOrder": 0 },
  "visual": {
    "visualType": "tableEx",
    "query": {
      "queryState": {
        "Values": {
          "projections": [
            {
              "field": {
                "Column": {
                  "Expression": { "SourceRef": { "Entity": "<DimensionTable>" } },
                  "Property": "<ColumnName>"
                }
              },
              "queryRef": "<DimensionTable>.<ColumnName>",
              "nativeQueryRef": "<ColumnName>"
            },
            {
              "field": {
                "Measure": {
                  "Expression": { "SourceRef": { "Entity": "_Measures" } },
                  "Property": "<MeasureName>"
                }
              },
              "queryRef": "_Measures.<MeasureName>",
              "nativeQueryRef": "<MeasureName>"
            }
          ]
        }
      }
    },
    "drillFilterOtherVisuals": true
  }
}
```

---

## Visual Type Mapping

| Blueprint `visualType` | PBIR `visualType` |
|---|---|
| `card` | `cardVisual` |
| `clusteredBarChart` | `clusteredBarChart` |
| `clusteredColumnChart` | `clusteredColumnChart` |
| `lineClusteredColumnComboChart` | `lineClusteredColumnComboChart` |
| `scatterChart` | `scatterChart` |
| `table` | `tableEx` |
| `slicer` | `slicer` |

---

## Page JSON Template

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.0.0/schema.json",
  "name": "<PageId>",
  "displayName": "<Display Name>",
  "displayOption": "FitToPage",
  "height": 720,
  "width": 1280
}
```

> Page schema `2.0.0` uses `additionalProperties: false`; do not add custom properties such as `ordinal`.

---

## Derived Rules (From Manual Page1)

1. Visual folder names are object ids (20-char alphanumeric in current Desktop output).
2. Card visuals are saved as `cardVisual`, not `card`.
3. Slicer visuals include `visual.objects.data.mode = 'Dropdown'` for dropdown behavior.
4. Combo chart uses `queryState.Category`, `Y`, and `Y2` sections.
5. Scatter chart uses `queryState.Series`, `Size`, `X`, and `Y` sections.
6. `filterConfig` appears on many visuals (especially charts/cards) after manual authoring and can contain both measure and column filters.

---

## Implementation Notes

1. Keep visual IDs stable and unique per page.
2. Build visuals incrementally: first one slicer + one card, then reopen report.
3. Add optional `visualContainerObjects` only after the baseline set loads correctly.
4. Reopen Power BI Desktop after external JSON changes.
