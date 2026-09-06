"""Costruisce l'indice comuni SNAI -> regione, e riepiloga la copertura attuale."""
import ast, json, os, collections

REPO = r"C:/Users/aalbe/Desktop/Code/Aree Interne Italia"
OUT = os.path.dirname(os.path.abspath(__file__))

# ── estrai AREE_BASE da build_dashboard.py senza eseguire lo script ───────────
src = open(os.path.join(REPO, "build_dashboard.py"), encoding="utf-8").read()
start = src.index("AREE_BASE = [")
end = src.index("\n]", start) + 2
aree = ast.literal_eval(src[start + len("AREE_BASE = "):end])
area2reg = {a["area"]: a["regione"] for a in aree}
print("aree definite in build_dashboard.py: %d" % len(aree))
print("regioni distinte: %d" % len(set(area2reg.values())))

# ── comuni SNAI dal geojson ──────────────────────────────────────────────────
gj = json.load(open(os.path.join(REPO, "comuni-snai-perimetri.geojson"), encoding="utf-8"))
comuni = []
senza_regione = []
for f in gj["features"]:
    p = f["properties"]
    reg = area2reg.get(p["area"])
    if reg is None:
        senza_regione.append(p["area"])
    comuni.append({"procom": p["procom"], "comune": p["comune"],
                   "area": p["area"], "status": p["status"], "regione": reg})

print("comuni nel geojson: %d" % len(comuni))
if senza_regione:
    print("AREE SENZA REGIONE: %s" % sorted(set(senza_regione)))

per_reg = collections.Counter(c["regione"] for c in comuni)
print("\ncomuni SNAI per regione:")
for k, v in sorted(per_reg.items(), key=lambda x: -x[1]):
    print("  %-24s %4d" % (k, v))

# ── copertura accessibilita attuale ──────────────────────────────────────────
acc = json.load(open(os.path.join(REPO, "DATA/accessibility_data.json"), encoding="utf-8"))
coperti = set(acc["comuni"])
proc2reg = {c["procom"]: c["regione"] for c in comuni}
cop_reg = collections.Counter(proc2reg.get(p, "?") for p in coperti)
print("\ncomuni con dati di accessibilita: %d su %d (%.1f%%)" % (
    len(coperti), len(comuni), 100.0 * len(coperti) / len(comuni)))
print("ripartizione per regione: %s" % dict(cop_reg))

lazio = [c for c in comuni if c["regione"] == "Lazio"]
lazio_cop = [c for c in lazio if c["procom"] in coperti]
print("\nLazio: %d comuni SNAI, %d con dati (%.1f%%)" % (
    len(lazio), len(lazio_cop), 100.0 * len(lazio_cop) / len(lazio)))

# nomi duplicati fra comuni SNAI della stessa regione (rischio join per nome)
dup = collections.Counter((c["regione"], c["comune"]) for c in comuni)
collisioni = {k: v for k, v in dup.items() if v > 1}
print("\nomonimi fra comuni SNAI nella stessa regione: %d" % len(collisioni))
for k, v in sorted(collisioni.items()):
    print("  %s / %s  x%d" % (k[0], k[1], v))

json.dump(comuni, open(os.path.join(OUT, "comuni_snai_index.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("\nindice scritto in comuni_snai_index.json")
