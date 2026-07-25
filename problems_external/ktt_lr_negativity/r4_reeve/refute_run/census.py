"""Status census: how often does the vertex-integrality hypothesis, or the
index<=64 hypothesis, fail?  Also the 6a1 histogram and the realised
simple-vertex cone multiplicities."""
import sys, os, random, math, json
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kt4

def one(g):
    A, b, bad = kt4.gap_rows(g)
    if bad: return "empty_boundary", None, None
    ds, bs = kt4.reduce_rows(A, b)
    V = kt4.verts(ds, bs)
    if not V: return "empty", None, None
    if kt4.affine_rank([list(v) for v in V]) < 3: return "lowdim", None, None
    nonint = any(c.denominator != 1 for v in V for c in v)
    mults = []
    for v, T in V.items():
        rays = kt4.cone_rays(ds, T)
        if len(rays) == 3:
            mults.append(abs(kt4.det3([list(r) for r in rays])))
    r = kt4.ehrhart_brion(ds, bs)
    if r["status"] != "ok":
        return r["status"], None, mults
    return ("nonintegral_vertex" if nonint else "ok"), r["poly"][1] * 6, mults

if __name__ == "__main__":
    seed = int(sys.argv[1]); N = int(sys.argv[2]); K = int(sys.argv[3])
    random.seed(seed)
    st = Counter(); h6 = Counter(); mm = Counter()
    for _ in range(N):
        g = kt4.fix_gap(tuple(max(1, int(10 ** random.uniform(0, math.log10(K))))
                              for _ in range(9)))
        s, v, mults = one(g)
        st[s] += 1
        if mults:
            for m in set(mults): mm[m] += 1
        if v is not None:
            h6[int(v)] += 1
            if v < 0:
                print(json.dumps({"NEGATIVE": True, "g": list(g)})); sys.exit(3)
    print(json.dumps({"seed": seed, "K": K, "status": dict(st),
                      "min6a1": min(h6) if h6 else None,
                      "6a1_hist_low": dict(sorted(h6.items())[:12]),
                      "simple_cone_mults_seen": dict(sorted(mm.items()))}))
