# Skill: Physical Model & TMDL Development

## Prerequisites — MANDATORY
Before writing ANY TMDL code:
1. **Read** `.github/references/tmdl-syntax-reference.md` — contains validated syntax templates.
2. **Read** `.github/references/naming-conventions.md` — contains naming rules for all objects.
3. **Read** `.github/references/pbip-folder-structure.md` — defines output folder structure.
4. **Verify** any uncertain syntax using `microsoft_docs_search` MCP tool with query: `"TMDL <object_type> definition syntax"`.

## TMDL Syntax Critical Rules

TMDL is **whitespace-sensitive**. Violations cause Power BI Desktop parsing failures.

### ⛔ COMMENTS NOT SUPPORTED IN TMDL SYNTAX (CRITICAL)

**CRITICAL DISTINCTION**:

**❌ TMDL Syntax Comments NOT Supported** (outside expressions):
- ❌ **NO** triple-slash comments: `///` before table/column/measure declarations
- ❌ **NO** double-slash comments: `//` at TMDL property level
- ❌ **NO** block comments: `/* */` in TMDL structure
- ❌ **NO** XML-style comments: `<!-- -->`

**✅ DAX Expression Comments ARE Supported** (inside measure expressions):
- ✅ Single-line DAX comments: `// This is a DAX comment`
- ✅ Multi-line DAX comments: `/* DAX comment block */`

**Examples**:

```tmdl
❌ WRONG (TMDL comment):
/// This is a table comment
table Dim_Date
	/// This is a column comment
	column DateKey
		dataType: int64

✅ CORRECT (No TMDL comments, but DAX comments allowed in expressions):
table _Measures

	measure 'Sales Amount' =
			// This DAX comment is OK inside the expression
			VAR TotalSales = SUM(Fact_Sales[SalesAmount])  // Inline DAX comment OK
			/* Multi-line DAX comment
			   also acceptable here */
			RETURN TotalSales
		formatString: "#,##0.00"
		displayFolder: "Sales Metrics"
```

**Rule Summary**:
- **TMDL structure** (table, column, measure declarations, properties) → NO comments of any kind
- **DAX expressions** (inside `measure 'Name' = <expression>`) → Comments fully supported

If you need to document your model structure:
- ✅ Use separate documentation files (Markdown, Word)
- ✅ Use `description` property for measures/columns (where supported)
- ✅ Use self-documenting naming conventions
- ✅ Use DAX comments INSIDE measure expressions for business logic documentation

**Historical Error**: In previous iterations, comments like `/// Date dimension for time intelligence` were added before table declarations, causing model load failures with cryptic error messages about "unexpected tokens".

### Indentation
- Use **single TAB** for each indentation level. Do NOT use spaces.
- Level 1: Object declaration (table, relationship) — NO indentation (root level).
- Level 2: Object properties — ONE tab indent.
- Level 3: Multi-line expressions — TWO tabs indent.

### Object Hierarchy (no indentation required at root)
These objects are root-level (no indentation):
- `model`, `table`, `relationship`, `expression`, `role`, `culture`, `perspective`, `database`

### Property Delimiters
- Colon (`:`) for non-expression properties: `dataType: int64`
- Equals (`=`) for expressions and default properties: `measure Sales = SUM(...)`

### Naming
- Object names with spaces, dots, equals, or colons MUST be enclosed in single quotes: `'Sales Amount'`
- Single quotes in names are escaped by doubling: `'Customer''s Name'`

## ⛔ CRITICAL: Ambiguous Path Prevention

**BEFORE generating relationships.tmdl**, verify that your logical model does NOT have redundant Foreign Keys that would create ambiguous paths.

**Check for ambiguity**:
1. List ALL Foreign Keys in each Fact table
2. For each FK, trace the relationship chain to see which dimensions it connects to
3. If TWO different FKs lead to the SAME dimension through different paths, you have an ambiguity

