# Discordanza fra il GeoParquet OCPR locale e il server MCP hex-intelligence

Nota diagnostica sui dati di accessibilità ai servizi usati dalla dashboard.
Redatta il 2026-09-05.

## Il problema

I dati di accessibilità in `DATA/accessibility_data.json` sono generati da
`generate_accessibility_data.py`, che legge il GeoParquet OCPR locale
(`~/ILAB_DATA/OCPR_LAZIO/DATA/grid_08_adv.geoparquet`). Su disco esiste solo il
Lazio, quindi la copertura si ferma a 189 comuni su 1.967 (9,6%).

Per estendere la copertura a tutte le regioni l'unica fonte disponibile è il server
MCP `hex-intelligence`, che dichiara copertura nazionale ed espone gli stessi nomi di
campo. Ma interrogando le due fonti sugli stessi comuni con lo stesso indicatore e la
stessa aggregazione, **i valori non coincidono**.

Indicatore usato per tutte le prove: `sanita_ospedale||traffic__30__total_ospedale`
(codice MCP `L261`, "Totale ospedali raggiungibili in 30 minuti con trasporto privato").
Aggregazione richiesta a entrambe le fonti: media (`mean`).

| comune | GeoParquet locale | MCP | scarto |
|---|---|---|---|
| Settefrati | 0,131 | 1,836 | +1,705 |
| Picinisco | 0,078 | 1,382 | +1,304 |
| Sutri | 0,309 | 2,644 | +2,335 |
| Aprilia | 3,018 | 5,669 | +2,651 |
| Subiaco | 0,747 | 0,995 | +0,248 |
| Anzio | 2,000 | 2,057 | +0,057 |
| Amatrice | 0,000 | 0,000 | 0,000 |
| Latina | 1,427 | 1,411 | −0,016 |

Su un campione iniziale di 29 comuni SNAI del Lazio coincidevano solo gli 11 che valgono
zero (38%), con scarto medio assoluto 0,349 e massimo 1,710.

## Cosa è stato escluso

Le prove sono state fatte su un campione di 48 comuni del Lazio, scelti per coprire sia
comuni di confine sia comuni interni, con valori MCP letti da
`hex_aggregate_by_comune(LAZIO, ospedali, mean, top_k=400)`.

### 1. Non è la geometria del join

Lo script locale prende i centroidi delle celle H3 e li associa al comune che li contiene
(`within`). Ricalcolando con `intersects`, cioè includendo tutte le celle che toccano il
poligono, i valori restano vicini a quelli originali e lontani da MCP:

| comune | centroide | intersezione | MCP |
|---|---|---|---|
| Settefrati | 0,129 | 0,198 | 1,836 |
| Picinisco | 0,078 | 0,096 | 1,382 |
| San Donato Val di Comino | 0,744 | 0,677 | 1,822 |

Il metodo a centroide riproduce esattamente i valori già presenti in
`accessibility_data.json`, il che conferma che il file rispecchia davvero lo script.

### 2. Non è una variante di aggregazione

Provate quattro varianti sugli stessi 12 comuni, contando quante volte ciascuna cade
entro 0,02 dal valore MCP:

| variante | comuni riprodotti |
|---|---|
| media su tutte le celle (metodo attuale) | 1 su 12 |
| media sulle sole celle con valore > 0 | 2 su 12 |
| media sulle sole celle non nulle | 1 su 12 |
| massimo di cella | 2 su 12 |

Nessuna variante ricostruisce i valori MCP. Nel GeoParquet non ci sono valori nulli
(0 NaN su 22.519 celle), quindi "media su tutte" e "media sui non nulli" coincidono.

### 3. Non è un effetto bordo

L'ipotesi era che il dataset del Lazio calcolasse le isocrone usando solo i servizi interni
all'estensione regionale, sottostimando i comuni di confine, per i quali l'ospedale più
vicino sta in Abruzzo, Umbria, Toscana, Marche, Molise o Campania. **L'ipotesi è smentita**:
lo scarto non cresce avvicinandosi al confine, cresce allontanandosene.

| gruppo | n | scarto medio |
|---|---|---|
| entro 10 km dal confine regionale | 32 | +0,701 |
| oltre 20 km dal confine regionale | 10 | +1,160 |

Correlazione di Pearson fra distanza dal confine e scarto: **+0,286**, di segno opposto a
quello che l'ipotesi richiederebbe.

### 4. Non è un fattore di scala né una conversione di unità

