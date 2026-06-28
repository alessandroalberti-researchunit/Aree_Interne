"""
Genera dashboard-aree-interne.html con GeoJSON SNAI embedded come variabile JS.
Arricchisce ogni area con dati calcolati dall'Excel: n_comuni, pop_2020, distribuzione SNAI 2020.
"""
import json, os
import pandas as pd

GEOJSON_PATH        = r'C:\Users\aalbe\Desktop\Code\Aree Interne Italia\aree-snai-perimetri.geojson'
COMUNI_GEOJSON_PATH = r'C:\Users\aalbe\Desktop\Code\Aree Interne Italia\comuni-snai-perimetri.geojson'
SLL_GEOJSON_PATH    = r'C:\Users\aalbe\Desktop\Code\Aree Interne Italia\sll-perimetri.geojson'
EXCEL_08            = r'C:\Users\aalbe\Desktop\Code\Aree Interne Italia\DATA\08_elenco-aree-comuni.xlsx'
EXCEL_MAPPA         = r'C:\Users\aalbe\Desktop\Code\Aree Interne Italia\DATA\mappa-ai-2020-elenco-classificazione-comuni.xlsx'
OUT_HTML            = r'C:\Users\aalbe\Desktop\Code\Aree Interne Italia\dashboard-aree-interne.html'

# ── GeoJSON ────────────────────────────────────────────────────────────────────
with open(GEOJSON_PATH, encoding='utf-8') as f:
    geojson_str = f.read().strip()
gj = json.loads(geojson_str)

with open(COMUNI_GEOJSON_PATH, encoding='utf-8') as f:
    comuni_geojson_str = f.read().strip()

with open(SLL_GEOJSON_PATH, encoding='utf-8') as f:
    sll_geojson_str = f.read().strip()

# ── Per-area stats from Excel ──────────────────────────────────────────────────
def load_sheet_totale():
    COLS = ["_drop","pro_com","pro_com_t","comune","macroarea","regione","provincia",
            "pop_2020","macro_ai_2020","snai_2020","area_snai","note","gia_area_1420"]
    df = pd.read_excel(EXCEL_08, sheet_name="Elenco Aree 21-27 TOTALE",
                       header=None, skiprows=2, names=COLS, dtype=str)
    df = df.drop(columns=["_drop"])
    for c in ("area_snai","snai_2020"):
        df[c] = df[c].str.strip()
    df["pop_2020"] = pd.to_numeric(df["pop_2020"], errors="coerce")
    return df[df["pro_com_t"].notna() & df["pro_com_t"].str.match(r"^\d{6}$")].copy()

def load_sheet_no():
    COLS = ["_drop","pro_com","pro_com_t","comune","regione","provincia",
            "pop_2020","macro_ai_2020","snai_2020","area_snai","note"]
    raw = pd.read_excel(EXCEL_08, sheet_name="Comuni 13 Aree 21-27 NO finanz.", header=None, dtype=str)
    hdr = int((raw.iloc[:, 2] == "PRO_COM_T").idxmax()) + 1
    df = raw.iloc[hdr:].copy().reset_index(drop=True)
    df.columns = COLS
    df = df.drop(columns=["_drop"])
    for c in ("area_snai","snai_2020"):
        df[c] = df[c].str.strip()
    df["pop_2020"] = pd.to_numeric(df["pop_2020"], errors="coerce")
    return df[df["pro_com_t"].notna() & df["pro_com_t"].str.match(r"^\d{6}$")].copy()

df_all = pd.concat([load_sheet_totale(), load_sheet_no()], ignore_index=True)

# ── Extra per-comune data: superficie km², tempi di percorrenza ────────────────
_mappa = pd.read_excel(EXCEL_MAPPA, sheet_name="DATI", header=2, dtype=str)
_mappa.columns = [str(c).strip() for c in _mappa.columns]
_km2_col  = [c for c in _mappa.columns if 'superficie' in c.lower()][0]
_min_col  = [c for c in _mappa.columns if 'tempi' in c.lower()][0]
_mappa['_procom'] = _mappa['PROCOM_T'].str.zfill(6)
_mappa['_km2']    = pd.to_numeric(_mappa[_km2_col], errors='coerce')
_mappa['_min']    = pd.to_numeric(_mappa[_min_col], errors='coerce')
_comuni_extra = {row['_procom']: {'km2': row['_km2'], 'min': row['_min']}
                 for _, row in _mappa.iterrows() if pd.notna(row['_procom'])}

# ── Area-level investments from "Assegnazioni per Aree" ───────────────────────
_inv_raw = pd.read_excel(EXCEL_08, sheet_name="Assegnazioni per Aree", header=None, skiprows=5, dtype=str)
_inv_raw.columns = ['macroarea', 'regione', 'area', 'totale', 'fsc', 'fdr']
_area_inv = {}
for _, row in _inv_raw.iterrows():
    area = str(row.get('area') or '').strip()
    tot  = pd.to_numeric(row.get('totale'), errors='coerce')
    if area and pd.notna(tot):
        _area_inv[area] = int(tot)

def snai_letter(s):
    return s[0] if isinstance(s, str) and s.strip() else None

area_stats = {}
for area_name, grp in df_all.groupby("area_snai"):
    dist = {}
    for s in grp["snai_2020"]:
        ltr = snai_letter(s)
        if ltr:
            dist[ltr] = dist.get(ltr, 0) + 1
    area_stats[area_name] = {
        "n": int(len(grp)),
        "pop": int(grp["pop_2020"].sum()),
        "snai_dist": {k: dist[k] for k in sorted(dist)},
    }

