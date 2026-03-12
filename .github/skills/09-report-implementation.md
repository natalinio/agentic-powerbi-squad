---
name: powerbi-report-implementation
description: Generate PBIR pages and visuals from blueprint with schema-safe mappings.
---

# Skill: Report Implementation (PBIR Visual Generation)

## Purpose
Generate the physical Power BI Report (PBIR) files from the report design blueprint (`report_blueprint.json`) produced in Step 8. This step creates the actual page folders, `page.json` files, visual folders, and `visual.json` files inside the PBIP Report definition.

## Prerequisites — MANDATORY
Before starting report implementation:
1. ✅ Step 8 completed and approved — `<ProjectName>/spec/report_blueprint.json` exists on disk.
2. ✅ Semantic Model exists — `<ProjectName>/PBIP/<ProjectName>.SemanticModel/definition/` contains valid TMDL files.
3. ✅ PBIP Report scaffold exists — `<ProjectName>/PBIP/<ProjectName>.Report/definition/` folder exists (created in Step 00).
4. ✅ Empty-canvas report baseline is intact before adding visuals:
   - `definition/report.json` uses the current baseline schema and theme resources.
   - `definition/version.json` and `definition/pages/pages.json` exist.
   - At least one page folder exists and is referenced by `pages.json`.
   - `StaticResources/SharedResources/BaseThemes/CY25SU12.json` exists.
   - `<ProjectName>.Report/report.json` at report root does NOT exist.

## Context Flushing Rule

When starting this step, the agent MUST:
- **READ** `<ProjectName>/workflow_state.json` to verify Steps 01-08 are completed.
- **READ** `<ProjectName>/spec/report_blueprint.json` from disk (the primary input for this step).
- **READ** TMDL files from disk for exact table/column/measure names (anti-hallucination).
- **DO NOT** rely on chat history for any data from previous steps.

## Step Scope & I/O Gate Alignment (MANDATORY)

- This skill is step-scoped: execute it only for **Step 09**. Do NOT preload Step 10 validation logic except where strictly required for schema correctness.
- Input gate: verify Step 08 blueprint exists, is valid JSON, and all referenced fields are resolvable in TMDL.
- Output gate: before completion, verify generated page/visual files exist, are non-empty, and are persisted in `workflow_state.json`.

## References — MANDATORY
Before generating ANY PBIR JSON:
1. **READ** `.github/references/pbir-visual-templates.md` for validated visual JSON templates.
2. **READ** `.github/references/pbip-folder-structure.md` for correct folder hierarchy.
3. **VERIFY** all PBIR visual structures against the **official Microsoft documentation**:
   - **Primary reference**: https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report
   - **PBIR schema source**: `https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.5.0/schema.json`
4. If uncertain about any PBIR schema, use `microsoft_docs_search` MCP tool with queries like:
   - `"Power BI PBIR page definition schema"`
   - `"Power BI PBIR visual container schema"`
   - `"Power BI report definition JSON format"`
5. Use `microsoft_docs_fetch` for full documentation pages when search results are insufficient.

> **CRITICAL**: NEVER invent or guess PBIR JSON structures. Always validate against Microsoft official documentation or the template reference file. In the current baseline, `drillFilterOtherVisuals` belongs to `visual`, cards use `visualType: cardVisual` with `queryState.Data`, page navigation is governed by `definition/pages/pages.json`, and PBIR JSON must be written as UTF-8 without BOM.

## Anti-Hallucination Protocol

**CRITICAL**: PBIR JSON is verbose and deeply nested. The agent MUST NOT guess JSON structures.

1. **Use templates**: Every visual MUST be generated from a template in `.github/references/pbir-visual-templates.md`.
2. **Validate field names**: Every `Entity` and `Property` in visual queries MUST match exactly the TMDL table and column/measure names.
3. **No invented visuals**: Only generate visuals defined in `report_blueprint.json`.
4. **Schema compliance**: All JSON files MUST reference the correct Microsoft `$schema` URLs.
5. **Physical ID discipline**: Page and visual runtime ids used in PBIR folders and `name` properties MUST be generated explicitly and kept synchronized across all referencing files.
6. **Encoding discipline**: Write every generated PBIR JSON file as UTF-8 without BOM.

