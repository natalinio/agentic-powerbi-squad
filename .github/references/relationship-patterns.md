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
