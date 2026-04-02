---
name: deneb-visuals
description: >-
  Use when creating Deneb custom visuals with Vega or Vega-Lite in Power BI reports.
  Triggers: "create Deneb visual", "add Vega-Lite chart", "inject Deneb spec",
  "build custom visualization with Deneb", "Vega or Vega-Lite in Power BI",
  "cross-filtering in Deneb", "theme a Deneb visual", "Deneb spec for Power BI",
  "configure Deneb interactivity", "fix Deneb not rendering", "Deneb field name escaping",
  "pbiColor theme colors in Deneb", "Deneb PBIR structure", "Deneb bullet chart",
  "Deneb KPI card", "Deneb heatmap", "Deneb lollipop", "Deneb waterfall".
user-invocable: true
---

# Skill: Deneb Visuals in Power BI (PBIR)

## Purpose
Create custom Vega and Vega-Lite visualizations using the Deneb certified custom visual for Power BI. Author specs, inject them into PBIR visual.json files, and configure interactivity.

## Provider Policy

**Prefer Vega-Lite** for new Deneb visuals unless specific Vega-only features are required (signals, event streams, custom projections, force/voronoi layouts). Vega-Lite is more concise, easier to maintain, and covers most chart types.

## Visual Identity

- **visualType:** `deneb7E15AEF80B9E4D4F8E12924291ECE89A`
- **Bundled runtime:** Vega 6.2.0 / Vega-Lite 6.4.1 (since Deneb 1.8; use `v6.json` schema URLs)
- **Data role:** Single `dataset` role (all fields go into one "Values" well)
- **Default row limit:** 10,000 rows (override via `dataLimit.override`)
- **Provider:** `vegaLite` (default) or `vega` (when Vega-specific features needed)
- **Render modes:** `svg` (default, sharp text) or `canvas` (better for large datasets)

## Custom Visual Registration (Required)

Register `deneb7E15AEF80B9E4D4F8E12924291ECE89A` in `report.json` `publicCustomVisuals` array. Without this, the visual shows "Can't display this visual."

```json
{
  "publicCustomVisuals": ["deneb7E15AEF80B9E4D4F8E12924291ECE89A"]
}
```

## Workflow: Creating a Deneb Visual

### Step 1: Add the Visual

Create the `visual.json` file with `visualType: deneb7E15AEF80B9E4D4F8E12924291ECE89A`, field bindings for the columns and measures you need, and position/size as required.

All fields bind to the single `dataset` role. Use `Table.Column` for columns and `Table.Measure` for measures. Field names in bindings must match those used in the Vega/Vega-Lite spec.

See `references/pbir-structure.md` for the complete visual.json structure.

### Step 2: Write the Spec

Create a Vega-Lite (or Vega) JSON spec. Key difference:
- **Vega-Lite:** `"data": {"name": "dataset"}` (object)
- **Vega:** `"data": [{"name": "dataset"}]` (array)

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "data": {"name": "dataset"},
  "mark": {"type": "bar", "tooltip": true},
  "encoding": {
    "y": {"field": "Category", "type": "nominal"},
    "x": {"field": "Value", "type": "quantitative"}
  }
}
```

See `references/vega-lite-patterns.md` for common chart patterns and `references/vega-patterns.md` for advanced Vega specs. Field names in the spec must match the `nativeQueryRef` from the field bindings.

### Step 3: Inject the Spec into PBIR

Set the spec and config in `objects.vega[0].properties` as single-quoted DAX literal strings.

**Escaping rules for visual.json injection:**
- The entire JSON spec is flattened to one line
- All inner double quotes (`"`) become `\"` (standard JSON string escaping)
- The stringified JSON is wrapped in single quotes: `'...'`
- Field names with spaces inside Vega expressions use doubled single quotes: `datum[''Sales Amount'']`

```json
"jsonSpec": {"expr": {"Literal": {"Value": "'{\"$schema\":\"...\",\"data\":{\"name\":\"dataset\"},\"mark\":\"bar\"}'" }}}
```

See `references/pbir-structure.md` for the full encoding pattern and examples.

### Step 4: Validate

Validate JSON syntax and inspect the visual.json to confirm spec content and field bindings.

## Spec Authoring Rules