---

## Step 9 Procedure

### 9.1 Read Inputs

1. **READ** `<ProjectName>/spec/report_blueprint.json` — Parse the complete blueprint.
2. **READ** TMDL files — Build a Model Object Registry (same as Step 7, Step B.0):
   - All table names
   - All column names per table (PascalCase)
   - All measure names from `_Measures.tmdl` (natural language with spaces)
3. **CROSS-VALIDATE**: Verify that every field referenced in `report_blueprint.json` exists in the Model Object Registry. If any field is missing, **STOP** and report the discrepancy.

### 9.2 Clean Up Existing Report Pages

Before generating new pages:
1. **CHECK** if `<ProjectName>/PBIP/<ProjectName>.Report/definition/pages/` already contains page folders.
2. If the folder contains only the default `Page1/` from Step 00 initialization, **remove it** (it will be replaced by the blueprint pages).
3. If the folder contains pages from a previous Step 9 execution, ask the user whether to overwrite or skip.
4. **CHECK** `definition/pages/pages.json` before deletion or creation. Folder cleanup is invalid unless the metadata file is updated in the same operation.

### 9.3 Derive Physical PBIR IDs (MANDATORY)

The blueprint provides canonical logical identifiers for design intent. Step 09 must translate them into physical PBIR runtime ids.

For each page and visual:
1. Generate a runtime-safe id following the repository-safe baseline observed from Desktop output:
   - 20 lowercase alphanumeric characters
2. Keep a deterministic mapping:
   - `blueprint pageId` -> `pageRuntimeId`
   - `blueprint visualId` -> `visualRuntimeId`
3. Use the runtime id for:
   - page folder names
   - `page.json.name`
   - `pages/pages.json.pageOrder[]`
   - `pages/pages.json.activePageName`
   - visual folder names
   - `visual.json.name`

> **CRITICAL**: Do NOT use user-facing labels like `Page1`, `Page2`, or `visual_01` as final PBIR folder names. They are blueprint identifiers, not the physical PBIR object names.

### 9.4 Generate Page Folders and Files

For each page defined in `report_blueprint.json`:

#### A) Create Page Folder
```
<ProjectName>/PBIP/<ProjectName>.Report/definition/pages/<pageRuntimeId>/
```

Where `<pageRuntimeId>` is the generated PBIR runtime id for the page.

#### B) Create `page.json`

Use the page template from `.github/references/pbir-visual-templates.md`:

```json
{
   "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.0.0/schema.json",
   "name": "<pageRuntimeId>",
  "displayName": "<displayName from blueprint>",
   "displayOption": "FitToPage",
  "height": <height from blueprint>,
  "width": <width from blueprint>
}
```

> **CRITICAL**: The PBIR page schema `2.0.0` does NOT allow additional properties. Only use the 6 properties shown above. Do NOT add `ordinal` or any other custom property — Power BI Desktop enforces strict schema validation and rejects unknown properties with `AdditionalProperties` error.

**File location**: `<ProjectName>/PBIP/<ProjectName>.Report/definition/pages/<pageRuntimeId>/page.json`

#### C) Create `visuals/` Folder
```
<ProjectName>/PBIP/<ProjectName>.Report/definition/pages/<pageRuntimeId>/visuals/
```

#### D) Update `pages/pages.json`

Generate or update:

```json
{
   "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json",
   "pageOrder": ["<pageRuntimeId1>", "<pageRuntimeId2>"],
   "activePageName": "<firstPageRuntimeId>"
}
```

Guardrails:
- `pageOrder` must reflect blueprint navigation order.
- `activePageName` must point to a generated page.
- Page folders on disk and entries in `pageOrder` must match exactly.

### 9.5 Generate Visual Files

For each visual defined in a page's `visuals` array in the blueprint:

#### A) Create Visual Folder
```
<ProjectName>/PBIP/<ProjectName>.Report/definition/pages/<pageRuntimeId>/visuals/<visualRuntimeId>/
```

