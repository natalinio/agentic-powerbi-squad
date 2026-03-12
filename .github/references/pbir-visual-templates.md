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
7. Write PBIR JSON files as UTF-8 **without BOM**. BOM-prefixed `visual.json` files are a known corruption risk for externally generated reports.
8. The physical PBIR object id used in folder names and `name` properties must be runtime-safe and consistent across the artifact set.
9. `definition/pages/pages.json` is part of the canonical PBIR report surface and MUST be updated together with page folder creation/removal.

---

## Canonical PBIR Guardrails (Observed From Desktop-Generated Report)

These guardrails are derived from the current `SalesOverview.Report` PBIR output and should be treated as the safest baseline for Step 09.

### 1. Physical Runtime IDs

Power BI Desktop currently serializes page and visual names as compact 20-character lowercase alphanumeric identifiers.

Observed examples:
- page folder/name: `32fe1020890a4d7642b0`
- visual folder/name: `001dfd009480a8d9e500`

Guardrails:
- Do NOT use user-facing labels like `Page1` or `visual_01` as final PBIR folder names.
- Generate a runtime-safe physical id for each page and visual.
- Keep a deterministic mapping from blueprint logical ids to PBIR physical ids during generation.
- The physical id must match in all places where it appears.

### 2. Page Metadata Contract

Page generation is not complete until all three layers are aligned:
- page folder name
- `page.json -> name`
- `definition/pages/pages.json -> pageOrder[]` and `activePageName`

