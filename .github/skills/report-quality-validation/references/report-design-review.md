# Report Design Review Checklist

Design quality, visual complexity, and performance assessment for PBIR reports at development time. Distilled from best practices for local/PBIP validation without requiring Power BI Service access.

## The 3/30/300 Rule

| Time | What the user should grasp | Design implication |
|---|---|---|
| **3 seconds** | Main message or headline insight | KPIs, cards, and titles at the top-left |
| **30 seconds** | Context and supporting trends | Charts and comparisons in the middle |
| **300 seconds** | Granular detail for exploration | Tables, matrices, and drill-through in the bottom-right |

## Design Checklist

| # | Check | Severity |
|---|---|---|
| 1 | Page titles present and descriptive | WARNING |
| 2 | Visual spacing consistent (equal gaps between visuals and page margins) | WARNING |
| 3 | Detail gradient followed (KPIs top-left, detail bottom-right) | INFO |
| 4 | Color usage intentional and accessible (no gratuitous color, no red/green only) | WARNING |
| 5 | Font family, size, and formatting consistent throughout | WARNING |
| 6 | Visual count reasonable (≤ 8 per page recommended) | WARNING (9-12) / FAIL (>12) |
| 7 | No empty visuals (all visuals have field bindings in queryState) | FAIL |
| 8 | Theme applied (not default Power BI theme) | WARNING |
| 9 | Default sort configured on visuals with categorical data | WARNING |
| 10 | Visual titles/labels in Selection pane are descriptive (not generic IDs) | INFO |
| 11 | Slicer count ≤ 3 per page (rest in filter pane) | WARNING |
| 12 | No visual-level filters hidden from users without documentation | WARNING |

## Chart Type Anti-Patterns

| Anti-Pattern | Problem | Better Alternative |
|---|---|---|
| Pie chart with > 5 slices | Hard to compare categories | Bar chart or treemap |
| Dual-axis chart | Misleading when scales differ | Small multiples or separate visuals |
| Gauge for single value | Takes up space, shows one value poorly | Card with trend or KPI |
| Too many custom visuals (SVG/Deneb/R/Python) | Maintenance burden, fragile | Use native visuals where possible |
| Default interactions left unchanged | Cross-filtering may confuse users | Review and set explicit interactions |

## Visual Complexity Analysis (Performance)

Assess performance risk from PBIR structure without needing Service-side load time data.

### Complexity Indicators

| Indicator | How to Check (from PBIR) | Impact |
|---|---|---|
| Visual count per page | Count `visual.json` files per page directory | Each visual = separate DAX query |
| Field count per visual | Count projections in `visual.query.queryState` | More fields = wider query |
| Grouping column count | Count `Column` projections in Category/Rows/Series roles | Multiplies cardinality exponentially |
| Extension measures | Check `reportExtensions.json` for measure count | Complex DAX evaluates per data point |
| Conditional formatting | Check `visual.objects` for `FillRule`, `Conditional`, measure-driven fill | Adds hidden query columns |
| Tooltip pages | Check for pages with `type: "Tooltip"` | Extra queries on hover |
| Cross-filtering scope | Check `drillFilterOtherVisuals` in visual config | Cascading re-queries on interaction |

### DAX Query Inference

Each visual's field bindings map to a `SUMMARIZECOLUMNS` query:

```
SUMMARIZECOLUMNS(
    <Column projections from Category/Rows/Series roles>,
    "Alias1", <Measure from Y/Values roles>,
    "Alias2", <Measure from Y/Values roles>
)
```

Hidden overhead sources:
- **Conditional formatting measures**: Add extra query columns per data point
- **Sort-by-column**: Model-level `sortByColumn` adds hidden columns to query
- **Custom tooltips**: Bind additional measures not in main visual
- **Data labels**: Dynamic format measures add evaluations

### Performance Risk Matrix

| Risk Level | Indicators | Action |
|---|---|---|
| **Low** | ≤ 6 visuals, ≤ 2 grouping columns, no CF | No action needed |
| **Medium** | 7-10 visuals, or 3+ grouping columns, or moderate CF | Flag for review |
| **High** | > 10 visuals, or 4+ grouping columns in one visual, or heavy CF + extension measures | Recommend simplification |

## Accessibility Checklist

| # | Check | Severity |
|---|---|---|
| 1 | Color contrast meets WCAG 2.1 AA (4.5:1 text, 3:1 UI) | WARNING |
| 2 | No reliance on color alone to convey meaning (pair with icon/text) | WARNING |
| 3 | Font sizes legible (min 9pt data, 12pt labels) | WARNING |
| 4 | Tab order / visual layer order established | INFO |
| 5 | No unnecessary animations or shadows | INFO |
| 6 | Alt text present on data visuals (when applicable) | INFO |

## Data Model Binding Quality

| # | Check | Severity |
|---|---|---|
| 1 | Report uses thin-report pattern (connects to published model, not embedded) | INFO |
| 2 | Extension measures used sparingly and only for report-specific logic | WARNING |
| 3 | No broken or orphaned field references | FAIL |
| 4 | Appropriate use of measures vs columns (aggregation context) | WARNING |
| 5 | No visual-level filters active without documentation | WARNING |

## Theme Validation

When the report uses a custom theme, validate it against the theme validation checklist:
- **Load** `.github/skills/theme-customization/references/theme-validation-checklist.md`
- Apply structural, color, typography, wildcard, and visual-type override checks
- Report findings with PASS/WARNING/FAIL per checklist item

## Review Output Format

```markdown
## Report Design Review — <ProjectName>

### Summary
- Design score: X/12 checks passed
- Complexity risk: Low / Medium / High
- Accessibility: X/6 checks passed

### Findings
| # | Category | Check | Status | Details |
|---|----------|-------|--------|---------|
| 1 | Design | Page titles | ✅ PASS | All pages have titles |
| 2 | Design | Visual count | ⚠️ WARNING | Page2 has 10 visuals |
| ... | ... | ... | ... | ... |

### Recommendations
1. <Prioritized recommendation>
2. <Prioritized recommendation>
```
