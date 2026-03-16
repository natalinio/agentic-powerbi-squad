# Sales Performance Analytics report

## 1. Report Objective & Target Audience

**Report Objective:**
Fornire una soluzione di analisi centralizzata per monitorare le performance di vendita, la redditività e il raggiungimento dei target (Budget) per Contoso LDT. Il report permette di analizzare i trend temporali e di confrontare le performance attuali con il budget e l'anno precedente (PY).

**Target Audience:**
- Executive Management
- Sales Managers
- Financial Analysts

**Key Business Questions:**
- Qual è l'andamento delle vendite (Sales LC) rispetto al budget stabilito?
- Qual è la marginalità percentuale (Adjusted Profit %) per area e industria?
- Come si confrontano le performance attuali rispetto allo stesso periodo dell'anno precedente (YOY)?

---

## 2. Key Performance Indicators (KPIs)

### KPI 1: Sales (LC)
- **Description:** Valore totale delle vendite in valuta locale.
- **Business Logic:** Sum of transaction amounts in local currency.
- **Format:** Currency
- **Time Intelligence:** Current Period, YTD, Prior Year (PY), YOY Growth %.

### KPI 2: Budget Variance (LC & %)
- **Description:** Differenza tra vendite effettive e budget.
- **Business Logic:** `[Sales (LC)] - [Budget (LC)]` e `[Budget Variance (LC)] / [Budget (LC)]`.
- **Format:** Currency / Percentage
- **Time Intelligence:** Current Period, YTD.

### KPI 3: Adjusted Profit %
- **Description:** Percentuale di profitto rettificato sulle vendite.
- **Business Logic:** `[Adjusted Profit (LC)] / [Sales (LC)]`.
- **Format:** Percentage
- **Time Intelligence:** Current Period.

---

## 3. Data Groupings & Segmentations

**Primary Groupings:**
- **Area:** Segmentazione geografica (es. NT, SA, NSW, etc.).
- **Industry:** Settore industriale del cliente.
- **Salesperson:** Persona responsabile della vendita.
- **Time:** Gerarchia basata sull'anno fiscale (Fiscal Year → Month).

**Expected Granularity:**
Livello transazionale (Transaction/Invoice level) per supportare aggregazioni dinamiche.

---

## 4. Filter Dimensions

**Global Filters:**
- Fiscal Year
- Month
- Area
- Industry
- Salesperson
- Sales Budget Status

**Report-Specific Filters:**
- **Dimension Switcher:** Slicer basato su Field Parameters per cambiare dinamicamente l'asse delle righe nella "Sales Table" tra Area, Industry e Salesperson.

---

## 5. Visualization Structure

### Chart 1: Sales vs. Budget (LC) over Time (Page 1)
- **Type:** Clustered Column Chart with Target Markers.
- **Purpose:** Monitoraggio mensile dei ricavi rispetto al budget.
- **Dimensions:** Fiscal Month.
- **Measures:** Sales (LC), Budget (LC).

### Chart 2: Sales (LC) vs. Profit % by Area (Page 1)
- **Type:** Bubble Chart (Scatter Plot).
- **Purpose:** Analisi della profittabilità in relazione ai volumi di vendita per area.
- **Dimensions:** Area.
- **Measures:** Sales (LC), Adjusted Profit %.

### Chart 3: Sales Performance Ranking (Page 1)
- **Type:** Bar Charts.
- **Purpose:** Top 10 per Clienti, Paesi, Venditori e Industrie.
- **Dimensions:** Customer, Country, Salesperson, Industry.
- **Measures:** Sales (LC).

### Chart 4: Analytical Sales Matrix (Page 2)
- **Type:** Matrix with Sparklines and Icons.
- **Purpose:** Analisi tabellare comparativa con KPI di stato.
- **Dimensions:** Dynamic Dimension (Area, Industry, or Salesperson).
- **Measures:** Sales (LC), Sales Sparkline, Budget Variance, Adjusted Profit %, Sales YOY %.
- **Conditional Formatting:** Semafori (Verde, Giallo, Rosso) per Budget Variance e Profit %.

---

## 6. Data Schema & Sample Values

### Table 1: Fact_Sales

| Column Name | Data Type | Description | Sample Values |
|-------------|-----------|-------------|---------------|
| OrderID | String | Transaction ID | "SO-12345" |
| DateKey | Date | Reference to Date Table | 2024-07-01 |
| AreaID | String | Link to Geography | "NSW", "VIC" |
| SalespersonID | String | Link to Salesperson | "S_001" |
| Sales_LC | Decimal | Gross Sales Amount | 4340325.14 |
| Budget_LC | Decimal | Targeted Budget | 3306204.67 |
| Profit_LC | Decimal | Adjusted Profit | 1126358.72 |

### Table 2: Dim_Date

| Column Name | Data Type | Description | Sample Values |
|-------------|-----------|-------------|---------------|
| Date | Date | Full Date | 2024-07-01 |
| FiscalYear | String | Fiscal Year Label | "FY2024" |
| FiscalMonth | Integer | Month of Fiscal Year | 1, 2, 3 |

---

## 7. Logical Relationships Between Data

**Relationship 1:**
- **From:** `Fact_Sales[DateKey]`
- **To:** `Dim_Date[Date]`
- **Cardinality:** Many-to-One (N:1)

**Relationship 2:**
- **From:** `Fact_Sales[AreaID]`
- **To:** `Dim_Area[AreaID]`
- **Cardinality:** Many-to-One (N:1)

---

## 8. Row-Level Security (RLS) Requirements

**No RLS Required:**
- [x] Tutti gli utenti vedono tutti i dati.

---

## 9. Functional Requirements

### 9.1 Data Refresh Strategy

**Refresh Frequency:**
- [x] Daily (Scheduled at 08:00 AM)

**Storage Mode Preference:**
- [x] **Import Mode**

**Expected Data Volumes:**
- **Fact Table:** ~5,000,000 rows.
- **Dimension Tables:** ~50,000 rows.

**Incremental Refresh Requirements:**
- [x] **Not needed** (Current volume is manageable with full refresh).

### 9.2 Technical Implementation Rules

**Field Parameters (Dynamic Dimension):**
Implementare un parametro di campo denominato `Dynamic Dimension Selector` che includa:
- `Dim_Area[AreaName]`
- `Dim_Industry[IndustryName]`
- `Dim_Salesperson[SalespersonName]`

**DAX Language:**
Tutte le misure e i commenti nel codice DAX devono essere in **Inglese**.

---

## 10. Additional Notes

**Business Rules:**
- I colori dei semafori (Above, Close, Below Target) sono definiti come:
  - Green (Above): Variance > 5%
  - Yellow (Close): Variance between -5% and 5%
  - Red (Below): Variance < -5%
- L'anno fiscale inizia il 1° Luglio.