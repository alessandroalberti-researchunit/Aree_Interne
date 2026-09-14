"""Verifica su tutti i 378 comuni del Lazio: perche' GeoParquet locale e MCP discordano.

Confronta, comune per comune:
  - media di sanita_ospedale||traffic__30__total_ospedale dal GeoParquet OCPR_LAZIO
  - stesso indicatore da MCP hex-intelligence (mcp_lazio_ospedali.json)
  - tempo di percorrenza al polo ISTAT/NUVAP come riferimento indipendente

Test eseguiti:
  1. copertura e appaiamento
  2. distribuzione dello scarto e del rapporto
  3. regime per fascia di accessibilita (effetto soglia)
  4. coerenza di ciascuna fonte col tempo al polo ISTAT
  5. confronto fra le soglie a 15 e 30 minuti, per stimare la portata dell'isocrona
"""
import json
import os
import warnings

import geopandas as gpd
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
PARQUET = os.path.expanduser("~/ILAB_DATA/OCPR_LAZIO/DATA/grid_08_adv.geoparquet")
C15 = "sanita_ospedale||traffic__15__total_ospedale"
C30 = "sanita_ospedale||traffic__30__total_ospedale"

LAZIO_PROV = {"056", "057", "058", "059", "060"}


def sep(t):
    print("\n" + "=" * 72)
    print(t)
    print("=" * 72)


# ── 1. dati ──────────────────────────────────────────────────────────────────
mcp = json.load(open(os.path.join(HERE, "mcp_lazio_ospedali.json"), encoding="utf-8"))["valori"]
print("valori MCP caricati: %d" % len(mcp))

grid = gpd.read_parquet(PARQUET)
if grid.total_bounds[0] > 1000:
    grid = grid.set_crs("EPSG:32632", allow_override=True).to_crs("EPSG:4326")
else:
    grid = grid.to_crs("EPSG:4326")
print("celle H3 r8 nel parquet: %d" % len(grid))

com = gpd.read_file(os.path.join(REPO, "DATA", "comuni_italia.geojson")).to_crs("EPSG:4326")
col_nome = next(c for c in com.columns if c.lower() in ("name", "comune", "nome"))
col_istat = next(c for c in com.columns if c.lower() in
                 ("com_istat_code_num", "istat", "pro_com_t", "com_istat_code"))
com = com.rename(columns={col_nome: "comune"})
com["procom"] = com[col_istat].map(lambda v: str(v).zfill(6))
lazio = com[com["procom"].str[:3].isin(LAZIO_PROV)][["comune", "procom", "geometry"]].copy()
print("comuni del Lazio nei confini nazionali: %d" % len(lazio))

g32 = grid[["geometry", C15, C30]].to_crs("EPSG:32632")
pts = g32.copy()
pts["geometry"] = g32.geometry.centroid
pts = pts.to_crs("EPSG:4326")
j = gpd.sjoin(pts, lazio, how="inner", predicate="within")
loc = j.groupby("comune").agg(
    locale=(C30, "mean"), locale15=(C15, "mean"),
    n_celle=(C30, "size"), max30=(C30, "max"), max15=(C15, "max"),
    celle_nz=(C30, lambda s: int((s > 0).sum())))
print("comuni agganciati alle celle: %d" % len(loc))

istat = pd.read_excel(
    os.path.join(REPO, "DATA", "mappa-ai-2020-elenco-classificazione-comuni.xlsx"),
    sheet_name="DATI", header=2, dtype=str)
c_t = next(c for c in istat.columns if "tempi di pe" in str(c).lower())
c_n = next(c for c in istat.columns if str(c).startswith("COMUNE"))
c_cl = next(c for c in istat.columns if "DES_AI_2020" in str(c))
ist = istat[[c_n, c_t, c_cl]].copy()
ist.columns = ["comune", "min_polo", "classe"]
ist["min_polo"] = pd.to_numeric(ist["min_polo"], errors="coerce")

df = (pd.DataFrame({"comune": list(mcp), "mcp": list(mcp.values())})
      .merge(loc.reset_index(), on="comune", how="outer")
      .merge(ist, on="comune", how="left"))

sep("1. COPERTURA E APPAIAMENTO")
print("comuni in MCP:                 %d" % df["mcp"].notna().sum())
print("comuni con valore locale:      %d" % df["locale"].notna().sum())
print("comuni con entrambi:           %d" % (df["mcp"].notna() & df["locale"].notna()).sum())
solo_mcp = df[df["mcp"].notna() & df["locale"].isna()]["comune"].tolist()
solo_loc = df[df["locale"].notna() & df["mcp"].isna()]["comune"].tolist()
if solo_mcp:
    print("solo in MCP (%d): %s" % (len(solo_mcp), ", ".join(sorted(solo_mcp))))
if solo_loc:
    print("solo nel parquet (%d): %s" % (len(solo_loc), ", ".join(sorted(solo_loc))))

d = df.dropna(subset=["mcp", "locale"]).copy()
d["scarto"] = d["mcp"] - d["locale"]

sep("2. DISTRIBUZIONE DELLO SCARTO (n=%d)" % len(d))
print("MCP maggiore:            %4d (%.1f%%)" % ((d["scarto"] > 1e-9).sum(),
                                                 100 * (d["scarto"] > 1e-9).mean()))
print("coincidenti:             %4d (%.1f%%)" % ((d["scarto"].abs() <= 1e-9).sum(),
                                                 100 * (d["scarto"].abs() <= 1e-9).mean()))
print("locale maggiore:         %4d (%.1f%%)" % ((d["scarto"] < -1e-9).sum(),
                                                 100 * (d["scarto"] < -1e-9).mean()))
