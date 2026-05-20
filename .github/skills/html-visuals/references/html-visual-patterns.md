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

---

## HTML Bar Chart in PBI iframe — Reliable Patterns

> **Critical**: PBI htmlContent renders inside an `<iframe>` where the document body has **no explicit height**. Any `height` that depends on `100%` or `calc(100% - X)` resolution will collapse to 0 or behave unpredictably.

### Anti-Patterns (DO NOT USE)

| Pattern | Why it fails |
|---|---|
| `height: X%` on bar divs inside flex parent | `%` resolves to `auto` when parent height is determined by flex (not explicit) |
| `height: calc(100% - 28px)` on wrapper | PBI iframe does not propagate explicit height to body → resolves to 0 |
| `height: 100%` on chart container | Same root cause — no explicit ancestor height |
| `position:absolute; top:X; bottom:0` inside another `position:absolute; top:X; bottom:0` | Inner container collapses to 0 height — double-absolute nesting anti-pattern |
| `flex-grow: N` spacer above bars | Spacer expands → bars pushed out of view |

### Reliable Pattern — Explicit Pixel Container

**Rule**: The flex row that holds the bars MUST have an **explicit pixel height**. No exceptions inside PBI iframe.

```html
<!-- ✅ Correct: explicit height on bar flex row -->
<div style="position:relative; height:360px; display:flex; align-items:flex-end; justify-content:space-around; padding-right:36px;">

  <!-- Optional: absolute-positioned gridlines inside this container -->
  <div style="position:absolute; bottom:90px; left:0; right:0; border-top:1px dashed rgba(255,255,255,0.12);"></div>
  <div style="position:absolute; bottom:180px; left:0; right:0; border-top:1px dashed rgba(255,255,255,0.12);"></div>
  <div style="position:absolute; bottom:270px; left:0; right:0; border-top:1px dashed rgba(255,255,255,0.12);"></div>

  <!-- Each bar column: value label + bar + category label -->
  <div style="display:flex; flex-direction:column; align-items:center; gap:4px;">
    <span style="font-size:11px; color:#ccc;">VALUE%</span>
    <div style="width:52px; height:Hpx; background:#FA9600; border-radius:3px 3px 0 0;"></div>
    <span style="font-size:11px; color:#aaa;">Q1</span>
  </div>

</div>
```

### DAX Bar Height Formula

```dax
VAR _DataMin = MIN(MIN(Q1, Q2), MIN(Q3, Q4))
VAR _DataMax = MAX(MAX(Q1, Q2), MAX(Q3, Q4))
VAR _Range   = _DataMax - _DataMin

-- min bar = 40px, max bar = 310px, container = 360px
VAR H1px = FORMAT(ROUND(40 + DIVIDE(Q1 - _DataMin, IF(_Range=0,1,_Range)) * 270, 0), "0")
VAR H2px = FORMAT(ROUND(40 + DIVIDE(Q2 - _DataMin, IF(_Range=0,1,_Range)) * 270, 0), "0")
VAR H3px = FORMAT(ROUND(40 + DIVIDE(Q3 - _DataMin, IF(_Range=0,1,_Range)) * 270, 0), "0")
VAR H4px = FORMAT(ROUND(40 + DIVIDE(Q4 - _DataMin, IF(_Range=0,1,_Range)) * 270, 0), "0")
```

### Gridline Positions

With `height:360px` container:

| Visual level | `bottom` value |
|---|---|
| 25% | `90px` |
| 50% | `180px` |
| 75% | `270px` |

**Formula**: `containerHeight × fraction` — always compute from the fixed container height, never from `%`.

### Y-Axis Labels (right side)

```html
<!-- Y-axis label container: position:absolute inside the 360px container -->
<div style="position:absolute; right:0; top:0; height:100%; display:flex; flex-direction:column; justify-content:space-between; padding-bottom:20px;">
  <span style="font-size:10px; color:#888;">30%</span>
  <span style="font-size:10px; color:#888;">25%</span>
  <span style="font-size:10px; color:#888;">20%</span>
</div>
```

