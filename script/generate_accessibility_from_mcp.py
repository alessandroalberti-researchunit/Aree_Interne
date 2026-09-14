"""Costruisce DATA/accessibility_data.json dai file regionali MCP.

Input:
  - DATA/mcp_accessibilita/*.json      valori per comune SNAI, per regione MCP
  - script/diagnostica/comuni_snai_index.json   mappa (regione, comune) -> procom
  - geo/comuni-snai-perimetri.geojson   geometrie per pesare l'aggregazione SLL
  - DATA/sll_2021/Sistemi Locali del Lavoro (SLL) 2021 ... .json  mappa procom -> cod_sll

Output:
  - DATA/accessibility_data.json

Aggregazione SLL: i valori MCP sono medie per cella H3 r8 (celle di area costante),
quindi la media sulle celle di un SLL equivale alla media dei valori comunali pesata
per la superficie del comune. Il peso usato è la superficie della geometria comunale
riproiettata in EPSG:3035 (equal-area). ATTENZIONE: sono disponibili solo i comuni
SNAI, quindi il valore SLL descrive la sola porzione SNAI del sistema locale; il
numero di comuni usati e la quota di superficie coperta sono riportati nel file.
"""
import glob
import json
import os
import statistics

import geopandas as gpd

# Radice del repo, calcolata da __file__: gli script funzionano da qualsiasi cwd.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = lambda *p: os.path.join(ROOT, *p)

MCP_DIR = R('DATA', 'mcp_accessibilita')
IDX_PATH = R('script', 'diagnostica', 'comuni_snai_index.json')
COMUNI_GEO = R('geo', 'comuni-snai-perimetri.geojson')
SLL_GEO = R('geo', 'sll-perimetri.geojson')
OUT_PATH = R('DATA', 'accessibility_data.json')
ORDINE = ["ospedali", "sanita", "istruzione", "trasporti", "sport", "cultura"]
LABEL = {
    "ospedali": "Ospedali SSN",
    "sanita": "Servizi sanitari",
    "istruzione": "Strutture educative",
    "trasporti": "Trasporti",
    "sport": "Sport",
    "cultura": "Cultura",
}


def percentile(sorted_vals, q):
    """Percentile con interpolazione lineare, su lista gia ordinata."""
    if not sorted_vals:
        return None
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    pos = q * (len(sorted_vals) - 1)
    lo = int(pos)
    hi = min(lo + 1, len(sorted_vals) - 1)
    frac = pos - lo
    return sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac


# ── 1. indice comuni SNAI ─────────────────────────────────────────────────────
idx = json.load(open(IDX_PATH, encoding="utf-8"))
key2procom = {(x["regione"], x["comune"]): x["procom"] for x in idx}
assert len(key2procom) == len(idx), "chiavi (regione, comune) non univoche"

# ── 2. merge dei file regionali ───────────────────────────────────────────────
comuni = {}
regioni_coperte = set()
files = sorted(glob.glob(os.path.join(MCP_DIR, "*.json")))
for f in files:
    d = json.load(open(f, encoding="utf-8"))
    assert d["_ordine"] == ORDINE, f"ordine indicatori inatteso in {f}"
    regs = d["_regioni_progetto"]
    for nome, vals in d["valori"].items():
        procom = None
        for r in regs:
            if (r, nome) in key2procom:
                procom = key2procom[(r, nome)]
                regioni_coperte.add(r)
                break
        assert procom, f"{nome} ({regs}) non trovato nell'indice SNAI"
        assert procom not in comuni, f"procom {procom} ({nome}) duplicato"
        comuni[procom] = {k: round(v, 2) for k, v in zip(ORDINE, vals)}

print(f"comuni coperti: {len(comuni)} su {len(idx)} "
      f"({100 * len(comuni) / len(idx):.1f}%)")
non_coperte = sorted({x["regione"] for x in idx} - regioni_coperte)
print(f"regioni non coperte: {non_coperte}")

