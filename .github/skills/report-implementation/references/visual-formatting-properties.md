# Visual Formatting Properties Reference

Formatting hierarchy, universal containers, and property catalogue for PBIR visuals.

## Formatting Hierarchy

Power BI applies formatting in cascade: **base theme → custom theme → visual-type defaults → individual visual overrides**. Most formatting should come from the theme, not from individual visuals.

1. **Check** what the theme already provides (inspect theme.json `visualStyles`)
2. **Set in theme** if the formatting applies to all visuals of that type
3. **Override per-visual** only for genuinely one-off cases

## Universal Containers

Present on all/most visual types. Set in `visual.visualContainerObjects`:

### title

| Property | Type | Notes |
|---|---|---|
| `show` | boolean | Show/hide visual title |
| `text` | string | Title text |
| `fontSize` | number | 6-45 |
| `fontColor` | object | Color value |
| `fontFamily` | string | Font name |
| `bold` | boolean | |
| `italic` | boolean | |
| `alignment` | string | `left`, `center`, `right` |
| `heading` | string | `Normal`, `Heading2`..`Heading6` |

### subTitle

Same properties as `title`.

### background

| Property | Type | Notes |
|---|---|---|
| `show` | boolean | |
| `color` | object | Background color |
| `transparency` | number | 0-100 |

### border

| Property | Type | Notes |
|---|---|---|
| `show` | boolean | |
| `color` | object | Border color |
| `radius` | number | Corner radius |
| `width` | number | Border width |

### padding

| Property | Type | Notes |
|---|---|---|
| `top` | number | Pixels |
| `bottom` | number | |
| `left` | number | |
| `right` | number | |

### dropShadow

| Property | Type | Notes |
|---|---|---|
| `show` | boolean | **Avoid** — shadows hurt accessibility |
| `preset` | string | Shadow style preset |

### visualHeader

| Property | Type | Notes |
|---|---|---|
| `show` | boolean | Show visual header on hover |
| `showOptionsMenu` | boolean | Show ... menu |
| `showFilterRestatementButton` | boolean | |
| `showFocusModeButton` | boolean | |

### visualLink (Action Buttons)

| Property | Type | Notes |
|---|---|---|
| `show` | boolean | Enable action |
| `type` | string | `Back`, `Bookmark`, `Drillthrough`, `PageNavigation`, `WebUrl`, `QnA` |
| `bookmark` | string | Bookmark name (when type=Bookmark) |
| `navigationSection` | string | Page ID (when type=PageNavigation) |
| `webUrl` | string | URL (when type=WebUrl) |

## Type-Specific Container Index

Key visual types and their unique containers:

| Visual Type | Key Containers |
|---|---|
| `lineChart` | `categoryAxis`, `valueAxis`, `dataPoint`, `labels`, `lineStyles`, `markers`, `legend`, `forecast` |
| `clusteredBarChart` | `categoryAxis`, `valueAxis`, `dataPoint`, `labels`, `legend` |
| `clusteredColumnChart` | `categoryAxis`, `valueAxis`, `dataPoint`, `labels`, `legend` |
| `cardVisual` | `accentBar`, `value`, `label`, `image`, `fillCustom`, `grid`, `smallMultiplesLayout` |
| `card` | `categoryLabels`, `labels`, `wordWrap` |
| `kpi` | `goals`, `indicator`, `status`, `trendline`, `lastDate` |
| `tableEx` | `grid`, `columnHeaders`, `values`, `total`, `columnWidth`, `sparklines` |
| `pivotTable` | `grid`, `columnHeaders`, `rowHeaders`, `values`, `columnTotal`, `rowTotal`, `subTotals`, `columnWidth` |
| `advancedSlicerVisual` | `data`, `selection`, `label`, `value`, `layout`, `accentBar` |
| `donutChart` | `dataPoint`, `labels`, `legend`, `slices` |
| `scatterChart` | `categoryAxis`, `valueAxis`, `dataPoint`, `legend`, `markers`, `bubbles` |
| `textbox` | `general` (paragraphs) |
| `actionButton` | `fill`, `text`, `icon`, `outline`, `shape` |

## Literal Value Encoding

PBIR JSON encodes values in `Literal.Value` with type suffixes:

| Type | Format | Example |
|---|---|---|
| Boolean | bare | `"true"`, `"false"` |
| Number | `D` suffix | `"12D"`, `"0.5D"` |
| String | single quotes | `"'hello'"` |
| Long | `L` suffix | `"1000L"` |
| JSON (spec) | escaped string in single quotes | `'{...}'` |

## Visual Calculations

Visual calculations are DAX expressions embedded in individual visuals. They compute values relative to the visual's axes.

### When to Use

- Running totals along an axis: `RUNNINGSUM([Revenue])`
- Ranks within displayed rows: `RANK()`
- Period navigation: `PREVIOUS([Revenue])`, `NEXT([Revenue])`
- Moving averages: `MOVINGAVERAGE([Revenue], 3)`

### vs Extension Measures

| Aspect | Visual Calculations | Extension Measures |
|---|---|---|
| Scope | Single visual | Entire report |
| Location | Visual JSON | reportExtensions.json |
| DAX functions | Axis-aware (RUNNINGSUM, RANK, PREVIOUS) | Standard DAX only |
| Best for | Running totals, ranks, row navigation | Conditional formatting, conditional rendering |

**Promote to semantic model** when the calculation is reused across visuals.

## Bookmarks (Use Sparingly)

Bookmarks should be **avoided** unless a specific use-case justifies them:
- Fragile state capture — any report change can silently break bookmarks
- Hidden complexity — hard to track what state each bookmark captures
- Maintenance burden — every structural change requires re-testing all bookmarks
- **Better alternatives**: Page navigation, drillthrough, report-level filters

If bookmarks are required, each is stored as a JSON file in `definition/bookmarks/`:

```
definition/
  bookmarks/
    bookmarks.json              # Bookmark order and groups
    abc123.bookmark.json        # Individual bookmark state
```

A bookmark captures: filter/slicer state (data), visual visibility (display), active page. Each dimension can be toggled via `options.suppressData`, display settings, and `explorationState.activeSection`.
