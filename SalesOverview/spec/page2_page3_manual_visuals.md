# Manual Build Pack  Page2 + Page3

## Page 2  Detail Analysis (build manually)

### Slicers (top row)
1. Fiscal Year  field: Dim_Date[FiscalYear]  type: Dropdown
2. Area  field: Dim_Area[AreaName]  type: Dropdown
3. Industry  field: Dim_Industry[IndustryName]  type: Dropdown

### Visuals
1. Table  Sales (LC) by Customer
   - Rows: Dim_Customer[CustomerName]
   - Values: [Sales Amount FYTD]
   - Sort: [Sales Amount FYTD] descending

2. Table  Sales (LC) by Customer Country
   - Rows: Dim_Customer[Country]
   - Values: [Sales Amount FYTD]
   - Sort: [Sales Amount FYTD] descending

3. Table  Sales (LC) by Salesperson
   - Rows: Dim_Salesperson[SalespersonName]
   - Values: [Sales Amount FYTD]
   - Sort: [Sales Amount FYTD] descending

4. Table  Sales (LC) by Industry
   - Rows: Dim_Industry[IndustryName]
   - Values: [Sales Amount FYTD]
   - Sort: [Sales Amount FYTD] descending

## Page 3  Visual Lab Native (build manually)

### Slicers (top row)
1. Fiscal Year  Dim_Date[FiscalYear]
2. Area  Dim_Area[AreaName]
3. Industry  Dim_Industry[IndustryName]

### Visual set (native visuals not covered in Page1/Page2)
1. Funnel  Sales by Fiscal Quarter
   - Category/Group: Dim_Date[FiscalQuarter]
   - Values: [Sales Amount]

2. Treemap  Sales by Industry and Country
   - Group: Dim_Industry[IndustryName]
   - Details: Dim_Customer[Country]
   - Values: [Sales Amount FYTD]

3. Gauge  Sales vs Budget Gauge
   - Value: [Sales Amount FYTD]
   - Target value: [Budget Amount FYTD]
   - Min: 0
   - Max: [Budget Amount FYTD] * 1.5 (manual/static if needed)

4. Waterfall  Sales vs Budget Variance by Fiscal Month
   - Category: Dim_Date[FiscalMonth]
   - Y axis: [Sales vs Budget]
   - Sort category by: Dim_Date[FiscalMonthNumber]

5. Ribbon chart  Sales Rank by Area over Fiscal Month
   - Axis: Dim_Date[FiscalMonth]
   - Legend: Dim_Area[AreaName]
   - Values: [Sales Amount]
   - Sort axis by: Dim_Date[FiscalMonthNumber]

6. Donut chart  Sales Mix by Industry
   - Legend/Category: Dim_Industry[IndustryName]
   - Values: [Sales Amount FYTD]

7. Pie chart  Sales Mix by Area
   - Legend/Category: Dim_Area[AreaName]
   - Values: [Sales Amount FYTD]

8. Map  Sales by Country
   - Location: Dim_Customer[Country]
   - Bubble size: [Sales Amount FYTD]

## Selection Pane naming pattern (important for reverse engineering)

Use this pattern for each visual title in Selection Pane:
- <Component> - <DataReference>

Examples:
- Funnel - Sales Amount by FiscalQuarter
- Treemap - Sales Amount FYTD by IndustryName and Country
- Gauge - Sales Amount FYTD vs Budget Amount FYTD
- Waterfall - Sales vs Budget by FiscalMonth
- Map - Sales Amount FYTD by Country
