# Relationship Patterns Reference — Advanced Star Schema

> Validated relationship design patterns for complex Power BI semantic model scenarios.
> Use `microsoft_docs_search` MCP tool to verify any pattern before implementation.

---

## 1. Role-Playing Dimensions

### Pattern Description
When a single dimension serves multiple purposes in a fact table (e.g., Order Date, Ship Date, Delivery Date).

### Implementation Strategy
- **Single Dimension Table**: Create ONE `Dim_Date` table
- **Multiple Relationships**: Define one relationship per role
- **Active vs Inactive**: Only ONE relationship can be active; others are inactive
- **DAX Usage**: Use `USERELATIONSHIP()` function to activate inactive relationships in measures

### TMDL Example
```tmdl
relationship
	fromColumn: Fact_Sales.OrderDateKey
	toColumn: Dim_Date.DateKey
	fromCardinality: many
	toCardinality: one
	isActive: true
	securityFilteringBehavior: bothDirections
	relyOnReferentialIntegrity: false
	crossFilteringBehavior: oneDirection

relationship
	fromColumn: Fact_Sales.ShipDateKey
	toColumn: Dim_Date.DateKey
	fromCardinality: many
	toCardinality: one
	isActive: false
	securityFilteringBehavior: bothDirections
	relyOnReferentialIntegrity: false
	crossFilteringBehavior: oneDirection

relationship
	fromColumn: Fact_Sales.DeliveryDateKey
	toColumn: Dim_Date.DateKey
	fromCardinality: many
	toCardinality: one
	isActive: false
	securityFilteringBehavior: bothDirections
	relyOnReferentialIntegrity: false
	crossFilteringBehavior: oneDirection
```

### DAX Measure Pattern
```dax
-- Uses active relationship (OrderDateKey)
measure 'Sales by Order Date' = 
	SUM(Fact_Sales[SalesAmount])

-- Uses inactive relationship (ShipDateKey)
measure 'Sales by Ship Date' =
	VAR ShipSales = 
		CALCULATE(
			SUM(Fact_Sales[SalesAmount]),
			USERELATIONSHIP(Fact_Sales[ShipDateKey], Dim_Date[DateKey])
		)
	RETURN
		ShipSales

-- Uses inactive relationship (DeliveryDateKey)
measure 'Sales by Delivery Date' =
	VAR DeliverySales = 
		CALCULATE(
			SUM(Fact_Sales[SalesAmount]),
			USERELATIONSHIP(Fact_Sales[DeliveryDateKey], Dim_Date[DateKey])
		)
	RETURN
		DeliverySales
```

### When to Use
- Multiple date roles in transactions (Order/Ship/Delivery/Invoice)
- Multiple geography roles (Origin/Destination, Billing/Shipping Address)
- Multiple person roles (Salesperson/Manager, Created By/Modified By)

---

## 2. Many-to-Many Relationships

### Pattern Description
When both sides of a relationship can have multiple matching records (e.g., Students enrolled in multiple Courses, Products sold by multiple Salespersons).

### ✅ Recommended Pattern: Bridge Table
Instead of native many-to-many, use an intermediate **Bridge Table** (also called **Factless Fact Table**).

### Structure
```
Dim_Student (1) ← (M) Bridge_StudentCourse (M) → (1) Dim_Course
     ↓                                                    ↓
StudentKey                                          CourseKey
     ↓                                                    ↓
   [PK]              StudentKey + CourseKey             [PK]
                        (composite FK)
```

### TMDL Implementation
```tmdl
-- Bridge Table
table Bridge_StudentCourse
	lineageTag: <guid>
	
	column StudentKey
		dataType: int64
		sourceColumn: StudentKey
		summarizeBy: none
	
	column CourseKey
		dataType: int64
		sourceColumn: CourseKey
		summarizeBy: none
	
	partition Bridge_StudentCourse
		mode: import
		source =
			let
				Source = Csv.Document(File.Contents("data/bridge_student_course.csv"))
			in
				Source

-- Relationships
relationship
	fromColumn: Bridge_StudentCourse.StudentKey
	toColumn: Dim_Student.StudentKey
	fromCardinality: many
	toCardinality: one
	isActive: true
	crossFilteringBehavior: oneDirection

relationship
	fromColumn: Bridge_StudentCourse.CourseKey
	toColumn: Dim_Course.CourseKey
	fromCardinality: many
	toCardinality: one
	isActive: true
	crossFilteringBehavior: oneDirection
```

