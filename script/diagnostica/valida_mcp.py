import json, glob, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
idx = json.load(open(os.path.join(ROOT, 'script', 'diagnostica', 'comuni_snai_index.json'), encoding='utf-8'))
tot = 0
for f in sorted(glob.glob(os.path.join(ROOT, 'DATA', 'mcp_accessibilita', '*.json'))):
    d = json.load(open(f, encoding='utf-8'))
    regs = d['_regioni_progetto']
    attesi = set(x['comune'] for x in idx if x['regione'] in regs)
    avuti = set(d['valori'])
    mal = [k for k, v in d['valori'].items()
           if len(v) != 6 or any(not isinstance(x, (int, float)) or x < 0 for x in v)]
    tot += len(avuti)
    nome = os.path.basename(f)
    print(f"{nome:28s} {len(avuti):4d}/{len(attesi):4d}", end='')
    if attesi - avuti: print(f"  MANCANTI {sorted(attesi-avuti)}", end='')
    if avuti - attesi: print(f"  EXTRA {sorted(avuti-attesi)}", end='')
    if mal: print(f"  MALFORMATI {mal}", end='')
    if d.get('_comuni_snai') != len(avuti): print(f"  META _comuni_snai={d.get('_comuni_snai')}", end='')
    print()
print(f"\nTOTALE comuni SNAI coperti: {tot} / {len(idx)} ({100*tot/len(idx):.1f}%)")
