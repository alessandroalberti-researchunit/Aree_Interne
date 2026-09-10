# -*- coding: utf-8 -*-
"""Costruisce dashboard-aree-interne... no: costruisce il deck per il convegno RER."""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
import copy

# ---------- palette ----------
BG = RGBColor(0x0A, 0x0E, 0x17)
PANEL = RGBColor(0x12, 0x18, 0x24)
TEAL = RGBColor(0x2F, 0xE3, 0xC4)
TEAL_DARK = RGBColor(0x1A, 0xA8, 0x93)
WHITE = RGBColor(0xF2, 0xF5, 0xF8)
GRAY = RGBColor(0xA9, 0xB2, 0xC0)
MUTED = RGBColor(0x6B, 0x76, 0x88)
LINE = RGBColor(0x2A, 0x31, 0x40)

FONT = "Arial"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]

SW = prs.slide_width
SH = prs.slide_height


def add_slide():
    slide = prs.slides.add_slide(BLANK)
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SW, SH)
    bg.fill.solid()
    bg.fill.fore_color.rgb = BG
    bg.line.fill.background()
    bg.shadow.inherit = False
    # send to back is default since added first
    return slide


def set_no_line(shape):
    shape.line.fill.background()


def add_rect(slide, left, top, width, height, color=PANEL, line_color=None, radius=None):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    sh = slide.shapes.add_shape(shape_type, left, top, width, height)
    sh.fill.solid()
    sh.fill.fore_color.rgb = color
    if line_color:
        sh.line.color.rgb = line_color
        sh.line.width = Pt(0.75)
    else:
        sh.line.fill.background()
    sh.shadow.inherit = False
    if radius:
        try:
            sh.adjustments[0] = radius
        except Exception:
            pass
    return sh


def add_text(slide, text, left, top, width, height, size=18, color=WHITE, bold=False,
             align=PP_ALIGN.LEFT, italic=False, font=FONT, anchor=MSO_ANCHOR.TOP,
             line_spacing=1.0, wrap=True):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = anchor
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    lines = text.split("\n")
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing
        r = p.add_run()
        r.text = line
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.italic = italic
        r.font.name = font
        r.font.color.rgb = color
    return tb


def add_multirun_para(tf, runs, align=PP_ALIGN.LEFT, first=False, line_spacing=1.0, space_after=0):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.line_spacing = line_spacing
    p.space_after = Pt(space_after)
    for text, size, color, bold, italic in runs:
        r = p.add_run()
        r.text = text
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.italic = italic
        r.font.name = FONT
        r.font.color.rgb = color
    return p


def add_kicker(slide, text, left, top):
    return add_text(slide, text.upper(), left, top, Inches(9), Inches(0.4),
                     size=13, color=TEAL, bold=True)


def add_title(slide, text, left, top, width, size=32):
    return add_text(slide, text, left, top, width, Inches(1.4), size=size, color=WHITE, bold=True,
                     line_spacing=1.05)


def add_logo(slide, left=SW - Inches(1.75), top=Inches(0.45), width=Inches(1.0)):
    height = width * (830 / 2500)
    slide.shapes.add_picture("assets/izilab_logo_white_cropped.png", left, top, width=width, height=height)


def add_page_number(slide, n):
    add_text(slide, f"{n:02d}", SW - Inches(0.9), SH - Inches(0.55), Inches(0.6), Inches(0.35),
              size=11, color=MUTED, align=PP_ALIGN.RIGHT)


def add_source(slide, text, top=None):
    if top is None:
        top = SH - Inches(0.55)
    add_text(slide, text, Inches(0.55), top, Inches(9), Inches(0.35), size=10.5, color=MUTED, italic=True)


