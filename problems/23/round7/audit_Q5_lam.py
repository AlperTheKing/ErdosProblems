"""A10 (heavy graphs): exact Lambda = tau*(product weights) WITHOUT enumerating all
odd cycles, by a two-sided certificate:

  * primal cover z (rationalised from a float LP over SHORT odd cycles only), then
    verified feasible against ALL odd cycles by my own exact min-odd-cycle oracle
    (double cover + Dijkstra over Fraction)          -> tau* <= w.z
  * dual packing y supported on those short cycles, verified load <= w exactly
                                                     -> tau* >= sum y
  * accept only if the two coincide.

The float LP only STEERS; both certificates are checked in exact rational arithmetic.
"""
from fractions import Fraction as F
import heapq
import sys
sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\round7")
from audit_Q5_lib import (E_of, bip, psi, emass, all_cycles, C5n, andrasfai,
                          petersen, grotzsch, g6, NAMED_G6, tri_free)

FAIL = []


def chk(name, got, want=True):
    good = (got == want)
    if not good:
        FAIL.append((name, got, want))
    print(f"  {'OK  ' if good else 'FAIL'} {name}: {got}" + ("" if good else f" (want {want})"))


# ---- my own exact min-weight odd cycle: shortest v+ -> v- in the double cover ----
def min_odd_cycle_weight(n, A, z):
    """z: dict (u,v)->Fraction >= 0.  Returns the exact minimum z-weight of an odd
    cycle (= of an odd closed walk, which for z >= 0 is the same), or None."""
    nb = [[v for v in range(n) if (A[u] >> v) & 1] for u in range(n)]

    def wt(u, v):
        return z[(u, v)] if u < v else z[(v, u)]

    best = None
    for s in range(n):
        dist = {(s, 0): F(0)}
        pq = [(F(0), s, 0)]
        done = set()
        while pq:
            d, u, p = heapq.heappop(pq)
            if (u, p) in done:
                continue
            done.add((u, p))
            if (u, p) == (s, 1):
                if best is None or d < best:
                    best = d
                break
            if best is not None and d >= best:
                break
            for v in nb[u]:
                nd = d + wt(u, v)
                k = (v, 1 - p)
                if k not in dist or nd < dist[k]:
                    dist[k] = nd
                    heapq.heappush(pq, (nd, v, 1 - p))
    return best


def lam_exact(n, A, w, maxlen=9, name=""):
    import numpy as np
    from scipy.optimize import linprog
    E = E_of(n, A)
    ei = {e: i for i, e in enumerate(E)}
    C = all_cycles(n, A, only_odd=True, maxlen=maxlen)
    C = list(dict.fromkeys(C))
    M = len(C)
    Aub = np.zeros((M, len(E)))
    for k, cyc in enumerate(C):
        for e in cyc:
            Aub[k, ei[e]] = -1.0
    r = linprog(np.array([float(w[e]) for e in E]), A_ub=Aub, b_ub=-np.ones(M),
                bounds=[(0, None)] * len(E), method="highs")
    assert r.success, r.message
    zf, yf = r.x, -r.ineqlin.marginals
    for D in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21, 24, 25, 28, 30,
              32, 35, 36, 40, 42, 45, 48, 49, 50, 56, 60, 63, 64, 70, 72, 80, 84, 90,
              98, 100, 120, 126, 140, 168, 180, 196, 210, 240, 252, 280, 315, 336, 360,
              420, 504, 560, 630, 720, 840, 1260, 2520):
        z = {E[i]: F(zf[i]).limit_denominator(D) for i in range(len(E))}
        if any(v < 0 for v in z.values()):
            continue
        mo = min_odd_cycle_weight(n, A, z)          # EXACT, over ALL odd cycles
        if mo is None or mo < 1:
            continue
        val = sum(w[e] * z[e] for e in E)
        y = [F(yf[k]).limit_denominator(D) for k in range(M)]
        if any(v < 0 for v in y):
            continue
        load = {e: F(0) for e in E}
        for k, cyc in enumerate(C):
            if y[k]:
                for e in cyc:
                    load[e] += y[k]
        if any(load[e] > w[e] for e in E):
            continue
        if sum(y) != val:
            continue
        print(f"    [{name}] certified at denominator {D}: cover value {val} "
              f"= packing value; #shortcycles={M}, exact min odd z-length={mo}")
        return val
    raise RuntimeError("no two-sided certificate found")