# ── Base area list (regione, area, status; lat/lon only for solo-1420) ─────────
AREE_BASE = [
    # SI (43 aree)
    {"regione":"Abruzzo",               "area":"Piana del Cavaliere - Alto Liri",                                       "status":"SI"},
    {"regione":"Abruzzo",               "area":"Valle del Sagittario e dell'Alto Sangro",                               "status":"SI"},
    {"regione":"Basilicata",            "area":"Medio Agri",                                                            "status":"SI"},
    {"regione":"Basilicata",            "area":"Medio Basento",                                                         "status":"SI"},
    {"regione":"Calabria",              "area":"Alto Jonio Cosentino",                                                  "status":"SI"},
    {"regione":"Calabria",              "area":"Versante Tirrenico Aspromonte",                                         "status":"SI"},
    {"regione":"Campania",              "area":"Alto Matese",                                                           "status":"SI"},
    {"regione":"Campania",              "area":"Fortore Beneventano",                                                   "status":"SI"},
    {"regione":"Campania",              "area":"Sele Tanagro",                                                          "status":"SI"},
    {"regione":"Emilia-Romagna",        "area":"Appennino Forlivese e Cesenate",                                        "status":"SI"},
    {"regione":"Emilia-Romagna",        "area":"Appennino Modenese",                                                    "status":"SI"},
    {"regione":"Emilia-Romagna",        "area":"Appennino Parma Est",                                                   "status":"SI"},
    {"regione":"Friuli-Venezia Giulia", "area":"Valli del Torre e Natisone",                                            "status":"SI"},
    {"regione":"Lazio",                 "area":"Monti Lepini",                                                          "status":"SI"},
    {"regione":"Lazio",                 "area":"Pre.gio",                                                               "status":"SI"},
    {"regione":"Liguria",               "area":"Fontanabuona",                                                          "status":"SI"},
    {"regione":"Liguria",               "area":"Imperiese",                                                             "status":"SI"},
    {"regione":"Lombardia",             "area":"Lario Intelvese - Lario Ceresio",                                       "status":"SI"},
    {"regione":"Lombardia",             "area":"Valcamonica",                                                           "status":"SI"},
    {"regione":"Lombardia",             "area":"Valtrompia",                                                            "status":"SI"},
    {"regione":"Marche",                "area":"Appennino Alto Fermano",                                                "status":"SI"},
    {"regione":"Marche",                "area":"Montefeltro e Alta Valle del Metauro",                                  "status":"SI"},
    {"regione":"Molise",                "area":"Isernia - Venafro",                                                     "status":"SI"},
    {"regione":"Molise",                "area":"Medio Basso Molise",                                                    "status":"SI"},
    {"regione":"Piemonte",              "area":"Terre del Giarolo",                                                     "status":"SI"},
    {"regione":"Piemonte",              "area":"Valsesia",                                                              "status":"SI"},
    {"regione":"Puglia",                "area":"Alto Salento",                                                          "status":"SI"},
    {"regione":"Sardegna",              "area":"Barbagia",                                                              "status":"SI"},
    {"regione":"Sardegna",              "area":"Valle del Cedrino",                                                     "status":"SI"},
    {"regione":"Sicilia",               "area":"Bronte",                                                                "status":"SI"},
    {"regione":"Sicilia",               "area":"Corleone",                                                              "status":"SI"},
    {"regione":"Sicilia",               "area":"Troina",                                                                "status":"SI"},
    {"regione":"Toscana",               "area":"Alta Valdera - Alta Valdicecina - Colline Metallifere - Valdimerse",    "status":"SI"},
    {"regione":"Toscana",               "area":"Amiata Valdorcia - Amiata Grossetana - Colline del Fiora",             "status":"SI"},
    {"regione":"PA Bolzano",            "area":"Alta Val Venosta",                                                      "status":"SI"},
    {"regione":"PA Bolzano",            "area":"Val d'Ultimo - Alta Val di Non - Tesimo - Lana",                       "status":"SI"},
    {"regione":"PA Trento",             "area":"Giudicarie centrali ed esteriori",                                      "status":"SI"},
    {"regione":"PA Trento",             "area":"Valle Rendena",                                                         "status":"SI"},
    {"regione":"Umbria",                "area":"Media Valle del Tevere e Umbria meridionale",                           "status":"SI"},
    {"regione":"Umbria",                "area":"Unione di Comuni del Trasimeno",                                        "status":"SI"},
    {"regione":"Valle d'Aosta",         "area":"Mont Cervin",                                                           "status":"SI"},
    {"regione":"Veneto",                "area":"Alpago Zoldo",                                                          "status":"SI"},
    {"regione":"Veneto",                "area":"Cadore",                                                                "status":"SI"},
    # NO (13 aree)
    {"regione":"Basilicata",            "area":"Vulture",                                                               "status":"NO"},
    {"regione":"Calabria",              "area":"Alto Tirreno-Pollino",                                                  "status":"NO"},
    {"regione":"Emilia-Romagna",        "area":"Alta Val Trebbia e Val Tidone",                                         "status":"NO"},
    {"regione":"Emilia-Romagna",        "area":"Appennino Bolognese",                                                   "status":"NO"},
    {"regione":"Lazio",                 "area":"Etrusco Cimina",                                                        "status":"NO"},
    {"regione":"Liguria",               "area":"Val Bormida Ligure",                                                    "status":"NO"},
    {"regione":"Liguria",               "area":"Valle Scrivia",                                                         "status":"NO"},
    {"regione":"Marche",                "area":"Potenza Esino Musone",                                                  "status":"NO"},
    {"regione":"Sicilia",               "area":"Mussomeli",                                                             "status":"NO"},
    {"regione":"Sicilia",               "area":"Palagonia",                                                             "status":"NO"},
    {"regione":"Sicilia",               "area":"Santa Teresa di Riva",                                                  "status":"NO"},
    {"regione":"Toscana",               "area":"Valdichiana Senese",                                                    "status":"NO"},
    {"regione":"PA Bolzano",            "area":"Val Passiria - Tirolo",                                                 "status":"NO"},
    # CONF (67 aree)
    {"regione":"Abruzzo",               "area":"Alto Aterno - Gran Sasso Laga",                                        "status":"CONF"},
    {"regione":"Abruzzo",               "area":"Basso Sangro - Trigno",                                                "status":"CONF"},
    {"regione":"Abruzzo",               "area":"Gran Sasso - Valle Subequana",                                         "status":"CONF"},
    {"regione":"Abruzzo",               "area":"Valfino-Vestina",                                                       "status":"CONF"},
    {"regione":"Abruzzo",               "area":"Valle del Giovenco - Valle Roveto",                                    "status":"CONF"},
    {"regione":"Basilicata",            "area":"Alto Bradano",                                                          "status":"CONF"},
    {"regione":"Basilicata",            "area":"Marmo Platano",                                                         "status":"CONF"},
    {"regione":"Basilicata",            "area":"Mercure - Alto Sinni - Val Sarmento",                                   "status":"CONF"},
    {"regione":"Basilicata",            "area":"Montagna Materana",                                                     "status":"CONF"},
    {"regione":"Calabria",              "area":"Versante Ionico - Serre",                                               "status":"CONF"},
    {"regione":"Calabria",              "area":"Grecanica",                                                             "status":"CONF"},
    {"regione":"Calabria",              "area":"Reventino - Savuto",                                                    "status":"CONF"},
    {"regione":"Calabria",              "area":"Sila e Presila",                                                        "status":"CONF"},
    {"regione":"Campania",              "area":"Alta Irpinia",                                                          "status":"CONF"},
    {"regione":"Campania",              "area":"Cilento Interno",                                                       "status":"CONF"},
    {"regione":"Campania",              "area":"Tammaro - Titerno",                                                     "status":"CONF"},
    {"regione":"Campania",              "area":"Vallo di Diano",                                                        "status":"CONF"},
    {"regione":"Emilia-Romagna",        "area":"Alta Valmarecchia",                                                     "status":"CONF"},
    {"regione":"Emilia-Romagna",        "area":"Appennino Emiliano",                                                    "status":"CONF"},
    {"regione":"Emilia-Romagna",        "area":"Appennino Piacentino Parmense",                                        "status":"CONF"},
    {"regione":"Emilia-Romagna",        "area":"Basso Ferrarese",                                                       "status":"CONF"},
    {"regione":"Friuli-Venezia Giulia", "area":"Alta Carnia",                                                           "status":"CONF"},
    {"regione":"Friuli-Venezia Giulia", "area":"Dolomiti Friulane",                                                     "status":"CONF"},
    {"regione":"Friuli-Venezia Giulia", "area":"Canal del Ferro - Val Canale",                                         "status":"CONF"},
    {"regione":"Lazio",                 "area":"Alta Tuscia Antica Città del Castro",                                   "status":"CONF"},
    {"regione":"Lazio",                 "area":"Monti Reatini",                                                         "status":"CONF"},
    {"regione":"Lazio",                 "area":"Monti Simbruini",                                                       "status":"CONF"},
    {"regione":"Lazio",                 "area":"Valle del Comino",                                                      "status":"CONF"},
    {"regione":"Liguria",               "area":"Beigua SOL",                                                            "status":"CONF"},
    {"regione":"Liguria",               "area":"Alta Valle Arroscia",                                                   "status":"CONF"},
    {"regione":"Liguria",               "area":"Antola-Tigullio",                                                       "status":"CONF"},
    {"regione":"Liguria",               "area":"Val di Vara",                                                           "status":"CONF"},
    {"regione":"Lombardia",             "area":"Alto Lago di Como e Valli del Lario",                                   "status":"CONF"},
    {"regione":"Lombardia",             "area":"Appennino Lombardo - Alto Oltrepò Pavese",                             "status":"CONF"},
    {"regione":"Lombardia",             "area":"Valchiavenna",                                                          "status":"CONF"},
    {"regione":"Marche",                "area":"Appennino Basso Pesarese e Anconetano",                                "status":"CONF"},
    {"regione":"Marche",                "area":"Alto Maceratese",                                                       "status":"CONF"},
    {"regione":"Marche",                "area":"Piceno",                                                                "status":"CONF"},
    {"regione":"Molise",                "area":"Alto Medio Sannio",                                                     "status":"CONF"},
    {"regione":"Molise",                "area":"Fortore",                                                               "status":"CONF"},
    {"regione":"Molise",                "area":"Mainarde",                                                              "status":"CONF"},
    {"regione":"Molise",                "area":"Matese",                                                                "status":"CONF"},
    {"regione":"Puglia",                "area":"Alta Murgia",                                                           "status":"CONF"},
    {"regione":"Puglia",                "area":"Gargano",                                                               "status":"CONF"},
    {"regione":"Puglia",                "area":"Monti Dauni",                                                           "status":"CONF"},
    {"regione":"Puglia",                "area":"Sud Salento",                                                           "status":"CONF"},
    {"regione":"Sardegna",              "area":"Alta Marmilla",                                                         "status":"CONF"},
    {"regione":"Sardegna",              "area":"Gennargentu - Mandrolisai",                                             "status":"CONF"},
    {"regione":"Sicilia",               "area":"Calatino",                                                              "status":"CONF"},
    {"regione":"Sicilia",               "area":"Madonie",                                                               "status":"CONF"},
    {"regione":"Sicilia",               "area":"Nebrodi",                                                               "status":"CONF"},
    {"regione":"Sicilia",               "area":"Valle del Simeto",                                                      "status":"CONF"},
    {"regione":"Sicilia",               "area":"Terre Sicane",                                                          "status":"CONF"},
    {"regione":"Toscana",               "area":"Casentino - Valtiberina",                                               "status":"CONF"},
    {"regione":"Toscana",               "area":"Garfagnana-Lunigiana - Media Valle del Serchio - Appennino Pistoiese", "status":"CONF"},
    {"regione":"Toscana",               "area":"Valdarno e Valdisieve, Mugello, Val Bisenzio",                         "status":"CONF"},
    {"regione":"PA Trento",             "area":"Tesino",                                                                "status":"CONF"},
    {"regione":"PA Trento",             "area":"Val di Sole",                                                           "status":"CONF"},
    {"regione":"Umbria",                "area":"Nord Est Umbria",                                                       "status":"CONF"},
    {"regione":"Umbria",                "area":"Sud Ovest Orvietano",                                                   "status":"CONF"},
    {"regione":"Umbria",                "area":"Val Nerina",                                                            "status":"CONF"},
    {"regione":"Valle d'Aosta",         "area":"Grand Paradis",                                                         "status":"CONF"},
    {"regione":"Valle d'Aosta",         "area":"Bassa Valle",                                                           "status":"CONF"},
    {"regione":"Veneto",                "area":"Agordino",                                                              "status":"CONF"},
    {"regione":"Veneto",                "area":"Comelico",                                                              "status":"CONF"},
    {"regione":"Veneto",                "area":"Contratto di Foce - Delta del Po",                                      "status":"CONF"},
    {"regione":"Veneto",                "area":"Spettabile Reggenza",                                                   "status":"CONF"},
    # solo-1420 (5 aree)
    {"regione":"Lombardia",             "area":"Alta Valtellina",     "status":"1420", "n":5},
    {"regione":"Piemonte",              "area":"Val Bormida",         "status":"1420", "n":33},
    {"regione":"Piemonte",              "area":"Val di Lanzo",        "status":"1420", "n":19},
    {"regione":"Piemonte",              "area":"Val d'Ossola",        "status":"1420", "n":10},
    {"regione":"Piemonte",              "area":"Valli Grana e Maira", "status":"1420", "n":18},
]

# ── Compute totals ─────────────────────────────────────────────────────────────
def total_n(status):
    return sum(area_stats.get(a['area'], {}).get('n', 0) for a in AREE_BASE if a['status'] == status)

si_n    = total_n('SI')
conf_n  = total_n('CONF')
no_n    = total_n('NO')
known_n = si_n + conf_n + no_n

# ── Generate AREE JS array ─────────────────────────────────────────────────────
def jv(v):
    if v is None:
        return 'null'
    return json.dumps(v, ensure_ascii=False)

aree_lines = []
for a in AREE_BASE:
    stats = area_stats.get(a['area'], {})
    n    = stats.get('n', a.get('n'))
    pop  = stats.get('pop', a.get('pop'))
    dist = stats.get('snai_dist')
    parts = [
        f'regione:{jv(a["regione"])}',
        f'area:{jv(a["area"])}',
        f'n:{jv(n)}',
        f'pop:{jv(pop)}',
        f'status:{jv(a["status"])}',
        f'snai_dist:{jv(dist)}',
    ]
    if 'lat' in a:
        parts += [f'lat:{a["lat"]}', f'lon:{a["lon"]}']
    aree_lines.append('  {' + ','.join(parts) + '}')

AREE_JS = 'const AREE = [\n' + ',\n'.join(aree_lines) + '\n];'

# ── Generate COMUNI_BY_AREA JS object ─────────────────────────────────────────
# Keys: n=nome, p=provincia(2 chars), pop=popolazione, s=snai letter,
#       km2=superficie, min=tempi percorrenza
comuni_by_area = {}
for area_name, grp in df_all.groupby("area_snai"):
    entries = []
    for _, row in grp.sort_values("comune").iterrows():
        prov   = str(row.get("provincia") or "").strip()
        snai   = str(row.get("snai_2020") or "").strip()
        pop    = int(row["pop_2020"]) if pd.notna(row.get("pop_2020")) else None
        procom = str(row.get("pro_com_t") or "").strip().zfill(6)
        extra  = _comuni_extra.get(procom, {})
        km2_v  = extra.get('km2')
        min_v  = extra.get('min')
        entry  = {
            "n":   str(row["comune"]).strip(),
            "p":   prov[:2] if prov else "",
            "pop": pop,
            "s":   snai[0] if snai else "",
        }
        if km2_v is not None and not pd.isna(km2_v):
            entry["km2"] = round(float(km2_v), 1)
        if min_v is not None and not pd.isna(min_v):
            entry["min"] = round(float(min_v), 1)
        entries.append(entry)
    comuni_by_area[area_name] = entries

