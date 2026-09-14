# Registro sessione, 2026-09-06

Cosa è stato fatto, cosa è stato verificato e cosa resta aperto. Continua
`NOTE_sessione-2026-09-05.md`, che si era fermato a metà della raccolta MCP.

Due filoni:

1. **Completamento della raccolta dei dati di accessibilità da MCP** e loro integrazione
   nella dashboard, chiudendo il lavoro aperto dalla sessione precedente.
2. **Riorganizzazione delle cartelle del repo**: in root resta solo il deliverable web.

---

## 1. Accessibilità ai servizi: raccolta MCP completata

### Punto di raccordo con la sessione precedente

`DATA/accessibility_data.json` copriva **189 comuni SNAI, solo Lazio**, da GeoParquet
locale. La motivazione dell'abbandono di quella fonte è in
`NOTE_discordanza-accessibilita.md`. La raccolta dal server MCP `hex-intelligence` era
arrivata a 12 regioni su 19 (1.019 comuni).

### Regioni completate in questa sessione

| regione MCP | comuni regione | comuni SNAI |
|---|---|---|
| LAZIO | 378 | 134 |
| SICILIA | 391 | 155 |
| CALABRIA | 404 | 109 |
| CAMPANIA | 549 | 143 |
| VENETO | 560 | 56 |
| PIEMONTE | 1.179 | 145 |
| LOMBARDIA | 1.501 | 159 |

### Copertura finale

**1.920 comuni SNAI su 1.967 (97,6%)**, che è **il massimo raggiungibile** con questa
fonte. I 47 comuni mancanti sono tutti in **Valle d'Aosta**, regione strutturalmente
assente dal dataset MCP: nessuna grafia del nome viene riconosciuta dal server (le prove
fatte sono elencate in `DATA/mcp_accessibilita/_STATO.md`).

Dettaglio per file in `_STATO.md`; il conteggio si riproduce con
`python script/diagnostica/valida_mcp.py`, che confronta ogni file regionale con l'indice
dei comuni SNAI e segnala mancanti, extra e valori malformati. Tutti i 19 file passano a
0 mancanti / 0 extra / 0 malformati.

### Il collo di bottiglia e come si è sbloccato

Il server MCP non espone un export su file: fino a metà sessione ogni valore passava
dalla conversazione e andava trascritto a mano nel JSON regionale. Con Piemonte
(1.179 comuni) il risultato ha **superato il limite di token del tool**, che lo ha quindi
**salvato su file** in
`~/.claude/projects/<progetto>/<sessione>/tool-results/mcp-*hex_aggregate_by_comune-*.txt`.

Da qui è nato **`script/diagnostica/estrai_mcp.py`**, che legge quei file, ne verifica il
campo `indicator`, tiene la versione più recente per ciascuno dei 6 indicatori e assembla
il JSON regionale senza passare dalla conversazione:

```bash
python script/diagnostica/estrai_mcp.py PIEMONTE "Piemonte"
python script/diagnostica/estrai_mcp.py TRENTINO-ALTO_ADIGE "PA Trento,PA Bolzano"
```

Cerca in tutte le sessioni del progetto; `MCP_TOOL_RESULTS` forza una cartella specifica.
Questo rimuove la trascrizione manuale da qualsiasi raccolta futura, a patto che il
risultato MCP sia abbastanza grande da essere salvato su file (regioni oltre ~600 comuni).

### Merge e nuova pipeline

Nuovo script **`script/generate_accessibility_from_mcp.py`**:

```
DATA/mcp_accessibilita/*.json        (19 file regionali, 188 KB)
script/diagnostica/comuni_snai_index.json   (nome+regione -> procom)
geo/comuni-snai-perimetri.geojson    (superfici per pesare gli SLL)
DATA/sll_2021/Sistemi Locali…json    (procom -> cod_sll)
        ↓
DATA/accessibility_data.json         (349 KB, 1.920 comuni, 239 SLL)
```

Fa tre cose: unisce i file regionali mappando nome comune → `procom` a 6 cifre,
ricalcola `soglie` (p33/p67/mean) e `indicatori` (label/max/mean) sulla distribuzione dei
comuni coperti, aggrega gli SLL.

