# SVG Patterns for Table and Matrix Visuals

Table (`tableEx`) and Matrix (`pivotTable`) visuals are the primary target for DAX SVG measures. Configure `grid.imageHeight` and `grid.imageWidth` in visual objects to control rendering size (default: 25px height, 100px width).

## Setup

### Image Size Configuration

Set in the visual's `objects.grid`:

```json
"grid": [{
  "properties": {
    "imageHeight": {"expr": {"Literal": {"Value": "25D"}}},
    "imageWidth": {"expr": {"Literal": {"Value": "100D"}}}
  }
}]
```

### Sort Trick

Embed a `<desc>` tag to enable sorting the SVG column by bar length:

```dax
VAR _Sort = "<desc>" & FORMAT(_Actual, "000000000000") & "</desc>"
```

Power BI uses the `<desc>` content as the sort key for the image column.

### Axis Normalization (Required for All Bar-Based Charts)

All bar, bullet, and dumbbell charts need a shared axis maximum so bars are comparable across rows:

```dax
VAR _BarMax = 100          -- max pixel width of the bar area
VAR _BarMin = 20           -- left offset (space for labels/dots)
VAR _Scope = ALLSELECTED('Table'[GroupColumn])

VAR _MaxActual = CALCULATE(
    MAXX(_Scope, [Actual]),
    REMOVEFILTERS('Table'[GroupColumn])
)
VAR _MaxTarget = CALCULATE(
    MAXX(_Scope, [Target]),
    REMOVEFILTERS('Table'[GroupColumn])
)

VAR _AxisMax =
    IF(
        HASONEVALUE('Table'[GroupColumn]),
        MAX(_MaxActual, _MaxTarget),
        CALCULATE(MAX([Actual], [Target]), REMOVEFILTERS('Table'[GroupColumn]))
    ) * 1.1   -- 10% headroom

VAR _AxisRange = _BarMax - _BarMin
VAR _ActualNormalized = DIVIDE(_Actual, _AxisMax) * _AxisRange
VAR _TargetNormalized = (DIVIDE(_Target, _AxisMax) * _AxisRange) + _BarMin - 1
```

Key points:
- `REMOVEFILTERS` on the group column ensures `_AxisMax` is consistent across all rows
- Multiply by 1.1 for headroom so bars never hit the edge
- Target position = normalized value + left offset

### Number Formatting (Adaptive Scale)

```dax
VAR _Label = SWITCH(TRUE(),
    _Actual <= 1E3,  FORMAT(_Actual, "#,0"),
    _Actual <= 1E6,  FORMAT(_Actual, "#,0, K"),
    _Actual <= 1E9,  FORMAT(_Actual, "#,0,, M"),
    FORMAT(_Actual, "#,0,,, B")
)
```

---

## Pattern: Data Bar

Simple proportional bar for table columns. The most basic SVG pattern.

```dax
Data Bar =
VAR _Value = [Sales Amount]
VAR _Max = CALCULATE(MAX([Sales Amount]), REMOVEFILTERS('Product'[Category]))
VAR _Pct = DIVIDE(_Value, _Max)
VAR _W = _Pct * 100
VAR _Color = "#5B8DBE"

RETURN
"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 16'>" &
"<rect width='" & _W & "' height='16' fill='" & _Color & "' opacity='0.7' rx='2'/>" &
"<text x='" & (_W + 3) & "' y='12' font-size='10' fill='#333'>" &
FORMAT(_Value, "#,0") & "</text></svg>"
```

**Variants:**
- Rounded corners: add `rx='4'` to the rect
- Conditional color: `VAR _Color = IF(_Value > _Threshold, "#4CAF50", "#F44336")`
