# Mock Data Generation Setup

## Prerequisites

- Python 3.10 or higher installed
- PowerShell (Windows) or Terminal (macOS/Linux)

## Setup Instructions

### 1. Create Virtual Environment

Navigate to the repository root and create a Python virtual environment:

```powershell
# Windows PowerShell
cd c:\Users\andrea.natali\OneDrive - Avanade\Documents\Progetti\Avanade\Repos\aisemanticlayer

python -m venv .venv
```

### 2. Activate Virtual Environment

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# If you get an execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. Install Required Packages

```powershell
pip install pandas faker
```

### 4. Verify Installation

```powershell
python -c "import pandas; import faker; print('✓ Dependencies installed successfully')"
```

### 5. Generate Mock Data

```powershell
python scripts/generate_mock_data.py
```

Expected output:
```
============================================================
MOCK DATA GENERATION - Sales Overview FYTD
============================================================

[1/10] Generating Dim_Date...
   ✓ Generated 2922 rows

[2/10] Generating Dim_Area...
   ✓ Generated 5 rows

...

============================================================
DATA GENERATION COMPLETED SUCCESSFULLY!
============================================================
```

### 6. Verify Generated Files

Check the `PBIP/data/` folder. You should see:
- `dim_date.csv`
- `dim_area.csv`
- `dim_country.csv`
- `dim_customer.csv`
- `dim_industry.csv`
- `dim_salesperson.csv`
- `fact_sales.csv`
- `fact_budget.csv`
- `measure_info.csv`
- `parameters.csv`

### 7. Open Power BI Desktop

1. Open `PBIP/SalesOverviewFYTD.pbip` in Power BI Desktop
2. Go to Transform Data > Refresh All
3. Close and Apply
4. Verify data loaded successfully

## Configuration

### Change Fiscal Year Start Month

Edit `PBIP/data/parameters.csv`:
```csv
ParameterName,ParameterValue
FiscalYearStartMonth,7
```

Change `7` to the desired month (1=January, 7=July, etc.)

Then regenerate `dim_date.csv`:
```python
python scripts/generate_mock_data.py
```

### Adjust Data Volume

Edit `scripts/generate_mock_data.py` and modify these parameters:
```python
dim_customer = generate_dim_customer(dim_country, dim_industry, n_customers=100)  # Change 100
dim_salesperson = generate_dim_salesperson(n_salespeople=20)  # Change 20
fact_sales = generate_fact_sales(..., n_transactions=2000)  # Change 2000
```

## Troubleshooting

### "pandas not found"
Solution: Make sure virtual environment is activated and packages are installed:
```powershell
.\.venv\Scripts\Activate.ps1
pip install pandas faker
```

### "File path not found" in Power BI
Solution: Close Power BI Desktop, regenerate data, then reopen the PBIP file.

### "Encoding error"
Solution: The script uses UTF-8 encoding. If you see special characters incorrectly, verify your Power BI Desktop locale settings.
