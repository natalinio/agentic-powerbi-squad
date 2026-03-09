# Skill: Physical Model & TMDL Development

## Prerequisites — MANDATORY
Before writing ANY TMDL code:
1. **Read** `.github/references/tmdl-syntax-reference.md` — contains validated syntax templates.
2. **Read** `.github/references/naming-conventions.md` — contains naming rules for all objects.
3. **Read** `.github/references/pbip-folder-structure.md` — defines output folder structure.
4. If (and ONLY if) the specification includes Row-Level Security requirements, **read** `.github/references/security-rls-best-practices.md` before defining any RLS roles, table permissions, or bidirectional security propagation.
5. **Verify** any uncertain syntax using `microsoft_docs_search` MCP tool with query: `"TMDL <object_type> definition syntax"`.

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

## ⚠️ MANDATORY CHECKPOINT: Refresh Strategy Confirmation

**BEFORE generating ANY TMDL partition definitions**, the agent MUST verify that the functional specification contains the following information:

1. **Data Refresh Frequency** (e.g., Real-time, Hourly, Daily, Weekly)
2. **Storage Mode Preference** (Import, DirectQuery, Composite)
3. **Expected Data Volumes** (current and projected row counts for fact tables)
4. **Incremental Refresh Requirements** (yes/no + audit field name if applicable)
5. **Source System Update Pattern** (Append-only, Updates in place, Soft deletes, Hard deletes)

**If ANY of these are missing or unclear:**
- 🛑 **STOP execution**
- 📋 Ask the user to provide the missing information
- 💡 Provide guidance based on typical patterns:
  - **Small datasets** (< 1M rows): Import mode with full refresh
  - **Medium datasets** (1M-10M rows): Import mode with incremental refresh
  - **Large datasets** (> 10M rows): Consider DirectQuery or Composite mode
  - **Real-time requirements**: DirectQuery or Composite mode
  - **Hourly/Daily refresh**: Import mode typically sufficient

**Example Questions to Ask User:**
```
Missing Refresh Strategy Information:

I need the following details to configure the physical model correctly:

1. **Data Refresh Frequency**: How often should the report data be updated?
   - Real-time (< 1 minute latency)
   - Near real-time (5-15 minutes)
   - Hourly
   - Multiple times per day
   - Daily
   - Weekly

2. **Expected Data Volumes**: What are the current and projected row counts for fact tables?
   - Fact_Sales: ___ rows (current), ___ rows (12 months projection)

3. **Incremental Refresh**: Do any fact tables support incremental refresh?
   - If yes, what field tracks last modification? (e.g., LastModifiedDate, TransactionDate)

4. **Storage Mode**: What is your preference?
   - Import (best performance, scheduled refresh)
   - DirectQuery (real-time, slower queries)
   - Composite (hybrid approach)
   - Undecided (let me recommend based on requirements)

Please update your specification file (Section 9.1 - Data Refresh Strategy) with these details.
```

## Data Refresh Strategy & Storage Mode Selection

### Decision Tree: Import vs DirectQuery vs Composite

**Use Import Mode when:**
- ✅ Data refresh frequency is hourly or slower
- ✅ Data volumes are manageable (< 10GB compressed)
- ✅ Query performance is critical
- ✅ Source system cannot handle concurrent query load
- ✅ Complex DAX calculations required

**Use DirectQuery when:**
- ✅ Real-time data required (< 5 minute latency)
- ✅ Data volumes exceed Power BI Import limits (> 10GB)
- ✅ Source system is optimized for analytical queries (e.g., Azure Synapse, SQL Server columnstore)
- ✅ Single Source of Truth enforcement required
- ⚠️ Accept slower query performance
- ⚠️ Limited DAX function support

**Use Composite/Hybrid when:**
- ✅ Dimensions are small (Import) but facts are large (DirectQuery)
- ✅ Recent data needs real-time refresh, historical data is static
- ✅ Balancing performance and freshness
- ⚠️ More complex to configure and troubleshoot

### Incremental Refresh Configuration

**When to use Incremental Refresh:**
- Fact tables with > 1M rows
- Import mode with daily/hourly refresh
- Source system supports Last Modified Date tracking
- Historical data rarely changes (append-only or updates within recent window)

**Requirements:**
1. **Audit Field**: A DateTime or Date column that tracks when each row was last modified
   - Common names: `LastModifiedDate`, `TransactionDate`, `CreatedDate`, `UpdatedTimestamp`
2. **Power Query Parameters**: `RangeStart` and `RangeEnd` (generated automatically)
3. **Partition Strategy**: Define refresh window (e.g., "Last 7 days") and archive window (e.g., "Keep last 3 years")

**Benefits:**
- Only recent data is refreshed (faster refresh times)
- Historical data compressed and cached (better performance)
- Reduces source system load

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

> **CRITICAL**: The `defaultPowerBIDataSourceVersion: powerBI_V3` property is **MANDATORY**. Without it, Power BI Desktop (December 2025+) throws *"A data model with version 3 of metadata is required"* and cascading null-query errors on every refresh attempt.

