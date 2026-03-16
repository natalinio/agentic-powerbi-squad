---
name: powerbi-report-design
description: Design report layout, storytelling, UX, and interactions and persist blueprint artifacts.
---

# Skill: Report Design (Layout, UX, Navigation)

## Purpose
Design the Power BI report experience (pages, layout, visuals, interactions, navigation) based on:
- the functional specification (`<ProjectName>/spec/*.md`), and
- the finalized semantic model (`<ProjectName>/PBIP/<ProjectName>.SemanticModel/definition/`).
- any user-validated visual baseline, such as screenshots, manually refined report pages, or design feedback captured during the workflow.

This step produces a **design blueprint** only. It does NOT implement PBIP report artifacts.

This step must convert requirements into a report that is:
- analytically clear,
- visually consistent,
- narratively intentional, and
- implementation-ready for Step 09.

## Context Window Management (CRITICAL)
- Load only the minimum needed inputs for this step: the spec + the semantic model object names.
- Use `.github/references/report-design-visualization-best-practices.md` when deriving chart choice, storytelling flow, spacing rules, sorting logic, container styling, cross-filtering rules, or accessibility checks.
- NEVER invent measure/field names: always read them from TMDL.
- If the user has manually refined one or more pages in Power BI Desktop, treat that validated visual grammar as authoritative unless it conflicts with the specification.

## Step Contract

> Governance: `.github/references/workflow-core.md` — context flushing, checkpointing, and stop/approval gate apply automatically.

| | |
|---|---|
| **Reads** | `workflow_state.json` (verify Steps 01-07 completed), functional spec, all TMDL files (visual field registry) |
| **Writes** | `<ProjectName>/spec/report_blueprint.json` |

## Prerequisites — MANDATORY
Before starting report design:
1. ✅ The semantic model exists and is valid (Steps 3–7 completed).
2. ✅ The specification describes report goals (audience, questions, KPIs, navigation expectations). If missing, ask targeted questions and STOP.
3. ✅ Model introspection is possible by reading TMDL files.
4. ✅ Any user-approved visual conventions discovered during the workflow are captured as design constraints for this step.

> **Official Reference**: When designing pages and visual layouts, refer to the Microsoft official PBIR documentation for valid properties and schema constraints: https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report

## Step 8 Procedure

### 8.1 Inputs to Read
1. Functional spec: `<ProjectName>/spec/<spec>.md`
2. Semantic model TMDL:
   - `<ProjectName>/PBIP/<ProjectName>.SemanticModel/definition/model.tmdl`
   - `<ProjectName>/PBIP/<ProjectName>.SemanticModel/definition/tables/*.tmdl`
   - `<ProjectName>/PBIP/<ProjectName>.SemanticModel/definition/relationships.tmdl`
3. Workflow evidence from previous approved steps, if relevant:
  - `<ProjectName>/workflow_state.json`
  - Step 07 test outputs
4. User-provided design evidence, if available:
  - screenshots
  - manual page reconstructions in Power BI Desktop
  - explicit UX feedback captured in chat or state

### 8.2 Build a Visual Design Field Registry (MANDATORY)
Create an internal registry of report-usable objects by reading TMDL (same anti-hallucination principle as Step 7):
- **Measures**: from `_Measures.tmdl` (exact display names)
- **Date table**: confirm the Date table and main Date column
- **Dimensions**: user-facing attributes (prefer non-hidden descriptive columns)
- **Facts**: avoid exposing technical keys; prefer measures
- **Field parameters**: detect disconnected calculated tables that expose dynamic-switch semantics and record their visible column, hidden metadata column, and allowed target fields

**CRITICAL RULES**:
- NEVER guess object names.
- If the spec uses business labels that don't map 1:1 to model objects, ask clarifying questions and STOP.

### 8.3 Build the Storyboard Before the Layout (MANDATORY)
Before placing any visual on a page, define the narrative skeleton for each page:
- **Audience**: who consumes the page
- **Business question**: what question the page answers
- **Key takeaway**: the one message the user should retain
- **Evidence flow**: KPI summary -> supporting trend/comparison -> detail/ranking
- **Expected action**: what decision or follow-up the page should support

Each page in the blueprint must answer a specific business question. A page without a clear question or takeaway is invalid.