### DAX Pattern
```dax
-- Count distinct students in filtered courses
measure 'Student Count' =
	VAR StudentKeys = 
		VALUES(Bridge_StudentCourse[StudentKey])
	VAR Result = 
		COUNTROWS(StudentKeys)
	RETURN
		Result

-- Count distinct courses per student
measure 'Courses per Student' =
	DIVIDE(
		COUNTROWS(Bridge_StudentCourse),
		[Student Count],
		0
	)
```

### ⚠️ Native Many-to-Many (Use Sparingly)
Power BI supports native many-to-many, but it can cause:
- Unexpected filtering behavior
- Performance issues
- Ambiguous results

**Only use when:**
- Data model is simple and well-understood
- Performance is validated
- Bridge table approach is not feasible

---

## 3. Self-Referencing Relationships (Parent-Child Hierarchies)

### Pattern Description
When records in a table reference other records in the same table (e.g., Employee → Manager, Category → Parent Category).

### TMDL Structure
```tmdl
table Dim_Employee
	lineageTag: <guid>
	
	column EmployeeKey
		dataType: int64
		isKey
		sourceColumn: EmployeeKey
		summarizeBy: none
	
	column EmployeeName
		dataType: string
		sourceColumn: EmployeeName
	
	column ManagerKey
		dataType: int64
		sourceColumn: ManagerKey
		summarizeBy: none
		isHidden
	
	-- Parent-Child hierarchy
	hierarchy EmployeeHierarchy
		lineageTag: <guid>
		
		level Level1
			column: EmployeeName
		
	partition Dim_Employee
		mode: import
		source = 
			let
				Source = Csv.Document(File.Contents("data/dim_employee.csv"))
			in
				Source

-- Self-referencing relationship
relationship
	fromColumn: Dim_Employee.ManagerKey
	toColumn: Dim_Employee.EmployeeKey
	fromCardinality: many
	toCardinality: one
	isActive: true
	crossFilteringBehavior: oneDirection
```

### DAX Pattern with PATH Functions
```dax
-- Create flattened hierarchy using DAX calculated columns
column 'Employee Path' = 
	PATH(Dim_Employee[EmployeeKey], Dim_Employee[ManagerKey])

column 'Employee Level' = 
	PATHLENGTH(Dim_Employee[Employee Path])

column 'Top Manager' = 
	LOOKUPVALUE(
		Dim_Employee[EmployeeName],
		Dim_Employee[EmployeeKey],
		PATHITEM(Dim_Employee[Employee Path], 1)
	)

-- Measures using hierarchy
measure 'Total Employees in Branch' =
	VAR CurrentEmployee = SELECTEDVALUE(Dim_Employee[EmployeeKey])
	VAR SubordinatePath = 
		FILTER(
			ALL(Dim_Employee),
			PATHCONTAINS(Dim_Employee[Employee Path], CurrentEmployee)
		)
	VAR Result = 
		COUNTROWS(SubordinatePath)
	RETURN
		Result
```

### When to Use
- Organizational hierarchies (Employee → Manager)
- Product categories (Category → Parent Category)
- Geographic hierarchies (City → State → Country)
- Account hierarchies (Account → Parent Account)

---

## 4. Relationship Troubleshooting Patterns

### Problem: Orphaned Records (Missing Foreign Keys)

**Symptom**: Fact records with FK values that don't exist in dimension table

**Detection Query** (Power Query M):
```powerquery
let
    FactTable = Fact_Sales,
    DimTable = Dim_Customer,
    OrphanCheck = Table.NestedJoin(
        FactTable, {"CustomerKey"},
        DimTable, {"CustomerKey"},
        "Matched", JoinKind.LeftAnti
    )
in
    OrphanCheck
```

**Fix Options**:
1. **Data Cleansing**: Remove or fix orphaned records at source
2. **Unknown Member**: Add "Unknown" record in dimension (CustomerKey = -1)
3. **Relationship Property**: Set `relyOnReferentialIntegrity: true` (DirectQuery only)

### Problem: Circular Relationships

**Symptom**: DAX error "Cannot create a relationship between tables because it would cause a circular dependency"

**Example**: Product → Category → Subcategory → Product

**Fix**:
- **Denormalize**: Flatten hierarchy into single dimension table
- **Separate Tables**: Break circular chain with calculated columns
- **Inactive Relationships**: Make one relationship inactive

### Problem: Bidirectional Filtering Performance

**Symptom**: Slow query performance with bidirectional cross-filtering

**Detection**:
- Check relationships with `crossFilteringBehavior: bothDirections`
- Use Performance Analyzer in Power BI Desktop

