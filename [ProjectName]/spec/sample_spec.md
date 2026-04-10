# Semantic Model Specification: Sales Performance Analytics

## 1. Report Objective & Target Audience

**Report Objective:**
Fornire una soluzione di monitoraggio delle performance di vendita per **Yoda Networks LLC**, che permetta di analizzare i ricavi (Sales), il raggiungimento dei target (Budget) e la marginalita (Profit) attraverso una dashboard di sintesi e una tabella analitica granulare.

**Target Audience:**
- Executive Management (Monitoraggio KPI macro)
- Sales Managers (Performance dei venditori e delle aree)
- Financial Analysts (Analisi scostamenti e trend)

**Key Business Questions:**
- Stiamo raggiungendo i target di vendita stabiliti per l'anno fiscale?
- Qual e il trend mensile delle vendite rispetto al budget e all'anno precedente?
- Quali aree e industrie presentano i migliori margini di profitto?

---

## 2. Key Performance Indicators (KPIs)

### KPI 1: Sales (LC)
- **Description:** Totale dei ricavi in valuta locale.
- **Business Logic:** Somma delle vendite lorde effettive.
- **Format:** Currency (LC).
- **Time Intelligence:** Current Period, YTD, Prior Year (PY), YOY Growth %.

### KPI 2: Budget Variance (LC & %)
- **Description:** Differenza tra vendite effettive e budget pianificato.
- **Business Logic:** `Sales (LC) - Budget (LC)` e `(Sales / Budget) - 1`.
- **Format:** Currency / Percentage.
- **Visual Indicator:** Bandiere colorate (Verde/Giallo/Rosso) basate sulle soglie di scostamento.

### KPI 3: Adjusted Profit %
- **Description:** Percentuale di profitto rettificato calcolata sulle vendite.
- **Business Logic:** `Adjusted Profit (LC) / Sales (LC)`.
- **Format:** Percentage.
- **Visual Indicator:** Cerchi colorati (Stato del profitto).

- Da generare ogni altro kpi rilevante o che viene usato da quelli rilevanti.
---

## 3. Data Groupings & Segmentations

**Primary Groupings:**
- **Area:** Localizzazione geografica (es. NT, SA, NSW, VIC, QLD, WA, ACT).
- **Industry:** Settore industriale del cliente (es. Accommodations, TV-station, etc.).
- **Salesperson:** Nome del consulente/venditore.
- **Date:** Calendario Fiscale (Inizio Luglio) con gerarchia Anno -> Mese.

**Expected Granularity:**
Livello transazionale (singola riga di vendita).

---

## 4. Filter Dimensions

**Global Filters (Sidebar):**
- **Fiscal Year:** Selezione anno (Default: Current Fiscal Year).
- **Month:** Selezione singola o multipla.
- **Area:** Filtro geografico.
- **Industry:** Filtro per settore industriale.
- **Sales Budget:** Filtro per stato del budget.

**Dynamic Switcher (Page 2 Only):**
- **Field Parameter:** Uno slicer che permette all'utente di cambiare l'asse delle righe della "Sales Table" tra Area, Industry e Salesperson.

---

## 5. Visualization Structure

### Page 1: SALES OVERVIEW

#### 5.1 KPI Scorecards (Top)
- **Type:** KPI Cards (x5).
- **Measures:** Sales vs Budget FYTD, Sales FYOYTD, Adjusted Profit FYOYTD, Avg Monthly Sales, Adjusted Profit %.

#### 5.2 Sales vs. Budget (LC) over Time
- **Type:** Clustered Column Chart with Target Markers.
- **Logic:** Colonne per Sales (LC), marcatori orizzontali per Budget (LC). Colore dinamico delle barre basato sul raggiungimento del target (Verde/Giallo/Rosso).

#### 5.3 Sales vs. Budget (LC) by Area
- **Type:** Clustered Column Chart.
- **Dimensions:** Area. Measures: Sales (LC) e Budget (LC).

#### 5.4 Sales (LC) vs. Adjusted Profit % by Area
- **Type:** Scatter Plot (Bubble Chart).
- **X-Axis:** Adjusted Profit %. Y-Axis: Sales (LC). Bubble Size: Sales (LC).

#### 5.5 Rankings (Bottom)
- **Type:** Horizontal Bar Charts (x4).
- **Dimensions:** Customer Bill, Country, Salesperson, Industry.

---

### Page 2: SALES TABLE

#### 5.6 Analytical Matrix (Main Visual)
- **Type:** Matrix con formattazione condizionale e Sparklines.
- **Rows:** **Dynamic Dimension** (Switch via Slicer: Area, Industry, o Salesperson).
- **Columns & Metrics:**
    - **Sales (LC):** Valore + Barra Dati (Data Bar).
    - **Sales (LC) by Month Year:** Sparkline (Trend 12 mesi).
    - **Item Sales (LC):** Dettaglio vendite prodotto.
    - **Budget (LC):** Target monetario.
    - **Budget Variance (LC & %):** Valore + Icone Bandiera (Flag).
    - **Adjusted Profit (LC & %):** Valore + Icone Cerchio (Circle).
    - **Sales (LC) PY:** Vendite periodo precedente.
    - **Sales (LC) YOY %:** Variazione % con Icone Freccia (Up/Down).

---

## 6. Data Schema & Sample Values

### Table 1: Fact_Sales

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| TransactionID | String | ID Univoco transazione |
| DateKey | Date | Chiave data vendita |
| AreaID | String | FK per Dim_Area |
| Sales_LC | Decimal | Importo vendita |
| Budget_LC | Decimal | Valore budget |
| Profit_LC | Decimal | Profitto rettificato |

---

## 7. Logical Relationships

- **Fact_Sales[DateKey]** -> **Dim_Date[Date]** (Many-to-One).
- **Fact_Sales[AreaID]** -> **Dim_Geography[AreaID]** (Many-to-One).
- **Fact_Sales[SalespersonID]** -> **Dim_Staff[SalespersonID]** (Many-to-One).

---

## 8. Row-Level Security (RLS)

- **No RLS Required:** Tutti gli utenti hanno accesso alla totalita dei dati.

---

## 9. Functional Requirements

### 9.1 Data Refresh Strategy
- **Storage Mode:** **Import Mode**.
- **Refresh Frequency:** **Daily**.
- **Data Latency:** I dati devono essere pronti per l'inizio del business day.

### 9.2 Technical Implementation (DAX in English)
- Tutte le misure DAX e i commenti al codice devono essere scritti esclusivamente in **inglese**.
- **Field Parameter Script:**
  ```dax
  Dynamic Dimension = {
      ("Area", NAMEOF('Dim_Geography'[AreaName]), 0),
      ("Industry", NAMEOF('Dim_Customer'[IndustryName]), 1),
      ("Salesperson", NAMEOF('Dim_Staff'[SalespersonName]), 2)
  }
  ```
- Time Intelligence: Utilizzare un calendario fiscale con inizio Luglio per i calcoli YTD e PY.

## 10. Additional Notes
Conditional Formatting: Utilizzare icone SVG o set di icone native per Flags (Budget) e Circles (Profit).
Theme: Corporate orange/dark grey theme come da mockup.