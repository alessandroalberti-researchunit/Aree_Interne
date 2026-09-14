# Discordanza fra il GeoParquet OCPR locale e il server MCP hex-intelligence

Nota diagnostica sui dati di accessibilità ai servizi usati dalla dashboard.
Redatta il 2026-09-05, **rivista il 2026-09-06 con la verifica sull'intera popolazione
regionale del Lazio**, che ha ribaltato una delle conclusioni iniziali.

## Il problema

I dati di accessibilità in `DATA/accessibility_data.json` sono generati da
`generate_accessibility_data.py`, che legge il GeoParquet OCPR locale
(`~/ILAB_DATA/OCPR_LAZIO/DATA/grid_08_adv.geoparquet`). Su disco esiste solo il Lazio,
quindi la copertura si ferma a 189 comuni su 1.967 (9,6%).

L'unica fonte con copertura nazionale è il server MCP `hex-intelligence`, che espone gli
stessi nomi di campo. Ma sugli stessi comuni, stesso indicatore e stessa aggregazione,
**i valori non coincidono**.

Indicatore usato in tutte le prove: `sanita_ospedale||traffic__30__total_ospedale`
(codice MCP `L261`). Aggregazione richiesta a entrambe le fonti: media (`mean`).

## Verifica sull'intera popolazione: 378 comuni del Lazio

Entrambe le fonti coprono tutti e 378 i comuni, appaiamento completo, nessun comune orfano.

| esito | comuni | quota |
|---|---|---|
| MCP maggiore del locale | 340 | 89,9% |
| valori coincidenti | 31 | 8,2% |
| locale maggiore di MCP | 7 | 1,9% |

Scarto medio **+0,810**, mediano +0,667, minimo −0,190, massimo +6,355. I 7 casi in cui il
locale è maggiore sono tutti marginali (scarto massimo −0,190, su comuni con 12-39 celle).
Dei 31 valori coincidenti, 30 sono comuni a zero per entrambe le fonti e uno solo è un
accordo su valore positivo (Manziana, 1,0 esatto per entrambe).

## Cosa è stato escluso

### 1. Non è un dataset diverso né una colonna sbagliata

Il parquet locale ha **277 colonne**, il server dichiara **277 indicatori urbani**. Cercando
"ospedale" fra le colonne, una sola corrisponde a `traffic__30__total_ospedale`: non c'è
ambiguità di scelta.

### 2. Non è la geometria del join

Ricalcolando con `intersects` invece che con il centroide, i valori restano vicini
all'originale e lontani da MCP (Settefrati 0,129 → 0,198, contro MCP 1,836). Il metodo a
centroide riproduce esattamente `accessibility_data.json`, quindi il file rispecchia lo script.

### 3. Non è una variante di aggregazione

Su 12 comuni, contando quante volte ciascuna variante cade entro 0,02 dal valore MCP:
media su tutte le celle 1/12, media sulle sole celle positive 2/12, media sui non nulli
1/12, massimo di cella 2/12. Nel parquet non ci sono valori nulli (0 NaN su 22.519 celle).

### 4. Non è la risoluzione H3

Risalendo le celle r8 ai genitori r7 e r6 con h3 4.5.0, le medie comunali restano vicine a
r8 e non si avvicinano a MCP (Settefrati 0,131 a r8, 0,214 a r7, 0,341 a r6, contro 1,836).
Aggregando i genitori per somma invece che per media i valori esplodono (r6 somma: 16,0).

### 5. Non è un effetto bordo

L'ipotesi era che il dataset regionale ignorasse i servizi fuori dal Lazio, penalizzando i
comuni di confine. Smentita: lo scarto medio è +0,701 entro 10 km dal confine e +1,160 oltre
20 km, con correlazione distanza/scarto **+0,286**, di segno opposto a quello richiesto.

### 6. Non è un catalogo POI mancante

In tutti i capoluoghi laziali il dato locale vede il proprio ospedale entro 15 minuti
(`max15 ≥ 1`). Le uniche due eccezioni sul campione testato, Gaeta e Montefiascone, hanno
`max15 = 0` ma `max30 = 1`, plausibile visto il ridimensionamento di quei presidi. Il
catalogo delle strutture non è quindi rotto.

## La causa: isocrona sotto-estesa nella build locale

Tre evidenze convergenti sull'intera popolazione.

### Il rapporto cresce col livello di accessibilità

| fascia MCP | n | rapporto locale/MCP | p25 | p75 |
|---|---|---|---|---|
| 0,00 – 0,25 | 35 | 0,274 | 0,000 | 0,000 |
| 0,25 – 0,50 | 15 | 0,211 | 0,000 | 0,218 |
| 0,50 – 1,00 | 94 | 0,361 | 0,116 | 0,614 |
| 1,00 – 2,00 | 132 | 0,463 | 0,239 | 0,645 |
| 2,00 – 5,00 | 50 | 0,476 | 0,258 | 0,663 |
| oltre 5,00 | 22 | 0,642 | 0,541 | 0,720 |

Correlazione fra livello MCP e rapporto: Pearson +0,215, **Spearman +0,422**. È la firma di
un effetto soglia: dove i servizi abbondano si perde una quota del conteggio, dove se ne
raggiunge a stento uno lo si perde del tutto.

### La quota di celle che vedono almeno un ospedale collassa nelle zone marginali

| fascia MCP | n | quota media di celle locali non nulle |
|---|---|---|
| 0,0 – 0,5 | 50 | 0,025 |
| 0,5 – 1,0 | 94 | 0,335 |
| 1,0 – 2,0 | 132 | 0,606 |
| oltre 2,0 | 72 | 0,795 |