**Fix**:
- **Minimize Usage**: Only use bidirectional when absolutely necessary
- **Alternative**: Use DAX measures with explicit CALCULATE filters
- **Security Only**: Reserve bidirectional for Row-Level Security (RLS)

**Example - Replace Bidirectional with DAX**:
```dax
-- Instead of bidirectional relationship
measure 'Sales for Selected Products' =
	VAR SelectedProducts = VALUES(Dim_Product[ProductKey])
	VAR FilteredSales = 
		CALCULATE(
			SUM(Fact_Sales[SalesAmount]),
			Dim_Product[ProductKey] IN SelectedProducts
		)
	RETURN
		FilteredSales
```

### Problem: Multiple "Both" Security Filtering Behavior on Same Table

**Symptom**: Power BI load error: "Table 'X' already has a relationship where Security Filtering Behavior is set to Both. Only one relationship per table with this setting is allowed."

**Cause**: More than one relationship touching the same table has `securityFilteringBehavior: bothDirections`

**Example of VIOLATION**:
```tmdl
-- ❌ ERROR: Dim_Customer has 2 relationships with bothDirections
relationship rel1
	fromColumn: Dim_Customer.CountryKey
	toColumn: Dim_Country.CountryKey
	securityFilteringBehavior: bothDirections  -- First bothDirections

relationship rel2
	fromColumn: Fact_Sales.CustomerKey
	toColumn: Dim_Customer.CustomerKey
	securityFilteringBehavior: bothDirections  -- Second bothDirections ❌ VIOLATION
```

**Detection**:
1. Search all `.tmdl` files for `securityFilteringBehavior: bothDirections`
2. Group by table name (`fromColumn` and `toColumn` table names)
3. If any table appears in more than one `bothDirections` relationship → ERROR

**Fix Options**:
1. **Standard Star Schema (Recommended)**: Change ALL relationships to `securityFilteringBehavior: oneDirection`
```tmdl
-- ✅ CORRECT: All relationships use oneDirection
relationship rel1
	fromColumn: Dim_Customer.CountryKey
	toColumn: Dim_Country.CountryKey
	securityFilteringBehavior: oneDirection  -- ✅
	crossFilteringBehavior: oneDirection

relationship rel2
	fromColumn: Fact_Sales.CustomerKey
	toColumn: Dim_Customer.CustomerKey
	securityFilteringBehavior: oneDirection  -- ✅
	crossFilteringBehavior: oneDirection
```

2. **RLS Scenario (Advanced)**: If bidirectional RLS is required, keep ONLY ONE `bothDirections` per table
```tmdl
-- ✅ CORRECT: Only ONE bothDirections per table
relationship rel1
	fromColumn: Dim_Customer.CountryKey
	toColumn: Dim_Country.CountryKey
	securityFilteringBehavior: oneDirection  -- ✅

relationship rel2
	fromColumn: Fact_Sales.CustomerKey
	toColumn: Dim_Customer.CustomerKey
	securityFilteringBehavior: bothDirections  -- ✅ Only ONE bothDirections
```

**Key Distinction**:
- **`securityFilteringBehavior`**: Row-Level Security (RLS) filter propagation (max 1 bothDirections per table)
- **`crossFilteringBehavior`**: Query filter propagation (no limit on bothDirections)

**Prevention**: Always use `securityFilteringBehavior: oneDirection` unless you have a documented RLS requirement for bidirectional security filtering.

---

## 5. Composite Model Relationship Patterns

### Cross-Source Relationships
When relationships span different data sources (e.g., Import table → DirectQuery table).

### Rules
- **Limited Cardinality**: Can form **Limited Relationships** (one-to-many only)
- **No Bidirectional**: Cross-source relationships cannot be bidirectional
- **Performance Impact**: Queries may not fold to source

### TMDL Pattern
```tmdl
-- Import dimension
table Dim_Product
	lineageTag: <guid>
	mode: import

-- DirectQuery fact
table Fact_Sales
	lineageTag: <guid>
	mode: directQuery

-- Cross-source relationship
relationship
	fromColumn: Fact_Sales.ProductKey
	toColumn: Dim_Product.ProductKey
	fromCardinality: many
	toCardinality: one
	isActive: true
	crossFilteringBehavior: oneDirection
	relyOnReferentialIntegrity: true
```

### Best Practice: Dual Storage Mode for Dimensions
```tmdl
table Dim_Product
	lineageTag: <guid>
	mode: dual  -- Cached for import, queried for DirectQuery
```

---

## 6. Degenerate Dimensions (No Relationship Pattern)

### Pattern Description
Transaction identifiers (e.g., Order Number, Invoice Number) that don't warrant a separate dimension table.

