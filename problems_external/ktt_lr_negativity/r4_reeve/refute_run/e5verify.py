"""Direct verification (no LP trusted): build the hive polytope from genuine
partitions and inspect every vertex's tangent-cone multiplicity."""
import sys, os, itertools
from fractions import Fraction
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kt4

def report(g, label=""):
    g = tuple(g)
    if not kt4.realizable(g):
        g = tuple(4 * x for x in g)
    assert kt4.realizable(g)
    lam, mu, nu = kt4.realise(g)
    A, b, bad = kt4.hive_rows(lam, mu, nu)
    if bad:
        return {"g": g, "empty": True}
    ds, bs = kt4.reduce_rows(A, b)
    V = kt4.verts(ds, bs)
    pts = [list(v) for v in V]
    dim = kt4.affine_rank(pts)
    info = []
    for v, T in sorted(V.items()):
        rays = kt4.cone_rays(ds, T)
        if len(rays) == 3:
            m = abs(kt4.det3([list(r) for r in rays]))
        else:
            m = None
        info.append({"v": [str(c) for c in v], "nrays": len(rays), "mult": m,
                     "integral": all(c.denominator == 1 for c in v),
                     "rays": rays if len(rays) == 3 else None})
    simple_mults = sorted({d["mult"] for d in info if d["nrays"] == 3})
    nonint = [d for d in info if not d["integral"]]
    return {"g": g, "lam": lam, "mu": mu, "nu": nu, "dim": dim,
            "nverts": len(V), "simple_cone_mults": simple_mults,
            "nonintegral_vertices": len(nonint), "detail": info}

CANDS = [
    (1, 2, 1, 1, 1, 2, 1, 1, 1),
    (1, 1, 1, 1, 1, 1, 1, 1, 1),
    (1, 2, 1, 1, 1, 2, 1, 2, 1),
    (2, 1, 1, 1, 2, 1, 1, 2, 1),
    (1, 1, 2, 1, 1, 1, 1, 2, 1),
]
for g in CANDS:
    r = report(g)
    print("g =", r["g"], " dim =", r.get("dim"), " nverts =", r.get("nverts"),
          " simple-cone multiplicities =", r.get("simple_cone_mults"),
          " nonintegral verts =", r.get("nonintegral_vertices"))
    for d in r.get("detail", []):
        if d["nrays"] == 3 and d["mult"] and d["mult"] > 1:
            print("     NON-UNIMODULAR SIMPLE VERTEX", d["v"], "mult", d["mult"], "rays", d["rays"])
