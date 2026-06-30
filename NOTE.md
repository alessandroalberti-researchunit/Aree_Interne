# Note di progetto — Dashboard Aree Interne SNAI

Documento di tracciabilità per la dashboard interattiva sulla Strategia Nazionale Aree Interne (SNAI), cicli 2014-2020 e 2021-2027.

---

## Contesto e obiettivo

La **Strategia Nazionale Aree Interne** (SNAI) è una politica di sviluppo territoriale promossa dal Dipartimento per le Politiche di Coesione (DPCoe) che interviene sui comuni italiani classificati come "aree interne": territori distanti dai principali centri di erogazione di servizi (scuola, sanità, mobilità), spesso caratterizzati da spopolamento e declino economico.

La dashboard visualizza la distribuzione geografica delle 128 aree SNAI dei cicli 2014-2020 e 2021-2027, con dati statistici per area e comuni.

---

## Struttura del progetto

```
/
├── generate_snai_geojson.py       # Pipeline step 1: produce i GeoJSON
├── build_dashboard.py             # Pipeline step 2: genera l'HTML finale
├── dashboard-aree-interne.html    # Output (file singolo, self-contained)
├── aree-snai-perimetri.geojson    # GeoJSON dissolto per area (645 KB)
├── comuni-snai-perimetri.geojson  # GeoJSON per comune (1.932 KB)
├── DATA/                          # Dati sorgente (non modificare)
└── DOCS/                          # Documentazione ufficiale SNAI
```

---

## Dati sorgente

### `DATA/08_elenco-aree-comuni.xlsx` — fonte primaria

File ufficiale DPCoe. Fogli rilevanti:

| Foglio | Contenuto |
|--------|-----------|
| `Elenco Aree 21-27 TOTALE` | 1.727 comuni delle aree SI+CONF con codice ISTAT, popolazione 2020, classificazione SNAI |
| `Comuni 13 Aree 21-27 NO finanz.` | 153 comuni delle 13 aree non finanziate |
| `Sintesi Aree 21-27 finanziate` | Riepilogo per area: n. comuni, popolazione, distribuzione classificazioni |
| `Sintesi Aree 14-20 confermate` | Riepilogo aree confermate dal ciclo precedente |
| `Assegnazioni per Aree` | Investimento per area (€ 4.000.000 per ciascuna delle 43 aree finanziate) |
| `Assegnazioni per macroarea` | Totali per regione e macroarea |

Colonne chiave dei fogli comuni:
- `PRO_COM_T`: codice ISTAT a 6 cifre (3 provincia + 3 comune)
- `COMUNE`: nome comune
- `P_2020` / `pop_2020`: popolazione residente ISTAT 2020
- `SNAI_2020`: classificazione (es. `D - Intermedio`)
- `Aree SNAI 2021-2027`: nome dell'area di appartenenza
- `Macro_2020`: macroregione (`Centro-Nord` / `Mezzogiorno`)

### `DATA/mappa-ai-2020-elenco-classificazione-comuni.xlsx`

Fonte ISTAT/NUVAP, Mappa Aree Interne 2020. Contiene tutti i comuni italiani (non solo SNAI). Fogli rilevanti:

| Foglio | Contenuto |
|--------|-----------|
| `DATI` | 7.896 comuni con: `PROCOM_T` (codice ISTAT), superficie km², popolazione 2020, classificazione AI, tempi di percorrenza al polo, comune di destinazione prevalente |

Colonne estratte e usate nella dashboard:
- `Superficie territoriale (kmq) al 01/01/2019` → `km2` per comune
- `MEDIA tempi di percorrenza` → `min` (minuti al polo più vicino, arrotondati a 1 decimale)
- `DES_AI_2020`: classificazione estesa (A Polo, B Polo intercomunale, C Cintura, D Intermedio, E Periferico, F Ultraperiferico)

Le aree SNAI coprono solo i comuni D, E, F (mai A, B, C).

