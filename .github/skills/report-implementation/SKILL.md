---
name: report-implementation
description: >-
  Use when generating physical PBIR JSON files (pages, visuals) from a report blueprint.
  Triggers: "implement PBIR", "generate visual JSON", "create page.json", "visual binding",
  "PBIR template", "implement report from blueprint", "add visual to page",
  "visual.json structure", "report.json", "pages.json".
user-invocable: true
---

# Skill: Report Implementation (PBIR Visual Generation)

## Purpose
Generate the physical Power BI Report (PBIR) files from the report design blueprint (`report_blueprint.json`) produced in Step 8. This step creates the actual page folders, `page.json` files, visual folders, and `visual.json` files inside the PBIP Report definition.

This step must implement the strategy already decided in the blueprint. It must not silently redesign mockup translation decisions or feasibility constraints.

## Prerequisites — MANDATORY
Before starting report implementation:
1. ✅ Step 8 completed and approved — `<ProjectName>/spec/report_blueprint.json` exists on disk.
2. ✅ Semantic Model exists — `<ProjectName>/PBIP/<ProjectName>.SemanticModel/definition/` contains valid TMDL files.
3. ✅ PBIP Report scaffold exists — `<ProjectName>/PBIP/<ProjectName>.Report/definition/` folder exists (created in Step 00).
4. ✅ Empty-canvas report baseline is intact before adding visuals:
   - `definition/report.json` uses the current baseline schema and theme resources.
   - `definition/version.json` and `definition/pages/pages.json` exist.
   - At least one page folder exists and is referenced by `pages.json`.
   - `StaticResources/SharedResources/BaseThemes/ProjectDefault.json` exists.
   - `<ProjectName>.Report/report.json` at report root does NOT exist.

## Input / Output

| | |
|---|---|
| **Input** | `<ProjectName>/spec/report_blueprint.json`, all TMDL files (model object registry) |
| **Output** | PBIR files in `<ProjectName>/PBIP/<ProjectName>.Report/definition/pages/` + updated `pages/pages.json` |

## References — MANDATORY
Before generating ANY PBIR JSON:
1. **READ** `.github/skills/report-implementation/references/pbir-visual-templates.md` for validated visual JSON templates.
2. **READ** `.github/references/pbip-folder-structure.md` for correct folder hierarchy.
3. **READ** `.github/references/pbir-cli-integration.md` before using the local `pbir` CLI for any packaged report operation.
3. **READ on demand** (load only when needed for the specific task):
   - `references/fields-and-bindings.md` — Field types (Column/Measure/Extension), data roles by visual type, queryState structure
   - `references/filters.md` — Filter types (Categorical, TopN, Advanced, RelativeDate), scope, JSON structure
   - `references/conditional-formatting.md` — CF types, container.property mapping, measure-driven patterns
   - `references/extension-measures.md` — reportExtensions.json structure, common patterns, DAX verification
   - `references/visual-formatting-properties.md` — Universal containers, property catalogue, formatting hierarchy
4. **VERIFY** all PBIR visual structures against the **official Microsoft documentation**:
   - **Primary reference**: https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report
   - **PBIR schema source**: `https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.5.0/schema.json`
4. If uncertain about any PBIR schema, use `microsoft_docs_search` MCP tool with queries like:
   - `"Power BI PBIR page definition schema"`
   - `"Power BI PBIR visual container schema"`
   - `"Power BI report definition JSON format"`
5. Use `microsoft_docs_fetch` for full documentation pages when search results are insufficient.
6. If the step uncovers a **new reusable PBIR rule** about schema, folder structure, serialization, payload stability, or visual-role mapping, **update the relevant reference file** before ending the step. Do not leave recurring guidance only in chat output.

## PBIR CLI Mutation Policy (Mandatory for Existing Artifacts)

When the local `pbir` CLI is available, this skill must use it as the mutation backend for existing local PBIR report artifacts.