Soglie ricalcolate sui 1.920 comuni:

| indicatore | p33 | p67 | media | max |
|---|---|---|---|---|
| Ospedali SSN | 0,0 | 0,97 | 0,62 | 3,99 |
| Servizi sanitari | 3,0 | 12,9 | 12,36 | 159,61 |
| Strutture educative | 10,57 | 34,72 | 35,57 | 384,76 |
| Trasporti | 20,36 | 97,89 | 117,36 | 1.540,94 |
| Sport | 24,03 | 69,54 | 68,17 | 660,77 |
| Cultura | 12,2 | 29,61 | 27,78 | 234,92 |

Il file ora porta anche `regioni_non_coperte`, `copertura_comuni` e `sll_meta`, che prima
non c'erano.

### Blocco `sll`: limite noto, da tenere presente

I valori MCP sono medie per cella H3 r8, e le celle H3 hanno area costante: la media sulle
celle di un SLL equivale quindi alla **media dei valori comunali pesata per la superficie
del comune**. Il peso usato è l'area della geometria comunale riproiettata in EPSG:3035
(equal-area). Questa è la scelta matematicamente coerente con la semantica del dato, non
una convenzione arbitraria.

**Il limite**: sono disponibili i soli comuni SNAI, quindi il valore di un SLL descrive la
**porzione SNAI del sistema locale, non l'intero SLL**. Copertura: 239 SLL su 515, con
quota di superficie coperta mediana **0,609** (min 0,006, max 1,004; il valore sopra 1
viene dallo scarto fra geometrie semplificate e `sup_kmq` ISTAT).

Il limite è esplicitato in tre punti, per non lasciarlo implicito:

- nel campo `note` di `accessibility_data.json`;
- in `sll_meta`, per ogni SLL: `n_comuni_snai_usati`, `n_comuni_sll`,
  `quota_superficie_sll_coperta`;
- nel **pannello SLL della dashboard**, che ora scrive "Valore calcolato sui soli N comuni
  SNAI dell'SLL su M (X% della superficie), non sull'intero sistema locale"
  (funzione `sllAccNote` in `script/build_dashboard.py`).

Per avere valori SLL rappresentativi dell'intero sistema locale servirebbe una seconda
raccolta MCP estesa a **tutti** i comuni italiani. Ora è fattibile senza trascrizione
manuale grazie a `estrai_mcp.py`; stima ~700-900 mila token. **Non fatta**: è fuori dal
perimetro richiesto.

### Modifiche alla dashboard

- `accGrid(vals, extraNote)` accetta una nota aggiuntiva, usata dal pannello SLL.
- La nota di fonte nelle card di accessibilità ora cita MCP hex-intelligence, la
  risoluzione H3 r8 e l'isocrona 30 min con traffico, al posto della vecchia attribuzione
  "OvertureMaps + Min. Salute, IZI".

### Verifiche fatte

Tutti i controlli numerici sono stati eseguiti con script Python, non stimati:

- **1.920 righe riconfrontate una a una** con i file regionali di partenza: **0 discordanze**.
- `soglie` e `indicatori` **ricalcolati con numpy** (`np.percentile`, `mean`, `max`):
  tutti coincidenti con i valori scritti nel file.
- **10 aggregazioni SLL ricalcolate** in modo indipendente (5 primi + 5 ultimi codici):
  0 errori, incluso il conteggio `n_comuni_snai_usati`.
- 0 `cod_sll` orfani rispetto a `geo/sll-perimetri.geojson`.
- Struttura: tutti i `procom` presenti nell'indice SNAI, 6 indicatori per comune, tutti
  numerici e non negativi.
- Rilettura di `ACC_DATA` **dall'HTML generato**: 1.920 comuni, 239 SLL, 239 `sll_meta`.
- Spot-check di valori su comuni di regioni diverse (Alleghe, Longarone, Varallo, Bormio,
  Ala di Stura) coerenti con i file regionali.
