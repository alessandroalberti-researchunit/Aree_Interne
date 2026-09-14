"""Individua la causa dello scarto fra GeoParquet locale e MCP hex-intelligence.
Ipotesi testate, per ciascun comune di prova:
  A) media su TUTTE le celle (metodo dello script)          -> gia' noto
  B) media sulle sole celle con valore > 0
  C) media sulle sole celle non nulle (NaN esclusi)
  D) massimo di cella
  E) media pesata sulla popolazione (se colonna disponibile)
"""
import os
import numpy as np
import geopandas as gpd
import pandas as pd

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PARQUET = os.path.expanduser("~/ILAB_DATA/OCPR_LAZIO/DATA/grid_08_adv.geoparquet")
COL = "sanita_ospedale||traffic__30__total_ospedale"

MCP = {"Settefrati": 1.836, "Picinisco": 1.382, "San Donato Val di Comino": 1.822,
       "Alvito": 1.711, "Petrella Salto": 0.898, "Pescorocchiano": 0.644,
       "Fiamignano": 0.518, "Collalto Sabino": 0.773, "Carpineto Romano": 0.623,
       "Subiaco": 0.995, "Cervara di Roma": 0.966, "Amatrice": 0.0}

grid = gpd.read_parquet(PARQUET)
print("celle: %d, colonne totali: %d" % (len(grid), len(grid.columns)))
pop_cols = [c for c in grid.columns if "popolazione" in c.lower() or c.lower().startswith("pop")]
print("possibili colonne popolazione: %s" % pop_cols[:5])
print("NaN nella colonna indicatore: %d" % int(grid[COL].isna().sum()))
print("celle con valore 0: %d" % int((grid[COL] == 0).sum()))
print("celle con valore > 0: %d" % int((grid[COL] > 0).sum()))
print()

if grid.total_bounds[0] > 1000:
    grid = grid.set_crs("EPSG:32632", allow_override=True).to_crs("EPSG:4326")
else:
    grid = grid.to_crs("EPSG:4326")

com = gpd.read_file(REPO + "/geo/comuni-snai-perimetri.geojson").to_crs("EPSG:4326")
com = com[com["comune"].isin(MCP)][["comune", "geometry"]]

keep = ["geometry", COL] + ([pop_cols[0]] if pop_cols else [])
g = grid[keep].copy()
g32 = g.to_crs("EPSG:32632")
pts = g32.copy()
pts["geometry"] = g32.geometry.centroid
pts = pts.to_crs("EPSG:4326")
j = gpd.sjoin(pts, com, how="inner", predicate="within")

print("%-26s %7s %7s %7s %7s %7s %6s %6s" % (
    "comune", "A_tutte", "B_>0", "C_notna", "D_max", "MCP", "n", "n>0"))
print("-" * 82)
righe = []
for c in sorted(MCP):
    sub = j[j["comune"] == c][COL]
    if len(sub) == 0:
        continue
    a = sub.mean()
    pos = sub[sub > 0]
    b = pos.mean() if len(pos) else 0.0
    cc = sub.dropna().mean()
    d = sub.max()
    righe.append((c, a, b, cc, d, MCP[c], len(sub), len(pos)))
    print("%-26s %7.3f %7.3f %7.3f %7.3f %7.3f %6d %6d" % (
        c, a, b, cc, d, MCP[c], len(sub), len(pos)))

print()
for nome, idx in [("A media su tutte", 1), ("B media su >0", 2),
                  ("C media non-NaN", 3), ("D massimo", 4)]:
    errs = [abs(r[idx] - r[5]) for r in righe]
    entro = sum(1 for e in errs if e <= 0.02)
    print("%-18s  scarto medio %.4f, max %.4f, entro 0.02: %d/%d" % (
        nome, float(np.mean(errs)), float(np.max(errs)), entro, len(errs)))
