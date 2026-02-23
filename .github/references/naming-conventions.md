# Naming Conventions for Power BI Semantic Models

> Consistent naming ensures readability, maintainability, and a professional semantic model.
> ALL names in TMDL, DAX, and file output MUST follow these conventions.

---

## 1. Table Naming

| Object Type | Convention | Example |
|------------|-----------|---------|
| Fact table | `Fact_<BusinessProcess>` PascalCase | `Fact_Sales`, `Fact_Budget` |
| Dimension table | `Dim_<Entity>` PascalCase | `Dim_Date`, `Dim_Customer`, `Dim_Area` |
| Measures table | `_Measures` (underscore prefix) | `_Measures` |
| Bridge table | `Bridge_<Description>` PascalCase | `Bridge_CustomerIndustry` |
| Security table | `Security_<Description>` PascalCase | `Security_UserAreaMapping` |

### Rules:
- Use **PascalCase** after the prefix.
- Use **singular nouns** for dimensions (`Dim_Customer`, not `Dim_Customers`).
- The underscore prefix on `_Measures` ensures it sorts to the top of the field list.
- Avoid abbreviations unless universally understood (e.g., `LC` for Local Currency).

---

## 2. Column Naming

| Column Type | Convention | Example |
|------------|-----------|---------|
| Surrogate Key (PK) | `<Entity>Key` PascalCase | `DateKey`, `CustomerKey`, `SalesKey` |
| Foreign Key (FK) | Same as the PK it references | `DateKey`, `CustomerKey` |
| Descriptive attribute | PascalCase, descriptive | `CustomerName`, `Country`, `FiscalYear` |
| Amount / Currency | `<Description><Currency>` | `SalesAmountLC`, `BudgetAmountLC` |
| Percentage | `<Description>Pct` or `<Description>Percent` | `AdjustedProfitPct` |
| Boolean / Flag | `Is<Description>` | `IsCurrent`, `IsWeekend`, `IsActive` |
| Date column | `Date` or `<Qualifier>Date` | `Date`, `OrderDate`, `ShipDate` |
| Count column | `<Description>Count` | `TransactionCount` |
| SCD columns | `ValidFrom`, `ValidTo`, `IsCurrent` | `ValidFrom`, `ValidTo` |

### Rules:
- Use **PascalCase** for all column names.
- **DO NOT** use spaces in `sourceColumn` values (the M source column name). Use PascalCase.
- Display names in TMDL (the object name) CAN have spaces: `'Sales Amount LC'`.
- `sourceColumn` maps to the CSV header: `sourceColumn: SalesAmountLC`.
- ALL keys (PK and FK) must have `summarizeBy: none` and be `isHidden`.
- ALL FK columns in Fact tables must be `isHidden`.

---

## 3. Measure Naming

| Measure Type | Convention | Example |
|-------------|-----------|---------|
| Base aggregation | Descriptive noun phrase | `'Sales Amount'`, `'Total Quantity'` |
| Time intelligence - YTD | `<Base> FYTD` or `<Base> YTD` | `'Sales Amount FYTD'` |
| Time intelligence - PY | `<Base> PY` | `'Sales Amount PY'` |
| Time intelligence - MoM | `<Base> MoM` | `'Sales Amount MoM'` |
| Variance | `<Metric> vs <Metric>` | `'Sales vs Budget'` |
| Variance percentage | `<Metric> vs <Metric> %` | `'Sales vs Budget %'` |
| Percentage / Ratio | `<Description> %` | `'Adjusted Profit %'` |
| Average | `Avg <Description>` or `Average <Description>` | `'Avg Monthly Sales'` |
| Count | `# <Entity>` or `Count of <Entity>` | `'# Customers'`, `'# Transactions'` |
| Status / Category | `<Description> Status` | `'Budget Status'` |

### Rules:
- Measure names are **user-facing** — use natural language with spaces.
- Enclose in single quotes in TMDL: `measure 'Sales Amount' = ...`
- Use `displayFolder` to organize measures into logical groups.
- ALWAYS prefix percentage measures with the metric name, suffix with `%`.

---

## 4. Relationship Naming

Relationships in TMDL use GUIDs as identifiers:
```tmdl
relationship a1b2c3d4-e5f6-7890-abcd-ef1234567890
	fromColumn: Fact_Sales.DateKey
	toColumn: Dim_Date.DateKey
```

- Generate a unique GUID for each relationship.
- Use comments (`///`) above the relationship to describe it if needed.

---

## 5. File Naming

| File Type | Convention | Example |
|----------|-----------|---------|
| Table TMDL | `<TableName>.tmdl` PascalCase matching table name | `Dim_Date.tmdl`, `Fact_Sales.tmdl` |
| CSV data | `<table_name>.csv` lowercase with underscores | `dim_date.csv`, `fact_sales.csv` |
| Python script | `generate_mock_data.py` | `generate_mock_data.py` |
| Root TMDL files | lowercase | `model.tmdl`, `database.tmdl`, `relationships.tmdl`, `expressions.tmdl` |

---

## 6. Display Folder Organization

Organize measures into `displayFolder` categories:

| Folder Name | Contents |
|------------|---------|
| `Sales` | Revenue and volume base measures |
| `Budget` | Budget amounts and comparisons |
| `Profitability` | Margin, profit, cost measures |
| `Time Intelligence` | YTD, PY, MoM variants |
| `KPIs` | Status indicators and targets |

---

## 7. Anti-Patterns (DO NOT)

| Anti-Pattern | Correct Pattern |
|-------------|----------------|
| `tbl_sales`, `dimCustomer` | `Fact_Sales`, `Dim_Customer` |
| `SalesAmt`, `CustNm` | `SalesAmountLC`, `CustomerName` |
| `measure1`, `m_sales` | `'Sales Amount'`, `'Total Quantity'` |
| Spaces in `sourceColumn` | PascalCase: `SalesAmountLC` |
| `/` in measure names | Use words: `'Sales vs Budget %'` |
| `ID` suffix for keys | Use `Key` suffix: `CustomerKey` |
| `Date_dim`, `FACT_SALES` | `Dim_Date`, `Fact_Sales` |