### `DATA/tabella-comuni-e-finanziamento.xlsx`

Tabella con 820 righe, una per comune delle aree 21-27. La colonna `Area ammessa al finanziamento nazionale` contiene SI/NO, ma solo a livello di area (43 SI, 13 NO), non per singolo comune. Non è stato integrato nella dashboard perché ridondante con lo status area.

### `DATA/elenco_aree_snai_14-20-e-21-27.xlsx`

Elenco completo con riperimetrazioni tra i due cicli. Fogli rilevanti:

| Foglio | Contenuto |
|--------|-----------|
| `Comuni 72 Aree SNAI 14-20` | Comuni del ciclo precedente |
| `Comuni 56 Aree SNAI 21-27` | Comuni del ciclo corrente |
| `Comuni 30 Aree Riperimetrate` | Aree che hanno cambiato perimetro tra i cicli |
| `Comuni 35 Isole Minori` | Isole aggregate fuori SNAI |

### `DATA/comuni_italia.geojson`

Cache locale dei confini comunali ISTAT scaricata da [openpolis/geojson-italy](https://github.com/openpolis/geojson-italy) (~37 MB). Usata da `generate_snai_geojson.py` per il join geografico. Cancellare per ri-scaricare.

### `DATA/openkit_metadati.xlsx`

Metadati OpenKit DPCoe. Non usato attivamente negli script.

### `DATA/mappa-ai-2020-tavole-sintesi-per-regione.xlsx`

Tavole di sintesi per regione (A/B/C/D/E/F). Non usato negli script (le stesse informazioni sono in `mappa-ai-2020-elenco-classificazione-comuni.xlsx`).

---

## Pipeline di build

### Step 1 — `generate_snai_geojson.py`

1. Carica i codici ISTAT comunali dai fogli Excel DPCoe (SI, CONF, NO)
2. Scarica i confini comunali da openpolis (cache in `DATA/comuni_italia.geojson`)
3. Fa il join tra codici ISTAT e geometrie
4. Dissolve i poligoni comunali per ottenere il perimetro di area con `geopandas`
5. Semplifica le geometrie: tolerance 0.002° per aree, 0.003° per comuni
6. Scrive `aree-snai-perimetri.geojson` (128 features) e `comuni-snai-perimetri.geojson` (1.967 features)

Properties nel GeoJSON comuni: `area`, `status`, `comune`, `procom` (codice ISTAT 6 cifre).

### Step 2 — `build_dashboard.py`

1. Carica i GeoJSON prodotti al passo 1
2. Carica `08_elenco-aree-comuni.xlsx` → calcola statistiche per area (n. comuni, popolazione, distribuzione classificazioni)
3. Carica `mappa-ai-2020-elenco-classificazione-comuni.xlsx` → estrae `km2` e `min` per comune (join su codice ISTAT)
4. Carica "Assegnazioni per Aree" → dizionario `{nome_area: importo_totale}`
5. Genera tre variabili JS embedded nell'HTML:
   - `AREE`: array di oggetti `{regione, area, n, pop, status, snai_dist}`
   - `COMUNI_BY_AREA`: dizionario `{area: [{n, p, pop, s, km2, min}]}`
   - `AREA_INV`: dizionario `{area: importo_in_euro}` (solo per le 43 aree SI)
6. Inietta i GeoJSON come variabili JS (`SNAI_GEO`, `COMUNI_GEO`)
7. Scrive `dashboard-aree-interne.html` (~2.768 KB, file singolo self-contained)

---

## Struttura dati JavaScript nella dashboard

### `AREE` (array)

```js
{
  regione: "Abruzzo",
  area:    "Piana del Cavaliere - Alto Liri",
  n:       10,          // numero comuni
  pop:     19490,       // popolazione 2020
  status:  "SI",        // SI | CONF | NO | 1420
  snai_dist: { "D":4, "E":6 }   // distribuzione classificazioni SNAI
}
```

### `COMUNI_BY_AREA` (dizionario)

```js
"Alpago Zoldo": [
  { n:"Chies d'Alpago", p:"Be", pop:1262, s:"D", km2:45.3, min:38.0 },
  ...
]
```

- `p`: sigla provincia (2 caratteri)
- `s`: lettera classificazione SNAI (D/E/F)
- `km2`: superficie in km², 1 decimale
- `min`: minuti al polo di destinazione prevalente, 1 decimale

### `AREA_INV` (dizionario)

```js
{ "Appennino Modenese": 4000000, ... }
```

Presente solo per le 43 aree finanziate 21-27. Importo uniforme: €4.000.000 per area (€104 M Centro-Nord + €68 M Mezzogiorno = €172 M totale). Quota FSC 58,1%, Fondo di Rotazione 41,9%.

### `SNAI_GEO` / `COMUNI_GEO`

GeoJSON FeatureCollection embedded come stringa JS.

---

## Numeri chiave

| Metrica | Valore |
|---------|--------|
| Aree totali | 128 |
| — di cui finanziate 21-27 (SI) | 43 |
| — di cui confermate 14-20, non rifinanziate (CONF) | 67 |
| — di cui non finanziate 21-27 (NO) | 13 |
| — di cui solo ciclo 14-20 (1420) | 5 |
| Comuni in aree SI+CONF+NO | ~1.880 noti su ~1.965 totali |
| Popolazione totale aree SI+CONF+NO | ~3,84 M ab. (dati ISTAT 2020) |
| Aree Centro-Nord (SI+CONF) | 61 |
| Aree Mezzogiorno (SI+CONF) | 49 |
| Investimento totale ciclo 21-27 | €172 M (€4 M per area SI) |
| Comuni italiani con classificazione AI 2020 | 7.896 |
| — di cui D Intermedio | 1.928 |
| — di cui E Periferico | 1.524 |
| — di cui F Ultraperiferico | 382 |

---

## Classificazione SNAI (Mappa AI 2020)

La classificazione si basa sul **tempo di percorrenza** (in minuti) al polo di offerta di servizi più vicino (scuole superiori, ospedali con DEA, stazioni ferroviarie con almeno 25 treni/giorno):

| Codice | Denominazione | Logica |
|--------|---------------|--------|
| A | Polo | Il comune è esso stesso polo di riferimento |
| B | Polo intercomunale | Insieme di comuni che costituiscono un polo |
| C | Cintura | Comune "vicino" al polo (tempi bassi) |
| D | Intermedio | Distanza moderata dal polo |
| E | Periferico | Distanza elevata dal polo |
| F | Ultraperiferico | Distanza molto elevata dal polo |

Le aree SNAI includono solo comuni D, E, F. Il campo `min` nel tooltip rappresenta il tempo di percorrenza al comune polo di destinazione prevalente per quel comune specifico.

---

## Status aree

| Status | Significato |
|--------|-------------|
| `SI` | Finanziate ciclo 2021-2027 (43 aree) — ricevono €4 M da FSC + Fondo di Rotazione |
| `CONF` | Confermate dal ciclo 2014-2020, non incluse nel nuovo finanziamento (67 aree) |
| `NO` | Candidate al ciclo 2021-2027 ma non selezionate (13 aree) |
| `1420` | Aree del solo ciclo 2014-2020 non più presenti nella mappa 21-27 (5 aree) |

---

## Documentazione ufficiale (DOCS/)

### Documenti nazionali

| File | Contenuto |
|------|-----------|
| `PSNAI_2021-2027.pdf` | Piano Strategico Nazionale Aree Interne, testo completo |
| `estratto-snai-accordo-partenariato-2021-2027.pdf` | Estratto SNAI dall'Accordo di Partenariato Italia-UE |
| `snai-criteri-selezione-aree-21-27.pdf` | Criteri ufficiali di selezione delle aree 21-27 |
| `elenco_aree_snai_14-20-e-21-27.pdf` | Elenco ufficiale aree e comuni per entrambi i cicli |
| `mappa-ai-2020-nota-tecnica-nuvap.pdf` | Nota tecnica NUVAP sulla Mappa Aree Interne 2020 (metodologia classificazione) |
| `openkit_guida-alla-lettura.pdf` | Guida alla lettura dell'OpenKit DPCoe |
| `11_relazione-annuale-2023.pdf` | Relazione annuale SNAI 2023 |

### Linee guida tematiche

| File | Contenuto |
|------|-----------|
| `04_linee-guida-requisito-associativo.pdf` | Requisiti di associazionismo intercomunale |
| `05_linee-guida-mobilita-MIT.pdf` | Linee guida MIT per la mobilità nelle aree interne |
| `06_linee-guida-scuola-MIM.pdf` | Linee guida MIM per la scuola nelle aree interne |
| `07_linee-guida-salute.pdf` | Linee guida per la salute nelle aree interne |

### Contributi e ricerche

| File | Contenuto |
|------|-----------|
| `01_contributo-cnel-demografia-aree-interne.pdf` | Analisi demografica CNEL sulle aree interne |
| `02_contributo-censis-gruppi-omogenei.pdf` | Analisi Censis — gruppi omogenei di aree |
| `03_report-consultazione-PSNAI.pdf` | Report della consultazione pubblica sul PSNAI |

### Strumenti operativi

| File | Contenuto |
|------|-----------|
| `09_indice-strategie-di-area.pdf` | Schema-indice per la redazione delle strategie d'area |
| `09a_format-2-allegato-indice.xlsx` | Format allegato alla strategia d'area |
| `09b_format-3-allegato-indice.xlsx` | Format allegato alla strategia d'area |
| `10_scheda-intervento.xlsx` | Scheda di intervento standard |
| `08_elenco-aree-comuni-con-riperimetrazioni.xlsx` | Elenco con traccia delle riperimetrazioni |

### Documentazione regionale

Per ciascuna delle 20 regioni/PA (escluse Molise e Basilicata da Centro) sono presenti:

- **Rapporto di istruttoria**: analisi delle proposte di area presentate dalle regioni (selezione, criteri, valutazioni)
- **Dossier SNAI**: scheda di presentazione delle aree selezionate

Regioni coperte: Abruzzo, Basilicata, Calabria, Campania, Emilia-Romagna, Friuli-Venezia Giulia, Lazio, Liguria, Lombardia, Marche, Molise, PA Bolzano, PA Trento, Piemonte, Puglia, Sardegna, Sicilia, Toscana, Umbria, Valle d'Aosta, Veneto.

### Accordi di Programma Quadro (APQ) — Emilia-Romagna

Presenti nella cartella `DOCS/Documentazione Regionale/Nord/Emilia-Romagna/`:
- APQ Alta Valmarecchia
- APQ Appennino Emiliano
- APQ Appennino Piacentino-Parmense
- APQ Basso Ferrarese

Gli APQ sono i contratti attuativi tra Stato, Regione e Comuni dell'area: definiscono gli interventi finanziati, i responsabili, le scadenze e i costi per settore (scuola, salute, mobilità, sviluppo locale).

---

## Tecnologie della dashboard

| Componente | Tecnologia | Versione |
|------------|-----------|---------|
| Mappa | Leaflet.js | 1.9.4 |
| Grafici | Chart.js | 4.4.0 |
| Griglia geografica | H3 | — (non usato, dato per futuro sviluppo) |
| Confini comunali | openpolis/geojson-italy | — |
| Processing dati | Python / pandas / geopandas | — |
| Build | `build_dashboard.py` | — |

L'output è un file HTML singolo self-contained: nessun server necessario, nessuna dipendenza esterna a runtime (Leaflet e Chart.js sono caricati da CDN nel tag `<script>`).

---

## Funzionalità implementate

### Navigazione geografica

- Vista Italia: mappa con tutti i poligoni delle 128 aree, colorati per status
- Filtri: per regione, status (SI/CONF/NO/1420), ricerca per nome area, ricerca per nome comune
- Click su regione (layer sfondo): zoom + filtro automatico per regione
- Click su area: entra nel dettaglio area con suddivisione per comuni
- Navigazione gerarchica con stack (pulsante ← per tornare al livello precedente)

### Dettaglio area

- Popup descrittivo (nome, regione, n. comuni, popolazione, status) posizionato al bordo nord dell'area per non sovrapporsi ai comuni
- Comuni evidenziati con bordi tratteggiati; il comune capofila in giallo
- Tooltip per ogni comune al passaggio del cursore: nome (bold), popolazione, superficie km², minuti al polo, investimento dell'area
- Hover con highlight del comune sotto il cursore

### Pannello laterale (right panel)

- Navigazione gerarchica: legenda globale → lista aree per regione/status → dettaglio area → lista comuni
- KPI per area: popolazione totale, n. comuni, distribuzione classificazioni SNAI (D/E/F)
- Ente capofila (dove presente) evidenziato in giallo
- Lista comuni con popolazione e classificazione

### Header e controlli

- Filtri: dropdown regione, dropdown status, ricerca testo area, ricerca testo comune
- Reset filtri
- Toggle tema chiaro/scuro
- Modal "?" con nota metodologica

### Tabella

- Pannello espandibile in fondo con tabella completa delle aree filtrate
- Colonne: area, regione, comuni, popolazione, status
- Click su riga per entrare nel dettaglio

---

## Dati non ancora integrati

| Dato | Fonte | Note |
|------|-------|-------|
| Enti capofila per area | APQ regionali, dossier istruttoria | Parzialmente popolato manualmente in `CAPOFILA` e `CAPOFILA_COMUNE` nel template JS; molte aree ancora vuote |
| Investimenti per settore (scuola/salute/mobilità) | APQ singoli | Non strutturati, dispersi nei PDF regionali |
| Indicatori BES provinciali | ISTAT BES | Disponibili via MCP `bes` |
| Dati PNRR per comuni SNAI | OpenCUP / MIT | Disponibili via MCP `pnrr-intelligence` |
| Proiezioni demografiche | ISTAT PREVCOM | Disponibili via MCP `istat` |
| Classificazione AI aggiornata post-2020 | NUVAP/DPCoe | Attesa revisione 2023 |

---

## Decisioni tecniche rilevanti

**Dissolve + simplify invece di merge**: i confini di area sono ottenuti dissolvendo i poligoni comunali ISTAT, non da un dataset separato. Questo garantisce coerenza geometrica con i confini comunali ma dipende dalla versione di `comuni_italia.geojson` in cache.

**Tolerance di semplificazione**: 0.002° per aree, 0.003° per comuni. Trovato per tentativi: tolerance più bassa aumenta il peso del file, più alta distorce i confini.

**Self-contained HTML**: i GeoJSON (~2.5 MB compressi) sono embedded come variabili JS invece di essere caricati via fetch, per evitare CORS e permettere l'uso offline. Il risultato è un file di ~2.7 MB.

**Popup area fuori perimetro**: il popup descrittivo dell'area si apre all'anchor `{lat: bounds.getNorth(), lng: bounds.getCenter().lng}` con `autoPan:false`, così appare sopra l'area senza sovrapporsi ai confini comunali.

**Tooltip comune come funzione lazy**: `bindTooltip(() => comuneTooltipHTML(c, areaName), ...)` — il contenuto viene calcolato al momento del primo hover, non al caricamento dell'area. La funzione `comuneTooltipHTML` costruisce la card mostrando solo i campi disponibili (omette righe con valore null).
