---
name: powerbi-mock-data-generation
description: Produce realistic CSV mock datasets and align partitions for local validation.
---

# Skill: Mock Data Generation

## Purpose
Generate realistic mock data as CSV files using SDV probabilistic synthesis to validate the PBIP semantic model locally in Power BI Desktop.

## Step Contract

> Governance: `.github/references/workflow-core.md` — context flushing, checkpointing, and stop/approval gate apply automatically.

| | |
|---|---|
| **Reads** | `workflow_state.json` (verify Steps 01-04 completed), TMDL table files (column names and data types) |
| **Writes** | `<ProjectName>/scripts/generate_mock_data.py`, `<ProjectName>/data/*.csv`, updated TMDL partitions |

## Python Environment Setup

Before generating data, verify the Python virtual environment is set up:

### Prerequisites
The user must have **Python 3.10+** installed on their local machine.

### Setup Commands
```powershell
# Navigate to the repository root
cd <repository-root>

# Create virtual environment (if not already done)
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Install required packages (all steps)
pip install -r requirements.txt
```

### Verify Installation
```powershell
python -c "import pandas; import sdv; import faker; print('OK')"
```

## Script Generation Rules

### Technology
- Use **Python** with `pandas` and `sdv` libraries.
- Use `faker` only to bootstrap compact seed datasets when no source extracts are available.
- Generate ONE script file: `<ProjectName>/scripts/generate_mock_data.py`
- Output CSV files to `<ProjectName>/data/` folder.

### SDV Strategy for Star Schema Models
Use a star-schema-oriented generation flow optimized for performance and referential integrity:

1. Generate deterministic seed datasets for conformed dimensions:
    - `Dim_Date` MUST remain fully programmatic.
    - Low-cardinality dimensions may use controlled lists or `faker` to create a compact bootstrap sample.
2. Build SDV metadata from the seed tables and explicitly define primary keys and fact-to-dimension relationships.
3. Prefer a **hybrid SDV strategy** for performance:
    - Use SDV single-table synthesizers for dimensions.
    - Use an SDV probabilistic synthesizer for each fact table with FK columns treated as categorical business keys.
4. Use `HMASynthesizer` only when preserving cross-table dependency structure is more important than runtime.
5. After sampling, run post-processing to enforce integer keys, decimal precision, null rules, and orphan-key repair.

This hybrid pattern is preferred for Power BI star schemas because dimensions are usually small and stable, while fact tables require faster generation at higher volumes.

### Data Quality Requirements
1. **Referential Integrity**: ALL Foreign Keys in Fact tables MUST exist as Primary Keys in the corresponding Dimension tables.
2. **Data Type Consistency**: Generated data types must EXACTLY match the TMDL `dataType` definitions.
3. **Realistic Values**: Use SDV probabilistic synthesis to learn realistic value distributions from the bootstrap seed data. Use `faker` only to create the minimal seed sample when needed.
4. **Volume**: Generate sufficient data for meaningful visuals:
   - Dimension tables: 20-100 rows (depending on cardinality)
   - Fact tables: 500-2000 rows
   - Date dimension: Full fiscal year(s) — one row per day

### Date Dimension Generation
The `Dim_Date` table MUST be generated programmatically covering the required fiscal year range:
```python
import pandas as pd

def generate_dim_date(start_date, end_date, fiscal_year_start_month=7):
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    df = pd.DataFrame({'Date': dates})
    df['DateKey'] = df['Date'].dt.strftime('%Y%m%d').astype(int)
    df['Year'] = df['Date'].dt.year.astype(str)
    df['Quarter'] = 'Q' + df['Date'].dt.quarter.astype(str)
    df['Month'] = df['Date'].dt.month
    df['MonthName'] = df['Date'].dt.strftime('%B')
    df['DayOfWeek'] = df['Date'].dt.dayofweek + 1
    df['DayName'] = df['Date'].dt.strftime('%A')
    df['IsWeekend'] = df['DayOfWeek'].isin([6, 7])
    # Fiscal year logic
    df['FiscalYear'] = df['Date'].apply(
        lambda d: f"FY{d.year + 1}" if d.month >= fiscal_year_start_month else f"FY{d.year}"
    )
    df['FiscalMonth'] = df['Date'].apply(
        lambda d: ((d.month - fiscal_year_start_month) % 12) + 1
    )
    df['FiscalQuarter'] = 'FQ' + ((df['FiscalMonth'] - 1) // 3 + 1).astype(str)
    return df
```

