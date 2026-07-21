#!/usr/bin/env python3
"""
hive_poly.py -- WAVE-3 triage oracle for the KTT stretched-LR negativity hunt.

Builds the Knutson-Tao hive polytope Q(lam,mu,nu) EXACTLY (same rhombus model
and boundary convention as engine A / lr_hive.cpp, see engine/BUILD_A.md), and
returns, WITHOUT counting a single lattice point:

  * dim Q            = deg P   (Ehrhart degree = polytope dimension)
  * max vertex denominator q  (q >= 2  ==>  Q is NOT a lattice polytope)
  * the exact vertices found (Fractions), each certified feasible over Q

Why this matters in wave 3:
  - deg P is obtained in ~1 s instead of ~5 min of stretched LR counting, so a
    hunter can pre-select the dim-9/10 (r=6) stratum before spending profiles.
  - with d = dim Q known, the h*-prefix h*_j = sum_{i<=j} (-1)^i C(d+1,i) P(j-i)
    can be computed from the CHEAP low-n samples only (n = 0..j).  Any h*_j < 0
    is a rigorous non-integrality signature (Stanley: lattice polytopes have
    h* >= 0) and is exactly the region waves 1-2 never entered.
  - h*_1 < 0  <==>  c <= deg P.  For a LATTICE polytope c = P(1) >= dim+1
    always (the d+1 affinely independent vertices are lattice points), so
    c <= deg is by itself a proof of non-integrality.

RIGOR CONTRACT
  - Every returned vertex is verified EXACTLY (Fraction arithmetic) to satisfy
    all rhombus inequalities and to make d linearly independent of them tight;
    a reported denominator >= 2 is therefore a genuine certificate.
  - `dim_lo` (affine rank of certified vertices) is a RIGOROUS lower bound.
  - `dim_hi` is heuristic (constraints tight at every sampled vertex).
  - The float LP is used ONLY to choose which basis to solve exactly.  It is a
    TRIAGE device: no mathematical verdict may rest on it.  Every promoted
    candidate must still be settled by exact stretched counts + exact
    interpolation + the mandatory held-out points P(D+1), P(D+2).

CLI
  python hive_poly.py "lam" "mu" "nu" [K]     -> one JSON line
  python hive_poly.py --batch file            -> lines "lam;mu;nu", one JSON out
  python hive_poly.py --selftest              -> exit 0 on pass
"""

import json
import sys
from fractions import Fraction

import numpy as np
from scipy.optimize import linprog
from sympy import Matrix, Rational


# ---------------------------------------------------------------- geometry
def build(lam, mu, nu):
    """Return (A, b, d, interior, ok) with Q = {h in Q^d : A h <= b}."""
    n = len(nu)
    lam = list(lam) + [0] * (n - len(lam))
    mu = list(mu) + [0] * (n - len(mu))
    B = {}
    ps = lambda p, k: sum(p[:k])
    for y in range(n + 1):
        B[(0, y)] = ps(lam, y)
    for x in range(n + 1):
        B[(x, n - x)] = sum(lam) + ps(mu, x)
    for x in range(n + 1):
        B[(x, 0)] = ps(nu, x)
    B[(0, 0)] = 0
    interior = [(x, y) for x in range(1, n) for y in range(1, n) if x + y <= n - 1]
    idx = {v: i for i, v in enumerate(interior)}
    d = len(interior)
    A, b = [], []
    ok = True

    def add(plus, minus):
        co = [0] * d
        const = 0
        for v in plus:
            if v in idx:
                co[idx[v]] -= 1
            else:
                const -= B[v]
        for v in minus:
            if v in idx:
                co[idx[v]] += 1
            else:
                const += B[v]
        if all(c == 0 for c in co):
            return const <= 0
        A.append(co)
        b.append(-const)
        return True

    for x in range(0, n + 1):
        for y in range(0, n + 1):
            if x + y <= n - 2:
                ok &= add([(x + 1, y), (x, y + 1)], [(x, y), (x + 1, y + 1)])
            if y >= 1 and x + y <= n - 1:
                ok &= add([(x, y), (x + 1, y)], [(x, y + 1), (x + 1, y - 1)])
            if x >= 1 and x + y <= n - 1:
                ok &= add([(x, y), (x, y + 1)], [(x + 1, y), (x - 1, y + 1)])
    return A, b, d, interior, ok


