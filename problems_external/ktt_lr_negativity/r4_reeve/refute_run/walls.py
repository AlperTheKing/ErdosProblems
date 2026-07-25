"""The chamber-wall arrangement in 9-dim gap space, and exact extreme-ray probing.

Q(g) changes combinatorial type exactly when some Cramer point v_S(g) crosses
some row t, i.e. on the hyperplane  R_{S,t} . g = 0  (rows_for(S) of e5.py).
a1 is linear on each chamber of this arrangement, so a1 < 0 somewhere iff
a1 < 0 on an EXTREME RAY of some chamber -- and every extreme ray is the
1-dim kernel of 8 independent wall normals (or of walls together with the
orthant facets g_i = 0).

This enumerates the distinct wall normals exactly and then samples extreme
rays by solving random 8-subsets over Q.
"""
import sys, os, itertools, random, json, math, time
from fractions import Fraction
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kt4
from e5 import DS, NB, rows_for, cone_mult
from search import a1x6

def primitive(v):
    den = 1
    for x in v:
        den = den * x.denominator // math.gcd(den, x.denominator)
    w = [int(x * den) for x in v]
    g = 0
    for x in w: g = math.gcd(g, abs(x))
    if g == 0: return None
    w = [x // g for x in w]
    for x in w:
        if x != 0:
            if x < 0: w = [-y for y in w]
            break
    return tuple(w)

def wall_set():
    H = set()
    for S in itertools.combinations(range(NB), 3):
        if kt4.det3([list(DS[i]) for i in S]) == 0: continue
        R, D = rows_for(S)
        for r in R:
            p = primitive([Fraction(x) for x in r])
            if p is not None: H.add(p)
    return sorted(H)

def kernel_ray(rows):
    """1-dim kernel of 8 rows in Q^9 (exact); None if dim != 1"""
    M = [[Fraction(x) for x in r] for r in rows]
    n = 9
    piv_col = []
    r = 0
    for c in range(n):
        p = None
        for i in range(r, len(M)):
            if M[i][c] != 0: p = i; break
        if p is None: continue
        M[r], M[p] = M[p], M[r]
        pv = M[r][c]
        M[r] = [x / pv for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [M[i][t] - f * M[r][t] for t in range(n)]
        piv_col.append(c); r += 1
        if r == len(M): break
    free = [c for c in range(n) if c not in piv_col]
    if len(free) != 1: return None
    fc = free[0]
    v = [Fraction(0)] * n
    v[fc] = Fraction(1)
    for i, c in enumerate(piv_col):
        v[c] = -M[i][fc]
    return primitive(v)

if __name__ == "__main__":
    mode = sys.argv[1]
    H = wall_set()
    if mode == "count":
        print("distinct chamber-wall normals in 9-dim gap space:", len(H))
        nn = [h for h in H if all(x >= 0 for x in h) or all(x <= 0 for x in h)]
        print("of which sign-definite (never cross the open orthant):", len(nn))
        print("sample:", H[:6])
        sys.exit(0)
    seed = int(sys.argv[2]); N = int(sys.argv[3])
    random.seed(seed)
    best = None; tried = 0; got = 0; t0 = time.time()
    ORTH = []
    for i in range(9):
        e = [0] * 9; e[i] = 1
        ORTH.append(tuple(e))
    pool = H + ORTH
    while tried < N:
        tried += 1
        rows = random.sample(pool, 8)
        r = kernel_ray(rows)
        if r is None: continue
        for s in (1, -1):
            g = tuple(s * x for x in r)
            if any(x < 0 for x in g): continue
            if all(x == 0 for x in g): continue
            # push strictly inside the orthant is NOT allowed (would leave the
            # ray); evaluate the ray itself, and also a tiny thickening
            for cand in (g, tuple(x + 1 for x in g), tuple(4 * x + 1 for x in g)):
                if any(x < 1 for x in cand): continue
                gg = kt4.fix_gap(cand)
                res = a1x6(gg)
                if res[0] != "ok": continue
                got += 1
                v = res[1]
                if v < 0:
                    print(json.dumps({"NEGATIVE": True, "g": list(gg), "v": str(v)}))
                    sys.exit(3)
                if best is None or v < best[0]: best = (v, gg)
    print(json.dumps({"seed": seed, "subsets_tried": tried, "rays_evaluated": got,
                      "min6a1": str(best[0]) if best else None,
                      "argmin": list(best[1]) if best else None,
                      "secs": round(time.time() - t0, 1)}))
