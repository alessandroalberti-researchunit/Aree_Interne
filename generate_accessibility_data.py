"""
Genera DATA/accessibility_data.json con dati di accessibilita ai servizi per:
  - singoli comuni SNAI (chiave: procom a 6 cifre)
  - SLL 2021 (chiave: cod_sll)

Indicatori (auto con traffico, soglia 30 min):
  ospedali   -> sanita_ospedale||traffic__30__total_ospedale
  sanita     -> ovm_places_sanita||traffic__30__total_sanita
  istruzione -> ovm_places_istruzione||traffic__30__total_istruzione
  trasporti  -> ovm_infr_infrastrutture||traffic__30__total_infrastrutture
  sport      -> ovm_places_sport||traffic__30__total_sport
  cultura    -> ovm_places_cultura||traffic__30__total_cultura

Copertura: regioni con GeoParquet disponibile in ILAB_DATA_ROOT.
"""

import geopandas as gpd
import pandas as pd
import numpy as np
import json
import os

ILAB_DATA_ROOT = os.path.expanduser("~/ILAB_DATA")

OCPR_REGIONS = {
    "Lazio":     "OCPR_LAZIO",
    "Calabria":  "OCPR_CALABRIA",
    "Puglia":    "OCPR_PUGLIA",
    "Sardegna":  "OCPR_SARDEGNA",
    "Lombardia": "OCPR_LOMBARDIA",
    "Piemonte":  "OCPR_PIEMONTE",
    "Liguria":   "OCPR_LIGURIA",
}

INDICATORS = {
    "ospedali":   "sanita_ospedale||traffic__30__total_ospedale",
    "sanita":     "ovm_places_sanita||traffic__30__total_sanita",
    "istruzione": "ovm_places_istruzione||traffic__30__total_istruzione",
    "trasporti":  "ovm_infr_infrastrutture||traffic__30__total_infrastrutture",
    "sport":      "ovm_places_sport||traffic__30__total_sport",
    "cultura":    "ovm_places_cultura||traffic__30__total_cultura",
}

IND_LABELS = {
    "ospedali":   "Ospedali SSN",
    "sanita":     "Servizi sanitari",
    "istruzione": "Strutture educative",
    "trasporti":  "Trasporti",
    "sport":      "Sport",
    "cultura":    "Cultura",
}

COMUNI_GEOJSON = "comuni-snai-perimetri.geojson"
SLL_GEOJSON    = "sll-perimetri.geojson"
OUT_JSON       = "DATA/accessibility_data.json"

# ── Carica poligoni target ────────────────────────────────────────────────────
print("Carico comuni SNAI...", flush=True)
comuni_snai = gpd.read_file(COMUNI_GEOJSON)
comuni_snai = comuni_snai.to_crs("EPSG:4326")
print(f"  {len(comuni_snai)} comuni, colonne: {list(comuni_snai.columns)}")

print("Carico SLL...", flush=True)
sll = gpd.read_file(SLL_GEOJSON)
sll = sll.to_crs("EPSG:4326")

# ── Aggregazione H3 → poligoni ────────────────────────────────────────────────
comuni_results = {}   # {procom: {ind_key: val, ...}}
sll_results    = {}   # {cod_sll: {ind_key: val, ...}}
covered_regions = []