Default storytelling flow:
1. Controls first: slicers and navigation
2. Hero insight second: top KPI band
3. Explanatory evidence third: trends, comparisons, relationships
4. Detail last: ranked tables or drill paths

### 8.4 Define a Page-Level Design System (MANDATORY)
Before generating page visuals, define reusable design tokens and layout rules that Step 09 can implement consistently.

The design system must include:
- **Grid discipline**: use an 8 px grid or consistent multiples of it
- **Whitespace policy**:
  - minimum gap between sibling visuals: 16 px
  - recommended gap between visual sections: 24 px
  - page edge breathing space: 16 px minimum
- **Container separation**: visuals must be visually distinct from the canvas using elevated cards, shadowing, border contrast, or another explicit container treatment
- **Alignment policy**: slicers aligned on a common row, KPI containers aligned on a common baseline, analytic visuals aligned by section
- **Visual hierarchy**: top-left and top band reserved for the highest-value information
- **Title policy**: action-oriented, unambiguous titles that state measure + comparison/breakdown
- **Sorting policy**: all charts and tables must have explicit sorting logic

#### Mandatory design decisions

**Slicers**
- Place primary slicers on a dedicated top row whenever space allows.
- Use consistent width, height, alignment, and container treatment.
- Prefer dropdown slicers for dense categorical filters.
- If a slicer controls a field parameter, treat it as an interaction control rather than a business filter and map its downstream target roles explicitly in the blueprint.
- If a slicer controls a **measure parameter**, explicitly constrain the companion dimensions used in the visual to ones that remain meaningful for every selectable measure.

**KPI presentation**
- Use a **single card** when one metric is the dominant headline insight.
- Use a **multi-row card** when the requirement is to show multiple heterogeneous KPIs in the same narrative band and equal emphasis is acceptable.
- Use separated KPI cards only when each KPI needs standalone emphasis, distinct thresholds, or clearly different semantic meaning.

**Tables**
- Tables must serve a specific detail or ranking purpose.
- Every table must define:
  - primary KPI used for sorting,
  - sort direction,
  - reason for the ordering.
- Default sort for leaderboard/ranking tables is **descending by the primary KPI**.
- Use ascending sort only when the business question explicitly targets low performers, earliest values, or another exception.

**Chart clutter**
- Remove non-essential labels, borders, legends, and gridlines when they do not add meaning.
- Prefer tooltips for secondary details instead of overcrowding the canvas.

### 8.5 Derive Report Information Architecture
From the spec and storyboard, define:
- Primary KPIs (what must be seen immediately)
- Supporting analysis (trends, comparisons, drivers, relationships)
- Detail and ranking content
- Tertiary controls (slicers, navigation, bookmarks, drillthrough)

Default to the simplest structure that satisfies the spec:
- If the spec is summary-only → single-page layout.
- If the spec includes drill-down needs → summary page + detail page.

Default page grammar:
- top filter band
- KPI band
- explanatory chart zone
- detail/ranking zone

### 8.6 Produce the Report Design Blueprint (OUTPUT)

The agent MUST generate and save the report design blueprint as a **physical JSON file** at `<ProjectName>/spec/report_blueprint.json`. This file will be the input for Step 9 (Report Implementation). Only AFTER saving the file, the agent must present a summary and stop for approval.

#### JSON Schema for `report_blueprint.json`