### When to Use
- Unique transaction identifiers with no descriptive attributes
- High cardinality (millions of unique values)
- Rarely used for filtering or grouping
- No drill-through requirements

### TMDL Structure
```tmdl
table Fact_Sales
	lineageTag: <guid>
	
	column SalesKey
		dataType: int64
		isKey
		isHidden
		sourceColumn: SalesKey
		summarizeBy: none
	
	column OrderNumber
		dataType: string
		sourceColumn: OrderNumber
		summarizeBy: none
		-- No relationship, just a descriptive attribute
	
	column InvoiceNumber
		dataType: string
		sourceColumn: InvoiceNumber
		summarizeBy: none
```

### DAX Usage
```dax
-- Count distinct orders
measure 'Order Count' =
	DISTINCTCOUNT(Fact_Sales[OrderNumber])

-- Filter by specific order
measure 'Sales for Order' =
	VAR SelectedOrder = SELECTEDVALUE(Fact_Sales[OrderNumber])
	VAR OrderSales = 
		CALCULATE(
			SUM(Fact_Sales[SalesAmount]),
			Fact_Sales[OrderNumber] = SelectedOrder
		)
	RETURN
		OrderSales
```

---

## 7. Ambiguous Paths (Critical Anti-Pattern)

### ⛔ Problem Description
**Ambiguous paths** occur when there are MULTIPLE active relationship paths between the same two tables. Power BI cannot resolve which path to use for filtering, causing model load failure.

### Error Signature
```
There are ambiguous paths between '<FactTable>' and '<DimensionTable>':
'<FactTable>'->'<IntermediateDim>'->'<DimensionTable>' and 
'<FactTable>'->'<DimensionTable>'
```

### Common Cause: Redundant Foreign Keys

**INCORRECT Design** (creates 3 ambiguous paths):
```
Fact_Sales:
  - CustomerKey FK → Dim_Customer
  - CountryKey FK → Dim_Country  ❌ REDUNDANT
  - AreaKey FK → Dim_Area        ❌ REDUNDANT
  - IndustryKey FK → Dim_Industry ❌ REDUNDANT

Dim_Customer:
  - CountryKey FK → Dim_Country
  - IndustryKey FK → Dim_Industry

Dim_Country:
  - AreaKey FK → Dim_Area
```

This creates:
1. **Path A**: `Fact_Sales → Dim_Country` (direct)  
   **Path B**: `Fact_Sales → Dim_Customer → Dim_Country` (indirect) ❌ CONFLICT
2. **Path A**: `Fact_Sales → Dim_Area` (direct)  
   **Path B**: `Fact_Sales → Dim_Customer → Dim_Country → Dim_Area` (indirect) ❌ CONFLICT
3. **Path A**: `Fact_Sales → Dim_Industry` (direct)  
   **Path B**: `Fact_Sales → Dim_Customer → Dim_Industry` (indirect) ❌ CONFLICT

### ✅ CORRECT Design (snowflake with single path)
```
Fact_Sales:
  - CustomerKey FK → Dim_Customer  ✅ ONLY this FK
  - ProductKey FK → Dim_Product
  - DateKey FK → Dim_Date
  - SalespersonKey FK → Dim_Salesperson

Dim_Customer:
  - CountryKey FK → Dim_Country
  - IndustryKey FK → Dim_Industry

Dim_Country:
  - AreaKey FK → Dim_Area
```

**Result**: Each dimension is reachable through EXACTLY ONE active path.

### TMDL Example (Corrected Relationships)

```tmdl
relationship a1b2c3d4-e5f6-7890-abcd-ef1234567890
	fromColumn: Fact_Sales.CustomerKey
	toColumn: Dim_Customer.CustomerKey
	fromCardinality: many
	toCardinality: one
	isActive: true
	securityFilteringBehavior: oneDirection
	relyOnReferentialIntegrity: false
	crossFilteringBehavior: oneDirection

relationship b2c3d4e5-f6a7-8901-bcde-f01234567890
	fromColumn: Dim_Customer.CountryKey
	toColumn: Dim_Country.CountryKey
	fromCardinality: many
	toCardinality: one
	isActive: true
	securityFilteringBehavior: oneDirection
	relyOnReferentialIntegrity: false
	crossFilteringBehavior: oneDirection

relationship c3d4e5f6-a7b8-9012-cdef-012345678901
	fromColumn: Dim_Country.AreaKey
	toColumn: Dim_Area.AreaKey
	fromCardinality: many
	toCardinality: one
	isActive: true
	securityFilteringBehavior: oneDirection
	relyOnReferentialIntegrity: false
	crossFilteringBehavior: oneDirection

relationship d4e5f6a7-b8c9-0123-def0-123456789012
	fromColumn: Dim_Customer.IndustryKey
	toColumn: Dim_Industry.IndustryKey
	fromCardinality: many
	toCardinality: one
	isActive: true
	securityFilteringBehavior: oneDirection
	relyOnReferentialIntegrity: false
	crossFilteringBehavior: oneDirection
```