Where `<visualRuntimeId>` is the generated PBIR runtime id for the visual.

#### B) Create `visual.json`

1. **Identify the visual type** from the blueprint's `visualType` field.
2. **Look up the corresponding template** in `.github/references/pbir-visual-templates.md` (use the Visual Type Mapping table).
3. **Populate the template** with:
    - `name`: The `visualRuntimeId` generated for the visual.
    - `position`: Map `x`, `y`, `width`, `height` from the blueprint's `position` object. Set `z` and `tabOrder` as deterministic monotonic integers based on visual order. Do NOT assume that increments of `1000` are required.
   - **usability sizing guardrails**:
      - top-row dropdown slicers should default to about `width = 180`, `height = 64-66`
      - grouped KPI bands should default to about `height = 120`
      - gauges should default to a primary analytical tile size above `300 x 130`
      - azure maps and treemaps should default to large analytical surfaces and should not be compressed into small tiles
   - **operational token guardrails**:
      - consume `designSystem.pagePadding`, `visualGap`, `sectionGap`, `gridUnit`, and per-visual `renderTokens` from the blueprint when present
      - if tokens are absent, use repository-safe fallback defaults
      - treat overlap as forbidden unless a visual explicitly sets `renderTokens.allowOverlap = true`
   - `visual.visualType`: The PBIR visual type (from mapping table).
   - `visual.query.queryState`: Map measures and fields from the blueprint to the correct PBIR query structure:
       - **Card measures** → `Data` projections with `Measure` field type, `Entity` = `_Measures`.
          - **Grouped KPI band / multi-row card intent** → safe baseline is `cardVisual` with multiple `Data` projections.
       - **Table/Slicer values** → `Values` projections.
     - **Axis/Category fields** → `Category` projections with `Column` field type.
     - **Legend fields** → `Series` projections with `Column` field type.
       - **Combo chart** → `Y` (column values) + `Y2` (line values).
       - **Scatter chart** → `X`, `Y`, `Size`, optional `Series`.
       - **Gauge** → `Y`, `TargetValue`, optional `Tooltips`.
       - **Treemap** → `Group` plus `Values`.
       - **Azure Map** → `Category` plus `Size`; include validated object settings when using the repository baseline map behavior.
     - **Row fields (matrix)** → `Rows` projections.
     - **Column group fields (matrix)** → `Columns` projections.
    - `visual.drillFilterOtherVisuals`: set `true` as baseline behavior.
    - `filterConfig`: optional for handcrafted files; Desktop may generate it automatically on save.
      - `visual.query.sortDefinition`: generate explicitly whenever the blueprint defines `sortBy`.
   - `visual.objects.value.fontSize`: for grouped KPI bands and the current card baseline, set explicit `20D` unless a user-approved design token overrides it.
   - `visual.visualContainerObjects`: apply only the metadata needed by that visual family.
      - slicers: prefer `title` metadata plus `dropShadow` when container separation is required
      - gauge / azureMap: `dropShadow` is part of the observed stable baseline
      - treemap: do not force `title` or `dropShadow` if the canonical baseline does not require them

4. **Validate**: Ensure every `Entity` value matches a TMDL table name and every `Property` value matches a column or measure name.
5. **Validate folder/name contract**: Ensure visual folder name equals `visual.json.name`.
6. **Validate layout contract**: Ensure computed positions respect page bounds, token spacing, and non-overlap rules.

7. **Selection/Layer Metadata Naming (CONDITIONAL)**:
    - When the visual family uses `visualContainerObjects.title`, set `text.expr.Literal.Value` using this pattern:
       - `'<ComponentName> - <DataOrMetadataReference>'`
    - Examples:
       - `'Slicer - FiscalYear'`
       - `'Card - Sales Amount FYTD'`
       - `'Chart - Sales Amount vs Budget Amount by FiscalMonth'`
    - The label must be unique within the page and must help identify objects in the Selection pane for layer order/tab order management.

   - For slicers, it is acceptable and recommended to keep `show = false` while still populating the metadata title text.
   - Do NOT force a `title` block onto every visual family if the canonical baseline for that visual works without it.