### Data Binding
- Vega: `"data": [{"name": "dataset"}]` (array form)
- Vega-Lite: `"data": {"name": "dataset"}` (object form)
- Fields reference display names. Special characters (`.`, `[`, `]`, `\`, `"`) become `_`
- Spaces are NOT replaced — field names keep their spaces

### Responsive Sizing (Vega)

Use Deneb's built-in signals for responsive container sizing:
```json
"width": {"signal": "pbiContainerWidth - 25"},
"height": {"signal": "pbiContainerHeight - 27"}
```

### Config (Separate from Spec)

Always provide a config for consistent styling. Use `examples/standard-config.json` as a baseline. Key settings: `autosize: fit`, `view.stroke: transparent`, `font: Segoe UI`.

## Theme Integration

Use Power BI theme colors instead of hardcoded hex values:

| Function/Scheme | Purpose | Usage |
|-----------------|---------|-------|
| `pbiColor(index)` | Theme color by index (0-based) | `{"signal": "pbiColor(0)"}` |
| `pbiColor(0, -0.3)` | Darken theme color by 30% | Shade: -1 (dark) to 1 (light) |
| `pbiColor("negative")` | Sentiment colors | `"min"`, `"middle"`, `"max"`, `"negative"`, `"positive"` |
| `pbiColor("bad")` | Aliases for sentiment | `"bad"` = `"negative"`, `"good"` = `"positive"` |
| `pbiColorNominal` | Categorical palette | `"range": {"scheme": "pbiColorNominal"}` |
| `pbiColorOrdinal` | Ordinal palette | `"range": {"scheme": "pbiColorOrdinal"}` |
| `pbiColorLinear` | Continuous gradient | `"range": {"scheme": "pbiColorLinear"}` |
| `pbiColorDivergent` | Divergent gradient | `"range": {"scheme": "pbiColorDivergent"}` |

## Interactivity

Enable interactivity via the `vega` objects in visual.json:

| Feature | Property | Default | Notes |
|---------|----------|---------|-------|
| Tooltips | `enableTooltips` | `true` | Use `"tooltip": {"signal": "datum"}` in encode |
| Context menu | `enableContextMenu` | `true` | Right-click drill-through |
| Cross-filtering | `enableSelection` | `false` | Requires `__selected__` handling |
| Cross-highlighting | `enableHighlight` | `false` | Creates `<field>__highlight` fields |

### Cross-Filtering

When `enableSelection` is true, handle `__selected__` (`"on"`, `"off"`, `"neutral"`) in encode blocks:
```json
"fillOpacity": [
  {"test": "datum.__selected__ == 'off'", "value": 0.3},
  {"value": 1}
]
```

### Cross-Highlighting

Use layered marks — background at reduced opacity, foreground shows `<field>__highlight` values.

### Special Runtime Fields

Key fields: `__row__` (zero-based row index), `__selected__` (selection state), `<field>__highlight` + `<field>__highlightStatus` (cross-highlighting), `<field>__formatted` (pre-formatted string), `<field>__format` (format string).

> **Breaking change in Deneb 1.9:** `__identity__` and `__key__` were removed. Use `datum.__row__` instead.

## Best Practices

1. **Use Vega-Lite** unless Vega-specific features are needed
2. **Always use `autosize: fit`** in config for responsive sizing
3. **Use `pbiContainerWidth`/`pbiContainerHeight`** signals for responsive Vega specs
4. **Use theme colors** (`pbiColor`, `pbiColorNominal`) instead of hex values
5. **Enable tooltips** with `"tooltip": {"signal": "datum"}` on marks
6. **Mind row limits** — 10K default; set `dataLimit.override` and use `renderMode: canvas` for large datasets
7. **Test field names** — verify `nativeQueryRef` matches spec field references
8. **Avoid external data** — AppSource certification prevents loading external URLs
9. **Escaping depends on context** — double quotes in standalone specs, doubled single quotes in PBIR visual.json

## When to Use Deneb

Deneb is the preferred choice for **advanced custom visuals** that need interactivity and go beyond what native Power BI visuals offer:
- Custom chart types not available natively (bullet charts, beeswarms, sankeys, etc.)
- Fine-grained control over visual encoding, animation, and interactivity
- Vector-based rendering (crisp at any size)

For inline micro-charts in table/matrix rows, prefer **SVG visuals** (see `svg-visuals` skill).

## References

| Reference | Purpose |
|---|---|
| `references/capabilities.md` | Object properties, data roles, template format v1 |
| `references/pbir-structure.md` | Complete visual.json structure, literal encoding, query state |
| `references/vega-lite-patterns.md` | 10+ Vega-Lite chart patterns |
| `references/vega-patterns.md` | Vega spec anatomy, encode blocks, advanced charts |
| `references/community-examples.md` | Template repos, fetch patterns, format conversion |

## Examples

See `examples/` for ready-to-use artifacts:
- `standard-config.json` — reusable Deneb config
- `spec/vega-lite/` — standalone Vega-Lite specs (bullet chart, KPI card)
- `spec/vega/` — standalone Vega specs (bar chart, line chart)
- `visual/` — complete PBIR visual.json files (bullet chart, KPI card, trend line, YTD comparison, YTD line chart)
