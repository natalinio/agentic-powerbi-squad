"""
Mock Data Generator for Sales Overview FYTD Semantic Model
Generates realistic CSV files for all dimension and fact tables.

Requirements:
- pandas
- faker

Usage:
    python scripts/generate_mock_data.py
"""

import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta
import os

# Initialize Faker
fake = Faker()
random.seed(42)
Faker.seed(42)

# Output directory
OUTPUT_DIR = "SalesOverviewFYTD/data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 60)
print("MOCK DATA GENERATION - Sales Overview FYTD")
print("=" * 60)


# =============================================================================
# 1. DIMENSION: Dim_Date
# =============================================================================
def generate_dim_date(start_date='2020-01-01', end_date='2027-12-31', fiscal_year_start_month=1):
    """
    Generate date dimension with fiscal calendar support.
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        fiscal_year_start_month: Fiscal year start month (1=January, 7=July)
    """
    print("\n[1/10] Generating Dim_Date...")
    
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    df = pd.DataFrame({'Date': dates})
    
    # DateKey in YYYYMMDD format
    df['DateKey'] = df['Date'].dt.strftime('%Y%m%d').astype(int)
    
    # Calendar columns
    df['CalendarYear'] = df['Date'].dt.year
    df['CalendarMonth'] = df['Date'].dt.month
    df['CalendarMonthName'] = df['Date'].dt.strftime('%B')
    df['CalendarQuarter'] = df['Date'].dt.quarter
    
    # Fiscal year logic
    def get_fiscal_year(date, fy_start_month):
        if date.month >= fy_start_month:
            return date.year + 1
        else:
            return date.year
    
    def get_fiscal_month(date, fy_start_month):
        return ((date.month - fy_start_month) % 12) + 1
    
    df['FiscalYear'] = df['Date'].apply(lambda d: get_fiscal_year(d, fiscal_year_start_month))
    df['FiscalMonth'] = df['Date'].apply(lambda d: get_fiscal_month(d, fiscal_year_start_month))
    
    # Fiscal month name (same as calendar month name for simplicity)
    df['FiscalMonthName'] = df['CalendarMonthName']
    
    # Fiscal quarter
    df['FiscalQuarter'] = ((df['FiscalMonth'] - 1) // 3) + 1
    
    # Current fiscal year flag (based on today's date)
    today = datetime.now()
    current_fy = get_fiscal_year(today, fiscal_year_start_month)
    df['IsCurrentFY'] = df['FiscalYear'] == current_fy
    
    # Weekend flag
    df['DayOfWeek'] = df['Date'].dt.dayofweek + 1  # 1=Monday, 7=Sunday
    df['DayName'] = df['Date'].dt.strftime('%A')
    df['IsWeekend'] = df['DayOfWeek'].isin([6, 7])
    
    # Reorder columns to match TMDL
    df = df[['DateKey', 'Date', 'CalendarYear', 'CalendarMonth', 'CalendarMonthName', 
             'CalendarQuarter', 'FiscalYear', 'FiscalMonth', 'FiscalMonthName', 
             'FiscalQuarter', 'IsCurrentFY', 'IsWeekend', 'DayOfWeek', 'DayName']]
    
    df.to_csv(f"{OUTPUT_DIR}/dim_date.csv", index=False, encoding='utf-8')
    print(f"   ✓ Generated {len(df)} rows")
    return df


# =============================================================================
# 2. DIMENSION: Dim_Area
# =============================================================================
def generate_dim_area():
    """Generate geographic areas."""
    print("\n[2/10] Generating Dim_Area...")
    
    areas = [
        {'AreaKey': 1, 'AreaName': 'Europe'},
        {'AreaKey': 2, 'AreaName': 'North America'},
        {'AreaKey': 3, 'AreaName': 'Asia Pacific'},
        {'AreaKey': 4, 'AreaName': 'Latin America'},
        {'AreaKey': 5, 'AreaName': 'Middle East & Africa'},
    ]
    
    df = pd.DataFrame(areas)
    df.to_csv(f"{OUTPUT_DIR}/dim_area.csv", index=False, encoding='utf-8')
    print(f"   ✓ Generated {len(df)} rows")
    return df


# =============================================================================
# 3. DIMENSION: Dim_Country
# =============================================================================
def generate_dim_country(dim_area):
    """Generate countries with area relationships."""
    print("\n[3/10] Generating Dim_Country...")
    
    countries = [
        # Europe
        {'CountryKey': 1, 'CountryName': 'Germany', 'AreaKey': 1},
        {'CountryKey': 2, 'CountryName': 'France', 'AreaKey': 1},
        {'CountryKey': 3, 'CountryName': 'Italy', 'AreaKey': 1},
        {'CountryKey': 4, 'CountryName': 'United Kingdom', 'AreaKey': 1},
        {'CountryKey': 5, 'CountryName': 'Spain', 'AreaKey': 1},
        # North America
        {'CountryKey': 6, 'CountryName': 'United States', 'AreaKey': 2},
        {'CountryKey': 7, 'CountryName': 'Canada', 'AreaKey': 2},
        {'CountryKey': 8, 'CountryName': 'Mexico', 'AreaKey': 2},
        # Asia Pacific
        {'CountryKey': 9, 'CountryName': 'China', 'AreaKey': 3},
        {'CountryKey': 10, 'CountryName': 'Japan', 'AreaKey': 3},
        {'CountryKey': 11, 'CountryName': 'Australia', 'AreaKey': 3},
        {'CountryKey': 12, 'CountryName': 'India', 'AreaKey': 3},
        # Latin America
        {'CountryKey': 13, 'CountryName': 'Brazil', 'AreaKey': 4},
        {'CountryKey': 14, 'CountryName': 'Argentina', 'AreaKey': 4},
        # Middle East & Africa
        {'CountryKey': 15, 'CountryName': 'South Africa', 'AreaKey': 5},
        {'CountryKey': 16, 'CountryName': 'United Arab Emirates', 'AreaKey': 5},
    ]
    
    df = pd.DataFrame(countries)
    df.to_csv(f"{OUTPUT_DIR}/dim_country.csv", index=False, encoding='utf-8')
    print(f"   ✓ Generated {len(df)} rows")
    return df


# =============================================================================
# 4. DIMENSION: Dim_Industry
# =============================================================================
def generate_dim_industry():
    """Generate industry sectors."""
    print("\n[4/10] Generating Dim_Industry...")
    
    industries = [
        {'IndustryKey': 1, 'IndustryName': 'Manufacturing'},
        {'IndustryKey': 2, 'IndustryName': 'Retail'},
        {'IndustryKey': 3, 'IndustryName': 'Financial Services'},
        {'IndustryKey': 4, 'IndustryName': 'Healthcare'},
        {'IndustryKey': 5, 'IndustryName': 'Technology'},
        {'IndustryKey': 6, 'IndustryName': 'Energy'},
        {'IndustryKey': 7, 'IndustryName': 'Telecommunications'},
        {'IndustryKey': 8, 'IndustryName': 'Transportation'},
        {'IndustryKey': 9, 'IndustryName': 'Hospitality'},
        {'IndustryKey': 10, 'IndustryName': 'Professional Services'},
    ]
    
    df = pd.DataFrame(industries)
    df.to_csv(f"{OUTPUT_DIR}/dim_industry.csv", index=False, encoding='utf-8')
    print(f"   ✓ Generated {len(df)} rows")
    return df


# =============================================================================
# 5. DIMENSION: Dim_Customer
# =============================================================================
def generate_dim_customer(dim_country, dim_industry, n_customers=100):
    """Generate customer dimension with referential integrity."""
    print("\n[5/10] Generating Dim_Customer...")
    
    customers = []
    for i in range(1, n_customers + 1):
        customers.append({
            'CustomerKey': i,
            'CustomerName': fake.company(),
            'CountryKey': random.choice(dim_country['CountryKey'].tolist()),
            'IndustryKey': random.choice(dim_industry['IndustryKey'].tolist()),
        })
    
    df = pd.DataFrame(customers)
    df.to_csv(f"{OUTPUT_DIR}/dim_customer.csv", index=False, encoding='utf-8')
    print(f"   ✓ Generated {len(df)} rows")
    return df


# =============================================================================
# 6. DIMENSION: Dim_Salesperson
# =============================================================================
def generate_dim_salesperson(n_salespeople=20):
    """Generate salesperson dimension."""
    print("\n[6/10] Generating Dim_Salesperson...")
    
    salespeople = []
    for i in range(1, n_salespeople + 1):
        salespeople.append({
            'SalespersonKey': i,
            'SalespersonName': fake.name(),
        })
    
    df = pd.DataFrame(salespeople)
    df.to_csv(f"{OUTPUT_DIR}/dim_salesperson.csv", index=False, encoding='utf-8')
    print(f"   ✓ Generated {len(df)} rows")
    return df


# =============================================================================
# 7. FACT TABLE: Fact_Sales
# =============================================================================
def generate_fact_sales(dim_date, dim_customer, dim_country, dim_area, dim_industry, 
                        dim_salesperson, n_transactions=2000):
    """Generate sales fact table with realistic distributions."""
    print("\n[7/10] Generating Fact_Sales...")
    
    # Get lookups for denormalized columns
    customer_lookups = dim_customer.merge(
        dim_country[['CountryKey', 'AreaKey']], on='CountryKey'
    )
    
    # Filter date range for sales (last 2 years)
    recent_dates = dim_date[dim_date['Date'] >= '2024-01-01']['DateKey'].tolist()
    
    transactions = []
    for i in range(1, n_transactions + 1):
        # Select customer (this gives us Customer, Country, Area, Industry)
        customer = customer_lookups.sample(1).iloc[0]
        
        sales_amount = round(random.uniform(500, 100000), 2)
        profit_margin = random.uniform(0.15, 0.45)
        adjusted_profit = round(sales_amount * profit_margin, 2)
        
        # Item and Resource profit (sum should be close to adjusted profit)
        item_profit_pct = random.uniform(0.6, 0.8)
        item_profit = round(adjusted_profit * item_profit_pct, 2)
        resource_profit = round(adjusted_profit - item_profit, 2)
        
        # Discount (0-10% of sales)
        discount_pct = random.uniform(0, 0.1)
        discount = round(sales_amount * discount_pct, 2)
        
        # Delivery days
        expected_days = random.randint(3, 10)
        actual_days = expected_days + random.randint(-2, 5)
        
        transactions.append({
            'SalesKey': i,
            'SalesID': f'SO-{i:06d}',
            'DateKey': random.choice(recent_dates),
            'CustomerKey': int(customer['CustomerKey']),
            'CountryKey': int(customer['CountryKey']),
            'AreaKey': int(customer['AreaKey']),
            'IndustryKey': int(customer['IndustryKey']),
            'SalespersonKey': random.choice(dim_salesperson['SalespersonKey'].tolist()),
            'SalesAmountLC': sales_amount,
            'AdjustedProfitLC': adjusted_profit,
            'ItemProfitLC': item_profit,
            'ResourceProfitLC': resource_profit,
            'DiscountAmountLC': discount,
            'ActualDeliveryDays': actual_days,
            'ExpectedDeliveryDays': expected_days,
        })
    
    df = pd.DataFrame(transactions)
    df.to_csv(f"{OUTPUT_DIR}/fact_sales.csv", index=False, encoding='utf-8')
    print(f"   ✓ Generated {len(df)} rows")
    return df


# =============================================================================
# 8. FACT TABLE: Fact_Budget
# =============================================================================
def generate_fact_budget(dim_date, dim_area, dim_industry):
    """Generate budget fact table (monthly grain, first day of month)."""
    print("\n[8/10] Generating Fact_Budget...")
    
    # Get first day of each month in 2024-2026
    budget_dates = dim_date[
        (dim_date['Date'] >= '2024-01-01') & 
        (dim_date['Date'] <= '2026-12-31') &
        (dim_date['Date'].dt.day == 1)
    ]['DateKey'].tolist()
    
    budgets = []
    budget_key = 1
    
    for date_key in budget_dates:
        for area_key in dim_area['AreaKey']:
            for industry_key in dim_industry['IndustryKey']:
                # Budget amount varies by area and industry
                base_budget = random.uniform(50000, 500000)
                
                budgets.append({
                    'BudgetKey': budget_key,
                    'DateKey': date_key,
                    'AreaKey': area_key,
                    'IndustryKey': industry_key,
                    'BudgetAmountLC': round(base_budget, 2),
                })
                budget_key += 1
    
    df = pd.DataFrame(budgets)
    df.to_csv(f"{OUTPUT_DIR}/fact_budget.csv", index=False, encoding='utf-8')
    print(f"   ✓ Generated {len(df)} rows")
    return df


# =============================================================================
# 9. PARAMETER TABLE: MeasureInfo
# =============================================================================
def generate_measure_info():
    """Generate MeasureInfo parameter table with KPI thresholds."""
    print("\n[9/10] Generating MeasureInfo...")
    
    measure_info = [
        {'MeasureName': 'Adjusted Profit %', 'LowerBoundary': 25, 'UpperBoundary': 35, 
         'MeasureFormat': '%', 'HighIsGood': True, 
         'IconHigh': 'CircleHigh', 'IconMedium': 'CircleMedium', 'IconLow': 'CircleLow'},
        
        {'MeasureName': 'Item Profit %', 'LowerBoundary': 25, 'UpperBoundary': 35, 
         'MeasureFormat': '%', 'HighIsGood': True, 
         'IconHigh': 'CircleHigh', 'IconMedium': 'CircleMedium', 'IconLow': 'CircleLow'},
        
        {'MeasureName': 'Resource Profit %', 'LowerBoundary': 15, 'UpperBoundary': 20, 
         'MeasureFormat': '%', 'HighIsGood': True, 
         'IconHigh': 'CircleHigh', 'IconMedium': 'CircleMedium', 'IconLow': 'CircleLow'},
        
        {'MeasureName': 'Sales YOY %', 'LowerBoundary': -10, 'UpperBoundary': 0, 
         'MeasureFormat': '%', 'HighIsGood': True, 
         'IconHigh': 'TriangleHigh', 'IconMedium': 'TriangleMedium', 'IconLow': 'TriangleLow'},
        
        {'MeasureName': 'Item Discount %', 'LowerBoundary': 3, 'UpperBoundary': 5, 
         'MeasureFormat': '%', 'HighIsGood': False, 
         'IconHigh': 'CircleHigh', 'IconMedium': 'CircleMedium', 'IconLow': 'CircleLow'},
        
        {'MeasureName': 'Period over Comparison %', 'LowerBoundary': -1, 'UpperBoundary': 1, 
         'MeasureFormat': '%', 'HighIsGood': True, 
         'IconHigh': 'TriangleHigh', 'IconMedium': 'TriangleMedium', 'IconLow': 'TriangleLow'},
        
        {'MeasureName': 'Budget Variance %', 'LowerBoundary': -10, 'UpperBoundary': 0, 
         'MeasureFormat': '%', 'HighIsGood': True, 
         'IconHigh': 'FlagHigh', 'IconMedium': 'FlagMedium', 'IconLow': 'FlagLow'},
        
        {'MeasureName': 'Item Budget Variance %', 'LowerBoundary': -10, 'UpperBoundary': 0, 
         'MeasureFormat': '%', 'HighIsGood': True, 
         'IconHigh': 'FlagHigh', 'IconMedium': 'FlagMedium', 'IconLow': 'FlagLow'},
        
        {'MeasureName': 'Delivery Days Variance', 'LowerBoundary': 0, 'UpperBoundary': 2, 
         'MeasureFormat': 'Days', 'HighIsGood': False, 
         'IconHigh': 'FlagHigh', 'IconMedium': 'FlagMedium', 'IconLow': 'FlagLow'},
        
        {'MeasureName': 'On Time Delivery %', 'LowerBoundary': 70, 'UpperBoundary': 80, 
         'MeasureFormat': '%', 'HighIsGood': True, 
         'IconHigh': 'CircleHigh', 'IconMedium': 'CircleMedium', 'IconLow': 'CircleLow'},
        
        {'MeasureName': 'Fill Rate %', 'LowerBoundary': 70, 'UpperBoundary': 80, 
         'MeasureFormat': '%', 'HighIsGood': True, 
         'IconHigh': 'CircleHigh', 'IconMedium': 'CircleMedium', 'IconLow': 'CircleLow'},
    ]
    
    df = pd.DataFrame(measure_info)
    df.to_csv(f"{OUTPUT_DIR}/measure_info.csv", index=False, encoding='utf-8')
    print(f"   ✓ Generated {len(df)} rows")
    return df


# =============================================================================
# 10. PARAMETER TABLE: Parameters
# =============================================================================
def generate_parameters():
    """Generate Parameters table for report configuration."""
    print("\n[10/10] Generating Parameters...")
    
    parameters = [
        {'ParameterName': 'FiscalYearStartMonth', 'ParameterValue': '1'},  # January (can be modified)
        {'ParameterName': 'DateRangeMode', 'ParameterValue': 'Auto'},
    ]
    
    df = pd.DataFrame(parameters)
    df.to_csv(f"{OUTPUT_DIR}/parameters.csv", index=False, encoding='utf-8')
    print(f"   ✓ Generated {len(df)} rows")
    return df


# =============================================================================
# MAIN EXECUTION
# =============================================================================
if __name__ == "__main__":
    print("\nStarting data generation...\n")
    
    # Generate dimensions (order matters for referential integrity)
    dim_date = generate_dim_date(fiscal_year_start_month=1)  # January start
    dim_area = generate_dim_area()
    dim_country = generate_dim_country(dim_area)
    dim_industry = generate_dim_industry()
    dim_customer = generate_dim_customer(dim_country, dim_industry, n_customers=100)
    dim_salesperson = generate_dim_salesperson(n_salespeople=20)
    
    # Generate fact tables
    fact_sales = generate_fact_sales(
        dim_date, dim_customer, dim_country, dim_area, dim_industry, dim_salesperson,
        n_transactions=2000
    )
    fact_budget = generate_fact_budget(dim_date, dim_area, dim_industry)
    
    # Generate parameter tables
    measure_info = generate_measure_info()
    parameters = generate_parameters()
    
    print("\n" + "=" * 60)
    print("DATA GENERATION COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print(f"\nOutput directory: {OUTPUT_DIR}/")
    print("\nGenerated files:")
    print("  ✓ dim_date.csv          (2,922 rows)")
    print("  ✓ dim_area.csv          (5 rows)")
    print("  ✓ dim_country.csv       (16 rows)")
    print("  ✓ dim_industry.csv      (10 rows)")
    print("  ✓ dim_customer.csv      (100 rows)")
    print("  ✓ dim_salesperson.csv   (20 rows)")
    print("  ✓ fact_sales.csv        (2,000 rows)")
    print(f"  ✓ fact_budget.csv       ({len(fact_budget)} rows)")
    print("  ✓ measure_info.csv      (11 rows)")
    print("  ✓ parameters.csv        (2 rows)")
    print("\nNext steps:")
    print("  1. Review generated CSV files in SalesOverviewFYTD/data/")
    print("  2. Open SalesOverviewFYTD/PBIP/SalesOverviewFYTD.pbip in Power BI Desktop")
    print("  3. Refresh all tables to load data")
    print("  4. Validate model and measures")
    print("\n" + "=" * 60)
