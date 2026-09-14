"""Il rapporto locale/MCP dipende dal livello di accessibilita?
Se il dataset locale usa un'isocrona di portata piu' corta, ci si aspetta:
  - nelle zone ben servite, rapporto stabile e < 1 (si perde una quota del conteggio)
  - nelle zone marginali, crollo verso 0 (effetto soglia: non si raggiunge piu' nulla)
  - nelle zone remote, accordo perfetto a 0 (fuori portata per entrambi)
"""
import numpy as np
import pandas as pd

# (comune, locale, MCP) da test_edge_effect.py e dal confronto sui comuni ad alta accessibilita
D = [
 ("Roma",11.720,18.075),("Ciampino",13.706,17.010),("Marino",8.759,11.126),
 ("Monte Porzio Catone",6.000,10.185),("Frascati",7.154,9.840),("Fonte Nuova",4.615,8.780),
 ("Guidonia Montecelio",5.549,8.578),("Fiumicino",4.550,8.016),("Aprilia",3.018,5.669),
 ("Pomezia",3.245,5.532),("Zagarolo",3.914,4.867),("Tivoli",2.693,4.671),
 ("Monterotondo",2.520,3.972),("Palestrina",1.732,3.398),("Cerveteri",0.854,3.121),
 ("Velletri",1.837,2.824),("Sutri",0.309,2.644),("Civitavecchia",1.857,1.997),
 ("Anzio",2.000,2.057),("Tarquinia",1.313,1.990),("Genazzano",1.143,1.968),
 ("Nepi",0.953,1.925),("Castelforte",0.829,1.900),("Ronciglione",0.385,1.851),
 ("Settefrati",0.131,1.836),("San Donato Val di Comino",0.681,1.822),
 ("Alvito",0.862,1.711),("Acquapendente",0.701,1.709),("Cave",1.524,1.779),
 ("Proceno",0.536,1.796),("Cassino",0.962,1.629),("Sora",0.714,1.584),
 ("Capranica",0.113,1.555),("Frosinone",1.053,1.502),("Latina",1.427,1.411),
 ("Picinisco",0.078,1.382),("Vetralla",0.660,1.083),("Minturno",1.000,1.081),
 ("Rieti",0.847,1.057),("Bracciano",0.845,0.997),("Subiaco",0.747,0.995),
 ("Viterbo",0.634,0.993),("Cervara di Roma",0.564,0.966),("Petrella Salto",0.123,0.898),
 ("Collalto Sabino",0.080,0.773),("Pescorocchiano",0.057,0.644),
 ("Carpineto Romano",0.037,0.623),("Fiamignano",0.032,0.518),
 ("Trevi nel Lazio",0.000,0.336),
 ("Amatrice",0.000,0.000),("Accumoli",0.000,0.000),("Cittareale",0.000,0.000),
 ("Leonessa",0.000,0.000),("Borbona",0.000,0.000),("Filettino",0.000,0.000),
 ("Vallepietra",0.000,0.000),
]
df = pd.DataFrame(D, columns=["comune", "loc", "mcp"])
print("comuni con entrambi i valori: %d" % len(df))

remoti = df[(df["loc"] == 0) & (df["mcp"] == 0)]
print("\nregime 1, fuori portata per entrambe le fonti: %d comuni, tutti a 0" % len(remoti))
print("  %s" % ", ".join(remoti["comune"]))

att = df[df["mcp"] > 0].copy()
att["rap"] = att["loc"] / att["mcp"]

print("\nrapporto locale/MCP per fascia di accessibilita MCP:")
print("%-16s %5s %8s %8s %8s" % ("fascia MCP", "n", "rap med", "rap min", "rap max"))
print("-" * 50)
bins = [(0, 0.5), (0.5, 1.0), (1.0, 2.0), (2.0, 5.0), (5.0, 100.0)]
for lo, hi in bins:
    s = att[(att["mcp"] > lo) & (att["mcp"] <= hi)]
    if len(s) == 0:
        continue
    print("%-16s %5d %8.3f %8.3f %8.3f" % (
        "%.1f - %.1f" % (lo, hi), len(s), s["rap"].mean(), s["rap"].min(), s["rap"].max()))

ben = att[att["mcp"] >= 2.0]
marg = att[(att["mcp"] > 0) & (att["mcp"] < 2.0)]
print("\nregime 2, zone ben servite (MCP >= 2):    n=%d, rapporto medio %.3f, dev.std %.3f" % (
    len(ben), ben["rap"].mean(), ben["rap"].std(ddof=1)))
print("regime 3, zone marginali (0 < MCP < 2):   n=%d, rapporto medio %.3f, dev.std %.3f" % (
    len(marg), marg["rap"].mean(), marg["rap"].std(ddof=1)))

sotto = marg[marg["rap"] < 0.25]
print("\ncomuni marginali con crollo sotto 0.25: %d su %d" % (len(sotto), len(marg)))
for _, r in sotto.sort_values("rap").iterrows():
    print("  %-26s locale %.3f  MCP %.3f  rapporto %.3f" % (
        r["comune"], r["loc"], r["mcp"], r["rap"]))

r = np.corrcoef(att["mcp"], att["rap"])[0, 1]
print("\ncorrelazione fra livello MCP e rapporto locale/MCP: %+.3f" % r)
print("(un rapporto che cresce col livello e' la firma di un effetto soglia)")
