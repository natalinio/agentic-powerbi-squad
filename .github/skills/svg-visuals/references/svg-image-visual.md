# SVG Patterns for Image Visuals

Image visuals (`image` visual type) render SVG measures as standalone graphics on the report canvas. Unlike table/matrix SVGs (which are inline micro-charts in rows), image visuals occupy their own visual container and can be any size.

## Critical: sourceType Must Be 'imageData'

For `data:image/svg+xml;utf8,...` data URIs, the image visual **must** use `sourceType = 'imageData'`. Using `'imageUrl'` (which is for HTTP URLs) causes `VisualDataProxyExecutionUnknownError` and renders black.

## JSON Structure

The image visual uses `objects.image` with these properties:

```json
{
  "objects": {
    "image": [{
      "properties": {
        "sourceType": {"expr": {"Literal": {"Value": "'imageData'"}}},
        "transparency": {"expr": {"Literal": {"Value": "0D"}}},
        "sourceField": {
          "expr": {
            "Measure": {
              "Expression": {
                "SourceRef": {"Schema": "extension", "Entity": "TableName"}
              },
              "Property": "SVG Measure Name"
            }
          }
        },
        "effects": {"expr": {"Literal": {"Value": "false"}}}
      }
    }]
  }
}
```

Note: image visuals need no `query` block — only `objects.image` with `sourceType`, `sourceField`, and optionally `transparency`/`effects`.

---

## Pattern: KPI Header Card

A standalone SVG that shows a metric value, label, and trend indicator. Designed for image visuals.

```dax
KPI Header SVG =
VAR _Value = [Total Revenue]
VAR _PY = [Total Revenue PY]
VAR _Change = DIVIDE(_Value - _PY, _PY)
VAR _ChangeLabel = FORMAT(_Change, "+#,##0.0%;-#,##0.0%")
VAR _ValueLabel = FORMAT(_Value, "$#,##0,, M")
VAR _ChangeColor = IF(_Change >= 0, "#2D6A2E", "#982F2F")
VAR _Arrow = IF(_Change >= 0,
    "<polygon points='170,28 175,20 180,28' fill='" & _ChangeColor & "'/>",
    "<polygon points='170,20 175,28 180,20' fill='" & _ChangeColor & "'/>"
)

RETURN
"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 300 60'>" &
"<text x='10' y='20' font-family='Segoe UI' font-size='11' fill='#666' font-weight='600'>TOTAL REVENUE</text>" &
"<text x='10' y='48' font-family='Segoe UI' font-size='28' fill='#333' font-weight='700'>" & _ValueLabel & "</text>" &
_Arrow &
"<text x='185' y='28' font-family='Segoe UI' font-size='12' fill='" & _ChangeColor & "' font-weight='600'>" & _ChangeLabel & " vs PY</text>" &
"</svg>"
```

**Design notes:**
- Use a wide `viewBox` (e.g., 300x60) since image visuals are typically wider than table cells
- Include all text labels inside the SVG — no separate visual title needed
- Font sizes can be larger than table SVGs (28px value vs 10-12px in tables)
