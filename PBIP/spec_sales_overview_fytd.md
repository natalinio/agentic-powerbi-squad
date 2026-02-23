# Specifiche Reportistica – Sales Overview (FYTD)

## 1. Obiettivo del Report

Fornire una vista integrata e navigabile delle performance di vendita nel periodo **Fiscal Year To Date (FYTD)**, consentendo il confronto tra **vendite**, **budget** e **marginalità**, con analisi per **tempo**, **area geografica**, **cliente**, **salesperson** e **industry**, a supporto del monitoraggio operativo e delle decisioni commerciali.

---

## 2. KPI Principali

I KPI sono visualizzati nella parte superiore della dashboard e rappresentano indicatori sintetici delle performance FYTD.

- **Sales vs Budget (FYTD)**: valore totale delle vendite FYTD confrontato con il budget assegnato, comprensivo di scostamento percentuale.
- **Sales (LC) FYTD**: valore delle vendite FYTD in valuta locale.
- **Adjusted Profit (LC) FYTD**: margine operativo aggiustato FYTD in valuta locale.
- **Average Monthly Sales (LC)**: media mensile delle vendite nel periodo considerato.
- **Adjusted Profit %**: percentuale di marginalità aggiustata sulle vendite.

### 2.1 Stato rispetto al Budget

Le performance sono classificate tramite indicatori visivi:

- **Above target**: vendite superiori al budget.
- **Close to target**: vendite in linea con il budget.
- **Below target**: vendite inferiori al budget.

---

## 3. Dimensioni per i Filtri

La dashboard consente il filtraggio dinamico dei dati tramite le seguenti dimensioni:

- **Fiscal Year** (es. *Current Fiscal Year*)
- **Month**: selezione singolo mese o cumulato FYTD (es. *A8*)
- **Area**: tutte o singola area geografica
- **Industry**: segmento industriale del cliente
- **Sales Budget**: stato rispetto al budget (*Above / Close / Below target*)

Questi filtri impattano tutti i KPI, grafici e tabelle presenti nella vista.

---

## 4. Struttura dei Grafici

### 4.1 Grafico Temporale – Sales vs Budget (LC) Over Time

- **Tipo**: grafico combinato (barre + linea)
- **Asse X**: mese fiscale
- **Asse Y**: valore vendite (LC)
- **Serie**:
  - Vendite effettive
  - Budget
- **Obiettivo**: analizzare l’andamento temporale delle vendite rispetto al budget.

### 4.2 Grafico per Area – Sales vs Budget (LC) by Area

- **Tipo**: barre verticali
- **Asse X**: area geografica
- **Asse Y**: valore vendite (LC)
- **Serie**:
  - Vendite
  - Budget
- **Obiettivo**: evidenziare le aree con performance sopra o sotto target.

### 4.3 Grafico a Bolle – Sales (LC) vs Profit % by Area

- **Tipo**: bubble chart
- **Asse X**: Adjusted Profit %
- **Asse Y**: Sales (LC)
- **Dimensione bolla**: volume vendite
- **Colore**: area geografica
- **Obiettivo**: confrontare volumi e marginalità tra le diverse aree.

---

## 5. Tabelle di Dettaglio

### 5.1 Sales (LC) by Customer Bill

- **Dimensione principale**: cliente
- **Misura**: Sales (LC)
- **Ordinamento**: decrescente per valore
- **Obiettivo**: identificare i clienti a maggior contributo.

### 5.2 Sales (LC) by Customer Bill Country

- **Dimensione**: paese del cliente
- **Misura**: Sales (LC)
- **Obiettivo**: analisi geografica a livello paese.

### 5.3 Sales (LC) by Salesperson

- **Dimensione**: salesperson
- **Misura**: Sales (LC)
- **Obiettivo**: monitorare le performance individuali della forza vendita.

### 5.4 Sales (LC) by Industry

- **Dimensione**: industry
- **Misura**: Sales (LC)
- **Obiettivo**: comprendere il contributo dei diversi settori industriali.

---

## 6. Schema Dati Necessario – Esempio di Modello Informativo

### Tabella: Sales Fact

| Campo | Tipo | Descrizione |
|---|---:|---|
| Sales ID | String | Identificativo univoco transazione |
| Fiscal Year | String | Anno fiscale |
| Fiscal Month | String | Mese fiscale |
| Data transazione | Date | Data vendita |
| Area | String | Area geografica |
| Country | String | Paese cliente |
| Cliente | String | Nome cliente |
| Industry | String | Settore industriale |
| Salesperson | String | Responsabile commerciale |
| Sales Amount (LC) | Decimal | Vendite in valuta locale |
| Adjusted Profit (LC) | Decimal | Margine aggiustato |
| Adjusted Profit % | Decimal | Percentuale di margine |
| Budget Amount (LC) | Decimal | Budget associato |

### Tabella: Budget

| Campo | Tipo | Descrizione |
|---|---:|---|
| Fiscal Year | String | Anno fiscale |
| Fiscal Month | String | Mese fiscale |
| Area | String | Area geografica |
| Industry | String | Settore |
| Budget Amount (LC) | Decimal | Valore budget |

### Relazioni

- **Sales Fact ↔ Budget**: collegamento tramite **Fiscal Year**, **Fiscal Month**, **Area**, **Industry**.
- **Dimensioni condivise** (a supporto di filtri e drill): **Cliente**, **Area**, **Industry**, **Salesperson**.

---

## 7. Requisiti Funzionali

- Filtri globali applicabili a tutte le visualizzazioni.
- Confronto immediato tra vendite, budget e marginalità.
- Evidenziazione visiva delle performance rispetto al target.
- Possibilità di drill-down: **area → paese → cliente → salesperson**.
- Aggiornamento periodico dei dati (es. giornaliero o mensile).

---

## 8. Note Finali

- Il modello dati deve essere a **schema stellare** per garantire performance e semplicità di manutenzione.
- La separazione tra **fatti di vendita** e **budget** consente analisi comparative flessibili.
- La struttura è estendibile con ulteriori dimensioni (es. **prodotto**, **canale**, **contratto**).
- I KPI sono progettati per supportare sia controllo direzionale sia analisi operative.
