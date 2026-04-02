# Conditional Formatting Reference

How to implement conditional formatting (CF) in PBIR visual JSON.

## CF Types

| Type | Description | JSON Expression |
|---|---|---|
| **Measure-driven** (preferred) | Extension measure returns theme token | `Measure` with `dataViewWildcard` selector |
| **Gradient** | 2- or 3-color scale on a numeric field | `FillRule` with `linearGradient2/3` |
| **Rules** | Conditional cases (if/else logic) | `Conditional` with `Cases` |
| **Data bars** | Inline bars showing magnitude in tables | `dataBars` property on column |

CF entries live in `visual.objects` (not `visualContainerObjects`). Each container (e.g., `dataPoint`, `labels`, `values`) can hold both regular entries and CF entries. CF entries are identified by `dataViewWildcard` selectors or `FillRule`/`Conditional` expressions.

## Measure-Driven CF (Preferred Pattern)

Create a DAX extension measure returning theme sentiment tokens (`"good"`, `"bad"`, `"neutral"`), then bind it to a visual property. When the theme changes, all CF updates automatically.

### Step 1: Create Extension Measure

In `reportExtensions.json`:

```json
{
  "entities": {
    "_Fmt": {
      "measures": [
        {
          "name": "Revenue Color",
          "expression": "IF([Total Revenue] >= [Target Revenue], \"good\", IF([Total Revenue] >= [Target Revenue] * 0.8, \"neutral\", \"bad\"))",
          "dataType": "string"
        }
      ]
    }
  }
}
```

### Step 2: Bind to Visual Property

In `visual.json` → `visual.objects`, add a CF entry with `dataViewWildcard`:

```json
"dataPoint": [
  {
    "properties": {
      "fill": {
        "solid": {
          "color": {
            "expr": {
              "Measure": {
                "Expression": {
                  "SourceRef": {
                    "Schema": "extension",
                    "Entity": "_Fmt"
                  }
                },
                "Property": "Revenue Color"
              }
            }
          }
        }
      }
    },
    "selector": {
      "data": {
        "dataViewWildcard": {
          "matchingOption": 1
        }
      }
    }
  }
]
```

The `dataViewWildcard` with `matchingOption: 1` applies the CF to all data points.

## Common Containers and Properties

| Container | Property | Typical Use |
|---|---|---|
| `dataPoint` | `fill` | Bar/column/area fill color |
| `dataPoint` | `strokeColor` | Data point border |
| `labels` | `color` | Data label font color |
| `values` | `fontColor` | Table/matrix value font color |
| `values` | `backColor` | Table/matrix value background |
| `columnFormatting` | `fontColor` | Matrix column header color |
| `columnFormatting` | `backColor` | Matrix column header background |
| `accentBar` | `color` | KPI accent bar color |
| `fillCustom` | `color` | New card fill color |
| `value` | `color` | New card value font color |

## Gradient CF

Two-color gradient on a numeric field:

```json
"dataPoint": [
  {
    "properties": {
      "fill": {
        "expr": {
          "FillRule": {
            "input": {
              "Measure": {
                "Expression": { "SourceRef": { "Entity": "Sales" } },
                "Property": "Total Revenue"
              }
            },
            "fillRule": {
              "linearGradient2": {
                "min": { "color": { "expr": { "ThemeDataColor": { "ColorId": 0, "Percent": 0 } } } },
                "max": { "color": { "expr": { "ThemeDataColor": { "ColorId": 0, "Percent": -0.5 } } } }
              }
            }
          }
        }
      }
    },
    "selector": {
      "data": { "dataViewWildcard": { "matchingOption": 1 } }
    }
  }
]
```

For 3-color gradient, use `linearGradient3` with `min`, `mid`, `max`.

## Best Practices

1. **Theme tokens over hex** — Use sentiment tokens (`"good"`, `"bad"`, `"neutral"`) so theme changes cascade to all CF
2. **Measure-driven preferred** — Extension measures returning tokens are easier to maintain than gradients/rules
3. **Apply sparingly** — CF should highlight exceptions, not decorate everything. Format variance columns, not raw values
4. **Accessible palettes** — Blue/orange instead of red/green. Always pair color with a secondary cue (icon, text)
5. **Define theme sentiment colors** — Ensure `good`, `bad`, `neutral` are set in the theme JSON before applying measure-driven CF