**Example**:
If `Fact_Sales` has:
- `CustomerKey → Dim_Customer.CustomerKey`
- `CountryKey → Dim_Country.CountryKey`

AND `Dim_Customer` has:
- `CountryKey → Dim_Country.CountryKey`

Then you have TWO paths from Fact_Sales to Dim_Country:
- Path A: `Fact_Sales.CountryKey → Dim_Country` (direct)
- Path B: `Fact_Sales.CustomerKey → Dim_Customer → Dim_Country` (indirect)

**Power BI will REJECT this model** with error:
```
There are ambiguous paths between 'Fact_Sales' and 'Dim_Country'
```

**Solution**: Remove the direct relationship `Fact_Sales.CountryKey → Dim_Country`. Keep only the path through `Dim_Customer`.

**Rule**: A fact table should connect to the **most granular dimension** in a hierarchy, NOT to every level of the hierarchy.

## File Generation Rules

Generate the following TMDL files inside `<ProjectName>/PBIP/<ProjectName>.SemanticModel/definition/`:

### 1. `database.tmdl`

**CRITICAL**: The `compatibilityLevel` MUST match the Power BI Desktop version being used. Using an incorrect compatibility level will cause one of two errors:
- **Downgrade error**: If the TMDL file specifies a lower level than what Power BI Desktop already created
- **Upgrade error**: If the TMDL file requires features not supported by the installed Power BI Desktop version

**How to determine the correct compatibilityLevel:**

| Power BI Desktop Version | Release Date | CompatibilityLevel | Notes |
|--------------------------|--------------|-----------------------|-------|
| December 2025 (2.150.x) | Dec 2025 | **1600** | Current version |
| September 2024 (2.133.x) | Sep 2024 | 1567 | Legacy version |
| June 2024 (2.130.x) | Jun 2024 | 1550 | Older version |

**Rule**: When generating a new model, ALWAYS use the compatibility level matching the **installed Power BI Desktop version**. If uncertain, use **1600** for December 2025 and later.

```tmdl
database <ProjectName>
	compatibilityLevel: 1600
```

### 2. `model.tmdl`
```tmdl
model Model
	culture: en-US

ref table Dim_Date
ref table Dim_Customer
ref table Fact_Sales
ref table _Measures
```

### 3. `tables/<TableName>.tmdl` (one file per table)

#### Dimension Table Template:

**Note**: This example shows a Date dimension table. Do NOT add comments in actual TMDL files.

```tmdl
table Dim_Date
	lineageTag: <generate-guid>

	column DateKey
		dataType: int64
		isKey
		isHidden
		sourceColumn: DateKey
		summarizeBy: none
		lineageTag: <generate-guid>

	column Date
		dataType: dateTime
		formatString: yyyy-MM-dd
		sourceColumn: Date
		summarizeBy: none
		lineageTag: <generate-guid>

	column Year
		dataType: string
		sourceColumn: Year
		summarizeBy: none
		lineageTag: <generate-guid>

	partition Dim_Date = m
		mode: import
		source =
			let
				Source = Csv.Document(File.Contents("<absolute-path-to-data>/dim_date.csv"), [Delimiter = ",", Columns = 12, Encoding = 65001, QuoteStyle = QuoteStyle.None]),
				PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
				ChangedTypes = Table.TransformColumnTypes(PromotedHeaders, {{"DateKey", Int64.Type}, {"Date", type datetime}})
			in
				ChangedTypes
```

#### Fact Table Template:

**Note**: This example shows a Sales fact table at daily grain per customer. Do NOT add comments in actual TMDL files.