```tmdl
model Model
	culture: en-US
	defaultPowerBIDataSourceVersion: powerBI_V3

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

#### Advanced Partition Templates (Based on Refresh Strategy)

##### A. Import Mode with Incremental Refresh

**When to use:** Large fact tables (> 1M rows) with audit field for incremental updates.

**Requirements:**
1. Power Query parameters `RangeStart` and `RangeEnd` must be defined in `expressions.tmdl`
2. Fact table MUST have a DateTime/Date column for filtering (e.g., `LastModifiedDate`, `TransactionDate`)

**Template:**

```tmdl
table Fact_Sales
	lineageTag: <generate-guid>

	column TransactionDate
		dataType: dateTime
		formatString: yyyy-MM-dd HH:mm:ss
		sourceColumn: TransactionDate
		summarizeBy: none
		lineageTag: <generate-guid>

	column LastModifiedDate
		dataType: dateTime
		isHidden
		sourceColumn: LastModifiedDate
		summarizeBy: none
		lineageTag: <generate-guid>

	partition Fact_Sales = m
		mode: import
		source =
			let
				Source = Csv.Document(File.Contents("<absolute-path-to-data>/fact_sales.csv"), [Delimiter = ",", Columns = 10, Encoding = 65001, QuoteStyle = QuoteStyle.None]),
				PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
				ChangedTypes = Table.TransformColumnTypes(PromotedHeaders, {
					{"SalesKey", Int64.Type},
					{"TransactionDate", type datetime},
					{"LastModifiedDate", type datetime},
					{"SalesAmountLC", type number}
				}),
				FilteredRows = Table.SelectRows(ChangedTypes, each [LastModifiedDate] >= RangeStart and [LastModifiedDate] < RangeEnd)
			in
				FilteredRows
```

**Note**: The `FilteredRows` step filters data using `RangeStart` and `RangeEnd` parameters. These are automatically managed by Power BI's incremental refresh policy (configured in Power BI Desktop UI after model deployment).

##### B. DirectQuery Mode Partition

**When to use:** Real-time requirements or data volumes exceeding Import limits.

**Template:**

```tmdl
table Fact_Sales
	lineageTag: <generate-guid>

	column SalesKey
		dataType: int64
		isHidden
		sourceColumn: SalesKey
		summarizeBy: none
		lineageTag: <generate-guid>

	partition Fact_Sales = m
		mode: directQuery
		source =
			let
				Source = Sql.Database("<server-name>", "<database-name>"),
				Schema = Source{[Schema="dbo"]}[Data],
				Table = Schema{[Name="Fact_Sales"]}[Data]
			in
				Table
```

**Note**: DirectQuery partitions query the source database in real-time. Source must support efficient analytical queries (indexed, columnstore, etc.).

##### C. Composite Mode Partition (Dimension: Import, Fact: DirectQuery)

**When to use:** Balance performance (cached dimensions) with freshness (real-time facts).

**Dimension (Import):**
```tmdl
table Dim_Customer
	lineageTag: <generate-guid>

	partition Dim_Customer = m
		mode: import
		source =
			let
				Source = Csv.Document(File.Contents("<absolute-path-to-data>/dim_customer.csv"), [Delimiter = ",", Columns = 5, Encoding = 65001, QuoteStyle = QuoteStyle.None]),
				PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true])
			in
				PromotedHeaders
```

**Fact (DirectQuery):**
```tmdl
table Fact_Sales
	lineageTag: <generate-guid>

	partition Fact_Sales = m
		mode: directQuery
		source =
			let
				Source = Sql.Database("<server-name>", "<database-name>"),
				Table = Source{[Schema="dbo",Item="Fact_Sales"]}[Data]
			in
				Table
```

**Note**: In Composite mode, relationships must be configured carefully. DirectQuery tables can only have limited relationships with Import tables.

##### Decision Matrix for Partition Mode

| Scenario | Partition Mode | Configuration Notes |
|----------|----------------|---------------------|
| **Mock/Prototype** (CSV) | `mode: import` | Default for Step 05 (Mock Data Generation) |
| **Small dataset** (< 1M rows, daily refresh) | `mode: import` | Full refresh from source |
| **Medium dataset** (1M-10M rows, daily refresh) | `mode: import` + Incremental Refresh | Requires `RangeStart`/`RangeEnd` parameters |
| **Large dataset** (> 10M rows, real-time) | `mode: directQuery` | Source must support analytical queries |
| **Hybrid** (small dims, large facts) | Composite (Import + DirectQuery) | Dims: Import, Facts: DirectQuery |

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

### 5. `expressions.tmdl` (Shared M Expressions & Parameters)

#### Basic Expression (Data Path Parameter)
```tmdl
expression DataPath = "<absolute-path-to-data>" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true]
```

**Use Case:** Centralized path for CSV file sources, making it easier to update source location.

#### Incremental Refresh Parameters (Required for Large Fact Tables)

**When to include:** If Section 9.1 of the specification indicates incremental refresh is required.

```tmdl
expression RangeStart = #datetime(2020, 1, 1, 0, 0, 0) meta [IsParameterQuery = true, Type = "DateTime", IsParameterQueryRequired = true]

