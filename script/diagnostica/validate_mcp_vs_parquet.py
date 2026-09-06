"""Confronta i valori 'ospedali' ottenuti via MCP hex-intelligence
con quelli gia' presenti in accessibility_data.json (derivati dal GeoParquet OCPR_LAZIO).
Campione di comuni SNAI del Lazio coprendo tutto il range di valori.
"""
import json, os

REPO = r"C:/Users/aalbe/Desktop/Code/Aree Interne Italia"
IDX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "comuni_snai_index.json")

# valori restituiti da hex_aggregate_by_comune(LAZIO, ospedali, mean)
MCP = {
    "Amatrice": 0.0,
    "Accumoli": 0.0,
    "Leonessa": 0.0,
    "Borbona": 0.0,
    "Cittareale": 0.0,
    "Micigliano": 0.05435628132065646,
    "Posta": 0.00022097674439907768,
    "Petrella Salto": 0.8979871168804165,
    "Fiamignano": 0.5181064069375599,
    "Pescorocchiano": 0.643999309985606,
    "Concerviano": 0.6584460256265338,
    "Varco Sabino": 0.0,
    "Marcetelli": 0.0,
    "Collegiove": 0.03790007913192191,
    "Nespolo": 0.00023275363843435008,
    "Trevi nel Lazio": 0.3359444011939363,
    "Filettino": 0.0,
    "Jenne": 0.36442433130097346,
    "Vallepietra": 0.0,
    "Subiaco": 0.9949721318378865,
    "Cervara di Roma": 0.9659721676199569,
    "Alvito": 1.7108163658876023,
    "San Donato Val di Comino": 1.8218037823359767,
    "Settefrati": 1.836122153224843,
    "Picinisco": 1.3819142793636991,
    "Vallecorsa": 0.0,
    "Carpineto Romano": 0.6225621102476445,
    "Maenza": 0.254989265713237,
    "Rocca Canterano": 0.7130564474331905,
    "Collalto Sabino": 0.7731914389047846,
}

comuni = json.load(open(IDX, encoding="utf-8"))
name2proc = {c["comune"]: c["procom"] for c in comuni if c["regione"] == "Lazio"}
acc = json.load(open(REPO + "/DATA/accessibility_data.json", encoding="utf-8"))["comuni"]

print("%-28s %10s %10s %10s" % ("comune", "MCP", "parquet", "diff"))
print("-" * 62)
diffs = []
mancanti = []
for nome, v_mcp in sorted(MCP.items()):
    proc = name2proc.get(nome)
    if proc is None:
        mancanti.append((nome, "non e' comune SNAI del Lazio nell'indice"))
        continue
    rec = acc.get(proc)
    if rec is None or "ospedali" not in rec:
        mancanti.append((nome, "assente in accessibility_data.json"))
        continue
    v_pq = rec["ospedali"]
    d = round(v_mcp, 2) - v_pq
    diffs.append(abs(d))
    print("%-28s %10.4f %10.2f %10.4f" % (nome, v_mcp, v_pq, d))

print()
if mancanti:
    print("non confrontabili (%d):" % len(mancanti))
    for n, m in mancanti:
        print("  %-28s %s" % (n, m))
    print()

if diffs:
    n = len(diffs)
    esatti = sum(1 for d in diffs if d < 1e-9)
    entro_001 = sum(1 for d in diffs if d <= 0.01)
    print("confrontati: %d" % n)
    print("identici dopo arrotondamento a 2 decimali: %d (%.0f%%)" % (esatti, 100.0 * esatti / n))
    print("entro 0.01: %d (%.0f%%)" % (entro_001, 100.0 * entro_001 / n))
    print("scarto massimo assoluto: %.6f" % max(diffs))
    print("scarto medio assoluto: %.6f" % (sum(diffs) / n))
