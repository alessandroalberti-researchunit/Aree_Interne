# -*- coding: utf-8 -*-
"""Genera Sceneggiatura-Convegno-RER.docx: sceneggiatura slide per slide."""
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

VIOLET = RGBColor(0x64, 0x22, 0xE8)
MUTED = RGBColor(0x57, 0x57, 0x67)
DARK = RGBColor(0x27, 0x27, 0x35)

doc = Document()

# base style
style = doc.styles["Normal"]
style.font.name = "Calibri"
style.font.size = Pt(11)
style.font.color.rgb = DARK

def add_title(text):
    p = doc.add_heading(level=0)
    r = p.add_run(text)
    r.font.color.rgb = VIOLET

def add_h1(text):
    p = doc.add_heading(level=1)
    r = p.add_run(text)
    r.font.color.rgb = VIOLET

def add_h2(text):
    p = doc.add_heading(level=2)
    r = p.add_run(text)
    r.font.color.rgb = DARK

def add_label(text):
    p = doc.add_paragraph()
    r = p.add_run(text.upper())
    r.bold = True
    r.font.size = Pt(9)
    r.font.color.rgb = MUTED
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    return p

def add_body(text, italic=False):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.italic = italic
    p.paragraph_format.space_after = Pt(8)
    return p

def add_bullets(items):
    for item in items:
        p = doc.add_paragraph(style="List Bullet")
        p.add_run(item)

def add_source(text):
    p = doc.add_paragraph()
    r = p.add_run("Fonte: " + text)
    r.italic = True
    r.font.size = Pt(9)
    r.font.color.rgb = MUTED
    p.paragraph_format.space_before = Pt(4)

def add_divider():
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("─" * 40)
    r.font.color.rgb = RGBColor(0xCE, 0xCD, 0xE0)
    r.font.size = Pt(8)


# ============================================================
# COPERTINA DOCUMENTO
# ============================================================
add_title("Sceneggiatura — Convegno RER")
add_body(
    "Assemblea Legislativa della Regione Emilia-Romagna · Sala Polivalente, viale Aldo Moro 52, Bologna · "
    "14 luglio 2026, ore 9,30–13,30"
)
add_body(
    "Intervento di Martino Bellincampi (IZILab), Seconda sessione — \"Il futuro dei luoghi: temi e "
    "approfondimenti\". Titolo assegnato in agenda: \"Orientare il futuro: ridurre i divari è una possibilità "
    "che prende forma attraverso le scelte di oggi\". Durata indicativa: 15 minuti, 17 slide."
)
add_body(
    "Questo documento affianca a ogni slide il contenuto a schermo e una proposta di testo per il relatore. "
    "Il testo suggerito è un punto di partenza da adattare al proprio stile e ai tempi reali concessi dal "
    "moderatore — non va letto parola per parola.",
    italic=True,
)

doc.add_page_break()

