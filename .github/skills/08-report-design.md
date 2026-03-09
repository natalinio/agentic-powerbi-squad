# Skill: Report Design (Layout, UX, Navigation)

## Purpose
Design the Power BI report experience (pages, layout, visuals, interactions, navigation) based on:
- the functional specification (`<ProjectName>/spec/*.md`), and
- the finalized semantic model (`<ProjectName>/PBIP/<ProjectName>.SemanticModel/definition/`).

This step produces a **design blueprint** only. It does NOT implement PBIP report artifacts.

## Context Window Management (CRITICAL)
- Load only the minimum needed inputs for this step: the spec + the semantic model object names.
- Use `.github/references/report-design-visualization-best-practices.md` **only when needed** (e.g., choosing a chart type, defining cross-filtering rules, accessibility checks). Do NOT preload it if the spec already dictates the visual choices.
- NEVER invent measure/field names: always read them from TMDL.

## Prerequisites — MANDATORY
Before starting report design:
1. ✅ The semantic model exists and is valid (Steps 3–7 completed).
2. ✅ The specification describes report goals (audience, questions, KPIs, navigation expectations). If missing, ask targeted questions and STOP.
3. ✅ Model introspection is possible by reading TMDL files.

## Step 8 Procedure

### 8.1 Inputs to Read
1. Functional spec: `<ProjectName>/spec/<spec>.md`
2. Semantic model TMDL:
   - `<ProjectName>/PBIP/<ProjectName>.SemanticModel/definition/model.tmdl`
   - `<ProjectName>/PBIP/<ProjectName>.SemanticModel/definition/tables/*.tmdl`
   - `<ProjectName>/PBIP/<ProjectName>.SemanticModel/definition/relationships.tmdl`

### 8.2 Build a Visual Design Field Registry (MANDATORY)
Create an internal registry of report-usable objects by reading TMDL (same anti-hallucination principle as Step 7):
- **Measures**: from `_Measures.tmdl` (exact display names)
- **Date table**: confirm the Date table and main Date column
- **Dimensions**: user-facing attributes (prefer non-hidden descriptive columns)
- **Facts**: avoid exposing technical keys; prefer measures

**CRITICAL RULES**:
- NEVER guess object names.
- If the spec uses business labels that don't map 1:1 to model objects, ask clarifying questions and STOP.

### 8.3 Derive Report Information Architecture
From the spec, define:
- Primary KPIs (what must be seen immediately)
- Secondary analysis (trends, comparisons, breakdowns)
- Tertiary controls (slicers/filters/navigation)

Default to the simplest structure that satisfies the spec:
- If the spec is summary-only → single-page layout.
- If the spec includes drill-down needs → summary page + detail page.

### 8.4 Produce the Report Design Blueprint (OUTPUT)

The agent MUST generate and save the report design blueprint as a **physical JSON file** at `<ProjectName>/spec/report_blueprint.json`. This file will be the input for Step 9 (Report Implementation). Only AFTER saving the file, the agent must present a summary and stop for approval.

#### JSON Schema for `report_blueprint.json`

```json
{
  "$schema": "report_blueprint_schema",
  "projectName": "<ProjectName>",
  "generatedDate": "<ISO 8601 timestamp>",
  "semanticModelPath": "<ProjectName>/PBIP/<ProjectName>.SemanticModel/definition/",
  "pages": [
    {
      "pageId": "Page1",
      "pageName": "Overview",
      "displayName": "Sales Overview",
      "goal": "Provide a summary of key sales KPIs and trends",
      "targetAudience": "Sales Manager",
      "width": 1280,
      "height": 720,
      "displayOption": "FitToWidth",
      "slicers": [
        {
          "field": "Dim_Date[FiscalYear]",
          "type": "dropdown",
          "label": "Fiscal Year"
        }
      ],
      "visuals": [
        {
          "visualId": "visual_01",
          "visualType": "card",
          "title": "Total Sales FYTD",
          "measures": ["Sales Amount FYTD"],
          "axisFields": [],
          "legendField": null,
          "sortBy": null,
          "defaultGranularity": null,
          "tooltip": null,
          "drillthrough": null,
          "position": {
            "x": 0,
            "y": 0,
            "width": 200,
            "height": 100
          }
        }
      ],
      "interactions": {
        "crossFilterMode": "highlight",
        "customInteractions": []
      }
    }
  ],
  "navigation": {
    "model": "tabs",
    "drillthroughPages": [],
    "bookmarks": []
  },
  "accessibility": {
    "altTextRequired": true,
    "colorBlindSafe": true,
    "notes": []
  },
  "performanceGuardrails": {
    "maxVisualsPerPage": 8,
    "avoidHighCardinalitySlicers": true,
    "preferMeasuresOverImplicitAggregations": true,
    "notes": []
  }
}
```

#### Blueprint Generation Rules

The agent MUST follow these rules when generating the JSON:

1. **Page definitions**: One object per page. `pageId` must be a valid folder name (e.g., `Page1`, `Page2`).
2. **Visual definitions**: Each visual must reference measures and fields that exist in the Visual Design Field Registry (8.2).
3. **Field references**: Use exact `Table[Column]` or `[Measure Name]` syntax as found in TMDL.
4. **Positions**: Provide approximate `x`, `y`, `width`, `height` values for visual layout (based on 1280x720 canvas).
5. **No invented content**: Every page, visual, and field must trace back to the functional specification.
6. **Slicer definitions**: Include all required filters/slicers with their source fields.

#### Saving the Blueprint

The agent MUST:
1. **WRITE** the complete JSON to `<ProjectName>/spec/report_blueprint.json`.
2. **PRESENT** a summary of the blueprint to the user (page count, visual count per page, measures mapped).
3. **DO NOT** output the full JSON in chat — reference the saved file instead.

### 8.5 Validation Gate (STOP)
Before declaring Step 8 complete:
- [ ] `report_blueprint.json` has been saved to `<ProjectName>/spec/report_blueprint.json`
- [ ] Every measure/field referenced exists in the Visual Design Field Registry
- [ ] Report pages/visuals match the spec (no invented extra pages)
- [ ] Interactions are defined (or explicitly "default interactions")
- [ ] Accessibility and performance considerations are stated

Present a summary of the saved blueprint and **STOP here**. Await user approval before proceeding to Step 9 (Report Implementation).

## Artifact Checkpointing (MANDATORY)

**BEFORE presenting results to the user**, the agent MUST:

1. **SAVE** the report design blueprint to `<ProjectName>/spec/report_blueprint.json`.
2. **UPDATE** `<ProjectName>/workflow_state.json`:
   - Set `pendingStep` to Step 08 completed.
   - Add artifact path `<ProjectName>/spec/report_blueprint.json`.
3. **CONFIRM** to the user that the blueprint file has been saved.

## Context Flushing Rule

When starting this step, the agent MUST:
- **READ** `<ProjectName>/workflow_state.json` to verify Steps 01-07 are completed.
- **READ** the functional specification from disk.
- **READ** TMDL files from disk for the Visual Design Field Registry.
- **DO NOT** rely on chat history for any data from previous steps.

## Reference (load only if needed)
- `.github/references/report-design-visualization-best-practices.md`