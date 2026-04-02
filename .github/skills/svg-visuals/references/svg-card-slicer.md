# SVG Patterns for Card and Slicer Visuals

Card (`cardVisual`) and Slicer (`advancedSlicerVisual`) visuals support SVG measures through specific binding patterns. The classic card does NOT support SVG — only the new card visual works.

## Card Visual (cardVisual)

### Binding

Card visuals render SVG via `callout.imageFX`. Bind the SVG measure to the card's `calloutValue` field, then configure `imageFX`:

```json
{
  "objects": {
    "callout": [{
      "properties": {
        "imageFX": {"expr": {"Literal": {"Value": "true"}}},
        "imageHeight": {"expr": {"Literal": {"Value": "40D"}}},
        "imageWidth": {"expr": {"Literal": {"Value": "100D"}}}
      }
    }]
  }
}
```

### Pattern: Arrow Indicator

Compact directional indicator for KPI cards.

```dax
Arrow Indicator =
VAR _Growth = [Growth %]
VAR _Up = _Growth >= 0
VAR _Path = IF(_Up, "M 10,15 L 5,10 L 15,10 Z", "M 10,5 L 5,10 L 15,10 Z")
VAR _Color = IF(_Up, "#4CAF50", "#F44336")

RETURN
"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20'>" &
"<path d='" & _Path & "' fill='" & _Color & "'/></svg>"
```

### Pattern: Mini Gauge

Semi-circular gauge for progress or performance.

```dax
Mini Gauge =
VAR _Pct = DIVIDE([Value], [Target], 0)
VAR _Angle = (_Pct * 180) - 90
VAR _R = 40
VAR _CX = 50
VAR _CY = 50
VAR _Rad = _Angle * PI() / 180
VAR _NX = _CX + (_R * 0.8 * COS(_Rad))
VAR _NY = _CY + (_R * 0.8 * SIN(_Rad))

RETURN
"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 60'>" &
"<path d='M 10 50 A 40 40 0 0 1 90 50' fill='none' stroke='#E0E0E0' stroke-width='8'/>" &
"<line x1='" & _CX & "' y1='" & _CY & "' x2='" & _NX & "' y2='" & _NY & "' stroke='#333' stroke-width='2'/>" &
"<circle cx='" & _CX & "' cy='" & _CY & "' r='3' fill='#333'/></svg>"
```

### Pattern: Mini Donut

Percentage completion as a donut ring.

```dax
Mini Donut =
VAR _Pct = [Percentage]
VAR _Angle = _Pct * 360
VAR _LargeArc = IF(_Angle > 180, 1, 0)
VAR _R = 40
VAR _CX = 50
VAR _CY = 50
VAR _Rad = (_Angle - 90) * PI() / 180
VAR _EndX = _CX + (_R * COS(_Rad))
VAR _EndY = _CY + (_R * SIN(_Rad))

RETURN
"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'>" &
"<circle cx='" & _CX & "' cy='" & _CY & "' r='" & _R & "' fill='none' stroke='#E0E0E0' stroke-width='8'/>" &
"<path d='M " & _CX & " " & (_CY - _R) & " A " & _R & " " & _R & " 0 " & _LargeArc & " 1 " & _EndX & " " & _EndY & "' fill='none' stroke='#2196F3' stroke-width='8'/></svg>"
```

### Pattern: Progress Bar

Horizontal bar with label, sized for card visuals.

```dax
Progress Bar =
VAR _Pct = [Completion %]
VAR _W = 100
VAR _H = 20
VAR _FillW = _Pct * _W
VAR _Label = FORMAT(_Pct, "0%")
VAR _Color = SWITCH(TRUE(), _Pct < 0.5, "#F44336", _Pct < 0.8, "#FF9800", "#4CAF50")

RETURN
"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 " & _W & " " & _H & "'>" &
"<rect width='" & _W & "' height='" & _H & "' fill='#E0E0E0' rx='" & (_H / 2) & "'/>" &
"<rect width='" & _FillW & "' height='" & _H & "' fill='" & _Color & "' rx='" & (_H / 2) & "'/>" &
"<text x='" & (_W / 2) & "' y='" & (_H / 2 + 5) & "' font-size='11' text-anchor='middle' fill='white' font-weight='bold'>" & _Label & "</text></svg>"
```

---

## Slicer Visual (advancedSlicerVisual)

Slicers can display SVG in header images and custom slicer items. This is less common but useful for branded slicer headers.

### Binding

Set SVG in slicer header via `header.image` in the visual's objects configuration.
