"""Quale delle due fonti e' piu' coerente con un riferimento indipendente?

Riferimento: 'MEDIA tempi di percorrenza' della Mappa Aree Interne 2020 (ISTAT/NUVAP),
in DATA/mappa-ai-2020-elenco-classificazione-comuni.xlsx, foglio DATI.
E' il tempo medio di percorrenza dal comune al polo piu' vicino, cioe' al centro che
eroga i servizi essenziali fra cui l'ospedale.

Attesa: piu' alto il tempo al polo, meno ospedali raggiungibili in 30 minuti.
La fonte migliore e' quella che correla piu' fortemente in senso negativo.
"""
import os
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
 ("Trevi nel Lazio",0.000,0.336),("Amatrice",0.000,0.000),("Accumoli",0.000,0.000),
 ("Cittareale",0.000,0.000),("Leonessa",0.000,0.000),("Borbona",0.000,0.000),
 ("Filettino",0.000,0.000),("Vallepietra",0.000,0.000),
]
df = pd.DataFrame(D, columns=["comune", "locale", "mcp"])

x = pd.read_excel(REPO + "/DATA/mappa-ai-2020-elenco-classificazione-comuni.xlsx",
                  sheet_name="DATI", header=2, dtype=str)
col_t = next(c for c in x.columns if "tempi di pe" in str(c).lower())
col_n = next(c for c in x.columns if str(c).startswith("COMUNE"))
print("colonna tempo: %r" % col_t)
print("colonna nome:  %r" % col_n)
print("righe nel foglio DATI: %d" % len(x))

t = x[[col_n, col_t]].copy()
t.columns = ["comune", "min_polo"]
t["min_polo"] = pd.to_numeric(t["min_polo"], errors="coerce")

m = df.merge(t, on="comune", how="left")
mancanti = m[m["min_polo"].isna()]["comune"].tolist()
m = m.dropna(subset=["min_polo"])
print("comuni appaiati: %d su %d" % (len(m), len(df)))
if mancanti:
    print("non appaiati: %s" % ", ".join(mancanti))

print("\n%-26s %8s %8s %9s" % ("comune", "locale", "MCP", "min_polo"))
print("-" * 56)
for _, r in m.sort_values("min_polo").iterrows():
    print("%-26s %8.3f %8.3f %9.1f" % (r["comune"], r["locale"], r["mcp"], r["min_polo"]))

rl = np.corrcoef(m["min_polo"], m["locale"])[0, 1]
rm = np.corrcoef(m["min_polo"], m["mcp"])[0, 1]
# Spearman = Pearson sui ranghi, senza scipy
rk = m[["min_polo", "locale", "mcp"]].rank()
sl = np.corrcoef(rk["min_polo"], rk["locale"])[0, 1]
sm = np.corrcoef(rk["min_polo"], rk["mcp"])[0, 1]

print("\ncorrelazione con il tempo al polo ISTAT (n=%d)" % len(m))
print("  Pearson   locale %+.3f   MCP %+.3f" % (rl, rm))
print("  Spearman  locale %+.3f   MCP %+.3f" % (sl, sm))
print("\n(attesa: negativa. Piu' forte in negativo = piu' coerente col riferimento)")

print("\n--- comuni molto distanti dal polo (min_polo >= 40) ---")
lon = m[m["min_polo"] >= 40]
print("n=%d  locale medio %.3f  MCP medio %.3f" % (
    len(lon), lon["locale"].mean(), lon["mcp"].mean()))
print("--- comuni molto vicini al polo (min_polo <= 15) ---")
vic = m[m["min_polo"] <= 15]
print("n=%d  locale medio %.3f  MCP medio %.3f" % (
    len(vic), vic["locale"].mean(), vic["mcp"].mean()))
