"""
Mock Data Generator for SalesOverview PBIP project.
Generates CSV files matching the TMDL semantic model schema.

Fiscal Year: starts July (FY2025 = Jul 2024 - Jun 2025)
Output: SalesOverview/data/*.csv
"""

import os
import random
import pandas as pd
from faker import Faker

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SEED = 42
random.seed(SEED)
fake = Faker()
Faker.seed(SEED)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

FISCAL_YEAR_START_MONTH = 7  # July
DATE_START = "2024-07-01"    # FY2025 start
DATE_END = "2026-06-30"      # FY2026 end

NUM_AREAS = 6
NUM_CUSTOMERS = 50
NUM_INDUSTRIES = 8
NUM_SALESPERSONS = 15
NUM_SALES_ROWS = 1500

# ---------------------------------------------------------------------------
# Dim_Date
# ---------------------------------------------------------------------------
def generate_dim_date(start_date: str, end_date: str, fy_start_month: int = 7) -> pd.DataFrame:
    dates = pd.date_range(start=start_date, end=end_date, freq="D")
    df = pd.DataFrame({"Date": dates})
    df["DateKey"] = df["Date"].dt.strftime("%Y%m%d").astype(int)
    df["CalendarYear"] = df["Date"].dt.year
    df["CalendarMonth"] = df["Date"].dt.month
    df["MonthName"] = df["Date"].dt.strftime("%B")
    df["CalendarQuarter"] = "Q" + df["Date"].dt.quarter.astype(str)

    def _fiscal_year(d):
        return f"FY{d.year + 1}" if d.month >= fy_start_month else f"FY{d.year}"

    def _fiscal_month_number(d):
        return ((d.month - fy_start_month) % 12) + 1

    df["FiscalYear"] = df["Date"].apply(_fiscal_year)
    df["FiscalMonthNumber"] = df["Date"].apply(_fiscal_month_number)
    df["FiscalMonth"] = "FM" + df["FiscalMonthNumber"].astype(str).str.zfill(2)
    df["FiscalQuarter"] = "FQ" + ((df["FiscalMonthNumber"] - 1) // 3 + 1).astype(str)
    df["FiscalYearMonth"] = df["FiscalYear"] + "-" + df["FiscalMonthNumber"].astype(str).str.zfill(2)
    df["IsWeekend"] = df["Date"].dt.dayofweek.isin([5, 6])

    col_order = [
        "DateKey", "Date", "CalendarYear", "CalendarMonth", "MonthName",
        "CalendarQuarter", "FiscalYear", "FiscalMonthNumber", "FiscalMonth",
        "FiscalQuarter", "FiscalYearMonth", "IsWeekend",
    ]
    return df[col_order]


# ---------------------------------------------------------------------------
# Dim_Area
# ---------------------------------------------------------------------------
AREA_NAMES = ["North America", "EMEA", "APAC", "LATAM", "Southern Europe", "Northern Europe"]

def generate_dim_area() -> pd.DataFrame:
    rows = [{"AreaKey": i + 1, "AreaName": name} for i, name in enumerate(AREA_NAMES[:NUM_AREAS])]
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Dim_Customer  (each customer assigned to one area & one country)
# ---------------------------------------------------------------------------
COUNTRIES_BY_AREA = {
    "North America": ["United States", "Canada", "Mexico"],
    "EMEA": ["United Kingdom", "Germany", "France", "Netherlands"],
    "APAC": ["Japan", "Australia", "Singapore", "India"],
    "LATAM": ["Brazil", "Argentina", "Colombia", "Chile"],
    "Southern Europe": ["Italy", "Spain", "Portugal", "Greece"],
    "Northern Europe": ["Sweden", "Norway", "Denmark", "Finland"],
}

def generate_dim_customer(dim_area: pd.DataFrame) -> pd.DataFrame:
    rows = []
    area_names = dim_area["AreaName"].tolist()
    for i in range(NUM_CUSTOMERS):
        area = random.choice(area_names)
        country = random.choice(COUNTRIES_BY_AREA[area])
        rows.append({
            "CustomerKey": i + 1,
            "CustomerName": fake.company(),
            "Country": country,
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Dim_Industry
# ---------------------------------------------------------------------------
INDUSTRY_NAMES = [
    "Technology", "Healthcare", "Financial Services", "Manufacturing",
    "Retail", "Energy", "Telecommunications", "Transportation",
]

def generate_dim_industry() -> pd.DataFrame:
    rows = [{"IndustryKey": i + 1, "IndustryName": name} for i, name in enumerate(INDUSTRY_NAMES[:NUM_INDUSTRIES])]
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Dim_Salesperson
# ---------------------------------------------------------------------------
def generate_dim_salesperson() -> pd.DataFrame:
    rows = [{"SalespersonKey": i + 1, "SalespersonName": fake.name()} for i in range(NUM_SALESPERSONS)]
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Helper: build customer -> area mapping for referential integrity
# ---------------------------------------------------------------------------
def build_customer_area_map(dim_customer: pd.DataFrame, dim_area: pd.DataFrame) -> dict:
    """Return {CustomerKey: AreaKey} based on country -> area mapping."""
    country_to_area = {}
    for area_name, countries in COUNTRIES_BY_AREA.items():
        for c in countries:
            country_to_area[c] = area_name
    area_name_to_key = dict(zip(dim_area["AreaName"], dim_area["AreaKey"]))
    mapping = {}
    for _, row in dim_customer.iterrows():
        area_name = country_to_area.get(row["Country"], random.choice(dim_area["AreaName"].tolist()))
        mapping[row["CustomerKey"]] = area_name_to_key[area_name]
    return mapping


# ---------------------------------------------------------------------------
# Fact_Sales
# ---------------------------------------------------------------------------
def generate_fact_sales(
    dim_date: pd.DataFrame,
    dim_area: pd.DataFrame,
    dim_customer: pd.DataFrame,
    dim_industry: pd.DataFrame,
    dim_salesperson: pd.DataFrame,
    n_rows: int = NUM_SALES_ROWS,
) -> pd.DataFrame:
    date_keys = dim_date["DateKey"].tolist()
    customer_keys = dim_customer["CustomerKey"].tolist()
    industry_keys = dim_industry["IndustryKey"].tolist()
    salesperson_keys = dim_salesperson["SalespersonKey"].tolist()
    customer_area_map = build_customer_area_map(dim_customer, dim_area)

    rows = []
    for i in range(n_rows):
        customer_key = random.choice(customer_keys)
        area_key = customer_area_map[customer_key]
        sales_amount = round(random.uniform(500, 80000), 2)
        profit_pct = random.uniform(0.05, 0.35)
        adjusted_profit = round(sales_amount * profit_pct, 2)
        rows.append({
            "SalesId": f"S-{i + 1:06d}",
            "DateKey": random.choice(date_keys),
            "AreaKey": area_key,
            "CustomerKey": customer_key,
            "IndustryKey": random.choice(industry_keys),
            "SalespersonKey": random.choice(salesperson_keys),
            "SalesAmountLC": sales_amount,
            "AdjustedProfitLC": adjusted_profit,
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Fact_Budget  (grain: fiscal month x area x industry)
# ---------------------------------------------------------------------------
def generate_fact_budget(
    dim_date: pd.DataFrame,
    dim_area: pd.DataFrame,
    dim_industry: pd.DataFrame,
) -> pd.DataFrame:
    # One budget row per fiscal-month x area x industry
    # Use 1st day of each calendar month as DateKey representative
    month_first_days = dim_date.drop_duplicates(subset=["CalendarYear", "CalendarMonth"])
    month_date_keys = month_first_days["DateKey"].tolist()

    area_keys = dim_area["AreaKey"].tolist()
    industry_keys = dim_industry["IndustryKey"].tolist()

    rows = []
    for dk in month_date_keys:
        for ak in area_keys:
            for ik in industry_keys:
                budget = round(random.uniform(20000, 200000), 2)
                rows.append({
                    "DateKey": dk,
                    "AreaKey": ak,
                    "IndustryKey": ik,
                    "BudgetAmountLC": budget,
                })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("Generating mock data for SalesOverview...")

    # Dimensions
    dim_date = generate_dim_date(DATE_START, DATE_END, FISCAL_YEAR_START_MONTH)
    dim_area = generate_dim_area()
    dim_customer = generate_dim_customer(dim_area)
    dim_industry = generate_dim_industry()
    dim_salesperson = generate_dim_salesperson()

    # Facts
    fact_sales = generate_fact_sales(
        dim_date, dim_area, dim_customer, dim_industry, dim_salesperson
    )
    fact_budget = generate_fact_budget(dim_date, dim_area, dim_industry)

    # Write CSVs
    datasets = {
        "dim_date": dim_date,
        "dim_area": dim_area,
        "dim_customer": dim_customer,
        "dim_industry": dim_industry,
        "dim_salesperson": dim_salesperson,
        "fact_sales": fact_sales,
        "fact_budget": fact_budget,
    }

    for name, df in datasets.items():
        path = os.path.join(DATA_DIR, f"{name}.csv")
        df.to_csv(path, index=False, encoding="utf-8")
        print(f"  {name}.csv  -> {len(df):>6} rows")

    print(f"\nAll CSV files saved to: {DATA_DIR}")
    print("Done.")


if __name__ == "__main__":
    main()