def bullet_list(slide, items, left, top, width, height, size=15, color=GRAY, gap=10, bold_lead=False):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap)
        p.line_spacing = 1.12
        r1 = p.add_run()
        r1.text = "▸  "
        r1.font.size = Pt(size)
        r1.font.color.rgb = TEAL
        r1.font.bold = True
        r1.font.name = FONT
        if isinstance(item, tuple):
            lead, rest = item
            r2 = p.add_run()
            r2.text = lead
            r2.font.size = Pt(size)
            r2.font.color.rgb = WHITE
            r2.font.bold = True
            r2.font.name = FONT
            r3 = p.add_run()
            r3.text = rest
            r3.font.size = Pt(size)
            r3.font.color.rgb = color
            r3.font.name = FONT
        else:
            r2 = p.add_run()
            r2.text = item
            r2.font.size = Pt(size)
            r2.font.color.rgb = color
            r2.font.name = FONT
    return tb


def stat_card(slide, left, top, width, height, big, label):
    card = add_rect(slide, left, top, width, height, color=PANEL, radius=0.08)
    add_text(slide, big, left + Inches(0.25), top + Inches(0.18), width - Inches(0.5), Inches(0.9),
              size=40, color=TEAL, bold=True)
    add_text(slide, label, left + Inches(0.25), top + Inches(1.05), width - Inches(0.5), height - Inches(1.2),
              size=14, color=GRAY, line_spacing=1.1)


def scenario_card(slide, left, top, width, height, title, body, accent=TEAL):
    card = add_rect(slide, left, top, width, height, color=PANEL, radius=0.06)
    bar = add_rect(slide, left, top, Inches(0.09), height, color=accent)
    add_text(slide, title, left + Inches(0.35), top + Inches(0.28), width - Inches(0.6), Inches(0.6),
              size=19, color=WHITE, bold=True)
    add_text(slide, body, left + Inches(0.35), top + Inches(0.95), width - Inches(0.6), height - Inches(1.15),
              size=13.5, color=GRAY, line_spacing=1.2)


def reco_card(slide, left, top, width, height, num, title, dest, body):
    add_rect(slide, left, top, width, height, color=PANEL, radius=0.06)
    add_text(slide, num, left + Inches(0.28), top + Inches(0.22), Inches(0.7), Inches(0.6),
              size=26, color=TEAL, bold=True)
    add_text(slide, title, left + Inches(0.28), top + Inches(0.85), width - Inches(0.56), Inches(0.8),
              size=16.5, color=WHITE, bold=True, line_spacing=1.05)
    add_text(slide, "DESTINATARIO", left + Inches(0.28), top + Inches(1.55), width - Inches(0.56), Inches(0.3),
              size=10, color=TEAL, bold=True)
    add_text(slide, dest, left + Inches(0.28), top + Inches(1.82), width - Inches(0.56), Inches(0.55),
              size=12, color=GRAY, line_spacing=1.05)
    add_text(slide, body, left + Inches(0.28), top + Inches(2.35), width - Inches(0.56), height - Inches(2.55),
              size=12, color=GRAY, line_spacing=1.15)


PAGE = 0
def next_page():
    global PAGE
    PAGE += 1
    return PAGE

# ============================================================
# SLIDE 1 — COPERTINA
# ============================================================
s = add_slide()
add_logo(s, left=Inches(0.7), top=Inches(0.6), width=Inches(1.5))
add_text(s, "ASSEMBLEA LEGISLATIVA DELLA REGIONE EMILIA-ROMAGNA  ·  14 LUGLIO 2026",
          Inches(0.7), Inches(2.5), Inches(11.5), Inches(0.4), size=13, color=TEAL, bold=True)
add_text(s, "Orientare il futuro:\nridurre i divari è una possibilità\nche prende forma attraverso le scelte di oggi",
          Inches(0.7), Inches(3.0), Inches(11.5), Inches(2.6), size=38, color=WHITE, bold=True, line_spacing=1.12)
add_rect(s, Inches(0.72), Inches(6.05), Inches(0.55), Inches(0.045), color=TEAL)
add_text(s, "Martino Bellincampi  —  IZILab", Inches(0.7), Inches(6.2), Inches(8), Inches(0.5),
          size=16, color=GRAY, bold=False)

