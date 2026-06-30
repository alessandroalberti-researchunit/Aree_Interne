# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Progetto

Dashboard interattiva sulla Strategia Nazionale Aree Interne (SNAI), cicli 2014-2020 e 2021-2027. 128 aree, ~1.965 comuni, dati ufficiali DPCoe.

## Pipeline di build

Due script vanno eseguiti in sequenza:

```bash
# 1. Genera i GeoJSON (scarica comuni_italia.geojson ~30 MB se non in cache)
python generate_snai_geojson.py

# 2. Genera la dashboard HTML self-contained
python build_dashboard.py
```

Output finale: `dashboard-aree-interne.html` (file singolo, nessun server necessario).

## Architettura

### Flusso dati
```
DATA/*.xlsx  →  generate_snai_geojson.py  →  aree-snai-perimetri.geojson
                                          →  comuni-snai-perimetri.geojson
                        ↓
              build_dashboard.py  →  dashboard-aree-interne.html
              (inietta GeoJSON + metadati come variabili JS embedded)
```

### `generate_snai_geojson.py`
Legge i codici ISTAT comunali dai fogli Excel DPCoe, scarica i confini comunali da openpolis/geojson-italy (cache in `DATA/comuni_italia.geojson`), fa il dissolve con `geopandas` per ottenere i poligoni per area, e semplifica le geometrie (tolerance 0.002° per aree, 0.003° per comuni).

### `build_dashboard.py`
Legge i GeoJSON e gli Excel, calcola statistiche per area (n. comuni, popolazione 2020, distribuzione classificazione ISTAT), poi inietta tutto in un template HTML/JS inline. Il template è hardcoded nello script come stringa Python con placeholder (`SNAI_GEOJSON_PLACEHOLDER`, `KPI_SI_INT`, ecc.).

### Dashboard (Leaflet + Chart.js)
Layout a 3 colonne: sidebar sinistra (grafici Chart.js), mappa centrale Leaflet con filtri, pannello destro dinamico. Navigazione gerarchica Italia → Regione → Area → Comuni via `AREE` e `COMUNI_BY_AREA` (variabili JS embedded).

## Dati

**`DATA/`** — file sorgente (non modificare manualmente):
- `08_elenco-aree-comuni.xlsx` — master list comuni per area (fogli: SI finanziate, 14-20 confermate, 13 aree NO)
- `elenco_aree_snai_14-20-e-21-27.xlsx` — 5 aree solo ciclo 14-20
- `comuni_italia.geojson` — cache confini comunali openpolis (~30 MB); cancellare per ri-scaricare
- Altri Excel: classificazione ISTAT 2020, tavole sintesi, metadati OpenKit

**`DOCS/`** — documentazione ufficiale SNAI (PDF, XLSX), non usata dagli script di build. Organizzata in `Documentazione Regionale/Nord|Centro|Sud` con rapporti istruttoria e dossier per regione; `Nord/Emilia-Romagna/` contiene gli APQ (Accordi di Programma Quadro).

## Concetti dominio

- **Status aree**: `SI` = finanziate ciclo 21-27 (43); `CONF` = confermate da 14-20, non rifinanziate (67); `NO` = non finanziate 21-27 (13); `1420` = solo ciclo 14-20 (5)
- **Classificazione ISTAT**: A=polo, B=polo intercomunale, C=cintura, D=intermedio, E=periferico, F=ultraperiferico. Le aree SNAI coprono solo comuni D/E/F.
- **DPCoe** = Dipartimento per le Politiche di Coesione, ente titolare della strategia

## Dipendenze Python

```
geopandas, pandas, openpyxl, requests
```
