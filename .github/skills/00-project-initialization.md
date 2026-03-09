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
- `<ProjectName>/PBIP/<ProjectName>.Report/definition/pages/Page1/`

Create `<ProjectName>/PBIP/<ProjectName>.Report/definition/version.json`:

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/versionMetadata/1.0.0/schema.json",
  "version": "1.0.0"
}
```

Create `<ProjectName>/PBIP/<ProjectName>.Report/definition/report.json`:

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/1.0.0/schema.json",
  "layoutOptimization": "None",
  "themeCollection": {}
}
```

Create `<ProjectName>/PBIP/<ProjectName>.Report/definition/pages/Page1/page.json`:

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/1.0.0/schema.json",
  "name": "Page1",
  "displayName": "Page 1",
  "displayOption": "FitToWidth",
  "width": 1280,
  "height": 720
}
```

Notes:
- PBIR allows a report with a single empty page (no visuals).
- Keep the page folder name aligned with the page `name` to avoid surprises.

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
```

Optionally create empty placeholders (recommended for a stable baseline):

- `relationships.tmdl` (empty)
- `expressions.tmdl` (empty)

## Validation Gate

Before proceeding to Step 1, confirm:

- [ ] `<ProjectName>/PBIP/<ProjectName>.pbip` exists and points to `<ProjectName>.Report`
- [ ] `<ProjectName>/PBIP/<ProjectName>.Report/definition.pbir` exists and references `../<ProjectName>.SemanticModel`
- [ ] `<ProjectName>/PBIP/<ProjectName>.Report/definition/` contains `version.json`, `report.json`, and `pages/Page1/page.json`
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
