"""Ipotesi: hex_aggregate_by_comune aggrega a risoluzione H3 piu' grossolana di r8.
Il server dichiara r6/r7/r8; il parquet locale e' r8.

Per ogni comune di prova si calcola la media comunale a r8 (baseline = valore locale),
poi risalendo ai genitori r7 e r6, con valore del genitore = media o somma dei figli.
"""
import os
import numpy as np
import geopandas as gpd
import pandas as pd
import h3

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PARQUET = os.path.expanduser("~/ILAB_DATA/OCPR_LAZIO/DATA/grid_08_adv.geoparquet")
COL = "sanita_ospedale||traffic__30__total_ospedale"

MCP = {"Settefrati": 1.836, "Picinisco": 1.382, "San Donato Val di Comino": 1.822,
       "Alvito": 1.711, "Petrella Salto": 0.898, "Pescorocchiano": 0.644,
       "Fiamignano": 0.518, "Collalto Sabino": 0.773, "Carpineto Romano": 0.623,
       "Subiaco": 0.995, "Cervara di Roma": 0.966, "Amatrice": 0.000,
       "Sutri": 2.644, "Capranica": 1.555, "Tivoli": 4.671, "Ronciglione": 1.851,
       "Nepi": 1.925, "Viterbo": 0.993, "Rieti": 1.057, "Latina": 1.411}

print("h3 %s" % h3.__version__)
grid = gpd.read_parquet(PARQUET)
if grid.total_bounds[0] > 1000:
    grid = grid.set_crs("EPSG:32632", allow_override=True).to_crs("EPSG:4326")
else:
    grid = grid.to_crs("EPSG:4326")

# parent cells
def parent(c, res):
    try:
        return h3.cell_to_parent(c, res)
    except AttributeError:
        return h3.h3_to_parent(c, res)

grid["h3_07"] = [parent(c, 7) for c in grid["h3_08"]]
grid["h3_06"] = [parent(c, 6) for c in grid["h3_08"]]
print("celle r8 %d, genitori r7 distinti %d, r6 distinti %d" % (
    len(grid), grid["h3_07"].nunique(), grid["h3_06"].nunique()))

# valore del genitore: media e somma dei figli presenti
p7_mean = grid.groupby("h3_07")[COL].mean()
p7_sum = grid.groupby("h3_07")[COL].sum()
p6_mean = grid.groupby("h3_06")[COL].mean()
p6_sum = grid.groupby("h3_06")[COL].sum()

# assegna le celle r8 ai comuni per centroide
com = gpd.read_file(REPO + "/DATA/comuni_italia.geojson").to_crs("EPSG:4326")
col_nome = next(c for c in com.columns if c.lower() in ("name", "comune", "nome"))
com = com.rename(columns={col_nome: "comune"})
com = com[com["comune"].isin(MCP)][["comune", "geometry"]]

g32 = grid[["geometry", COL, "h3_08", "h3_07", "h3_06"]].to_crs("EPSG:32632")
pts = g32.copy()
pts["geometry"] = g32.geometry.centroid
pts = pts.to_crs("EPSG:4326")
j = gpd.sjoin(pts, com, how="inner", predicate="within")
print("comuni di test agganciati: %d\n" % j["comune"].nunique())

righe = []
for c in sorted(MCP):
    sub = j[j["comune"] == c]
    if len(sub) == 0:
        continue
    r8 = sub[COL].mean()
    u7 = sub["h3_07"].unique()
    u6 = sub["h3_06"].unique()
    righe.append({
        "comune": c,
        "r8": r8,
        "r7_med": p7_mean.reindex(u7).mean(),
        "r7_som": p7_sum.reindex(u7).mean(),
        "r6_med": p6_mean.reindex(u6).mean(),
        "r6_som": p6_sum.reindex(u6).mean(),
        "MCP": MCP[c],
        "n7": len(u7), "n6": len(u6),
    })
df = pd.DataFrame(righe)

print("%-26s %7s %7s %7s %7s %7s %7s %4s %4s" % (
    "comune", "r8", "r7_med", "r7_som", "r6_med", "r6_som", "MCP", "n7", "n6"))
print("-" * 92)
for _, r in df.iterrows():
    print("%-26s %7.3f %7.3f %7.3f %7.3f %7.3f %7.3f %4d %4d" % (
        r["comune"], r["r8"], r["r7_med"], r["r7_som"], r["r6_med"], r["r6_som"],
        r["MCP"], r["n7"], r["n6"]))

print()
for nome in ["r8", "r7_med", "r7_som", "r6_med", "r6_som"]:
    e = (df[nome] - df["MCP"]).abs()
    entro = int((e <= 0.02).sum())
    print("%-8s scarto medio %7.3f  max %7.3f  entro 0.02: %2d/%d" % (
        nome, e.mean(), e.max(), entro, len(df)))