def analyze(lam, mu, nu, K=25, seed=7):
    """Sample K exact vertices by random objectives. Returns dict or None."""
    A, b, d, interior, ok = build(lam, mu, nu)
    if not ok:
        return None                       # boundary data already infeasible
    if d == 0:
        return dict(d=0, dim_lo=0, dim_hi=0, maxden=1, nverts=1, verts=[])
    An = np.array(A, dtype=float)
    bn = np.array(b, dtype=float)
    Aq = Matrix([[Rational(v) for v in row] for row in A])
    bq = Matrix([Rational(v) for v in b])
    import random as _r
    rng = _r.Random(seed)
    verts, alltight = [], None
    for _ in range(K):
        w = [rng.randint(-1000, 1000) for _ in range(d)]
        res = linprog(np.array(w, dtype=float), A_ub=An, b_ub=bn,
                      bounds=[(None, None)] * d, method="highs")
        if not res.success:
            return None
        x = res.x
        tight = [i for i in range(len(A)) if abs(An[i] @ x - bn[i]) < 1e-6]
        if not tight:
            continue
        cur = Matrix.zeros(0, d)
        rows = []
        for i in tight:
            trial = cur.col_join(Matrix([[Rational(A[i][j]) for j in range(d)]]))
            if trial.rank() > cur.rank():
                cur = trial
                rows.append(i)
            if len(rows) == d:
                break
        if len(rows) < d:
            continue
        sol = cur.solve(Matrix([Rational(b[i]) for i in rows]))
        prod = Aq * sol
        if any(prod[i] > bq[i] for i in range(len(A))):
            continue                       # exact feasibility failed -> drop
        verts.append(sol)
        tset = set(i for i in range(len(A)) if prod[i] == bq[i])
        alltight = tset if alltight is None else (alltight & tset)
    if not verts:
        return None
    V = Matrix.hstack(*verts).T
    dim_lo = (V - Matrix.ones(V.rows, 1) * V.row(0)).rank()
    if alltight:
        E = Matrix([[Rational(A[i][j]) for j in range(d)] for i in sorted(alltight)])
        dim_hi = d - E.rank()
    else:
        dim_hi = d
    maxden = max(max(q.q for q in v) for v in verts)
    return dict(d=d, dim_lo=int(dim_lo), dim_hi=int(dim_hi), maxden=int(maxden),
                nverts=len(verts),
                verts=[[str(q) for q in v] for v in verts[:3]])


# ---------------------------------------------------------------- h* prefix
def hstar_prefix(d, samples):
    """h*_j for j = 0..len(samples)-1 given d = dim and samples[n] = P(n), n=0..

    h*_j = sum_{i=0}^{j} (-1)^i C(d+1,i) P(j-i).  Exact integers.
    Requires d to be correct; a defect flag must always be escalated to a full
    exact profile + interpolation before it is believed.
    """
    from math import comb
    out = []
    for j in range(len(samples)):
        out.append(sum((-1) ** i * comb(d + 1, i) * samples[j - i] for i in range(j + 1)))
    return out


# ---------------------------------------------------------------- selftest
def _selftest():
    fails = 0
    # (lam, mu, nu, expected dim)   -- expectations verified against engine A
    cases = [
        ((2, 1), (1,), (3, 1), 0),                       # c=1  -> point
        ((2, 1), (2, 1), (3, 2, 1), 1),                  # c=2  -> segment
        ((6, 5, 4, 3, 2, 1), (6, 5, 4, 3, 2, 1), (11, 9, 8, 7, 5, 2), 6),
        ((5, 4, 3, 2, 1), (5, 4, 3, 2, 1), (9, 7, 6, 4, 3, 1), 10),
    ]
    for lam, mu, nu, exp in cases:
        r = analyze(lam, mu, nu, K=30, seed=7)
        got = None if r is None else r["dim_lo"]
        okk = (got == exp and (r is None or r["dim_lo"] == r["dim_hi"]))
        print(f"dim {lam} {mu} {nu}: got {got} expect {exp} {'OK' if okk else 'FAIL'}")
        fails += 0 if okk else 1
    # h*-prefix against the exactly interpolated c=12 example
    hs = hstar_prefix(6, [1, 12, 74, 304])
    okk = hs == [1, 5, 11, 3]
    print(f"hstar_prefix: got {hs} expect [1, 5, 11, 3] {'OK' if okk else 'FAIL'}")
    fails += 0 if okk else 1
    print("SELFTEST", "PASS" if fails == 0 else f"FAIL({fails})")
    return 0 if fails == 0 else 1


def _p(s):
    return tuple(int(t) for t in s.replace(";", ",").split(",") if t.strip())


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "--selftest":
        sys.exit(_selftest())
    if len(sys.argv) >= 3 and sys.argv[1] == "--batch":
        for line in open(sys.argv[2]):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            a, b_, c_ = line.split(";")[:3]
            r = analyze(_p(a), _p(b_), _p(c_))
            print(json.dumps({"lam": a, "mu": b_, "nu": c_, "res": r}))
        sys.exit(0)
    K = int(sys.argv[4]) if len(sys.argv) > 4 else 25
    print(json.dumps(analyze(_p(sys.argv[1]), _p(sys.argv[2]), _p(sys.argv[3]), K=K)))