expression RangeEnd = #datetime(2026, 12, 31, 23, 59, 59) meta [IsParameterQuery = true, Type = "DateTime", IsParameterQueryRequired = true]
```

**Important Notes:**
- `RangeStart` and `RangeEnd` are **special parameters** recognized by Power BI's incremental refresh engine
- Initial values are placeholders — Power BI overwrites them automatically based on the refresh policy configured in Power BI Desktop UI
- These parameters MUST be referenced in the partition's M query using a filter step (see "Import Mode with Incremental Refresh" template above)
- **Do NOT** use these parameters if incremental refresh is not configured — they will cause errors

**Workflow:**
1. Agent generates `expressions.tmdl` with `RangeStart`/`RangeEnd` parameters (if spec indicates incremental refresh)
2. Agent generates partition M query with filter step: `Table.SelectRows(..., each [AuditField] >= RangeStart and [AuditField] < RangeEnd)`
3. User opens model in Power BI Desktop → Navigate to table → Configure Incremental Refresh policy in UI
4. Power BI automatically manages parameter values during refresh

#### DirectQuery Connection Parameters (Optional)

**When to include:** If Section 9.1 indicates DirectQuery mode is required.

```tmdl
expression ServerName = "your-server.database.windows.net" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true]

expression DatabaseName = "YourDatabase" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true]
```

**Use Case:** Parameterize DirectQuery source for easier migration between environments (Dev → Test → Prod).

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

### TMDL Syntax & Structure
- [ ] All TMDL files use TAB indentation (not spaces)
- [ ] All object names follow naming conventions
- [ ] No TMDL-level comments (`///`, `//`) exist (causes parsing errors)

### Data Types & Column Properties (BPA Compliance)
- [ ] All surrogate keys are `int64` with `summarizeBy: none`
- [ ] All fact columns that are FKs are `isHidden` and `isAvailableInMDX: false` (BPA)
- [ ] All numeric columns use `dataType: decimal` not `double` (BPA)
- [ ] All columns have `summarizeBy: none` (BPA)
- [ ] All numeric columns have `formatString` property (BPA)
- [ ] No calculated columns in large fact tables (BPA)
- [ ] No reserved keywords in object names (BPA)

### Relationships & Model Structure
- [ ] All relationships are single-directional unless RLS required (BPA)
- [ ] Relationship `fromColumn`/`toColumn` reference existing columns
- [ ] No ambiguous relationship paths (fact → dimension via multiple routes)
- [ ] `Dim_Date` has `isKey` on `DateKey` AND column named `Date` for time intelligence (BPA)

### Refresh Strategy Configuration (NEW)
- [ ] **Refresh frequency confirmed** with user (Section 9.1 of spec)
- [ ] **Storage mode** matches requirements:
  - [ ] Import mode: CSV paths correct for mock data (Step 05)
  - [ ] DirectQuery mode: Source connection parameters defined in `expressions.tmdl`
  - [ ] Composite mode: Correct `mode:` property set per table
- [ ] **Incremental refresh** (if required):
  - [ ] `RangeStart` and `RangeEnd` parameters defined in `expressions.tmdl`
  - [ ] Audit field (LastModifiedDate) exists in fact table
  - [ ] Partition M query includes filter step: `Table.SelectRows(..., each [AuditField] >= RangeStart and [AuditField] < RangeEnd)`
- [ ] **Data volumes** considered in partition design (< 1M: full refresh, > 1M: incremental)

### GUIDs & Lineage Tags
- [ ] CRITICAL: All `lineageTag` and relationship GUIDs are unique UUIDv4 strings
- [ ] CRITICAL: No cyclic or repeating hex patterns (like `d1e2f3a...`) exist in any generated GUID

### File Paths & References
- [ ] All partition sources point to correct file paths (CSV for mock, DB for production)
- [ ] If using `DataPath` parameter, all partitions reference it consistently

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

## Artifact Checkpointing (MANDATORY)

**BEFORE presenting results to the user**, the agent MUST:

1. **VERIFY** all TMDL files have been written to `<ProjectName>/PBIP/<ProjectName>.SemanticModel/definition/`.
2. **UPDATE** `<ProjectName>/workflow_state.json`:
   - Set `pendingStep` to Step 03 completed.
   - Add all generated TMDL file paths to the artifacts list.
3. **CONFIRM** to the user that all TMDL files have been saved.

## Context Flushing Rule

When starting this step, the agent MUST:
- **READ** `<ProjectName>/workflow_state.json` to verify Steps 01-02 are completed.
- **READ** `<ProjectName>/spec/requirements_summary.md` and `<ProjectName>/spec/er_diagram.md` from disk.
- **DO NOT** rely on chat history for requirements or model design data.

**STOP here. Await user validation before proceeding to Step 4.**