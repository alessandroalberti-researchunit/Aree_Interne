"""
Genera DATA/accessibility_data.json con punteggi medi di accessibilità ai servizi
per aree SNAI e SLL, a partire dai GeoParquet H3 OCPR.

Copertura: solo le regioni con GeoParquet disponibile in ILAB_DATA_ROOT.
Aree/SLL fuori copertura non compaiono nel JSON (la dashboard li omette silenziosamente).

Indicatori selezionati (traffico, 30 min — soglia rilevante per aree interne):
  ospedali   -> sanita_ospedale||traffic__30__total_ospedale
  sanita     -> ovm_places_sanita||traffic__30__total_sanita
  istruzione -> ovm_places_istruzione||traffic__30__total_istruzione
  trasporti  -> ovm_infr_infrastrutture||traffic__30__total_infrastrutture
  sport      -> ovm_places_sport||traffic__30__total_sport
  cultura    -> ovm_places_cultura||traffic__30__total_cultura
"""

import geopandas as gpd
import pandas as pd
import json
import os

# ── Config ────────────────────────────────────────────────────────────────────
ILAB_DATA_ROOT = os.path.expanduser("~/ILAB_DATA")

# Regioni OCPR disponibili -> nome cartella
OCPR_REGIONS = {
    "Lazio":      "OCPR_LAZIO",
    "Calabria":   "OCPR_CALABRIA",
    "Puglia":     "OCPR_PUGLIA",
    "Sardegna":   "OCPR_SARDEGNA",
    "Lombardia":  "OCPR_LOMBARDIA",
    "Piemonte":   "OCPR_PIEMONTE",
    "Liguria":    "OCPR_LIGURIA",
}

INDICATORS = {
    "ospedali":   "sanita_ospedale||traffic__30__total_ospedale",
    "sanita":     "ovm_places_sanita||traffic__30__total_sanita",
    "istruzione": "ovm_places_istruzione||traffic__30__total_istruzione",
    "trasporti":  "ovm_infr_infrastrutture||traffic__30__total_infrastrutture",
    "sport":      "ovm_places_sport||traffic__30__total_sport",
    "cultura":    "ovm_places_cultura||traffic__30__total_cultura",
}

SNAI_GEOJSON  = "aree-snai-perimetri.geojson"
SLL_GEOJSON   = "sll-perimetri.geojson"
OUT_JSON      = "DATA/accessibility_data.json"

# ── Carica poligoni target ────────────────────────────────────────────────────
print("Carico poligoni SNAI...", flush=True)
snai = gpd.read_file(SNAI_GEOJSON)
snai = snai.to_crs("EPSG:4326")
snai_key = "area"
snai_reg_col = "regione"

print("Carico poligoni SLL...", flush=True)
sll = gpd.read_file(SLL_GEOJSON)
sll = sll.to_crs("EPSG:4326")
sll_key = "cod_sll"
sll_reg_col = "regione"

# Mappa regione SNAI -> nome OCPR (normalizzazione)
REG_NORMALIZE = {
    "Valle d'Aosta": "Valle d'Aosta",
    "Trentino-Alto Adige": "Trentino-Alto Adige",
    "Friuli-Venezia Giulia": "Friuli-Venezia Giulia",
}

def normalize_reg(r):
    if not isinstance(r, str): return ""
    r = r.strip()
    # Rimuovi caratteri speciali da encoding
    r = r.encode("ascii", "ignore").decode()
    return r

# ── Aggregazione H3 -> poligoni ────────────────────────────────────────────────
snai_results = {}  # {area_name: {ind_key: mean_val, ...}}
sll_results  = {}  # {cod_sll:   {ind_key: mean_val, ...}}
covered_regions = []