Use it for:
- report inspection: `pbir ls`, `pbir tree`, `pbir model`, `pbir get`, `pbir cat`
- schema/property discovery: `pbir schema types`, `pbir schema containers`, `pbir schema describe`
- targeted local edits: `pbir add`, `pbir pages`, `pbir visuals`, `pbir set`, `pbir fields`, `pbir filters`, `pbir dax`, `pbir theme`
- local safety loop: `pbir backup`, `pbir validate`, `pbir open`

Rules:
1. Do **NOT** run `pbir setup` from this skill.
2. Do **NOT** let CLI behavior replace blueprint-driven design or repository templates.
3. Use the CLI for existing-report mutations that map cleanly to the requested change.
4. Before any CLI read or write command, clear or replace any existing active `pbir` connection and reconnect it to the current project report under `<ProjectName>/PBIP/<PbipBaseName>.Report`.
5. Never assume the active `pbir` session already points to the current project; verify with `pbir connect` or reconnect explicitly.
6. Before bulk or structurally risky commands, run `pbir backup`.
7. After every CLI mutation, run `pbir validate` (prefer `--all` when available), then still satisfy the repository validation gate below.
8. If the CLI is unavailable or unsupported for a requested mutation, stop and request explicit approval before falling back to direct JSON edits.
9. Do not use `pbir download` or `pbir publish` in Step 9 unless the user explicitly requests Fabric-edge operations.

Direct JSON edit prohibition (existing artifacts):
- Do not hand-edit `visual.json`, `page.json`, `pages.json`, or theme JSON for routine report mutations.
- Use CLI commands (`pbir set`, `pbir visuals`, `pbir fields`, `pbir filters`, `pbir theme`) as the default path.
- If fallback is approved, record rationale and run dual validation before completion.

### Mandatory Implementation Safety Gate

Before marking implementation complete, run this exact sequence:

```powershell
pbir connect --clear
pbir connect "<PbipBaseName>.Report"
pbir validate "<PbipBaseName>.Report" --all
python .github/skills/report-quality-validation/scripts/validate_pbir_report.py <ProjectName>
```

Gate rules:
- If either validation fails, implementation is NOT complete.
- Fix errors first, rerun both commands, then update workflow state.
- Treat Desktop `AdditionalProperties` failures as schema-blocking defects.

Schema red flags to check explicitly:
- `visualContainerObjects` must be inside `visual`.
- `drillFilterOtherVisuals` must be inside `visual`.
- Visual filters must be in top-level `filterConfig.filters`, never in `visual.filters`.
- Top-level keys in `visual.json` must stay within the schema surface (`$schema`, `name`, `position`, `visual|visualGroup`, optional `filterConfig`).

### Canonical `pbir` Command Patterns

Use these examples only when they match the requested local report task.

1. Inspect an existing report before edits:

```powershell
pbir connect --clear
pbir connect "Sales.Report"
pbir tree "Sales.Report" -v
pbir model "Sales.Report" -d
```

2. Create a backup before risky local changes:

```powershell
pbir connect --clear
pbir connect "Sales.Report"
pbir backup "Sales.Report" -m "Before report implementation changes"
```

3. Add a native visual with explicit binding:

```powershell
pbir connect --clear
pbir connect "Sales.Report"
pbir add visual card "Sales.Report/Overview.Page" --title "Revenue" -d "Values:Sales.Revenue"
```

4. Apply a narrow formatting or layout change:

```powershell
pbir connect --clear
pbir connect "Sales.Report"
pbir visuals title "Sales.Report/Overview.Page/Revenue.Visual" --text "Net Revenue" --bold
pbir visuals position "Sales.Report/Overview.Page/Revenue.Visual" --x 40 --y 32 --width 260 --height 120
```

5. Apply a safe theme-first formatting change:

