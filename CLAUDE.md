# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Progetto

Dashboard interattiva sulla Strategia Nazionale Aree Interne (SNAI), cicli 2014-2020 e 2021-2027. 128 aree, ~1.965 comuni, dati ufficiali DPCoe.

## Struttura cartelle

In root sta solo il deliverable web (`dashboard-aree-interne.html` e la landing
`index.html`, che lo linka con path relativo). Tutto il resto in sottocartelle:

| Cartella | Contenuto |
|---|---|
| `script/` | pipeline (`generate_*.py`, `build_dashboard.py`) e `script/diagnostica/` per le verifiche |
| `geo/` | GeoJSON prodotti: `aree-snai-perimetri`, `comuni-snai-perimetri`, `sll-perimetri` |
| `DATA/` | dati sorgente, incl. `mcp_accessibilita/`, `sll_2021/`, `nazionali/`, `tavole_istat_2023/` |
| `DOCS/` | documentazione ufficiale SNAI; `DOCS/progetto/` le note di progetto (`NOTE*.md`) |
| `output/` | elaborati prodotti, una sottocartella per regione |

## Pipeline di build

Due script vanno eseguiti in sequenza:

```bash
# 1. Genera i GeoJSON (scarica comuni_italia.geojson ~30 MB se non in cache)
python script/generate_snai_geojson.py

# 2. Genera la dashboard HTML self-contained
python script/build_dashboard.py
```

Gli script risolvono i percorsi da `__file__`, quindi funzionano da qualsiasi
directory di lavoro.

Output finale: `dashboard-aree-interne.html` (file singolo, nessun server necessario).

I dati di accessibilità sono già su disco in `DATA/accessibility_data.json` e non vanno
rigenerati a ogni build. Servono solo se cambiano i dati MCP a monte:

```bash
python script/generate_accessibility_from_mcp.py   # merge DATA/mcp_accessibilita/* -> accessibility_data.json
```

## Architettura

### Flusso dati
```
DATA/*.xlsx  →  script/generate_snai_geojson.py  →  geo/aree-snai-perimetri.geojson
                                                 →  geo/comuni-snai-perimetri.geojson
                        ↓
              script/build_dashboard.py  →  dashboard-aree-interne.html
              (inietta GeoJSON + metadati come variabili JS embedded)
```

### `script/generate_snai_geojson.py`
Legge i codici ISTAT comunali dai fogli Excel DPCoe, scarica i confini comunali da openpolis/geojson-italy (cache in `DATA/comuni_italia.geojson`), fa il dissolve con `geopandas` per ottenere i poligoni per area, e semplifica le geometrie (tolerance 0.002° per aree, 0.003° per comuni).

### `script/build_dashboard.py`
Legge i GeoJSON e gli Excel, calcola statistiche per area (n. comuni, popolazione 2020, distribuzione classificazione ISTAT), poi inietta tutto in un template HTML/JS inline. Il template è hardcoded nello script come stringa Python con placeholder (`SNAI_GEOJSON_PLACEHOLDER`, `KPI_SI_INT`, ecc.).

### Dashboard (Leaflet + Chart.js)
Layout a 3 colonne: sidebar sinistra (grafici Chart.js), mappa centrale Leaflet con filtri, pannello destro dinamico. Navigazione gerarchica Italia → Regione → Area → Comuni via `AREE` e `COMUNI_BY_AREA` (variabili JS embedded).

## Dati

**`DATA/`** — file sorgente (non modificare manualmente):
- `08_elenco-aree-comuni.xlsx` — master list comuni per area (fogli: SI finanziate, 14-20 confermate, 13 aree NO)
- `elenco_aree_snai_14-20-e-21-27.xlsx` — 5 aree solo ciclo 14-20
- `comuni_italia.geojson` — cache confini comunali openpolis (~30 MB); cancellare per ri-scaricare
- Altri Excel: classificazione ISTAT 2020, tavole sintesi, metadati OpenKit
- `sll_2021/` — sorgenti SLL 2021 ISTAT: shapefile `SLL_2021.*`, JSON di composizione (comune → SLL), `metadati_SLL_2021.xlsx` e il PDF metodologico sulla specializzazione produttiva. Consumati da `script/generate_sll_geojson.py`.