```tmdl
table Fact_Sales
	lineageTag: <generate-guid>

	column SalesKey
		dataType: int64
		isHidden
		sourceColumn: SalesKey
		summarizeBy: none
		lineageTag: <generate-guid>

	column DateKey
		dataType: int64
		isHidden
		sourceColumn: DateKey
		summarizeBy: none
		lineageTag: <generate-guid>

	column CustomerKey
		dataType: int64
		isHidden
		sourceColumn: CustomerKey
		summarizeBy: none
		lineageTag: <generate-guid>

	column 'Sales Amount LC'
		dataType: decimal
		formatString: #,##0.00
		sourceColumn: SalesAmountLC
		summarizeBy: sum
		lineageTag: <generate-guid>

	partition Fact_Sales = m
		mode: import
		source =
			let
				Source = Csv.Document(File.Contents("<absolute-path-to-data>/fact_sales.csv"), [Delimiter = ",", Columns = 8, Encoding = 65001, QuoteStyle = QuoteStyle.None]),
				PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
				ChangedTypes = Table.TransformColumnTypes(PromotedHeaders, {{"SalesKey", Int64.Type}, {"DateKey", Int64.Type}, {"SalesAmountLC", type number}})
			in
				ChangedTypes
```

#### Measures Table Template (disconnected):

**Note**: This is a disconnected table containing only DAX measures. Do NOT add comments in actual TMDL files.

```tmdl
table _Measures

	measure 'Placeholder' = 0
		lineageTag: <generate-guid>

	partition _Measures = m
		mode: import
		source =
			let
				Source = #table({"MeasuresColumn"}, {{""}})
			in
				Source
```

### 4. `relationships.tmdl`

**CRITICAL RULE**: Power BI enforces **only ONE relationship per table with `securityFilteringBehavior: bothDirections`**. For standard Star Schema models without advanced RLS requirements, ALWAYS use `securityFilteringBehavior: oneDirection` on ALL relationships.

**Property Distinctions:**
- **`securityFilteringBehavior`**: Controls Row-Level Security (RLS) filter propagation. Values: `oneDirection`, `bothDirections`. Default: `oneDirection`. Use `bothDirections` ONLY for RLS scenarios requiring bidirectional security filtering (max 1 per table).
- **`crossFilteringBehavior`**: Controls query filter propagation for DAX calculations. Values: `oneDirection`, `bothDirections`, `automatic`. Default: `automatic`. Use `oneDirection` for Star Schema (Dim → Fact), `bothDirections` only for specific advanced scenarios (e.g., many-to-many bridges).

**Template (Star Schema):**
```tmdl
relationship <generate-unique-guid>
	fromColumn: Fact_Sales.DateKey
	toColumn: Dim_Date.DateKey
	fromCardinality: many
	toCardinality: one
	isActive: true
	securityFilteringBehavior: oneDirection
	relyOnReferentialIntegrity: false
	crossFilteringBehavior: oneDirection

relationship <generate-unique-guid>
	fromColumn: Fact_Sales.CustomerKey
	toColumn: Dim_Customer.CustomerKey
	fromCardinality: many
	toCardinality: one
	isActive: true
	securityFilteringBehavior: oneDirection
	relyOnReferentialIntegrity: false
	crossFilteringBehavior: oneDirection
```

**Common Error:**
```
Table 'Dim_Customer' already has a relationship where Security Filtering Behavior is set to Both.
```
**Cause**: More than one relationship touching the same table has `securityFilteringBehavior: bothDirections`.  
**Fix**: Change all relationships to `securityFilteringBehavior: oneDirection` unless you have a specific RLS requirement.

### 5. `expressions.tmdl` (if needed for shared M expressions/parameters)
```tmdl
expression DataPath = "<absolute-path-to-data>" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true]
```

## Relationship Rules (CRITICAL)

**Direction:**
- `fromColumn`: FK column (Many side - typically Fact or lower-level Dimension)
- `toColumn`: PK column (One side - typically Dimension)
- Flow: Filters flow from Dimension → Fact (one-directional)

**Cardinality:**
- Star Schema: Always **Many-to-One** (Fact/Lower Dim → Dimension)
- Explicitly specify: `fromCardinality: many` and `toCardinality: one`