Canonical `pages.json` shape:

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json",
  "pageOrder": [
    "<pageRuntimeId1>",
    "<pageRuntimeId2>"
  ],
  "activePageName": "<pageRuntimeId1>"
}
```

Guardrails:
- `pageOrder` must list every existing page folder exactly once.
- `activePageName` must reference one of the entries in `pageOrder`.
- `page.json.name` must equal the page folder name.
- Do not delete or create page folders without atomically updating `pages.json`.

### 3. Visual Metadata Contract

For every visual:
- visual folder name must equal `visual.json -> name`
- each visual id must be unique within the page
- `visualContainerObjects.title` should be populated for selection-pane readability, even when the visible title is hidden

Slicer example from the observed report:
- `visualContainerObjects.title.properties.show = false`
- `visualContainerObjects.title.properties.text = 'Slicer - FiscalYear'`

This means the metadata title is useful even when the end-user visible title is hidden.

### 4. Runtime-Safe Encoding and JSON Hygiene

Guardrails:
- Always write JSON as UTF-8 without BOM.
- Do not use generators or shell commands that prepend a BOM.
- Do not emit comments, trailing commas, or schema-foreign properties.
- After writing files, validate that the first bytes do not contain `EF BB BF`.

### 5. Position and Layering Rules

Observed report characteristics:
- `position.x`, `y`, `width`, `height` may be integers or decimals
- `z` and `tabOrder` are integer-valued
- Power BI Desktop accepts non-uniform `z` spacing; fixed increments of `1000` are not required

Guardrails:
- Preserve monotonic layering order with integer `z` values.
- Preserve deterministic keyboard order with integer `tabOrder` values.
- Avoid overlapping bounding boxes unless deliberately layering decorative elements.

### 5.1 Minimum Usability Size Guardrails

These are usability guardrails derived from the manually corrected report, not just schema constraints.

#### Dropdown slicers
Observed stable baseline:
- width: `180`
- height: about `65.37`

Guardrails:
- dropdown slicers should use a minimum height of **64 px**
- do not generate dropdown slicers at `60 px` height when the top-row layout includes title/value chrome, because the control can appear visually compressed and the dropdown affordance becomes harder to read or click
- recommended default top-row slicer size for this repository: `width = 180`, `height = 64-66`

#### KPI card / grouped KPI band
Observed stable baseline:
- grouped KPI band height: about `120.30`
- value font size: `20D`

Guardrails:
- for grouped KPI bands, prefer a container height around **120 px**
- default callout/value font size should be **20D** for the current 1280x720 baseline
- avoid using `24D` as the default grouped KPI callout size in this repository baseline because it risks visual crowding and reduced balance when multiple KPIs are displayed together

#### Page 3 analytical surfaces
Observed stable baseline:
- top analytical gauge: about `328 x 139`
- left analytical map: about `660 x 472`
- right analytical treemap: about `592 x 472`

Guardrails:
- gauge visuals should not be generated as tiny tiles when they are used as a primary analytical object; prefer a width above **300 px** and a height above **130 px**
- azure maps require a large interaction surface; prefer widths above **600 px** and heights above **420 px** in the current 1280x720 baseline
- treemaps become visually noisy when compressed; prefer widths above **500 px** and heights above **420 px** for summary analysis use cases

### 5.2 Operational Layout Tokens

Step 09 should consume operational layout tokens from the blueprint when present.

Recommended token families:
- `designSystem.gridUnit`
- `designSystem.pagePadding`
- `designSystem.visualGap`
- `designSystem.sectionGap`
- `designSystem.containerStyle`
- `visual.position`
- optional per-visual `renderTokens`

Recommended per-visual `renderTokens` examples:

```json
{
  "renderTokens": {
    "minWidth": 180,
    "minHeight": 65,
    "preferredWidth": 180,
    "preferredHeight": 65,
    "containerStyle": "elevated",
    "dropShadow": true,
    "valueFontSize": "20D",
    "allowOverlap": false
  }
}
```

Guardrails:
- if tokens are present, Step 09 should honor them unless they would violate PBIR schema or create out-of-bounds placement
- if tokens are absent, Step 09 must fall back to repository-safe defaults derived from the canonical report
- `allowOverlap` defaults to `false`
- every visual should be validated against page bounds after token application

### 6. Current Visual Query Patterns

#### Slicer
- use `visualType: "slicer"`
- use `queryState.Values.projections`
- for dropdown behavior, include `objects.data.mode = 'Dropdown'`
- observed primary projection includes `active: true`

#### Grouped KPI band
- in the current Desktop baseline, a grouped KPI band is serialized as `cardVisual`
- multiple measures are placed inside `queryState.Data.projections`
- optional `sortDefinition` can point to the primary KPI
- `objects.value[selector=default].properties.fontSize = 20D` is part of the observed usable baseline

Guardrail:
- Do NOT emit an unverified PBIR `visualType` such as `multiRowCard` unless it has been confirmed by a Desktop-generated reference.
- When the blueprint requests a grouped KPI band, use `cardVisual` with multiple `Data.projections` as the safe baseline for this repository.
- Apply explicit `objects.value.fontSize = 20D` when generating the grouped KPI band baseline unless the blueprint or user-approved design token says otherwise.

#### Table
- use `visualType: "tableEx"`
- use `queryState.Values.projections`
- include `sortDefinition` whenever the blueprint defines ranking intent

#### Clustered Bar Chart
- use `queryState.Category` for the categorical axis
- use `queryState.Y` for one or more measures

#### Combo Chart
- use `queryState.Category`
- use `queryState.Y` for column values
- use `queryState.Y2` for line values

#### Scatter Chart
- use `queryState.Series`, `Size`, `X`, `Y`
- mark the primary analytical axis as `active: true` when observed in the Desktop reference pattern

#### Gauge
- use `visualType: "gauge"`
- use `queryState.Y` for the actual value
- use `queryState.TargetValue` for the target
- use `queryState.Tooltips` for supporting variance or contextual measures
- observed page 3 sample uses `visualContainerObjects.dropShadow`

#### Treemap
- use `visualType: "treemap"`
- use `queryState.Group` for the category grouping
- use `queryState.Values` for the aggregated measure
- observed primary grouping projection includes `active: true`

#### Azure Map
- use `visualType: "azureMap"`
- use `queryState.Category` for the location/category field
- use `queryState.Size` for the bubble magnitude
- observed sample includes `objects.mapControls`, `objects.categoryLabels`, `objects.bubbleLayer`, and `objects.filledMap`
- observed page 3 sample uses `visualContainerObjects.dropShadow`

### 7. Sorting Guardrails

`sortDefinition` is part of the safe baseline when the report intent depends on ranking or a primary KPI.

Observed examples:
- KPI band sorted by `Sales vs Budget`
- table sorted descending by `Sales Amount FYTD`

Guardrails:
- If the blueprint defines `sortBy`, generate `query.sortDefinition` explicitly.
- For tables and ranking visuals, do not rely on implicit Power BI default sorting.
- Use the measure or column declared as primary sort field in the blueprint.

### 8. Report Baseline Guardrails

Observed report-level baseline:
- `definition/report.json` schema: `report/3.1.0`
- `definition/version.json` schema: `versionMetadata/1.0.0`, `version = 2.0.0`
- `definition/pages/pages.json` schema: `pagesMetadata/1.0.0`
- shared base theme: `StaticResources/SharedResources/BaseThemes/CY25SU12.json`

Guardrails:
- Do not rewrite `report.json`, `version.json`, or theme resources unless required by the blueprint and verified against Desktop output.
- Keep report baseline files stable while generating pages and visuals.

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

For elevated containers in the current baseline, this block is also valid when supported by the visual:

```json
"visualContainerObjects": {
  "dropShadow": [
    {
      "properties": {
        "show": { "expr": { "Literal": { "Value": "true" } } }
      }
    }
  ]
}
```

Do not assume that all visual families also need a `title` object. In the current canonical sample:
- slicers include `title` metadata plus `dropShadow`
- gauge and azureMap use `dropShadow` without `title`
- treemap is valid without either `title` or `dropShadow`

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
    "objects": {
      "value": [
        {
          "properties": {
            "show": {
              "expr": {
                "Literal": {
                  "Value": "true"
                }
              }
            }
          }
        },
        {
          "properties": {
            "fontSize": {
              "expr": {
                "Literal": {
                  "Value": "20D"
                }
              }
            }
          },
          "selector": {
            "id": "default"
          }
        }
      ]
    },
    "drillFilterOtherVisuals": true
  }
}
```

