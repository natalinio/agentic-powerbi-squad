# TMDL Authoring Rules

These rules come from real failures on PBIP projects. Violating them corrupts files silently
or causes Power BI Desktop to refuse to open the report.

## Encoding — UTF-8 Without BOM (Critical)

TMDL files **must** be UTF-8 without BOM.

| Method | BOM added? | Safe? |
|---|---|---|
| PowerShell `Out-File -Encoding UTF8` | ✅ Yes | ❌ NO — breaks PBIP parsing |
| PowerShell `[System.Text.Encoding]::UTF8` | ✅ Yes | ❌ NO |
| PowerShell `[System.IO.File]::WriteAllBytes(path, bytes)` | ❌ No | ✅ YES |
| Python `f.write(s.encode("utf-8"))` | ❌ No | ✅ YES |
| Python `open(..., encoding="utf-8")` write | ❌ No | ✅ YES |

When writing TMDL from PowerShell, always use:

```powershell
[System.IO.File]::WriteAllBytes($path, [System.Text.Encoding]::UTF8.GetBytes($content))
```

## Indentation (Non-Negotiable)

TMDL uses **tabs**, not spaces.

```
table TCO                           ← 0 tabs
	measure 'My Measure' =          ← 1 tab
			VAR x = 1               ← 3 tabs (DAX body lines)
			RETURN x                ← 3 tabs
		lineageTag: xxxx-...        ← 2 tabs (property lines)
		dataCategory: ImageUrl      ← 2 tabs
		displayFolder: HTML Charts  ← 2 tabs
```

- **DAX body lines** (VAR, RETURN, and blank lines inside the body): exactly **3 tabs**
- **Property lines** (`lineageTag`, `dataCategory`, `formatString`, `displayFolder`): exactly **2 tabs**
- Blank lines inside a DAX body must contain exactly 3 tabs (not empty) to preserve structure
- Do NOT use spaces as substitutes for tabs

Property order inside a measure block:
1. `lineageTag`
2. `dataCategory` (if present)
3. `formatString` (if present)
4. `displayFolder` (if present)

## No Measure Aliases

```tmdl
-- ❌ INVALID — throws UnsupportedObjectType on file open
measure 'Alias' = [OtherMeasure]

-- ✅ VALID — copy the full DAX expression
measure 'Alias' =
			[full DAX expression here]
```

`measure 'X' = [Y]` is not valid TMDL syntax. Power BI Desktop will refuse to open the file.
Always copy the full DAX expression instead of creating an alias.

## `sourceColumn` Required on Calculated Tables

For calculated tables (DATATABLE, ADDCOLUMNS, CALENDAR, CALENDARAUTO), every column definition
**must** include `sourceColumn: <name>` matching the exact column name produced by the DAX
expression. Omitting it throws a load error.

```tmdl
-- ✅ Correct
table Calendario
	column Date
		dataType: dateTime
		sourceColumn: Date

-- ❌ Missing sourceColumn — load error
table Calendario
	column Date
		dataType: dateTime
```

## Relationships on Calculated Tables — Use PBI Desktop UI

Do NOT write relationships between calculated tables directly in `relationships.tmdl`.
The Analysis Services Engine assigns internal column IDs only after first materialization in
Power BI Desktop.

**Error**: `PFE_TM_RELATIONSHIP_END_COLUMN_INVALID`

**Correct workflow**:
1. Open PBIP in Power BI Desktop
2. Create the relationship via Model View drag-and-drop
3. Save → Power BI writes the correct TMDL automatically

## Hierarchies on Calculated Tables — Use PBI Desktop UI

Same reason as relationships — writing hierarchies manually in TMDL before first materialization
throws `PFE_TM_LEVEL_SOURCE_COLUMN_INVALID`.

**Correct workflow**:
1. Open PBIP in Power BI Desktop
2. Right-click column → New Hierarchy → add levels
3. Save

## `isDateTable` Does Not Exist in TMDL

The keyword `isDateTable` does NOT exist in TMDL syntax (Power BI Desktop April 2026+).
Power BI manages date table marking internally.

**Error**: `UnknownKeyword` on file open.

Never write `isDateTable` as a standalone line in a table definition.

## Editing Existing Measures

- Preserve existing indentation and property ordering when editing measure blocks.
- Avoid formatting-only changes to lines unrelated to the task.
- When reading a file before editing, check the actual tab count — do not assume.

## Post-Edit Validation

After any TMDL edit:
1. Open the PBIP in Power BI Desktop — verify no parse errors on open.
2. Confirm the edited measure evaluates correctly in a report visual.
3. Check that related measures and relationships still function as expected.