---

## CSS Donut Chart Pattern

Create a donut chart using pure CSS `conic-gradient` + an absolute inner circle as the hole:

```html
<div style="position:relative; width:120px; height:120px; border-radius:50%;
            background: conic-gradient(#4CAF50 0% 45%, #FA9600 45% 72%, #2196F3 72% 100%);">
  <!-- Donut hole: 54-60% of outer size, same color as card background -->
  <div style="position:absolute; top:50%; left:50%;
              transform:translate(-50%,-50%);
              width:56%; height:56%;
              background:#2a2a2a;
              border-radius:50%;"></div>
</div>
```

Rules:
- Hole diameter = 50–60% of outer circle. Adjust for visual balance.
- `background` color of inner circle MUST match the card/panel background exactly (e.g. `#2a2a2a` for dark theme).
- `conic-gradient` segments are defined as `color from% to%` — values are cumulative percentages.
- For single-series donuts (filled vs empty): `conic-gradient(#FA9600 0% VALUE%, #333 VALUE% 100%)`.

---

## Executive Insight Panel Pattern

4-section narrative panel for executive dashboards. All values injected via DAX string concatenation.

```html
<div style="height:100%; box-sizing:border-box; padding:12px 16px;
            background:#2a2a2a; border-radius:6px;
            display:flex; gap:10px; font-family:Segoe UI,Arial,sans-serif;">

  <!-- Left: icon -->
  <div style="font-size:22px; padding-top:2px;">💡</div>

  <!-- Right: sections -->
  <div style="flex:1; display:flex; flex-direction:column; gap:0;">

    <!-- 1. Title + Summary -->
    <p style="font-weight:bold; font-size:14px; color:#fff; margin:0 0 4px 0;">Key Insight</p>
    <p style="font-size:12px; color:#ccc; margin:0 0 10px 0;">DYNAMIC SUMMARY LINE</p>

    <!-- 2. Highlights -->
    <div style="border-top:1px solid rgba(255,255,255,0.1); padding-top:8px; margin-bottom:8px;">
      <p style="font-size:11px; font-weight:bold; color:#aaa; margin:0 0 4px 0;">HIGHLIGHTS</p>
      <ul style="list-style:none; padding:0; margin:0; display:flex; flex-direction:column; gap:3px;">
        <li style="font-size:11px; color:#ccc;">• Highlight 1</li>
        <li style="font-size:11px; color:#ccc;">• Highlight 2</li>
      </ul>
    </div>

    <!-- 3. Risk -->
    <div style="border-top:1px solid rgba(255,255,255,0.1); padding-top:8px; margin-bottom:8px;">
      <p style="font-size:11px; color:#e8a838; margin:0;">⚠ RISK LINE</p>
    </div>

    <!-- 4. Action -->
    <div style="border-top:1px solid rgba(255,255,255,0.1); padding-top:8px;">
      <p style="font-size:11px; color:#4CAF50; font-weight:bold; margin:0;">→ ACTION STATEMENT</p>
    </div>

  </div>
</div>
```

### Color tokens for insight panel (dark theme)

| Role | Color |
|---|---|
| Title | `#ffffff` |
| Body / bullets | `#cccccc` |
| Section headers | `#aaaaaa` |
| Risk / warning | `#e8a838` |
| Positive KPI | `#4CAF50` |
| Accent / highlight value | `#FA9600` |
| Section divider | `rgba(255,255,255,0.1)` |

### DAX injection pattern

```dax
VAR GARPct = FORMAT([Green Assets Ratio], "0.0%")
VAR NeutralPct = FORMAT([ESG Neutral %], "0.0%")

RETURN
  "<div style='...'>..." &
  "<p style='font-size:12px;color:#ccc'>GAR reached <span style='color:#FA9600;font-weight:bold'>" & GARPct & "</span> this period.</p>" &
  "...</div>"
```

### Recommended visual position

Place the insight panel in the **bottom-left area** below analytical charts (not below slicers). Suggested sizing: `width ≈ 65% of page width`, `height ≈ 220–260px`.