# ============================================================
# SLIDE 2 — Aggancio statistiche
# ============================================================
s = add_slide(); add_logo(s)
add_kicker(s, "Perché il futuro non si può improvvisare", Inches(0.7), Inches(0.55))
add_title(s, "Il futuro non si può improvvisare", Inches(0.7), Inches(1.05), Inches(11.8))
cardw = Inches(3.6); gap = Inches(0.35); startx = Inches(0.7); cy = Inches(2.75); ch = Inches(2.7)
stats = [
    ("> 50%", "delle aziende, negli Stati Uniti e nell'Unione Europea,\nchiude o fallisce entro 10 anni"),
    ("> 80%", "delle imprese sociali\nchiude entro 3 anni"),
    ("> 40%", "dei nuovi prodotti o servizi lanciati sul mercato\nnon suscita un interesse significativo"),
]
for i, (big, label) in enumerate(stats):
    stat_card(s, startx + i * (cardw + gap), cy, cardw, ch, big, label)
add_source(s, "Fonte: Simeone et al., 2023")

# ============================================================
# SLIDE 3 — Programma Delta
# ============================================================
s = add_slide(); add_logo(s)
add_kicker(s, "Un esempio", Inches(0.7), Inches(0.55))
add_title(s, "Investire oggi contro un rischio\nche arriva tra decenni", Inches(0.7), Inches(1.05), Inches(11.8), size=30)
add_text(s, "Il Programma Delta del governo olandese destina 1,4 miliardi di euro, fino al 2034, "
             "a opere e manutenzione per mantenere il Paese sicuro, vivibile e prospero.\n\n"
             "Il livello del mare nei Paesi Bassi potrebbe superare quello attuale, tra 50 e 100 anni, "
             "di una misura stimata fra 1 e 5 metri.",
          Inches(0.7), Inches(2.9), Inches(7.0), Inches(2.6), size=17, color=GRAY, line_spacing=1.3)
add_rect(s, Inches(8.15), Inches(2.9), Inches(0.06), Inches(2.9), color=TEAL)
add_text(s, "Non prevedere il futuro.\nPrepararsi ad affrontarlo.", Inches(8.5), Inches(3.15), Inches(4.1), Inches(2.4),
          size=24, color=TEAL, bold=True, line_spacing=1.2)
add_source(s, "Fonte: Programma Delta, Governo Olandese")

# ============================================================
# SLIDE 4 — 4 tipi di dato
# ============================================================
s = add_slide(); add_logo(s)
add_kicker(s, "La nostra metodologia", Inches(0.7), Inches(0.55))
add_title(s, "Un solo tipo di dato non basta", Inches(0.7), Inches(1.05), Inches(11.8), size=30)
add_text(s, "I metodi di foresight tradizionali rischiano di restare astratti, senza indicazioni chiare "
             "per l'azione. La nostra risposta: integrare quattro tipologie di dato.",
          Inches(0.7), Inches(1.95), Inches(5.7), Inches(1.3), size=15, color=GRAY, line_spacing=1.25)
items4 = [
    ("Thick Data — ", "storie, interviste, motivazioni, comportamenti"),
    ("Big Data — ", "dati digitali su larga scala, sensori, tracce online"),
    ("Forward-Looking Data — ", "trend, scenari, backcasting"),
    ("Participatory Data — ", "workshop, co-progettazione, hackathon"),
]
bullet_list(s, items4, Inches(0.7), Inches(3.35), Inches(5.7), Inches(3.4), size=14.5, gap=16)
s.shapes.add_picture("assets/radar_4dati.png", Inches(6.75), Inches(1.55), height=Inches(5.6))
add_source(s, "Bellincampi et al., Futures Thinking — Cap. 1 e 4")

# ============================================================
# SLIDE 5 — Caso reale Appennino
# ============================================================
s = add_slide(); add_logo(s)
add_kicker(s, "Lo abbiamo già fatto", Inches(0.7), Inches(0.55))
add_title(s, "Un piccolo comune dell'Appennino,\nuna visione a 30 anni", Inches(0.7), Inches(1.05), Inches(11.8), size=28)
add_text(s, "Una nuova sindaca, eletta con un patto chiaro: non gestire l'ordinario, "
             "ma costruire una visione di lungo periodo per la propria comunità di montagna.",
          Inches(0.7), Inches(2.55), Inches(6.7), Inches(1.1), size=14.5, color=GRAY, line_spacing=1.25)
