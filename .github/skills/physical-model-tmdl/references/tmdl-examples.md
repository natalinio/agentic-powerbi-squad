# TMDL Examples — Key Patterns

Curated real-world TMDL patterns for reference. Adapted from production models. Use these as validated templates when authoring TMDL.

## 1. Dimension Table with Hierarchy

```tmdl
table Dim_Region
	lineageTag: <guid>

	column RegionKey
		dataType: int64
		isKey
		isHidden
		sourceColumn: RegionKey
		summarizeBy: none
		lineageTag: <guid>

	column Territory
		dataType: string
		displayFolder: 1. Region Hierarchy
		sourceColumn: Territory
		summarizeBy: none
		lineageTag: <guid>

		annotation SummarizationSetBy = Automatic

	column Station
		dataType: string
		displayFolder: 1. Region Hierarchy
		sourceColumn: Station
		summarizeBy: none
		lineageTag: <guid>

		annotation SummarizationSetBy = Automatic

	column Country
		dataType: string
		displayFolder: 2. Attributes
		sourceColumn: Country
		summarizeBy: none
		lineageTag: <guid>

		annotation SummarizationSetBy = Automatic

	hierarchy 'Region Hierarchy'
		displayFolder: 1. Region Hierarchy
		lineageTag: <guid>

		level Territory
			lineageTag: <guid>
			column: Territory

		level Station
			lineageTag: <guid>
			column: Station

	partition Dim_Region = m
		mode: import
		source =
			let
				Source = Csv.Document(File.Contents("<path>/dim_region.csv"), [Delimiter = ",", Columns = 4, Encoding = 65001, QuoteStyle = QuoteStyle.None]),
				PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
				ChangedTypes = Table.TransformColumnTypes(PromotedHeaders, {{"RegionKey", Int64.Type}, {"Territory", type text}, {"Station", type text}, {"Country", type text}})
			in
				ChangedTypes
```

## 2. Measures with Descriptions and Display Folders

```tmdl
/// Total actual amounts in local currency.
measure Actuals =
		SUM ( Fact_Sales[SalesAmountLC] )
	formatString: #,##0.00
	displayFolder: Sales
	lineageTag: <guid>

/// Total actuals month-to-date.
measure 'Actuals MTD' =
		CALCULATE (
		    [Actuals],
		    DATESMTD ( Dim_Date[Date] )
		)
	formatString: #,##0.00
	displayFolder: Sales\Time Intelligence
	lineageTag: <guid>

/// Year-to-date sales target vs actuals expressed as a percentage delta.
measure 'Sales Target YTD vs Actuals (%)' =
		VAR TargetYTD = [Sales Target YTD]
		VAR ActualsYTD = [Actuals YTD]
		VAR DeltaPct = DIVIDE ( ActualsYTD - TargetYTD, TargetYTD )
		RETURN
		    DeltaPct
	formatString: 0.0%;-0.0%;0.0%
	displayFolder: Sales\Comparison
	lineageTag: <guid>
```

## 3. Relationships — Active and Inactive

```tmdl
// Standard many-to-one (Fact → Dim)
relationship <guid>
	fromColumn: Fact_Sales.DateKey
	toColumn: Dim_Date.DateKey

relationship <guid>
	fromColumn: Fact_Sales.CustomerKey
	toColumn: Dim_Customer.CustomerKey

// Many-to-many via bridge (note toCardinality: many)
relationship <guid>
	toCardinality: many
	fromColumn: Fact_Forecast.ProductType
	toColumn: Dim_Product.Type

/// Inactive relationship for analyzing by requested delivery date via USERELATIONSHIP
relationship <guid>
	isActive: false
	fromColumn: Fact_Orders.RequestedDeliveryDateKey
	toColumn: Dim_Date.DateKey
```

## 4. Calculated Table (Measures Container)

```tmdl
table _Measures
	lineageTag: <guid>

	measure Placeholder = 0
		lineageTag: <guid>

	partition _Measures = calculated
		mode: import
		source = {1}
```

**Note:** Using `partition = calculated` with `source = {1}` is the standard pattern for a disconnected measures table. An alternative uses `partition = m` with `source = #table({"Value"}, {{""}})`.

## 5. Role-Level Security (RLS)

```tmdl
role 'Territory Managers'
	modelPermission: read

	tablePermission Dim_Region = Dim_Region[Territory] = USERPRINCIPALNAME()
```

For more complex RLS with reusable logic, consider DAX UDFs:
```tmdl
role 'Account Managers'
	modelPermission: read

	tablePermission Dim_Customer = RLS.ApplySimpleRLS ( Dim_Customer[AccountManager] )
```

## 6. Shared M Expression Parameter

```tmdl
expression DataPath = "C:\Data\PowerBI" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true]
	lineageTag: <guid>
	queryGroup: Parameters
```

## 7. Column with sortByColumn

```tmdl
column MonthName
	dataType: string
	displayFolder: 2. Month
	sourceColumn: MonthName
	summarizeBy: none
	sortByColumn: MonthNumber
	lineageTag: <guid>

	annotation SummarizationSetBy = Automatic
```

## 8. Measure with formatStringDefinition (Dynamic Format)

```tmdl
measure 'Sales Target MTD vs Actuals (%)' =
		VAR TargetMTD = [Sales Target MTD]
		VAR DeltaPct = DIVIDE ( [Actuals MTD] - TargetMTD, TargetMTD )
		RETURN DeltaPct
	displayFolder: Sales\Comparison
	lineageTag: <guid>

	formatStringDefinition =
			IF (
			    [Sales Target MTD vs Actuals (%)] >= 0,
			    "↑ 0.0%;↓ 0.0%;0.0%",
			    "↓ 0.0%;↑ 0.0%;0.0%"
			)
```

## 9. Date Table Pattern (Calculated)

```tmdl
table Dim_Date
	dataCategory: Time
	lineageTag: <guid>

	column Date
		dataType: dateTime
		isKey
		formatString: yyyy-MM-dd
		sourceColumn: [Date]
		summarizeBy: none
		lineageTag: <guid>

	column Year
		dataType: int64
		sourceColumn: [Year]
		summarizeBy: none
		lineageTag: <guid>

	column IsDateInScope
		dataType: boolean
		isHidden
		sourceColumn: [IsDateInScope]
		summarizeBy: none
		lineageTag: <guid>

	partition Dim_Date = calculated
		mode: import
		source =
			// Calculated date table DAX goes here
			// CALENDAR, ADDCOLUMNS, etc.
```

## 10. model.tmdl — Complete Example

```tmdl
model Model
	culture: en-US
	defaultPowerBIDataSourceVersion: powerBI_V3
	discourageImplicitMeasures

	annotation __PBI_TimeIntelligenceEnabled = 0

ref table Dim_Date
ref table Dim_Customer
ref table Dim_Area
ref table Fact_Sales
ref table Fact_Budget
ref table _Measures
```

Key elements:
- `defaultPowerBIDataSourceVersion: powerBI_V3` — **MANDATORY** for Power BI Desktop 2025+
- `discourageImplicitMeasures` — best practice to enforce explicit measures
- `__PBI_TimeIntelligenceEnabled = 0` — disables auto date/time tables
- `ref table` entries define collection ordering for source control stability
