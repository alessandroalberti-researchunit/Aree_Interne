"""
Genera sll-perimetri.geojson a partire da:
  - SLL_2021.shp (geometrie UTM 32N)
  - DATA/tavole_istat_2023/... Tav.42 (dati economici 2023 per SLL)
  - SLL composition JSON (capoluogo per SLL)
"""
import geopandas as gpd
import pandas as pd
import json, os, sys

SHP_PATH  = "SLL_2021.shp"
ECON_XLS  = "DATA/tavole_istat_2023/Tavole/1. Appendice Statistica Frame territoriale.xlsx"
SPEC_XLS  = "DATA/Specializzazione_produttiva_SLL_2021.xlsx"
COMP_JSON = "Sistemi Locali del Lavoro (SLL) 2021 _ Composizione Data Indagine 28-06-2026 Stampa 28062026191300.json"
OUT_PATH  = "sll-perimetri.geojson"
SIMPLIFY_TOL = 0.005   # gradi decimali ≈ 400-500 m

# ── 1. Shapefile ───────────────────────────────────────────────────────────────
print("Lettura shapefile SLL 2021...", flush=True)
gdf = gpd.read_file(SHP_PATH)
print(f"  {len(gdf)} SLL, CRS: {gdf.crs}")
print(f"  Colonne: {list(gdf.columns)}")

# Riproiezione WGS84
print("Riproiezione a WGS84 (EPSG:4326)...", flush=True)
gdf = gdf.to_crs("EPSG:4326")

# Semplificazione
print(f"Semplificazione geometrie (tolerance={SIMPLIFY_TOL})...", flush=True)
gdf["geometry"] = gdf["geometry"].simplify(SIMPLIFY_TOL, preserve_topology=True)

# Normalizza cod_sll (4 cifre)
cod_col  = "COD_SLL"
name_col = next(c for c in gdf.columns if "SLL_2021" in c or c == "SLL_2021")
reg_col  = "REG_SLL"  # nome regione (non CREG_SLL che è il codice)
pop_col  = next((c for c in gdf.columns if "POP_2021" in c), None)
ncom_col = next((c for c in gdf.columns if "N_COM" in c), None)
sup_col  = next((c for c in gdf.columns if "SUP" in c.upper()), None)

gdf[cod_col] = gdf[cod_col].astype(str).str.strip().str.zfill(4)

# ── 2. Dati economici ISTAT 2023 ───────────────────────────────────────────────
print("Lettura dati economici (Tav.42)...", flush=True)
raw = pd.read_excel(ECON_XLS, sheet_name="Tav.42_Sistemi_Locali", header=None)

# Riga 2 (indice 2) = header; dati da riga 3
hdr = raw.iloc[2].tolist()
df  = raw.iloc[3:].copy()
df.columns = range(len(df.columns))

# Mappa posizionale (ordine colonne verificato dall'output precedente):
# 0=Regione, 1=Ripartizione, 2=COD_SLL, 3=DEN_SLL,
# 4=unita_locali, 5=addetti, 6=dipendenti,
# 7=retribuzioni, 8=costo_lavoro, 9=valore_aggiunto, 10=fatturato, 11=acquisti,
# 12=va_per_addetto, 13=va_su_fatturato, 14=acquisti_su_fatturato,
# 15=retrib_su_va, 16=retrib_per_dip
col_map = {
    0:  "regione_econ",
    1:  "ripartizione",
    2:  "cod_sll_econ",
    3:  "den_sll_econ",
    4:  "unita_locali",
    5:  "addetti",
    6:  "dipendenti",
    7:  "retribuzioni",
    8:  "costo_lavoro",
    9:  "valore_aggiunto",
    10: "fatturato",
    11: "acquisti",
    12: "va_per_addetto",
    13: "va_su_fatturato",
    14: "acq_su_fatturato",
    15: "retrib_su_va",
    16: "retrib_per_dip",
}
df = df.rename(columns=col_map)
df = df.dropna(subset=["cod_sll_econ"])
df = df[df["cod_sll_econ"].astype(str).str.match(r"^\d{4}$")]
df["cod_sll_econ"] = df["cod_sll_econ"].astype(str).str.zfill(4)
print(f"  {len(df)} SLL con dati economici")

# ── 3. Specializzazione produttiva (ISTAT, feb 2026) ──────────────────────────
print("Lettura specializzazione produttiva...", flush=True)
raw_spec = pd.read_excel(SPEC_XLS, sheet_name="class", header=0)
raw_spec.columns = ["cod_sll_spec","cod_sll_n","den_sll_spec",
                    "cod_classe","den_classe","cod_gruppo","den_gruppo",
                    "pop_spec","sup_spec"]
