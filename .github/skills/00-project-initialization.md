# Skill: Project Initialization (PBIP Canvas Bootstrap)

## Goal

Bootstrap a new project folder so Power BI Desktop can open it as a PBIP project **without requiring the user to manually create the empty canvas first**.

This skill creates the minimal **PBIP + Report (PBIR) + SemanticModel (TMDL)** scaffolding and the project subfolders used by later steps.

## When to Run

Run this skill **before Step 1** whenever:

- The user points to a `<ProjectName>/` at repository root, AND
- `<ProjectName>/PBIP/` or `<ProjectName>/PBIP/<ProjectName>.pbip` is missing, OR
- `<ProjectName>/PBIP/<ProjectName>.Report/` or `<ProjectName>/PBIP/<ProjectName>.SemanticModel/` is missing.

## Non-Negotiable Constraints

- Use Microsoft official JSON schemas declared in the files.
- Paths inside PBIP/PBIR definitions MUST be **relative** and MUST use `/` as separator.
- Files should be encoded as **UTF-8 without BOM**.
- This repo standard keeps PBIP artifacts under `<ProjectName>/PBIP/` (not at project root).

## What to Create

### 1) Project subfolders (if missing)

Under `<ProjectName>/` ensure the existence of:

- `spec/`
- `data/`
- `scripts/`
- `tests/`
- `PBIP/`

If you create any of these folders, also create a `README.md` in each folder with:

- `data/README.md`: This folder contains generated CSV mock data files for local development and testing.
- `scripts/README.md`: This folder contains Python scripts for mock data generation and data processing utilities.
- `tests/README.md`: This folder contains functional test definitions, execution reports, and test result artifacts.
- `spec/README.md`: This folder contains user-provided specification files (requirements, functional specs, etc.).
- `PBIP/README.md`: This folder contains PBIP project artifacts (Report and Semantic Model definitions).

### 2) PBIP shortcut file (required for “open by .pbip”)

Create `<ProjectName>/PBIP/<ProjectName>.pbip` with the minimal content:

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json",
  "version": "1.0.0",
  "artifacts": [
    {
      "report": {
        "path": "<ProjectName>.Report"
      }
    }
  ],
  "settings": {
    "enableAutoRecovery": true
  }
}
```

### 3) Report item folder (PBIR)

Create folder: `<ProjectName>/PBIP/<ProjectName>.Report/`

Create `<ProjectName>/PBIP/<ProjectName>.Report/definition.pbir`:

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
  "version": "4.0",
  "datasetReference": {
    "byPath": {
      "path": "../<ProjectName>.SemanticModel"
    }
  }
}
```

Create the PBIR definition folder structure:

- `<ProjectName>/PBIP/<ProjectName>.Report/definition/`
- `<ProjectName>/PBIP/<ProjectName>.Report/definition/pages/`
- `<ProjectName>/PBIP/<ProjectName>.Report/definition/pages/<PageObjectName>/`
- `<ProjectName>/PBIP/<ProjectName>.Report/definition/pages/<PageObjectName>/visuals/`
- `<ProjectName>/PBIP/<ProjectName>.Report/StaticResources/SharedResources/BaseThemes/`

Where `<PageObjectName>` is the PBIR page object name (recommended: 20-character lowercase alphanumeric id, for example `32fe1020890a4d7642b0`). It must be unique within the report.

Create `<ProjectName>/PBIP/<ProjectName>.Report/definition/version.json`:

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/versionMetadata/1.0.0/schema.json",
  "version": "2.0.0"
}
```

> **CRITICAL**: The `version` field MUST follow semver format matching `^[1-9][0-9]*\.(0|[1-9][0-9]*)\.0$` (e.g., `"1.0.0"`). Do NOT use `"4.0"` or any non-semver value — Power BI Desktop will reject it with a regex validation error. The value `"4.0"` belongs ONLY in `definition.pbir` and `definition.pbism`, NOT in `version.json`.

Create `<ProjectName>/PBIP/<ProjectName>.Report/definition/report.json`:

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/3.1.0/schema.json",
  "themeCollection": {
    "baseTheme": {
      "name": "CY25SU12",
      "reportVersionAtImport": {
        "visual": "2.5.0",
        "report": "3.1.0",
        "page": "2.3.0"
      },
      "type": "SharedResources"
    }
  },
  "objects": {
    "section": [
      {
        "properties": {
          "verticalAlignment": {
            "expr": {
              "Literal": {
                "Value": "'Top'"
              }
            }
          }
        }
      }
    ]
  },
  "resourcePackages": [
    {
      "name": "SharedResources",
      "type": "SharedResources",
      "items": [
        {
          "name": "CY25SU12",
          "path": "BaseThemes/CY25SU12.json",
          "type": "BaseTheme"
        }
      ]
    }
  ],
  "settings": {
    "useStylableVisualContainerHeader": true,
    "exportDataMode": "AllowSummarized",
    "defaultDrillFilterOtherVisuals": true,
    "allowChangeFilterTypes": true,
    "useEnhancedTooltips": true,
    "useDefaultAggregateDisplayName": true
  }
}
```