methods = [
    "Horizon scanning e framework PESTEL",
    "Metodo Delphi e assemblee pubbliche",
    "Futures workshop con cittadini ed esperti",
]
bullet_list(s, methods, Inches(0.7), Inches(3.75), Inches(6.7), Inches(1.6), size=14, gap=10)
add_text(s, "Esito: politiche su lavoro remoto in montagna, coworking ad alta connettività, "
             "turismo di rigenerazione. Prima esperienza italiana di questo tipo, con risonanza nazionale.",
          Inches(0.7), Inches(5.55), Inches(6.7), Inches(1.3), size=14.5,
          color=TEAL, bold=True, line_spacing=1.25)

# tabella 4 dati -> caso
tbl_left = Inches(7.85); tbl_top = Inches(2.55); tbl_w = Inches(4.75)
rows = [
    ("Thick Data", "Sondaggi ai cittadini"),
    ("Big Data", "Social media su vissuto turisti e residenti"),
    ("Forward-Looking", "Insight degli esperti di foresight"),
    ("Participatory", "Workshop per scenari e policy condivise"),
]
rh = Inches(1.02)
for i, (k, v) in enumerate(rows):
    ry = tbl_top + i * rh
    add_rect(s, tbl_left, ry, tbl_w, rh - Inches(0.12), color=PANEL, radius=0.08)
    add_text(s, k, tbl_left + Inches(0.25), ry + Inches(0.13), tbl_w - Inches(0.5), Inches(0.3),
              size=13, color=TEAL, bold=True)
    add_text(s, v, tbl_left + Inches(0.25), ry + Inches(0.44), tbl_w - Inches(0.5), Inches(0.4),
              size=12.5, color=GRAY)
add_source(s, "Bellincampi et al., Futures Thinking — Cap. 7.2 (Tabella 7.2)")

# ============================================================
# SLIDE 6 — Chorema cos'è
# ============================================================
s = add_slide(); add_logo(s)
add_kicker(s, "Da un comune a centinaia di territori", Inches(0.7), Inches(0.55))
add_title(s, "Chorema non è una dashboard,\nè un research environment", Inches(0.7), Inches(1.05), Inches(11.8), size=30)
add_text(s, "Si distingue da GIS tradizionali (Esri, QGIS), location intelligence (CARTO) e consulenza "
             "(Deloitte, McKinsey) combinando foresight di lungo periodo e intelligenza agentica "
             "su indici territoriali validati scientificamente.",
          Inches(0.7), Inches(2.9), Inches(9.5), Inches(1.6), size=17, color=GRAY, line_spacing=1.3)
add_rect(s, Inches(0.7), Inches(5.1), Inches(9.9), Inches(1.15), color=PANEL, radius=0.1)
add_text(s, "Gli stessi quattro tipi di dato del metodo, ora integrati e aggiornati in continuo.",
          Inches(1.0), Inches(5.4), Inches(9.3), Inches(0.7), size=18, color=TEAL, bold=True)

# ============================================================
# SLIDE 7 — Chorema come funziona
# ============================================================
s = add_slide(); add_logo(s)
add_kicker(s, "Come funziona", Inches(0.7), Inches(0.55))
add_title(s, "Indici validati + intelligenza agentica", Inches(0.7), Inches(1.05), Inches(11.8), size=30)
cols = [
    ("Data Lake", "80.000+ indicatori geospaziali e 500+ report, da fonti istituzionali e scientifiche"),
    ("Indici validati", "Sviluppati con Politecnico di Milano, Aalborg University, LUM"),
    ("Architettura multi-agente", "Coordinatore, agenti esperti di dominio, agente critico anti-hallucination"),
]
cw = Inches(3.75); cg = Inches(0.3); cx0 = Inches(0.7); cy0 = Inches(2.75); chh = Inches(3.6)
for i, (t, b) in enumerate(cols):
    cx = cx0 + i * (cw + cg)
    add_rect(s, cx, cy0, cw, chh, color=PANEL, radius=0.06)
    add_rect(s, cx, cy0, cw, Inches(0.08), color=TEAL)
    add_text(s, t, cx + Inches(0.3), cy0 + Inches(0.4), cw - Inches(0.6), Inches(0.9),
              size=18, color=WHITE, bold=True, line_spacing=1.1)
    add_text(s, b, cx + Inches(0.3), cy0 + Inches(1.4), cw - Inches(0.6), chh - Inches(1.6),
              size=13.5, color=GRAY, line_spacing=1.25)