```powershell
pbir connect --clear
pbir connect "Sales.Report"
pbir theme set-colors "Sales.Report" --primary "#2B579A" --secondary "#217346"
pbir theme set-formatting "Sales.Report" "card.*.border.show" --value true
```

6. Validate after mutation:

```powershell
pbir connect --clear
pbir connect "Sales.Report"
pbir validate "Sales.Report"
```

Fallback:
- if any of these commands cannot express the blueprint requirement cleanly, return to the repository templates and direct file generation flow
- if a command requires broader destructive scope than requested, stop and keep the change in the repository-managed workflow instead
- if `pbir cat` fails with a packaged runtime error but `pbir ls` or `pbir get` still work, treat `cat` as unavailable for the current environment and continue with repository-managed file inspection instead of blocking Step 9

> **CRITICAL**: NEVER invent or guess PBIR JSON structures. Always validate against Microsoft official documentation or the template reference file. In the current baseline, `drillFilterOtherVisuals` belongs to `visual`, cards use `visualType: cardVisual` with `queryState.Data`, page navigation is governed by `definition/pages/pages.json`, and PBIR JSON must be written as UTF-8 without BOM.

> **CRITICAL**: Schema lookup findings belong in repository knowledge, not in ad-hoc local scratch files. Temporary inspection artifacts may be used while working, but any durable conclusion must be normalized into a reference file and temporary files must not remain as project artifacts.

## Anti-Hallucination Protocol

**CRITICAL**: PBIR JSON is verbose and deeply nested. The agent MUST NOT guess JSON structures.

1. **Use templates**: Every visual MUST be generated from a template in `.github/skills/report-implementation/references/pbir-visual-templates.md`.
2. **Validate field names**: Every `Entity` and `Property` in visual queries MUST match exactly the TMDL table and column/measure names.
3. **No invented visuals**: Only generate visuals defined in `report_blueprint.json`.
4. **Schema compliance**: All JSON files MUST reference the correct Microsoft `$schema` URLs.
5. **Physical ID discipline**: Page and visual runtime ids used in PBIR folders and `name` properties MUST be generated explicitly and kept synchronized across all referencing files.
6. **Encoding discipline**: Write every generated PBIR JSON file as UTF-8 without BOM.
7. **Knowledge-base discipline**: If a new rule is discovered that is not specific to the current report, persist it in the corresponding reference before closing the step.

---

## Step 9 Procedure

### 9.1 Read Inputs

1. **READ** `<ProjectName>/spec/report_blueprint.json` — Parse the complete blueprint.
2. **READ** TMDL files — Build a Model Object Registry (same as Step 7, Step B.0):
   - All table names
   - All column names per table (PascalCase)
   - All measure names from `_Measures.tmdl` (natural language with spaces)
3. **CROSS-VALIDATE**: Verify that every field referenced in `report_blueprint.json` exists in the Model Object Registry. If any field is missing, **STOP** and report the discrepancy.
4. **READ strategy metadata**: If a visual declares `implementationStrategy`, honor the selected mode (`native`, `composite-native`, `svg`, `deneb`, `approximation`, `not-feasible`) during generation.
5. **LOAD custom-visual skills on demand**:
   - If `implementationStrategy.mode = svg`, load the `svg-visuals` skill before implementation.
   - If `implementationStrategy.mode = deneb`, load the `deneb-visuals` skill before implementation.
   - If `implementationStrategy.mode = approximation`, implement only the documented approximation. Do not invent a new strategy.
   - If `implementationStrategy.mode = not-feasible`, STOP and report the blueprint conflict instead of generating a fake equivalent.

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

