"""Statistiche esatte sul confronto locale vs MCP, dai 48 comuni di test."""
import numpy as np

# comune, locale, mcp, dist_km  (output di test_edge_effect.py)
R = [
 ("Proceno",0.536,1.796,1.4),("Anzio",2.000,2.057,2.0),("Castelforte",0.829,1.900,2.3),
 ("Sora",0.714,1.584,2.4),("Cervara di Roma",0.564,0.966,2.6),("Collalto Sabino",0.080,0.773,2.8),
 ("Minturno",1.000,1.081,2.8),("Civitavecchia",1.857,1.997,3.0),("Accumoli",0.000,0.000,3.0),
 ("San Donato Val di Comino",0.681,1.822,3.0),("Borbona",0.000,0.000,3.1),("Filettino",0.000,0.000,3.7),
 ("Acquapendente",0.701,1.709,3.9),("Cittareale",0.000,0.000,3.9),("Sabaudia",0.989,1.866,4.0),
 ("Vallepietra",0.000,0.000,4.3),("Pescorocchiano",0.057,0.644,4.4),("Alvito",0.862,1.711,4.5),
 ("Fiamignano",0.032,0.518,4.6),("Settefrati",0.131,1.836,4.6),("Picinisco",0.078,1.382,4.7),
 ("Amatrice",0.000,0.000,4.9),("Leonessa",0.000,0.000,5.2),("Pomezia",3.245,5.532,5.8),
 ("Tarquinia",1.313,1.990,6.2),("Cerveteri",0.854,3.121,6.3),("Latina",1.427,1.411,6.4),
 ("Cassino",0.962,1.629,6.7),("Subiaco",0.747,0.995,8.2),("Trevi nel Lazio",0.000,0.336,9.1),
 ("Petrella Salto",0.123,0.898,9.2),("Aprilia",3.018,5.669,9.9),("Rieti",0.847,1.057,11.5),
 ("Velletri",1.837,2.824,12.1),("Bracciano",0.845,0.997,16.6),("Zagarolo",3.914,4.867,16.7),
 ("Palestrina",1.732,3.398,18.7),("Viterbo",0.634,0.993,19.1),("Frosinone",1.053,1.502,20.7),
 ("Nepi",0.953,1.925,21.7),("Ronciglione",0.385,1.851,22.3),("Monterotondo",2.520,3.972,22.5),
 ("Tivoli",2.693,4.671,22.6),("Genazzano",1.143,1.968,23.2),("Cave",1.524,1.779,24.1),
 ("Sutri",0.309,2.644,25.4),("Capranica",0.113,1.555,27.9),("Vetralla",0.660,1.083,28.2),
]

loc = np.array([r[1] for r in R])
mcp = np.array([r[2] for r in R])
dist = np.array([r[3] for r in R])
gap = mcp - loc

n = len(R)
pos = int((gap > 1e-9).sum())
neg = int((gap < -1e-9).sum())
zero_pari = int(((np.abs(gap) <= 1e-9) & (loc == 0) & (mcp == 0)).sum())

print("comuni confrontati: %d" % n)
print("MCP strettamente maggiore: %d (%.0f%%)" % (pos, 100.0*pos/n))
print("coincidenti, entrambi esattamente 0: %d" % zero_pari)
print("MCP minore: %d" % neg)
print("scarto medio: %+.3f" % gap.mean())
print("scarto mediano: %+.3f" % float(np.median(gap)))
print("scarto massimo: %+.3f (%s)" % (gap.max(), R[int(gap.argmax())][0]))
print("scarto minimo: %+.3f (%s)" % (gap.min(), R[int(gap.argmin())][0]))
print()

nz = loc > 0
rap = loc[nz] / mcp[nz]
print("rapporto locale/MCP sui %d comuni con valore locale > 0:" % int(nz.sum()))
print("  min %.3f (%s)" % (rap.min(), np.array([r[0] for r in R])[nz][int(rap.argmin())]))
print("  max %.3f (%s)" % (rap.max(), np.array([r[0] for r in R])[nz][int(rap.argmax())]))
print("  media %.3f, deviazione standard %.3f" % (rap.mean(), rap.std(ddof=1)))
print("  coefficiente di variazione %.1f%%" % (100.0*rap.std(ddof=1)/rap.mean()))
print()

vic = dist <= 10
lon = dist > 20
print("entro 10 km dal confine: n=%d, scarto medio %+.3f" % (int(vic.sum()), gap[vic].mean()))
print("oltre 20 km dal confine: n=%d, scarto medio %+.3f" % (int(lon.sum()), gap[lon].mean()))
print("correlazione Pearson distanza/scarto: %+.3f" % float(np.corrcoef(dist, gap)[0,1]))
print()

zl = loc == 0
print("comuni con locale esattamente 0: %d, di cui MCP anche 0: %d" % (
    int(zl.sum()), int(((mcp == 0) & zl).sum())))
print("  eccezione: %s" % [R[i][0] for i in range(n) if zl[i] and mcp[i] != 0])