print("scarto medio  %+.3f | mediano %+.3f | min %+.3f | max %+.3f" % (
    d["scarto"].mean(), d["scarto"].median(), d["scarto"].min(), d["scarto"].max()))
ent = d[d["scarto"].abs() <= 1e-9]
print("i coincidenti sono tutti a zero: %s" % bool(((ent["mcp"] == 0) & (ent["locale"] == 0)).all()))

sep("3. RAPPORTO LOCALE/MCP PER FASCIA (effetto soglia)")
a = d[d["mcp"] > 0].copy()
a["rap"] = a["locale"] / a["mcp"]
print("%-16s %5s %9s %9s %9s" % ("fascia MCP", "n", "rap medio", "rap p25", "rap p75"))
print("-" * 54)
for lo, hi in [(0, 0.25), (0.25, 0.5), (0.5, 1.0), (1.0, 2.0), (2.0, 5.0), (5.0, 1e9)]:
    s = a[(a["mcp"] > lo) & (a["mcp"] <= hi)]
    if len(s) == 0:
        continue
    et = "oltre 5.0" if hi > 1e8 else "%.2f - %.2f" % (lo, hi)
    print("%-16s %5d %9.3f %9.3f %9.3f" % (
        et, len(s), s["rap"].mean(), s["rap"].quantile(.25), s["rap"].quantile(.75)))
rk = a[["mcp", "rap"]].rank()
print("\ncorrelazione livello MCP / rapporto: Pearson %+.3f, Spearman %+.3f" % (
    np.corrcoef(a["mcp"], a["rap"])[0, 1], np.corrcoef(rk["mcp"], rk["rap"])[0, 1]))

sep("4. COERENZA COL TEMPO AL POLO ISTAT")
k = d.dropna(subset=["min_polo"])
rkk = k[["min_polo", "locale", "mcp"]].rank()
print("comuni con tempo al polo: %d" % len(k))
print("Pearson   locale %+.3f   MCP %+.3f" % (
    np.corrcoef(k["min_polo"], k["locale"])[0, 1],
    np.corrcoef(k["min_polo"], k["mcp"])[0, 1]))
print("Spearman  locale %+.3f   MCP %+.3f" % (
    np.corrcoef(rkk["min_polo"], rkk["locale"])[0, 1],
    np.corrcoef(rkk["min_polo"], rkk["mcp"])[0, 1]))
print("\nmedie per fascia di tempo al polo:")
print("%-18s %5s %9s %9s" % ("min al polo", "n", "locale", "MCP"))
print("-" * 44)
for lo, hi in [(0, 15), (15, 25), (25, 40), (40, 1e9)]:
    s = k[(k["min_polo"] >= lo) & (k["min_polo"] < hi)]
    if len(s) == 0:
        continue
    et = "oltre 40" if hi > 1e8 else "%d - %d" % (lo, hi)
    print("%-18s %5d %9.3f %9.3f" % (et, len(s), s["locale"].mean(), s["mcp"].mean()))

sep("5. PORTATA DELL'ISOCRONA: 15 CONTRO 30 MINUTI")
print("media regionale locale a 15 min: %.4f" % d["locale15"].mean())
print("media regionale locale a 30 min: %.4f" % d["locale"].mean())
print("media regionale MCP a 30 min:    %.4f" % d["mcp"].mean())
print("rapporto locale30/MCP30: %.3f" % (d["locale"].mean() / d["mcp"].mean()))
print("\nQuanti comuni hanno ZERO ospedali raggiungibili?")
print("  locale a 30 min: %d" % int((d["locale"] == 0).sum()))
print("  MCP a 30 min:    %d" % int((d["mcp"] == 0).sum()))
print("  locale a 15 min: %d" % int((d["locale15"] == 0).sum()))
solo_l0 = d[(d["locale"] == 0) & (d["mcp"] > 0)]
print("\ncomuni azzerati dal locale ma non da MCP: %d" % len(solo_l0))
for _, r in solo_l0.sort_values("mcp", ascending=False).head(12).iterrows():
    print("  %-26s MCP %.3f  celle %d  min_polo %s" % (
        r["comune"], r["mcp"], r["n_celle"],
        "n.d." if pd.isna(r["min_polo"]) else "%.1f" % r["min_polo"]))

sep("6. IL LOCALE VEDE MENO OSPEDALI IN ASSOLUTO?")
print("massimo di cella nel Lazio, locale 30 min: %.0f" % d["max30"].max())
print("comuni in cui il massimo di cella locale e' 1 o meno: %d su %d" % (
    int((d["max30"] <= 1).sum()), len(d)))
print("di questi, quanti hanno MCP > 1.5: %d" % int(((d["max30"] <= 1) & (d["mcp"] > 1.5)).sum()))
print("\nQuota di celle con almeno un ospedale (locale):")
d["quota_nz"] = d["celle_nz"] / d["n_celle"]
for lo, hi in [(0, 0.5), (0.5, 1.0), (1.0, 2.0), (2.0, 1e9)]:
    s = d[(d["mcp"] > lo) & (d["mcp"] <= hi)]
    if len(s) == 0:
        continue
    et = "oltre 2.0" if hi > 1e8 else "%.1f - %.1f" % (lo, hi)
    print("  MCP %-12s n=%3d  quota media celle non nulle %.3f" % (
        et, len(s), s["quota_nz"].mean()))

out = os.path.join(HERE, "confronto_lazio_completo.csv")
d.sort_values("mcp", ascending=False).to_csv(out, index=False, encoding="utf-8")
print("\ntabella completa salvata in %s" % os.path.basename(out))