```json
{
  "$schema": "report_blueprint_schema",
  "projectName": "<ProjectName>",
  "generatedDate": "<ISO 8601 timestamp>",
  "semanticModelPath": "<ProjectName>/PBIP/<ProjectName>.SemanticModel/definition/",
  "storytelling": {
    "narrativePattern": "callToActionLoop",
    "audienceNotes": [],
    "globalDesignConstraints": []
  },
  "designSystem": {
    "gridUnit": 8,
    "pagePadding": 16,
    "visualGap": 16,
    "sectionGap": 24,
    "containerStyle": {
      "mode": "elevated",
      "shadow": true,
      "border": false
    },
    "slicerStyle": {
      "placement": "top-row",
      "container": "elevated",
      "alignment": "consistent"
    },
    "kpiStyle": {
      "preferMultiRowCardForGroupedHeterogeneousKpis": true,
      "singleCardReservedForHeroMetric": true
    },
    "tableStyle": {
      "requireExplicitSort": true,
      "defaultRankingDirection": "descending"
    }
  },
  "pages": [
    {
      "pageId": "Page1",
      "pageName": "Overview",
      "displayName": "Sales Overview",
      "goal": "Provide a summary of key sales KPIs and trends",
      "targetAudience": "Sales Manager",
      "storyCard": {
        "businessQuestion": "Are we on track against budget and where should the manager investigate first?",
        "keyMessage": "Budget variance is negative while FYTD sales remain concentrated in a subset of areas.",
        "expectedAction": "Inspect area-level variance and profitability drivers."
      },
      "width": 1280,
      "height": 720,
      "displayOption": "FitToWidth",
      "slicers": [
        {
          "field": "Dim_Date[FiscalYear]",
          "type": "dropdown",
          "label": "Fiscal Year",
          "containerStyle": "elevated",
          "position": {
            "x": 16,
            "y": 16,
            "width": 180,
            "height": 64
          }
        }
      ],
      "visuals": [
        {
          "visualId": "visual_01",
          "visualType": "multiRowCard",
          "title": "Total Sales FYTD",
          "measures": ["Sales Amount FYTD"],
          "axisFields": [],
          "legendField": null,
          "narrativeRole": "hero-kpi",
          "containerStyle": "elevated",
          "sortBy": null,
          "defaultGranularity": null,
          "tooltip": null,
          "drillthrough": null,
          "position": {
            "x": 16,
            "y": 96,
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
4. **Positions**: Provide approximate `x`, `y`, `width`, `height` values for visual layout (based on 1280x720 canvas) and keep consistent spacing.
5. **No invented content**: Every page, visual, and field must trace back to the functional specification.
6. **Slicer definitions**: Include all required filters/slicers with their source fields.
7. **Field parameter definitions**: If dynamic switching is required, represent it explicitly in the blueprint with the parameter table, visible parameter column, target visual(s), target role(s), and optional default selection.
8. **Context compatibility**: If a measure parameter is used, declare the allowed context dimensions for the visual and reject dimension choices that are not consistently related to every selectable measure through the active model relationships.
9. **Narrative metadata**: Every page must define the business question, key message, and expected action.
10. **Container treatment**: Every slicer, KPI band, and analysis visual must declare a container style or explicitly opt out with a reason.
11. **Sorting metadata**: Every sortable chart or table must define `sortBy`, including field and direction.
12. **KPI grouping rationale**: If a page shows multiple KPIs in one zone, choose between `card` and `multiRowCard` explicitly and record the reason.

Recommended blueprint extension for field parameters:

```json
{
  "visualId": "visual_02",
  "visualType": "tableEx",
  "fieldParameterBindings": [
    {
      "parameterTable": "Measure",
      "parameterColumn": "Measure",
      "targetRole": "Values",
      "defaultSelection": "Sales Amount FYTD",
      "allowedContextDimensions": ["Dim_Area[AreaName]"]
    }
  ]
}
```

#### Saving the Blueprint

The agent MUST:
1. **WRITE** the complete JSON to `<ProjectName>/spec/report_blueprint.json`.
2. **PRESENT** a summary of the blueprint to the user (page count, visual count per page, measures mapped).
3. **DO NOT** output the full JSON in chat — reference the saved file instead.

### 8.7 Validation Gate (STOP)
Before declaring Step 8 complete:
- [ ] `report_blueprint.json` has been saved to `<ProjectName>/spec/report_blueprint.json`
- [ ] Every measure/field referenced exists in the Visual Design Field Registry
- [ ] Report pages/visuals match the spec (no invented extra pages)
- [ ] Interactions are defined (or explicitly "default interactions")
- [ ] Accessibility and performance considerations are stated
- [ ] Every page has a business question, key takeaway, and expected action
- [ ] Spacing and container rules are consistent across pages
- [ ] Slicers are positioned and styled consistently unless a page-specific exception is justified
- [ ] Field parameter controls are distinguished from ordinary filters and include explicit target-role bindings
- [ ] Measure-parameter visuals declare relationship-safe context dimensions for all selectable measures
- [ ] Every table/chart with sortable categories has explicit sorting metadata
- [ ] KPI zones explicitly justify `card` vs `multiRowCard`

Present a summary of the saved blueprint and **STOP here**. Await user approval before proceeding to Step 9 (Report Implementation).

**STOP. Save primary artifact → update `workflow_state.json` → await user approval.**

## Reference (load only if needed)
- `.github/references/report-design-visualization-best-practices.md`