- Unico gruppo senza dati: i 47 comuni della Valle d'Aosta.

### Correzione fatta in corsa

La prima versione di `sll_meta` calcolava `quota_superficie_snai_coperta` con al
denominatore la superficie **SNAI** dell'SLL: risultava 1,000 per tutti i 239 SLL, quindi
non informativa. Sostituita con `quota_superficie_sll_coperta`, che usa `sup_kmq` ISTAT
dal geojson SLL, e affiancata da `n_comuni_sll`.

---

## 2. Riorganizzazione delle cartelle

La root conteneva **27 file sciolti** (26 tracciati a `HEAD` più
`generate_accessibility_from_mcp.py`, non ancora tracciato) fra script, GeoJSON prodotti,
shapefile, note, PDF e deliverable. Obiettivo: **in root solo il deliverable web**.

### Struttura risultante

```
/
├── dashboard-aree-interne.html      il deliverable
├── index.html                       landing page (linka la dashboard con path relativo)
├── CLAUDE.md  .gitignore  .claude/
│
├── script/          pipeline + diagnostica/
├── geo/             i 3 GeoJSON prodotti
├── DATA/            dati sorgente (+ sll_2021/, mcp_accessibilita/, nazionali/)
├── DOCS/            documentazione SNAI (+ progetto/ per le NOTE*.md)
└── output/          elaborati per regione: Emilia-Romagna, Lombardia, Puglia
```

### Spostamenti

| da | a |
|---|---|
| `build_dashboard.py`, `generate_*.py` (5 file) | `script/` |
| `aree-snai-perimetri.geojson`, `comuni-snai-perimetri.geojson`, `sll-perimetri.geojson` | `geo/` |
| `SLL_2021.*` (7 file), JSON di composizione, `metadati_SLL_2021.xlsx`, PDF specializzazione | `DATA/sll_2021/` |
| `NOTE.md`, `NOTE_discordanza-accessibilita.md`, `NOTE_sessione-2026-09-05.md` | `DOCS/progetto/` |
| `presentazione ER/` | `output/Emilia-Romagna/` |
| `area-interna-alta-murgia.docx` | `output/Puglia/` |

Lo spostamento di `presentazione ER/` completa un'intenzione già annotata in `CLAUDE.md`
("non è ancora stata spostata sotto `output/`").

Tutto con **`git mv`**, quindi la storia dei file è preservata: git registra **234
rinomine**.

### Cosa è rimasto in root, e perché

- **`index.html`**: linka `dashboard-aree-interne.html` con path relativo. I due file sono
  lo stesso deliverable web e devono stare nella stessa cartella.
- **`CLAUDE.md`**: Claude Code lo legge solo dalla root.

### Due file cancellati

`rapporto-istruttoria_pa-bolzano.pdf` e `snai-dossier-pa-bolzano.pdf` erano **duplicati
byte-identici** (md5 confrontato) di file già archiviati in
`DOCS/Documentazione Regionale/Nord/` con la nomenclatura corretta
(`rapporto-istruttoria_pa-bolzano.pdf`, `snai-dossier_pa-bolzano.pdf`, con underscore).

Rimossi con `git rm`. Il contenuto resta in DOCS e nella storia git; per recuperarli:

```bash
git checkout HEAD -- rapporto-istruttoria_pa-bolzano.pdf snai-dossier-pa-bolzano.pdf
```

### Percorsi negli script: da hardcoded a relativi a `__file__`

Prima erano un misto di percorsi assoluti (`C:\Users\aalbe\Desktop\Code\Aree Interne
Italia\...`) e percorsi relativi che assumevano il cwd nella root. Ora ogni script
calcola la radice del repo da `__file__`:

```python
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = lambda *p: os.path.join(ROOT, *p)
```

Gli script si lanciano quindi **da qualsiasi directory di lavoro**. Aggiornati anche i 9
script in `script/diagnostica/` che avevano `REPO` hardcoded, e `valida_mcp.py` /
`estrai_mcp.py` che usavano percorsi relativi al cwd.

### Verifiche fatte

