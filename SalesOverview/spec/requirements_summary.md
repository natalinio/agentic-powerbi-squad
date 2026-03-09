# Requirements Summary – Sales Overview (FYTD)

**Source**: `SalesOverview/spec/spec_sales_overview_fytd.md`
**Generated at**: 2026-03-09

---

## KPIs Identified

| # | KPI Name | Aggregation | Formula | Format | Time Intelligence |
|---|----------|-------------|---------|--------|-------------------|
| 1 | Sales (LC) FYTD | SUM (additive) | TOTALYTD( SUM( FactSales[SalesAmountLC] ), DimDate[Date], "6/30" ) | Currency | FYTD |
| 2 | Budget (LC) FYTD | SUM (additive) | TOTALYTD( SUM( FactBudget[BudgetAmountLC] ), DimDate[Date], "6/30" ) | Currency | FYTD |
| 3 | Sales vs Budget Variance | Derived (non-additive) | DIVIDE( [Sales (LC) FYTD] - [Budget (LC) FYTD], [Budget (LC) FYTD] ) | Percentage | FYTD |
| 4 | Adjusted Profit (LC) FYTD | SUM (additive) | TOTALYTD( SUM( FactSales[AdjustedProfitLC] ), DimDate[Date], "6/30" ) | Currency | FYTD |
| 5 | Average Monthly Sales (LC) | AVERAGE (semi-additive) | AVERAGEX( VALUES( DimDate[FiscalYearMonth] ), [Sales (LC)] ) over FYTD months | Currency | FYTD context |
| 6 | Adjusted Profit % | Derived (non-additive) | DIVIDE( [Adjusted Profit (LC) FYTD], [Sales (LC) FYTD] ) | Percentage | FYTD |
| 7 | Sales (LC) | SUM (additive) | SUM( FactSales[SalesAmountLC] ) | Currency | None (base) |
| 8 | Budget (LC) | SUM (additive) | SUM( FactBudget[BudgetAmountLC] ) | Currency | None (base) |
| 9 | Adjusted Profit (LC) | SUM (additive) | SUM( FactSales[AdjustedProfitLC] ) | Currency | None (base) |
| 10 | Sales Budget Status | Calculated (non-additive) | Categorical: Above / Close to / Below target (based on variance % thresholds) | Text | FYTD |

---

## Dimensions Identified

| # | Dimension | Key Attributes | Hierarchy | Shared across Facts? |
|---|-----------|---------------|-----------|----------------------|
| 1 | DimDate | DateKey (int64 surrogate), Date, FiscalYear, FiscalMonth, FiscalMonthNumber, FiscalYearMonth, CalendarYear, CalendarMonth, MonthName | FiscalYear → FiscalMonth | Yes (FactSales, FactBudget) |
| 2 | DimArea | AreaKey (int64 surrogate), AreaName | Flat | Yes (FactSales, FactBudget) |
| 3 | DimCustomer | CustomerKey (int64 surrogate), CustomerName, Country | Area → Country → Customer | FactSales only |
| 4 | DimIndustry | IndustryKey (int64 surrogate), IndustryName | Flat | Yes (FactSales, FactBudget) |
| 5 | DimSalesperson | SalespersonKey (int64 surrogate), SalespersonName | Flat | FactSales only |

---

## Fact Tables

| # | Fact Table | Grain | Columns | Related Dimensions |
|---|-----------|-------|---------|--------------------|
| 1 | FactSales | One row per sales transaction (identified by SalesId) | SalesId, DateKey (FK), AreaKey (FK), CustomerKey (FK), IndustryKey (FK), SalespersonKey (FK), SalesAmountLC, AdjustedProfitLC | DimDate, DimArea, DimCustomer, DimIndustry, DimSalesperson |
| 2 | FactBudget | One row per fiscal month × area × industry | DateKey (FK), AreaKey (FK), IndustryKey (FK), BudgetAmountLC | DimDate, DimArea, DimIndustry |

---

## Relationships (Star Schema)

| From (Dim) → To (Fact) | Key | Cardinality | Direction |
|------------------------|-----|-------------|-----------|
| DimDate → FactSales | DateKey | 1:M | Single |
| DimArea → FactSales | AreaKey | 1:M | Single |
| DimCustomer → FactSales | CustomerKey | 1:M | Single |
| DimIndustry → FactSales | IndustryKey | 1:M | Single |
| DimSalesperson → FactSales | SalespersonKey | 1:M | Single |
| DimDate → FactBudget | DateKey | 1:M | Single |
| DimArea → FactBudget | AreaKey | 1:M | Single |
| DimIndustry → FactBudget | IndustryKey | 1:M | Single |

---

## RLS Rules

Nessun requisito RLS rilevato nella specifica.

---

## Drill-Down Paths

La specifica richiede drill-down: **Area → Country → Customer → Salesperson**.
- Country è un attributo di DimCustomer; la gerarchia sarà gestita come: DimArea.AreaName → DimCustomer.Country → DimCustomer.CustomerName.
- Il drill su Salesperson è contestuale (filtro aggiuntivo parallelo, non gerarchico rispetto a Customer).

---

## Design Decisions

1. **Schema Stellare**: Sales Fact e Budget Fact come tabelle dei fatti separate, collegate tramite dimensioni condivise conformate (DimDate, DimArea, DimIndustry). Nessun collegamento diretto tra le due fact table.
2. **Adjusted Profit %**: calcolato come misura DAX (non colonna su FactSales), così da essere correttamente aggregabile a qualsiasi livello dimensionale.
3. **Budget Amount**: rimosso da FactSales; mantenuto unicamente su FactBudget con granularità mese × area × industry.
4. **DimDate**: tabella calendario dedicata, marcata come Date Table, con attributi fiscali.
5. **Chiavi surrogate int64**: tutte le dimensioni useranno surrogate key per performance ottimali.

---

## ⚠️ Ambiguità e Domande Aperte

| # | Ambiguità | Default Assunto | Azione Richiesta |
|---|-----------|----------------|------------------|
| 1 | **Mese di inizio dell'anno fiscale** non specificato. Necessario per calcoli FYTD e generazione DimDate. | Default: Luglio (FY inizia il 1° luglio). FY2025 = Jul 2024 – Jun 2025. | Confermare o correggere. |
| 2 | **Soglia "Close to target"**: quale percentuale di scostamento dal budget definisce "Close"? | Default: tra -5% e 0% = Close to target; > 0% = Above; < -5% = Below. | Confermare o correggere. |
| 3 | **Adjusted Profit %** presente come colonna nella Sales Fact nella specifica, ma è una ratio non additiva. | Decisione: calcolata SOLO come misura DAX, non come colonna. | Confermare. |
| 4 | **Budget Amount (LC)** presente sia su Sales Fact che su Budget. | Decisione: mantenuto SOLO su FactBudget (evitare duplicazione). | Confermare. |
| 5 | **Granularità budget**: la specifica indica FiscalYear × FiscalMonth × Area × Industry. Manca la dimensione Salesperson e Customer nel budget. | Decisione: budget rimane a granularità mese × area × industry (non a livello salesperson/customer). | Confermare. |
| 6 | **Valuta locale (LC)**: si assume un'unica valuta (nessuna conversione richiesta). | Default: tutte le cifre in valuta locale unica. | Confermare. |