### 49 comuni vengono azzerati dal locale ma non da MCP

Il locale dà zero ospedali raggiungibili in **79 comuni**, MCP in **30**. I 49 di differenza
includono casi non plausibili: Casape ha zero secondo il locale e 1,961 secondo MCP, pur
essendo a **26,1 minuti dal proprio polo** secondo ISTAT. Un comune a 26 minuti dal centro
che eroga i servizi non può avere zero ospedali raggiungibili in 30 minuti in auto. Stesso
schema per Marta (25,3 minuti dal polo), Barbarano Romano (31,6), San Giovanni Incarico (29,1).

Complessivamente la media regionale locale a 30 minuti è **0,8309** contro **1,6409** di MCP:
un rapporto di **0,506**, cioè il dato locale conta circa metà delle strutture. Per confronto,
la media locale a 15 minuti è 0,0987, quindi il divario non si spiega con uno scambio fra le
due soglie temporali: la portata effettiva di MCP eccede quella del locale a 30 minuti.

## Arbitraggio con riferimento indipendente: correzione

Come arbitro esterno è stato usato il **tempo medio di percorrenza al polo** della Mappa Aree
Interne 2020 (ISTAT/NUVAP), in `DATA/mappa-ai-2020-elenco-classificazione-comuni.xlsx`.
Attesa: più lontano il polo, meno ospedali raggiungibili.

**Su tutti i 378 comuni del Lazio:**

| correlazione col tempo al polo | locale | MCP |
|---|---|---|
| Pearson | −0,368 | **−0,399** |
| Spearman | −0,529 | **−0,558** |

| minuti al polo | n | locale medio | MCP medio |
|---|---|---|---|
| 0 – 15 | 29 | 1,851 | 2,828 |
| 15 – 25 | 93 | 1,330 | 2,464 |
| 25 – 40 | 190 | 0,632 | 1,428 |
| oltre 40 | 66 | 0,252 | 0,574 |

⚠️ **Correzione rispetto alla prima stesura.** Su un campione di 56 comuni scelti a mano per
coprire tutto il range di valori, l'arbitraggio dava il locale come più coerente
(Spearman −0,668 contro −0,561). Su tutti i 378 comuni il risultato **si inverte** e MCP
risulta più coerente su entrambe le misure. Il campione iniziale non era casuale e il suo
esito non era rappresentativo: vale il risultato sull'intera popolazione.

## Conclusione

La discordanza **non nasce dall'aggregazione** (esclusi join, variante, risoluzione, bordo)
**ma dai valori delle singole celle**: la build locale conta circa metà delle strutture
raggiungibili, con un deficit che si concentra là dove il servizio è al limite della portata,
fino ad azzerare 49 comuni che MCP considera serviti.

Il meccanismo compatibile con tutte le evidenze è una **isocrona sotto-estesa nella build
locale**: stessa etichetta "30 minuti in auto", ma portata effettiva minore. Non è possibile
identificare da qui il parametro responsabile (tempo di percorrenza, profilo di velocità,
versione del grafo stradale) perché il server non espone il dato di cella:
`get_indicator_data` restituisce solo i parametri di fetch per il frontend. Questa parte
resta **inferenza, non verificata**.

Sul riferimento ISTAT, però, **MCP è la fonte più coerente delle due**, e i casi come Casape
indicano che dove le due divergono è il locale a sbagliare. Il GeoParquet locale è
verosimilmente una build più vecchia o mal parametrizzata.

## Conseguenza operativa

Le due fonti non vanno mescolate: un dataset con il Lazio da GeoParquet e le altre regioni da
MCP produrrebbe valori non confrontabili e falserebbe le soglie di severità p33/p67, che sono
calcolate sulla distribuzione di tutti i comuni coperti.

Decisione: **rigenerare l'intero dataset da MCP, Lazio incluso**. I valori del Lazio già
pubblicati cambieranno, in alcuni casi di oltre un fattore 10. La migrazione è motivata sia
dall'omogeneità fra regioni sia, alla luce dell'arbitraggio ISTAT sull'intera popolazione,
da una maggiore coerenza del dato MCP con il riferimento ufficiale.

## Riproducibilità

Script in `script/diagnostica/`:

| script | cosa verifica |
|---|---|
| `build_index.py` | indice comuni SNAI → regione e copertura attuale |
| `validate_mcp_vs_parquet.py` | primo confronto su 29 comuni SNAI del Lazio |
| `diagnose_gap.py` | centroide contro intersezione, contro il JSON pubblicato |
| `diagnose_cause.py` | le quattro varianti di aggregazione |
| `test_edge_effect.py` | correlazione fra scarto e distanza dal confine |
| `test_resolution.py` | aggregazione ai genitori H3 r7 e r6 |
| `test_soglia.py` | regimi del rapporto locale/MCP sul campione |
| `verifica_lazio_completo.py` | **verifica definitiva su tutti i 378 comuni** |

Dati di appoggio nella stessa cartella: `mcp_lazio_ospedali.json` (i 378 valori MCP, con la
chiamata che li ha prodotti) e `confronto_lazio_completo.csv` (tabella comune per comune).
Richiedono `~/ILAB_DATA/OCPR_LAZIO/DATA/grid_08_adv.geoparquet`, `geopandas`, `h3` e
`openpyxl`. I valori MCP sono su file perché il server non è interrogabile da uno script Python.
