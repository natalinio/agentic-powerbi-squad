---
name: html-visuals
description: >-
  Use when creating full-frame HTML or SVG visuals rendered via the Power BI HTML custom visual
  (htmlContent GUID). Triggers: "HTML custom visual Power BI", "misura DAX HTML", "html visual
  power bi", "full-frame SVG", "trend chart HTML", "narrative panel DAX", "comparison table DAX",
  "HTML visual TMDL", "dataCategory ImageUrl HTML", "custom visual HTML GUID",
  "grafico html power bi", "visual custom power bi", "html custom visual",
  "SVG fullscreen power bi", "full page SVG DAX".
user-invocable: true
---

# Skill: HTML Visuals via DAX Measures (htmlContent custom visual)

## Purpose

Generate DAX measures that return full HTML or SVG markup for the Power BI **HTML custom visual**
(`htmlContent443BE3AD55E043BF878BED274D3A6855`). Unlike inline SVG micro-charts (see `svg-visuals`
skill), these measures render in a dedicated full-frame visual and support CSS layout, multi-element
HTML structures, and full-canvas SVG charts.

## When to Use This Skill vs `svg-visuals`

| Criterion | `html-visuals` (this skill) | `svg-visuals` |
|---|---|---|
| Visual type | HTML custom visual (htmlContent GUID) | Table, Matrix, Image, Card, Slicer |
| Output format | Full HTML page or full-frame SVG | `data:image/svg+xml;utf8,` prefix |
| CSS support | Full CSS (flex, grid, multi-element) | Inline SVG attributes only |
| Layout | Entire visual frame | Micro-chart per table row |
| TMDL `dataCategory` | `ImageUrl` | `ImageUrl` |
| Binding | `visual-containers/*.json` GUID wiring | PBIR visual role binding |

**Rule**: use `html-visuals` for standalone full-frame visuals → use `svg-visuals` for inline micro-charts inside table/matrix columns.

## Supported Output Types

| Pattern | Template | Use when |
|---|---|---|
| Full-frame YoY SVG chart | `examples/trend-chart.dax` | Quarterly trend comparison, CY vs PP |
| HTML ranked table | `examples/comparison-table.dax` | Top-N items with score coloring and K cost |
| Executive narrative panel | `examples/narrative-panel.dax` | KPI summary, best/worst performers |

## Workflow: Creating an HTML Visual Measure

### Step 1: Read the Model

Before writing any DAX, read the target TMDL files to confirm:
- Exact table and column names (never invent names — read from disk)
- Calendar model type: **continuous** or **snapshot** (affects time intelligence — see `references/html-visual-patterns.md`)
- Locale setting (`it-IT` requires decimal conversion before SVG attributes)

### Step 2: Choose the Template

Select the closest template from `examples/` and adapt it:
1. Replace placeholder table/column references with real model objects.
2. Confirm locale — Italian models need `SUBSTITUTE(FORMAT(val,"#0.0"),",",".")`.
3. Adjust colors, labels, and viewBox dimensions to match the report design system.

### Step 3: Declare the Measure in TMDL

Add the measure to the target table TMDL file with correct indentation and properties.
See `references/tmdl-authoring-rules.md` for mandatory rules (BOM, indentation, no aliases).

Required measure properties:
```
		dataCategory: ImageUrl
```
(2-tab indent inside the measure block)

### Step 4: Wire the Visual in PBIR

Edit the `visual-containers/*.json` for the page hosting the HTML visual.
See `references/html-visual-binding.md` for the correct `visualType` GUID, field binding,
and `visualContainerObjects` pattern.

### Step 5: Validate

1. Test with representative values: one low, one medium, one high.
2. Open the PBIP in Power BI Desktop — verify no TMDL parse errors on open.
3. Confirm the visual fills the frame correctly (no letterbox, no overflow).

## Core Patterns

### 1. CSS Baseline (mandatory in every measure RETURN)

```dax
"<style>html,body{margin:0;padding:0;overflow:hidden}svg{display:block;width:100vw;height:100vh}</style>"
```

Do NOT use `height:100%` on body — Power BI renders the visual in an iframe where `100%` resolves to 0. Always use `100vh`.

### 2. Full-Frame SVG Root

```dax
"<svg width='100%' height='100%' viewBox='0 0 540 250' xmlns='http://www.w3.org/2000/svg' preserveAspectRatio='none' font-family='Segoe UI,Arial,sans-serif'>"
```

- `preserveAspectRatio='none'` — fills the visual frame without letterboxing
- `viewBox` — defines the internal coordinate space; use fixed integers (e.g. `0 0 540 250`)
- `xmlns` — required on the root `<svg>` element

### 3. Locale-Safe Decimals (Italian models)

```dax
VAR _SafeVal = SUBSTITUTE(FORMAT(value, "#0.0"), ",", ".")
```

Italian locale (`it-IT`) formats decimals with a comma. SVG numeric attributes require a dot.
Apply this conversion to **every** numeric value used in SVG attributes.

### 4. Y-Axis Normalization (SVG coordinate system — Y=0 is top)

```dax
VAR Ypx = MarginTop + ROUNDDOWN(PlotHeight * (1 - DIVIDE(val - YMin, YRange, 0)), 0)
```

Where `PlotHeight = ChartHeight - MarginTop - MarginBottom`.
Always apply `IF(ISBLANK(val), 0, val)` before entering the Y formula.
Add 8% padding to Y scale: `YPad = (YMaxRaw - YMinRaw) * 0.08`.

### 5. Score Color Mapping

```dax
VAR ScoreColor = SWITCH(TRUE(), score >= 75, "#038C25", score >= 50, "#FFF3CD", "#C00000")
-- Score colors: >=75 green, >=50 yellow, <50 red
```

## Guardrails

1. BOM: write TMDL files as UTF-8 without BOM (see `references/tmdl-authoring-rules.md`).
2. Indentation: DAX body lines → 3 tabs; property lines → 2 tabs.
3. No measure aliases: `measure 'X' = [Y]` throws `UnsupportedObjectType` on file open.
4. Decimal separators in SVG attributes must use `.` — always apply locale conversion.
5. Never use `height:100%` on body in the CSS baseline — use `100vh`.
6. Test output with at least one low, one medium, and one high sample value.
7. After any TMDL edit, verify the file opens in Power BI Desktop without errors.

## References

| Reference | Purpose |
|---|---|
| `references/html-visual-binding.md` | htmlContent GUID, PBIR visual-container wiring, dataCategory binding |
| `references/tmdl-authoring-rules.md` | TMDL syntax rules: BOM, indentation, aliases, sourceColumn, relationships |
| `references/html-visual-patterns.md` | CSS baseline, layout patterns, snapshot time intelligence, score colors |

## Examples

| File | Chart type | Key features |
|---|---|---|
| `examples/trend-chart.dax` | YoY SVG line chart | Quarterly snapshots, gradient area fill, locale-safe labels, CY vs PP |
| `examples/comparison-table.dax` | HTML ranked table | Top-N items, score coloring, K-formatted costs, delta |
| `examples/narrative-panel.dax` | Executive narrative panel | KPI summary, best/worst performers, HTML layout |