Create `<ProjectName>/PBIP/<ProjectName>.Report/definition/pages/pages.json`:

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json",
  "pageOrder": [
    "<PageObjectName>"
  ],
  "activePageName": "<PageObjectName>"
}
```

Create `<ProjectName>/PBIP/<ProjectName>.Report/definition/pages/<PageObjectName>/page.json`:

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.0.0/schema.json",
  "name": "<PageObjectName>",
  "displayName": "Page 1",
  "displayOption": "FitToPage",
  "height": 720,
  "width": 1280
}
```

Create `<ProjectName>/PBIP/<ProjectName>.Report/StaticResources/SharedResources/BaseThemes/CY25SU12.json` by copying the baseline theme from an empty report generated by the same Power BI Desktop version.

> **CRITICAL**: Do NOT create `<ProjectName>.Report/report.json` at report root. That file is PBIR-Legacy and causes a hard failure when combined with PBIR (`definition/` folder).

> **CRITICAL**: The PBIR page schema `1.0.0` does NOT allow additional properties. Only use the 6 properties shown above: `$schema`, `name`, `displayName`, `displayOption`, `height`, `width`. Do NOT add `ordinal` or any other property — Power BI Desktop will reject the file with `AdditionalProperties` validation error. Page ordering is determined by folder name alphabetical order, not by any property. Use `"FitToWidth"` as the standard displayOption.

Notes:
- PBIR allows a report with a single empty page (no visuals).
- Keep the page folder name aligned with the page `name` to avoid surprises.
- Keep `<ProjectName>/PBIP/<ProjectName>.Report/.pbi/` out of source control and regenerate local settings in Desktop.

### 4) Semantic model item folder (TMDL)

Create folder: `<ProjectName>/PBIP/<ProjectName>.SemanticModel/`

Create `<ProjectName>/PBIP/<ProjectName>.SemanticModel/definition.pbism`:

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
  "version": "4.0",
  "settings": {}
}
```

Create the TMDL definition folder structure:

- `<ProjectName>/PBIP/<ProjectName>.SemanticModel/definition/`
- `<ProjectName>/PBIP/<ProjectName>.SemanticModel/definition/tables/`

Create minimal TMDL files (TAB-indented):

`database.tmdl`
```tmdl
database <ProjectName>
	compatibilityLevel: 1600
```

`model.tmdl`
```tmdl
model Model
	culture: en-US
	defaultPowerBIDataSourceVersion: powerBI_V3
```

> **CRITICAL**: Always include `defaultPowerBIDataSourceVersion: powerBI_V3`. Omitting it causes *"metadata version 3 required"* errors in Power BI Desktop.

Optionally create empty placeholders (recommended for a stable baseline):

- `relationships.tmdl` (empty)
- `expressions.tmdl` (empty)

## Validation Gate

Before proceeding to Step 1, confirm:

- [ ] `<ProjectName>/PBIP/<ProjectName>.pbip` exists and points to `<ProjectName>.Report`
- [ ] `<ProjectName>/PBIP/<ProjectName>.Report/definition.pbir` exists and references `../<ProjectName>.SemanticModel`
- [ ] `<ProjectName>/PBIP/<ProjectName>.Report/definition/` contains `version.json`, `report.json`, `pages/pages.json`, and `pages/<PageObjectName>/page.json`
- [ ] `<ProjectName>/PBIP/<ProjectName>.Report/StaticResources/SharedResources/BaseThemes/CY25SU12.json` exists and is referenced by `definition/report.json`
- [ ] `<ProjectName>/PBIP/<ProjectName>.Report/report.json` does NOT exist
- [ ] `<ProjectName>/PBIP/<ProjectName>.SemanticModel/definition.pbism` exists
- [ ] `<ProjectName>/PBIP/<ProjectName>.SemanticModel/definition/` contains at least `database.tmdl` and `model.tmdl`
- [ ] `<ProjectName>/workflow_state.json` exists with initial state

If any check fails, STOP and fix the initialization before running Step 1.

## Workflow State Initialization

At the end of Step 00 (after all scaffolding is created and validated), CREATE the initial `<ProjectName>/workflow_state.json`:

```json
{
  "projectName": "<ProjectName>",
  "currentStep": 0,
  "completedSteps": [],
  "pendingStep": null,
  "createdAt": "<ISO 8601 timestamp>",
  "lastUpdated": "<ISO 8601 timestamp>"
}
```

This file will be updated by every subsequent step to track workflow progress and enable resumability.
