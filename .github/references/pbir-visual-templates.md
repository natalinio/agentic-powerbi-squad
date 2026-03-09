# PBIR Visual Templates Reference

## Purpose
This document provides validated JSON templates for Power BI Report (PBIR) visual definitions. These templates are the **single source of truth** for generating `visual.json` files in Step 9 (Report Implementation).

**Schema Source**: `https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/1.0.0/schema.json`

> **CRITICAL**: The agent MUST use these templates as the base for all generated visuals. Do NOT invent JSON structures. If a visual type is not covered here, use `microsoft_docs_search` or `microsoft_docs_fetch` MCP tools to find the correct schema.

---

## Common Visual Structure

Every `visual.json` file follows this base structure:

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/1.0.0/schema.json",
  "name": "<unique_visual_id>",
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
        "Values": {
          "projections": [
            {
              "field": {
                "Measure": {
                  "Expression": {
                    "SourceRef": { "Entity": "_Measures" }
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
    "visualContainerObjects": {
      "title": [
        {
          "properties": {
            "show": { "expr": { "Literal": { "Value": "true" } } },
            "text": { "expr": { "Literal": { "Value": "'<Visual Title>'" } } }
          }
        }
      ]
    },
    "drillFilterOtherVisuals": true
  }
}
```

---

## Field Reference Patterns

### Measure Reference
Used to reference a measure from the `_Measures` table:

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
Used to reference a column from a dimension table:

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

## Visual Type Templates

### 1. Card Visual

Single KPI value display.

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/1.0.0/schema.json",
  "name": "<unique_id>",
  "position": {
    "x": 0,
    "y": 0,
    "z": 0,
    "width": 200,
    "height": 100,
    "tabOrder": 0
  },
  "visual": {
    "visualType": "card",
    "query": {
      "queryState": {
        "Values": {
          "projections": [
            {
              "field": {
                "Measure": {
                  "Expression": {
                    "SourceRef": { "Entity": "_Measures" }
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
  }
}
```

### 2. Clustered Bar Chart

Comparison across categories.

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/1.0.0/schema.json",
  "name": "<unique_id>",
  "position": {
    "x": 0,
    "y": 0,
    "z": 0,
    "width": 400,
    "height": 300,
    "tabOrder": 0
  },
  "visual": {
    "visualType": "clusteredBarChart",
    "query": {
      "queryState": {
        "Category": {
          "projections": [
            {
              "field": {
                "Column": {
                  "Expression": {
                    "SourceRef": { "Entity": "<DimensionTable>" }
                  },
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
                  "Expression": {
                    "SourceRef": { "Entity": "_Measures" }
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
  }
}
```

### 3. Clustered Column Chart

Comparison across categories (vertical orientation).

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/1.0.0/schema.json",
  "name": "<unique_id>",
  "position": {
    "x": 0,
    "y": 0,
    "z": 0,
    "width": 400,
    "height": 300,
    "tabOrder": 0
  },
  "visual": {
    "visualType": "clusteredColumnChart",
    "query": {
      "queryState": {
        "Category": {
          "projections": [
            {
              "field": {
                "Column": {
                  "Expression": {
                    "SourceRef": { "Entity": "<DimensionTable>" }
                  },
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
                  "Expression": {
                    "SourceRef": { "Entity": "_Measures" }
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
  }
}
```

### 4. Line Chart

Trends over time.

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/1.0.0/schema.json",
  "name": "<unique_id>",
  "position": {
    "x": 0,
    "y": 0,
    "z": 0,
    "width": 500,
    "height": 300,
    "tabOrder": 0
  },
  "visual": {
    "visualType": "lineChart",
    "query": {
      "queryState": {
        "Category": {
          "projections": [
            {
              "field": {
                "Column": {
                  "Expression": {
                    "SourceRef": { "Entity": "Dim_Date" }
                  },
                  "Property": "MonthName"
                }
              },
              "queryRef": "Dim_Date.MonthName",
              "nativeQueryRef": "MonthName"
            }
          ]
        },
        "Y": {
          "projections": [
            {
              "field": {
                "Measure": {
                  "Expression": {
                    "SourceRef": { "Entity": "_Measures" }
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
  }
}
```

### 5. Matrix (Table with Row/Column Groups)

Cross-tabulation with measures.

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/1.0.0/schema.json",
  "name": "<unique_id>",
  "position": {
    "x": 0,
    "y": 0,
    "z": 0,
    "width": 600,
    "height": 400,
    "tabOrder": 0
  },
  "visual": {
    "visualType": "pivotTable",
    "query": {
      "queryState": {
        "Rows": {
          "projections": [
            {
              "field": {
                "Column": {
                  "Expression": {
                    "SourceRef": { "Entity": "<DimensionTable>" }
                  },
                  "Property": "<RowColumn>"
                }
              },
              "queryRef": "<DimensionTable>.<RowColumn>",
              "nativeQueryRef": "<RowColumn>"
            }
          ]
        },
        "Columns": {
          "projections": [
            {
              "field": {
                "Column": {
                  "Expression": {
                    "SourceRef": { "Entity": "<DimensionTable2>" }
                  },
                  "Property": "<ColumnGroupField>"
                }
              },
              "queryRef": "<DimensionTable2>.<ColumnGroupField>",
              "nativeQueryRef": "<ColumnGroupField>"
            }
          ]
        },
        "Values": {
          "projections": [
            {
              "field": {
                "Measure": {
                  "Expression": {
                    "SourceRef": { "Entity": "_Measures" }
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
  }
}
```

### 6. Table Visual

Simple flat table.

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/1.0.0/schema.json",
  "name": "<unique_id>",
  "position": {
    "x": 0,
    "y": 0,
    "z": 0,
    "width": 600,
    "height": 300,
    "tabOrder": 0
  },
  "visual": {
    "visualType": "tableEx",
    "query": {
      "queryState": {
        "Values": {
          "projections": [
            {
              "field": {
                "Column": {
                  "Expression": {
                    "SourceRef": { "Entity": "<Table>" }
                  },
                  "Property": "<Column1>"
                }
              },
              "queryRef": "<Table>.<Column1>",
              "nativeQueryRef": "<Column1>"
            },
            {
              "field": {
                "Measure": {
                  "Expression": {
                    "SourceRef": { "Entity": "_Measures" }
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
  }
}
```

### 7. Slicer Visual

Filter control for dimension fields.

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/1.0.0/schema.json",
  "name": "<unique_id>",
  "position": {
    "x": 0,
    "y": 0,
    "z": 0,
    "width": 200,
    "height": 60,
    "tabOrder": 0
  },
  "visual": {
    "visualType": "slicer",
    "query": {
      "queryState": {
        "Values": {
          "projections": [
            {
              "field": {
                "Column": {
                  "Expression": {
                    "SourceRef": { "Entity": "<DimensionTable>" }
                  },
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
            "mode": { "expr": { "Literal": { "Value": "'Dropdown'" } } }
          }
        }
      ]
    },
    "visualContainerObjects": {
      "title": [
        {
          "properties": {
            "show": { "expr": { "Literal": { "Value": "true" } } },
            "text": { "expr": { "Literal": { "Value": "'<SlicerLabel>'" } } }
          }
        }
      ]
    },
    "drillFilterOtherVisuals": true
  }
}
```

### 8. Donut Chart

Parts-of-whole composition.

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/1.0.0/schema.json",
  "name": "<unique_id>",
  "position": {
    "x": 0,
    "y": 0,
    "z": 0,
    "width": 300,
    "height": 300,
    "tabOrder": 0
  },
  "visual": {
    "visualType": "donutChart",
    "query": {
      "queryState": {
        "Category": {
          "projections": [
            {
              "field": {
                "Column": {
                  "Expression": {
                    "SourceRef": { "Entity": "<DimensionTable>" }
                  },
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
                  "Expression": {
                    "SourceRef": { "Entity": "_Measures" }
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
  }
}
```

---

## Visual Type Mapping

| Blueprint `visualType` | PBIR `visualType` Value |
|------------------------|------------------------|
| `card` | `card` |
| `clusteredBar` | `clusteredBarChart` |
| `clusteredColumn` | `clusteredColumnChart` |
| `line` | `lineChart` |
| `matrix` | `pivotTable` |
| `table` | `tableEx` |
| `slicer` | `slicer` |
| `donut` | `donutChart` |
| `pie` | `pieChart` |
| `stackedBar` | `stackedBarChart` |
| `stackedColumn` | `stackedColumnChart` |
| `waterfall` | `waterfallChart` |
| `gauge` | `gauge` |
| `kpi` | `kpi` |
| `treemap` | `treemap` |
| `map` | `map` |
| `filledMap` | `filledMap` |

---

## Page JSON Template

Each page folder must contain a `page.json` file:

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/1.0.0/schema.json",
  "name": "<PageId>",
  "displayName": "<Display Name>",
  "displayOption": "FitToWidth",
  "width": 1280,
  "height": 720
}
```

---

## Important Notes

1. **Visual IDs**: Each visual `name` must be a unique identifier within the page (e.g., UUID or sequential like `visual_01`).
2. **Z-order**: Controls visual stacking. Higher `z` values render on top.
3. **TabOrder**: Controls keyboard navigation order for accessibility.
4. **Entity names**: Must match EXACTLY the TMDL table names (case-sensitive).
5. **Property names**: Must match EXACTLY the TMDL column/measure names.
6. **Slicer modes**: `"Dropdown"`, `"List"`, `"Between"` (for date ranges).
7. **Cross-filtering**: Set `drillFilterOtherVisuals: true` for interactive filter behavior.
