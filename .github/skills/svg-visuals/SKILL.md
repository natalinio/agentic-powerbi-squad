---
name: svg-visuals
description: >-
  Use when creating inline SVG graphics via DAX measures for Power BI reports.
  Triggers: "create SVG visual", "add DAX sparkline", "SVG measure", "inline graphics with DAX",
  "progress bar in DAX", "SVG in Power BI", "bullet chart via DAX", "KPI indicator with SVG",
  "data bar", "dumbbell chart", "status pill", "lollipop chart", "overlapping bars",
  "gauge in DAX", "donut chart in DAX", "boxplot in DAX", "IBCS bar chart",
  "jitter plot", "box-and-whisker chart", "SVG extension measure", "ImageUrl dataCategory".
user-invocable: true
---

# Skill: SVG Visuals via DAX Measures (PBIR)

## Purpose
Generate inline SVG graphics using DAX measures that return SVG markup strings. These render as images in table, matrix, card, image, and slicer visuals. Store as extension measures in `reportExtensions.json`.

## How It Works

1. A DAX measure returns an SVG string prefixed with `data:image/svg+xml;utf8,`
2. The measure's `dataCategory` is set to `ImageUrl`
3. Power BI renders the SVG as an image in supported visuals

## Supported Visuals

| Visual | visualType | Binding | Reference |
|--------|------------|---------|-----------|
| Table | `tableEx` | `grid.imageHeight` / `grid.imageWidth` | `references/svg-table-matrix.md` |
| Matrix | `pivotTable` | Same as table | `references/svg-table-matrix.md` |
| Image | `image` | `sourceType='imageData'` + `sourceField` | `references/svg-image-visual.md` |
| Card (New) | `cardVisual` | `callout.imageFX` | `references/svg-card-slicer.md` |
| Slicer (New) | `advancedSlicerVisual` | Header images | `references/svg-card-slicer.md` |

## Workflow: Creating an SVG Measure

### Step 0: Design and Preview

Before writing DAX, design the SVG visually:

1. **Query the model first** — use actual values with the intended filter context. Use real numbers, not placeholders.
2. **Write static SVG to a temp file** — save to a `.svg` file and open in a browser to preview layout, colors, and proportions.
3. **Ask for feedback** before converting to DAX — iterating on static SVG is far easier than on DAX string concatenation.
4. **Colors must be hex codes with `#`** — e.g., `fill='#2B7A78'`. Never use `%23` URL encoding or named colors. Always hex.

### Step 1: Create the Extension Measure

Create the extension measure in `reportExtensions.json`:
- `dataType`: `Text`
- `dataCategory`: `ImageUrl`
- `displayFolder`: `SVG Charts`

Extension measures use `"Schema": "extension"` in the SourceRef:

```json
{
  "field": {
    "Measure": {
      "Expression": {
        "SourceRef": {"Schema": "extension", "Entity": "TableName"}
      },
      "Property": "SVG Measure Name"
    }
  }
}
```

### Step 2: Bind to a Visual

See the appropriate reference for the target visual type:
- Table/Matrix → `references/svg-table-matrix.md`
- Image → `references/svg-image-visual.md`
- Card/Slicer → `references/svg-card-slicer.md`

### Step 3: Validate

Validate JSON syntax and inspect the file to confirm measure definitions and data categories.

## DAX SVG Conventions

### Measure Structure (VAR Pattern)

Every SVG measure must follow a strict VAR-based structure. Organize code into clearly separated regions:

```dax
SVG Measure =
-- CONFIG: Input fields and visual parameters
VAR _Actual = [Sales Amount]
VAR _Target = [Sales Target]
VAR _Scope = ALLSELECTED ( 'Product'[Category] )

-- CONFIG: Colors
VAR _BarColor = "#5B8DBE"
VAR _TargetColor = "#333333"

-- NORMALIZATION: Scale values to SVG coordinate space
VAR _AxisMax = CALCULATE( MAXX( _Scope, [Sales Amount] ), REMOVEFILTERS( 'Product'[Category] ) ) * 1.1
VAR _AxisRange = 100
VAR _ActualNormalized = DIVIDE( _Actual, _AxisMax ) * _AxisRange

-- SVG ELEMENTS: One VAR per visual element
VAR _SvgPrefix = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 25'>"
VAR _Sort = "<desc>" & FORMAT( _Actual, "000000000000" ) & "</desc>"
VAR _Bar = "<rect x='0' y='5' width='" & _ActualNormalized & "' height='15' fill='" & _BarColor & "'/>"
VAR _TargetLine = "<rect x='" & DIVIDE( _Target, _AxisMax ) * _AxisRange & "' y='2' width='2' height='21' fill='" & _TargetColor & "'/>"
VAR _SvgSuffix = "</svg>"

-- ASSEMBLY: Combine in rendering order (back to front)
VAR _SVG = _SvgPrefix & _Sort & _Bar & _TargetLine & _SvgSuffix

RETURN _SVG
```

