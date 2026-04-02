# Layout Guidelines

Detailed specifications for Power BI report page layouts.

## Page Dimensions

### Standard Page (16:9)

```
Width:  1280px
Height: 720px
```

### Alternative Sizes

| Type | Width | Height | Use Case |
|------|-------|--------|----------|
| Standard | 1280 | 720 | Desktop (PBI default) |
| Full HD | 1920 | 1080 | High-resolution displays, presentations |
| Letter | 816 | 1056 | Print, portrait |
| 4:3 | 1280 | 960 | Legacy displays |
| Custom | Variable | Variable | Specific requirements |

## Margins and Spacing

### Page Margins

```
Top:    24-32px
Bottom: 24-32px
Left:   24-32px
Right:  24-32px
```

### Visual Spacing

```
Minimum gap between visuals: 16px
Recommended gap: 24px
```

### Grid System

Use 8px or 16px grid for consistent alignment:

```
Positions: 0, 16, 32, 48, 64, 80...
Sizes: 200, 300, 400, 500...
```

## Visual Zones (Detail Gradient)

```
+------------------+------------------+
|       ZONE 1     |      ZONE 1      |  y: 24 - 200
|   KPIs / Cards   |   KPIs / Cards   |  (Important, summary)
+------------------+------------------+
|                                     |
|              ZONE 2                 |  y: 216 - 600
|        Charts / Analysis            |  (Context, trends)
|                                     |
+------------------+------------------+
|                                     |
|              ZONE 3                 |  y: 616 - 1056
|        Tables / Details             |  (Drill-down, detail)
|                                     |
+------------------+------------------+
```

### Zone Specifications

| Zone | Purpose | Height | Visual Types |
|------|---------|--------|--------------|
| 1 | Summary | 150-200px | Cards, KPIs, Slicers |
| 2 | Analysis | 350-450px | Charts, Maps, Gauges |
| 3 | Detail | 350-450px | Tables, Matrix, Lists |

## Common Visual Sizes

### Cards/KPIs

```
Width:  200-300px
Height: 100-150px
```

### Charts

```
Small:  Width: 400px,  Height: 300px
Medium: Width: 600px,  Height: 400px
Large:  Width: 900px,  Height: 500px
Full:   Width: 1872px, Height: 500px
```

### Tables

```
Width:  Variable (fill available space)
Height: 300-500px
```

### Slicers

```
Horizontal: Width: 200-400px, Height: 60-80px
Vertical:   Width: 150-200px, Height: 200-400px
```

## Title Area

### Page Title

```
Position: x: 24, y: 24
Width:    400-600px
Height:   48-64px
Font:     24pt bold
```

### Subtitle (Optional)

```
Position: x: 24, y: 72
Width:    400-600px
Height:   32-48px
Font:     14pt regular
```

## Sample Layouts

### Dashboard Layout

```
+--------------------------------------------------+
|  Title                            [Slicer]       |  y: 24
+--------+--------+--------+--------+--------------+
|  KPI   |  KPI   |  KPI   |  KPI   |              |  y: 96
+--------+--------+--------+--------+              +
|                         |                        |
|     Line Chart          |     Bar Chart          |  y: 232
|                         |                        |
+-------------------------+------------------------+
|                                                  |
|                    Table                         |  y: 616
|                                                  |
+--------------------------------------------------+
```

### Analysis Layout

```
+--------------------------------------------------+
|  Title                                           |  y: 24
+-------------------------+------------------------+
|                         |  Slicer                |  y: 96
|                         +------------------------+
|     Main Chart          |  Supporting Chart 1    |  y: 180
|                         +------------------------+
|                         |  Supporting Chart 2    |  y: 440
+-------------------------+------------------------+
|  Detail Table or Additional Analysis             |  y: 700
+--------------------------------------------------+
```

### KPI Dashboard

```
+--------------------------------------------------+
|  Title                            [Date Slicer]  |  y: 24
+--------+--------+--------+--------+--------------+
| Big    | Big    | Big    | Big    |              |  y: 96
| KPI    | KPI    | KPI    | KPI    |              |
+--------+--------+--------+--------+--------------+
|                                                  |
|           Trend Chart (Sparklines)               |  y: 280
|                                                  |
+--------------------------------------------------+
|                                                  |
|           Comparison Table                       |  y: 540
|                                                  |
+--------------------------------------------------+
```

## Positioning Rules

### Alignment

1. **Vertical alignment**: Left edges of visuals in same column must align
2. **Horizontal alignment**: Top edges of visuals in same row must align
3. **Consistent spacing**: Equal gaps between all visuals

### Symmetrical Spacing (Critical)

All gaps between visuals must be equal. Uneven spacing creates visual tension and signals misalignment.

When calculating positions for a row of N visuals:
```
visual_width = (available_width - (N-1) * gap) / N
x[i] = margin_left + i * (visual_width + gap)
```
