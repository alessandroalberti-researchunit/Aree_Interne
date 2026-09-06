"""Perche' MCP e GeoParquet danno valori diversi?
Ricalcola la media di traffic__30__total_ospedale per alcuni comuni SNAI del Lazio
con due geometrie di join: centroide-dentro (metodo dello script) e intersezione.
"""
import json, os
import geopandas as gpd

REPO = r"C:/Users/aalbe/Desktop/Code/Aree Interne Italia"
PARQUET = os.path.expanduser("~/ILAB_DATA/OCPR_LAZIO/DATA/grid_08_adv.geoparquet")
COL = "sanita_ospedale||traffic__30__total_ospedale"

TEST = ["Settefrati", "Picinisco", "San Donato Val di Comino", "Alvito",
        "Petrella Salto", "Pescorocchiano", "Fiamignano", "Collalto Sabino",
        "Carpineto Romano", "Subiaco", "Cervara di Roma", "Amatrice"]

MCP = {"Settefrati": 1.8361, "Picinisco": 1.3819, "San Donato Val di Comino": 1.8218,
       "Alvito": 1.7108, "Petrella Salto": 0.8980, "Pescorocchiano": 0.6440,
       "Fiamignano": 0.5181, "Collalto Sabino": 0.7732, "Carpineto Romano": 0.6226,
       "Subiaco": 0.9950, "Cervara di Roma": 0.9660, "Amatrice": 0.0}

grid = gpd.read_parquet(PARQUET)
print("celle nel parquet: %d" % len(grid))
print("colonna presente: %s" % (COL in grid.columns))
if grid.total_bounds[0] > 1000:
    grid = grid.set_crs("EPSG:32632", allow_override=True).to_crs("EPSG:4326")
else:
    grid = grid.to_crs("EPSG:4326")

com = gpd.read_file(REPO + "/comuni-snai-perimetri.geojson").to_crs("EPSG:4326")
com = com[com["comune"].isin(TEST)][["comune", "procom", "geometry"]]
print("comuni di test trovati: %d\n" % len(com))

g = grid[["geometry", COL]].copy()
g32 = g.to_crs("EPSG:32632")
pts = g32.copy()
pts["geometry"] = g32.geometry.centroid
pts = pts.to_crs("EPSG:4326")

j_cent = gpd.sjoin(pts, com, how="inner", predicate="within")
j_int = gpd.sjoin(g, com, how="inner", predicate="intersects")

m_cent = j_cent.groupby("comune")[COL].agg(["mean", "count"])
m_int = j_int.groupby("comune")[COL].agg(["mean", "count"])

acc = json.load(open(REPO + "/DATA/accessibility_data.json", encoding="utf-8"))["comuni"]
proc = dict(zip(com["comune"], com["procom"]))

print("%-26s %8s %6s %8s %6s %8s %8s" % (
    "comune", "centroid", "n", "interse.", "n", "json", "MCP"))
print("-" * 78)
for c in sorted(TEST):
    mc = m_cent["mean"].get(c)
    nc = m_cent["count"].get(c)
    mi = m_int["mean"].get(c)
    ni = m_int["count"].get(c)
    jv = acc.get(proc.get(c, ""), {}).get("ospedali")
    print("%-26s %8s %6s %8s %6s %8s %8s" % (
        c,
        "%.3f" % mc if mc is not None else "-",
        int(nc) if nc is not None else "-",
        "%.3f" % mi if mi is not None else "-",
        int(ni) if ni is not None else "-",
        "%.2f" % jv if jv is not None else "-",
        "%.3f" % MCP[c]))
