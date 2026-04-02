# Visual Colors

Guidelines for effective color usage in Power BI reports.

## Color Principles

### Use Theme Colors

Prefer theme colors over hardcoded hex:

```json
// Good — uses theme color
"expr": {"ThemeDataColor": {"ColorId": 1, "Percent": 0}}

// Avoid in visuals — use only in extension measures
"expr": {"Literal": {"Value": "'#118DFF'"}}
```

### Semantic Colors

Use theme color names in extension measures:

| Color Name | Meaning | Typical Color |
|---|---|---|
| `"good"` | Positive, on-target | Green |
| `"bad"` | Negative, off-target | Red |
| `"neutral"` | Unchanged, baseline | Gray/Yellow |
| `"minColor"` | Gradient minimum | Red/Orange |
| `"midColor"` | Gradient midpoint | Yellow/White |
| `"maxColor"` | Gradient maximum | Green/Blue |

### Extension Measure Pattern

```dax
Color Measure =
IF([Value] >= [Target], "good",
IF([Value] >= [Target] * 0.9, "neutral", "bad"))
```

## Color Contrast (WCAG 2.1)

| Element | Minimum Ratio |
|---|---|
| Normal text | 4.5:1 |
| Large text (18pt+) | 3:1 |
| UI components | 3:1 |

### Common Contrast Issues

| Background | Text | Ratio | Status |
|---|---|---|---|
| White (#FFF) | Dark gray (#333) | 12.6:1 | Pass |
| White (#FFF) | Medium gray (#777) | 4.5:1 | Pass (barely) |
| White (#FFF) | Light gray (#AAA) | 2.9:1 | **Fail** |

## Color Categories

### Data Colors (dataColors)

Primary series colors in theme:

```json
"dataColors": [
  "#118DFF",  // Blue (primary)
  "#12239E",  // Dark blue
  "#E66C37",  // Orange
  "#6B007B",  // Purple
  "#E044A7",  // Pink
  "#744EC2"   // Violet
]
```

### Background Colors

- White: `#FFFFFF`
- Light gray: `#F5F5F5`, `#FAFAFA`
- Light blue: `#F0F8FF`, `#E3F2FD`

### Accent Colors

- Use sparingly
- Reserve bright colors for important data
- Don't use red/orange unless indicating problems

## Conditional Formatting Colors

### Best Practices

1. **Theme tokens over hex** — CF should use sentiment tokens (`"good"`, `"bad"`, `"neutral"`) not hardcoded hex. Theme tokens cascade to all reports when the theme changes.
2. **Measure-driven preferred** — Extension measures returning theme tokens. Logic lives in one place.
3. **Sparingly applied** — Highlight exceptions, not everything. Apply to variance/gap columns, not raw values.
4. **Accessible** — Blue/orange instead of red/green for colorblind safety. Always pair color with a secondary cue.
5. **Theme-first** — Check theme sentiment colors exist before applying CF.

### Positive/Negative Pattern

```dax
// Extension measure returns theme token
IF([Value] >= 0, "good", "bad")
```

Theme defines actual colors:

```json
"good": "#00B050",
"bad": "#FF0000",
"neutral": "#FFC000"
```

### Traffic Light Pattern

| Range | Color Name | Meaning |
|---|---|---|
| < 50% | `"bad"` | Critical |
| 50-80% | `"neutral"` | Warning |
| > 80% | `"good"` | On track |

## Color Don'ts

1. **Too many colors** — Maximum 6-8 distinct colors per visual
2. **Pure black** — Use dark gray (#333) instead
3. **Neon/bright colors** — Cause eye strain
4. **Red for positive** — Confuses users
5. **Color-only meaning** — Always pair with text/icons
6. Rainbow gradients, clashing combinations, low contrast combinations

## Accessibility

### Color Blindness Safe Combinations

- Blue + Orange (instead of Red + Green)
- Blue + Yellow
- Dark + Light variants of same hue

### Alternative Indicators

Always pair colors with:
- Icons (up/down arrows)
- Patterns (solid/hatched)
- Text labels
- Shapes (markers)
