# Registro sessione, 2026-09-05

Cosa è stato fatto, cosa è stato verificato e cosa resta aperto. Documento di
promemoria: per il dettaglio metodologico sulla discordanza dei dati di accessibilità
vedi `NOTE_discordanza-accessibilita.md`.

---

## 1. Incorporazione del workspace `Aree_Interne_Lombardia`

Commit **`ea32454`** su `main`, 14 file, non pushato.

La cartella `C:\Users\aalbe\Desktop\Code\Aree_Interne_Lombardia` (16 MB, 16 file in root,
nessun repo git, nessuno script Python) è stata assorbita in questo repo.

### Dove è finito cosa

**`DATA/nazionali/`** — sei dataset comunali a copertura nazionale, tracciati in git.
I nomi sono stati normalizzati alla convenzione del repo, conservando il dataflow ID ISTAT.

| nome originale | nuovo nome |
|---|---|
| `Redditi_e_principali_variabili_IRPEF_su_base_comunale_CSV_2024.csv` | `redditi-irpef_comuni_2024.csv` |
| `Indice composito di fragilità … (IT1,DF_COMP_FRA_IND_MUNICIPAL_01,1.0).xlsx` | `indice-composito-fragilita_comuni_DF_COMP_FRA_IND_MUNICIPAL_01.xlsx` |
| `Indicatori demografici - comuni (IT1,…).xlsx` | `indicatori-demografici_comuni_DF_DCSS_POP_DEMCITMIG_TV_5.xlsx` |
| `Abitazioni occupate e non occupate - comuni (IT1,…).xlsx` | `abitazioni-occupate-non-occupate_comuni_DF_DCSS_ABITAZIONI_TV_1.xlsx` |
| `Famiglie per titolo di godimento - comuni (IT1,…).xlsx` | `famiglie-titolo-godimento_comuni_DF_DCSS_HUDW_1_COM.xlsx` |
| `Appendice-statistica-Censimprese-ERRATA-CORRIGE.xlsx` | `censimprese-appendice-statistica_errata-corrige.xlsx` |

**`DOCS/`** — `istat-focus_fragilita-comuni-italiani-2022.pdf` in root (è un documento
nazionale), e nuova cartella `Documentazione Regionale/Nord/Lombardia/` con
`elenco-comuni-14-aree-interne-regionali_allegato-a.pdf` e `aree-interne-lombardia.pdf`.

**`output/Lombardia/`** — i tre `.docx` (Report, Perimetro Regionale, Rapporto Integrato)
e `Sceneggiatura_PowerPoint_Aree_Interne.md` (26 slide). Nuova convenzione: `output/`
raccoglie gli elaborati per regione. La cartella `presentazione ER/` in root ha la stessa
funzione per l'Emilia-Romagna e **non è ancora stata spostata** sotto `output/`.

### Verifiche fatte

- Copia verificata con md5: **13 file su 13 identici** all'originale, 9,62 MB.
- `snai-dossier-regionale-lombardia.pdf` **non è stato copiato**: era già nel repo come
  `DOCS/Documentazione Regionale/Nord/snai-dossier_lombardia.pdf`, md5 identico
  (`1d52fdb2619a763df92f6c8500b031d2`).
- `Aree interne Lombardia.pdf` è invece un documento **diverso** da
  `rapporto-istruttoria_lombardia.pdf` (md5 diversi), quindi è stato conservato.

### Cancellazione della cartella originale

Audit preventivo su tutti i 16 file: **14 presenti nel repo con md5 identico, 2 esclusi
deliberatamente, 0 persi**. I due esclusi:

- `CLAUDE.md` — contenuto rifuso nel `CLAUDE.md` del repo
- `.claude/settings.local.json` — permission list riferita a script già cancellati

La cartella è stata spostata nel **Cestino di Windows**, non eliminata definitivamente,
quindi è ancora recuperabile.

---

## 2. Correzioni fatte durante l'incorporazione

Tre cose emerse ispezionando i file, tutte documentate in `CLAUDE.md`:

1. **Censimprese non è a granularità comunale.** Il `CLAUDE.md` del workspace lombardo lo
   dichiarava municipale, ma le 77 tavole sono per settore ATECO e classe di addetti,
   aggregate a livello nazionale.

2. **Gli export IstatData ingannano `openpyxl`.** Con `read_only=True` i quattro xlsx ISTAT
   restituiscono `max_row=1, max_column=1`, perché la dimensione dichiarata nel file è
   errata. Con `read_only=False` compaiono le dimensioni reali: 7.909 / 8.039 / 8.063 /
   8.046 righe.

3. **La colonna territoriale di quegli export contiene nomi di comune, non codici ISTAT.**
   Il CSV MEF ha invece `Codice Istat Comune`. Quindi il CSV si aggancia direttamente ai
   GeoJSON, i quattro xlsx no: serve una normalizzazione dei nomi con gestione degli
   omonimi. **Questo è l'ostacolo principale se si vogliono portare quei dati in dashboard.**