for reg_name, folder in OCPR_REGIONS.items():
    parquet_path = os.path.join(ILAB_DATA_ROOT, folder, "DATA", "grid_08_adv.geoparquet")
    if not os.path.exists(parquet_path):
        print(f"  [{reg_name}] GeoParquet non trovato - salto", flush=True)
        continue

    print(f"\n[{reg_name}] Carico GeoParquet...", flush=True)
    grid = gpd.read_parquet(parquet_path)

    if grid.total_bounds[0] > 1000:
        grid = grid.set_crs("EPSG:32632", allow_override=True).to_crs("EPSG:4326")
    else:
        grid = grid.to_crs("EPSG:4326")

    print(f"  {len(grid)} celle H3", flush=True)

    avail = {k: v for k, v in INDICATORS.items() if v in grid.columns}
    if not avail:
        print(f"  Nessun indicatore trovato - salto", flush=True)
        continue

    covered_regions.append(reg_name)
    ind_cols = list(avail.values())

    # Centroidi H3 in UTM (accurati), poi riproietta in WGS84 per il join
    grid_sub = grid[["geometry"] + ind_cols].copy()
    grid_32  = grid_sub.to_crs("EPSG:32632")
    grid_pts = grid_32.copy()
    grid_pts["geometry"] = grid_32.geometry.centroid
    grid_pts = grid_pts.to_crs("EPSG:4326")

    # ── Join comuni ───────────────────────────────────────────────────────────
    print(f"  Spatial join comuni...", flush=True)
    com_join = gpd.sjoin(grid_pts, comuni_snai[["procom", "geometry"]], how="inner", predicate="within")
    if len(com_join) > 0:
        agg = com_join.groupby("procom")[ind_cols].mean().round(2)
        for procom, row in agg.iterrows():
            d = {k: float(row[v]) for k, v in avail.items() if pd.notna(row[v])}
            comuni_results[str(procom)] = d
        print(f"  -> {len(agg)} comuni coperti", flush=True)

    # ── Join SLL ──────────────────────────────────────────────────────────────
    print(f"  Spatial join SLL...", flush=True)
    sll_join = gpd.sjoin(grid_pts, sll[["cod_sll", "geometry"]], how="inner", predicate="within")
    if len(sll_join) > 0:
        agg_sll = sll_join.groupby("cod_sll")[ind_cols].mean().round(2)
        for cod, row in agg_sll.iterrows():
            d = {k: float(row[v]) for k, v in avail.items() if pd.notna(row[v])}
            sll_results[str(cod)] = d
        print(f"  -> {len(agg_sll)} SLL coperti", flush=True)

# ── Soglie di severita (basate su distribuzione dei comuni coperti) ───────────
all_com_vals = {}
for d in comuni_results.values():
    for k, v in d.items():
        all_com_vals.setdefault(k, []).append(v)

thresholds = {}
for k, vs in all_com_vals.items():
    arr = np.array(vs)
    thresholds[k] = {
        "p33": round(float(np.percentile(arr, 33)), 2),
        "p67": round(float(np.percentile(arr, 67)), 2),
        "mean": round(float(arr.mean()), 2),
    }

# ── Statistiche per indicatore (max utile per normalizzazione SLL) ───────────
all_vals = {}
for d in list(comuni_results.values()) + list(sll_results.values()):
    for k, v in d.items():
        all_vals.setdefault(k, []).append(v)

ind_stats = {}
for k, vs in all_vals.items():
    arr = np.array(vs)
    ind_stats[k] = {
        "label": IND_LABELS[k],
        "max":   round(float(arr.max()), 2),
        "mean":  round(float(arr.mean()), 2),
    }

# ── Output ────────────────────────────────────────────────────────────────────
os.makedirs("DATA", exist_ok=True)

output = {
    "fonte": "OvertureMaps + Ministero della Salute, isocrone Valhalla 30 min auto. Elaborazione IZI.",
    "note": "Media di strutture raggiungibili per cella H3 r8 (~0.7 km2) intersecante ciascun comune/SLL.",
    "regioni_coperte": covered_regions,
    "indicatori": ind_stats,
    "soglie": thresholds,
    "comuni": comuni_results,
    "sll":    sll_results,
}

with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

size_kb = os.path.getsize(OUT_JSON) / 1024
print(f"\nFile generato: {OUT_JSON} ({size_kb:.0f} KB)")
print(f"Comuni: {len(comuni_results)}, SLL: {len(sll_results)}")
print(f"Regioni: {covered_regions}")

if thresholds:
    print("\nSoglie severita (p33/p67):")
    for k, t in thresholds.items():
        print(f"  {k}: critico <{t['p33']}, limitato <{t['p67']}, ok >={t['p67']}")
