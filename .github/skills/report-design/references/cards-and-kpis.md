# Cards and KPIs: Design Best Practices

Cards and KPI visuals occupy the most prominent position on a report page (top-left, per the 3-30-300 rule). Every KPI must answer two questions without requiring the reader to think:

1. **"Is this good or bad?"** — answered by a target and gap
2. **"Is it getting better or worse?"** — answered by a trend

## Limiting KPI Quantity

Working memory holds approximately 3-4 information chunks. **5 represents a practical ceiling for most pages.** Every KPI must directly serve the page's central question. Metrics that don't contribute are noise.

## Choosing Actionable Metrics

A useful test: *"If this number changed 20%, should someone act differently?"* If the answer is no, the metric hasn't earned dashboard space.

Comparative metrics (orders vs. prior year) outperform absolute ones because they immediately signal relative performance.

## Sourcing Targets

| Target Source | When to Use | Example DAX |
|---|---|---|
| **Prior year (1YP)** | Default choice when no budget exists | `CALCULATE([Measure], DATEADD('Date'[Date], -1, YEAR))` |
| **Prior month/period** | Short-term operational metrics | `CALCULATE([Measure], DATEADD('Date'[Date], -1, MONTH))` |
| **Budget/forecast** | When budgets exist in the model | Direct measure reference |
| **Rolling average** | Smoothing volatile metrics | `CALCULATE([Measure], DATESINPERIOD('Date'[Date], MAX('Date'[Date]), -3, MONTH))` |

**Preferred**: Add targets to the semantic model as model-level measures (reusable, server-side evaluation).

**Fallback**: Extension measures in `reportExtensions.json`. Use only when the target is report-specific.

**If no clear target exists**: Ask the user to discuss options. Do not leave KPIs bare.

## The Three Elements of a Good KPI

| Element | Purpose | Example |
|---------|---------|---------|
| **Actual value** | Shows magnitude | 518M |
| **Target / comparison** | Establishes the benchmark | Target: 483M |
| **Gap (delta)** | Explicitly answers "good or bad?" | +35.4M (+7.3%) |

Express gaps in **both absolute and percentage terms** — the absolute shows scale, the percentage shows relative significance.

**Always label the target** — set `goals.goalText` to describe the comparison: "1YP", "Budget", "3M Avg".

### Implementation Patterns

**KPI visual**: Bind `Indicator`, `Goal`, and `TrendLine` data roles.

**Card with extension measures**:

```dax
Revenue vs Target =
VAR _actual = [Actuals MTD]
VAR _target = [Sales Target MTD]
VAR _gap = _actual - _target
RETURN FORMAT(_gap, "+#,##0;-#,##0") & " (" & FORMAT(DIVIDE(_gap, _target), "+0.0%;-0.0%") & ")"
```

## Adding Trends

Options for adding trends to KPI cards:

1. **KPI visual type**: Built-in trend line via `TrendLine` data role
2. **SVG sparkline**: Extension measure generating inline SVG (see `svg-visuals` skill)
3. **Adjacent line chart**: Small line chart positioned next to or below the card

## Formatting with Intent

### Size Hierarchy

1. Headline number (largest, boldest)
2. Verdict / gap (medium, colored)
3. Supporting context — target, trend (smallest, muted)

### Conditional Color and Symbols

Apply conditional formatting to the **gap** — not the primary value. Pair color with directional symbols (arrows) for accessibility.

**Accessible palettes**: Blue/orange instead of red/green. Always pair color with a secondary cue.

### Display Units and Number Formatting

Round aggressively at the KPI level: **"518M" beats "517,893,412"**. Precision belongs in detail tables.

**"Auto" display units do not work reliably** when measures have custom format strings. Pick the display unit explicitly.

#### Display Unit Selection Rule

Pick the largest unit where the displayed integer part is >= 1:

```
if value >= 1,000,000,000,000:  Trillions
elif value >= 1,000,000,000:    Billions
elif value >= 1,000,000:        Millions
elif value >= 1,000:            Thousands
else:                           None
```

Precision: 1 digit → precision 1 (e.g., 3.8M); 2+ digits → precision 0 (e.g., 35bn). Percentage measures always use unit=None, precision=1.

#### `indicatorDisplayUnits` Enum

| Value | Label |
|---|---|
| 0 | Auto (unreliable — avoid) |
| 1 | None |
| 1000 | Thousands |
| 1000000 | Millions |
| 1000000000 | Billions |
| 1000000000000 | Trillions |

### Labels and Titles

**Title vs. callout/category label — show one, not both.** Showing both is redundant:

- **Category label only (preferred)**: Hide visual title. Cleaner, more room for the value.
- **Title only**: Hide category label. Use when page context already establishes meaning.

**Card sizing**: Minimum recommended height: **130-150px** for value + category label.

Hide auto-generated subtitles (they repeat field binding names): set `subtitle.show` to `false`.

## Icons in KPI Cards

Use SVG extension measures with `dataCategory: ImageUrl` — see the `svg-visuals` skill for the full pattern.

```dax
Trend Arrow SVG =
VAR _gap = [Actuals MTD] - [Sales Target MTD]
VAR _color = IF(_gap >= 0, "#2B7A78", "#D4602E")
VAR _rotation = IF(_gap >= 0, "0", "180")
RETURN
"data:image/svg+xml;utf8," &
"<svg xmlns=""http://www.w3.org/2000/svg"" width=""24"" height=""24"" viewBox=""0 0 24 24"">" &
"<polygon points=""12,4 20,16 4,16"" fill=""" & _color & """ transform=""rotate(" & _rotation & " 12 12)""/>" &
"</svg>"
```

Icons should be used sparingly — only when they add information beyond color and numbers.

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| Bare number with no target | Reader cannot judge performance | Add target and gap |
| Too many cards (>5) | Exceeds working memory | Prioritize by page question |
| Same display units across all cards | Misrepresents scale | Select per-visual unit based on value magnitude |
| Color on primary value | Distracts from judgment | Apply color to gap/delta only |
| Decorative icons | Visual noise | Use icons only when they convey information |
