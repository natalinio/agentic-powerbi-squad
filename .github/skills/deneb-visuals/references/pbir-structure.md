# Deneb PBIR JSON Structure

Complete reference for how Deneb visuals are represented in PBIR format `visual.json` files.

## Visual Container Structure

Minimal Deneb visual container:

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.5.0/schema.json",
  "name": "2c2722561a0b6c3deded",
  "position": {
    "x": 80,
    "y": 56,
    "z": 0,
    "height": 280,
    "width": 280,
    "tabOrder": 0
  },
  "visual": {
    "visualType": "deneb7E15AEF80B9E4D4F8E12924291ECE89A",
    "query": {
      "queryState": {
        "dataset": {
          "projections": [
            {
              "field": {
                "Column": {
                  "Expression": {
                    "SourceRef": { "Entity": "Product" }
                  },
                  "Property": "Product"
                }
              },
              "queryRef": "Product.Product",
              "nativeQueryRef": "Product"
            },
            {
              "field": {
                "Measure": {
                  "Expression": {
                    "SourceRef": { "Entity": "Financials" }
                  },
                  "Property": "$ Sales"
                }
              },
              "queryRef": "Financials.$ Sales",
              "nativeQueryRef": "$ Sales"
            }
          ]
        }
      }
    },
    "objects": {
      "vega": [
        {
          "properties": {
            "jsonSpec": {
              "expr": {
                "Literal": {
                  "Value": "'{\"data\": {\"name\": \"dataset\"}, \"mark\": {\"type\": \"bar\"}, \"encoding\": {\"y\": {\"field\": \"Product\", \"type\": \"nominal\"}, \"x\": {\"field\": \"$ Sales\", \"type\": \"quantitative\"}}}'"
                }
              }
            },
            "jsonConfig": {
              "expr": {
                "Literal": {
                  "Value": "'{}'"
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

## Literal Value Encoding Rules

All Deneb object properties use PBIR literal expressions. The encoding varies by type:

### Booleans
Bare `true` or `false` (no quotes):
```json
{"enableTooltips": {"expr": {"Literal": {"Value": "true"}}}}
```

### Numbers (D-suffix)
Append `D` to numeric values:
```json
{"selectionMaxDataPoints": {"expr": {"Literal": {"Value": "50D"}}}}
```

### Strings and Enums
Wrap in single quotes:
```json
{"provider": {"expr": {"Literal": {"Value": "'vegaLite'"}}}}
{"renderMode": {"expr": {"Literal": {"Value": "'svg'"}}}}
```

### JSON Specs (jsonSpec, jsonConfig)
Stringified JSON wrapped in single quotes:
```json
{"jsonSpec": {"expr": {"Literal": {"Value": "'{\"data\":{\"name\":\"dataset\"},\"mark\":\"bar\"}'"}}}}
```

### Colors (solid fill structure)
```json
{
  "scrollbarColor": {
    "solid": {
      "color": {
        "expr": {
          "Literal": {"Value": "'#000000'"}
        }
      }
    }
  }
}
```

Or bind to theme:
```json
{
  "scrollbarColor": {
    "solid": {
      "color": {
        "expr": {
          "ThemeDataColor": {"ColorId": 1, "Percent": 0}
        }
      }
    }
  }
}
```

## Query State (Field Bindings)

Fields are bound under `visual.query.queryState.dataset.projections`. Each projection contains:

| Property | Purpose |
|----------|---------|
| `field.Column` or `field.Measure` | Field type and reference |
| `field.*.Expression.SourceRef.Entity` | Table name |
| `field.*.Property` | Column or measure name |
| `queryRef` | Fully qualified reference (`Table.Column`) |
| `nativeQueryRef` | Display name used in Vega specs |
| `displayName` | Custom display name (if renamed) |

Field names in Vega-Lite encoding channels must match `nativeQueryRef` or `displayName`.

### Extension Measures

For report extension measures, add `"Schema": "extension"` to the SourceRef:
```json
{
  "field": {
    "Measure": {
      "Expression": {
        "SourceRef": {
          "Schema": "extension",
          "Entity": "Orders"
        }
      },
      "Property": "Order Lines (PY)"
    }
  }
}
```

### Sort Definition

```json
{
  "sortDefinition": {
    "sort": [
      {
        "field": {
          "Column": {
            "Expression": {"SourceRef": {"Entity": "TableName"}},
            "Property": "ColumnName"
          }
        },
        "direction": "Ascending"
      }
    ],
    "isDefaultSort": true
  }
}
```

## Complete Interactivity Example

Cross-filtering and tooltips with full PBIR literal encoding:

```json
"objects": {
  "vega": [{
    "properties": {
      "provider": {"expr": {"Literal": {"Value": "'vegaLite'"}}},
      "jsonSpec": {"expr": {"Literal": {"Value": "'...spec...'"}}},
      "jsonConfig": {"expr": {"Literal": {"Value": "'...config...'"}}},
      "enableTooltips": {"expr": {"Literal": {"Value": "true"}}},
      "enableContextMenu": {"expr": {"Literal": {"Value": "true"}}},
      "enableSelection": {"expr": {"Literal": {"Value": "true"}}},
      "enableHighlight": {"expr": {"Literal": {"Value": "true"}}}
    }
  }]
}
```
