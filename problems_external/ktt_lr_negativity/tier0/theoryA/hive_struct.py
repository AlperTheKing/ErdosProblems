#!/usr/bin/env python3
"""
hive_struct.py -- EXACT structural analyzer for Knutson-Tao hive polytopes.

Same boundary/rhombus model as engine A (lr_hive.cpp / BUILD_A.md):
  triangle {(x,y): x,y>=0, x+y<=n}, n = len(nu)
  B[(0,y)]     = sum(lam[:y])                     (left edge)
  B[(x,n-x)]   = |lam| + sum(mu[:x])              (right edge)
  B[(x,0)]     = sum(nu[:x])                      (bottom edge)
  rhombi (obtuse sum >= acute sum):
   (A) h(x+1,y)+h(x,y+1) >= h(x,y)+h(x+1,y+1)   x,y>=0, x+y<=n-2
   (B) h(x,y)+h(x+1,y)   >= h(x,y+1)+h(x+1,y-1) y>=1, x+y<=n-1
   (C) h(x,y)+h(x,y+1)   >= h(x+1,y)+h(x-1,y+1) x>=1, x+y<=n-1

Outputs, all exact integer arithmetic:
  * D           = #interior sites  (ambient dimension)
  * c           = #integer hives (lattice points of Q)
  * dim_lat     = affine dim of the SET OF LATTICE POINTS  (<= dim Q)
  * eqs         = rhombus constraints tight at EVERY lattice point
  * n_int/n_bdy = lattice points with all non-eq slacks > 0  /  else
  * free sites  = interior sites appearing in no implicit equality
  * step-check  = for each lattice point p in relint and each free site v,
                  walk p +- k e_v to the last feasible point and check that
                  the stopping constraint is tight there.

CAUTION: dim_lat <= dim Q always; equality must be cross-checked against the
Ehrhart degree d from tier0_screen.py.  Implicit-equality detection here is
relative to the lattice points, so it is exact only when dim_lat == dim Q.
"""
import sys, json, itertools
from fractions import Fraction


def build(lam, mu, nu):
    n = len(nu)
    lam = list(lam) + [0] * (n - len(lam))
    mu = list(mu) + [0] * (n - len(mu))
    if len(lam) > n or len(mu) > n:
        return None
    B = {}
    ps = lambda p, k: sum(p[:k])
    for y in range(n + 1):
        B[(0, y)] = ps(lam, y)
    for x in range(n + 1):
        B[(x, n - x)] = sum(lam) + ps(mu, x)
    for x in range(n + 1):
        B[(x, 0)] = ps(nu, x)
    # consistency at corners
    if B[(0, n)] != sum(lam) + 0 and B.get((0, n)) is not None:
        pass
    interior = [(x, y) for x in range(1, n) for y in range(1, n) if x + y <= n - 1]
    interior.sort()
    idx = {v: i for i, v in enumerate(interior)}
    D = len(interior)

    # constraint list: each is (coef dict over interior idx, const) meaning
    #   sum coef*h >= -const   i.e.  obtuse - acute >= 0
    cons = []
    def add(pluses, minuses):
        vec = [0] * D
        const = 0
        ok = True
        for p, s in [(pluses, 1), (minuses, -1)]:
            for pt in p:
                if pt in idx:
                    vec[idx[pt]] += s
                elif pt in B:
                    const += s * B[pt]
                else:
                    ok = False
        if not ok:
            return
        cons.append((tuple(vec), const))   # slack = <vec,h> + const >= 0

    for x in range(0, n + 1):
        for y in range(0, n + 1):
            if x + y <= n - 2:
                add([(x + 1, y), (x, y + 1)], [(x, y), (x + 1, y + 1)])
    for x in range(0, n + 1):
        for y in range(1, n + 1):
            if x + y <= n - 1:
                add([(x, y), (x + 1, y)], [(x, y + 1), (x + 1, y - 1)])
    for x in range(1, n + 1):
        for y in range(0, n + 1):
            if x + y <= n - 1:
                add([(x, y), (x, y + 1)], [(x + 1, y), (x - 1, y + 1)])
    return dict(n=n, B=B, interior=interior, idx=idx, D=D, cons=cons)


def slacks(P, h):
    out = []
    for vec, const in P["cons"]:
        s = const
        for i, cv in enumerate(vec):
            if cv:
                s += cv * h[i]
        out.append(s)
    return out


def feasible(P, h):
    for vec, const in P["cons"]:
        s = const
        for i, cv in enumerate(vec):
            if cv:
                s += cv * h[i]
        if s < 0:
            return False
    return True


