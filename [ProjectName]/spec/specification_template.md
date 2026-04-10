# Semantic Model Specification Template

> **Instructions:** This template provides a structured format for defining functional requirements for Power BI semantic models. Fill in each section with your project-specific information. Replace placeholder text in `<angle brackets>` with actual content. Delete this instruction block before submitting to the agent.

---

## 1. Report Objective & Target Audience

**Report Objective:**
<Describe the primary business goal this report will support. What decisions will it enable?>

**Target Audience:**
<Who will use this report? (e.g., Executive Management, Sales Managers, Financial Analysts, Operations Team)>

**Key Business Questions:**
- <Question 1 the report should answer>
- <Question 2 the report should answer>
- <Question 3 the report should answer>

---

## 2. Key Performance Indicators (KPIs)

> **Note:** Describe KPIs from a **functional perspective**, not technical DAX formulas. Focus on *what* needs to be measured, not *how*.

### KPI 1: <KPI Name>
- **Description:** <What does this KPI measure?>
- **Business Logic:** <How is it calculated in business terms? (e.g., "Total revenue minus total costs")>
- **Format:** <Currency, Percentage, Decimal, Integer>
- **Time Intelligence:** <Current Period, YTD, Prior Year, % Growth, etc.>

### KPI 2: <KPI Name>
- **Description:**
- **Business Logic:**
- **Format:**
- **Time Intelligence:**

### KPI 3: <KPI Name>
- **Description:**
- **Business Logic:**
- **Format:**
- **Time Intelligence:**

*(Add more KPIs as needed)*

---

## 3. Data Groupings & Segmentations

**Primary Groupings:**
<Describe how data should be grouped or segmented for analysis>

Examples:
- By **Geography**: Region -> Country -> City
- By **Customer**: Industry -> Customer Segment -> Individual Customer
- By **Product**: Category -> Subcategory -> Product
- By **Time**: Year -> Quarter -> Month -> Day

**Expected Granularity:**
<What is the lowest level of detail needed? (e.g., "Individual transaction level", "Daily aggregates", "Monthly summaries")>

---

## 4. Filter Dimensions

**Global Filters:**
<List dimensions that should filter the entire report>

Examples:
- Fiscal Year
- Month (single or cumulative YTD)
- Region / Area
- Customer Industry
- Product Category
- Salesperson

**Report-Specific Filters:**
<Any filters specific to certain pages or visuals>

---

## 5. Visualization Structure

> **Note:** The agent will NOT generate Power BI visuals, but needs to understand how the model will be used to optimize data structures and relationships.

### Chart 1: <Chart Name>
- **Type:** <Bar Chart, Line Chart, Combo Chart, Table, Matrix, Bubble Chart, etc.>
- **Purpose:** <What business insight does this chart provide?>
- **Dimensions:** <What fields go on rows/columns/axis?>
- **Measures:** <What KPIs/metrics are displayed?>
- **Drill Path:** <What drill-down paths are needed? (e.g., Area -> Country -> Customer)>

### Chart 2: <Chart Name>
- **Type:**
- **Purpose:**
- **Dimensions:**
- **Measures:**
- **Drill Path:**

### Chart 3: <Chart Name>
- **Type:**
- **Purpose:**
- **Dimensions:**
- **Measures:**
- **Drill Path:**

*(Add more charts as needed)*

---

## 6. Data Schema & Sample Values

### Table 1: <Fact Table Name>

**Description:** <What business events does this table capture?>

| Column Name | Data Type | Description | Sample Values |
|-------------|-----------|-------------|---------------|
| <ColumnName1> | String | <Description> | "ABC123", "XYZ456" |
| <ColumnName2> | Date | <Description> | 2025-01-15, 2025-02-20 |
| <ColumnName3> | Decimal | <Description> | 1500.50, 2300.75 |
| <ColumnName4> | Integer | <Description> | 10, 25, 100 |

### Table 2: <Dimension Table Name>

**Description:** <What master data does this table contain?>

| Column Name | Data Type | Description | Sample Values |
|-------------|-----------|-------------|---------------|
| <ColumnName1> | String | <Description> | "Customer A", "Customer B" |
| <ColumnName2> | String | <Description> | "North", "South", "East", "West" |
| <ColumnName3> | String | <Description> | "Manufacturing", "Retail" |

### Table 3: <Dimension Table Name>

**Description:**

| Column Name | Data Type | Description | Sample Values |
|-------------|-----------|-------------|---------------|
| <ColumnName1> | | | |
| <ColumnName2> | | | |

*(Add more tables as needed)*

---

## 7. Logical Relationships Between Data