Key conventions:
- **CONFIG section first** — input measures, scope column, colors, font settings. Users change only this section.
- **NORMALIZATION section** — scale raw values to SVG coordinate space (see below).
- **SVG ELEMENTS** — one VAR per `<rect>`, `<circle>`, `<text>`, `<line>`, etc.
- **ASSEMBLY** — concatenate elements in document order (first = back layer, last = front).
- **`<desc>` sort trick** — embed `FORMAT(_Actual, "000000000000")` in a `<desc>` tag so the table/matrix can sort by the SVG column.

### Axis Normalization (Critical)

SVG coordinates must be normalized to a fixed range. Raw measure values cannot be used directly as pixel coordinates:

```dax
-- 1. Define the SVG coordinate range
VAR _BarMin = 0
VAR _BarMax = 100

-- 2. Find the maximum value across all rows in the visual's filter context
VAR _Scope = ALLSELECTED( 'Table'[GroupColumn] )
VAR _MaxInScope = CALCULATE( MAXX( _Scope, [Measure] ), REMOVEFILTERS( 'Table'[GroupColumn] ) )
VAR _AxisMax = _MaxInScope * 1.1   -- 10% padding

-- 3. Normalize each value to the SVG range
VAR _AxisRange = _BarMax - _BarMin
VAR _Normalized = DIVIDE( _Actual, _AxisMax ) * _AxisRange
```

Use `ALLSELECTED` for the scope when the chart should respond to slicer context. Use `ALL` for a fixed axis across all filter contexts. The `* 1.1` padding prevents bars from touching the edge.

### HASONEVALUE Guard

Table/matrix SVG measures must guard against subtotal/total rows where multiple categories are in scope:

```dax
IF( HASONEVALUE( 'Table'[GroupColumn] ),
    -- SVG code here
)
```

Without this guard, the measure evaluates on grand total rows with meaningless aggregated values.

### Escaping and Color Rules

- **Single quotes for SVG attributes** — avoids DAX double-quote escaping: `fill='#2196F3'`
- **Double quotes in DAX**: escape as `""` (DAX convention)
- **`viewBox`** for responsive scaling: `viewBox='0 0 100 25'`
- **`xmlns`** required on `<svg>` element
- **Hex colors with `#` only** — e.g., `fill='#2196F3'`. `%23` URL encoding causes errors in image visuals. Never use named colors.
- **No JavaScript** — SVG must be purely declarative

### SVG Coordinate System

- Y=0 is at the **top** — invert values for charts: `_Height - _Value`
- Use `viewBox` with a 0-100 range for normalized coordinates
- Elements render in document order (first = back, last = front)

### Number Formatting (Adaptive Scale)

```dax
VAR _Label = SWITCH(TRUE(),
    _Actual <= 1E3,  FORMAT(_Actual, "#,0"),
    _Actual <= 1E6,  FORMAT(_Actual, "#,0, K"),
    _Actual <= 1E9,  FORMAT(_Actual, "#,0,, M"),
    FORMAT(_Actual, "#,0,,, B")
)
```

## When to Use SVG vs Deneb vs Core Visuals

| Criterion | Core Visual | SVG (DAX) | Deneb (Vega-Lite) |
|---|---|---|---|
| Maintenance cost | Low | Medium | Medium-High |
| Interactivity (cross-filter, tooltip) | Native | None | Full |
| Inline in table/matrix | No | Yes | No |
| Non-native chart types | No | Yes (simple) | Yes (complex) |
| Accessibility | Good | Limited | Good (tooltips, ARIA) |
| Performance on large datasets | Good | OK (1 SVG per row) | Watch > 10K rows |

**Rule**: prefer core visuals → if inline micro-chart in table/matrix needed: SVG → if advanced custom chart with interactivity needed: Deneb.

## References

| Reference | Purpose |
|---|---|
| `references/svg-elements.md` | Quick reference for SVG elements usable in DAX |
| `references/svg-table-matrix.md` | Table/matrix binding, sort trick, axis normalization, patterns |
| `references/svg-image-visual.md` | Image visual binding (`sourceType=imageData`), standalone patterns |
| `references/svg-card-slicer.md` | Card/slicer binding, arrow indicator, gauge, donut, progress bar patterns |

## Examples

See `examples/` for 12 ready-to-use DAX measure templates covering sparklines, progress bars, bullet charts, dumbbells, IBCS bars, status pills, boxplots, jitter plots, lollipops, overlapping bars, and waterfalls.
