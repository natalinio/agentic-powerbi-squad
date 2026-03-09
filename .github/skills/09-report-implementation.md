# Skill: Report Implementation (PBIR Visual Generation)

## Purpose
Generate the physical Power BI Report (PBIR) files from the report design blueprint (`report_blueprint.json`) produced in Step 8. This step creates the actual page folders, `page.json` files, visual folders, and `visual.json` files inside the PBIP Report definition.

## Prerequisites — MANDATORY
Before starting report implementation:
1. ✅ Step 8 completed and approved — `<ProjectName>/spec/report_blueprint.json` exists on disk.
2. ✅ Semantic Model exists — `<ProjectName>/PBIP/<ProjectName>.SemanticModel/definition/` contains valid TMDL files.
3. ✅ PBIP Report scaffold exists — `<ProjectName>/PBIP/<ProjectName>.Report/definition/` folder exists (created in Step 00).

## Context Flushing Rule

When starting this step, the agent MUST:
- **READ** `<ProjectName>/workflow_state.json` to verify Steps 01-08 are completed.
- **READ** `<ProjectName>/spec/report_blueprint.json` from disk (the primary input for this step).
- **READ** TMDL files from disk for exact table/column/measure names (anti-hallucination).
- **DO NOT** rely on chat history for any data from previous steps.

## References — MANDATORY
Before generating ANY PBIR JSON:
1. **READ** `.github/references/pbir-visual-templates.md` for validated visual JSON templates.
2. **READ** `.github/references/pbip-folder-structure.md` for correct folder hierarchy.
3. If uncertain about any PBIR schema, use `microsoft_docs_search` MCP tool with queries like:
   - `"Power BI PBIR page definition schema"`
   - `"Power BI PBIR visual container schema"`
   - `"Power BI report definition JSON format"`
4. Use `microsoft_docs_fetch` for full documentation pages when search results are insufficient.

## Anti-Hallucination Protocol

**CRITICAL**: PBIR JSON is verbose and deeply nested. The agent MUST NOT guess JSON structures.

1. **Use templates**: Every visual MUST be generated from a template in `.github/references/pbir-visual-templates.md`.
2. **Validate field names**: Every `Entity` and `Property` in visual queries MUST match exactly the TMDL table and column/measure names.
3. **No invented visuals**: Only generate visuals defined in `report_blueprint.json`.
4. **Schema compliance**: All JSON files MUST reference the correct Microsoft `$schema` URLs.

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

### 9.3 Generate Page Folders and Files

For each page defined in `report_blueprint.json`:

#### A) Create Page Folder
```
<ProjectName>/PBIP/<ProjectName>.Report/definition/pages/<pageId>/
```

Where `<pageId>` matches the `pageId` from the blueprint (e.g., `Page1`, `Page2`).

#### B) Create `page.json`

Use the page template from `.github/references/pbir-visual-templates.md`:

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/1.0.0/schema.json",
  "name": "<pageId>",
  "displayName": "<displayName from blueprint>",
  "displayOption": "<displayOption from blueprint>",
  "width": <width from blueprint>,
  "height": <height from blueprint>
}
```

**File location**: `<ProjectName>/PBIP/<ProjectName>.Report/definition/pages/<pageId>/page.json`

#### C) Create `visuals/` Folder
```
<ProjectName>/PBIP/<ProjectName>.Report/definition/pages/<pageId>/visuals/
```

### 9.4 Generate Visual Files

For each visual defined in a page's `visuals` array in the blueprint:

#### A) Create Visual Folder
```
<ProjectName>/PBIP/<ProjectName>.Report/definition/pages/<pageId>/visuals/<visualId>/
```

Where `<visualId>` matches the `visualId` from the blueprint (e.g., `visual_01`, `visual_02`).

#### B) Create `visual.json`

1. **Identify the visual type** from the blueprint's `visualType` field.
2. **Look up the corresponding template** in `.github/references/pbir-visual-templates.md` (use the Visual Type Mapping table).
3. **Populate the template** with:
   - `name`: The `visualId` from the blueprint.
   - `position`: Map `x`, `y`, `width`, `height` from the blueprint's `position` object. Set `z` based on visual order (increment by 1000 for each visual). Set `tabOrder` to the visual's index.
   - `visual.visualType`: The PBIR visual type (from mapping table).
   - `visual.query.queryState`: Map measures and fields from the blueprint to the correct PBIR query structure:
     - **Measures** → `Values` projections with `Measure` field type, `Entity` = `_Measures`.
     - **Axis/Category fields** → `Category` projections with `Column` field type.
     - **Legend fields** → `Series` projections with `Column` field type.
     - **Row fields (matrix)** → `Rows` projections.
     - **Column group fields (matrix)** → `Columns` projections.
   - `visualContainerObjects.title`: Set the visual title from the blueprint.

4. **Validate**: Ensure every `Entity` value matches a TMDL table name and every `Property` value matches a column or measure name.

**File location**: `<ProjectName>/PBIP/<ProjectName>.Report/definition/pages/<pageId>/visuals/<visualId>/visual.json`

### 9.5 Generate Slicer Visuals

For each slicer defined in a page's `slicers` array in the blueprint:

1. **Parse the field reference**: Extract table name and column name from `Table[Column]` syntax.
2. **Use the slicer template** from `.github/references/pbir-visual-templates.md`.
3. **Set slicer mode**: Map the blueprint's `type` to PBIR mode:
   - `dropdown` → `"Dropdown"`
   - `list` → `"List"`
   - `dateRange` → `"Between"`
4. **Generate a unique visual ID** for each slicer (e.g., `slicer_01`, `slicer_02`).
5. **Position slicers**: Place slicers at the top or left of the page (before data visuals).

### 9.6 Update `report.json` (if needed)

If the blueprint specifies navigation bookmarks, themes, or other report-level settings, update:
```
<ProjectName>/PBIP/<ProjectName>.Report/definition/report.json
```

For basic reports, the existing `report.json` from Step 00 is sufficient.

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
   - **Action**: Adjust positions to avoid overlap. Use the blueprint's position values as guidelines, but ensure no two visuals share the same pixel space.

---

## Validation Gate — MANDATORY

Before presenting results to the user, verify:

- [ ] All pages from `report_blueprint.json` have corresponding folders in `pages/`
- [ ] Each page folder contains a valid `page.json`
- [ ] Each page has a `visuals/` folder with the correct number of visual subfolders
- [ ] Each visual folder contains a valid `visual.json`
- [ ] All `Entity` references in visual queries match TMDL table names exactly
- [ ] All `Property` references match TMDL column/measure names exactly
- [ ] Visual types use correct PBIR type names (from mapping table)
- [ ] Slicer modes are valid PBIR slicer mode values
- [ ] No duplicate visual IDs within a page
- [ ] All JSON files reference the correct Microsoft `$schema` URLs

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