Use the page template from `.github/skills/report-implementation/references/pbir-visual-templates.md`:

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
2. **Look up the corresponding template** in `.github/skills/report-implementation/references/pbir-visual-templates.md` (use the Visual Type Mapping table).
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
      - **Scatter chart** → `X`, `Y`, optional `Size`. For **colored bubbles by category**, place the categorical field in `Series` (Legend). For **distinct unlabeled points**, use `Details` (Values). At least one of `Series` or `Details` must carry a categorical field.
       - **Gauge** → `Y`, `TargetValue`, optional `Tooltips`.
       - **Treemap** → `Group` plus `Values`.
       - **Azure Map** → `Category` plus `Size`; include validated object settings when using the repository baseline map behavior.
     - **Row fields (matrix)** → `Rows` projections.
     - **Column group fields (matrix)** → `Columns` projections.
      - **Field parameter bindings** → keep the active concrete projection for the target role and also emit `queryState.<Role>.fieldParameters[]` referencing the parameter display column.
      - **Measure parameter on `Values`** → keep any companion grouping dimensions only if they are valid filter context for all selectable measures.
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
7. **Validate field-parameter contract**: When a blueprint visual declares `fieldParameterBindings`, ensure the consuming PBIR role contains both the concrete projection and the matching `fieldParameters` descriptor.
8. **Validate context compatibility**: When a blueprint visual declares a measure parameter, ensure any non-parameter grouping fields are present in `allowedContextDimensions` and are reachable from every selectable measure through the active relationships.
9. **Validate reference coverage**: If the chosen visual family or payload pattern is not already represented in the PBIR references, add the generalized rule or stop and capture a Desktop-generated reference before continuing.
10. **Validate scatter grouping**: A scatter visual must have at least one categorical field in `queryState.Series` (Legend — colored bubbles) or `queryState.Details` (Values — point identity). Use `Series` when the design requires color-coded bubbles per category. If neither role contains a categorical field, the visual collapses to a single point.
11. **Validate unique nativeQueryRef**: When the same measure is placed in multiple query-state roles within the same visual, each projection must have a distinct `nativeQueryRef`. Duplicate values cause a Desktop runtime error. Append a disambiguating suffix such as `(Size)` or `(Tooltip)` to the secondary occurrence.
12. **Validate strategy alignment**: The generated PBIR payload must remain compatible with the blueprint's `implementationStrategy`. If the implementation requires a different mode than the one declared in the blueprint, STOP and send the issue back to report design rather than silently switching strategy.

9. **Selection/Layer Metadata Naming (CONDITIONAL)**:
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
2. **Use the slicer template** from `.github/skills/report-implementation/references/pbir-visual-templates.md`.
3. **Set slicer mode**: Map the blueprint's `type` to PBIR mode:
   - `dropdown` → `"Dropdown"`
   - `list` → `"List"`
   - `dateRange` → `"Between"`
4. **Generate a unique visual runtime id** for each slicer.
5. **Position slicers**: Place slicers at the top or left of the page (before data visuals).
6. **Observed guardrail**: include `active: true` on the slicer projection when using the current Desktop baseline pattern.
7. **Usability guardrail**: do not compress dropdown slicers below 64 px height in the standard top-row layout, otherwise the dropdown affordance can become visually cramped and hard to click.

If the slicer is bound to a field parameter:
- Bind the slicer projection to the **visible parameter column** (for example `Dimension[Dimension]`).
- If the blueprint declares a default selection, emit the Desktop-observed `visual.objects.general[].properties.filter` payload against the hidden object-reference column (for example `Dimension[Dimension Fields]`) using the corresponding `NAMEOF(...)` literal value.
- Keep the slicer metadata title readable, because field-parameter slicers behave like report controls and are harder to identify later in the Selection pane.

### 9.7 Encoding and Serialization Guardrails (MANDATORY)

When writing PBIR files:
- use UTF-8 without BOM
- avoid shell or serializer defaults that prepend BOM bytes
- avoid rewriting unrelated report baseline files
- write JSON atomically where possible to prevent partial report corruption

Recommended validation:
- check that the first bytes of each generated JSON file are not `EF BB BF`
- verify JSON parses cleanly before ending the step
- convert any generalized lesson from this validation into `.github/skills/report-implementation/references/pbir-visual-templates.md` or `.github/references/pbip-folder-structure.md`

