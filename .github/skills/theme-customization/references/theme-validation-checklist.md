# Theme Validation Checklist

Validation checklist for Power BI report themes. Used during theme creation (by `pbi-report`) and during quality review (by `pbi-qa`).

## Structural Validation

| # | Check | Severity | Rule |
|---|---|---|---|
| 1 | JSON syntax valid | FAIL | Must parse without errors |
| 2 | `name` property present | FAIL | Theme must have a display name |
| 3 | `dataColors` array present | FAIL | Must have at least 6 hex values |
| 4 | All `dataColors` are valid 6-digit hex | FAIL | Pattern: `^#[0-9A-Fa-f]{6}$` |
| 5 | `visualStyles["*"]["*"]` exists | FAIL | Wildcard section is mandatory for consistency |
| 6 | No `null` values in `visualStyles` keys | FAIL | Null visual-type sections cause silent failures |
| 7 | All `visualStyles` values use array wrapper | WARNING | Properties must be `[{...}]` not `{...}` |

## Color Validation

| # | Check | Severity | Rule |
|---|---|---|---|
| 8 | `dataColors` has 6-12 entries | WARNING | < 6 repeats too soon; > 12 is hard to distinguish |
| 9 | `dataColors[0]` is the intended primary color | INFO | First color appears most frequently |
| 10 | Sentiment colors defined (`good`, `bad`, `neutral`) | WARNING | Required if report uses measure-driven CF |
| 11 | Sentiment colors are root-level keys | FAIL | Must be `"good": "#hex"`, NOT nested under `sentimentColors` |
| 12 | Sentiment colors distinct from each other | WARNING | `good` ≠ `bad` ≠ `neutral` |
| 13 | Gradient colors defined (`maximum`, `center`, `minimum`) | INFO | Required if report uses gradient CF |
| 14 | Colors accessible for colorblind users | WARNING | Avoid red/green pairs; prefer blue/orange diverging |
| 15 | Foreground/background variants defined | INFO | Recommended for container surfaces and filter pane |

## Typography Validation

| # | Check | Severity | Rule |
|---|---|---|---|
| 16 | `textClasses` defined | WARNING | Required for consistent typography |
| 17 | Minimum roles covered: `title`, `header`, `label`, `callout` | WARNING | Missing roles fall back to built-in defaults |
| 18 | Font is supported by Power BI | FAIL | Only built-in fonts (Segoe UI, Arial, Calibri, etc.) |
| 19 | `textClasses` uses plain hex for `color` | FAIL | Must be `"color": "#hex"`, NOT `{"solid": {"color": ...}}` |
| 20 | Font sizes legible (min 9pt data, 12pt labels) | WARNING | Accessibility requirement |

## Wildcard Validation

| # | Check | Severity | Rule |
|---|---|---|---|
| 21 | `dropShadow.show: false` in wildcard | WARNING | Shadows cause visual noise and accessibility issues |
| 22 | `background.show: false` in wildcard | INFO | Clean canvas; visuals opt in individually |
| 23 | `border.show: false` in wildcard | INFO | Use spacing instead of borders |
| 24 | `title` configured in wildcard | WARNING | Font, size, color should be consistent |
| 25 | `padding` configured in wildcard | INFO | Consistent inner spacing across visuals |

## Visual-Type Override Validation

| # | Check | Severity | Rule |
|---|---|---|---|
| 26 | `textbox` suppresses container chrome | WARNING | Title, background, border, shadow should be off |
| 27 | `image` suppresses container chrome | WARNING | Same as textbox |
| 28 | Property names match schema | FAIL | e.g., `backColor` not `backgroundColor` for tables |
| 29 | Color values use correct format for context | FAIL | `visualStyles` uses `{"solid": {"color": ...}}`; `textClasses` uses plain hex |

## Cross-Report Consistency

| # | Check | Severity | Rule |
|---|---|---|---|
| 30 | Theme referenced in `report.json` | FAIL | `themeCollection.customTheme.name` must point to existing file |
| 31 | Theme file exists at expected path | FAIL | `StaticResources/SharedResources/BaseThemes/` or `RegisteredResources/` |
| 32 | No hardcoded hex in visuals that contradicts theme palette | WARNING | Visual overrides should use ThemeDataColor or match palette |

## Review Output Format

```markdown
## Theme Validation — <ThemeName>

### Summary
- Structural: X/7 passed
- Colors: X/8 passed
- Typography: X/5 passed
- Wildcard: X/5 passed
- Visual-type: X/4 passed

### Findings
| # | Category | Check | Status | Details |
|---|----------|-------|--------|---------|
| 1 | Structure | JSON valid | ✅ PASS | |
| 8 | Color | dataColors count | ⚠️ WARNING | Only 4 colors — recommend 6+ |
| ... | ... | ... | ... | ... |
```
