# Presentazione — Convegno Assemblea Legislativa RER, 14 luglio 2026

## Contesto
Slot di Martino Bellincampi (IZILab) nella Seconda sessione del convegno "Un futuro per tutti i luoghi" (Bologna, Sala Polivalente Ass. Leg., 9,30-13,30). Titolo fissato in agenda: **"Orientare il futuro: ridurre i divari è una possibilità che prende forma attraverso le scelte di oggi"**. Condivide il panel con Rosina (demografia), Zonta/DG Regio (UE, right to stay), Filippetti/CNR (coesione e PNRR). Pubblico istituzionale, non un pitch commerciale. Durata stimata ~15 min.

## Materiali di partenza (in questa cartella)
- `IZILab - Intro Foresight (1).pptx` — vecchio deck IZILab sul foresight (50 slide), usato come fonte di contenuti, non come base grafica
- `Chorema_Product_Deck v11.pdf` — deck prodotto Chorema (30 pagine), fonte per posizionamento, architettura, casi d'uso
- `Testo Libro Futures Thinking (Draft).pdf` — libro di Bellincampi/IZILab (156 pagine). Contiene il framework originale **a 4 tipi di dato** (Thick / Big / Forward-Looking / Participatory Data, Cap. 1 e 4) e un caso reale IZILab (Cap. 7.2) su un piccolo comune dell'Appennino tosco-emiliano
- `AGENDA CONVEGNO AL RER...docx` — programma ufficiale del convegno
- Due studi Chorema su Berceto (incollati in chat, non salvati come file separati) — dati su area SNAI, accessibilità (Hex Intelligence), scenari Three Horizons, raccomandazioni
- `Immagine 2026-07-07 132222.png` — griglia 4 mappe H3 Berceto (popolazione, trasporti, sanità, istruzione)
- `Immagine 2026-07-07 132353.png` — screenshot piattaforma Chorema, radar accessibilità + demografia Berceto

## Decisioni chiave prese in conversazione
- **Non essere nozionistici sul foresight**: niente Berkhout/VUCA/Dator da manuale. Usare invece il framework originale del libro (i 4 tipi di dato) e il caso reale del piccolo comune d'Appennino, perché è materiale autoriale di Bellincampi
- **Scenari e raccomandazioni strategiche devono essere centrali** nel caso studio Berceto (per dimostrare la potenzialità predittiva/prescrittiva della piattaforma Chorema, non solo la diagnosi)
- Caso Berceto: dati incrociati dei due studi Chorema, tenendo solo i punti convergenti (es. indice accessibilità ospedali = 0,000 identico in entrambi; paradosso ristorazione più accessibile di tutto il resto)
- Popolazione Berceto: calcolo esplicito fatto via script Python, -25,7% tra 1991 (2.586 ab.) e 2021 (1.922 ab.), non stimato a memoria

## Scaletta finale (12 slide)
1. Copertina
2. Aggancio — statistiche fallimento pianificazione lineare (Simeone et al. 2023)
3. Un esempio — Programma Delta (Governo Olandese)
4. La nostra metodologia — i 4 tipi di dato (radar Thick/Big/Forward-Looking/Participatory)
5. Lo abbiamo già fatto — caso reale libro, piccolo comune d'Appennino, visione a 30 anni
6. Chorema: cos'è (non una dashboard, un research environment)
7. Chorema: come funziona (Data Lake, indici validati, architettura multi-agente)
8. Perché non basta un chatbot generico (confronto ForeSkill vs generalisti)
9. Caso studio Berceto — chi è + il paradosso (zero ospedali, ristorazione più accessibile)
10. Scenari al 2030 — Inerzia strutturale vs Rigenerazione connessa
11. Raccomandazioni strategiche (telemedicina intercomunale, mobilità a chiamata, residenzialità digitale)
12. Chiusura — "Le scelte di oggi"