raw_spec = raw_spec.dropna(subset=["cod_sll_spec"])
raw_spec = raw_spec[raw_spec["cod_classe"].isin(["A","B","C","D"])]
raw_spec["cod_sll_spec"] = raw_spec["cod_sll_spec"].astype(float).astype(int).astype(str).str.zfill(4)
print(f"  {len(raw_spec)} SLL con specializzazione")

# ── 4. Capoluogo per SLL dal JSON di composizione ──────────────────────────────
print("Lettura capoluoghi dal JSON composizione...", flush=True)
with open(COMP_JSON, encoding="utf-8") as f:
    comp = json.load(f)["resultset"]
df_comp = pd.DataFrame(comp)
df_comp["PRO_COM_T"] = df_comp["PRO_COM_T"].astype(str).str.zfill(6)
df_comp["COD_SLL"]   = df_comp["COD_SLL"].astype(str).str.zfill(4)
# capoluogo = CC_SLL == 1
capoluoghi = (
    df_comp[df_comp["CC_SLL"] == 1][["COD_SLL", "COMUNE"]]
    .rename(columns={"COD_SLL": "cod_sll_cap", "COMUNE": "capoluogo"})
)
print(f"  {len(capoluoghi)} capoluoghi trovati")

# ── 5. Join ────────────────────────────────────────────────────────────────────
econ_cols = ["cod_sll_econ", "ripartizione", "unita_locali", "addetti", "dipendenti",
             "valore_aggiunto", "fatturato", "va_per_addetto", "retrib_per_dip"]
spec_cols = ["cod_sll_spec", "cod_classe", "den_classe", "cod_gruppo", "den_gruppo"]

gdf = gdf.merge(df[econ_cols],          left_on=cod_col, right_on="cod_sll_econ",  how="left")
gdf = gdf.merge(raw_spec[spec_cols],    left_on=cod_col, right_on="cod_sll_spec",  how="left")
gdf = gdf.merge(capoluoghi,             left_on=cod_col, right_on="cod_sll_cap",   how="left")

# ── 5. Rinomina + seleziona colonne ────────────────────────────────────────────
rename = {
    cod_col:  "cod_sll",
    name_col: "nome_sll",
    reg_col:  "regione",
}
if pop_col:  rename[pop_col]  = "pop_2021"
if ncom_col: rename[ncom_col] = "n_comuni"
if sup_col:  rename[sup_col]  = "sup_kmq"

gdf = gdf.rename(columns=rename)

keep = ["cod_sll", "nome_sll", "regione", "ripartizione", "capoluogo",
        "pop_2021", "n_comuni", "sup_kmq",
        "unita_locali", "addetti", "dipendenti",
        "valore_aggiunto", "fatturato", "va_per_addetto", "retrib_per_dip",
        "cod_classe", "den_classe", "cod_gruppo", "den_gruppo",
        "geometry"]
keep = [c for c in keep if c in gdf.columns]
gdf = gdf[keep]

# Arrotonda valori float
for col in ["sup_kmq", "va_per_addetto", "retrib_per_dip"]:
    if col in gdf.columns:
        gdf[col] = gdf[col].round(2)

# Valori numerici interi
for col in ["pop_2021", "n_comuni", "unita_locali", "addetti", "dipendenti",
            "valore_aggiunto", "fatturato"]:
    if col in gdf.columns:
        gdf[col] = pd.to_numeric(gdf[col], errors="coerce").fillna(0).astype(int)

print(f"Colonne finali: {[c for c in gdf.columns if c != 'geometry']}")
print(gdf[["cod_sll", "nome_sll", "regione", "pop_2021", "addetti", "va_per_addetto"]].head(3))

# ── 6. Export GeoJSON ──────────────────────────────────────────────────────────
print(f"\nEsportazione in {OUT_PATH}...", flush=True)
gdf.to_file(OUT_PATH, driver="GeoJSON")

size_mb = os.path.getsize(OUT_PATH) / 1024 / 1024
print(f"File generato: {size_mb:.1f} MB  ({len(gdf)} features)")

if size_mb > 8:
    print(f"\nATTENZIONE: file grande ({size_mb:.1f} MB). Considera tolerance più alta.")
    print("Riesegui con SIMPLIFY_TOL = 0.01 se necessario.")
