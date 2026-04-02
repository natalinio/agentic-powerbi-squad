# Filters Reference

Filter types, JSON structure, and scope (report, page, visual) for PBIR reports.

## Filter Scope

Filters can be applied at three levels:

| Scope | Location in PBIR | Applied To |
|---|---|---|
| Report | `definition/filters.json` | All pages and visuals |
| Page | `definition/pages/<id>/filters.json` | All visuals on that page |
| Visual | Inside `visual.json` → `visual.filters` | Single visual only |

## Filter Types

### Categorical Filter (Default)

Filters by specific values in a column:

```json
{
  "type": "Categorical",
  "expression": {
    "Column": {
      "Expression": {
        "SourceRef": { "Entity": "Date" }
      },
      "Property": "Calendar Year"
    }
  },
  "filter": {
    "whereItems": [
      {
        "condition": {
          "In": {
            "expressions": [
              {
                "Column": {
                  "Expression": { "SourceRef": { "Entity": "Date" } },
                  "Property": "Calendar Year"
                }
              }
            ],
            "values": [
              [{ "Literal": { "Value": "'2024'" } }],
              [{ "Literal": { "Value": "'2025'" } }]
            ]
          }
        }
      }
    ]
  }
}
```

### TopN Filter

Shows top/bottom N items ranked by a measure:

```json
{
  "type": "TopN",
  "expression": {
    "Column": {
      "Expression": {
        "SourceRef": { "Entity": "Product" }
      },
      "Property": "Category"
    }
  },
  "filter": {
    "whereItems": [
      {
        "condition": {
          "Top": {
            "expression": {
              "Column": {
                "Expression": { "SourceRef": { "Entity": "Product" } },
                "Property": "Category"
              }
            },
            "count": 10,
            "orderBy": [
              {
                "expression": {
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
      }
    ]
  }
}
```

### Advanced Filter

Operator-based filter for numeric or text comparisons:

```json
{
  "type": "Advanced",
  "expression": {
    "Column": {
      "Expression": {
        "SourceRef": { "Entity": "Sales" }
      },
      "Property": "Amount"
    }
  },
  "filter": {
    "whereItems": [
      {
        "condition": {
          "Comparison": {
            "comparisonKind": 1,
            "left": {
              "Column": {
                "Expression": { "SourceRef": { "Entity": "Sales" } },
                "Property": "Amount"
              }
            },
            "right": {
              "Literal": { "Value": "1000L" }
            }
          }
        }
      }
    ]
  }
}
```

ComparisonKind values:
| Value | Operator |
|---|---|
| 0 | Equal |
| 1 | GreaterThan |
| 2 | GreaterThanOrEqual |
| 3 | LessThan |
| 4 | LessThanOrEqual |
| 5 | NotEqual |

### Relative Date Filter

Filters by relative time period:

```json
{
  "type": "RelativeDate",
  "expression": {
    "Column": {
      "Expression": {
        "SourceRef": { "Entity": "Date" }
      },
      "Property": "Date"
    }
  },
  "filter": {
    "whereItems": [
      {
        "condition": {
          "RelativeDate": {
            "timeUnit": 2,
            "periodCount": 30,
            "includeToday": true
          }
        }
      }
    ]
  }
}
```

TimeUnit values: `0` = Days, `1` = Weeks, `2` = Months, `3` = Years.

## Filter Configuration

### Hide Filter in View Mode

Add `isHiddenInViewMode: true` to prevent end users from seeing the filter:

```json
{
  "type": "Categorical",
  "isHiddenInViewMode": true,
  "expression": { ... },
  "filter": { ... }
}
```

### Lock Filter

Add `isLockedInViewMode: true` to prevent users from changing the filter value:

```json
{
  "type": "Categorical",
  "isLockedInViewMode": true,
  "expression": { ... },
  "filter": { ... }
}
```

## Filter Pane Configuration

Control the filter pane appearance in `definition/report.json`:

```json
"filterConfig": {
  "filtersOperationMode": "Advanced",
  "filterPaneEnabled": true,
  "filterPaneCollapsed": true
}
```
