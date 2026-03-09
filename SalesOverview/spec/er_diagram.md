# Logical Data Model — Sales Overview (FYTD)

**Methodology**: Kimball Star Schema
**Generated at**: 2026-03-09

---

## ER Diagram (Mermaid.js)

```mermaid
erDiagram
    Dim_Date {
        int DateKey PK
        date Date
        int CalendarYear
        int CalendarMonth
        string MonthName
        string CalendarQuarter
        string FiscalYear
        int FiscalMonthNumber
        string FiscalMonth
        string FiscalQuarter
        string FiscalYearMonth
        boolean IsWeekend
    }
    Dim_Area {
        int AreaKey PK
        string AreaName
    }
    Dim_Customer {
        int CustomerKey PK
        string CustomerName
        string Country
    }
    Dim_Industry {
        int IndustryKey PK
        string IndustryName
    }
    Dim_Salesperson {
        int SalespersonKey PK
        string SalespersonName
    }
    Fact_Sales {
        string SalesId DD
        int DateKey FK
        int AreaKey FK
        int CustomerKey FK
        int IndustryKey FK
        int SalespersonKey FK
        decimal SalesAmountLC
        decimal AdjustedProfitLC
    }
    Fact_Budget {
        int DateKey FK
        int AreaKey FK
        int IndustryKey FK
        decimal BudgetAmountLC
    }
    _Measures {
        string MeasurePlaceholder
    }

    Dim_Date ||--o{ Fact_Sales : "DateKey"
    Dim_Area ||--o{ Fact_Sales : "AreaKey"
    Dim_Customer ||--o{ Fact_Sales : "CustomerKey"
    Dim_Industry ||--o{ Fact_Sales : "IndustryKey"
    Dim_Salesperson ||--o{ Fact_Sales : "SalespersonKey"

    Dim_Date ||--o{ Fact_Budget : "DateKey"
    Dim_Area ||--o{ Fact_Budget : "AreaKey"
    Dim_Industry ||--o{ Fact_Budget : "IndustryKey"
```

---

## Grain Definitions

| Fact Table | Grain | Description |
|---|---|---|
| **Fact_Sales** | 1 riga per transazione di vendita | Identificata da SalesId (degenerate dimension). Ogni riga ha un importo vendita e un margine aggiustato. |
| **Fact_Budget** | 1 riga per mese fiscale × area × industry | Budget pianificato a granularità mensile per combinazione area/industry. |

---

## Conformed Dimensions

| Dimension | Used by Fact_Sales | Used by Fact_Budget |
|---|---|---|
| **Dim_Date** | ✅ | ✅ |
| **Dim_Area** | ✅ | ✅ |
| **Dim_Industry** | ✅ | ✅ |
| **Dim_Customer** | ✅ | ❌ |
| **Dim_Salesperson** | ✅ | ❌ |

---

## Ambiguous Path Analysis

**Rischio verificato**: nessun percorso ambiguo.

- **Dim_Customer** contiene solo `CustomerKey`, `CustomerName`, `Country` — nessun FK verso Dim_Area o Dim_Industry.
- Ogni percorso Fact → Dim è unico e diretto:
  - `Fact_Sales → Dim_Area` (unico, via AreaKey)
  - `Fact_Sales → Dim_Customer` (unico, via CustomerKey)
  - `Fact_Sales → Dim_Industry` (unico, via IndustryKey)
- Nessun snowflaking → nessun percorso indiretto.

**Drill-down Area → Country → Customer**:
1. Filtro su `Dim_Area.AreaName` → riduce le righe in `Fact_Sales` per area.
2. Breakdown per `Dim_Customer.Country` → mostra i paesi dei clienti nelle transazioni filtrate.
3. Drill a `Dim_Customer.CustomerName` → dettaglio cliente.

Funziona correttamente perché `Fact_Sales` porta sia `AreaKey` che `CustomerKey`, e la coerenza area–customer è garantita dai dati (referential integrity nei dati mock).

---

## Design Decisions

1. **Pure Star Schema**: nessun snowflaking. Tutte le dimensioni sono direttamente collegate alle fact table.
2. **Adjusted Profit %** non è una colonna: sarà calcolato come misura DAX `DIVIDE([Adjusted Profit (LC) FYTD], [Sales (LC) FYTD])`.
3. **Budget solo su Fact_Budget**: nessuna colonna budget in Fact_Sales.
4. **SalesId** come degenerate dimension: resta nella fact table, non diventa una dimensione separata.
5. **_Measures** come tabella disconnessa: conterrà tutte le misure DAX, nessuna relazione con altre tabelle.
6. **Dim_Date** marcata come Date Table con range continuo e attributi fiscali (FY inizia a luglio).
7. **Dim_Customer.Country** come attributo denormalizzato (non come dimensione separata) per semplicità e assenza di requisiti autonomi sulla dimensione Country.

---

## Fiscal Year Configuration

- **FY Start Month**: Luglio (mese 7)
- **FY End Month**: Giugno (mese 6)
- **Convention**: FY2025 = Jul 2024 – Jun 2025
- **FiscalYearMonth format**: `"FY2025-01"` (mese fiscale 1 = luglio)

---

## Checklist

- [x] Tutte le fact table hanno grain documentato
- [x] Tutte le dimensioni usano surrogate key int64
- [x] Dim_Date inclusa con colonne fiscal period
- [x] Tutte le relazioni sono 1:N (Dim → Fact)
- [x] Dimensioni conformate identificate (Date, Area, Industry)
- [x] Naming segue le convenzioni (`Fact_`, `Dim_`, `_Measures`)
- [x] **Nessun percorso ambiguo**: ogni coppia Fact–Dim ha un unico path attivo
- [x] RLS non richiesto (confermato nello Step 1)