### Grouped KPI Band (`cardVisual` with multiple measures)

Use this pattern when the blueprint defines a grouped KPI zone or `multiRowCard`-style summary.

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.5.0/schema.json",
  "name": "<visual_runtime_id>",
  "position": { "x": 0, "y": 0, "z": 0, "width": 840, "height": 120, "tabOrder": 0 },
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
                  "Property": "<PrimaryMeasureName>"
                }
              },
              "queryRef": "_Measures.<PrimaryMeasureName>",
              "nativeQueryRef": "<PrimaryMeasureName>"
            },
            {
              "field": {
                "Measure": {
                  "Expression": { "SourceRef": { "Entity": "_Measures" } },
                  "Property": "<SecondaryMeasureName>"
                }
              },
              "queryRef": "_Measures.<SecondaryMeasureName>",
              "nativeQueryRef": "<SecondaryMeasureName>"
            }
          ]
        }
      },
      "sortDefinition": {
        "sort": [
          {
            "field": {
              "Measure": {
                "Expression": { "SourceRef": { "Entity": "_Measures" } },
                "Property": "<PrimaryMeasureName>"
              }
            },
            "direction": "Descending"
          }
        ],
        "isDefaultSort": true
      }
    },
    "visualContainerObjects": {
      "title": [
        {
          "properties": {
            "show": { "expr": { "Literal": { "Value": "true" } } },
            "text": { "expr": { "Literal": { "Value": "'Card - <PrimaryMeasureName>'" } } }
          }
        }
      ]
    },
    "objects": {
      "value": [
        {
          "properties": {
            "show": {
              "expr": {
                "Literal": {
                  "Value": "true"
                }
              }
            }
          }
        },
        {
          "properties": {
            "fontSize": {
              "expr": {
                "Literal": {
                  "Value": "20D"
                }
              }
            }
          },
          "selector": {
            "id": "default"
          }
        }
      ]
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
  "position": { "x": 0, "y": 0, "z": 0, "width": 180, "height": 65, "tabOrder": 0 },
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
              "nativeQueryRef": "<SlicerColumn>",
              "active": true
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
      },
      "sortDefinition": {
        "sort": [
          {
            "field": {
              "Measure": {
                "Expression": { "SourceRef": { "Entity": "_Measures" } },
                "Property": "<MeasureName>"
              }
            },
            "direction": "Descending"
          }
        ]
      }
    },
    "drillFilterOtherVisuals": true
  }
}
```

### Gauge

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.5.0/schema.json",
  "name": "<visual_id>",
  "position": { "x": 0, "y": 0, "z": 0, "width": 328, "height": 139, "tabOrder": 0 },
  "visual": {
    "visualType": "gauge",
    "query": {
      "queryState": {
        "Y": {
          "projections": [
            {
              "field": {
                "Measure": {
                  "Expression": { "SourceRef": { "Entity": "_Measures" } },
                  "Property": "<ActualMeasureName>"
                }
              },
              "queryRef": "_Measures.<ActualMeasureName>",
              "nativeQueryRef": "<ActualMeasureName>"
            }
          ]
        },
        "TargetValue": {
          "projections": [
            {
              "field": {
                "Measure": {
                  "Expression": { "SourceRef": { "Entity": "_Measures" } },
                  "Property": "<TargetMeasureName>"
                }
              },
              "queryRef": "_Measures.<TargetMeasureName>",
              "nativeQueryRef": "<TargetMeasureName>"
            }
          ]
        },
        "Tooltips": {
          "projections": [
            {
              "field": {
                "Measure": {
                  "Expression": { "SourceRef": { "Entity": "_Measures" } },
                  "Property": "<TooltipMeasureName>"
                }
              },
              "queryRef": "_Measures.<TooltipMeasureName>",
              "nativeQueryRef": "<TooltipMeasureName>"
            }
          ]
        }
      }
    },
    "visualContainerObjects": {
      "dropShadow": [
        {
          "properties": {
            "show": { "expr": { "Literal": { "Value": "true" } } }
          }
        }
      ]
    },
    "drillFilterOtherVisuals": true
  }
}
```

