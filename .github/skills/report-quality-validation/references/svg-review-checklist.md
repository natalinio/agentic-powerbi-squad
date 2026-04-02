# SVG Measure Review Checklist

Validation checklist for SVG DAX measures before deployment. Apply when reviewing any measure that generates inline SVG graphics.

## Validation Checklist

| # | Check | Rule | Severity |
|---|---|---|---|
| 1 | **Prefix** | Measure returns string starting with `"data:image/svg+xml;utf8,"` | FAIL |
| 2 | **xmlns** | `<svg>` element includes `xmlns='http://www.w3.org/2000/svg'` | FAIL |
| 3 | **viewBox** | Uses `viewBox` for responsive scaling (not fixed `width`/`height` alone) | WARNING |
| 4 | **Colors** | Hex codes with `#` only (e.g., `fill='#2196F3'`). No `%23` URL encoding, no named colors | FAIL |
| 5 | **Quotes** | SVG attributes use single quotes to avoid DAX double-quote conflicts | FAIL |
| 6 | **DAX escaping** | Double quotes inside DAX strings escaped as `""` | FAIL |
| 7 | **HASONEVALUE guard** | Returns `BLANK()` when not in single-category context (for table/matrix measures) | WARNING |
| 8 | **dataCategory** | Measure definition includes `dataCategory: ImageUrl` (in TMDL or reportExtensions.json) | FAIL |
| 9 | **VAR structure** | SVG broken into VAR variables (Prefix, Content elements, Suffix) for readability | WARNING |
| 10 | **Coordinate system** | Y-axis inverted correctly (Y=0 at top in SVG) | FAIL |

## Design Review

After the checklist, assess:

- **Complexity**: Rendered SVG > 32K characters will fail in Power BI. Flag measures that concatenate large datasets without limits
- **Coordinates**: Values rounded to 1-2 decimal places for performance
- **Series data**: Uses `CONCATENATEX` for polyline/path point generation
- **Target visual**: Clear whether the SVG is for table/matrix cell, Image visual, or card
- **Colors**: Muted and purposeful — not decorative

## Common Failures

| Symptom | Cause | Fix |
|---|---|---|
| Blank image | Missing `xmlns` attribute | Add `xmlns='http://www.w3.org/2000/svg'` |
| Broken image icon | Missing `data:image/svg+xml;utf8,` prefix | Prepend the data URI prefix |
| Image not showing | Missing `dataCategory: ImageUrl` | Add annotation to measure definition |
| Garbled rendering | `%23` instead of `#` for colors | Use `#` directly — Power BI handles encoding |
| Upside-down chart | Y-axis not inverted | Remember SVG Y=0 is top; subtract from max Y |
| Error in table context | No `HASONEVALUE` guard | Wrap in `IF(HASONEVALUE(...), <svg>, BLANK())` |
| Truncated output | SVG string > 32K chars | Reduce data points, simplify paths, round coordinates |