### Detection Rules

Before generating `relationships.tmdl`, **ALWAYS** check:

1. **List all FKs**: For each Fact table, list ALL Foreign Key columns
2. **Trace paths**: For each FK, identify which dimension(s) it connects to (directly or indirectly)
3. **Check for duplicates**: If TWO FKs reach the SAME dimension through different paths → AMBIGUOUS
4. **Remove redundancy**: Keep ONLY the FK to the most granular dimension in the hierarchy

### Design Principle: **Connect to Lowest Grain Only**

✅ **Correct**: Fact connects to the **leaf dimension** in a hierarchy  
❌ **Incorrect**: Fact connects to BOTH the leaf AND parent dimensions

**Example**: For geographic hierarchy (Area → Country → Customer):
- ✅ Fact_Sales has `CustomerKey` (leaf) → walks up to Country and Area
- ❌ Fact_Sales has `CustomerKey` AND `CountryKey` AND `AreaKey` (redundant)

### When Snowflaking is Acceptable

Snowflaking (dimension-to-dimension relationships) is acceptable ONLY IF:
1. The hierarchy is natural and stable (e.g., geography: City → State → Country)
2. Parent dimensions have descriptive attributes beyond the FK (e.g., CountryName, CountryCurrency)
3. The fact table connects ONLY to the lowest grain (leaf dimension)

**Never snowflake if it creates ambiguous paths.**

### DAX Measure Impact

With the corrected design, measures automatically use the single path:

```dax
measure 'Sales by Area' =
    -- Power BI follows: Fact_Sales → Dim_Customer → Dim_Country → Dim_Area
    SUM(Fact_Sales[SalesAmount])
```

No `USERELATIONSHIP()` needed because there's only ONE path.

### Troubleshooting Checklist

If you encounter ambiguous path error:
- [ ] Identify ALL FK columns in the Fact table
- [ ] Map each FK to its target dimension
- [ ] Check if target dimension has FKs to other dimensions (creates hierarchy)
- [ ] If hierarchy exists, remove direct FK from Fact to parent dimensions
- [ ] Keep ONLY the FK to the most granular dimension
- [ ] Regenerate `relationships.tmdl` without redundant relationships
- [ ] Verify: Between any two tables, there is EXACTLY ONE active path

---

## Relationship Configuration Checklist

When defining any relationship, verify:

| Property | Recommendation | Notes |
|----------|---------------|-------|
| **Cardinality** | Set correctly (one-to-many, many-to-many) | Based on actual data inspection |
| **Active** | Only ONE active per FK column | Use inactive for role-playing |
| **Cross-filtering** | `oneDirection` (default) | Bidirectional only for RLS or specific need |
| **Referential Integrity** | `true` for DirectQuery | Improves performance if data is clean |
| **Security Filtering** | Match cross-filtering unless RLS | Typically `bothDirections` for RLS |

---

## MCP Verification Workflow

Before implementing any complex relationship pattern:

1. **Search Microsoft Docs**:
```
microsoft_docs_search: "Power BI relationship cardinality"
microsoft_docs_search: "USERELATIONSHIP DAX function"
microsoft_docs_search: "Power BI many to many relationships"
```

2. **Validate Pattern**:
- Read reference documentation
- Check for Power BI version compatibility
- Verify performance implications

3. **Test Thoroughly**:
- Create sample data
- Test filtering behavior
- Validate measure calculations
- Check performance with large datasets

---

## Anti-Patterns to Avoid

❌ **DON'T**: Create relationships just because columns have similar names  
✅ **DO**: Verify business meaning and cardinality

❌ **DON'T**: Use bidirectional relationships everywhere  
✅ **DO**: Default to single-direction, use bidirectional only when required

❌ **DON'T**: Ignore orphaned records in fact tables  
✅ **DO**: Add "Unknown" dimension members or fix data quality

❌ **DON'T**: Create snowflake schemas with excessive chaining  
✅ **DO**: Flatten into star schema with denormalized dimensions

❌ **DON'T**: Use native many-to-many without understanding implications  
✅ **DO**: Prefer bridge table pattern for clarity and control
