# HTML Visual Patterns Reference

## CSS Baseline

Every HTML visual measure **must** include this CSS baseline in its RETURN string:

```html
<style>html,body{margin:0;padding:0;overflow:hidden}svg{display:block;width:100vw;height:100vh}</style>
```

Rules:
- Do NOT use `height:100%` on body — Power BI renders the visual in an iframe where `100%` resolves to 0.
- Always use `100vh` for full-frame height.
- `overflow:hidden` prevents scrollbars from appearing.

For HTML (non-SVG) measures, adapt the baseline:
```html
<style>*{box-sizing:border-box}html,body{margin:0;padding:0;overflow:hidden;font-family:Segoe UI,Arial,sans-serif;font-size:12px}</style>
```

## Full-Frame SVG Pattern

```dax
RETURN
    "<style>*{box-sizing:border-box;margin:0;padding:0}html,body{margin:0;padding:0;overflow:hidden}svg{display:block;width:100vw;height:100vh}</style>" &
    "<svg width='100%' height='100%' viewBox='0 0 540 250' xmlns='http://www.w3.org/2000/svg' preserveAspectRatio='none' font-family='Segoe UI,Arial,sans-serif'>" &
    -- ... SVG elements ...
    "</svg>"
```

Key attributes on the root `<svg>`:
- `width='100%' height='100%'` — fills the container
- `viewBox='0 0 W H'` — defines the internal coordinate space (use integer constants)
- `preserveAspectRatio='none'` — stretches to fill without letterboxing
- `xmlns='http://www.w3.org/2000/svg'` — required
- `font-family` — set globally here to avoid repeating on every text element

## SVG Coordinate System

- Y=0 is at the **top** — values increase downward.
- Use `viewBox` with fixed integer dimensions (e.g., `0 0 540 250`) for predictable coordinates.
- Elements render in document order: first element = back layer, last element = front layer.

### Y-Axis Normalization Formula

```dax
-- Define visual dimensions
VAR CW = 540   -- canvas width
VAR CH = 250   -- canvas height
VAR ML = 50    -- margin left
VAR MT = 38    -- margin top
VAR MB = 42    -- margin bottom
VAR PW = CW - ML - 15           -- plot width
VAR PH = CH - MT - MB           -- plot height
VAR YBot = MT + PH              -- Y pixel of baseline

-- Scale data to Y pixels
VAR YPad = (YMaxRaw - YMinRaw) * 0.08    -- 8% padding
VAR YMin = YMinRaw - YPad
VAR YMax = YMaxRaw + YPad
VAR YRange = YMax - YMin

VAR Ypx = MT + ROUNDDOWN(PH * (1 - DIVIDE(val - YMin, YRange, 0)), 0)
```

Always apply `IF(ISBLANK(val), 0, val)` before entering the Y formula.

## Locale-Safe Decimals

Italian locale (`it-IT`) formats decimals with a comma. SVG attributes require a dot.

```dax
-- ✅ Locale-safe
VAR _SafeVal = SUBSTITUTE(FORMAT(value, "#0.0"), ",", ".")

-- ❌ Will break SVG rendering on Italian locale
VAR _Broken = FORMAT(value, "#0.0")
```

Apply this conversion to **every** numeric value used in SVG attributes (coordinates, widths, r, cx, cy, etc.).

## Number Formatting (Adaptive Scale)

For label text (not SVG coordinates — text labels can use formatted strings):

```dax
VAR Label = SWITCH(TRUE(),
    value >= 1E9,  FORMAT(value / 1E9, "#,0.0") & " B",
    value >= 1E6,  FORMAT(value / 1E6, "#,0.0") & " M",
    value >= 1E3,  FORMAT(value / 1E3, "#,0.0") & " K",
    FORMAT(value, "#,0")
)
```

For K-formatting (common in cost tables):
```dax
VAR CostoK = FORMAT(value / 1000, "#,##0") & " K"
```

## Score Color Mapping

Standard 3-tier color scheme for score-based visuals:

```dax
VAR ScoreColor = SWITCH(TRUE(),
    score >= 75, "#038C25",   -- green: good
    score >= 50, "#FFF3CD",   -- yellow: warning
    "#C00000"                 -- red: bad
)
-- Score colors: >=75 green (#038C25), >=50 yellow (#FFF3CD), <50 red (#C00000)
```

Always comment the thresholds explicitly in the measure for future maintainability.

## Snapshot-Model Time Intelligence

Models with quarterly snapshots (dates at month 1/4/7/10) **cannot** use `PARALLELPERIOD()` —
it returns BLANK on non-continuous calendars.

### Previous Period (PP) Equivalent for Snapshot Models

```dax
VAR DataFiltro = MAX('Calendario filtro'[Date])
VAR AnnoFiltro = YEAR(DataFiltro)
VAR AnnoPP = AnnoFiltro - 1

-- Quarterly totals for a specific quarter of previous year (e.g., Q1 = month 1)
VAR Q1_PP = CALCULATE(
    SUM(Fact[Value]),
    REMOVEFILTERS(Calendario),
    FILTER(ALL(Fact[DateSnapshot]), YEAR(Fact[DateSnapshot]) = AnnoPP && MONTH(Fact[DateSnapshot]) = 1)
)
-- Repeat for Q2 (month 4), Q3 (month 7), Q4 (month 10)
```

Rules:
- Always include `REMOVEFILTERS(Calendario)` to bypass the date slicer.
- Use `FILTER(ALL(...))` on the fact-table date column, not on the calendar table.
- Do not use `PARALLELPERIOD()`, `SAMEPERIODLASTYEAR()`, or `DATEADD()` on snapshot models.

## Escaping and Quoting in DAX SVG Strings

- Use **single quotes** for SVG attribute values — avoids DAX double-quote escaping:
  ```dax
  "<rect x='0' y='5' width='100' fill='#2196F3'/>"
  ```
- Double quotes inside DAX strings: escape as `""` (DAX convention):
  ```dax
  "<text class=""label"">text</text>"
  ```
- No JavaScript — SVG/HTML must be purely declarative (Power BI strips scripts).
- Hex colors with `#` only — e.g., `fill='#2196F3'`. Never use `%23` URL encoding or named colors.

## HTML Table Pattern

```dax
VAR Header = "<table style='border-collapse:collapse;width:100%;font-size:11px'>" &
             "<tr><th style='padding:4px 8px;border-bottom:2px solid #ccc'>App</th>" &
             "<th>Score</th><th>Cost</th><th>Delta</th></tr>"

VAR Body = CONCATENATEX(
    RowsTable,
    "<tr>" &
    "<td style='padding:3px 8px'>" & [Name] & "</td>" &
    "<td style='background:" & ScoreColor & ";padding:3px 8px'>" & FORMAT([Score],"0.0") & "</td>" &
    "<td style='padding:3px 8px'>" & CostoK & "</td>" &
    "<td style='padding:3px 8px'>" & DeltaTxt & "</td>" &
    "</tr>",
    ""
)

RETURN Header & Body & "</table>"
```

## Null / Blank Safety

Always guard data values before using them in coordinates or labels:

```dax
VAR SafeVal = IF(ISBLANK(rawVal), 0, rawVal)
```

For CONCATENATEX rows that may have BLANKs, add a WHERE filter:
```dax
CONCATENATEX(FILTER(RowsTable, NOT ISBLANK([Value])), ...)
```