**File location**: `<ProjectName>/PBIP/<ProjectName>.Report/definition/pages/<pageRuntimeId>/visuals/<visualRuntimeId>/visual.json`

### 9.6 Generate Slicer Visuals

For each slicer defined in a page's `slicers` array in the blueprint:

1. **Parse the field reference**: Extract table name and column name from `Table[Column]` syntax.
2. **Use the slicer template** from `.github/references/pbir-visual-templates.md`.
3. **Set slicer mode**: Map the blueprint's `type` to PBIR mode:
   - `dropdown` → `"Dropdown"`
   - `list` → `"List"`
   - `dateRange` → `"Between"`
4. **Generate a unique visual runtime id** for each slicer.
5. **Position slicers**: Place slicers at the top or left of the page (before data visuals).
6. **Observed guardrail**: include `active: true` on the slicer projection when using the current Desktop baseline pattern.
7. **Usability guardrail**: do not compress dropdown slicers below 64 px height in the standard top-row layout, otherwise the dropdown affordance can become visually cramped and hard to click.

### 9.7 Encoding and Serialization Guardrails (MANDATORY)

When writing PBIR files:
- use UTF-8 without BOM
- avoid shell or serializer defaults that prepend BOM bytes
- avoid rewriting unrelated report baseline files
- write JSON atomically where possible to prevent partial report corruption

Recommended validation:
- check that the first bytes of each generated JSON file are not `EF BB BF`
- verify JSON parses cleanly before ending the step

### 9.8 Apply Layout Tokens and Resolve Overlaps

Before writing the final PBIR files:
1. Read blueprint-level layout tokens when present.
2. Apply page padding and inter-visual gaps before finalizing positions.
3. Snap or normalize positions to the declared grid when required by the design system.
4. Detect rectangle overlap between all visual bounding boxes on the page.
5. If overlap is detected and `allowOverlap` is not explicitly enabled, reposition the later visual or stop with a blocking validation message.

Fallback defaults when tokens are absent:
- `pagePadding = 16`
- `visualGap = 16`
- `sectionGap = 24`
- `gridUnit = 8`

### 9.9 Update `report.json` (if needed)

If the blueprint specifies navigation bookmarks, themes, or other report-level settings, update:
```
<ProjectName>/PBIP/<ProjectName>.Report/definition/report.json
```

For basic reports, the existing `report.json` from Step 00 is sufficient.

> **CRITICAL**: During Step 9, do NOT downgrade or rewrite the Step 00 report baseline (`report.json`, `version.json`, `pages/pages.json`, page schema family, `StaticResources`) unless explicitly requested by the user and validated against a Desktop-generated reference.

---

## Error Handling

### Common Errors and Mitigations

1. **Field Not Found in TMDL**:
   - **Cause**: Blueprint references a field that doesn't exist in the semantic model.
   - **Action**: STOP. Report the exact field name and suggest corrections based on TMDL registry.

2. **Invalid Visual Type**:
   - **Cause**: Blueprint uses a visual type not in the mapping table.
   - **Action**: Use `microsoft_docs_search` to find the correct PBIR visual type name. If not found, STOP and ask the user.

3. **JSON Schema Validation**:
   - **Cause**: Generated JSON doesn't conform to Microsoft schema.
   - **Action**: Re-validate against templates. Use `microsoft_docs_fetch` to check official schema.

4. **Position Overlap**:
   - **Cause**: Multiple visuals have overlapping positions.
   - **Action**: Apply operational layout tokens, recompute spacing, and adjust positions to avoid overlap. Use the blueprint's position values as guidelines, but ensure no two visuals share the same pixel space unless overlap is explicitly allowed.

5. **Compressed Slicer / Unusable Dropdown**:
   - **Cause**: Slicer height too small for the chosen layout and visual chrome.
   - **Action**: Increase slicer height to the repository baseline range of `64-66 px` and revalidate alignment.

