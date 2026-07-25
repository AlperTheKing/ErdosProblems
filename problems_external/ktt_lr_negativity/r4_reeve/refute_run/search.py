"""Targeted refutation search on the 9-dim gap cone.

a1(g) is homogeneous of degree 1 and piecewise linear on the gap cone, so
a1 < 0 somewhere  <=>  a1 < 0 on an extreme ray of some linearity chamber.
Therefore: (i) probe wildly anisotropic rays, (ii) run exact piecewise-linear
descent on the scale-invariant objective 6a1(g)/sum(g).
"""
import random, sys, os, math, json, time
from fractions import Fraction
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kt4

def a1x6(g):
    """returns (tag, 6*a1) ; tag in {'ok','lowdim','empty','bad'}"""
    try:
        A, b, bad = kt4.gap_rows(g)
    except AssertionError:
        return ("nonrealisable", None)
    if bad:
        return ("empty", None)
    ds, bs = kt4.reduce_rows(A, b)
    r = kt4.ehrhart_brion(ds, bs)
    st = r["status"]
    if st != "ok":
        return (st, None)
    v = r["poly"][1] * 6
    return ("ok", v, r)

def full(g):
    A, b, bad = kt4.gap_rows(g)
    ds, bs = kt4.reduce_rows(A, b)
    r = kt4.ehrhart_brion(ds, bs)
    P = r["poly"]
    c = P[0] + P[1] + P[2] + P[3]
    i = -(P[0] - P[1] + P[2] - P[3])
    V = P[3] * 6
    return {"poly": [str(x) for x in P], "c": c, "i": i, "V": V,
            "6a1": P[1] * 6, "nv": r["nv"], "nonsimple": r["nonsimple"],
            "maxidx": r["maxidx"]}

# ---------------------------------------------------------------- descent
def descent(g0, iters=200, verbose=False):
    """exact piecewise-linear descent on R(g) = 6a1(g)/sum(g), g in Z_{>=1}^9"""
    g = list(g0)
    res = a1x6(tuple(g))
    if res[0] != "ok":
        return None
    best = (Fraction(res[1], sum(g)), tuple(g), res[1])
    for it in range(iters):
        cur = best
        improved = False
        # finite-difference gradient (exact integers)
        base = cur[2]
        grad = []
        for k in range(9):
            h = list(cur[1]); h[k] += 1
            r2 = a1x6(tuple(h))
            grad.append(r2[1] - base if r2[0] == "ok" else None)
        # candidate moves: single coordinate up/down, and gradient-guided combos
        cands = []
        for k in range(9):
            for d in (1, -1, 2, -2, 4, -4):
                h = list(cur[1]); h[k] += d
                if h[k] >= 1: cands.append(tuple(h))
        if all(x is not None for x in grad):
            # ratio-reducing direction: minimise grad.d while sum(d) >= 0
            order = sorted(range(9), key=lambda k: grad[k])
            for take in (1, 2, 3, 4):
                for mult in (1, 2, 4, 8):
                    h = list(cur[1])
                    for k in order[:take]: h[k] += mult
                    for k in order[-take:]:
                        h[k] = max(1, h[k] - mult)
                    cands.append(tuple(h))
        for h in cands:
            r2 = a1x6(h)
            if r2[0] != "ok": continue
            val = Fraction(r2[1], sum(h))
            if val < best[0]:
                best = (val, h, r2[1]); improved = True
        if not improved:
            break
    return best

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "random":
        seed = int(sys.argv[2]); N = int(sys.argv[3]); K = int(sys.argv[4])
        aniso = len(sys.argv) > 5 and sys.argv[5] == "aniso"
        random.seed(seed)
        best6 = None; bestr = None; stats = {}
        t0 = time.time()
        for it in range(N):
            if aniso:
                # highly anisotropic: independent random magnitudes per coord
                g = []
                for _ in range(9):
                    e = random.uniform(0, math.log10(K))
                    g.append(max(1, int(10 ** e)))
                g = kt4.fix_gap(tuple(g))
            else:
                g = kt4.fix_gap(tuple(random.randint(1, K) for _ in range(9)))
            r = a1x6(g)
            stats[r[0]] = stats.get(r[0], 0) + 1
            if r[0] != "ok": continue
            v = r[1]
            if best6 is None or v < best6[0]: best6 = (v, g)
            rr = Fraction(v, sum(g))
            if bestr is None or rr < bestr[0]: bestr = (rr, g, v)
            if v < 0:
                print("!!! NEGATIVE", g, v); sys.exit(3)
        print(json.dumps({"seed": seed, "N": N, "K": K, "aniso": aniso,
                          "stats": stats, "min6a1": [str(best6[0]), best6[1]] if best6 else None,
                          "min_ratio": [str(bestr[0]), bestr[1], str(bestr[2])] if bestr else None,
                          "secs": round(time.time() - t0, 1)}))
    elif mode == "descent":
        seed = int(sys.argv[2]); N = int(sys.argv[3]); K = int(sys.argv[4])
        random.seed(seed)
        gbest = None
        for trial in range(N):
            while True:
                g = kt4.fix_gap(tuple(random.randint(1, K) for _ in range(9)))
                if a1x6(g)[0] == "ok": break
            b = descent(g)
            if b is None: continue
            if gbest is None or b[0] < gbest[0]:
                gbest = b
                print("trial", trial, "ratio", str(b[0]), "6a1", b[2], "g", b[1], flush=True)
            if b[2] < 0:
                print("!!! NEGATIVE", b); sys.exit(3)
        print("BEST", str(gbest[0]), gbest[1], gbest[2])