COMUNI_JS = 'const COMUNI_BY_AREA = ' + json.dumps(comuni_by_area, ensure_ascii=False, separators=(',', ':')) + ';'

# ── Area investments JS object ─────────────────────────────────────────────────
AREA_INV_JS = 'const AREA_INV = ' + json.dumps(_area_inv, ensure_ascii=False, separators=(',', ':')) + ';'

# ── HTML template ──────────────────────────────────────────────────────────────
HTML = r"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dashboard — Aree Interne SNAI</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  *, *::before, *::after { box-sizing:border-box; margin:0; padding:0; }
  body { font-family:'Segoe UI',system-ui,sans-serif; background:#0f172a; color:#e2e8f0; min-height:100vh; display:flex; flex-direction:column; }
  header { background:#1e293b; border-bottom:1px solid #334155; padding:12px 20px; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:10px; }
  .logo h1 { font-size:1.05rem; font-weight:700; color:#f1f5f9; }
  .logo p { font-size:0.68rem; color:#64748b; margin-top:2px; }
  .kpi-row { display:flex; gap:8px; flex-wrap:wrap; }
  .kpi { background:#0f172a; border:1px solid #334155; border-radius:8px; padding:8px 14px; text-align:center; min-width:80px; }
  .kpi .num { font-size:1.35rem; font-weight:800; line-height:1; }
  .kpi .lbl { font-size:0.62rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.06em; margin-top:3px; }
  .kpi.teal .num  { color:#2dd4bf; }
  .kpi.blue .num  { color:#60a5fa; }
  .kpi.green .num { color:#4ade80; }
  .kpi.lblue .num { color:#93c5fd; }
  .kpi.orange .num{ color:#fb923c; }
  .kpi.gray .num  { color:#94a3b8; }
  .main { display:flex; flex:1; height:calc(100vh - 118px); min-height:500px; }
  .sidebar { width:300px; min-width:260px; background:#1e293b; border-right:1px solid #334155; display:flex; flex-direction:column; overflow-y:auto; }
  .sidebar-section { padding:14px; border-bottom:1px solid #334155; }
  .sidebar-section h3 { font-size:0.68rem; text-transform:uppercase; letter-spacing:0.08em; color:#64748b; margin-bottom:10px; }
  .chart-wrap      { position:relative; height:150px; }
  .chart-wrap-tall { position:relative; height:300px; }
  .stat-grid { display:grid; grid-template-columns:1fr 1fr; gap:7px; }
  .stat-card { background:#0f172a; border:1px solid #334155; border-radius:6px; padding:8px; text-align:center; }
  .stat-card .val { font-size:0.98rem; font-weight:700; color:#f1f5f9; }
  .stat-card .desc { font-size:0.6rem; color:#64748b; margin-top:2px; line-height:1.3; }
  .center-col { flex:1; display:flex; flex-direction:column; min-width:0; }
  .filter-bar { background:#1e293b; border-bottom:1px solid #334155; padding:8px 14px; display:flex; align-items:center; gap:12px; flex-wrap:wrap; }
  .filter-bar .fg { display:flex; align-items:center; gap:5px; }
  .filter-bar label { font-size:0.68rem; color:#64748b; white-space:nowrap; }
  .filter-bar select, .filter-bar input[type=text] { background:#0f172a; border:1px solid #334155; border-radius:6px; color:#e2e8f0; padding:4px 8px; font-size:0.76rem; outline:none; }
  .filter-bar select:focus, .filter-bar input:focus { border-color:#60a5fa; }
  .btn-reset { background:#334155; border:none; color:#cbd5e1; border-radius:6px; padding:5px 12px; font-size:0.73rem; cursor:pointer; white-space:nowrap; margin-left:auto; }
  .btn-reset:hover { background:#475569; }
  #map { flex:1; z-index:1; }
  .right-panel { width:260px; min-width:220px; background:#1e293b; border-left:1px solid #334155; display:flex; flex-direction:column; overflow-y:auto; padding:14px; }
  .rp-header { display:flex; align-items:center; gap:6px; margin-bottom:10px; }
  .rp-header h3 { font-size:0.68rem; text-transform:uppercase; letter-spacing:0.08em; color:#64748b; }
  .btn-back { background:#1e293b; border:1px solid #334155; color:#94a3b8; border-radius:4px; padding:3px 8px; font-size:0.7rem; cursor:pointer; line-height:1; }
  .btn-back:hover { background:#334155; color:#e2e8f0; }
  .legend { display:flex; flex-direction:column; gap:8px; }
  .legend-item { display:flex; align-items:center; gap:8px; font-size:0.74rem; color:#cbd5e1; line-height:1.3; }
  .legend-dot { width:12px; height:12px; border-radius:50%; flex-shrink:0; }
  .stats-title { font-size:0.9rem; font-weight:700; color:#f1f5f9; margin-bottom:10px; line-height:1.3; }
  .s-kpi-row { display:grid; grid-template-columns:1fr 1fr; gap:6px; margin-bottom:10px; }
  .s-kpi { background:#0f172a; border:1px solid #334155; border-radius:6px; padding:8px 6px; text-align:center; }
  .s-kpi .val { display:block; font-size:1.05rem; font-weight:700; color:#f1f5f9; }
  .s-kpi .lbl { display:block; font-size:0.6rem; color:#64748b; margin-top:2px; text-transform:uppercase; letter-spacing:0.05em; }
  .s-section-title { font-size:0.62rem; color:#64748b; text-transform:uppercase; letter-spacing:0.06em; margin:8px 0 5px; }
  .item-list { display:flex; flex-direction:column; gap:3px; }
  .list-item { background:#0f172a; border-radius:5px; padding:6px 8px; cursor:default; }
  .list-item.clickable { cursor:pointer; border:1px solid transparent; }
  .list-item.clickable:hover { border-color:#334155; }
  .list-item .i-name { font-size:0.73rem; font-weight:500; line-height:1.3; }
  .list-item .i-meta { font-size:0.63rem; color:#64748b; margin-top:1px; }
  .comune-item { background:#0f172a; border-radius:4px; padding:5px 8px; }
  .comune-item .c-name { font-size:0.72rem; color:#e2e8f0; }
  .comune-item .c-meta { font-size:0.62rem; color:#64748b; margin-top:1px; }
  .table-panel { background:#1e293b; border-top:1px solid #334155; max-height:220px; overflow-y:auto; }
  .table-toggle { display:flex; align-items:center; justify-content:space-between; padding:9px 16px; cursor:pointer; background:#1e293b; border-bottom:1px solid #334155; position:sticky; top:0; z-index:10; }
  .table-toggle span { font-size:0.72rem; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; color:#94a3b8; }
  table { width:100%; border-collapse:collapse; font-size:0.76rem; }
  th { background:#0f172a; color:#64748b; font-size:0.65rem; text-transform:uppercase; letter-spacing:0.06em; padding:7px 12px; text-align:left; position:sticky; top:38px; }
  td { padding:6px 12px; border-bottom:1px solid #1e293b; color:#cbd5e1; }
  tr:hover td { background:#0f172a; }
  .badge { display:inline-flex; align-items:center; padding:2px 7px; border-radius:20px; font-size:0.65rem; font-weight:600; }
  .badge.si    { background:#14532d; color:#4ade80; }
  .badge.no    { background:#431407; color:#fb923c; }
  .badge.conf  { background:#1e3a5f; color:#93c5fd; }
  .badge.s1420 { background:#1e293b; color:#94a3b8; border:1px solid #334155; }
  .leaflet-popup-content-wrapper { background:#1e293b; border:1px solid #334155; border-radius:10px; box-shadow:0 4px 24px rgba(0,0,0,0.5); }
  .leaflet-popup-content { color:#e2e8f0; font-family:'Segoe UI',system-ui,sans-serif; font-size:0.8rem; margin:11px 13px; }
  .leaflet-popup-tip { background:#1e293b; }
  .comune-tooltip { background:#0f172a !important; border:1px solid #475569 !important; border-radius:6px; color:#e2e8f0; font-family:'Segoe UI',system-ui,sans-serif; padding:7px 10px !important; white-space:nowrap; box-shadow:0 3px 12px rgba(0,0,0,0.6); pointer-events:none; }
  .comune-tooltip::before { display:none !important; }
  .ct-name { font-size:0.76rem; font-weight:700; color:#f1f5f9; margin-bottom:4px; }
  .ct-row { display:flex; justify-content:space-between; gap:14px; font-size:0.68rem; color:#94a3b8; line-height:1.6; }
  .ct-row span:last-child { color:#cbd5e1; font-weight:500; }
  .area-popup .leaflet-popup-close-button { color:#94a3b8; font-size:1rem; top:6px; right:8px; }
  .area-popup .leaflet-popup-close-button:hover { color:#f1f5f9; }
  .popup-title { font-weight:700; font-size:0.88rem; color:#f1f5f9; margin-bottom:6px; line-height:1.3; }
  .popup-row { display:flex; justify-content:space-between; gap:12px; color:#94a3b8; margin:2px 0; }
  .popup-row span:last-child { color:#e2e8f0; font-weight:500; }
  .popup-snai { font-size:0.68rem; color:#64748b; margin-top:5px; padding-top:5px; border-top:1px solid #334155; }
  ::-webkit-scrollbar { width:4px; height:4px; }
  ::-webkit-scrollbar-track { background:#0f172a; }
  ::-webkit-scrollbar-thumb { background:#334155; border-radius:2px; }
  /* Capofila */
  .capofila-row { display:flex; align-items:center; gap:8px; background:#0f172a; border:1px solid #334155; border-radius:6px; padding:7px 10px; margin-bottom:8px; }
  .capofila-lbl { font-size:0.6rem; color:#64748b; text-transform:uppercase; letter-spacing:0.06em; flex-shrink:0; }
  .capofila-val { font-size:0.75rem; font-weight:600; color:#fbbf24; line-height:1.3; }
  .comune-item.is-capofila { border-left:2px solid #fbbf24; background:#0f172a; padding-left:6px; }
  .capofila-badge { display:inline-block; font-size:0.5rem; font-weight:700; background:#fbbf24; color:#0f172a; border-radius:3px; padding:1px 4px; margin-left:5px; letter-spacing:0.05em; vertical-align:middle; }
  /* Tema toggle */
  .btn-theme { background:transparent; border:1px solid #334155; color:#94a3b8; border-radius:6px; padding:5px 9px; font-size:0.88rem; cursor:pointer; line-height:1; }
  .btn-theme:hover { border-color:#60a5fa; color:#60a5fa; }
  /* ── Tema chiaro ─────────────────────────────────────────────────────────── */
  body.light { background:#f8fafc; color:#1e293b; }
  body.light header { background:#ffffff; border-bottom-color:#e2e8f0; }
  body.light .logo h1 { color:#0f172a; }
  body.light .logo p { color:#94a3b8; }
  body.light .kpi { background:#f1f5f9; border-color:#e2e8f0; }
  body.light .kpi .num { color:#0f172a; }
  body.light .kpi .lbl { color:#64748b; }
  body.light .sidebar { background:#ffffff; border-color:#e2e8f0; }
  body.light .sidebar-section { border-color:#f1f5f9; }
  body.light .sidebar-section h3 { color:#64748b; }
  body.light .stat-card { background:#f1f5f9; border-color:#e2e8f0; }
  body.light .stat-card .val { color:#0f172a; }
  body.light .stat-card .desc { color:#64748b; }
  body.light .sidebar-input { background:#f1f5f9; border-color:#e2e8f0; color:#1e293b; }
  body.light .right-panel { background:#ffffff; border-color:#e2e8f0; }
  body.light .rp-header h3 { color:#94a3b8; }
  body.light .stats-title { color:#0f172a; }
  body.light .s-kpi { background:#f1f5f9; border-color:#e2e8f0; }
  body.light .s-kpi .val { color:#0f172a; }
  body.light .s-kpi .lbl { color:#94a3b8; }
  body.light .s-section-title { color:#94a3b8; }
  body.light .list-item { background:#f1f5f9; }
  body.light .list-item.clickable:hover { border-color:#cbd5e1; }
  body.light .list-item .i-meta { color:#94a3b8; }
  body.light .comune-item { background:#f8fafc; }
  body.light .comune-item .c-name { color:#1e293b; }
  body.light .comune-item .c-meta { color:#94a3b8; }
  body.light .comune-item.is-capofila { background:#fffbeb; border-left-color:#d97706; }
  body.light .capofila-badge { background:#d97706; color:#fff; }
  body.light .capofila-row { background:#fefce8; border-color:#fef08a; }
  body.light .legend-item { color:#475569; }
  body.light .btn-back { background:#f1f5f9; border-color:#e2e8f0; color:#475569; }
  body.light .btn-back:hover { background:#e2e8f0; }
  body.light .btn-info { border-color:#e2e8f0; color:#64748b; }
  body.light .btn-theme { border-color:#e2e8f0; color:#64748b; }
  body.light .btn-theme:hover { border-color:#3b82f6; color:#3b82f6; }
  body.light .leaflet-popup-content-wrapper { background:#ffffff; border-color:#e2e8f0; }
  body.light .leaflet-popup-content { color:#1e293b; }
  body.light .leaflet-popup-tip { background:#ffffff; }
  body.light .popup-row { color:#475569; }
  body.light .popup-row span:last-child { color:#1e293b; }
  body.light .popup-snai { color:#94a3b8; border-top-color:#e2e8f0; }
  body.light .popup-title { color:#0f172a; }
  body.light .comune-tooltip { background:#ffffff !important; border-color:#cbd5e1 !important; }
  body.light .ct-name { color:#0f172a; }
  body.light .ct-row { color:#64748b; }
  body.light .ct-row span:last-child { color:#1e293b; }
  body.light .badge.conf { background:#dbeafe; color:#1d4ed8; }
  body.light .badge.si { background:#dcfce7; color:#15803d; }
  body.light .badge.no { background:#ffedd5; color:#c2410c; }
  body.light .badge.s1420 { background:#f1f5f9; color:#475569; border-color:#e2e8f0; }
  body.light table th { background:#f1f5f9; color:#94a3b8; }
  body.light table td { color:#475569; border-bottom-color:#f1f5f9; }
  body.light tr:hover td { background:#f8fafc; }
  body.light .table-panel { background:#ffffff; border-top-color:#e2e8f0; }
  body.light .table-toggle { background:#ffffff; border-bottom-color:#e2e8f0; }
  body.light .table-toggle span { color:#475569; }
  body.light ::-webkit-scrollbar-track { background:#f1f5f9; }
  body.light ::-webkit-scrollbar-thumb { background:#cbd5e1; }
  body.light .modal-box { background:#ffffff; border-color:#e2e8f0; }
  body.light .md p, body.light .md li { color:#475569; }
  body.light .md h2 { color:#0f172a; }
  body.light .md h3 { color:#1e293b; }
  body.light .md strong { color:#1e293b; }
  body.light .md code { background:#f1f5f9; border-color:#e2e8f0; color:#2563eb; }
  body.light .md hr { border-top-color:#e2e8f0; }
  /* Info modal */
  .btn-info { background:transparent; border:1px solid #334155; color:#64748b; border-radius:6px; padding:5px 11px; font-size:0.78rem; cursor:pointer; }
  .btn-info:hover { border-color:#60a5fa; color:#60a5fa; }
  .modal-overlay { display:none; position:fixed; inset:0; background:rgba(0,0,0,0.7); z-index:9000; align-items:center; justify-content:center; }
  .modal-overlay.open { display:flex; }
  .modal-box { background:#1e293b; border:1px solid #334155; border-radius:12px; max-width:720px; width:90%; max-height:85vh; overflow-y:auto; padding:28px 32px; position:relative; }
  .modal-close { position:absolute; top:14px; right:16px; background:transparent; border:none; color:#64748b; font-size:1.2rem; cursor:pointer; line-height:1; }
  .modal-close:hover { color:#f1f5f9; }
  .md h2 { font-size:1.1rem; font-weight:700; color:#f1f5f9; margin:0 0 16px; }
  .md h3 { font-size:0.85rem; font-weight:700; color:#e2e8f0; margin:20px 0 8px; text-transform:uppercase; letter-spacing:0.05em; }
  .md p { font-size:0.82rem; color:#94a3b8; line-height:1.7; margin:0 0 10px; }
  .md ul { margin:0 0 10px 18px; }
  .md li { font-size:0.82rem; color:#94a3b8; line-height:1.7; }
  .md strong { color:#e2e8f0; font-weight:600; }
  .md code { background:#0f172a; border:1px solid #334155; border-radius:4px; padding:1px 6px; font-size:0.78rem; color:#7dd3fc; font-family:monospace; }
  .md hr { border:none; border-top:1px solid #334155; margin:20px 0; }
  .md .tag-row { display:flex; flex-wrap:wrap; gap:6px; margin-top:6px; }
  .md .tag { background:#0f172a; border:1px solid #334155; border-radius:20px; padding:3px 10px; font-size:0.72rem; color:#7dd3fc; font-family:monospace; }
  /* ── Layer toggle ──────────────────────────────────────────────────────────── */
  .layer-toggles { display:flex; gap:5px; align-items:center; }
  .layer-toggles .lbl { font-size:0.68rem; color:#64748b; white-space:nowrap; }
  .btn-layer { background:#0f172a; border:1px solid #334155; color:#94a3b8; border-radius:6px; padding:4px 10px; font-size:0.72rem; cursor:pointer; display:flex; align-items:center; gap:5px; white-space:nowrap; transition:border-color .15s,color .15s; }
  .btn-layer .dot-layer { width:8px; height:8px; border-radius:50%; flex-shrink:0; }
  .btn-layer.active { border-color:currentColor; }
  .btn-layer.snai-btn.active { color:#22c55e; }
  .btn-layer.sll-btn.active  { color:#a78bfa; }
  .btn-layer:hover { border-color:#475569; color:#e2e8f0; }
  /* SLL panel */
  .sll-title { font-size:0.9rem; font-weight:700; color:#f1f5f9; margin-bottom:10px; line-height:1.3; }
  .sll-region { font-size:0.72rem; color:#64748b; margin-bottom:10px; }
  .econ-section { margin-top:10px; }
  .econ-title { font-size:0.62rem; color:#64748b; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:6px; }
  .econ-row { display:flex; justify-content:space-between; padding:4px 0; border-bottom:1px solid #1e293b; font-size:0.75rem; }
  .econ-row .ek { color:#94a3b8; }
  .econ-row .ev { color:#e2e8f0; font-weight:600; }
  .econ-highlight { background:#0f172a; border:1px solid #334155; border-radius:6px; padding:8px; margin-bottom:6px; text-align:center; }
  .econ-highlight .val { font-size:1.2rem; font-weight:800; color:#a78bfa; }
  .econ-highlight .lbl { font-size:0.6rem; color:#64748b; margin-top:2px; text-transform:uppercase; letter-spacing:0.06em; }
  body.light .btn-layer { background:#f1f5f9; border-color:#e2e8f0; color:#64748b; }
  body.light .btn-layer.snai-btn.active { color:#15803d; }
  body.light .btn-layer.sll-btn.active  { color:#7c3aed; }
  body.light .econ-row { border-bottom-color:#f1f5f9; }
  body.light .econ-row .ek { color:#64748b; }
  body.light .econ-row .ev { color:#1e293b; }
  body.light .econ-highlight { background:#f8f0ff; border-color:#ddd6fe; }
  body.light .econ-highlight .val { color:#7c3aed; }
  body.light .econ-highlight .lbl { color:#94a3b8; }
  body.light .sll-title { color:#0f172a; }
  body.light .sll-region { color:#94a3b8; }
</style>
</head>
<body>
<header>
  <div class="logo">
    <h1>Strategia Nazionale Aree Interne — Dashboard SNAI (cicli 2014-2020 e 2021-2027)</h1>
    <p>Fonte: DPCoe · 08_elenco-aree-comuni.xlsx · elenco_aree_snai_14-20-e-21-27.xlsx · ISTAT Mappa AI 2020 · Confini comunali: openpolis/geojson-italy</p>
  </div>
  <button class="btn-theme" id="btnTheme" onclick="toggleTheme()" title="Cambia tema">☀</button>
  <button class="btn-info" onclick="document.getElementById('infoModal').classList.add('open')">ⓘ Note metodologiche</button>
  <div class="kpi-row">
    <div class="kpi teal"><div class="num">128</div><div class="lbl">Aree Totali</div></div>
    <div class="kpi blue"><div class="num">KPI_KNOWN_N+</div><div class="lbl">Comuni SNAI</div></div>
    <div class="kpi green"><div class="num">43</div><div class="lbl">Finanz. 21-27</div></div>
    <div class="kpi lblue"><div class="num">67</div><div class="lbl">Conf. 14-20</div></div>
    <div class="kpi orange"><div class="num">13</div><div class="lbl">Non finanz.</div></div>
    <div class="kpi gray"><div class="num">5</div><div class="lbl">Solo 14-20</div></div>
  </div>
</header>
<div class="main">
  <aside class="sidebar">
    <div class="sidebar-section">
      <h3>Aree per regione</h3>
      <div class="chart-wrap-tall"><canvas id="chartRegioni"></canvas></div>
    </div>
    <div class="sidebar-section">
      <h3>Contesto ISTAT 2020</h3>
      <div class="stat-grid">
        <div class="stat-card"><div class="val">3.834</div><div class="desc">Comuni area interna (D+E+F)</div></div>
        <div class="stat-card"><div class="val">22,7%</div><div class="desc">Popolazione nelle aree interne</div></div>
        <div class="stat-card"><div class="val">58,8%</div><div class="desc">Superficie nazionale coperta</div></div>
        <div class="stat-card"><div class="val">67,4%</div><div class="desc">Comuni AI nel Mezzogiorno</div></div>
      </div>
      <div style="font-size:0.63rem;color:#475569;margin-top:8px;line-height:1.5">Le aree SNAI sono un sottoinsieme finanziato dei 3.834 comuni classificati da ISTAT.<br>Fonte: ISTAT, <em>La geografia delle aree interne nel 2020</em>, 20/07/2022.</div>
    </div>
    <div class="sidebar-section">
      <h3>Cicli a confronto (comuni)</h3>
      <div class="chart-wrap"><canvas id="chartCicli"></canvas></div>
    </div>
  </aside>
  <div class="center-col">
    <div class="filter-bar">
      <div class="layer-toggles">
        <span class="lbl">Layer</span>
        <button class="btn-layer snai-btn active" id="btnLayerSNAI" onclick="toggleLayerSNAI()">
          <span class="dot-layer" style="background:#22c55e"></span>Aree SNAI
        </button>
        <button class="btn-layer sll-btn" id="btnLayerSLL" onclick="toggleLayerSLL()">
          <span class="dot-layer" style="background:#a78bfa"></span>SLL 2021
        </button>
      </div>
      <div style="width:1px;height:20px;background:#334155;margin:0 4px"></div>
      <div class="fg"><label>Regione</label><select id="filtroRegione"><option value="">Tutte</option></select></div>
      <div class="fg"><label>Status</label>
        <select id="filtroFin">
          <option value="">Tutti</option>
          <option value="SI">Finanziate 21-27 (43)</option>
          <option value="CONF">Confermate 14-20 (67)</option>
          <option value="NO">Non finanziate 21-27 (13)</option>
          <option value="1420">Solo ciclo 14-20 (5)</option>
        </select>
      </div>
      <div class="fg"><label>Cerca area</label><input type="text" id="searchArea" placeholder="es. Appennino&#8230;"></div>
      <div class="fg"><label>Cerca comune</label><input type="text" id="searchComune" placeholder="es. Fanano&#8230;"></div>
      <div class="fg sll-filter-group" id="sllFilterGroup" style="display:none">
        <div style="width:1px;height:20px;background:#334155;margin-right:12px"></div>
        <label style="color:#a78bfa">Classe SLL</label>
        <select id="filtroSLLClasse">
          <option value="">Tutte</option>
          <option value="A">A — Made in Italy</option>
          <option value="B">B — Manifatturiero pesante</option>
          <option value="C">C — Non manifatturiero</option>
          <option value="D">D — Non specializzato</option>
        </select>
      </div>
      <button class="btn-reset" onclick="resetFiltri()">&#8635; Azzera</button>
    </div>
    <div id="map"></div>
  </div>
  <div class="right-panel" id="rightPanel"></div>
</div>
<div class="table-panel">
  <div class="table-toggle" onclick="toggleTable()">
    <span id="tableCount">Tutte le 128 aree — clicca per espandere</span>
    <span id="chevron">&#9650;</span>
  </div>
  <div id="tableContent" style="display:none">
    <table>
      <thead><tr><th>Regione</th><th>Area SNAI</th><th>N. Comuni</th><th>Popolazione 2020</th><th>AI 2020</th><th>Status</th></tr></thead>
      <tbody id="tableBody"></tbody>
    </table>
  </div>
</div>

<!-- Info modal -->
<div class="modal-overlay" id="infoModal" onclick="if(event.target===this)this.classList.remove('open')">
  <div class="modal-box md">
    <button class="modal-close" onclick="document.getElementById('infoModal').classList.remove('open')">&#x2715;</button>
    <h2>Dashboard SNAI — Note metodologiche</h2>
    <p>Questa dashboard è stata costruita combinando fonti dati ufficiali DPCoe, elaborazione GIS vettoriale e un database semantico locale per l'analisi documentale.</p>

    <h3>Fonti dati</h3>
    <ul>
      <li><strong>DPCoe — Dipartimento per le Politiche di Coesione</strong>: fogli Excel ufficiali con l'elenco comuni per ciclo SNAI
        <ul>
          <li><code>08_elenco-aree-comuni.xlsx</code>: 1.880 comuni delle aree SI, CONF e NO (ciclo 21-27)</li>
          <li><code>elenco_aree_snai_14-20-e-21-27.xlsx</code>: 85 comuni delle 5 aree solo ciclo 14-20</li>
        </ul>
      </li>
      <li><strong>ISTAT — Mappa Aree Interne 2020</strong>: classificazione comune per comune (polo, cintura, intermedio, periferico, ultraperiferico)</li>
      <li><strong>openpolis/geojson-italy</strong>: confini comunali vettoriali (~30 MB, 7.896 comuni italiani)</li>
    </ul>

    <h3>Elaborazione dati</h3>
    <ul>
      <li><strong>Lettura Excel</strong>: i dati comuni sono stati estratti dai fogli Excel DPCoe via <code>pandas</code>, con rilevamento automatico dell'header e validazione dei codici ISTAT a 6 cifre. I totali (SI=KPI_SI_N, CONF=KPI_CONF_N, NO=KPI_NO_N comuni) sono calcolati direttamente dall'Excel a ogni build, non hardcoded.</li>
      <li><strong>Generazione perimetri GIS</strong>: per ciascuna delle 128 aree SNAI, i confini comunali sono stati dissolti con <code>geopandas</code> (tolerance=0.002°) per ottenere il poligono d'area. Un secondo GeoJSON conserva i perimetri dei 1.967 comuni individuali (tolerance=0.003°) per la navigazione nel dettaglio.</li>
      <li><strong>VectorDB locale</strong>: i documenti SNAI (PDF, DOCX, relazioni di area, rapporti di monitoraggio) sono stati indicizzati in un database vettoriale <code>ChromaDB</code> per ricerca semantica ibrida, usando il modello di embedding <code>paraphrase-multilingual-MiniLM-L12-v2</code> (~115 MB). Il VectorDB permette di interrogare i documenti in linguaggio naturale e recuperare passaggi rilevanti con score di similarità.</li>
    </ul>

    <h3>Dashboard</h3>
    <ul>
      <li>Layout a 3 colonne: sidebar sinistra (grafici + contesto ISTAT), mappa centrale con barra filtri, pannello destro dinamico</li>
      <li>Navigazione gerarchica: <strong>Italia → Regione → Area → Comuni</strong>. Il pannello destro si aggiorna a ogni livello; al click su un'area la mappa zooma e sovrappone i confini dei singoli comuni</li>
      <li>Filtri: regione, status ciclo SNAI, nome area, nome comune (ricerca nei 1.880 comuni indicizzati)</li>
      <li>Dati embedded: GeoJSON aree (645 KB) + GeoJSON comuni (1.845 KB) + metadati comuni (~75 KB) — nessuna dipendenza server, file HTML unico</li>
    </ul>

    <hr>
    <h3>Stack tecnico</h3>
    <div class="tag-row">
      <span class="tag">Python</span><span class="tag">pandas</span><span class="tag">geopandas</span>
      <span class="tag">openpyxl</span><span class="tag">ChromaDB</span><span class="tag">sentence-transformers</span>
      <span class="tag">Leaflet.js</span><span class="tag">Chart.js</span>
    </div>
  </div>
</div>

<script>
// ── DATI ──────────────────────────────────────────────────────────────────────
// AREE_JS_PLACEHOLDER
// COMUNI_JS_PLACEHOLDER
// AREA_INV_JS_PLACEHOLDER

const AREA_META = {};
// Ente capofila per area SNAI — popolare da APQ e rapporti istruttoria DPCoe.
const CAPOFILA = {
  // ── Emilia-Romagna ───────────────────────────────────────────────────────
  "Basso Ferrarese":                         "Comune di Copparo",                      // APQ_Basso-Ferrarese.pdf
  // ── Marche ───────────────────────────────────────────────────────────────
  "Appennino Alto Fermano":                  "Comune di Amandola",                     // rapporto-istruttoria_marche.pdf
  "Monti Azzurri":                           "Unione Montana Potenza Esino Musone",    // rapporto-istruttoria_marche.pdf
  // ── Umbria ───────────────────────────────────────────────────────────────
  "Alta Valle del Tevere":                   "Comune di Gubbio",                       // rapporto-istruttoria_umbria.pdf (verif.)
  // ── P.A. Bolzano ─────────────────────────────────────────────────────────
  "Burgraviato":                             "Comunità Comprensoriale Burgraviato",    // snai-dossier_pa-bolzano.pdf
};
// Nome comune del capofila (per matching con COMUNI_GEO e lista comuni).
const CAPOFILA_COMUNE = {
  "Basso Ferrarese":        "Copparo",
  "Appennino Alto Fermano": "Amandola",
  "Alta Valle del Tevere":  "Gubbio",
};
AREE.forEach(a => { AREA_META[a.area] = a; });

function snaiLabel(dist) {
  if (!dist) return '—';
  const order = ['F','E','D','C','B','A'];
  return order.filter(k => dist[k] > 0).map(k => k+':'+dist[k]).join(' ') || '—';
}
function snaiColor(s) {
  if (s==='F') return '#ef4444';
  if (s==='E') return '#f97316';
  if (s==='D') return '#eab308';
  if (s==='C') return '#38bdf8';
  return '#64748b';
}
function snaiName(s) {
  return {F:'Ultraperiferico',E:'Periferico',D:'Intermedio',C:'Cintura',B:'Polo intercomunale',A:'Polo'}[s] || s;
}
function statusColor(s) {
  if (s==='SI')   return '#22c55e';
  if (s==='CONF') return '#60a5fa';
  if (s==='NO')   return '#f97316';
  return '#94a3b8';
}
function statusLabel(s) {
  if (s==='SI')   return 'Finanziata 21-27';
  if (s==='CONF') return 'Confermata 14-20';
  if (s==='NO')   return 'Non finanziata 21-27';
  return 'Solo ciclo 14-20';
}
function statusBadge(s) {
  if (s==='SI')   return 'si';
  if (s==='CONF') return 'conf';
  if (s==='NO')   return 'no';
  return 's1420';
}

// ── MAPPA ─────────────────────────────────────────────────────────────────────
const map = L.map('map').setView([42.5, 12.5], 6);
let tileLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
  attribution:'&copy; OpenStreetMap &copy; CARTO', subdomains:'abcd', maxZoom:19
}).addTo(map);

function normalizeReg(r) {
  return (r||'').replace(/^Regione\s+/i,'')
    .replace('Emilia Romagna','Emilia-Romagna')
    .replace("Valle d'Aosta/Vallée d'Aoste","Valle d'Aosta")
    .replace('Friuli Venezia Giulia','Friuli-Venezia Giulia')
    .trim();
}

fetch('https://raw.githubusercontent.com/openpolis/geojson-italy/master/geojson/limits_IT_regions.geojson')
  .then(r=>r.json())
  .then(geo=>L.geoJSON(geo,{
    style:{color:'#334155',weight:1,fillColor:'#1e293b',fillOpacity:0.05},
    onEachFeature(feat,layer){
      const nome=normalizeReg(feat.properties.reg_name);
      layer.on('click',()=>{
        document.getElementById('filtroRegione').value=nome;
        applicaFiltri();
        map.fitBounds(layer.getBounds(),{padding:[40,40]});
      });
      layer.on('mouseover',e=>{e.target.setStyle({fillOpacity:0.18,weight:2,color:'#475569'});});
      layer.on('mouseout',e=>{e.target.setStyle({fillOpacity:0.05,weight:1,color:'#334155'});});
    }
  }).addTo(map)).catch(()=>{});

const SNAI_GEO   = SNAI_GEOJSON_PLACEHOLDER;
const COMUNI_GEO = COMUNI_GEO_PLACEHOLDER;
const SLL_GEO    = SLL_GEOJSON_PLACEHOLDER;
let snaiLayer   = null;
let comuniLayer = null;
let sllLayer    = null;
let _showSNAI   = true;
let _showSLL    = false;

function popupHTML(area, status) {
  const m = AREA_META[area] || {};
  const c = statusColor(status);
  const dist = m.snai_dist;
  let snaiRow = '';
  if (dist) {
    snaiRow = `<div class="popup-snai">AI 2020: ${snaiLabel(dist)}<span style="color:#475569"> (F=Ultra E=Peri D=Inter C=Cin)</span></div>`;
  }
  return `<div class="popup-title">${area}</div>
    <div class="popup-row"><span>Regione</span><span>${m.regione||'&mdash;'}</span></div>
    <div class="popup-row"><span>Comuni</span><span>${m.n!=null?m.n:'&mdash;'}</span></div>
    <div class="popup-row"><span>Pop. 2020</span><span>${m.pop?m.pop.toLocaleString('it'):'&mdash;'}</span></div>
    <div class="popup-row"><span>Status</span><span style="color:${c}">${statusLabel(status)}</span></div>${snaiRow}`;
}

// ── SLL LAYER ─────────────────────────────────────────────────────────────────
function fmt(n, dec=0) {
  if (n==null || n===0) return '—';
  return Number(n).toLocaleString('it', {maximumFractionDigits:dec});
}

const SLL_CLASS_COLORS = {A:'#f59e0b', B:'#3b82f6', C:'#10b981', D:'#94a3b8'};
const SLL_CLASS_LABELS = {
  A:'Made in Italy',
  B:'Manifatturiero pesante',
  C:'Non manifatturiero',
  D:'Non specializzato'
};

function sllClassColor(cod) { return SLL_CLASS_COLORS[cod] || '#a78bfa'; }

function buildSLLLayer() {
  if (sllLayer) { map.removeLayer(sllLayer); sllLayer=null; }
  if (!_showSLL) return;
  const _sllClasse = document.getElementById('filtroSLLClasse').value;
  const features = _sllClasse
    ? SLL_GEO.features.filter(f => f.properties.cod_classe === _sllClasse)
    : SLL_GEO.features;
  sllLayer = L.geoJSON({type:'FeatureCollection', features}, {
    style: f => {
      const c = sllClassColor(f.properties.cod_classe);
      return {fillColor:c, fillOpacity:0.13, color:c, weight:1.2, dashArray:'4,5', opacity:0.75};
    },
    onEachFeature(f, layer) {
      const p = f.properties;
      const classLabel = p.cod_classe ? `${p.cod_classe} — ${SLL_CLASS_LABELS[p.cod_classe]||''}` : '—';
      layer.bindTooltip(
        `<div class="ct-name">${p.nome_sll}</div>
         <div class="ct-row"><span>Regione</span><span>${p.regione}</span></div>
         <div class="ct-row"><span>Capoluogo</span><span>${p.capoluogo||'—'}</span></div>
         <div class="ct-row"><span>Specializ.</span><span>${classLabel}</span></div>
         <div class="ct-row"><span>Pop. 2021</span><span>${fmt(p.pop_2021)} ab.</span></div>
         <div class="ct-row"><span>Addetti</span><span>${fmt(p.addetti)}</span></div>
         <div class="ct-row"><span>VA/addetto</span><span>${fmt(p.va_per_addetto,1)} k€</span></div>`,
        {sticky:true, opacity:1, className:'comune-tooltip'}
      );
      layer.on('click', () => showSLLDetail(p));
      layer.on('mouseover', e => {
        const c = sllClassColor(e.target.feature.properties.cod_classe);
        e.target.setStyle({fillOpacity:0.35, weight:2, dashArray:null, opacity:1, color:c});
        e.target.bringToFront();
      });
      layer.on('mouseout', e => { sllLayer.resetStyle(e.target); });
    }
  }).addTo(map);
  if (_showSNAI && snaiLayer) snaiLayer.bringToFront();
  updateSLLLegendCount();
}

function toggleLayerSNAI() {
  _showSNAI = !_showSNAI;
  document.getElementById('btnLayerSNAI').classList.toggle('active', _showSNAI);
  if (_showSNAI) {
    const reg=document.getElementById('filtroRegione').value;
    const fin=document.getElementById('filtroFin').value;
    const q=document.getElementById('searchArea').value.toLowerCase();
    const qc=document.getElementById('searchComune').value.toLowerCase().trim();
    const f=AREE.filter(a=>{
      if (reg && normalizeReg(a.regione)!==normalizeReg(reg)) return false;
      if (fin && a.status!==fin) return false;
      if (q  && !a.area.toLowerCase().includes(q)) return false;
      if (qc && !(COMUNI_BY_AREA[a.area]||[]).some(c=>c.n.toLowerCase().includes(qc))) return false;
      return true;
    });
    buildPolygons(f);
  } else {
    if (snaiLayer) { map.removeLayer(snaiLayer); snaiLayer=null; }
    clearComuniLayer();
  }
}

function toggleLayerSLL() {
  _showSLL = !_showSLL;
  document.getElementById('btnLayerSLL').classList.toggle('active', _showSLL);
  document.getElementById('sllFilterGroup').style.display = _showSLL ? 'flex' : 'none';
  buildSLLLayer();
  if (_showSLL && !_showSNAI) showLegendSLL();
  else if (!_showSLL && !_showSNAI) showLegend();
}

function showSLLDetail(p) {
  map.closePopup();
  const invest = p.valore_aggiunto ? `${fmt(Math.round(p.valore_aggiunto/1000))} M€` : '—';
  const vaAdd  = p.va_per_addetto  ? `${fmt(p.va_per_addetto,1)} k€`  : '—';
  const retDip = p.retrib_per_dip  ? `${fmt(p.retrib_per_dip,1)} k€`  : '—';
  const clColor = sllClassColor(p.cod_classe);
  const specHtml = p.cod_classe ? `
    <div class="econ-section" style="border-color:${clColor}33">
      <div class="econ-title">Specializzazione produttiva — ISTAT 2021</div>
      <div style="display:flex;align-items:center;gap:8px;margin:8px 0">
        <div style="width:12px;height:12px;border-radius:3px;background:${clColor};flex-shrink:0"></div>
        <div>
          <div style="font-size:0.7rem;font-weight:700;color:${clColor}">Classe ${p.cod_classe} — ${SLL_CLASS_LABELS[p.cod_classe]||''}</div>
          <div style="font-size:0.65rem;color:#94a3b8;margin-top:2px">${p.cod_gruppo||''} — ${p.den_gruppo||''}</div>
        </div>
      </div>
    </div>` : '';
  document.getElementById('rightPanel').innerHTML = `
    <div class="rp-header"><h3>SLL 2021</h3></div>
    <div class="sll-title">${p.nome_sll}</div>
    <div class="sll-region">${p.regione} &middot; ${p.ripartizione||''} &middot; Capoluogo: <strong>${p.capoluogo||'—'}</strong></div>
    <div class="s-kpi-row">
      <div class="s-kpi"><span class="val">${fmt(p.pop_2021)}</span><span class="lbl">Pop. 2021</span></div>
      <div class="s-kpi"><span class="val">${fmt(p.n_comuni)}</span><span class="lbl">Comuni</span></div>
    </div>
    <div class="s-kpi-row">
      <div class="s-kpi"><span class="val">${fmt(p.sup_kmq,0)} km²</span><span class="lbl">Superficie</span></div>
      <div class="s-kpi"><span class="val">${fmt(p.unita_locali)}</span><span class="lbl">Unità loc.</span></div>
    </div>
    ${specHtml}
    <div class="econ-section">
      <div class="econ-title">Risultati economici 2023 — fonte ISTAT</div>
      <div class="econ-highlight">
        <div class="val">${vaAdd}</div>
        <div class="lbl">Valore Aggiunto per addetto</div>
      </div>
      <div class="econ-row"><span class="ek">Addetti</span><span class="ev">${fmt(p.addetti)}</span></div>
      <div class="econ-row"><span class="ek">Dipendenti</span><span class="ev">${fmt(p.dipendenti)}</span></div>
      <div class="econ-row"><span class="ek">Valore Aggiunto</span><span class="ev">${invest}</span></div>
      <div class="econ-row"><span class="ek">Retrib./dip.</span><span class="ev">${retDip}</span></div>
    </div>`;
}

function sllVisibleCount() {
  const cl = document.getElementById('filtroSLLClasse').value;
  return cl ? SLL_GEO.features.filter(f => f.properties.cod_classe === cl).length
            : SLL_GEO.features.length;
}

function showLegendSLL() {
  const n = sllVisibleCount();
  const cl = document.getElementById('filtroSLLClasse').value;
  const classRows = Object.entries(SLL_CLASS_LABELS).map(([k,v]) => {
    const cnt = SLL_GEO.features.filter(f => f.properties.cod_classe === k).length;
    const dimmed = cl && cl !== k ? 'opacity:0.35;' : '';
    return `<div class="legend-item" style="${dimmed}"><div class="legend-dot" style="background:${SLL_CLASS_COLORS[k]}"></div><strong>${k}</strong> — ${v} <span style="color:#64748b">(${cnt})</span></div>`;
  }).join('');
  document.getElementById('rightPanel').innerHTML = `
    <div class="rp-header"><h3>Legenda SLL <span id="sllLegendCount" style="font-size:0.75rem;font-weight:400;color:#94a3b8">${n} SLL${cl ? ' — classe '+cl : ''}</span></h3></div>
    <div class="legend">
      ${classRows}
    </div>
    <div style="font-size:0.65rem;color:#475569;margin-top:12px;line-height:1.6">
      Specializzazione produttiva prevalente per SLL secondo la tassonomia ISTAT 2021 (4 classi, 17 gruppi). I SLL sono aggregazioni di comuni definite sulla base dei flussi pendolari casa-lavoro (Censimento 2021).<br><br>
      Clicca su un SLL per i dettagli.<br><br>
      Fonti: ISTAT — <em>Specializzazione produttiva prevalente dei SLL</em>, feb. 2026; <em>Risultati economici delle imprese</em>, Tavola 42, anno 2023.
    </div>`;
}

function updateSLLLegendCount() {
  const el = document.getElementById('sllLegendCount');
  if (!el) return;
  const n = sllVisibleCount();
  const cl = document.getElementById('filtroSLLClasse').value;
  el.textContent = `${n} SLL${cl ? ' — classe '+cl : ''}`;
  // aggiorna opacità righe
  el.closest('.rp-header').parentElement.querySelectorAll('.legend-item').forEach((row, i) => {
    const k = Object.keys(SLL_CLASS_LABELS)[i];
    row.style.opacity = (cl && cl !== k) ? '0.35' : '1';
  });
}

function buildPolygons(aree) {
  if (snaiLayer) { map.removeLayer(snaiLayer); snaiLayer=null; }
  const areaSet = new Set(aree.map(a=>a.area));
  const filtered = {type:'FeatureCollection', features: SNAI_GEO.features.filter(f=>areaSet.has(f.properties.area))};
  const _light = document.body.classList.contains('light');
  snaiLayer = L.geoJSON(filtered, {
    style: f => ({fillColor:statusColor(f.properties.status), fillOpacity:0.52, color:_light?'#94a3b8':'#0f172a', weight:0.8, opacity:1}),
    onEachFeature(f, layer) {
      layer.on('click', () => { showArea(f.properties.area); });
      layer.on('mouseover', e => { e.target.setStyle({fillOpacity:0.8,weight:1.8,color:document.body.classList.contains('light')?'#1e293b':'#f1f5f9'}); e.target.bringToFront(); });
      layer.on('mouseout', e => { snaiLayer.resetStyle(e.target); });
    }
  }).addTo(map);
}
buildPolygons(AREE);

// ── PANNELLO DESTRO ───────────────────────────────────────────────────────────
// Stato navigazione: stack di contesti {level, reg, fin, q, area}
let _navStack = [];

function clearComuniLayer() {
  if (comuniLayer) { map.removeLayer(comuniLayer); comuniLayer = null; }
}

function showLegend() {
  _navStack = [];
  clearComuniLayer();
  document.getElementById('rightPanel').innerHTML = `
    <div class="rp-header"><h3>Legenda</h3></div>
    <div class="legend">
      <div class="legend-item"><div class="legend-dot" style="background:#22c55e"></div>Finanziate 21-27 (43 aree, KPI_SI_N comuni)</div>
      <div class="legend-item"><div class="legend-dot" style="background:#60a5fa"></div>Confermate 14-20 (67 aree, KPI_CONF_N comuni)</div>
      <div class="legend-item"><div class="legend-dot" style="background:#f97316"></div>Non finanziate 21-27 (13 aree, KPI_NO_N comuni)</div>
      <div class="legend-item"><div class="legend-dot" style="background:#94a3b8"></div>Solo ciclo 14-20 — non confermate (5 aree)</div>
      ${_showSLL ? '<div class="legend-item" style="margin-top:6px;padding-top:6px;border-top:1px solid #334155"><div class="legend-dot" style="background:#a78bfa;opacity:.8"></div>Sistemi Locali del Lavoro 2021 (515)</div>' : ''}
      <div style="font-size:0.65rem;color:#475569;margin-top:8px;line-height:1.5">Perimetri esatti da confini comunali ISTAT. Clicca su un'area per vedere i comuni. Clicca su una regione per filtrare e zoomare.</div>
    </div>`;
}

function showRegion(aree, reg, fin, q) {
  clearComuniLayer();
  _navStack = [{level:'region', aree, reg, fin, q}];
  const totalComuni = aree.reduce((s,a)=>(s+(a.n||0)),0);
  const totalPop    = aree.reduce((s,a)=>(s+(a.pop||0)),0);
  const title = reg ? reg : fin==='SI'?'Finanziate 21-27':fin==='CONF'?'Confermate 14-20':fin==='NO'?'Non finanziate 21-27':fin==='1420'?'Solo ciclo 14-20':`"${q}"`;
  const section = reg ? 'Regione' : fin ? 'Status' : 'Ricerca';
  const popStr = totalPop>0 ? `<div class="s-kpi"><span class="val">${(totalPop/1000).toFixed(0)}k</span><span class="lbl">Pop. 2020</span></div>` : '';
  const regStr = !reg ? `<div class="s-kpi"><span class="val">${new Set(aree.map(a=>a.regione)).size}</span><span class="lbl">Regioni</span></div>` : '';
  const extraRow = (popStr||regStr) ? `<div class="s-kpi-row">${popStr}${regStr}</div>` : '';
  const itemsHtml = aree.map(a=>`<div class="list-item clickable" onclick="showArea('${a.area.replace(/'/g,"\\'")}')">
    <div class="i-name" style="color:${statusColor(a.status)}">${a.area}</div>
    <div class="i-meta">${[a.n!=null?a.n+' comuni':null, a.pop?(a.pop/1000).toFixed(0)+'k ab.':null].filter(x=>x).join(' · ')}</div>
  </div>`).join('');
  document.getElementById('rightPanel').innerHTML = `
    <div class="rp-header"><h3>${section}</h3></div>
    <div class="stats-title">${title}</div>
    <div class="s-kpi-row">
      <div class="s-kpi"><span class="val">${aree.length}</span><span class="lbl">Aree</span></div>
      <div class="s-kpi"><span class="val">${totalComuni>0?totalComuni.toLocaleString('it'):'—'}</span><span class="lbl">Comuni</span></div>
    </div>
    ${extraRow}
    <div class="s-section-title">Aree — clicca per i comuni</div>
    <div class="item-list">${itemsHtml}</div>`;
}

function comuneTooltipHTML(c, areaName) {
  const inv = AREA_INV[areaName];
  const rows = [
    c.pop != null ? ['Popolazione', c.pop.toLocaleString('it') + ' ab.'] : null,
    c.km2 != null ? ['Superficie', c.km2.toLocaleString('it') + ' km²'] : null,
    c.min != null ? ['Polo più vicino', c.min + ' min'] : null,
    inv   != null ? ['Investimento area', '€' + (inv/1000000).toLocaleString('it', {maximumFractionDigits:1}) + ' M'] : null,
  ].filter(Boolean);
  return `<div class="ct-name">${c.n}</div>` +
    rows.map(([k,v]) => `<div class="ct-row"><span>${k}</span><span>${v}</span></div>`).join('');
}

function showArea(areaName) {
  map.closePopup();
  clearComuniLayer();
  const areaFeatures = COMUNI_GEO.features.filter(f => f.properties.area === areaName);
  const cfComune = CAPOFILA_COMUNE[areaName];
  const _light = document.body.classList.contains('light');
  const comuni = COMUNI_BY_AREA[areaName] || [];
  const comuniMap = {};
  comuni.forEach(c => { comuniMap[c.n] = c; });

  if (areaFeatures.length > 0) {
    comuniLayer = L.geoJSON({type:'FeatureCollection', features: areaFeatures}, {
      style: f => {
        const isCf = cfComune && f.properties.comune === cfComune;
        if (isCf) return { fillOpacity:0.35, fillColor:'#fbbf24', color:'#fbbf24', weight:2, opacity:0.95 };
        return { fillOpacity:0.04, fillColor:_light?'#475569':'#ffffff', color:_light?'#475569':'#ffffff', weight:0.9, dashArray:'3,5', opacity:0.6 };
      },
      onEachFeature(f, layer) {
        const c = comuniMap[f.properties.comune] || {n: f.properties.comune};
        const isCf = cfComune && f.properties.comune === cfComune;
        layer.bindTooltip(() => comuneTooltipHTML(c, areaName),
          {sticky:true, opacity:1, className:'comune-tooltip'});
        layer.on('mouseover', e => {
          e.target.setStyle(isCf
            ? {fillOpacity:0.6, weight:2.5}
            : {fillOpacity:0.22, weight:1.5, color:_light?'#1e293b':'#e2e8f0', dashArray:null});
          e.target.bringToFront();
        });
        layer.on('mouseout', e => { comuniLayer.resetStyle(e.target); });
      }
    }).addTo(map);
    const bounds = comuniLayer.getBounds();
    map.fitBounds(bounds, {padding:[50,50]});
    const areaStatus = (AREE.find(a => a.area === areaName) || {}).status || '';
    L.popup({closeButton:true, className:'area-popup', maxWidth:230, autoPan:false})
      .setLatLng(L.latLng(bounds.getNorth(), bounds.getCenter().lng))
      .setContent(popupHTML(areaName, areaStatus))
      .openOn(map);
  }

  const m = AREA_META[areaName] || {};
  const totalPop = comuni.reduce((s,c)=>(s+(c.pop||0)),0);
  const dist = m.snai_dist;
  const cf = CAPOFILA[areaName];
  const backBtn = _navStack.length > 0
    ? `<button class="btn-back" onclick="goBack()">&#8592;</button>`
    : '';
  const cfHtml = cf
    ? `<div class="capofila-row"><span class="capofila-lbl">Capofila</span><span class="capofila-val">${cf}</span></div>`
    : '';
  let snaiHtml = '';
  if (dist) {
    const items = ['F','E','D','C'].filter(k=>dist[k]>0)
      .map(k=>`<div class="legend-item"><div class="legend-dot" style="background:${snaiColor(k)}"></div>${snaiName(k)}: ${dist[k]}</div>`)
      .join('');
    snaiHtml = `<div class="s-section-title">Classificazione AI 2020</div><div class="legend" style="margin-bottom:8px">${items}</div>`;
  }
  const sortedComuni = cfComune
    ? [...comuni].sort((a,b) => a.n===cfComune ? -1 : b.n===cfComune ? 1 : 0)
    : comuni;
  const comuniHtml = sortedComuni.length > 0
    ? sortedComuni.map(c => {
        const isCf = cfComune && c.n === cfComune;
        return `<div class="comune-item${isCf?' is-capofila':''}">
        <div class="c-name">${c.n}${isCf?'<span class="capofila-badge">CAPOFILA</span>':''}${c.p?` <span style="color:#475569">(${c.p})</span>`:''}</div>
        <div class="c-meta">${[c.pop?c.pop.toLocaleString('it')+' ab.':null, c.s?snaiName(c.s):null].filter(x=>x).join(' · ')}</div>
      </div>`;
      }).join('')
    : `<div style="font-size:0.7rem;color:#475569;padding:6px 0">Dati comuni non disponibili per questa area.</div>`;
  _navStack.push({level:'area', areaName});
  document.getElementById('rightPanel').innerHTML = `
    <div class="rp-header">${backBtn}<h3>Area</h3></div>
    <div class="stats-title" style="color:${statusColor(m.status||'')}">${areaName}</div>
    <div class="s-kpi-row">
      <div class="s-kpi"><span class="val">${comuni.length>0?comuni.length:(m.n||'—')}</span><span class="lbl">Comuni</span></div>
      <div class="s-kpi"><span class="val">${totalPop>0?(totalPop/1000).toFixed(0)+'k':m.pop?(m.pop/1000).toFixed(0)+'k':'—'}</span><span class="lbl">Pop. 2020</span></div>
    </div>
    ${cfHtml}${snaiHtml}
    <div class="s-section-title">Comuni (${comuni.length>0?comuni.length:(m.n||'?')})</div>
    <div class="item-list">${comuniHtml}</div>`;
}

function goBack() {
  _navStack.pop(); // remove current area level
  if (_navStack.length === 0) {
    const reg=document.getElementById('filtroRegione').value;
    const fin=document.getElementById('filtroFin').value;
    const q=document.getElementById('searchArea').value.toLowerCase();
    if (!reg && !fin && !q) { showLegend(); return; }
    const f=AREE.filter(a=>(!reg||normalizeReg(a.regione)===normalizeReg(reg))&&(!fin||a.status===fin)&&(!q||a.area.toLowerCase().includes(q)));
    showRegion(f, reg, fin, q);
  } else {
    const ctx = _navStack[_navStack.length-1];
    _navStack.pop();
    showRegion(ctx.aree, ctx.reg, ctx.fin, ctx.q);
  }
}

showLegend();

// ── GRAFICI ───────────────────────────────────────────────────────────────────
const regioniConti={};
AREE.forEach(a=>{regioniConti[a.regione]=(regioniConti[a.regione]||0)+1;});
const regSorted=Object.entries(regioniConti).sort((a,b)=>b[1]-a[1]);
new Chart(document.getElementById('chartRegioni'),{type:'bar',data:{
  labels:regSorted.map(([r])=>r.replace('Emilia-Romagna','Em.-Rom.').replace('Friuli-Venezia Giulia','FVG').replace("Valle d'Aosta",'VdA').replace('PA Bolzano','PABz').replace('PA Trento','PATn')),
  datasets:[{data:regSorted.map(([,n])=>n),backgroundColor:regSorted.map(([r])=>{
    const all=AREE.filter(a=>a.regione===r);const si=all.filter(a=>a.status==='SI').length;
    if(si===all.length) return '#22c55e88';if(si===0) return '#60a5fa88';return '#a78bfa88';
  }),borderColor:'#334155',borderWidth:1,borderRadius:3}]
},options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,
  plugins:{legend:{display:false}},
  scales:{x:{ticks:{color:'#64748b',font:{size:8}},grid:{color:'#1e293b'}},y:{ticks:{color:'#94a3b8',font:{size:8}},grid:{display:false}}}}});

new Chart(document.getElementById('chartCicli'),{type:'bar',data:{
  labels:['Finanz.\n21-27','Conf.\n14-20','Non\nfinanz.'],
  datasets:[{label:'N. Comuni',data:[KPI_SI_INT,KPI_CONF_INT,KPI_NO_INT],backgroundColor:['#22c55e88','#60a5fa88','#f9731688'],borderWidth:0,borderRadius:4}]
},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},
  scales:{x:{ticks:{color:'#64748b',font:{size:9}},grid:{display:false}},y:{ticks:{color:'#64748b',font:{size:9}},grid:{color:'#1e293b'}}}}});

// ── FILTRI ────────────────────────────────────────────────────────────────────
const regioni=[...new Set(AREE.map(a=>a.regione))].sort();
const sel=document.getElementById('filtroRegione');
regioni.forEach(r=>{const o=document.createElement('option');o.value=r;o.textContent=r;sel.appendChild(o);});

function applicaFiltri(){
  const reg=document.getElementById('filtroRegione').value;
  const fin=document.getElementById('filtroFin').value;
  const q=document.getElementById('searchArea').value.toLowerCase();
  const qc=document.getElementById('searchComune').value.toLowerCase().trim();
  const f=AREE.filter(a=>{
    if (reg && normalizeReg(a.regione)!==normalizeReg(reg)) return false;
    if (fin && a.status!==fin) return false;
    if (q  && !a.area.toLowerCase().includes(q)) return false;
    if (qc && !(COMUNI_BY_AREA[a.area]||[]).some(c=>c.n.toLowerCase().includes(qc))) return false;
    return true;
  });
  buildPolygons(f); renderTable(f);
  document.getElementById('tableCount').textContent=`${f.length} area${f.length!==1?'e':''} — clicca per espandere`;
  if (!reg && !fin && !q && !qc) { showLegend(); }
  else if (f.length === 1) { showArea(f[0].area); }
  else { showRegion(f, reg, fin, q||qc); }
}
function resetFiltri(){
  ['filtroRegione','filtroFin','searchArea','searchComune','filtroSLLClasse'].forEach(id=>{document.getElementById(id).value='';});
  buildPolygons(AREE); renderTable(AREE); map.setView([42.5,12.5],6);
  document.getElementById('tableCount').textContent='Tutte le 128 aree — clicca per espandere';
  showLegend();
}
['filtroRegione','filtroFin'].forEach(id=>document.getElementById(id).addEventListener('change',applicaFiltri));
document.getElementById('filtroSLLClasse').addEventListener('change', buildSLLLayer);
document.getElementById('searchArea').addEventListener('input',applicaFiltri);
document.getElementById('searchComune').addEventListener('input',applicaFiltri);

// ── TABELLA ───────────────────────────────────────────────────────────────────
function renderTable(aree){
  document.getElementById('tableBody').innerHTML=aree.map(a=>`<tr>
    <td>${a.regione}</td><td>${a.area}</td>
    <td style="text-align:center">${a.n!=null?a.n:'&mdash;'}</td>
    <td style="text-align:right">${a.pop?a.pop.toLocaleString('it'):'&mdash;'}</td>
    <td style="font-size:0.7rem;color:#94a3b8">${snaiLabel(a.snai_dist)}</td>
    <td><span class="badge ${statusBadge(a.status)}">${statusLabel(a.status)}</span></td>
  </tr>`).join('');
}
renderTable(AREE);

let tableOpen=false;
function toggleTable(){tableOpen=!tableOpen;document.getElementById('tableContent').style.display=tableOpen?'block':'none';document.getElementById('chevron').textContent=tableOpen?'▼':'▲';}

// ── TEMA ──────────────────────────────────────────────────────────────────────
function toggleTheme() {
  const isLight = document.body.classList.toggle('light');
  document.getElementById('btnTheme').textContent = isLight ? '🌙' : '☀';
  tileLayer.setUrl(isLight
    ? 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png'
    : 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png');
  localStorage.setItem('snai-theme', isLight ? 'light' : 'dark');
  const reg=document.getElementById('filtroRegione').value;
  const fin=document.getElementById('filtroFin').value;
  const q=document.getElementById('searchArea').value.toLowerCase();
  const f=AREE.filter(a=>(!reg||normalizeReg(a.regione)===normalizeReg(reg))&&(!fin||a.status===fin)&&(!q||a.area.toLowerCase().includes(q)));
  if (_showSNAI) buildPolygons(f);
  if (_showSLL)  buildSLLLayer();
}
if (localStorage.getItem('snai-theme') === 'light') toggleTheme();
</script>
</body>
</html>"""

# ── Inject computed data ───────────────────────────────────────────────────────
def fmt_n(n):
    return f"{n:,}".replace(',', '.')

HTML = HTML.replace('// AREE_JS_PLACEHOLDER', AREE_JS)
HTML = HTML.replace('// COMUNI_JS_PLACEHOLDER', COMUNI_JS)
HTML = HTML.replace('// AREA_INV_JS_PLACEHOLDER', AREA_INV_JS)
HTML = HTML.replace('SNAI_GEOJSON_PLACEHOLDER', geojson_str)
HTML = HTML.replace('COMUNI_GEO_PLACEHOLDER',   comuni_geojson_str)
HTML = HTML.replace('SLL_GEOJSON_PLACEHOLDER',  sll_geojson_str)
HTML = HTML.replace('KPI_KNOWN_N+', fmt_n(known_n) + '+')
HTML = HTML.replace('KPI_SI_INT',   str(si_n))
HTML = HTML.replace('KPI_CONF_INT', str(conf_n))
HTML = HTML.replace('KPI_NO_INT',   str(no_n))
HTML = HTML.replace('KPI_SI_N',   fmt_n(si_n))
HTML = HTML.replace('KPI_CONF_N', fmt_n(conf_n))
HTML = HTML.replace('KPI_NO_N',   fmt_n(no_n))

with open(OUT_HTML, 'w', encoding='utf-8') as f:
    f.write(HTML)

size_kb = os.path.getsize(OUT_HTML) / 1024
print(f"Dashboard generata: {OUT_HTML}")
print(f"Dimensione: {size_kb:.0f} KB")
print(f"Comuni: SI={si_n}, CONF={conf_n}, NO={no_n}, totale noto={known_n}")
print(f"Aree con stats Excel: {len(area_stats)}")
missing = [a['area'] for a in AREE_BASE if a['area'] not in area_stats and a['status'] != '1420']
if missing:
    print(f"ATTENZIONE: aree senza match Excel ({len(missing)}): {missing}")