Il rapporto locale/MCP sui 40 comuni con valore locale positivo va da 0,056 (Picinisco) a
1,011 (Latina), media 0,511 e deviazione standard 0,281, cioè un coefficiente di variazione
del 55%. Se fosse una differenza di unità o un fattore moltiplicativo, il rapporto sarebbe
costante.

## Cosa resta, e cosa è dimostrato

Su 48 comuni: MCP è strettamente maggiore in 40 casi (83%), i due valori coincidono in 7
casi (tutti con entrambe le fonti esattamente a zero), e MCP è minore in 1 solo caso
(Latina, −0,016). Scarto medio +0,799, mediano +0,685.

Due elementi vanno letti insieme:

1. **Le aree a zero coincidono.** Dove il dato locale è esattamente 0 su tutto il comune,
   anche MCP è 0 in 7 casi su 8 (Amatrice, Accumoli, Cittareale, Leonessa, Borbona,
   Filettino, Vallepietra; unica eccezione Trevi nel Lazio, locale 0 contro MCP 0,336).
   Le due fonti concordano quindi su *dove* non si raggiunge alcun ospedale in 30 minuti.

2. **Dove il servizio c'è, MCP ne conta di più.** A Settefrati il GeoParquet locale ha
   62 celle di cui solo 7 con valore diverso da zero, e valore massimo di cella pari a 2.
   Una media comunale di 1,836 come quella restituita da MCP è aritmeticamente impossibile
   a partire da quelle celle: richiede che la maggior parte delle celle valga circa 2.

**Conclusione dimostrata**: escluse la geometria del join, la variante di aggregazione,
l'effetto bordo e il fattore di scala, e constatato che il valore MCP non è ottenibile
dalle celle locali con nessuna aggregazione, la discordanza **non nasce da come i dati
vengono aggregati, ma dai valori delle singole celle**, che sono diversi a monte nelle due
fonti. Le due fonti condividono la stessa logica spaziale ma non lo stesso conteggio di
strutture raggiungibili.

**Causa a monte: non determinata.** Il server MCP non espone i valori di cella
(`get_indicator_data` restituisce solo i parametri di fetch per il frontend, non i dati),
quindi il confronto cella per cella non è eseguibile da qui. Le spiegazioni compatibili con
le evidenze, **non verificate**, sono:

- versione diversa del catalogo delle strutture sanitarie (il GeoParquet locale potrebbe
  essere una release più vecchia, con meno presidi censiti)
- versione diversa del grafo stradale o dei parametri di traffico usati per le isocrone
- definizione diversa del campo `total_ospedale`, per esempio somma di sottocategorie che
  nel dato locale non si sovrappongono e nel dato MCP sì

Per chiudere la questione serve accedere al dato di cella lato server, oppure alla scheda di
metadati con la data di produzione e la fonte del catalogo POI di entrambi i dataset.

## Conseguenza operativa

Le due fonti non sono intercambiabili e non vanno mescolate: un dataset con il Lazio da
GeoParquet e le altre regioni da MCP produrrebbe valori non confrontabili fra regioni, e
falserebbe le soglie di severità p33/p67, che sono calcolate sulla distribuzione di tutti i
comuni coperti.

Decisione presa: **rigenerare l'intero dataset da MCP, Lazio incluso**, così che tutte le
regioni siano omogenee. I valori del Lazio già pubblicati in dashboard cambieranno, in
alcuni casi di un fattore superiore a 10.

## Riproducibilità

Gli script diagnostici sono in `script/diagnostica/`:

| script | cosa verifica |
|---|---|
| `build_index.py` | costruisce l'indice comuni SNAI → regione e misura la copertura attuale |
| `validate_mcp_vs_parquet.py` | primo confronto su 29 comuni SNAI del Lazio |
| `diagnose_gap.py` | centroide contro intersezione, contro il JSON pubblicato |
| `diagnose_cause.py` | le quattro varianti di aggregazione |
| `test_edge_effect.py` | correlazione fra scarto e distanza dal confine regionale |
| `stats_finali.py` | statistiche riassuntive sui 48 comuni |

`validate_mcp_vs_parquet.py` va eseguito dopo `build_index.py`, che produce
`comuni_snai_index.json` nella stessa cartella.

Richiedono `~/ILAB_DATA/OCPR_LAZIO/DATA/grid_08_adv.geoparquet`. I valori MCP sono
incorporati negli script come costanti, con indicata la chiamata che li ha prodotti, perché
il server non è interrogabile da uno script Python.
