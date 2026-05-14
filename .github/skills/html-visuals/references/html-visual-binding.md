# HTML Custom Visual Binding Reference

## Visual Type GUID

The Power BI HTML custom visual uses the following `visualType`:

```
htmlContent443BE3AD55E043BF878BED274D3A6855
```

This GUID must be used exactly as-is in `visual-containers/*.json` files.

## Measure Requirements

Any DAX measure used as input for an HTML visual must declare:

```tmdl
		dataCategory: ImageUrl
```

(2-tab indent inside the measure block in TMDL)

The measure must return a complete HTML string starting with `<style>` or a full SVG markup.
Do NOT use the `data:image/svg+xml;utf8,` prefix — that is for the `svg-visuals` skill (inline
table/matrix visuals). The HTML custom visual renders the raw HTML/SVG string directly.

## PBIR visual-container JSON Structure

Minimal `visual-containers/<id>.json` for an HTML custom visual:

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/1.0.0/schema.json",
  "name": "<visual-id>",
  "position": {
    "x": 0,
    "y": 0,
    "z": 0,
    "width": 540,
    "height": 300,
    "tabOrder": 0
  },
  "visual": {
    "visualType": "htmlContent443BE3AD55E043BF878BED274D3A6855",
    "query": {
      "queryState": {
        "Values": {
          "projections": [
            {
              "field": {
                "Measure": {
                  "Expression": {
                    "SourceRef": {
                      "Entity": "<TableName>"
                    }
                  },
                  "Property": "<MeasureName>"
                }
              },
              "queryRef": "Values.0",
              "active": true
            }
          ]
        }
      }
    },
    "visualContainerObjects": {
      "general": [
        {
          "properties": {
            "responsive": { "expr": { "Literal": { "Value": "false" } } }
          }
        }
      ]
    }
  }
}
```

### Key fields

| Field | Value | Notes |
|---|---|---|
| `visualType` | `htmlContent443BE3AD55E043BF878BED274D3A6855` | Exact GUID — never shorten or modify |
| `Entity` | Table name containing the measure | Read from TMDL, do not invent |
| `Property` | Measure name | Exact name as declared in TMDL |
| `responsive` | `false` | Prevents Power BI from resizing the iframe content |

### Extension Measures (reportExtensions)

If the measure is declared in `reportExtensions.json` rather than in the semantic model TMDL,
use `"Schema": "extension"` in the SourceRef:

```json
{
  "SourceRef": {
    "Schema": "extension",
    "Entity": "<TableName>"
  }
}
```

## dataCategory in TMDL — Correct Syntax

```
	measure 'My HTML Measure' =
			VAR x = 1
			RETURN "<div>" & x & "</div>"
		lineageTag: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
		dataCategory: ImageUrl
```

Property order inside a measure block:
1. `lineageTag`
2. `dataCategory`
3. `formatString` (if present)
4. `displayFolder` (if present)

## Common Wiring Mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| Wrong visualType | Blank visual or "visual not available" error | Use exact GUID `htmlContent443BE3AD55E043BF878BED274D3A6855` |
| Missing `dataCategory: ImageUrl` | HTML displayed as raw text string | Add `dataCategory: ImageUrl` at 2-tab indent |
| `data:image/svg+xml` prefix in return | Visual shows broken image | Remove prefix — HTML visual does not need it |
| `responsive: true` | Visual rescales and breaks layout | Set `responsive` to `false` |
| BOM in TMDL file | Report fails to open, parse error on measure | Save without BOM (see `tmdl-authoring-rules.md`) |