6. **Oversized KPI Callout**:
   - **Cause**: Default card value font too large for grouped KPI presentation.
   - **Action**: Set explicit `objects.value.fontSize = 20D` for the grouped KPI band baseline unless a validated design token specifies another size.

7. **Runtime Load Error (`visualContainers`)**:
   - **Cause**: Structurally valid files but unstable visual payload generated in bulk.
   - **Action**: Reset to empty visual canvas and reintroduce visuals incrementally (first slicer + card, then reopen Desktop, then next batch).

8. **Compressed Analytical Visual**:
   - **Cause**: Gauge, treemap, or map placed into a tile too small for legible rendering.
   - **Action**: Expand the visual to the minimum analytical surface implied by tokens or repository defaults; if page space is insufficient, stop and request a layout revision instead of forcing a crowded render.

---

## Validation Gate — MANDATORY

Before presenting results to the user, verify:

- [ ] All pages from `report_blueprint.json` have corresponding folders in `pages/`
- [ ] `definition/pages/pages.json` exists and includes every generated page runtime id in `pageOrder`
- [ ] `activePageName` references an existing generated page runtime id
- [ ] Each page folder contains a valid `page.json`
- [ ] Each page folder name matches `page.json.name`
- [ ] Each page has a `visuals/` folder with the correct number of visual subfolders
- [ ] Each visual folder contains a valid `visual.json`
- [ ] Each visual folder name matches `visual.json.name`
- [ ] All `Entity` references in visual queries match TMDL table names exactly
- [ ] All `Property` references match TMDL column/measure names exactly
- [ ] Visual types use correct PBIR type names (from mapping table)
- [ ] Slicer modes are valid PBIR slicer mode values
- [ ] No duplicate visual IDs within a page
- [ ] All JSON files reference the correct Microsoft `$schema` URLs
- [ ] All JSON files are encoded as UTF-8 without BOM
- [ ] Every visual requiring explicit ranking or ordering has `query.sortDefinition`
- [ ] Top-row dropdown slicers respect the minimum usable height baseline (`>= 64 px`)
- [ ] Grouped KPI bands use an explicit value font size baseline (`20D`) unless a validated design override exists
- [ ] Gauge visuals use canonical `Y` / `TargetValue` query buckets
- [ ] Treemap visuals use canonical `Group` / `Values` query buckets
- [ ] Azure Map visuals use canonical `Category` / `Size` query buckets and stable map object settings when the baseline behavior is required
- [ ] Visual positions respect page padding, spacing tokens, and no-overlap rules unless explicitly overridden

---

## Artifact Checkpointing (MANDATORY)

**BEFORE presenting results to the user**, the agent MUST:

1. **VERIFY** all page folders and visual files have been created.
2. **GENERATE** a summary listing:
   - Number of pages created
   - Number of visuals per page
   - List of field references used
3. **UPDATE** `<ProjectName>/workflow_state.json`:
   - Set `pendingStep` to Step 09 completed.
   - Add artifact paths for all generated page and visual files.
4. **CONFIRM** to the user that all PBIR files have been saved.

Present a summary of generated files and **STOP here**. Await user approval before proceeding to Step 10 (Report Quality Validation).

---

## Output Structure Example

After Step 9, the Report definition folder should look like:

```
<ProjectName>/PBIP/<ProjectName>.Report/definition/
├── report.json
├── version.json
└── pages/
    ├── Page1/
    │   ├── page.json
    │   └── visuals/
    │       ├── slicer_01/
    │       │   └── visual.json
    │       ├── visual_01/
    │       │   └── visual.json
    │       ├── visual_02/
    │       │   └── visual.json
    │       └── visual_03/
    │           └── visual.json
    └── Page2/
        ├── page.json
        └── visuals/
            ├── slicer_01/
            │   └── visual.json
            └── visual_01/
                └── visual.json
```

---

## References
- `.github/references/pbir-visual-templates.md` — Visual JSON templates (MANDATORY)
- `.github/references/pbip-folder-structure.md` — Folder structure reference
- `.github/references/report-design-visualization-best-practices.md` — Design best practices (load only if needed)