**Security Filtering Behavior (RLS):**
- **Default**: `securityFilteringBehavior: oneDirection` (Dimension → Fact)
- **Rule**: Only ONE relationship per table can have `bothDirections`
- **Use Case**: Bidirectional RLS when security context must flow both ways (rare)

**Cross-Filtering Behavior (DAX):**
- **Default**: `crossFilteringBehavior: automatic`
- **Star Schema**: Use `oneDirection` for all Dim → Fact relationships
- **Advanced**: Use `bothDirections` ONLY for many-to-many bridges or role-playing dimensions requiring bidirectional query filtering

**Active Status:**
- `isActive: true` for primary relationship
- `isActive: false` for inactive relationships (role-playing dimensions with USERELATIONSHIP)

**Referential Integrity:**
- `relyOnReferentialIntegrity: false` when using Import mode (Power BI cannot enforce)
- `relyOnReferentialIntegrity: true` only for DirectQuery with database-enforced constraints

**COMMON ERRORS:**
1. **"Table 'X' already has a relationship where Security Filtering Behavior is set to Both"**  
   → Cause: Multiple relationships with `securityFilteringBehavior: bothDirections` on same table  
   → Fix: Change all to `oneDirection` unless specific RLS requirement exists

2. **Ambiguous relationship paths in DAX**  
   → Cause: Multiple active relationships between same two tables  
   → Fix: Set one to `isActive: false`, use USERELATIONSHIP() in DAX

## Data Type Mapping
| Spec Type | TMDL dataType | Power Query Type |
|-----------|---------------|-----------------|
| Integer / ID / Key | `int64` | `Int64.Type` |
| Decimal / Currency | `decimal` | `type number` |
| String / Text | `string` | `type text` |
| Date | `dateTime` | `type datetime` |
| Boolean | `boolean` | `type logical` |
| Percentage | `double` | `type number` |

## GUID Generation (CRITICAL ANTI-COLLISION RULE)
LLMs naturally struggle with random generation, often defaulting to cyclic or repeating hex patterns. You MUST actively counteract this behavior:
- **NEVER** use sequential, cyclic, or deterministic patterns (e.g., `d1e2f3a4-b5c6...`, `12345678-1234...`, `e2f3a4b5-...`).
- Every `lineageTag` and `relationship` name MUST be a strictly unique, randomly generated UUIDv4.
- Standard UUIDv4 format: `xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx` (where `x` is any random hex digit `0-9, a-f`, and `y` is strictly `8, 9, a, or b`).
- **Global Uniqueness**: Ensure absolute uniqueness across ALL objects in the model. Do NOT reuse or increment any previously generated GUID within the same file or across different tables/files.
- Treat each GUID generation as an isolated cryptographic task: visually verify that the hex string is completely different from the previous one.

## BPA Compliance Guidelines (Preventive)

**CRITICAL**: Before writing ANY TMDL code, review the following Best Practice Analyzer rules from `.github/references/bpa-rules-reference.md`. These guidelines ensure production-quality semantic models.

### Metadata Rules (Error Severity)

1. **AVOID_FLOAT_DATATYPE** (Error): Use `dataType: decimal` for ALL numeric columns (amounts, quantities). NEVER use `dataType: double` (causes rounding errors in financial calculations).

```tmdl
✅ DO:
column SalesAmount
	dataType: decimal
	summarizeBy: none
	formatString: "$#,##0.00"

❌ DON'T:
column SalesAmount
	dataType: double
```

**Explanation**: `decimal` provides precise arithmetic for financial calculations, while `double` causes floating-point rounding errors.

2. **SUMMARIZEBY_SHOULD_BE_NONE** (Warning): ALL columns SHOULD have `summarizeBy: none` to prevent accidental aggregations. Force users to use explicit measures.

```tmdl
✅ DO:
column SalesAmount
	dataType: decimal
	summarizeBy: none

❌ DON'T:
column SalesAmount
	dataType: decimal
	summarizeBy: sum
```

**Explanation**: `summarizeBy: none` prevents users from accidentally dragging columns directly into visuals, forcing them to use explicit measures instead.