Risolto anche un conflitto: il `CLAUDE.md` lombardo descriveva la classificazione ISTAT con
5 classi (A polo, B cintura, C intermedio, D periferico, E ultraperiferico), quello del repo
con 6 (A polo, B polo intercomunale, C cintura, D intermedio, E periferico, F
ultraperiferico). È stata tenuta la versione a 6 classi, coerente con la nota tecnica NUVAP
in `DOCS/`.

Aggiunta infine in `CLAUDE.md` la sezione sui server MCP utili al progetto, e una nota sul
perimetro regionale lombardo DGR 1705/2023 (14 aree, 334 comuni oltre ai 159 SNAI),
**marcata come non verificata** perché quel numero viene dalla sceneggiatura del deck e non
da una fonte primaria.

---

## 3. Estensione dell'accessibilità a tutte le regioni: stato del lavoro

### Punto di partenza

`DATA/accessibility_data.json` copre **189 comuni su 1.967 (9,6%)**, generati da
`generate_accessibility_data.py` a partire da `~/ILAB_DATA/OCPR_LAZIO/DATA/grid_08_adv.geoparquet`.
La copertura sconfina oltre il Lazio perché le celle H3 al bordo cadono in comuni
limitrofi: Lazio 134, Abruzzo 25, Umbria 17, Molise 7, Toscana 5, Marche 1.

### Vincolo trovato

Su disco esiste **solo `OCPR_LAZIO`**. Lo script elenca 7 regioni ma le altre 6 non hanno il
GeoParquet, quindi vengono saltate. Ricerca sul filesystem: nessun altro `grid_08_adv.geoparquet`.

### Fonte alternativa e problema aperto

Il server MCP `hex-intelligence` ha copertura nazionale e gli stessi nomi di campo
(`sanita_ospedale||traffic__30__total_ospedale`, codice `L261`), e funziona anche su regioni
non elencate nel suo docstring (verificato su Marche). **Ma restituisce valori diversi** da
quelli del GeoParquet locale: su 48 comuni del Lazio, MCP è più alto in 40 casi (83%),
scarto medio +0,799, massimo +2,651.

Sono state escluse per via sperimentale la geometria del join, quattro varianti di
aggregazione, l'effetto bordo e il fattore di scala. La discordanza nasce dai valori delle
singole celle, diversi a monte nelle due fonti; la causa a monte **non è stata determinata**
perché il server non espone il dato di cella. Dettaglio completo in
`NOTE_discordanza-accessibilita.md`.

### Decisione presa

**Rigenerare l'intero dataset da MCP, Lazio incluso**, per avere tutte le regioni omogenee.
I valori del Lazio già in dashboard cambieranno, in alcuni casi di oltre un fattore 10.

### Dove si è fermato il lavoro

La rigenerazione **non è ancora stata eseguita**. Ostacoli operativi individuati:

1. **Nomi regione MCP da determinare.** `VALLE-D'AOSTA`, `VALLE_D_AOSTA` e `VALLE-DAOSTA`
   restituiscono tutti "Metadati non disponibili". Dai risultati di ricerca si sono visti
   `TRENTINO-ALTO_ADIGE` e `FRIULI-VENEZIA_GIULIA`, quindi la convenzione esiste ma va
   ricostruita regione per regione. Nota: PA Trento e PA Bolzano sono 21 regioni
   nell'indice del progetto ma probabilmente una sola regione lato MCP.

2. **Nessuna via di export su file.** `get_indicator_data` restituisce solo i parametri di
   fetch per il frontend, non i valori; `hex_query_data` lavora per indirizzo. L'unico tool
   utile è `hex_aggregate_by_comune`, che però fa passare i dati attraverso la conversazione:
   1.967 comuni × 6 indicatori = **11.802 valori da trascrivere a mano**. È il collo di
   bottiglia principale.

3. **Il blocco `sll` va ripensato.** Il JSON attuale contiene anche 32 SLL, aggregati dalle
   celle H3. MCP aggrega per comune, non per SLL: i valori SLL andranno ricostruiti
   aggregando i comuni, con un criterio di ponderazione da decidere.

### Cosa è già pronto

- `script/diagnostica/build_index.py` produce `comuni_snai_index.json`, l'indice dei 1.967
  comuni SNAI con procom, area, status e regione, ricavando la regione da `AREE_BASE` in
  `build_dashboard.py`.
- Verificato che **non esistono omonimi fra comuni SNAI della stessa regione**, quindi il
  join per nome fra output MCP e codici ISTAT è sicuro.
- Codici indicatore MCP già identificati: `L261` ospedali, `L125` istruzione, `L211` sport.
  Restano da individuare quelli per `total_sanita`, `total_cultura` e `total_infrastrutture`.

---

## 4. Stato del repo

| | |
|---|---|
| ultimo commit | `ea32454` Incorpora il workspace Aree_Interne_Lombardia |
| non committati | `NOTE_discordanza-accessibilita.md`, `NOTE_sessione-2026-09-05.md`, `script/diagnostica/` |
| push | non effettuato |

`dashboard-aree-interne.html` **non è stata rigenerata** in questa sessione: riflette ancora
i dati di accessibilità del solo Lazio da GeoParquet.
