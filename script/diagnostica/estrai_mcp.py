"""Assembla DATA/mcp_accessibilita/<REGIONE>.json dai file tool-results del MCP hex-intelligence.

Uso: python script/diagnostica/estrai_mcp.py REGIONE_MCP "Regione Progetto"[,"Altra"]

Legge tutti i file mcp-*hex_aggregate_by_comune-*.txt nella cartella tool-results
della sessione, tiene quelli della regione richiesta, li mappa sui 6 indicatori
attesi e scrive il file regionale con i soli comuni SNAI.
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Cartella dei tool-results. Il percorso contiene l'id della sessione Claude Code,
# quindi si cercano tutte le sessioni del progetto: MCP_TOOL_RESULTS puo forzarne una.
PROJECT_SESSIONS = os.path.join(
    os.path.expanduser("~"),
    ".claude", "projects",
    "C--Users-aalbe-Desktop-Code-Aree-Interne-Italia",
)
TOOL_RESULT_DIRS = (
    [os.environ["MCP_TOOL_RESULTS"]]
    if os.environ.get("MCP_TOOL_RESULTS")
    else sorted(glob.glob(os.path.join(PROJECT_SESSIONS, "*", "tool-results")))
)

# indicatore MCP -> posizione nell'ordine _ordine
INDICATORI = {
    "sanita_ospedale||traffic__30__total_ospedale": 0,
    "ovm_places_sanita||traffic__30__total_sanita": 1,
    "ovm_places_istruzione||traffic__30__total_istruzione": 2,
    "ovm_infr_infrastrutture||traffic__30__total_infrastrutture": 3,
    "ovm_places_sport||traffic__30__total_sport": 4,
    "ovm_places_cultura||traffic__30__total_cultura": 5,
}
ORDINE = ["ospedali", "sanita", "istruzione", "trasporti", "sport", "cultura"]


def payload(path):
    raw = open(path, encoding="utf-8").read()
    try:
        raw = json.loads(raw)["result"]
    except Exception:
        pass
    m = re.search(r"```json\s*(\{.*\})\s*```", raw, re.S)
    if not m:
        return None
    return json.loads(m.group(1))


def main():
    regione_mcp = sys.argv[1]
    regioni_progetto = [r.strip() for r in sys.argv[2].split(",")]

    idx = json.load(open(os.path.join(ROOT, "script", "diagnostica", "comuni_snai_index.json"), encoding="utf-8"))
    attesi = sorted(x["comune"] for x in idx if x["regione"] in regioni_progetto)

    trovati = {}  # posizione -> (mtime, ranking dict, n_comuni)
    candidati = []
    for d in TOOL_RESULT_DIRS:
        candidati += glob.glob(os.path.join(d, "mcp-*hex_aggregate_by_comune-*.txt"))
    for f in candidati:
        d = payload(f)
        if not d or d.get("region") != regione_mcp:
            continue
        pos = INDICATORI.get(d.get("indicator"))
        if pos is None:
            continue
        mtime = os.path.getmtime(f)
        if pos in trovati and trovati[pos][0] >= mtime:
            continue
        trovati[pos] = (
            mtime,
            {r["comune"]: r["value"] for r in d["ranking"]},
            d["totale_comuni_regione"],
        )

    mancanti_ind = [ORDINE[i] for i in range(6) if i not in trovati]
    if mancanti_ind:
        print("INDICATORI MANCANTI:", mancanti_ind)
        return 1

    n_reg = trovati[0][2]
    valori = {}
    incompleti = []
    for c in attesi:
        riga = []
        for i in range(6):
            v = trovati[i][1].get(c)
            if v is None:
                incompleti.append((c, ORDINE[i]))
                riga.append(None)
            else:
                riga.append(round(v, 2))
        valori[c] = riga

    if incompleti:
        print("VALORI MANCANTI:", incompleti)
        return 1

    out = {
        "_regione_mcp": regione_mcp,
        "_regioni_progetto": regioni_progetto,
        "_comuni_regione": n_reg,
        "_comuni_snai": len(valori),
        "_ordine": ORDINE,
        "_fonte": f"MCP hex-intelligence, hex_aggregate_by_comune, agg_type=mean, top_k={n_reg}",
        "_data": "2026-09-06",
        "valori": valori,
    }
    dest = os.path.join(ROOT, "DATA", "mcp_accessibilita", f"{regione_mcp}.json")
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print(f"scritto {dest}: {len(valori)} comuni SNAI su {n_reg} comuni regione")
    return 0


if __name__ == "__main__":
    sys.exit(main())