### Model Layout Rules (Warning Severity)

3. **HIDE_FOREIGN_KEY_COLUMNS** (Warning): ALL foreign key columns in fact tables MUST have `isHidden: true`. Users should interact with dimension attributes, not numeric FKs.

```tmdl
✅ DO:
column ProductKey
	dataType: int64
	isKey: true
	isHidden: true
	isAvailableInMDX: false
	summarizeBy: none

❌ DON'T:
column ProductKey
	dataType: int64
	isKey: true
```

**Explanation**: Foreign keys should be hidden from the field list. Users should interact with dimension attributes, not numeric FK values.

4. **DISABLE_ATTRIBUTE_HIERARCHIES** (Info): Foreign key columns SHOULD have `isAvailableInMDX: false` to hide from MDX queries and reduce field list clutter.

5. **OBJECTS_WITH_NO_FORMAT_STRING_COLUMNS** (Warning): Numeric columns SHOULD have `formatString` property for consistent display.

```tmdl
✅ DO:
column SalesAmount
	dataType: decimal
	summarizeBy: none
	formatString: "$#,##0.00"

column 'Profit Margin'
	dataType: decimal
	summarizeBy: none
	formatString: "0.00%"
```

**Explanation**: Currency columns use `"$#,##0.00"`, percentage columns use `"0.00%"`.

**Common Format Strings**:
- Currency: `"$#,##0.00"` or `"€#,##0.00"`
- Percentage: `"0.00%"`
- Integer: `"#,##0"`
- Decimal: `"#,##0.00"`
- Date: `"yyyy-MM-dd"`

### Naming Convention Rules

6. **TABLE_NAME_MUST_START_WITH_PREFIX** (Warning): Tables MUST use prefixes `Fact_`, `Dim_`, `Bridge_`. See `.github/references/naming-conventions.md`.

7. **AVOID_RESERVED_KEYWORDS** (Error): Object names MUST NOT use DAX/SQL reserved keywords (`Date`, `Table`, `Value`, `Column`, `Year`, `Month`, etc.). Use prefixes/suffixes to avoid collisions.

```tmdl
✅ DO:
table Dim_Date
	column DateKey
	column DateValue

❌ DON'T:
table Date
	column Date
	column Value
```

**Explanation**: Prefix avoids reserved keywords. `Date`, `Table`, `Value`, `Column`, `Year`, `Month` are all reserved keywords in DAX/SQL.

8. **DATE_COLUMN_NAMED_DATE** (Warning): Date dimension MUST have a column named `Date` (dataType: dateTime) for Power BI time intelligence functions.

```tmdl
✅ DO:
table Dim_Date
	column DateKey
		dataType: int64
		isKey: true
		isHidden: true
	
	column Date
		dataType: dateTime
		formatString: "yyyy-MM-dd"
```

**Explanation**: `DateKey` is the surrogate key (int64), `Date` is the natural key used by time intelligence functions.

### Performance Rules

9. **AVOID_CALCULATED_COLUMNS_IN_LARGE_FACTS** (Warning): Large fact tables (> 1M rows) SHOULD NOT contain calculated columns. Use measures instead (computed at query time, not materialized at refresh).

```tmdl
❌ DON'T (in Large Fact):
column 'Profit Margin'  // Calculated column
	dataType: decimal
	expression: [Profit] / [Revenue]

✅ DO (as Measure):
measure 'Profit Margin' =
	VAR TotalProfit = SUM(Fact_Sales[Profit])
	VAR TotalRevenue = SUM(Fact_Sales[Revenue])
	RETURN DIVIDE(TotalProfit, TotalRevenue)
```

10. **MINIMIZE_BIDIRECTIONAL_RELATIONSHIPS** (Warning): Relationships SHOULD be single-directional (`crossFilteringBehavior: oneDirection`) unless required for RLS.

