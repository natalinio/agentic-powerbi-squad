# Tables and Matrices: Design Best Practices

Tables and matrices sit at the bottom of the detail gradient (3-30-300 rule). The core principle: **format tables to answer specific reader questions, not to display all available data.** Content selection comes first; formatting amplifies the signal.

## Decision-Making First

Before creating a table or matrix, answer:

1. **What question does this table answer?** (e.g., "Which products are behind target?")
2. **Who reads it and what action do they take?**
3. **What columns are essential?** Remove everything else.
4. **What should the reader see first?** This determines sort order and emphasis.

## Table vs Matrix: When to Use Which

| Scenario | Visual Type | Why |
|---|---|---|
| Flat list of records, no grouping | `tableEx` | Simple rows, no hierarchy needed |
| Hierarchical categories (Region > Country > City) | `pivotTable` (matrix) | Rows expand/collapse, subtotals per level |
| Cross-tab / pivot (categories on both axes) | `pivotTable` | Row headers + column headers + values |
| 2+ categorical columns forming a hierarchy | `pivotTable` | Avoids repeating parent values in every row |

**Rule of thumb**: If the table has 2+ categorical columns where one is a parent of the other, use a matrix. A flat table with repeating parent values is a common anti-pattern.

## Column Selection

- **Leading columns**: Primary dimension(s) the reader groups by
- **Measure columns**: KPIs that matter for this page
- **Avoid**: Internal IDs, keys, redundant names, unrelated measures

## Column Ordering (left to right)

1. Row labels / hierarchy (leftmost)
2. Primary measure (answers the page question)
3. Secondary measures (supporting metrics)
4. Variance / delta columns

## Sorting

**Always sort by the most important measure, descending.** Alphabetical sorting rarely answers useful questions. For time-based detail tables, sort ascending by date.

## Formatting

### Philosophy: Subtract, Don't Add

Remove visual noise and let whitespace do the separation work:

- Strip or minimize gridlines (horizontal only if any)
- Remove banded row shading (or use extremely subtle tint, 2-3% opacity)
- Reduce border complexity
- Increase row padding

### Key Formatting Properties

| Property | Recommended | Notes |
|---|---|---|
| Grid lines | Horizontal only, or none | Vertical lines add clutter |
| Banded rows | Off or very subtle | Heavy banding competes with data |
| Row padding | 6-10px | More breathing room than default |
| Header font | Segoe UI Semibold, 10-12pt | Distinguishable but not dominant |
| Value font | Segoe UI, 10-12pt | Consistent across all value columns |
| Column width | Auto or proportional | Avoid truncation |
| Borders | Minimal or none | Let content structure speak |

### Number Formatting in Tables

Unlike KPI cards, tables show **more precision** — this is where readers go for detail:

- Use the model's format string (`#,##0` for integers, `#,##0.0%` for percentages)
- Do NOT apply display units in tables — show full values
- Align numbers right, text left

## Conditional Formatting

Apply strategically — formatting on every column creates overload where nothing stands out.

### Data Bars

Apply to the **primary measure column**. Data bars let readers compare magnitudes at a glance.

### Color Scales on Variance Columns

Apply to **variance/delta columns only** — not absolute values. Use diverging scheme:
- Red/warm for negative/underperformance
- Blue/cool for positive/overperformance (avoid green for accessibility)

Extension measure pattern:

```dax
OTD Color = IF([OTD % (Lines)] >= 0.9, "good", IF([OTD % (Lines)] >= 0.8, "neutral", "bad"))
```

### What to Format and What Not To

| Column Type | Formatting | Rationale |
|---|---|---|
| Primary measure | Data bars | Magnitude comparison |
| Variance / delta | Color scale or font color | Signals good/bad |
| Status indicators | Color when above/below threshold | Only when threshold matters |
| Dimension columns | None | Text labels need no emphasis |
| Secondary measures | None | Formatting everything means formatting nothing |

## Sparklines and Inline Trends

Sparklines add temporal context — they distinguish between a product behind target but improving vs. one that is declining.

For richer inline visuals (dumbbell charts, bullet charts, progress bars), use SVG extension measures via the `svg-visuals` skill. Use only when benefits justify added complexity.

## Matrix-Specific Guidance

### Row Hierarchy

Bind categories from broadest to most granular (e.g., Key Account > Account > Product).

### Subtotals

Subtotals at each hierarchy level are usually desirable. For very deep hierarchies (4+ levels), consider hiding intermediate subtotals.

### Expand/Collapse

Default: collapsed to top level (respects detail gradient). Readers expand only what they need.

## Sizing

- **Minimum height**: 180-200px (header + 5-8 visible rows)
- **Full width**: Tables typically span full page width
- **Auto-size width**: Turn off when table shares a row with another visual (prevents horizontal scrollbar)

When auto-size is off:
```
columnHeaders.autoSizeColumnWidth = false  → columns fit container proportionally
columnWidth.value = <pixels>               → fixed width (only when autoSize is off)
```

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| Flat table with repeating parent values | Redundant, hard to scan | Use matrix with hierarchy |
| Too many columns (>8) | Horizontal scroll, overload | Remove non-essential columns |
| Alphabetical sort | Rarely answers questions | Sort by primary measure descending |
| Conditional formatting on every column | Visual overload | Data bars on primary, color on variance only |
| Heavy gridlines + banded rows | Noise competes with data | Whitespace to separate rows |
| Display units in tables | Loses detail | Show full precision |
| Unformatted data dump | Nobody scans raw number walls | Apply full formatting workflow |
