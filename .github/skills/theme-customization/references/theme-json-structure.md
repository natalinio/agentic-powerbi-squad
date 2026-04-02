# Theme JSON Structure Reference

Complete reference for Power BI report theme JSON structure.

## Top-Level Keys

| Key | Type | Purpose |
|---|---|---|
| `name` | string | Display name shown in Power BI UI |
| `dataColors` | string[] | Ordered hex palette for data series (6-12 recommended) |
| `good` | string | Hex for CF sentiment "good" (flat root-level key) |
| `bad` | string | Hex for CF sentiment "bad" (flat root-level key) |
| `neutral` | string | Hex for CF sentiment "neutral" (flat root-level key) |
| `maximum` | string | Gradient extreme — maximum |
| `center` | string | Gradient extreme — center |
| `minimum` | string | Gradient extreme — minimum |
| `foreground` | string | Primary text color |
| `foregroundLight` | string | Secondary/muted text |
| `foregroundDark` | string | Emphasis text |
| `foregroundNeutralSecondary` | string | Tertiary text |
| `background` | string | Canvas background |
| `backgroundLight` | string | Light surface |
| `backgroundNeutral` | string | Neutral surface |
| `backgroundDark` | string | Darker surface |
| `tableAccent` | string | Table/matrix accent color |
| `hyperlink` | string | Link color |
| `textClasses` | object | Typography per semantic role |
| `visualStyles` | object | `[visualType][state]` formatting cascade |

## Color System

### Data Colors

```json
"dataColors": ["#1971c2", "#f08c00", "#2f9e44", "#ae3ec9", "#e03131", "#0c8599"]
```

Rules:
- First color (`dataColors[0]`) is the "primary" — appears most frequently
- 6-12 colors recommended; < 6 may repeat too soon, > 12 is hard to distinguish
- Muted/desaturated tones preferred over saturated
- Must be distinguishable for colorblind users (avoid red/green pairs)

### Semantic Colors (Root-Level)

```json
"good": "#2f9e44",
"bad": "#e03131",
"neutral": "#868e96"
```

**Critical**: These are flat root-level keys, NOT nested under a `sentimentColors` object. CF measures returning `"good"` will resolve to this hex value.

### Gradient Colors

```json
"maximum": "#1971c2",
"center": "#f8f9fa",
"minimum": "#e03131"
```

Used by gradient conditional formatting (`FillRule` with `linearGradient2/3`).

### Background/Foreground

```json
"foreground": "#343a40",
"foregroundLight": "#868e96",
"foregroundDark": "#212529",
"foregroundNeutralSecondary": "#adb5bd",
"background": "#ffffff",
"backgroundLight": "#f8f9fa",
"backgroundNeutral": "#e9ecef",
"backgroundDark": "#dee2e6"
```

### ThemeDataColor References

In `visualStyles`, reference palette colors by index instead of hardcoding hex:

```json
"fontColor": {"solid": {"color": {"ThemeDataColor": {"ColorId": 0, "Percent": 0}}}}
```

- `ColorId`: 0-based index into `dataColors` array
- `Percent`: Lightness adjustment (-1.0 to 1.0; 0 = original, negative = darker, positive = lighter)

## Typography (`textClasses`)

```json
"textClasses": {
  "callout": { "fontSize": 32, "fontFace": "Segoe UI", "color": "#343a40" },
  "title":   { "fontSize": 14, "fontFace": "Segoe UI Semibold", "color": "#343a40" },
  "header":  { "fontSize": 12, "fontFace": "Segoe UI Semibold", "color": "#343a40" },
  "label":   { "fontSize": 11, "fontFace": "Segoe UI", "color": "#495057" },
  "dataTitle": { "fontSize": 12, "fontFace": "Segoe UI", "color": "#868e96" }
}
```

### textClasses Format Rules

- Uses `fontFace` (not `fontFamily`)
- Uses plain hex string for `color` (e.g., `"color": "#343a40"`)
- Does **NOT** use the `{"solid": {"color": "..."}}` wrapper — that format is for `visualStyles` only
- Mixing the wrong format causes silently ignored colors

### Standard Roles

| Role | Use | Recommended Size |
|---|---|---|
| `callout` | KPI values, big numbers | 28-36pt |
| `title` | Visual titles | 14-16pt |
| `header` | Section headers, column headers | 12-14pt |
| `label` | Axis labels, data labels | 11-12pt |
| `dataTitle` | KPI subtitles | 12pt |
| `boldLabel` | Emphasized labels | 12pt |

### Supported Fonts

Segoe UI, Segoe UI Semibold, Segoe UI Light, Segoe UI Bold, Arial, Calibri, Candara, Consolas, Courier New, DIN, DIN Light, Georgia, Tahoma, Times New Roman, Trebuchet MS, Verdana.

## Visual Styles (`visualStyles`)

### Structure

```json
"visualStyles": {
  "*": {
    "*": { /* wildcard — applies to ALL visuals */ }
  },
  "lineChart": {
    "*": { /* overrides wildcard for lineChart */ }
  },
  "textbox": {
    "*": { /* overrides wildcard for textbox */ }
  }
}
```

### Property Format in visualStyles

All container values use array wrapper and object color format:

```json
"title": [{
  "show": true,
  "fontSize": 14,
  "fontFamily": "Segoe UI Semibold",
  "fontColor": {"solid": {"color": "#343a40"}}
}]
```

### Minimum Viable Wildcard

```json
"*": {
  "*": {
    "title": [{"show": true, "fontSize": 14, "fontFamily": "Segoe UI Semibold", "fontColor": {"solid": {"color": "#343a40"}}}],
    "background": [{"show": false}],
    "border": [{"show": false}],
    "dropShadow": [{"show": false}],
    "padding": [{"top": 8, "bottom": 8, "left": 8, "right": 8}]
  }
}
```

### Design Guidelines

- `dropShadow.show: false` globally — shadows create visual noise and accessibility issues
- `background.show: false` by default — clean canvas; individual visuals opt in
- `border.show: false` by default — use spacing instead of borders
- `title.show: true` by default — visuals should have labels; suppress per type as needed