- Tutti gli script **compilano** (`python -m py_compile`).
- Le **19 costanti di percorso** dichiarate nei 5 script di pipeline sono state valutate
  con `ast` e risolvono tutte a **file esistenti**.
- Pipeline rieseguita **da una directory diversa dalla root** (`cd /`):
  `valida_mcp.py` → 1920/1967; `generate_accessibility_from_mcp.py` e
  `build_dashboard.py` producono output **byte-identici** a prima dello spostamento
  (md5 verificato su `dashboard-aree-interne.html` e `DATA/accessibility_data.json`).
- `build_index.py` rigenera `comuni_snai_index.json` identico (0 omonimi).

### Aggiunto `.gitignore`

Non esisteva. Contiene `__pycache__/` e `*.pyc`.

---

## 3. Documentazione aggiornata

- **`CLAUDE.md`**: nuova sezione "Struttura cartelle" con tabella; comandi di pipeline con
  il prefisso `script/`; flusso dati con i percorsi `geo/`; descrizione di
  `DATA/sll_2021/`, `DOCS/progetto/`, `output/Emilia-Romagna|Puglia`; sezione
  "Accessibilità ai servizi" con la copertura 97,6% e il limite del blocco `sll`.
- **`DOCS/progetto/NOTE.md`**: sezione "Struttura del progetto" riscritta con l'albero
  completo commentato; nuova sezione "Accessibilità ai servizi: cambio di fonte" con
  pipeline, copertura, limite SLL e riferimento al backup.
- **`DATA/mcp_accessibilita/_STATO.md`**: 19 regioni marcate completate, riga di totale
  aggiornata a 1.920 su 1.967 (97,6%).

---

## 4. Stato del repo

`HEAD` è **`1691b17`** ("Incorporazione del workspace `Aree_Interne_Lombardia` e
aggiornamenti vari"). **Niente di questa sessione è stato committato.**

`git status`: 234 rinomine, 8 modificati, 2 cancellati, 13 non tracciati.

File nuovi non ancora tracciati:

```
.gitignore
DATA/accessibility_data.LAZIO-parquet.bak.json   backup della versione solo-Lazio
DATA/mcp_accessibilita/                          19 file regionali + _STATO.md
script/generate_accessibility_from_mcp.py
script/diagnostica/estrai_mcp.py                 assembla dai tool-results MCP
script/diagnostica/valida_mcp.py                 validazione dei file regionali
script/diagnostica/comuni_snai_index.json        indice 1.967 comuni SNAI
script/diagnostica/{arbitro_istat,test_resolution,test_soglia,verifica_lazio_completo}.py
script/diagnostica/{mcp_lazio_ospedali.json,confronto_lazio_completo.csv}
```

`script/generate_accessibility_data.py` è la vecchia pipeline GeoParquet: **legacy**,
tenuta per riferimento, non va eseguita (sovrascriverebbe `accessibility_data.json` con i
soli 189 comuni del Lazio).

---

## 5. Cosa resta aperto

| Tema | Nota |
|---|---|
| **Valle d'Aosta** | 47 comuni SNAI senza accessibilità. Serve una fonte diversa da MCP `hex-intelligence`. |
| **Blocco `sll` rappresentativo** | Richiede una raccolta MCP su tutti i comuni italiani, non solo SNAI. Fattibile senza trascrizione manuale, stima ~700-900 mila token. |
| **Commit** | Nulla di questa sessione è committato. |
| **`DATA/nazionali/`** | I sei dataset comunali non sono ancora usati dagli script di build. Le due avvertenze sugli export IstatData (dimensione dichiarata errata, colonna territoriale con nomi e non codici) sono in `CLAUDE.md`. |
| **Perimetro regionale Lombardia** | Il dato "14 aree, 334 comuni aggiuntivi" (DGR 1705/2023) resta non verificato contro l'Allegato A in `DOCS/Documentazione Regionale/Nord/Lombardia/`. |
| **Radice di `DOCS/`** | Resta piatta con 20 file. È una serie numerata coerente (`01_`…`11_` più extra), non è stata toccata. |