def lam_by_packing(n, A, maxlen, target, name=""):
    """Cheaper and sufficient when Q5.md claims Lambda == psi: Lambda <= psi always,
    so it is enough to exhibit a fractional odd-cycle PACKING of value psi.  Unit
    capacities; scale by N^2 at the end.  float LP steers, exact check accepts."""
    import numpy as np
    from scipy.optimize import linprog
    E = E_of(n, A)
    ei = {e: i for i, e in enumerate(E)}
    C = list(dict.fromkeys(all_cycles(n, A, only_odd=True, maxlen=maxlen)))
    M = len(C)
    Aub = np.zeros((len(E), M))
    for k, cyc in enumerate(C):
        for e in cyc:
            Aub[ei[e], k] = 1.0
    r = linprog(-np.ones(M), A_ub=Aub, b_ub=np.ones(len(E)),
                bounds=[(0, None)] * M, method="highs")
    assert r.success, r.message
    yf = r.x
    for D in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21, 24, 25, 28,
              30, 32, 35, 36, 40, 42, 45, 48, 56, 60, 63, 70, 72, 84, 90, 105, 120,
              126, 140, 168, 180, 210, 252, 280, 315, 360, 420, 504, 630, 840, 1260, 2520):
        y = [F(yf[k]).limit_denominator(D) for k in range(M)]
        if any(v < 0 for v in y):
            continue
        load = {e: F(0) for e in E}
        for k, cyc in enumerate(C):
            if y[k]:
                for e in cyc:
                    load[e] += y[k]
        if any(load[e] > 1 for e in E):
            continue
        tot = sum(y)
        if tot == target:
            used = sum(1 for v in y if v)
            print(f"    [{name}] EXACT packing certificate: {used} odd cycles of length "
                  f"<= {maxlen}, denominator {D}, value {tot} = bip -> Lambda = psi")
            return tot
    raise RuntimeError("no exact packing certificate found")


HEAVY = [
    ("C5[3]", C5n(3), F(1, 25), F(1, 25)),
]
PACKONLY = [
    ("And(5)", andrasfai(5), F(3, 98), 6, 7),
    ("And(6)", andrasfai(6), F(9, 289), 9, 7),
]
print("=== A10 heavy graphs: Lambda and psi at uniform x, two-sided exact ===")
for nm, (n, A), rep_lam, rep_psi in HEAVY:
    E = E_of(n, A)
    x = [F(1, n)] * n
    b = bip(n, A)[0]
    e_ = emass(n, A, x)
    ps = F(b, n * n)
    w = {ed: x[ed[0]] * x[ed[1]] for ed in E}
    lam = lam_exact(n, A, w, maxlen=9, name=nm)
    print(f"  {nm}: N={n} |E|={len(E)} bip={b} e={e_} psi={ps} Lambda={lam}")
    chk(f"{nm}: psi matches Q5.md", ps == rep_psi)
    chk(f"{nm}: Lambda matches Q5.md", lam == rep_lam)
    chk(f"{nm}: Lambda <= psi", lam <= ps)
    chk(f"{nm}: psi <= e-4e^2", ps <= e_ - 4 * e_ * e_)
    chk(f"{nm}: psi <= 1/25", ps <= F(1, 25))
    chk(f"{nm}: Lambda <= 1/25 (Thm A)", lam <= F(1, 25))

print("\n=== And(5), And(6): Lambda = psi by an exact packing certificate ===")
for nm, (n, A), rep_lam, target, L in PACKONLY:
    E = E_of(n, A)
    x = [F(1, n)] * n
    b = bip(n, A)[0]
    e_ = emass(n, A, x)
    ps = F(b, n * n)
    print(f"  {nm}: N={n} |E|={len(E)} bip={b} e={e_} psi={ps}")
    chk(f"{nm}: psi matches Q5.md", ps == rep_lam)
    chk(f"{nm}: bip = target", b == target)
    v = lam_by_packing(n, A, L, F(target), nm)
    lam = F(v, n * n)
    chk(f"{nm}: Lambda = psi = {rep_lam} (packing meets psi)", lam == rep_lam)
    chk(f"{nm}: psi <= e-4e^2", ps <= e_ - 4 * e_ * e_)
    chk(f"{nm}: psi <= 1/25", ps <= F(1, 25))
    chk(f"{nm}: Lambda <= 1/25 (Thm A)", lam <= F(1, 25))

print("\nFAILURES:", len(FAIL))
for f in FAIL:
    print("   ", f)