# ── 3. soglie e metadati indicatori ───────────────────────────────────────────
soglie, indicatori = {}, {}
for k in ORDINE:
    vals = sorted(c[k] for c in comuni.values())
    soglie[k] = {
        "p33": round(percentile(vals, 0.33), 2),
        "p67": round(percentile(vals, 0.67), 2),
        "mean": round(statistics.fmean(vals), 2),
    }
    indicatori[k] = {
        "label": LABEL[k],
        "max": round(vals[-1], 2),
        "mean": round(statistics.fmean(vals), 2),
    }

# ── 4. superfici comunali (pesi) ──────────────────────────────────────────────
gdf = gpd.read_file(COMUNI_GEO)
gdf = gdf.to_crs(3035)
gdf["kmq"] = gdf.geometry.area / 1e6
peso = dict(zip(gdf["procom"], gdf["kmq"]))

# ── 5. mappa procom -> SLL ────────────────────────────────────────────────────
comp_file = glob.glob(R("DATA", "sll_2021", "Sistemi Locali del Lavoro (SLL) 2021*.json"))[0]
comp = json.load(open(comp_file, encoding="utf-8"))["resultset"]
procom2sll = {r["PRO_COM_T"]: r["COD_SLL"] for r in comp}
# superficie e numero comuni totali dell'SLL (denominatori della copertura),
# dalle proprieta ISTAT del geojson SLL
sll_props = {
    f["properties"]["cod_sll"]: f["properties"]
    for f in json.load(open(SLL_GEO, encoding="utf-8"))["features"]
}

# ── 6. aggregazione SLL ───────────────────────────────────────────────────────
acc_sll, meta_sll = {}, {}
buckets = {}
for procom, vals in comuni.items():
    s = procom2sll.get(procom)
    if not s:
        continue
    buckets.setdefault(s, []).append((peso.get(procom, 0.0), vals))

for s, rows in sorted(buckets.items()):
    w_tot = sum(w for w, _ in rows)
    if w_tot <= 0:
        continue
    acc_sll[s] = {
        k: round(sum(w * v[k] for w, v in rows) / w_tot, 2) for k in ORDINE
    }
    p = sll_props.get(s, {})
    meta_sll[s] = {
        "n_comuni_snai_usati": len(rows),
        "n_comuni_sll": p.get("n_comuni"),
        "quota_superficie_sll_coperta": (
            round(w_tot / p["sup_kmq"], 3) if p.get("sup_kmq") else None
        ),
    }

print(f"SLL con valori: {len(acc_sll)} su {len(sll_props)} SLL 2021")
q = sorted(m["quota_superficie_sll_coperta"] for m in meta_sll.values()
           if m["quota_superficie_sll_coperta"] is not None)
if q:
    print(f"  quota superficie SLL coperta: min {q[0]:.3f}, "
          f"mediana {q[len(q) // 2]:.3f}, max {q[-1]:.3f}")

# ── 7. scrittura ──────────────────────────────────────────────────────────────
out = {
    "fonte": "MCP hex-intelligence (hex_aggregate_by_comune, agg_type=mean), "
             "catalogo OvertureMaps + strutture sanitarie, isocrone 30 min "
             "trasporto privato con traffico su griglia H3 r8. Snapshot censimento 2021.",
    "note": "Media per cella H3 r8 (~0,74 kmq) delle strutture raggiungibili in 30 minuti "
            "in auto, calcolata sulle celle di ciascun comune. I valori SLL sono la media "
            "dei comuni SNAI del sistema locale, pesata per superficie comunale: "
            "descrivono la sola porzione SNAI dell'SLL, non l'intero sistema locale "
            "(vedi sll_meta: quota_superficie_sll_coperta).",
    "regioni_coperte": sorted(regioni_coperte),
    "regioni_non_coperte": non_coperte,
    "copertura_comuni": {
        "coperti": len(comuni),
        "totale_snai": len(idx),
        "quota": round(len(comuni) / len(idx), 4),
    },
    "indicatori": indicatori,
    "soglie": soglie,
    "comuni": dict(sorted(comuni.items())),
    "sll": acc_sll,
    "sll_meta": meta_sll,
}
with open(OUT_PATH, "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
print(f"scritto {OUT_PATH} ({os.path.getsize(OUT_PATH) / 1024:.0f} KB)")