**Accessibilità ai servizi**:
- `DATA/mcp_accessibilita/*.json` — un file per regione MCP con i 6 indicatori di accessibilità per comune SNAI, raccolti dal server MCP `hex-intelligence`. `_STATO.md` documenta le query verificate (due formulazioni intuitive cadono sull'indicatore sbagliato) e il formato.
- `DATA/accessibility_data.json` — output del merge, consumato da `script/build_dashboard.py`. Copre 1.920 comuni SNAI su 1.967 (97,6%): la **Valle d'Aosta è assente dal dataset MCP**, quindi i suoi 47 comuni restano senza dati e 97,6% è il massimo raggiungibile.
- Il blocco `sll` è ricavato aggregando i soli comuni SNAI di ciascun SLL, pesati per superficie: descrive la porzione SNAI del sistema locale, non l'intero SLL. Dettagli in `DOCS/progetto/NOTE.md`.

**`DATA/nazionali/`** — dataset socioeconomici comunali a copertura nazionale, non ancora usati dagli script di build (importati dal workspace `Aree_Interne_Lombardia`):

| File | Fonte | Granularità | Struttura |
|------|-------|-------------|-----------|
| `redditi-irpef_comuni_2024.csv` | MEF | 7.897 comuni | CSV `;`, 53 colonne, header a riga 1, colonna `Codice Istat Comune`; anno di imposta 2024 su tutte le righe |
| `indice-composito-fragilita_comuni_DF_COMP_FRA_IND_MUNICIPAL_01.xlsx` | ISTAT | 7.909 righe | export IstatData, anno 2018, indice + 52 componenti |
| `indicatori-demografici_comuni_DF_DCSS_POP_DEMCITMIG_TV_5.xlsx` | ISTAT | 8.039 righe | export IstatData, anno 2024, 5 indicatori |
| `abitazioni-occupate-non-occupate_comuni_DF_DCSS_ABITAZIONI_TV_1.xlsx` | ISTAT | 8.063 righe | export IstatData, anni 2019/2021/2023 |
| `famiglie-titolo-godimento_comuni_DF_DCSS_HUDW_1_COM.xlsx` | ISTAT | 8.046 righe | export IstatData, anno 2021, proprietà/affitto/altro |
| `censimprese-appendice-statistica_errata-corrige.xlsx` | ISTAT | **non comunale** | 77 tavole per settore ATECO e classe di addetti, aggregato nazionale |

Due avvertenze verificate sui quattro export IstatData:

1. `openpyxl.load_workbook(..., read_only=True)` restituisce `max_row=1, max_column=1` perché la dimensione dichiarata nel file è errata. Usare `read_only=False`, oppure `pandas.read_excel` con `skiprows`.
2. L'intestazione occupa più righe (metadati a r1-r3, poi `Anno`/`Indicatore`/`Territorio`; l'offset varia per file) e la colonna territoriale contiene **nomi di comune, non codici ISTAT**. Il join con i GeoJSON, che usano i codici, richiede quindi una normalizzazione dei nomi e la gestione degli omonimi.

**`DOCS/`** — documentazione ufficiale SNAI (PDF, XLSX), non usata dagli script di build. Organizzata in `Documentazione Regionale/Nord|Centro|Sud` con rapporti istruttoria e dossier per regione; `Nord/Emilia-Romagna/` contiene gli APQ (Accordi di Programma Quadro), `Nord/Lombardia/` l'elenco dei comuni delle 14 aree interne regionali (Allegato A). `DOCS/progetto/` contiene invece le note prodotte dal progetto: `NOTE.md` (tracciabilità e decisioni tecniche), `NOTE_discordanza-accessibilita.md`, `NOTE_sessione-2026-09-05.md`.

**`output/`** — elaborati prodotti dal progetto, per regione. `output/Lombardia/` contiene i tre report `.docx` e la sceneggiatura del deck (26 slide); `output/Emilia-Romagna/` il materiale del convegno RER (ex cartella `presentazione ER/` in root); `output/Puglia/` il profilo dell'area Alta Murgia.

## Concetti dominio

- **Status aree**: `SI` = finanziate ciclo 21-27 (43); `CONF` = confermate da 14-20, non rifinanziate (67); `NO` = non finanziate 21-27 (13); `1420` = solo ciclo 14-20 (5)
- **Classificazione ISTAT**: A=polo, B=polo intercomunale, C=cintura, D=intermedio, E=periferico, F=ultraperiferico. Le aree SNAI coprono solo comuni D/E/F.
- **DPCoe** = Dipartimento per le Politiche di Coesione, ente titolare della strategia
- **Perimetro regionale**: alcune regioni affiancano al perimetro SNAI nazionale un perimetro proprio. Per la Lombardia, secondo `output/Lombardia/Sceneggiatura_PowerPoint_Aree_Interne.md`, la DGR 1705/2023 definisce 14 aree con 334 comuni aggiuntivi rispetto ai 159 del perimetro SNAI. Dato non ancora verificato contro l'Allegato A in `DOCS/Documentazione Regionale/Nord/Lombardia/`.

## Dipendenze Python

```
geopandas, pandas, openpyxl, requests
```

## Server MCP utili al progetto

Diversi server MCP connessi coprono gli stessi territori dei dati locali e servono ad arricchirli:

- **Aree Interne** — dati SNAI (aree, comuni, classificazione, GeoJSON); sovrapposto alle fonti in `DATA/`, utile per verifiche incrociate
- **istat** — statistiche ISTAT via SDMX, granularità minima comune, con serie storiche
- **hex-intelligence** — indicatori H3 sub-comunali, copertura nazionale, snapshot censimento 2021
- **bes** — indicatori di benessere provinciali (107 province, 2004-2024)
- **hydrogeo-intelligence** — rischio idrogeologico ISPRA, pertinente all'indice di fragilità
- **climate-intelligence** — rischio climatico ERA5/CMIP6
- **hfa-navigator** — indicatori sanitari provinciali, pertinenti alla dimensione salute della SNAI
- **migrations-intelligence** — mercato del lavoro e mismatch competenze (Excelsior)
- **innovation-intelligence** — dati innovazione delle sole province lombarde
