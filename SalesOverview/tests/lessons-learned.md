# Lessons Learned — PBIP/TMDL/PBIR Error Registry

## Purpose
This document tracks all errors encountered during Power BI PBIP project generation, their root causes, applied fixes, and guardrails added to prevent recurrence. **Step 9 (Report Implementation — PBIR)** is the most error-prone step due to the strict and underdocumented JSON schema requirements of the PBIR format.

**Target audience**: AI coding agents and human developers working with PBIP projects.

---

## Error Index

| ID | Step | Severity | Error Category | Status |
|----|------|----------|---------------|--------|
| LL-001 | 03 | FATAL | TMDL — Missing `defaultPowerBIDataSourceVersion` | ✅ Fixed + Guardrail |
| LL-002 | 04 | FATAL | DAX — Reserved keywords as VAR names | ✅ Fixed + Guardrail |
| LL-003 | 09 | FATAL | PBIR — `version.json` wrong format | ✅ Fixed + Guardrail |
| LL-004 | 09 | INFO | PBIR — `report.json` empty `themeCollection` | ⚠️ Reverted (was WRONG FIX) |
| LL-005 | 09 | FATAL | PBIR — `page.json` `ordinal` property NOT allowed | ✅ Fixed + Guardrail |
| LL-006 | 09 | META | PBIR schema enforces `additionalProperties: false` | ✅ Guardrail |
| LL-007 | 09 | FATAL | PBIR — `visualContainerObjects` wrong nesting level | ✅ Fixed + Guardrail |
| LL-008 | 09 | INFO | PBIR — `displayOption` FitToPage vs FitToWidth | ✅ Reverted + Guardrail |

---

## LL-001: Missing `defaultPowerBIDataSourceVersion: powerBI_V3` in `model.tmdl`

### Error Message
```
A data model with version 3 of metadata is required.
```

### Root Cause
The `model.tmdl` file was generated without the `defaultPowerBIDataSourceVersion: powerBI_V3` property. Power BI Desktop v2.150+ (December 2025) requires this property to initialize the Analysis Services engine in Import mode.

### Fix Applied
Added `defaultPowerBIDataSourceVersion: powerBI_V3` to `model.tmdl`:
```tmdl
model Model
	culture: en-US
	defaultPowerBIDataSourceVersion: powerBI_V3
```

### Guardrails Added
- `.github/skills/00-project-initialization.md` — CRITICAL warning block
- `.github/skills/03-physical-model-tmdl.md` — Mandatory property in template
- `.github/skills/06-code-review.md` — Review checklist item
- `.github/references/tmdl-syntax-reference.md` — Documented in model template
- `.github/references/pbip-folder-structure.md` — Documented in Key Files section