# ============================================================
# SLIDE 8 — Perché non basta un chatbot
# ============================================================
s = add_slide(); add_logo(s)
add_kicker(s, "Perché non basta un chatbot generico", Inches(0.7), Inches(0.55))
add_title(s, "Stessa domanda, risposte diverse", Inches(0.7), Inches(1.05), Inches(11.8), size=30)
add_text(s, "“In quali provincie la domanda di competenze crescerà di più, e quali corridoi migratori "
             "saranno più praticabili nei prossimi anni?”",
          Inches(0.7), Inches(2.0), Inches(11.0), Inches(0.9), size=15, color=GRAY, italic=True, line_spacing=1.2)

leftw = Inches(5.6)
add_rect(s, Inches(0.7), Inches(3.05), leftw, Inches(3.55), color=PANEL, radius=0.06)
add_text(s, "GENERALISTI", Inches(1.0), Inches(3.3), leftw - Inches(0.6), Inches(0.35), size=13, color=MUTED, bold=True)
add_text(s, "ChatGPT · Gemini · Claude", Inches(1.0), Inches(3.68), leftw - Inches(0.6), Inches(0.35), size=13, color=GRAY)
bullet_list(s, ["Nessun dato realmente granulare", "Fonti generiche o non verificabili",
                "Nessuna indicazione operativa"], Inches(1.0), Inches(4.25), leftw - Inches(0.6), Inches(2.2),
                size=14, gap=12)

rightx = Inches(6.55)
add_rect(s, rightx, Inches(3.05), leftw, Inches(3.55), color=PANEL, radius=0.06, line_color=TEAL)
add_text(s, "FORESKILL (SU CHOREMA)", rightx + Inches(0.3), Inches(3.3), leftw - Inches(0.6), Inches(0.35), size=13, color=TEAL, bold=True)
add_text(s, "Verticale Chorema per il mercato del lavoro", rightx + Inches(0.3), Inches(3.68), leftw - Inches(0.6), Inches(0.35), size=13, color=GRAY)
bullet_list(s, ["Dati granulari per provincia e orizzonte temporale", "18 fonti curate e tracciabili",
                "Indicazioni pienamente azionabili"], rightx + Inches(0.3), Inches(4.25), leftw - Inches(0.6), Inches(2.2),
                size=14, gap=12)

# ============================================================
# SLIDE 9 — Berceto chi è + paradosso
# ============================================================
s = add_slide(); add_logo(s)
add_kicker(s, "Caso studio", Inches(0.7), Inches(0.55))
add_title(s, "Berceto, Appennino Parma Est", Inches(0.7), Inches(1.05), Inches(11.8), size=30)

facts = [
    ("Area SNAI ", "Appennino Parma Est, finanziata ciclo 2021-2027"),
    ("Classificazione ISTAT ", "E — Periferico, 44,7 minuti dal polo urbano"),
    ("Popolazione ", "-25,7% in 30 anni (1991-2021)"),
    ("Struttura demografica ", "over 65 oltre 4 volte gli under 15"),
]
bullet_list(s, facts, Inches(0.7), Inches(2.15), Inches(5.5), Inches(3.4), size=14.5, gap=18)

s.shapes.add_picture("assets/Immagine 2026-07-07 132353.png", Inches(6.55), Inches(2.05), width=Inches(6.1))
add_rect(s, Inches(0.7), Inches(5.75), Inches(11.9), Inches(0.95), color=PANEL, radius=0.1)
add_text(s, "Zero ospedali raggiungibili in 30 minuti. Il dominio più accessibile in assoluto: la ristorazione.",
          Inches(1.0), Inches(5.98), Inches(11.3), Inches(0.6), size=17, color=TEAL, bold=True)