```tmdl
✅ DO:
relationship
	fromColumn: Fact_Sales.ProductKey
	toColumn: Dim_Product.ProductKey
	crossFilteringBehavior: oneDirection

❌ DON'T:
relationship
	fromColumn: Fact_Sales.ProductKey
	toColumn: Dim_Product.ProductKey
	crossFilteringBehavior: bothDirections
```

**Explanation**: One-directional relationships provide best performance. Use `bothDirections` only for specific RLS scenarios.

### Template Compliance Checklist

Before writing TMDL tables, ensure templates include:

**Dimension Table Column Template**:
```tmdl
column <AttributeName>
	dataType: <string|int64|dateTime|decimal>
	summarizeBy: none
	formatString: "<format>"
	sourceColumn: <AttributeName>
	lineageTag: <guid>
```

**Note**: `summarizeBy: none` prevents accidental aggregation. `formatString` is required for numeric columns (BPA rule).

**Fact Table Foreign Key Template**:
```tmdl
column <DimensionKey>
	dataType: int64
	isHidden: true
	isAvailableInMDX: false
	summarizeBy: none
	sourceColumn: <DimensionKey>
	lineageTag: <guid>
```

**Note**: Foreign keys must be hidden (`isHidden: true`), have attribute hierarchy disabled (`isAvailableInMDX: false`), and prevent aggregation (`summarizeBy: none`) per BPA rules.

**Fact Table Measure Column Template**:
```tmdl
column <MeasureColumn>
	dataType: decimal
	formatString: "$#,##0.00"
	summarizeBy: none
	sourceColumn: <MeasureColumn>
	lineageTag: <guid>
```

**Note**: Use `decimal` datatype (not `double`), include `formatString` for display, and set `summarizeBy: none` to force users to use explicit measures (BPA rules).

**MCP Verification**: Before finalizing TMDL code, search `microsoft_docs_search("Power BI TMDL column properties syntax dataType formatString")` to verify property names and syntax.

---

## Validation Before Output
- [ ] All TMDL files use TAB indentation (not spaces)
- [ ] All object names follow naming conventions
- [ ] All surrogate keys are `int64` with `summarizeBy: none`
- [ ] All fact columns that are FKs are `isHidden` and `isAvailableInMDX: false` (BPA)
- [ ] All numeric columns use `dataType: decimal` not `double` (BPA)
- [ ] All columns have `summarizeBy: none` (BPA)
- [ ] All numeric columns have `formatString` property (BPA)
- [ ] All relationships are single-directional unless RLS required (BPA)
- [ ] No calculated columns in large fact tables (BPA)
- [ ] No reserved keywords in object names (BPA)
- [ ] All partition sources point to correct CSV file paths
- [ ] Relationship `fromColumn`/`toColumn` reference existing columns
- [ ] `Dim_Date` has `isKey` on `DateKey` AND column named `Date` for time intelligence (BPA)
- [ ] CRITICAL: All `lineageTag` and relationship GUIDs are unique UUIDv4 strings.
- [ ] CRITICAL: No cyclic or repeating hex patterns (like `d1e2f3a...`) exist in any generated GUID.

## ⚠️ Post-Generation: Universal Script Execution (MANDATORY)

After generating ALL TMDL files, the agent MUST instruct the user to run the following universal scripts from the repository root:

### 1. Fix LineageTags (Prevent GUID Collisions)
```powershell
python .github/scripts/fix_lineage_tags.py <ProjectName>
```
This regenerates all `lineageTag` values with cryptographically unique UUID v4, preventing "lineage-tag already exists" errors.

### 2. Remove TMDL Comments (Prevent Parsing Errors)
```powershell
python .github/scripts/remove_tmdl_comments.py <ProjectName>
```
This removes any accidentally generated `///` or `//` comments at the TMDL structure level that would cause Power BI Desktop parsing failures.

**Note**: Both scripts require Python 3.10+ and the `.venv` environment activated. If not set up yet, guide the user:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**STOP here. Await user validation before proceeding to Step 4.**