def enumerate_hives(P, cap=200000):
    """Brute-force DFS with interval propagation over interior sites in order."""
    D = P["D"]
    if D == 0:
        return [()] if feasible(P, []) else []
    cons = P["cons"]
    # for each site index i, constraints whose LAST nonzero index is i
    last = {}
    for k, (vec, const) in enumerate(cons):
        nz = [i for i, cv in enumerate(vec) if cv]
        if not nz:
            continue
        last.setdefault(max(nz), []).append(k)
    fully_bdry = [k for k, (vec, const) in enumerate(cons)
                  if not any(vec)]
    for k in fully_bdry:
        if cons[k][1] < 0:
            return []
    res = []
    h = [0] * D

    def rec(i):
        if len(res) > cap:
            raise MemoryError("cap")
        if i == D:
            res.append(tuple(h))
            return
        lo, hi = None, None
        for k in last.get(i, []):
            vec, const = cons[k]
            s0 = const + sum(vec[j] * h[j] for j in range(i))
            cv = vec[i]
            # s0 + cv*h[i] >= 0
            if cv > 0:
                b = -(-s0 // cv) if False else None
                # h[i] >= -s0/cv  -> ceil
                v = -(-(-s0) // cv) if False else None
                import math
                b = math.ceil(Fraction(-s0, cv))
                lo = b if lo is None else max(lo, b)
            else:
                import math
                b = math.floor(Fraction(-s0, cv))  # cv<0 flips
                hi = b if hi is None else min(hi, b)
        if lo is None or hi is None:
            raise ValueError("unbounded interval at site %d" % i)
        for v in range(lo, hi + 1):
            h[i] = v
            rec(i + 1)
        h[i] = 0

    try:
        rec(0)
    except MemoryError:
        return None
    return res


def affine_rank(pts):
    if not pts:
        return -1
    base = pts[0]
    rows = [[Fraction(a - b) for a, b in zip(p, base)] for p in pts[1:]]
    if not rows:
        return 0
    # gaussian elimination
    m = len(rows); nn = len(rows[0]); r = 0
    for col in range(nn):
        piv = None
        for i in range(r, m):
            if rows[i][col] != 0:
                piv = i; break
        if piv is None:
            continue
        rows[r], rows[piv] = rows[piv], rows[r]
        pv = rows[r][col]
        for i in range(r + 1, m):
            if rows[i][col] != 0:
                f = rows[i][col] / pv
                for j in range(col, nn):
                    rows[i][j] -= f * rows[r][j]
        r += 1
        if r == m:
            break
    return r


def analyze(lam, mu, nu, cap=200000):
    P = build(lam, mu, nu)
    if P is None:
        return {"status": "BAD"}
    pts = enumerate_hives(P, cap)
    if pts is None:
        return {"status": "CAP"}
    c = len(pts)
    if c == 0:
        return {"status": "EMPTY", "c": 0}
    S = [slacks(P, p) for p in pts]
    ncon = len(P["cons"])
    eq = [k for k in range(ncon) if all(s[k] == 0 for s in S)]
    eqset = set(eq)
    interior_flags = [all(s[k] > 0 for k in range(ncon) if k not in eqset) for s in S]
    n_int = sum(interior_flags)
    dim_lat = affine_rank(pts)
    # free sites: interior sites with zero coefficient in every implicit equality
    free = []
    for i in range(P["D"]):
        if all(P["cons"][k][0][i] == 0 for k in eq):
            free.append(i)
    return {"status": "OK", "lam": lam, "mu": mu, "nu": nu,
            "D": P["D"], "c": c, "dim_lat": dim_lat,
            "n_eq": len(eq), "n_int": n_int, "n_bdy": c - n_int,
            "n_free": len(free), "free": free,
            "interior_pts": [list(pts[i]) for i in range(c) if interior_flags[i]],
            "P": P, "pts": pts, "eq": eq, "interior_flags": interior_flags}


def step_check(res):
    """From each interior lattice point, walk +-e_v for each free site v;
    verify the last feasible point is on the relative boundary."""
    P = res["P"]; eqset = set(res["eq"]); ncon = len(P["cons"])
    bdry_found = set()
    ok = True
    for pi, p in enumerate(res["pts"]):
        if not res["interior_flags"][pi]:
            continue
        for v in res["free"]:
            for sgn in (1, -1):
                h = list(p); k = 0
                while True:
                    h2 = list(h); h2[v] += sgn
                    if feasible(P, h2):
                        h = h2; k += 1
                        if k > 10000: ok = False; break
                    else:
                        break
                sl = slacks(P, h)
                on_bdry = any(sl[j] == 0 for j in range(ncon) if j not in eqset)
                if not on_bdry:
                    ok = False
                if k >= 1:
                    bdry_found.add(tuple(h))
    return ok, len(bdry_found)


if __name__ == "__main__":
    if sys.argv[1] == "--batch":
        for line in open(sys.argv[2]):
            line = line.strip()
            if not line or line.startswith("#"): continue
            a, b, cc = line.split(";")
            f = lambda s: [int(t) for t in s.split(",") if t.strip()]
            r = analyze(f(a), f(b), f(cc))
            r.pop("P", None); r.pop("pts", None); r.pop("eq", None)
            r.pop("interior_flags", None)
            print(json.dumps(r))
    else:
        f = lambda s: [int(t) for t in s.split(",") if t.strip()]
        r = analyze(f(sys.argv[1]), f(sys.argv[2]), f(sys.argv[3]))
        if r["status"] == "OK":
            ok, nb = step_check(r)
            r["step_check_ok"] = ok
            r["bdry_from_steps"] = nb
        r.pop("P", None); r.pop("pts", None); r.pop("eq", None)
        r.pop("interior_flags", None)
        print(json.dumps(r))
