---
name: theme-customization
description: >-
  Use when creating, modifying, or auditing Power BI report themes.
  Triggers: "create a theme", "design a theme", "build a theme", "apply theme",
  "update theme colors", "change theme typography", "set text classes",
  "enforce theme compliance", "audit theme adherence", "push formatting to theme",
  "promote bespoke formatting to theme", "clear visual overrides",
  "standardize report formatting", "validate a theme",
  "add visual-type overrides to theme", "sentiment colors", "dataColors palette".
user-invocable: true
---

# Skill: Theme Customization

## Purpose
Create, modify, validate, and enforce Power BI report themes. A well-designed theme ensures visual consistency across the report by pushing formatting into a centralized JSON file rather than scattering overrides across individual visuals.

When a report is driven by a UI mockup, screenshot, Figma file, or React prototype, this skill should be used early to extract and encode the visual design system before heavy PBIR implementation begins.

## Prerequisites
1. ✅ A PBIP project exists with `<ProjectName>/PBIP/<ProjectName>.Report/` folder.
2. ✅ The theme file lives at `StaticResources/SharedResources/BaseThemes/<ThemeName>.json` or `StaticResources/RegisteredResources/<ThemeName>.json`.
3. ✅ `definition/report.json` references the theme via `themeCollection.customTheme.name`.

## References — Load on Demand

| Reference | Path | When to Load |
|---|---|---|
| Theme JSON Structure | `references/theme-json-structure.md` | Creating or modifying a theme |
| Visual Type Overrides | `references/visual-type-overrides.md` | Adding type-specific overrides |
| Theme Validation Checklist | `references/theme-validation-checklist.md` | Validating or auditing a theme |

## Optional PBIR CLI Backend

When the local `pbir` CLI is available, it may be used as an execution helper for theme inspection and theme application.

Good fits:
- `pbir theme colors`
- `pbir theme text-classes`
- `pbir theme fonts`
- `pbir theme set-colors`
- `pbir theme set-text-classes`
- `pbir theme set-formatting`
- `pbir theme validate`

Rules:
1. The theme JSON in the repository remains the source of truth.
2. Do **NOT** run `pbir setup`.
3. Prefer theme-level changes over visual-level overrides even when the CLI can change both.
4. If the CLI is unavailable or cannot express the required change cleanly, fall back to direct theme JSON edits guided by repository references.

## The Formatting Hierarchy

Power BI applies formatting through a four-level cascade:

```
Level 1  Power BI built-in defaults
Level 2  Theme wildcard:     visualStyles["*"]["*"]         → ALL visuals
Level 3  Theme visual-type:  visualStyles["lineChart"]["*"] → overrides wildcard for that type
Level 4  Visual instance:    visual.json objects             → overrides everything
```

**Core principle**: Push as much formatting as possible into levels 2 and 3. Visual-level overrides (level 4) should exist only for true one-offs or conditional formatting.

## Workflows

### A) Create a New Theme

1. **READ** `references/theme-json-structure.md` for complete structure reference.
2. **Start from a valid base** — use `examples/minimal-custom-theme.json` or `examples/enterprise-theme.json`. Never author from an empty `{}`.
3. **Design the color system first**:
   - `dataColors`: 6-12 hex values, muted/desaturated, visually distinguishable
   - Semantic colors: `good`, `bad`, `neutral` (flat hex at root level)
   - Background/foreground variants
4. **Set typography** (`textClasses`): `title`, `header`, `label`, `callout`, `dataTitle`. Use Segoe UI / Segoe UI Semibold only.
5. **Set wildcard container defaults** (`visualStyles["*"]["*"]`): title, background off, border off, dropShadow off, padding.
6. **Add visual-type overrides** — READ `references/visual-type-overrides.md`. At minimum: `textbox` and `image` to suppress container chrome.
7. **Validate** — READ `references/theme-validation-checklist.md` and apply all checks.
8. **Place file** at `StaticResources/SharedResources/BaseThemes/<ThemeName>.json`.
9. **Update `report.json`** to reference the theme.

### B) Modify an Existing Theme

1. **READ** the existing theme file to understand current structure.
2. **Identify the change scope**: colors, typography, wildcard, visual-type overrides.
3. **Apply changes** following the structure from `references/theme-json-structure.md`.
4. **Validate** with `references/theme-validation-checklist.md`.

### B.1) Theme-First Workflow for Mockup-Driven Reports

When a visual mockup is available, prefer a theme-first approach before detailed PBIR layout work.

1. Extract design tokens from the mockup: page background, card surfaces, accent colors, sentiment colors, typography hierarchy, spacing rhythm, and container treatment.
2. Encode reusable tokens in the theme JSON first instead of scattering them across visuals.
3. Reserve visual-level overrides for true one-offs, SVG content, Deneb specifics, or conditional formatting.
4. Align `good`, `bad`, and `neutral` with the mockup's semantic cues when possible.
5. Document any mockup styling that cannot be expressed in the theme and must remain a visual-level approximation.

This reduces drift between design intent and implementation and improves consistency when a mockup must be translated into a Power BI-feasible visual language.

### C) Promote Visual Overrides to Theme

When visuals have accumulated bespoke formatting that should become defaults:

1. **Audit**: Identify which visuals have `objects` or `visualContainerObjects` overrides.
2. **Classify** each override:
   - **Stale**: Duplicates theme value → remove from visual
   - **Conflicting**: Different from theme → promote to theme or document as exception
   - **Conditional formatting**: Expression-based → never promote, keep in visual
3. **Decide placement**: Wildcard (`["*"]["*"]`) for universal, visual-type (`["<type>"]["*"]`) for type-specific.
4. **Write** the value into the theme JSON.
5. **Remove** the override from the visual.
6. **Verify** the visual still renders correctly.

### D) Audit Theme Compliance

1. **Establish baseline**: Read theme wildcard and type-level sections.
2. **Scan visuals**: Find all `visual.json` files with `objects` or `visualContainerObjects`.
3. **Compare**: For each override, check if it matches or conflicts with the theme.
4. **Report findings** using severity levels:
   - **Critical**: Chrome overrides contradicting theme across multiple visuals
   - **Warning**: Individual property differences from theme defaults
   - **Suggestion**: Empty/null override keys, redundant values

## Anti-Hallucination Rules

1. **Never invent theme property names** — verify against the theme JSON schema or the `references/visual-type-overrides.md` index.
2. **Color format matters**: `textClasses` uses plain hex strings (`"color": "#343a40"`); `visualStyles` uses object wrappers (`{"solid": {"color": "#343a40"}}`). Mixing them causes silent failures.
3. **Supported fonts only**: Segoe UI, Segoe UI Semibold, Segoe UI Light, Segoe UI Bold, Arial, Calibri, Candara, Consolas, Courier New, DIN, Georgia, Tahoma, Times New Roman, Trebuchet MS, Verdana. No custom fonts.
4. **Semantic colors are root-level keys** (`"good": "#2f9e44"`), NOT nested under a `sentimentColors` object.
5. **Array wrapper required**: All `visualStyles` container values must be wrapped in `[{...}]`.

## Schema and Documentation

| Resource | URL |
|---|---|
| Theme JSON Schema (versioned, Draft 7) | https://github.com/microsoft/powerbi-desktop-samples/tree/main/Report%20Theme%20JSON%20Schema |
| Microsoft Learn — Report Themes | https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-report-themes |
| Community theme templates | https://github.com/deldersveld/PowerBI-ThemeTemplates |