## File prodotti
- `build_assets.py` — genera `assets/radar_4dati.png` (radar chart 4 tipi di dato, matplotlib, tema scuro/teal)
- `build_deck.py` — genera l'intero deck con python-pptx (helper per card, bullet, kicker, ecc.)
- `assets/` — logo IZILab ritagliato (estratto dal vecchio pptx), radar generato, copie degli screenshot Berceto
- **`dashboard-convegno-RER.pptx`** — deliverable finale, 12 slide, 16:9, tema scuro navy (#0A0E17) + teal (#2FE3C4), coerente con lo stile del Chorema Product Deck
- `dashboard-convegno-RER.pdf` — export di anteprima (via LibreOffice)

## Note tecniche utili per riprendere il lavoro
- Per rigenerare il deck dopo modifiche al testo: editare `build_deck.py` e rilanciare `python build_deck.py` dalla cartella
- Per rigenerare il radar: `python build_assets.py`
- Per verificare visivamente senza aprire PowerPoint: LibreOffice è installato (`C:\Program Files\LibreOffice\program\soffice.exe`), conversione con `--headless --convert-to pdf`, poi rendering PNG pagina per pagina con `pymupdf` (pip: `pymupdf`), poiché `pdftoppm`/poppler non è disponibile su questa macchina
- Font usato: Arial. Palette: sfondo `#0A0E17`, pannelli `#121824`, teal `#2FE3C4`, testo secondario `#A9B2C0`

## Possibili prossimi passi
- Giro di revisione contenuti/testi con Bellincampi
- Eventuale aggiunta di note del relatore per slide
- Timing reale del talk (non ancora confermato dagli organizzatori) potrebbe richiedere di tagliare la slide 8 (confronto chatbot)

## Fase 2 — Migrazione a Claude Design (2026-07-07/08)

Cambio di rotta: la versione python-pptx (sopra) resta come deliverable di riserva, ma la presentazione definitiva viene ricostruita sul vero design system IZILab e importata in un progetto Claude Design, perché:
- L'utente ha fornito il design system reale in `izilab-design-system-full/` (font Cirka/Instrument Sans/Chivo Mono, palette Violet `#6422E8`/Aqua `#49E1C0`/Blanche, backgrounds aurora, icone geometriche astratte, componenti React, un template `.dc.html` già pronto per deck di foresight, e un deck Chorema investor completo da cui riprendere pattern)
- Contenuti aggiuntivi da integrare in apertura, tratti da `IZILab - Intro Foresight (3).pptx`: Kodak, Lego, statistica "90% delle grandi aziende usa il futures thinking", definizione di Berkhout, citazione HBR Italia ("prevedere è impossibile, guardare in modo razionale no")

**Scaletta aggiornata: 17 slide** (le 12 originali + 5 nuove in apertura, aggancio più ricco):
1. Copertina — 2. Statistiche fallimento pianificazione — 3. Kodak — 4. Lego — 5. Statistica 90% — 6. Definizione Berkhout (quote) — 7. Quote HBR — 8. Programma Delta — 9. I 4 tipi di dato — 10. Caso reale libro (comune Appennino) — 11. Chorema cos'è — 12. Chorema come funziona — 13. Perché non basta un chatbot — 14. Berceto chi è + paradosso — 15. Scenari 2030 — 16. Raccomandazioni — 17. Chiusura

**Cosa è stato fatto:**
- Costruito `izilab-design-system-full/decks/convegno-rer/ConvegnoRER.dc.html`: le 17 slide nel formato nativo `.dc.html` (runtime `dc-runtime`/React), seguendo esattamente i pattern di `templates/foresight-deck/ForesightDeck.dc.html` (stage 1280×720, sezioni assolute con toggle opacity/visibility, navigazione prev/next da tastiera)
- Riusati asset del design system: icone astratte (`icon-seed`, `icon-concentric`, `icon-lens-arrow`, `icon-overlap-circle` per i 4 tipi di dato; `icon-stack-diamond`, `icon-diamond-square`, `icon-sunburst` per Chorema), sfondi aurora (`bg-dark-bloom`, `bg-light-violet`, `bg-dark-aurora`, `bg-dark-wisp`), logo IZILab
- Copiati in `decks/convegno-rer/assets/` i due screenshot Berceto (`berceto-hexmaps.png`, `berceto-radar-ui.png`) usati alle slide 14-15
- Creato un nuovo progetto Claude Design tramite `DesignSync` (nome **"IZILab Design System"**, projectId `55582351-98d8-4ac3-a1e7-75c34d1740e6`, type `PROJECT_TYPE_DESIGN_SYSTEM`) e caricato l'intero contenuto di `izilab-design-system-full/` (184 file: tokens, guidelines, componenti, asset, i due deck esistenti e il nuovo `ConvegnoRER.dc.html`), in batch da 8-12 file per restare sotto il limite di dimensione della richiesta

**Note tecniche:**
- `write_files` di DesignSync fallisce con "Request body larger than maxBodyLength" se il payload è troppo grande: bisogna splittare in chunk piccoli e isolare i file singoli grandi (PDF, pptx, HTML standalone con asset inline) in chiamate a sé
- Il file `Chorema Investor Deck (standalone).html` è enorme (6+ MB, asset inline in base64): evitarlo come riferimento salvo necessità specifiche
- Non è stato possibile fare una verifica visiva del `.dc.html` (dipende dal runtime React caricato dinamicamente e da CDN esterni, bloccati dalla CSP degli strumenti di preview disponibili): la correttezza è stata verificata strutturalmente (conteggio sezioni/ref, bilanciamento tag, path degli asset) rispecchiando fedelmente il template funzionante fornito

**Prossimi passi:**
- Aprire il progetto "IZILab Design System" su claude.ai/design e verificare visivamente il deck `convegno-rer/ConvegnoRER.dc.html`
- Segnalare eventuali aggiustamenti di layout/testo da lì, oppure tornare qui per rigenerare il file e ripubblicarlo