### SDV Metadata and Sampling Pattern
```python
from sdv.metadata import MultiTableMetadata, SingleTableMetadata
from sdv.single_table import GaussianCopulaSynthesizer

def build_metadata(dim_date_seed, dim_customer_seed, dim_area_seed, fact_sales_seed):
    metadata = MultiTableMetadata()
    metadata.detect_table_from_dataframe(table_name='Dim_Date', data=dim_date_seed)
    metadata.detect_table_from_dataframe(table_name='Dim_Customer', data=dim_customer_seed)
    metadata.detect_table_from_dataframe(table_name='Dim_Area', data=dim_area_seed)
    metadata.detect_table_from_dataframe(table_name='Fact_Sales', data=fact_sales_seed)

    metadata.set_primary_key(table_name='Dim_Date', column_name='DateKey')
    metadata.set_primary_key(table_name='Dim_Customer', column_name='CustomerKey')
    metadata.set_primary_key(table_name='Dim_Area', column_name='AreaKey')
    metadata.set_primary_key(table_name='Fact_Sales', column_name='SalesKey')

    metadata.add_relationship(
        parent_table_name='Dim_Date',
        parent_primary_key='DateKey',
        child_table_name='Fact_Sales',
        child_foreign_key='DateKey',
    )
    metadata.add_relationship(
        parent_table_name='Dim_Customer',
        parent_primary_key='CustomerKey',
        child_table_name='Fact_Sales',
        child_foreign_key='CustomerKey',
    )
    metadata.add_relationship(
        parent_table_name='Dim_Area',
        parent_primary_key='AreaKey',
        child_table_name='Fact_Sales',
        child_foreign_key='AreaKey',
    )
    return metadata

def synthesize_dimension(seed_df, num_rows):
    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(data=seed_df)
    synthesizer = GaussianCopulaSynthesizer(metadata)
    synthesizer.fit(seed_df)
    return synthesizer.sample(num_rows=num_rows)
```

### Fact Table Generation Pattern
```python
from sdv.metadata import SingleTableMetadata
from sdv.single_table import GaussianCopulaSynthesizer

def generate_fact_sales(dim_date, dim_customer, dim_area, fact_seed, num_rows=1000):
    fact_metadata = SingleTableMetadata()
    fact_metadata.detect_from_dataframe(data=fact_seed)
    synthesizer = GaussianCopulaSynthesizer(fact_metadata)
    synthesizer.fit(fact_seed)
    df = synthesizer.sample(num_rows=num_rows)

    df['DateKey'] = df['DateKey'].where(df['DateKey'].isin(dim_date['DateKey']), dim_date['DateKey'].sample(len(df), replace=True).to_numpy())
    df['CustomerKey'] = df['CustomerKey'].where(df['CustomerKey'].isin(dim_customer['CustomerKey']), dim_customer['CustomerKey'].sample(len(df), replace=True).to_numpy())
    df['AreaKey'] = df['AreaKey'].where(df['AreaKey'].isin(dim_area['AreaKey']), dim_area['AreaKey'].sample(len(df), replace=True).to_numpy())
    df['AdjustedProfitLC'] = df[['AdjustedProfitLC', 'SalesAmountLC']].min(axis=1)

    return df
```

### When to Use `HMASynthesizer`
- Use `HMASynthesizer` when you already have a representative relational seed dataset and must preserve multi-table correlations across the entire star schema.
- Do NOT make `HMASynthesizer` the default for Step 05 when the goal is fast local mock generation for Power BI validation.
- If `HMASynthesizer` is used, keep the seed dataset compact and sample up to the target row counts instead of fitting on large bootstrap datasets.

### CSV Output
- Files go to `<ProjectName>/data/` folder
- Use comma delimiter, **UTF-8 encoding WITHOUT BOM**, no index
- Filename convention: lowercase table name (e.g., `dim_date.csv`, `fact_sales.csv`)

```python
df.to_csv('<ProjectName>/data/dim_date.csv', index=False, encoding='utf-8')
```