#### PowerShell BOM Warning (CRITICAL)
When using PowerShell to write JSON files, `[System.Text.Encoding]::UTF8` produces UTF-8 WITH BOM.
Power BI Desktop rejects BOM-prefixed PBIR files with: "Only text with UTF8 encoding without BOM is supported."

**Always use the BOM-free encoder:**
```powershell
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($path, $content, $utf8NoBom)
```

Never use: `[System.IO.File]::WriteAllText($path, $content, [System.Text.Encoding]::UTF8)`

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

9. **Strategy Mismatch**:
   - **Cause**: Blueprint declares `native` or `composite-native`, but implementation would require `svg` or `deneb` to preserve the intended behavior.
   - **Action**: STOP. Report the mismatch and require a blueprint update instead of silently changing the implementation mode.

10. **BOM in PBIR JSON files**:
    - **Cause**: PowerShell System.Text.Encoding.UTF8 writes UTF-8 with BOM by default.
    - **Error**: "Only text with UTF8 encoding without BOM (byte order marks) is supported. Detected BOM: 'UTF-8'"
    - **Action**: Use New-Object System.Text.UTF8Encoding $false as the encoder for all file writes. Run a post-write BOM scan: check first 3 bytes for  xEF 0xBB 0xBF.

11. **Page background not visible**:
    - **Cause**: PBIR eport.json /objects does not support ackground or wallpaper properties.
    - **Action**: Use a asicShape visual at z=0, x=0, y=0, width=pageWidth, height=pageHeight with the desired fill color. Set drillFilterOtherVisuals: false on this visual.

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
- [ ] Visuals that declare field parameter bindings also serialize `queryState.<Role>.fieldParameters[]` correctly
- [ ] Field-parameter slicers bind to the visible parameter column and use the hidden metadata column only for explicit default selection filters
- [ ] Measure-parameter visuals use only relationship-safe context dimensions declared in the blueprint
- [ ] No duplicate visual IDs within a page
- [ ] All JSON files reference the correct Microsoft `$schema` URLs
- [ ] All JSON files are encoded as UTF-8 without BOM
- [ ] Every visual requiring explicit ranking or ordering has `query.sortDefinition`
- [ ] Every visual with `implementationStrategy` is implemented with the declared strategy mode or an explicitly approved equivalent
- [ ] Top-row dropdown slicers respect the minimum usable height baseline (`>= 64 px`)
- [ ] Grouped KPI bands use an explicit value font size baseline (`20D`) unless a validated design override exists
- [ ] Gauge visuals use canonical `Y` / `TargetValue` query buckets
- [ ] Treemap visuals use canonical `Group` / `Values` query buckets
- [ ] Azure Map visuals use canonical `Category` / `Size` query buckets and stable map object settings when the baseline behavior is required
- [ ] Visual positions respect page padding, spacing tokens, and no-overlap rules unless explicitly overridden

---

Save all generated PBIR artifacts to disk.

---

## Output Structure Example

The Report definition folder should look like:

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

| Reference | Path | Load |
|---|---|---|
| Visual JSON Templates | `references/pbir-visual-templates.md` | MANDATORY — always load |
| Fields and Bindings | `references/fields-and-bindings.md` | On demand — field types, data roles, queryState |
| Filters | `references/filters.md` | On demand — filter types and JSON structure |
| Conditional Formatting | `references/conditional-formatting.md` | On demand — CF types, container mappings |
| Extension Measures | `references/extension-measures.md` | On demand — reportExtensions.json patterns |
| Visual Formatting Properties | `references/visual-formatting-properties.md` | On demand — containers, property catalogue |
| Folder Structure | `.github/references/pbip-folder-structure.md` | MANDATORY — folder hierarchy |
| Design Best Practices | `.github/skills/report-design/references/report-design-visualization-best-practices.md` | On demand |