### Microsoft Documentation
- [TMDL overview](https://learn.microsoft.com/analysis-services/tmdl/tmdl-overview)
- [Power BI Projects overview](https://learn.microsoft.com/power-bi/developer/projects/projects-overview)
- [Model properties (defaultPowerBIDataSourceVersion)](https://learn.microsoft.com/analysis-services/tmsl/model-object-tmsl#properties)

---

## LL-002: DAX Reserved Keywords Used as VAR Names

### Error Message
```
Syntax error: 'Variance' is a reserved keyword and cannot be used as a variable name.
Syntax error: 'Status' is a reserved keyword and cannot be used as a variable name.
```

### Root Cause
DAX measures used `VAR Variance` and `VAR Status` — both are reserved DAX keywords. The DAX parser rejects these at evaluation time.

### Complete List of DAX Reserved Keywords (NEVER use as VAR names)
`Variance`, `Status`, `Value`, `Date`, `Time`, `Name`, `Type`, `Order`, `Table`, `Column`, `Measure`, `Format`, `Currency`, `Number`, `Text`, `Boolean`, `TRUE`, `FALSE`, `BLANK`, `IF`, `AND`, `OR`, `NOT`, `IN`, `VAR`, `RETURN`, `DEFINE`, `EVALUATE`, `CALCULATE`, `FILTER`, `ALL`, `VALUES`, `DISTINCT`

### Fix Applied
- `VAR Variance` → `VAR SalesBudgetVariance`
- `VAR Status` → `VAR BudgetStatusValue`

### Guardrails Added
- `.github/skills/04-dax-development.md` — Forbidden VAR names list
- `.github/skills/06-code-review.md` — Review checklist item (sections 5 and 11.1)
- `.github/skills/07-functional-testing.md` — Test generation validation
- `.github/references/dax-patterns.md` — Pattern naming rules
- `.github/references/dax-optimization-framework.md` — Keyword check in optimization
- `.github/references/bpa-rules-reference.md` — BPA rule for keyword detection

### Microsoft Documentation
- [DAX syntax reference](https://learn.microsoft.com/dax/dax-syntax-reference)
- [VAR keyword](https://learn.microsoft.com/dax/var-dax)
- [DAX reserved words](https://learn.microsoft.com/dax/understanding-functions-for-parent-child-hierarchies-in-dax)

---

## LL-003: `version.json` — Wrong Version Format (Regex Validation Error)

### Error Message
```
'version.json':
String '4.0' does not match regex pattern '^[1-9][0-9]*\.(0|[1-9][0-9]*)\.0$'. 
Path 'version', line 3, position 18.
```

### Root Cause
The agent incorrectly changed `version.json` from `"1.0.0"` to `"4.0"`, confusing it with `definition.pbir`/`definition.pbism` which use `"version": "4.0"`.

**The `version.json` file** (at `Report/definition/version.json`) uses **semantic versioning** validated by regex `^[1-9][0-9]*\.(0|[1-9][0-9]*)\.0$`. Valid values: `"1.0.0"`, `"2.0.0"`, `"1.1.0"`, etc.

**The `definition.pbir` and `definition.pbism` files** use a **different version format**: `"4.0"` (major.minor without patch).

### Key Insight: Version Formats in PBIP
| File | Location | Valid Format | Example | Regex |
|------|----------|-------------|---------|-------|
| `version.json` | `Report/definition/` | Semver `X.Y.0` | `"1.0.0"` | `^[1-9][0-9]*\.(0\|[1-9][0-9]*)\.0$` |
| `definition.pbir` | `Report/` | `Major.Minor` | `"4.0"` | N/A |
| `definition.pbism` | `SemanticModel/` | `Major.Minor` | `"4.0"` | N/A |
| `versionMetadata $schema` | URL path | Semver | `1.0.0` | N/A |

### Fix Applied
Reverted `version.json` to:
```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/versionMetadata/1.0.0/schema.json",
  "version": "1.0.0"
}
```

### Guardrails Added
- `.github/skills/00-project-initialization.md` — CRITICAL warning block after version.json template
- `.github/references/pbip-folder-structure.md` — New "version.json (Report)" section with regex documentation

### Microsoft Documentation
- [Power BI Enhanced Report Format (PBIR)](https://learn.microsoft.com/power-bi/developer/projects/projects-report)
- [PBIP report definition schema](https://developer.microsoft.com/json-schemas/fabric/item/report/definition/versionMetadata/1.0.0/schema.json)

---

## LL-004: `report.json` — Empty `themeCollection` Causes Rendering Failure

### Error Message
```
JavaScript: TypeError
Cannot read properties of undefined (reading 'visualContainers')
at DesktopExplorationComponent.onExplorationActivated
```

### Root Cause
The `report.json` was generated with `"themeCollection": {}` (empty object). Power BI Desktop's rendering engine requires a `baseTheme` to initialize the visual rendering pipeline. Without it, the internal `sections` array (which maps to pages/visual containers) is never populated, resulting in `undefined` when accessing `visualContainers`.

### Fix Applied
Updated `report.json` to include a standard `baseTheme`:
```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/1.0.0/schema.json",
  "themeCollection": {
    "baseTheme": {
      "name": "CY24SU06",
      "reportVersionAtImport": "5.50",
      "type": "SharedResources"
    }
  },
  "layoutOptimization": "None"
}
```

### Standard `baseTheme` Values by PBI Desktop Version
| PBI Desktop Version | Theme Name | reportVersionAtImport |
|---------------------|-----------|----------------------|
| December 2025 (v2.150) | `CY24SU06` | `5.50` |
| September 2024 (v2.133) | `CY24SU06` | `5.50` |
| March 2024 (v2.127) | `CY23SU11` | `5.45` |

> **Note**: These values are extracted from PBIP projects saved by Power BI Desktop. Microsoft does not officially document them. Always verify by saving a blank .pbip project from the target PBI Desktop version.

### Guardrails Added
- `.github/skills/00-project-initialization.md` — report.json template updated with baseTheme + CRITICAL warning
- `.github/references/pbip-folder-structure.md` — New "report.json" section

### Microsoft Documentation
- [Power BI report themes](https://learn.microsoft.com/power-bi/create-reports/desktop-report-themes)
- [PBIP report definition](https://learn.microsoft.com/power-bi/developer/projects/projects-report)

---

## LL-005: `page.json` — `ordinal` Property NOT Allowed (CORRECTED)

### Error Message
```
'pages/Page1/page.json':
Property 'ordinal' has not been defined and the schema does not allow additional properties. 
Path 'ordinal', line 8, position 12.
```

### Root Cause
The PBIR page schema `1.0.0` enforces `additionalProperties: false`. The only allowed properties are:
- `$schema`
- `name`
- `displayName`
- `displayOption`
- `height`
- `width`

Adding ANY other property (like `ordinal`) causes a fatal `AdditionalProperties` validation error.

**History**: The agent first hypothesized that `ordinal` was missing (LL-005 v1). This was WRONG — adding `ordinal` caused the next error. The correct fix is to NOT include `ordinal` at all. Page ordering in PBIR is determined by folder name alphabetical order, not by any JSON property.

### Fix Applied
Removed `ordinal` from both page.json files. Final correct format:
```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/1.0.0/schema.json",
  "name": "Page1",
  "displayName": "Sales Overview FYTD",
  "displayOption": "FitToPage",
  "height": 720,
  "width": 1280
}
```

### Guardrails Added (corrected)
- `.github/skills/00-project-initialization.md` — CRITICAL warning: do NOT add ordinal or extra properties
- `.github/skills/08-report-design.md` — Removed ordinal from blueprint template
- `.github/skills/09-report-implementation.md` — CRITICAL warning: strict schema, no additional properties
- `.github/references/pbir-visual-templates.md` — Page template without ordinal + warning
- `.github/references/pbip-folder-structure.md` — Page section without ordinal + warning

### Microsoft Documentation
- [PBIR page definition schema](https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/1.0.0/schema.json)
- [Power BI Enhanced Report Format](https://learn.microsoft.com/power-bi/developer/projects/projects-report)

---

## LL-006: PBIR Schema Enforces `additionalProperties: false` (META-LESSON)

### Root Cause
All PBIR JSON schemas (`page.json`, `visual.json`, `report.json`, `version.json`) use `additionalProperties: false`, meaning they REJECT any property not explicitly defined in the schema.

### Key Rule
**NEVER add properties to PBIR JSON files based on assumptions or hypotheses.** If unsure whether a property exists in the schema:
1. Download the schema from the `$schema` URL
2. Check if the property is listed in the schema's `properties` object
3. Or save a reference .pbip from PBI Desktop and inspect what properties it generates

### Validation Pattern
The error pattern is always:
```
Property '<name>' has not been defined and the schema does not allow additional properties.
Path '<name>', line X, position Y.
```

This means the property `<name>` does not exist in the referenced `$schema`.

### Microsoft Documentation
- [JSON Schema additionalProperties](https://json-schema.org/understanding-json-schema/reference/object#additionalproperties)
- [PBIR schemas index](https://developer.microsoft.com/json-schemas/fabric/)

---

## LL-007: `visualContainerObjects` and `drillFilterOtherVisuals` placement in `visual.json`

### Error Message
```
Cannot read properties of undefined (reading 'visualContainers')
```

### Root Cause
The issue was caused by inconsistent assumptions during iterative fixes. These properties were moved multiple times without validating against the official JSON schema definition for the exact `visualContainer/1.0.0` document in use.

**Schema-validated structure**:
```json
{
  "visual": {
    "visualType": "card",
    "query": { ... },
    "objects": {},
    "visualContainerObjects": { ... },  // ✅ allowed by VisualConfig
    "drillFilterOtherVisuals": true      // ✅ allowed by VisualConfig
  }
}
```

### Why This Matters
The report can fail at runtime even when files seem syntactically valid if the visual payload does not align with the exact object model expected by the rendering engine and the active schema/version combination.

### Fix Applied
The generated visuals were rolled back and then reset again to an empty baseline to remove all unstable visual payloads and restart Step 9 from a known-good canvas.

### Guardrails Added
- `.github/references/pbir-visual-templates.md` — Templates aligned to schema-validated object placement
- `.github/skills/09-report-implementation.md` — Official Microsoft docs reference added
- `.github/skills/08-report-design.md` — Official Microsoft docs reference added

### Microsoft Documentation
- [Power BI Projects — Report definition](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report)
- Visual container schema: `https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/1.0.0/schema.json`

---

## LL-008: `displayOption` — FitToPage vs FitToWidth

### Context
During fix attempts for the `visualContainers` error, the agent changed `displayOption` from `FitToWidth` (original working value) to `FitToPage` as a speculative fix. This was unnecessary.

### Resolution
Reverted to `FitToWidth` in all page.json files and all reference/skill files. Both values are technically valid, but `FitToWidth` was the original documented value in the Microsoft docs example.

### Guardrails Added
All 5 reference/skill files updated to use `FitToWidth` consistently.

---

## Step 9 Risk Assessment

Step 9 (Report Implementation — PBIR Visual Generation) is the **highest-risk step** in the workflow because:

1. **Underdocumented format**: Microsoft does not provide comprehensive public documentation for the PBIR JSON schema. The JSON schema URLs exist but the actual schema constraints (required fields, regex patterns, allowed values) are enforced internally by Power BI Desktop.

2. **Multiple interdependent files**: A single missing property in any of `version.json`, `report.json`, or `page.json` can cause cascade failures that manifest as generic JavaScript errors in the rendering engine.

3. **Version format confusion**: Three different version formats coexist in the same project (`"1.0.0"` in version.json, `"4.0"` in definition.pbir/pbism, schema URL versions), making it easy to cross-contaminate values.

4. **No validation tooling**: Unlike TMDL (which has the Analysis Services engine for validation), PBIR JSON files have no external validation tool — errors are only discovered at runtime in Power BI Desktop.

### Recommended Workflow for Step 9
1. **Always start from a PBI Desktop-saved baseline**: Save a blank .pbip report from the target PBI Desktop version, inspect the generated `version.json`, `report.json`, and `page.json` to capture exact expected formats.
2. **Never modify structural files speculatively**: Only add/modify visual.json files. Do NOT change version.json, report.json, or page.json structure without verifying against a PBI-saved reference.
3. **Test incrementally**: After generating files, open in PBI Desktop BEFORE adding all visuals. Start with one empty page, verify it loads, then add visuals incrementally.

---

## Version Compatibility Matrix

| Component | Property | PBI Desktop Dec 2025 (v2.150) | Format |
|-----------|----------|-------------------------------|--------|
| `version.json` | `version` | `"1.0.0"` | Semver `X.Y.0` |
| `definition.pbir` | `version` | `"4.0"` | Major.Minor |
| `definition.pbism` | `version` | `"4.0"` | Major.Minor |
| `database.tmdl` | `compatibilityLevel` | `1600` | Integer |
| `model.tmdl` | `defaultPowerBIDataSourceVersion` | `powerBI_V3` | Enum |
| `report.json` | `baseTheme.name` | `"CY24SU06"` (optional) | String |
| `page.json` | (6 props only) | `$schema`, `name`, `displayName`, `displayOption`, `height`, `width` | Strict schema, no extras |

---

## General Lessons

### L1: Do NOT confuse version formats across PBIP files
`definition.pbir` uses `"4.0"`, `version.json` uses `"1.0.0"`. They serve different purposes and have different validation rules.

### L2: An empty `themeCollection: {}` is valid in `report.json`
Power BI Desktop applies the default theme automatically. Adding a `baseTheme` is optional and should only be done if a specific theme is needed. The previous claim that `baseTheme` was required was a WRONG FIX (LL-004).

### L3: NEVER add extra properties to PBIR JSON files
All PBIR schemas use `additionalProperties: false`. Only use properties that exist in the schema. `ordinal` is NOT a valid page property.

### L4: TMDL `model.tmdl` MUST include `defaultPowerBIDataSourceVersion: powerBI_V3`
Without it, the Analysis Services engine refuses to load the model.

### L5: DAX VAR names must not use reserved keywords
The DAX parser is strict about reserved words. Use descriptive prefixed names instead.

### L6: When in doubt, save a blank .pbip from PBI Desktop and compare
The saved files are the ground truth. Any AI-generated file should match the structure and property set of PBI Desktop output.

### L7: Validate `visualContainer` payload against the official schema before edits
For `visualContainer/1.0.0`, verify property placement directly against the schema definitions and avoid speculative moves between top-level and `visual` object.

### L8: Always verify PBIR structures against Microsoft official documentation
Reference: https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report
NEVER guess or speculate about PBIR JSON schema. ALWAYS check the official docs or a PBI Desktop-saved reference file.

### L9: If runtime error persists after multiple schema fixes, reset Step 9 to empty canvas
When repeated `visualContainers` runtime failures occur, clear all visual folders and restart Step 9 from a minimal page baseline (`page.json` only), then reintroduce visuals incrementally.

---

## Change Log

| Date | Error ID | Action | Files Modified |
|------|----------|--------|---------------|
| 2026-03-09 | LL-001 | Fix + Guardrail | model.tmdl, 5 reference/skill files |
| 2026-03-09 | LL-002 | Fix + Guardrail | _Measures.tmdl, 6 reference/skill files |
| 2026-03-09 | LL-003 | Fix + Guardrail | version.json, 2 reference/skill files |
| 2026-03-09 | LL-004 | Fix + Guardrail | report.json, 2 reference/skill files |
| 2026-03-09 | LL-005 | Fix v1 WRONG (added ordinal) | 2× page.json, 5 reference/skill files |
| 2026-03-09 | LL-005 | Fix v2 CORRECT (removed ordinal) | 2× page.json, 5 reference/skill files |
| 2026-03-09 | LL-006 | Guardrail (meta-lesson) | lessons-learned.md |
| 2026-03-09 | LL-004 | REVERTED — baseTheme not required | report.json, 2 reference/skill files |
| 2026-03-09 | LL-007 | Fix + Guardrail | 19× visual.json, pbir-visual-templates.md, 2 skill files |
| 2026-03-09 | LL-008 | Revert FitToPage → FitToWidth | 2× page.json, 5 reference/skill files |
| 2026-03-09 | LL-009 | Reset Step 9 to empty visual canvas baseline | 19× visual folders removed, workflow_state.json |