### Treemap

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.5.0/schema.json",
  "name": "<visual_id>",
  "position": { "x": 0, "y": 0, "z": 0, "width": 592, "height": 472, "tabOrder": 0 },
  "visual": {
    "visualType": "treemap",
    "query": {
      "queryState": {
        "Group": {
          "projections": [
            {
              "field": {
                "Column": {
                  "Expression": { "SourceRef": { "Entity": "<DimensionTable>" } },
                  "Property": "<GroupColumn>"
                }
              },
              "queryRef": "<DimensionTable>.<GroupColumn>",
              "nativeQueryRef": "<GroupColumn>",
              "active": true
            }
          ]
        },
        "Values": {
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

### Azure Map

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.5.0/schema.json",
  "name": "<visual_id>",
  "position": { "x": 0, "y": 0, "z": 0, "width": 660, "height": 472, "tabOrder": 0 },
  "visual": {
    "visualType": "azureMap",
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
              "nativeQueryRef": "<CategoryColumn>",
              "active": true
            }
          ]
        },
        "Size": {
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
    "objects": {
      "mapControls": [
        {
          "properties": {
            "defaultStyle": { "expr": { "Literal": { "Value": "'road'" } } },
            "showStylePicker": { "expr": { "Literal": { "Value": "false" } } },
            "showNavigationControls": { "expr": { "Literal": { "Value": "false" } } },
            "showSelectionControl": { "expr": { "Literal": { "Value": "false" } } }
          }
        }
      ],
      "categoryLabels": [
        {
          "properties": {
            "show": { "expr": { "Literal": { "Value": "false" } } }
          }
        }
      ],
      "bubbleLayer": [
        {
          "properties": {
            "show": { "expr": { "Literal": { "Value": "true" } } },
            "bubbleRadius": { "expr": { "Literal": { "Value": "6L" } } },
            "minBubbleRadius": { "expr": { "Literal": { "Value": "6L" } } },
            "maxRadius": { "expr": { "Literal": { "Value": "21L" } } },
            "bubbleStrokeWidth": { "expr": { "Literal": { "Value": "1L" } } },
            "autoStrokeColor": { "expr": { "Literal": { "Value": "true" } } },
            "layerPosition": { "expr": { "Literal": { "Value": "''" } } }
          }
        }
      ],
      "filledMap": [
        {
          "properties": {
            "show": { "expr": { "Literal": { "Value": "true" } } },
            "mapTransparency": { "expr": { "Literal": { "Value": "40L" } } }
          }
        }
      ]
    },
    "visualContainerObjects": {
      "dropShadow": [
        {
          "properties": {
            "show": { "expr": { "Literal": { "Value": "true" } } }
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

| Blueprint `visualType` | PBIR `visualType` |
|---|---|
| `card` | `cardVisual` |
| `multiRowCard` | `cardVisual` |
| `clusteredBarChart` | `clusteredBarChart` |
| `clusteredColumnChart` | `clusteredColumnChart` |
| `lineClusteredColumnComboChart` | `lineClusteredColumnComboChart` |
| `scatterChart` | `scatterChart` |
| `gauge` | `gauge` |
| `treemap` | `treemap` |
| `azureMap` | `azureMap` |
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

## Pages Metadata Template

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json",
  "pageOrder": [
    "<pageRuntimeId1>",
    "<pageRuntimeId2>"
  ],
  "activePageName": "<pageRuntimeId1>"
}
```

Guardrails:
- keep `pageOrder` in the user-facing navigation order defined by the blueprint
- set `activePageName` to the first page unless the blueprint explicitly defines a different landing page
- keep every page runtime id synchronized with its folder name and `page.json.name`

---

## Derived Rules (From Manual Page1)

1. Visual folder names are physical object ids and must match `visual.json.name`.
2. Page folder names are physical object ids and must match `page.json.name` and `pages/pages.json.pageOrder`.
3. Card visuals are saved as `cardVisual`, not `card`.
4. Grouped KPI bands are currently serialized safely as `cardVisual` with multiple `queryState.Data.projections`.
5. Slicer visuals include `visual.objects.data.mode = 'Dropdown'` for dropdown behavior.
6. Observed slicer projections include `active: true`.
7. Top-row dropdown slicers are materially more usable at about `65 px` height than at `60 px` in the current baseline.
7. Combo chart uses `queryState.Category`, `Y`, and `Y2` sections.
8. Scatter chart uses `queryState.Series`, `Size`, `X`, and `Y` sections.
9. Tables and ranking visuals use `query.sortDefinition` when ordering matters.
10. `filterConfig` was not required in the current manually authored sample and should remain optional unless a Desktop-generated baseline demonstrates a need.
11. Metadata titles inside `visualContainerObjects.title` are valuable for selection-pane readability even when the visible title is hidden.
12. Report-level page navigation depends on `definition/pages/pages.json`; page folders alone are insufficient.
13. The observed grouped KPI band uses `objects.value.fontSize = 20D`, which should be treated as the default usability baseline unless explicitly overridden.
14. Gauge uses `Y`, `TargetValue`, and optional `Tooltips` query buckets.
15. Treemap uses `Group` plus `Values`.
16. Azure Map uses `Category` plus `Size` and can require explicit `mapControls`, `bubbleLayer`, and `filledMap` object settings for a stable baseline.
17. Elevated container treatment on page 3 is implemented through `visualContainerObjects.dropShadow` on slicers, gauge, and azureMap.
18. Not every canonical visual needs `visualContainerObjects.title`; treat it as conditional metadata, not a universal requirement.

---

## Implementation Notes

1. Keep logical blueprint ids separate from physical PBIR runtime ids.
2. Generate and write `pages/pages.json` atomically together with page folder creation.
3. Keep visual runtime ids stable and unique per page.
4. Build visuals incrementally: first one slicer + one card, then reopen report.
5. Add optional `visualContainerObjects` only after the baseline set loads correctly.
6. Prefer UTF-8 without BOM writers and validate encoding after file generation.
7. Reopen Power BI Desktop after external JSON changes.
