# Visual-Type Override Patterns

Override patterns for `visualStyles["<type>"]["*"]` in theme JSON. Add type-specific overrides when a visual type needs different defaults than the wildcard.

## Priority Types (Always Override)

### textbox

Suppress all container chrome — text has its own formatting.

```json
"textbox": {
  "*": {
    "title": [{"show": false}],
    "background": [{"show": false}],
    "border": [{"show": false}],
    "dropShadow": [{"show": false}],
    "padding": [{"top": 0, "bottom": 0, "left": 0, "right": 0}]
  }
}
```

### image

Images rarely need container formatting.

```json
"image": {
  "*": {
    "title": [{"show": false}],
    "background": [{"show": false}],
    "border": [{"show": false}],
    "dropShadow": [{"show": false}]
  }
}
```

### shape

Geometric shapes — no container chrome.

```json
"shape": {
  "*": {
    "title": [{"show": false}],
    "background": [{"show": false}],
    "border": [{"show": false}],
    "dropShadow": [{"show": false}]
  }
}
```

### actionButton

Buttons have their own state system (default/hover/active/disabled). Suppress container.

```json
"actionButton": {
  "*": {
    "title": [{"show": false}],
    "background": [{"show": false}],
    "border": [{"show": false}],
    "dropShadow": [{"show": false}]
  }
}
```

## Common Types (Override When Needed)

### cardVisual (New Card)

```json
"cardVisual": {
  "*": {
    "value": [{
      "fontFamily": "Segoe UI Semibold",
      "fontSize": 28,
      "horizontalAlignment": "center",
      "labelDisplayUnits": 0
    }],
    "label": [{
      "show": true,
      "fontFamily": "Segoe UI",
      "fontSize": 11,
      "position": "belowValue"
    }],
    "title": [{"show": false}],
    "background": [{"show": false}],
    "border": [{"show": false}],
    "dropShadow": [{"show": false}]
  }
}
```

Notes:
- Uses `fontColor` (not `color`) for value and label
- `label.position`: `"belowValue"` or `"aboveValue"`

### lineChart

```json
"lineChart": {
  "*": {
    "categoryAxis": [{
      "show": true,
      "fontSize": 11,
      "fontFamily": "Segoe UI",
      "gridlineShow": false
    }],
    "valueAxis": [{
      "show": true,
      "fontSize": 11,
      "fontFamily": "Segoe UI",
      "gridlineColor": {"solid": {"color": "#E0E0E0"}},
      "gridlineThickness": 1
    }],
    "legend": [{
      "show": true,
      "position": "Bottom",
      "fontSize": 11,
      "fontFamily": "Segoe UI"
    }],
    "labels": [{"show": false}],
    "lineStyles": [{
      "strokeWidth": 2,
      "lineChartType": "linear",
      "showMarker": false
    }]
  }
}
```

Notes:
- `gridlineColor`, `labelColor` use `{"solid": {"color": "#hex"}}` format
- `lineChartType`: `"linear"`, `"smooth"`, `"step"`
- `legend.position`: `"Top"`, `"Bottom"`, `"Left"`, `"Right"`, `"TopCenter"`, `"BottomCenter"`, etc.

### tableEx (Table)

```json
"tableEx": {
  "*": {
    "columnHeaders": [{
      "backColor": {"solid": {"color": "#252423"}},
      "fontColor": {"solid": {"color": "#FFFFFF"}},
      "fontSize": 11,
      "fontFamily": "Segoe UI Semibold"
    }],
    "values": [{
      "backColorPrimary": {"solid": {"color": "#FFFFFF"}},
      "backColorSecondary": {"solid": {"color": "#F3F2F1"}},
      "fontColorPrimary": {"solid": {"color": "#252423"}},
      "fontSize": 11,
      "fontFamily": "Segoe UI"
    }],
    "total": [{
      "backColor": {"solid": {"color": "#E1DFDD"}},
      "fontColor": {"solid": {"color": "#252423"}},
      "fontSize": 11,
      "fontFamily": "Segoe UI Semibold",
      "totals": true
    }],
    "grid": [{
      "gridHorizontal": true,
      "gridHorizontalColor": {"solid": {"color": "#E1DFDD"}},
      "gridHorizontalWeight": 1,
      "gridVertical": false
    }]
  }
}
```

Notes:
- `backColor` (not `backgroundColor`) for headers/totals
- `backColorPrimary`/`backColorSecondary` for alternating row banding
- `outlineStyle`: `0` (none), `1` (bottom only), `2` (all sides)

### pivotTable (Matrix)

Same structure as `tableEx` with additional containers:
- `rowHeaders` — row header formatting
- `columnHeaders` — column header formatting
- `subTotals` — subtotal row/column formatting

### slicer (Legacy)

```json
"slicer": {
  "*": {
    "items": [{
      "textSize": 11,
      "fontFamily": "Segoe UI",
      "fontColor": {"solid": {"color": "#252423"}}
    }],
    "header": [{
      "show": true,
      "textSize": 12,
      "fontFamily": "Segoe UI Semibold"
    }]
  }
}
```

Note: Uses `textSize` (not `fontSize`) — legacy convention.

### advancedSlicerVisual (New Slicer)

Same container structure as `cardVisual` — uses `label`/`value` containers.

### kpi

```json
"kpi": {
  "*": {
    "indicator": [{"fontSize": 36}],
    "trendline": [{"show": true}],
    "goals": [{"show": true, "fontSize": 11}]
  }
}
```

Note: Container name is `trendline` (lowercase), NOT `trendLine`.

## Visual Type Quick Reference

| Family | Types | Shared Containers |
|---|---|---|
| Bar/Column | `barChart`, `columnChart`, `clusteredBarChart`, `clusteredColumnChart`, `hundredPercentStackedBarChart`, `hundredPercentStackedColumnChart` | `categoryAxis`, `valueAxis`, `legend`, `labels`, `dataPoint` |
| Line/Area | `lineChart`, `areaChart`, `stackedAreaChart`, `hundredPercentStackedAreaChart` | `categoryAxis`, `valueAxis`, `legend`, `labels`, `lineStyles`, `markers` |
| Combo | `lineClusteredColumnComboChart`, `lineStackedColumnComboChart` | Combined line + bar containers |
| Pie/Donut | `pieChart`, `donutChart` | `labels`, `legend`, `slices` |
| Table | `tableEx`, `pivotTable` | `columnHeaders`, `values`, `total`, `grid` |
| Card | `card` (legacy), `cardVisual` (new) | `labels`/`value`, `label` |
| Slicer | `slicer`, `advancedSlicerVisual`, `listSlicer` | `items`/`header` or `label`/`value` |
| Decorative | `textbox`, `image`, `shape`, `actionButton` | Container chrome only |
