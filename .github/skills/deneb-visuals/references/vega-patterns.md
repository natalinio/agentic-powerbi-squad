# Vega Chart Patterns for Deneb

Common Vega chart patterns for Power BI Deneb visuals. All specs use `"data": [{"name": "dataset"}]` (array form) and Vega v6 (bundled in Deneb 1.8+). Use `pbiContainerWidth` / `pbiContainerHeight` signals for responsive sizing and `pbiColor()` for theme colors.

## Vega Spec Anatomy

Every Vega spec follows this structure:

```json
{
  "$schema": "https://vega.github.io/schema/vega/v6.json",
  "data": [{"name": "dataset"}],
  "width": {"signal": "pbiContainerWidth - 25"},
  "height": {"signal": "pbiContainerHeight - 27"},
  "padding": 5,
  "signals": [],
  "scales": [],
  "axes": [],
  "legends": [],
  "marks": []
}
```

Key differences from Vega-Lite:
- `data` is an **array** of named datasets, not a single object
- Scales, axes, legends are explicit (not inferred from encoding)
- Marks use `encode` blocks with `enter`/`update`/`hover` sets
- Signals enable reactive variables, events, and interactions
- Full control over every visual element

## Encode Blocks

Marks use three encoding sets:

| Set | When Applied |
|-----|-------------|
| `enter` | First time a mark is rendered |
| `update` | Every re-render (reactive to data/signal changes) |
| `hover` | On pointer hover (reverts to `update` on exit) |

## Bar Chart (Vertical)

```json
{
  "$schema": "https://vega.github.io/schema/vega/v6.json",
  "data": [{"name": "dataset"}],
  "padding": 5,
  "width": {"signal": "pbiContainerWidth - 25"},
  "height": {"signal": "pbiContainerHeight - 27"},
  "scales": [
    {"name": "xscale", "type": "band", "domain": {"data": "dataset", "field": "Category"}, "range": "width", "padding": 0.1, "round": true},
    {"name": "yscale", "type": "linear", "domain": {"data": "dataset", "field": "Sales"}, "range": "height", "nice": true, "zero": true}
  ],
  "axes": [
    {"orient": "bottom", "scale": "xscale"},
    {"orient": "left", "scale": "yscale"}
  ],
  "marks": [
    {
      "type": "rect",
      "from": {"data": "dataset"},
      "encode": {
        "enter": {
          "x": {"scale": "xscale", "field": "Category"},
          "width": {"scale": "xscale", "band": 1},
          "y": {"scale": "yscale", "field": "Sales"},
          "y2": {"scale": "yscale", "value": 0},
          "cornerRadiusTopLeft": {"value": 4},
          "cornerRadiusTopRight": {"value": 4}
        },
        "update": {"fill": {"signal": "pbiColor(0)"}},
        "hover": {"fill": {"signal": "pbiColor(0, -0.3)"}}
      }
    }
  ]
}
```

## Bar Chart (Horizontal)

```json
{
  "$schema": "https://vega.github.io/schema/vega/v6.json",
  "data": [{"name": "dataset"}],
  "padding": 5,
  "width": {"signal": "pbiContainerWidth - 25"},
  "height": {"signal": "pbiContainerHeight - 27"},
  "scales": [
    {"name": "yscale", "type": "band", "domain": {"data": "dataset", "field": "Category", "sort": {"op": "max", "field": "Sales", "order": "descending"}}, "range": "height", "padding": 0.1},
    {"name": "xscale", "type": "linear", "domain": {"data": "dataset", "field": "Sales"}, "range": "width", "nice": true, "zero": true}
  ],
  "axes": [
    {"orient": "bottom", "scale": "xscale"},
    {"orient": "left", "scale": "yscale"}
  ],
  "marks": [
    {
      "type": "rect",
      "from": {"data": "dataset"},
      "encode": {
        "enter": {
          "y": {"scale": "yscale", "field": "Category"},
          "height": {"scale": "yscale", "band": 1},
          "x": {"scale": "xscale", "field": "Sales"},
          "x2": {"scale": "xscale", "value": 0},
          "cornerRadiusTopRight": {"value": 4},
          "cornerRadiusBottomRight": {"value": 4}
        },
        "update": {"fill": {"signal": "pbiColor(0)"}},
        "hover": {"fill": {"signal": "pbiColor(0, -0.3)"}}
      }
    }
  ]
}
```

## Line Chart (Multi-Series)

```json
{
  "$schema": "https://vega.github.io/schema/vega/v6.json",
  "data": [{"name": "dataset"}],
  "padding": 5,
  "width": {"signal": "pbiContainerWidth - 25"},
  "height": {"signal": "pbiContainerHeight - 27"},
  "scales": [
    {"name": "x", "type": "point", "domain": {"data": "dataset", "field": "Date"}, "range": "width"},
    {"name": "y", "type": "linear", "domain": {"data": "dataset", "field": "Value"}, "range": "height", "nice": true, "zero": true},
    {"name": "color", "type": "ordinal", "domain": {"data": "dataset", "field": "Series"}, "range": {"scheme": "pbiColorNominal"}}
  ],
  "axes": [
    {"orient": "bottom", "scale": "x"},
    {"orient": "left", "scale": "y"}
  ],
  "legends": [{"stroke": "color", "orient": "top", "direction": "horizontal"}],
  "marks": [
    {
      "type": "group",
      "from": {"facet": {"name": "series", "data": "dataset", "groupby": "Series"}},
      "marks": [
        {
          "type": "line",
          "from": {"data": "series"},
          "encode": {
            "enter": {
              "x": {"scale": "x", "field": "Date"},
              "y": {"scale": "y", "field": "Value"},
              "stroke": {"scale": "color", "field": "Series"},
              "strokeWidth": {"value": 2}
            },
            "update": {"interpolate": {"value": "monotone"}, "strokeOpacity": {"value": 1}},
            "hover": {"strokeOpacity": {"value": 0.5}}
          }
        }
      ]
    }
  ]
}
```

## Cross-Filtering Pattern (Vega)

When `enableSelection` is true, use `__selected__` to control mark opacity:

```json
"marks": [
  {
    "type": "rect",
    "from": {"data": "dataset"},
    "encode": {
      "update": {
        "fillOpacity": [
          {"test": "datum.__selected__ == 'off'", "value": 0.3},
          {"value": 1}
        ]
      }
    }
  }
]
```

## Scale Types Quick Reference

| Type | Domain | Range | Use |
|------|--------|-------|-----|
| `linear` | Continuous | Continuous | Quantitative axes |
| `log` | Continuous (>0) | Continuous | Exponential data |
| `time` / `utc` | Temporal | Continuous | Date axes |
| `band` | Discrete | Continuous | Bar chart categories |
| `point` | Discrete | Continuous | Scatter/line categories |
| `ordinal` | Discrete | Discrete | Color by category |
| `quantize` | Continuous | Discrete | Choropleth bins |
| `threshold` | Arbitrary cuts | Discrete | Custom breakpoints |

## Available Transforms

| Transform | Purpose |
|-----------|---------|
| `aggregate` | Group and summarize data |
| `bin` | Discretize numeric values |
| `filter` | Filter with predicate expression |
| `fold` | Pivot columns to key/value pairs |
| `formula` | Compute derived fields |
| `joinaggregate` | Add aggregate values without grouping |
| `pie` | Compute angular layout |
| `stack` | Compute stacked positions |
| `window` | Running calculations (rank, lag, lead) |
| `force` | Force-directed layout |
| `treemap` | Treemap layout |
