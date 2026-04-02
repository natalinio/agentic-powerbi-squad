# Deneb Capabilities and Template Format

## Visual Capabilities

### Data Roles

Single data role — all columns and measures go into one "Values" well:

```json
{
  "dataRoles": [{"displayName": "Values", "name": "dataset", "kind": "GroupingOrMeasure"}],
  "dataViewMappings": [{
    "categorical": {
      "categories": {"select": [{"bind": {"to": "dataset"}}], "dataReductionAlgorithm": {"window": {"count": 10000}}},
      "values": {"select": [{"bind": {"to": "dataset"}}]}
    }
  }]
}
```

### Object Properties Reference

#### `vega` object (core)

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `jsonSpec` | text | — | Vega/Vega-Lite specification JSON |
| `jsonConfig` | text | — | Vega/Vega-Lite config JSON |
| `provider` | `vegaLite` / `vega` | `vegaLite` | Language provider |
| `version` | text | — | Provider version string |
| `logLevel` | 0-4 | 3 | none/error/warn/info/debug |
| `renderMode` | `svg` / `canvas` | `svg` | Rendering engine |
| `enableTooltips` | bool | true | Power BI tooltips |
| `enableContextMenu` | bool | true | Right-click context menu |
| `enableHighlight` | bool | false | Cross-highlighting |
| `enableSelection` | bool | false | Cross-filtering |
| `selectionMode` | `simple` / `advanced` | `simple` | Selection management |
| `selectionMaxDataPoints` | 1-250 | 50 | Max selectable points |
| `tooltipDelay` | numeric | — | Tooltip display delay (ms) |

#### `editor` object

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `theme` | `dark` / `light` | `light` | Editor color theme |
| `fontSize` | fontSize | 8 | Editor font size |
| `wordWrap` | bool | true | Enable word wrap |
| `position` | `left` / `right` | — | Editor pane position |

#### `display` object

| Property | Type | Description |
|----------|------|-------------|
| `scrollbarColor` | solid color | Scrollbar fill color |
| `scrollbarOpacity` | integer | Scrollbar opacity |
| `scrollbarRadius` | integer | Scrollbar border radius |

#### `dataLimit` object

| Property | Type | Description |
|----------|------|-------------|
| `override` | bool | Override default 10K row limit |
| `showCustomVisualNotes` | bool | Show custom visual notes |

## Template Format (v1)

Templates are valid Vega/Vega-Lite JSON files with a `usermeta` object. Schema: `https://deneb.guide/schema/deneb-template-usermeta-v1.json`

### Structure

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "usermeta": {
    "deneb": {
      "build": "1.9.0.0",
      "metaVersion": 1,
      "provider": "vegaLite",
      "providerVersion": "6.4.1"
    },
    "information": {
      "name": "Chart Name",
      "description": "Description",
      "author": "Author Name",
      "uuid": "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx",
      "generated": "2024-01-01T00:00:00.000Z"
    },
    "dataset": [
      {"key": "__category__", "name": "Category", "kind": "column", "type": "text"},
      {"key": "__measure__", "name": "Measure", "kind": "measure", "type": "numeric"}
    ],
    "interactivity": {
      "tooltip": true,
      "contextMenu": true,
      "selection": false,
      "highlight": false,
      "dataPointLimit": 50
    }
  },
  "data": {"name": "dataset"},
  "mark": "bar",
  "encoding": {
    "x": {"field": "__category__", "type": "nominal"},
    "y": {"field": "__measure__", "type": "quantitative"}
  }
}
```

### How to Use a Community Template in PBIR

1. Strip `usermeta` from the JSON
2. Replace placeholder keys (`__0__`, `__1__`) with actual field display names from your model (matching `nativeQueryRef`)
3. Stringify the spec and wrap in single quotes for `jsonSpec` literal value
4. Extract `config` separately for `jsonConfig`