add_source(s, "Fonte: Chorema — Aree Interne Intelligence, Urban Intelligence (Hex)")

# ============================================================
# SLIDE 10 — Scenari 2030
# ============================================================
s = add_slide(); add_logo(s)
add_kicker(s, "Scenari", Inches(0.7), Inches(0.55))
add_title(s, "Due traiettorie, a partire da oggi", Inches(0.7), Inches(1.05), Inches(11.8), size=30)

s.shapes.add_picture("assets/Immagine 2026-07-07 132222.png", Inches(0.7), Inches(2.05), width=Inches(5.6))

scenario_card(s, Inches(6.55), Inches(2.05), Inches(5.85), Inches(2.35),
              "Inerzia strutturale",
              "Il trend attuale continua: connettività e telemedicina non arrivano in tempo. "
              "La popolazione scende sotto la soglia critica entro il 2030.",
              accent=RGBColor(0xE0, 0x5A, 0x5A))
scenario_card(s, Inches(6.55), Inches(4.65), Inches(5.85), Inches(2.35),
              "Rigenerazione connessa",
              "Telemedicina, mobilità a chiamata e residenzialità digitale, attivate nel ciclo SNAI "
              "in corso, invertono parzialmente la traiettoria di declino.",
              accent=TEAL)

# ============================================================
# SLIDE 11 — Raccomandazioni
# ============================================================
s = add_slide(); add_logo(s)
add_kicker(s, "Raccomandazioni strategiche", Inches(0.7), Inches(0.55))
add_title(s, "Le scelte che possono cambiare la traiettoria", Inches(0.7), Inches(1.05), Inches(11.8), size=28)

recos = [
    ("1", "Telemedicina intercomunale", "AUSL Parma / Unione dei Comuni",
     "Presidio h24 con teleconsulto e telemonitoraggio per le cronicità, attivo entro il 2026."),
    ("2", "Mobilità a chiamata sovracomunale", "Agenzia TPL Emilia-Romagna",
     "Trasporto a chiamata tra i 9 comuni dell'area, operativo entro il 2027."),
    ("3", "Residenzialità digitale", "Comune di Berceto / GAL Appennino Parmense",
     "Incentivi abitativi e coworking per lavoratori remoti, su strutture ricettive esistenti."),
]
rw = Inches(3.85); rg = Inches(0.28); rx0 = Inches(0.7); ry0 = Inches(2.3); rh2 = Inches(4.3)
for i, (num, title, dest, body) in enumerate(recos):
    reco_card(s, rx0 + i * (rw + rg), ry0, rw, rh2, num, title, dest, body)

# ============================================================
# SLIDE 12 — Chiusura
# ============================================================
s = add_slide(); add_logo(s, left=Inches(0.7), top=Inches(0.7), width=Inches(1.4))
add_text(s, "Le scelte di oggi", Inches(0.7), Inches(2.5), Inches(11.5), Inches(1.3),
          size=44, color=WHITE, bold=True)
add_rect(s, Inches(0.72), Inches(3.55), Inches(0.55), Inches(0.045), color=TEAL)
add_text(s, "Il ciclo SNAI 2021-2027 è aperto. Le tecnologie per leggere e anticipare i divari "
             "territoriali esistono già.\nQuello che ridurrà davvero le disuguaglianze tra i luoghi "
             "non è un nuovo dato: è la scelta di usarlo, ora.",
          Inches(0.7), Inches(3.8), Inches(10.5), Inches(1.8), size=18, color=GRAY, line_spacing=1.35)
add_text(s, "Martino Bellincampi  —  IZILab  ·  www.izilab.it", Inches(0.7), Inches(6.5), Inches(9), Inches(0.5),
          size=14, color=TEAL, bold=True)

for i, slide in enumerate(prs.slides, 1):
    add_page_number(slide, i)

prs.save("dashboard-convegno-RER.pptx")
print("saved, slides:", len(prs.slides))
