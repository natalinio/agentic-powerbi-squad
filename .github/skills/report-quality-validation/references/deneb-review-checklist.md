# Deneb Visual Review Checklist

Validation checklist for Deneb custom visuals (Vega and Vega-Lite) before deployment. Apply when reviewing any Deneb spec or its PBIR integration.

## Validation Checklist

| # | Check | Rule | Severity |
|---|---|---|---|
| 1 | **Schema** | `$schema` points to valid Vega (`https://vega.github.io/schema/vega/v5.json`) or Vega-Lite (`https://vega.github.io/schema/vega-lite/v5.json`) URL | FAIL |
| 2 | **Data binding** | Vega uses `"data": [{"name": "dataset"}]` (array); Vega-Lite uses `"data": {"name": "dataset"}` (object) | FAIL |
| 3 | **Field names** | Match `nativeQueryRef` display names from PBIR bindings; special chars (`.[]\"`) become `_`, spaces preserved | FAIL |
| 4 | **Expressions** | Field refs with spaces use double quotes (`datum["Field Name"]`), never single quotes | FAIL |
| 5 | **Responsive sizing** (Vega) | Uses `pbiContainerWidth`/`pbiContainerHeight` signals | WARNING |
| 6 | **Config** | Includes `autosize: "fit"`, `view.stroke: "transparent"`, `font: "Segoe UI"` | WARNING |
| 7 | **Theme colors** | Uses `pbiColor()` / `pbiColorNominal` instead of hardcoded hex where possible | WARNING |
| 8 | **Marks** | Vega: encode blocks use `enter`/`update`/`hover`. Vega-Lite: proper encoding channels | FAIL |
| 9 | **Tooltips** | Enabled with `"tooltip": {"signal": "datum"}` (Vega) or `"tooltip": true` (Vega-Lite) | WARNING |
| 10 | **No external data** | No URL-based data sources (blocked by AppSource certification and Deneb sandbox) | FAIL |

## PBIR Integration Checks

| # | Check | Rule | Severity |
|---|---|---|---|
| 11 | **Visual type** | `visualType` in `visual.json` is `"deneb_deneb"` (community) or registered custom visual GUID | FAIL |
| 12 | **Spec location** | JSON spec embedded in `visual.objects.vega[].properties.jsonSpec` or `vegaLite[].properties.jsonSpec` | FAIL |
| 13 | **Field bindings** | All fields used in spec exist in `visual.query.queryState` projections | FAIL |
| 14 | **Provider match** | Spec type (Vega vs Vega-Lite) matches the object key (`vega` vs `vegaLite`) in visual.objects | FAIL |

## Design Review

After the checklist, assess:

- **Chart type**: Appropriate for the data relationship being shown?
- **Color usage**: Intentional (not decorative)? Accessible palette?
- **Axes/legends**: Minimal and readable?
- **Text sizes**: Sufficient (12pt+ for labels)?
- **Sort order**: Sensible (value descending unless time-based)?
- **Complexity**: Spec not over-engineered for what a native visual could do?

## Common Failures

| Symptom | Cause | Fix |
|---|---|---|
| Blank visual | Wrong data binding format (array vs object) | Vega = array, Vega-Lite = object |
| "Unknown field" in spec | Field name doesn't match `nativeQueryRef` | Check PBIR bindings for exact display names |
| Visual doesn't resize | Missing responsive signals (Vega) | Add `pbiContainerWidth`/`pbiContainerHeight` signals |
| Colors don't match theme | Hardcoded hex instead of `pbiColor()` | Replace with `pbiColor(n)` or `pbiColorNominal` |
| Tooltip not working | Missing tooltip configuration | Add tooltip encoding or signal |
| Spec validation error | Single quotes in field expression | Use `datum["Field Name"]` with double quotes |
| Visual blocked in service | External URL data source | Remove all URL-based data; use only `"dataset"` |