for reg_name, folder in OCPR_REGIONS.items():
    parquet_path = os.path.join(ILAB_DATA_ROOT, folder, "DATA", "grid_08_adv.geoparquet")
    if not os.path.exists(parquet_path):
        print(f"  [{reg_name}] GeoParquet non trovato — salto", flush=True)
        continue

    print(f"\n[{reg_name}] Carico GeoParquet...", flush=True)
    grid = gpd.read_parquet(parquet_path)

    # Il parquet è in UTM 32N nonostante il CRS dica 4326 — riproietta
    if grid.total_bounds[0] > 1000:  # coordinate in metri
        grid = grid.set_crs("EPSG:32632", allow_override=True).to_crs("EPSG:4326")
    else:
        grid = grid.to_crs("EPSG:4326")

    print(f"  {len(grid)} celle H3, CRS: {grid.crs}", flush=True)

    # Controlla quali indicatori sono disponibili
    avail = {k: v for k, v in INDICATORS.items() if v in grid.columns}
    missing = set(INDICATORS.keys()) - set(avail.keys())
    if missing:
        print(f"  Indicatori mancanti: {missing}", flush=True)
    if not avail:
        print(f"  Nessun indicatore trovato — salto", flush=True)
        continue

    covered_regions.append(reg_name)
    ind_cols = list(avail.values())

    # ── SNAI: filtra aree nella regione corrente ──────────────────────────────
    # Usa spatial join — include aree che intersecano la griglia
    print(f"  Spatial join SNAI...", flush=True)
    grid_sub = grid[["geometry"] + ind_cols].copy()

    # Centroidi H3 per join più veloce (evita edge effects)
    grid_pts = grid_sub.copy()
    grid_32 = grid_sub.to_crs("EPSG:32632")
    grid_pts = grid_32.copy()
    grid_pts["geometry"] = grid_32.geometry.centroid
    grid_pts = grid_pts.to_crs("EPSG:4326")

    snai_join = gpd.sjoin(grid_pts, snai[[snai_key, "geometry"]], how="inner", predicate="within")
    if len(snai_join) > 0:
        agg = snai_join.groupby(snai_key)[ind_cols].mean().round(2)
        for area_name, row in agg.iterrows():
            d = {k: float(row[v]) for k, v in avail.items() if v in row.index and pd.notna(row[v])}
            snai_results[area_name] = d
        print(f"  -> {len(agg)} aree SNAI coperte", flush=True)

    # ── SLL: stesso approccio ─────────────────────────────────────────────────
    print(f"  Spatial join SLL...", flush=True)
    sll_join = gpd.sjoin(grid_pts, sll[[sll_key, "geometry"]], how="inner", predicate="within")
    if len(sll_join) > 0:
        agg_sll = sll_join.groupby(sll_key)[ind_cols].mean().round(2)
        for cod, row in agg_sll.iterrows():
            d = {k: float(row[v]) for k, v in avail.items() if v in row.index and pd.notna(row[v])}
            sll_results[str(cod)] = d
        print(f"  -> {len(agg_sll)} SLL coperti", flush=True)

# ── Output ────────────────────────────────────────────────────────────────────
os.makedirs("DATA", exist_ok=True)

IND_LABELS = {
    "ospedali":   "Ospedali SSN",
    "sanita":     "Servizi sanitari",
    "istruzione": "Strutture educative",
    "trasporti":  "Infrastrutture trasporto",
    "sport":      "Strutture sportive",
    "cultura":    "Luoghi culturali",
}

# Calcola max per normalizzazione (tra aree SNAI e SLL insieme)
all_vals = {}
for d in list(snai_results.values()) + list(sll_results.values()):
    for k, v in d.items():
        all_vals.setdefault(k, []).append(v)

ind_stats = {
    k: {"label": IND_LABELS[k], "max": round(max(vs), 2), "mean": round(sum(vs)/len(vs), 2)}
    for k, vs in all_vals.items()
}

output = {
    "fonte": "OvertureMaps + Ministero della Salute, isocrone Valhalla. Elaborazione IZI su dati OCPR.",
    "note": "Valori medi per celle H3 r8 (~0.7 km2) che intersecano ciascuna area/SLL. Modalita: auto con traffico, soglia 30 minuti.",
    "regioni_coperte": covered_regions,
    "indicatori": ind_stats,
    "snai": snai_results,
    "sll":  sll_results,
}

with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

size_kb = os.path.getsize(OUT_JSON) / 1024
print(f"\nFile generato: {OUT_JSON} ({size_kb:.0f} KB)")
print(f"Regioni coperte: {covered_regions}")
print(f"Aree SNAI: {len(snai_results)}")
print(f"SLL: {len(sll_results)}")

if snai_results:
    example_area = next(iter(snai_results))
    print(f"\nEsempio — {example_area}:")
    for k, v in snai_results[example_area].items():
        print(f"  {k}: {v}")