# ============================================================
# SLIDES
# ============================================================
slides = [
    dict(
        n=1, kicker="Copertina", title="Orientare il futuro",
        contenuto=[
            "Titolo: \"Orientare il futuro\"",
            "Sottotitolo: \"Ridurre i divari è una possibilità che prende forma attraverso le scelte di oggi\"",
            "Martino Bellincampi — IZILab",
        ],
        script=(
            "Buongiorno a tutti, e grazie per l'invito. Il titolo di questo intervento è già di per sé una "
            "tesi: orientare il futuro, ridurre i divari è una possibilità che prende forma attraverso le "
            "scelte di oggi. Sono Martino Bellincampi, di IZILab: lavoriamo di foresight, cioè studiamo come "
            "anticipare i cambiamenti invece di subirli, e lo facciamo applicandolo ai territori."
        ),
    ),
    dict(
        n=2, kicker="Perché il futuro non si può improvvisare", title="Il futuro non si può improvvisare",
        contenuto=[
            ">50% delle aziende, USA e UE, chiude o fallisce entro 10 anni",
            ">80% delle imprese sociali chiude entro 3 anni",
            ">40% dei nuovi prodotti/servizi non trova mercato",
        ],
        script=(
            "Parto da un dato scomodo: più della metà delle aziende, tra Stati Uniti e Unione Europea, chiude "
            "o fallisce entro dieci anni. Per le imprese sociali va anche peggio: oltre l'80% chiude entro tre "
            "anni. E quasi la metà dei nuovi prodotti lanciati sul mercato non trova un interesse reale. Questo "
            "non succede perché manchino le idee: succede perché manca la capacità di leggere in anticipo dove "
            "va il contesto in cui si opera."
        ),
        fonte="Simeone et al., 2023",
    ),
    dict(
        n=3, kicker="Fallire a guardare avanti", title="Kodak",
        contenuto=[
            "Fatturato al picco: 16 mld $ (1996); utili al picco: 2,5 mld $ (1999)",
            "Tra le prime a brevettare l'immagine digitale, ma non la sviluppa per non cannibalizzare l'analogico",
            "Bancarotta: 2012",
        ],
        script=(
            "Un esempio storico. Kodak, a metà degli anni '90, era all'apice: 16 miliardi di dollari di "
            "fatturato. Ed è stata tra le prime aziende al mondo a brevettare la tecnologia dell'immagine "
            "digitale. Ma ha scelto di non svilupparla, per non fare concorrenza a se stessa sui prodotti "
            "analogici che la facevano guadagnare in quel momento. Nel 2012 ha dichiarato bancarotta. Non per "
            "mancanza di visione tecnologica: per mancanza di foresight strategico."
        ),
        fonte="Corporate Foresight Benchmarking Report, 2018 — Aarhus University",
    ),
    dict(
        n=4, kicker="Guardare avanti per sopravvivere", title="Lego",
        contenuto=[
            "2003: l'azienda è a un passo dalla bancarotta",
            "Istituisce un Future Lab con bambini, progettisti di giocattoli, scrittori di fantascienza",
            "Risultato: prodotti di enorme successo",
        ],
        script=(
            "Lego, nel 2003, era nella stessa identica posizione di rischio. La differenza è cosa ha fatto "
            "dopo: ha creato un Future Lab interno, coinvolgendo non solo i propri designer ma bambini, "
            "progettisti di giocattoli esterni, persino scrittori di fantascienza. Da lì sono nate le idee che "
            "hanno rilanciato l'azienda. Stessa crisi di Kodak, esito opposto."
        ),
        fonte="Corporate Foresight Benchmarking Report, 2018 — Aarhus University",
    ),
    dict(
        n=5, kicker="Non è un'eccezione, è la norma", title="Il 90% lo fa già",
        contenuto=[
            "90% delle più grandi aziende europee e USA usa regolarmente il futures thinking",
            "1/3 di queste ha una funzione aziendale dedicata",
        ],
        script=(
            "Kodak e Lego non sono due aneddoti isolati. Il 90% delle più grandi aziende europee e "
            "statunitensi utilizza oggi, regolarmente, metodi di futures thinking. Un terzo di queste ha "
            "addirittura una funzione aziendale interna dedicata solo a questo. Non è più un'eccezione per "
            "pochi visionari: è prassi corrente per chi vuole restare competitivo."
        ),
        fonte="Nuremberg Institute of Market Decisions",
    ),
    dict(
        n=6, kicker="Cos'è il foresight", title="(citazione — Berkhout et al.)",
        contenuto=[
            "Citazione: \"La scienza e l'arte di descrivere, spiegare, esplorare, prevedere e/o interpretare "
            "gli sviluppi futuri, nonché di valutarne le conseguenze per le decisioni e le azioni nel "
            "presente.\"",
            "— Berkhout, Van der Duin, Hartmann & Ortt, 2007, p. 74",
        ],
        script=(
            "Ma cos'è, esattamente, il foresight? La definizione più citata in letteratura è questa: è la "
            "scienza e l'arte di descrivere, spiegare, esplorare, prevedere o interpretare gli sviluppi "
            "futuri, e di valutarne le conseguenze per le decisioni e le azioni nel presente. Il punto chiave "
            "è proprio questo: nel presente. Il foresight non serve a indovinare il futuro, serve a decidere "
            "meglio oggi."
        ),
    ),
    dict(
        n=7, kicker="", title="(citazione — Harvard Business Review Italia)",
        contenuto=[
            "Citazione: \"Prevedere il futuro è scientificamente impossibile. Guardare al futuro in modo "
            "razionale e scientifico non lo è.\"",
        ],
        script=(
            "E qui arrivo a un punto che vorrei fosse chiaro fin da subito, perché toglie di mezzo "
            "un'obiezione comune: prevedere il futuro è scientificamente impossibile. Ma guardare al futuro "
            "in modo razionale e scientifico non lo è. È una distinzione che sembra sottile ma cambia tutto: "
            "non stiamo parlando di indovini, stiamo parlando di un metodo."
        ),
        fonte="Harvard Business Review Italia",
    ),
    dict(
        n=8, kicker="Un esempio", title="Investire oggi contro un rischio che arriva tra decenni",
        contenuto=[
            "Programma Delta, Governo Olandese: 1,4 mld € fino al 2034",
            "Orizzonte del rischio: 50–100 anni",
            "Innalzamento del mare stimato: 1–5 metri",
        ],
        script=(
            "Un esempio concreto di metodo applicato alle politiche pubbliche: il Programma Delta del governo "
            "olandese. Investono 1,4 miliardi di euro, fino al 2034, in opere e manutenzione per un rischio "
            "che si materializzerà tra 50 e 100 anni: un innalzamento del livello del mare stimato tra 1 e 5 "
            "metri. Non aspettano che il rischio sia certo e vicino: agiscono adesso, proprio perché la "
            "finestra per prepararsi è lunga ma non infinita."
        ),
        fonte="Programma Delta, Governo Olandese",
    ),
    dict(
        n=9, kicker="La nostra metodologia", title="Un solo tipo di dato non basta",
        contenuto=[
            "Critica al foresight tradizionale: rischia di restare astratto, senza indicazioni per l'azione",
            "Thick Data — storie, interviste, motivazioni, comportamenti",
            "Big Data — dati digitali su larga scala, sensori, tracce online",
            "Forward-Looking Data — trend, scenari, backcasting",
            "Participatory Data — workshop, co-progettazione, hackathon",
        ],
        script=(
            "Qui arrivo al cuore del nostro metodo, quello che abbiamo sviluppato come IZILab e descritto nel "
            "nostro libro, Futures Thinking. Il foresight tradizionale è stato criticato per un motivo "
            "preciso: rischia di restare astratto, di non tradursi in indicazioni operative. La nostra "
            "risposta è integrare quattro tipi di dato, non uno solo: i Thick Data, cioè le storie e le "
            "motivazioni delle persone; i Big Data, su larga scala; i Forward-Looking Data, cioè gli output "
            "dei metodi di foresight classici come scenari e trend; e i Participatory Data, quelli che nascono "
            "dal coinvolgimento diretto delle persone in workshop e percorsi condivisi. Non sono alternativi "
            "tra loro: vanno mixati a seconda del problema, come ingredienti di una ricetta."
        ),
        fonte="Bellincampi et al., Futures Thinking — Cap. 1 e 4",
    ),
    dict(
        n=10, kicker="Lo abbiamo già fatto", title="Un piccolo comune dell'Appennino, una visione a 30 anni",
        contenuto=[
            "Nuova sindaca eletta con un patto: costruire una visione di lungo periodo, non gestire l'ordinario",
            "Horizon scanning e framework PESTEL",
            "Metodo Delphi e assemblee pubbliche",
            "Futures workshop con cittadini ed esperti",
            "Esito: lavoro remoto in montagna, coworking, turismo di rigenerazione; risonanza nazionale",
        ],
        script=(
            "Questo non è un esercizio teorico: lo abbiamo già applicato. Un piccolo comune dell'Appennino "
            "tosco-emiliano ha eletto una nuova sindaca con un patto preciso: non passare cinque anni a "
            "tappare buche, ma costruire una visione a trent'anni per la propria comunità di montagna. Con il "
            "nostro supporto ha usato horizon scanning e framework PESTEL, il metodo Delphi con assemblee "
            "pubbliche, e futures workshop che hanno coinvolto cittadini ed esperti insieme. Il risultato: "
            "politiche su lavoro remoto in montagna, coworking ad alta connettività, turismo di rigenerazione. "
            "È stata una delle prime esperienze italiane di questo tipo, con una risonanza che è andata oltre "
            "i confini del comune stesso."
        ),
        fonte="Bellincampi et al., Futures Thinking — Cap. 7.2",
    ),
    dict(
        n=11, kicker="Da un comune a centinaia di territori", title="Chorema non è una dashboard, è un research environment",
        contenuto=[
            "Si distingue da GIS tradizionali (Esri, QGIS), location intelligence (CARTO), consulenza (Deloitte, McKinsey)",
            "Combina foresight di lungo periodo e intelligenza agentica su indici territoriali validati",
            "Callout: gli stessi 4 tipi di dato, ora integrati e aggiornati in continuo",
        ],
        script=(
            "La domanda naturale è: come si fa a ripetere questo lavoro non su un comune alla volta, con un "
            "team dedicato per nove mesi, ma su centinaia di territori insieme? La risposta è Chorema, la "
            "piattaforma che abbiamo sviluppato come IZILab. Chorema non è una dashboard: è un ambiente di "
            "ricerca. Si differenzia dai GIS tradizionali come Esri o QGIS, dagli strumenti di location "
            "intelligence come CARTO, e dalla consulenza di foresight classica, perché combina l'orizzonte di "
            "lungo periodo con l'intelligenza agentica, applicata a indici territoriali validati "
            "scientificamente. In sostanza: sono gli stessi quattro tipi di dato di cui parlavo prima, ma ora "
            "integrati e aggiornati in modo continuo, non più una volta ogni nove mesi."
        ),
    ),
    dict(
        n=12, kicker="Come funziona", title="Indici validati + intelligenza agentica",
        contenuto=[
            "Data Lake — 80.000+ indicatori geospaziali, 500+ report",
            "Indici validati — con Politecnico di Milano, Aalborg University, LUM",
            "Architettura multi-agente — coordinatore, agenti esperti, agente critico anti-hallucination",
        ],
        script=(
            "In pratica, Chorema si regge su tre pilastri. Il primo è un Data Lake che raccoglie oltre "
            "ottantamila indicatori geospaziali e cinquecento report, da fonti istituzionali e scientifiche. "
            "Il secondo sono gli indici validati, sviluppati insieme a partner accademici come il Politecnico "
            "di Milano, l'Università di Aalborg e la LUM. Il terzo è un'architettura multi-agente: un agente "
            "coordinatore, agenti esperti su singoli domini, e un agente critico che ha il compito specifico "
            "di segnalare vuoti informativi e possibili errori, prima che arrivino all'utente."
        ),
    ),
    dict(
        n=13, kicker="Perché non basta un chatbot generico", title="Stessa domanda, risposte diverse",
        contenuto=[
            "Domanda test: \"In quali provincie la domanda di competenze crescerà di più, e quali corridoi "
            "migratori saranno più praticabili?\"",
            "Generalisti (ChatGPT/Gemini/Claude): nessun dato granulare, fonti generiche, nessuna indicazione operativa",
            "ForeSkill su Chorema: dati granulari per provincia, 18 fonti curate e tracciabili, indicazioni azionabili",
        ],
        script=(
            "Perché non basta chiedere la stessa cosa a un chatbot generico? Abbiamo fatto la prova con una "
            "domanda reale: in quali provincie la domanda di competenze crescerà di più, e quali corridoi "
            "migratori saranno più praticabili nei prossimi anni. I generalisti, ChatGPT, Gemini, Claude, danno "
            "risposte senza dati realmente granulari, con fonti generiche o non verificabili, e senza alcuna "
            "indicazione operativa concreta. ForeSkill, il verticale di Chorema per il mercato del lavoro, dà "
            "invece dati granulari per provincia e per orizzonte temporale, con diciotto fonti curate e "
            "tracciabili, e indicazioni pienamente azionabili. La differenza non è nel modello linguistico: è "
            "nell'infrastruttura di conoscenza che c'è sotto."
        ),
    ),
    dict(
        n=14, kicker="Caso studio", title="Berceto, Appennino Parma Est",
        contenuto=[
            "Area SNAI Appennino Parma Est, finanziata ciclo 2021-2027",
            "Classificazione ISTAT E, Periferico, 44,7 minuti dal polo urbano",
            "Popolazione: -25,7% in 30 anni (1991-2021)",
            "Struttura demografica: over 65 oltre 4 volte gli under 15",
            "Callout: zero ospedali raggiungibili in 30 minuti; dominio più accessibile: la ristorazione",
        ],
        script=(
            "Vengo ora a un caso concreto, dentro questa stessa regione. Berceto, in provincia di Parma, fa "
            "parte dell'area SNAI Appennino Parma Est, finanziata nel ciclo 2021-2027. È classificato dall'ISTAT "
            "come comune periferico, a 44 minuti e 7 dal polo urbano di riferimento. La popolazione è calata "
            "del 25,7% in trent'anni, e la quota di over 65 supera di oltre quattro volte quella degli under "
            "15. Ma il dato che voglio sottolineare è un altro, ed è quello che un indice come quelli di "
            "Chorema riesce a far emergere meglio di una semplice descrizione: zero ospedali raggiungibili in "
            "trenta minuti. Il dominio più accessibile in assoluto, invece, è la ristorazione. È il paradosso "
            "di un territorio che accoglie turisti ma fatica a trattenere residenti."
        ),
        fonte="Chorema — Aree Interne Intelligence, Urban Intelligence (Hex)",
    ),
    dict(
        n=15, kicker="Scenari", title="Due traiettorie, a partire da oggi",
        contenuto=[
            "Scenario 1 — Inerzia strutturale: il trend attuale continua, popolazione sotto soglia critica entro il 2030",
            "Scenario 2 — Rigenerazione connessa: telemedicina, mobilità a chiamata, residenzialità digitale invertono parzialmente il declino",
        ],
        script=(
            "Da qui, due traiettorie possibili, a partire da oggi. Nello scenario di inerzia strutturale, il "
            "trend attuale continua: connettività e telemedicina non arrivano in tempo, e la popolazione scende "
            "sotto la soglia critica già entro il 2030. Nello scenario di rigenerazione connessa, invece, le "
            "leve già previste nel ciclo SNAI in corso, telemedicina, mobilità a chiamata, residenzialità "
            "digitale, vengono attivate in tempo e invertono almeno parzialmente la traiettoria di declino. La "
            "differenza tra i due scenari non è il caso: sono le scelte fatte nei prossimi mesi."
        ),
    ),
    dict(
        n=16, kicker="Raccomandazioni strategiche", title="Le scelte che possono cambiare la traiettoria",
        contenuto=[
            "01 — Telemedicina intercomunale — AUSL Parma / Unione dei Comuni — presidio h24 entro il 2026",
            "02 — Mobilità a chiamata sovracomunale — Agenzia TPL Emilia-Romagna — operativa entro il 2027",
            "03 — Residenzialità digitale — Comune di Berceto / GAL Appennino Parmense — incentivi e coworking",
        ],
        script=(
            "Concretamente, tre scelte che possono spostare l'ago della bilancia. Primo: un presidio di "
            "telemedicina intercomunale, in capo ad AUSL Parma e all'Unione dei Comuni, attivo entro il 2026. "
            "Secondo: un servizio di mobilità a chiamata sovracomunale, con l'Agenzia TPL Emilia-Romagna, "
            "operativo entro il 2027. Terzo: incentivi per la residenzialità digitale, tra il Comune di Berceto "
            "e il GAL Appennino Parmense, per trasformare le strutture ricettive esistenti in spazi per "
            "lavoratori remoti. Sono scelte puntuali, con un destinatario chiaro ciascuna, non un piano "
            "generico."
        ),
    ),
    dict(
        n=17, kicker="In chiusura", title="Le scelte di oggi",
        contenuto=[
            "Il ciclo SNAI 2021-2027 è aperto",
            "Le tecnologie per leggere e anticipare i divari territoriali esistono già",
            "Chiusura: non è un nuovo dato che serve, è la scelta di usarlo, ora",
        ],
        script=(
            "Chiudo tornando al titolo di questo intervento. Il ciclo SNAI 2021-2027 è aperto. Le tecnologie "
            "per leggere e anticipare i divari territoriali esistono già, le abbiamo viste applicate sia a un "
            "singolo comune sia, con Chorema, a scala di centinaia di territori. Quello che ridurrà davvero le "
            "disuguaglianze tra i luoghi non è un nuovo dato: è la scelta di usarlo, ora. Grazie."
        ),
    ),
]

for s in slides:
    heading = f"Slide {s['n']:02d} / 17"
    if s.get("kicker"):
        heading += f" — {s['kicker']}"
    add_h1(heading)
    add_h2(s["title"])
    add_label("Contenuto in slide")
    add_bullets(s["contenuto"])
    add_label("Sceneggiatura (proposta di testo)")
    add_body(s["script"])
    if s.get("fonte"):
        add_source(s["fonte"])
    add_divider()

doc.save("Sceneggiatura-Convegno-RER.docx")
print("saved")
