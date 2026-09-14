# Raccolta accessibilità da MCP hex-intelligence — stato

Aggiornato: 2026-09-06

Obiettivo: sostituire `DATA/accessibility_data.json` (oggi 189 comuni, solo Lazio da
GeoParquet) con un dataset omogeneo per tutti i 1.967 comuni SNAI, generato da MCP.
Motivazione della scelta della fonte: `NOTE_discordanza-accessibilita.md`.

## Avanzamento

| regione MCP | comuni regione | comuni SNAI | stato |
|---|---|---|---|
| UMBRIA | 92 | 59 | ✅ |
| BASILICATA | 131 | 75 | ✅ |
| MOLISE | 136 | 108 | ✅ |
| FRIULI-VENEZIA_GIULIA | 215 | 71 | ✅ |
| MARCHE | 225 | 80 | ✅ |
| LIGURIA | 234 | 108 | ✅ |
| PUGLIA | 257 | 55 | ✅ |
| TOSCANA | 273 | 115 | ✅ |
| TRENTINO-ALTO_ADIGE | 282 | 54 (PA Trento 34 + PA Bolzano 20) | ✅ |
| ABRUZZO | 305 | 141 | ✅ |
| EMILIA-ROMAGNA | 330 | 108 | ✅ |
| SARDEGNA | 377 | 45 | ✅ |
| LAZIO | 378 | 134 | ✅ |
| SICILIA | 391 | 155 | ✅ |
| CALABRIA | 404 | 109 | ✅ |
| CAMPANIA | 549 | 143 | ✅ |
| VENETO | 560 | 56 | ✅ |
| PIEMONTE | 1179 | 145 | ✅ |
| LOMBARDIA | 1501 | 159 | ✅ |

**Raccolta completata: 1.920 comuni SNAI su 1.967 (97,6%), il massimo possibile
escludendo la Valle d’Aosta (47 comuni, assente dal dataset MCP).**

## Lacuna strutturale: Valle d'Aosta

La regione **non esiste nel dataset MCP**. Provate senza successo le grafie
`VALLE-D'AOSTA`, `VALLE_D_AOSTA`, `VALLE-DAOSTA`, `VALLE-D_AOSTA`, `VALLE_D'AOSTA`,
`VALLE D'AOSTA`, `AOSTA`, `VALLEDAOSTA`: tutte rispondono "Metadati non disponibili".
Non compare in nessuna delle liste "Disponibile solo in" restituite da
`search_urban_indicators`.

Conseguenza: **47 comuni SNAI della Valle d'Aosta resteranno senza dati di accessibilità**,
e la copertura massima raggiungibile è 1.920 su 1.967 (97,6%).

## Come proseguire

Per ogni regione, sei chiamate a `hex_aggregate_by_comune` con `agg_type="mean"` e
`top_k` pari al numero di comuni della regione, poi si trascrivono i soli comuni SNAI.

Query verificate, ciascuna risolve al campo indicato (controllare sempre il campo
`indicator` nella risposta):

| posizione | query | campo risolto | codice |
|---|---|---|---|
| 1 ospedali | `totale ospedali raggiungibili in 30 minuti con trasporto privato traffico` | `sanita_ospedale\|\|traffic__30__total_ospedale` | L261 |
| 2 sanita | `totale servizi sanitari raggiungibili in 30 minuti con trasporto privato traffico` | `ovm_places_sanita\|\|traffic__30__total_sanita` | L183 |
| 3 istruzione | `totale strutture educative raggiungibili in 30 minuti con trasporto privato traffico` | `ovm_places_istruzione\|\|traffic__30__total_istruzione` | L125 |
| 4 trasporti | `totale infrastrutture OVM raggiungibili in 30 minuti con trasporto privato traffico` | `ovm_infr_infrastrutture\|\|traffic__30__total_infrastrutture` | L061 |
| 5 sport | `totale strutture sportive raggiungibili in 30 minuti con trasporto privato traffico` | `ovm_places_sport\|\|traffic__30__total_sport` | L211 |
| 6 cultura | `totale luoghi culturali raggiungibili in 30 minuti con trasporto privato traffico` | `ovm_places_cultura\|\|traffic__30__total_cultura` | L081 |

⚠️ Due query intuitive **sbagliano bersaglio** e cadono su `total_ristorazione`:
"totale infrastrutture di trasporto…" e "totale luoghi di cultura…". Usare le formulazioni
esatte della tabella.

## Formato dei file

Un file per regione MCP, `valori` con una riga per comune SNAI e sei valori nell'ordine
`["ospedali","sanita","istruzione","trasporti","sport","cultura"]`, arrotondati a 2 decimali
(il JSON finale arrotonda comunque a 2).

L'elenco dei comuni SNAI per regione si ottiene da
`script/diagnostica/comuni_snai_index.json` (prodotto da `build_index.py`).
Verificato che **non esistono omonimi fra comuni SNAI della stessa regione**, quindi il join
per nome è sicuro.

## Passi finali, dopo la raccolta

1. Unire i file regionali, mappare i nomi comune → `procom` a 6 cifre.
2. Ricalcolare `soglie` (p33/p67/mean per indicatore) sulla distribuzione dei comuni coperti
   e `indicatori` (label/max/mean).
3. Ricostruire il blocco `sll`: MCP aggrega per comune, non per SLL, quindi i 32 SLL vanno
   ricavati aggregando i comuni, con un criterio di ponderazione da decidere.
4. Scrivere `DATA/accessibility_data.json` con `fonte` aggiornata e `regioni_coperte`.
5. Rigenerare la dashboard con `build_dashboard.py`.
6. Aggiornare `NOTE.md` e `CLAUDE.md` sul cambio di fonte.
