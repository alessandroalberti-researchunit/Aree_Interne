"""Ipotesi: il GeoParquet OCPR_LAZIO calcola l'accessibilita usando solo i servizi
interni all'estensione regionale, quindi sottostima i comuni vicini al confine,
per i quali gli ospedali raggiungibili si trovano in Abruzzo, Umbria, Toscana,
Marche, Molise o Campania.

Test: correlazione fra lo scarto (MCP - locale) e la distanza dal confine regionale.
"""
import os
import numpy as np
import geopandas as gpd
import pandas as pd

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PARQUET = os.path.expanduser("~/ILAB_DATA/OCPR_LAZIO/DATA/grid_08_adv.geoparquet")
COL = "sanita_ospedale||traffic__30__total_ospedale"

# valori MCP letti da hex_aggregate_by_comune(LAZIO, ospedali, mean, top_k=400)
MCP = {
    # interni
    "Viterbo": 0.993, "Rieti": 1.057, "Latina": 1.411, "Frosinone": 1.502,
    "Tivoli": 4.671, "Velletri": 2.824, "Ronciglione": 1.851, "Nepi": 1.925,
    "Bracciano": 0.997, "Cerveteri": 3.121, "Anzio": 2.057, "Sabaudia": 1.866,
    "Vetralla": 1.083, "Sutri": 2.644, "Capranica": 1.555, "Monterotondo": 3.972,
    "Palestrina": 3.398, "Zagarolo": 4.867, "Cave": 1.779, "Genazzano": 1.968,
    "Civitavecchia": 1.997, "Tarquinia": 1.990, "Pomezia": 5.532, "Aprilia": 5.669,
    # confinanti con altre regioni
    "Amatrice": 0.0, "Accumoli": 0.0, "Cittareale": 0.0, "Leonessa": 0.0,
    "Borbona": 0.0, "Settefrati": 1.836, "Picinisco": 1.382,
    "San Donato Val di Comino": 1.822, "Alvito": 1.711, "Acquapendente": 1.709,
    "Proceno": 1.796, "Castelforte": 1.900, "Minturno": 1.081, "Filettino": 0.0,
    "Vallepietra": 0.0, "Trevi nel Lazio": 0.336, "Fiamignano": 0.518,
    "Pescorocchiano": 0.644, "Petrella Salto": 0.898, "Collalto Sabino": 0.773,
    "Cassino": 1.629, "Sora": 1.584, "Subiaco": 0.995, "Cervara di Roma": 0.966,
}

print("Carico confini comunali nazionali...", flush=True)
tutti = gpd.read_file(REPO + "/DATA/comuni_italia.geojson")
print("  %d comuni, colonne: %s" % (len(tutti), list(tutti.columns)[:8]))

# individua le colonne nome e regione
col_nome = next(c for c in tutti.columns if c.lower() in ("name", "comune", "nome"))
cand_reg = [c for c in tutti.columns if "reg" in c.lower()]
print("  colonna nome: %s | candidate regione: %s" % (col_nome, cand_reg))

tutti = tutti.to_crs("EPSG:4326")

# Lazio = comuni il cui codice ISTAT inizia per 056..060 (province RM VT RI LT FR)
col_istat = next((c for c in tutti.columns if c.lower() in
                  ("com_istat_code_num", "istat", "pro_com_t", "com_istat_code")), None)
print("  colonna istat: %s" % col_istat)

lazio_prov = {"056", "057", "058", "059", "060"}
def is_lazio(v):
    s = str(v).zfill(6)
    return s[:3] in lazio_prov

lazio = tutti[tutti[col_istat].map(is_lazio)].copy()
print("  comuni del Lazio: %d" % len(lazio))

# confine esterno della regione
regione = lazio.dissolve().geometry.iloc[0]
confine = regione.boundary

# griglia
grid = gpd.read_parquet(PARQUET)
if grid.total_bounds[0] > 1000:
    grid = grid.set_crs("EPSG:32632", allow_override=True).to_crs("EPSG:4326")
else:
    grid = grid.to_crs("EPSG:4326")
g = grid[["geometry", COL]].copy()
g32 = g.to_crs("EPSG:32632")
pts = g32.copy()
pts["geometry"] = g32.geometry.centroid
pts = pts.to_crs("EPSG:4326")

test = lazio[lazio[col_nome].isin(MCP)][[col_nome, "geometry"]].copy()
test = test.rename(columns={col_nome: "comune"})
print("  comuni di test trovati: %d su %d" % (len(test), len(MCP)))

j = gpd.sjoin(pts, test, how="inner", predicate="within")
loc = j.groupby("comune")[COL].mean()

# distanza dal confine regionale, in km, calcolata in metri su UTM32N
test_32 = test.to_crs("EPSG:32632")
confine_32 = gpd.GeoSeries([confine], crs="EPSG:4326").to_crs("EPSG:32632").iloc[0]
test_32["dist_km"] = test_32.geometry.centroid.distance(confine_32) / 1000.0
dist = dict(zip(test_32["comune"], test_32["dist_km"]))

righe = []
for c in sorted(MCP):
    if c not in loc.index or c not in dist:
        continue
    righe.append({"comune": c, "locale": loc[c], "mcp": MCP[c],
                  "scarto": MCP[c] - loc[c], "dist_km": dist[c]})
df = pd.DataFrame(righe).sort_values("dist_km")

print("\n%-26s %8s %8s %8s %9s" % ("comune", "locale", "MCP", "scarto", "dist_km"))
print("-" * 64)
for _, r in df.iterrows():
    print("%-26s %8.3f %8.3f %8.3f %9.1f" % (
        r["comune"], r["locale"], r["mcp"], r["scarto"], r["dist_km"]))

vicini = df[df["dist_km"] <= 10]
lontani = df[df["dist_km"] > 20]
print("\ncomuni entro 10 km dal confine regionale: n=%d, scarto medio %.3f" % (
    len(vicini), vicini["scarto"].mean()))
print("comuni oltre 20 km dal confine regionale: n=%d, scarto medio %.3f" % (
    len(lontani), lontani["scarto"].mean()))

r = df["dist_km"].corr(df["scarto"])
r_abs = df["dist_km"].corr(df["scarto"].abs())
print("\ncorrelazione di Pearson distanza/scarto:          %.3f" % r)
print("correlazione di Pearson distanza/|scarto|:       %.3f" % r_abs)
print("scarto medio complessivo: %.3f su %d comuni" % (df["scarto"].mean(), len(df)))