**CRITICAL**: Pandas `encoding='utf-8'` generates UTF-8 **without BOM** by default, which is the format required by Power BI Desktop for TMDL parsing. Do NOT use other tools (like PowerShell `WriteAllText`) to modify CSV files after generation, as they may add a BOM and cause parsing errors.

## TMDL Partition Update

After generating CSVs, update each table's TMDL partition `source` expression to point to the correct CSV path.

The M expression should use **absolute paths** for local development:
```
source =
	let
		Source = Csv.Document(File.Contents("C:\path\to\repo\<ProjectName>\data\dim_date.csv"), [Delimiter = ",", Columns = 12, Encoding = 65001, QuoteStyle = QuoteStyle.None]),
		PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true])
	in
		PromotedHeaders
```

Alternatively, use a **parameterized path** via `expressions.tmdl`:
```
expression DataPath = "C:\path\to\repo\<ProjectName>\data" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true]
```

Then reference in partition source:
```
Source = Csv.Document(File.Contents(DataPath & "\dim_date.csv"), [Delimiter = ",", Columns = 12, Encoding = 65001, QuoteStyle = QuoteStyle.None])
```

## Lift and Shift Strategy — Transition to Production Data Source

**Important**: CSV files are intended as **temporary mock data** for local development and validation. In production, the semantic model will connect directly to a database (SQL Server, Azure SQL, Fabric Lakehouse, etc.).

### Recommended Approach for Easy Migration

#### Option 1: Parameterized Source (Recommended)
Create a shared M parameter in `expressions.tmdl` that controls the data source type:

```tmdl
expression SourceType = "CSV" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true]

expression DataPath = "C:\path\to\repo\<ProjectName>\data" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true]

expression DatabaseConnectionString = "Server=myserver;Database=mydb" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = false]
```

Then in each table partition, use conditional logic:
```m
source =
	let
		CSVSource = Csv.Document(File.Contents(DataPath & "\dim_date.csv"), [Delimiter = ",", Columns = 12, Encoding = 65001, QuoteStyle = QuoteStyle.None]),
		DatabaseSource = Sql.Database("myserver", "mydb"){[Schema="dbo",Item="Dim_Date"]}[Data],
		Source = if SourceType = "CSV" then CSVSource else DatabaseSource,
		PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true])
	in
		PromotedHeaders
```

**Advantage**: Switch between CSV and database by changing a single parameter value.

#### Option 2: Replace Partition Source (Simpler)
When ready for production, replace the entire partition `source` expression in each table's TMDL file:

**Before (CSV mock)**:
```m
source =
	let
		Source = Csv.Document(File.Contents("C:\...\<ProjectName>\data\dim_date.csv"), ...),
```

**After (SQL Database)**:
```m
source =
	let
		Source = Sql.Database("myserver.database.windows.net", "mydatabase"){[Schema="dbo",Item="Dim_Date"]}[Data],
```

**Advantage**: Simpler partition expressions (no conditional logic). Use Power BI Desktop's "Transform Data" UI to reconnect to the database, then save the TMDL changes.

#### Option 3: Fabric Lakehouse (Direct Lake)
For Fabric-based deployments, the partition mode changes from `import` to `directLake`:

```tmdl
partition Dim_Date = entity
	mode: directLake
	source
		schemaName: dbo
		tableName: Dim_Date
		expressionSource: DatabaseQuery
```

**Note**: This requires the semantic model to be published to a Fabric workspace and connected to a Lakehouse.

### Best Practice Recommendation
- Use **Option 1** (parameterized source) during Step 05 if you anticipate frequent switching between mock and real data during development.
- Use **Option 2** (replace partition source) for simpler models where the transition happens only once before production deployment.
- For Fabric deployments, plan for **Option 3** (Direct Lake) from the beginning if your target data platform is Fabric Lakehouse.

## Validation Before Output
- [ ] All FK values in fact tables exist in corresponding dimension PKs
- [ ] CSV column names match TMDL `sourceColumn` values exactly
- [ ] Data types are consistent (integers for keys, decimals for amounts)
- [ ] Date dimension covers the full required date range
- [ ] SDV metadata declares PK/FK relationships explicitly
- [ ] Post-processing repairs any orphan FK values before CSV export
- [ ] CSV files are comma-delimited, UTF-8 encoded
- [ ] Script runs without errors in the `.venv` environment

**STOP. Save primary artifact → update `workflow_state.json` → await user approval.**