**Relationship 1:**
- **From:** `<FactTable>[<ForeignKey>]`
- **To:** `<DimensionTable>[<PrimaryKey>]`
- **Cardinality:** Many-to-One (N:1)
- **Business Logic:** <Explain the relationship in business terms>

**Relationship 2:**
- **From:** `<FactTable>[<ForeignKey>]`
- **To:** `<DimensionTable>[<PrimaryKey>]`
- **Cardinality:** Many-to-One (N:1)
- **Business Logic:**

**Relationship 3:**
- **From:**
- **To:**
- **Cardinality:**
- **Business Logic:**

*(Add more relationships as needed)*

**Special Relationships:**
<Describe any complex patterns>
- **Role-Playing Dimensions:** <e.g., "Date table used for OrderDate, ShipDate, DueDate">
- **Many-to-Many:** <If applicable, describe the bridge table logic>
- **Self-Referencing Hierarchies:** <e.g., "Employee table with ManagerID referencing same table">

---

## 8. Row-Level Security (RLS) Requirements

**Security Requirement:**
<Describe who should see what data>

**Security Filters:**

### Filter 1: <Security Role Name>
- **Affected Table:** `<TableName>`
- **Logic:** <Describe the filter logic in business terms>
- **Example:** "Sales Managers see only their assigned region's data"
- **DAX Concept:** <Optional: provide filter expression if known, e.g., `[Region] = "North"`>

### Filter 2: <Security Role Name>
- **Affected Table:**
- **Logic:**
- **Example:**
- **DAX Concept:**

**Dynamic RLS:**
<If RLS depends on user identity (USERNAME() or USERPRINCIPALNAME()), describe the mapping table structure>

**No RLS Required:**
<Check this box if all users should see all data: ☐>

---

## 9. Functional Requirements

### 9.1 Data Refresh Strategy

> **Why This Matters:** Refresh requirements directly impact the physical model design (Import vs DirectQuery vs Composite, incremental refresh configuration).

**Refresh Frequency:**
<Select one or describe custom schedule>
- [ ] Real-time (data updated continuously, < 1 minute latency)
- [ ] Near Real-time (5-15 minute intervals)
- [ ] Hourly
- [ ] Multiple times per day (specify: ___ times)
- [ ] Daily (specify time: ___)
- [ ] Weekly
- [ ] Monthly
- [ ] On-demand only

**Storage Mode Preference:**
<Based on refresh frequency and data volume>
- [ ] **Import Mode** (default for prototyping, best performance, scheduled refresh. RECOMMENDED for most scenarios and prototyping)
- [ ] **DirectQuery** (real-time queries to source, slower performance, no data caching. In case user wants to prototype using skill 05-mock-data-generation.md, direct query must be discarded given that it is not applicable with CSV)
- [ ] **Composite/Hybrid** (Import for dimensions, DirectQuery for large facts)
- [ ] **Undecided** (let agent recommend based on requirements)

**Expected Data Volumes (Production Environment):**
<Critical for determining refresh strategy>

| Table Type | Table Name | Current Row Count | Expected Growth (12 months) | Estimated Final Size |
|------------|------------|-------------------|----------------------------|---------------------|
| Fact | <FactTableName> | <e.g., 10M rows> | <e.g., +5M/year> | <e.g., 50M rows> |
| Dimension | <DimTableName> | <e.g., 10K rows> | <e.g., +2K/year> | <e.g., 50K rows> |

**Incremental Refresh Requirements:**
<Required for large fact tables in Import mode>
- [ ] **Not needed** (small datasets, full refresh acceptable)
- [ ] **Required** (large fact tables, only refresh recent data)
  - **Audit Field for Incremental Refresh:** `<ColumnName>` (e.g., `LastModifiedDate`, `TransactionDate`, `CreatedDate`)
  - **Data Type:** <Date, DateTime, Integer (epoch)>
  - **Incremental Refresh Window:** <e.g., "Refresh last 7 days", "Refresh current month + last 2 months">
  - **Historical Archive Window:** <e.g., "Keep last 3 years", "Keep all data">

**Source System Update Pattern:**
<How does the source system update data?>
- [ ] **Append-only** (new rows added, existing rows never modified)
- [ ] **Updates in place** (existing rows modified, requires Last Modified Date tracking)
- [ ] **Soft deletes** (deleted rows marked with flag, not physically removed)
- [ ] **Hard deletes** (rows physically removed from source)

**Data Latency Tolerance:**
<What is the acceptable delay between source update and report availability?>
<e.g., "Users can work with data up to 24 hours old", "Must reflect source within 5 minutes">

### 9.2 Other Functional Requirements

**Historical Data Retention:**
<How much historical data is needed? (e.g., "Last 3 years", "All historical data", "Rolling 12 months")>