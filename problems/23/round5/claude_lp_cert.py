"""ROOT-AGENT certificate engine (Claude, round 5): LP-based x-dependent certificates for the
psi-ceiling, and the first attempt at the Wagner graph.

The verified C5 certificate (R3-C14) has the shape: quadratic forms lambda_S(x) >= 0, one per cut S
in a chosen family, with sum_S lambda_S = (sum x)^2, such that

        P(x) := (sum x)^4 - 25 * sum_S lambda_S(x) q_S(x)   is nonnegative on the orthant.

The SOS route certifies that nonnegativity with Gram matrices.  But there is a far cheaper
sufficient condition: P has ALL COEFFICIENTS NONNEGATIVE.  That turns the whole search into a
LINEAR PROGRAM in the entries of the lambda matrices, whose exact rational solution IS the
certificate and whose verification is a coefficient sign check.

If it is feasible this scales to patterns where the SOS route does not.
"""
import sys
import numpy as np
from fractions import Fraction as F
from itertools import combinations
from scipy.optimize import linprog


def gamma(m):
    return [[(u != v and 3 * min((u - v) % m, (v - u) % m) > m) for v in range(m)] for u in range(m)]


def cyc(m):
    return [[(u != v and min((u - v) % m, (v - u) % m) == 1) for v in range(m)] for u in range(m)]


def mono_edges(n, adj, inA):
    return [(u, v) for u, v in combinations(range(n), 2) if adj[u][v] and inA[u] == inA[v]]


def arc_cuts(n, lengths):
    out = []
    for i in range(n):
        for l in lengths:
            inA = [False] * n
            for t in range(l):
                inA[(i + t) % n] = True
            out.append(tuple(inA))
    seen, res = set(), []
    for c in out:
        k = min(c, tuple(not b for b in c))
        if k not in seen:
            seen.add(k); res.append(c)
    return res


def build_lp(n, adj, cuts):
    """variables: for each cut index s and each pair i<=j, the coefficient L_s[i][j] of z_i z_j
    (symmetric, so off-diagonals count twice).  Constraints:
      (a) sum_s L_s = J   (all-ones)          -> equality rows
      (b) all coefficients of P nonnegative   -> inequality rows
      (c) L_s >= 0 entrywise                  -> variable bounds
    """
    pairs = [(i, j) for i in range(n) for j in range(i, n)]
    nv = len(cuts) * len(pairs)

    def vidx(s, i, j):
        return s * len(pairs) + pairs.index((min(i, j), max(i, j)))

    # monomials of degree 4 in z, as sorted tuples
    monos = {}
    def midx(t):
        t = tuple(sorted(t))
        if t not in monos:
            monos[t] = len(monos)
        return monos[t]

    # (sum z)^4 coefficients
    rhs = {}
    for a in range(n):
        for b in range(n):
            for c in range(n):
                for d in range(n):
                    k = midx((a, b, c, d))
                    rhs[k] = rhs.get(k, 0) + 1

    # 25 * sum_s lambda_s(z) q_s(z)
    A = {}
    for s, inA in enumerate(cuts):
        for (u, v) in mono_edges(n, adj, inA):
            for (i, j) in pairs:
                k = midx((i, j, u, v))
                coef = 25 * (1 if i == j else 2)
                A[(k, vidx(s, i, j))] = A.get((k, vidx(s, i, j)), 0) + coef

    nm = len(monos)
    Aub = np.zeros((nm, nv))
    bub = np.zeros(nm)
    for (k, vi), c in A.items():
        Aub[k, vi] += c
    for k, c in rhs.items():
        bub[k] = c
    # constraint:  sum_s 25 lambda_s q_s  <=  (sum z)^4   coefficientwise
    Aeq = np.zeros((len(pairs), nv))
    beq = np.zeros(len(pairs))
    for pi, (i, j) in enumerate(pairs):
        for s in range(len(cuts)):
            Aeq[pi, vidx(s, i, j)] = 1
        beq[pi] = 1
    return Aub, bub, Aeq, beq, nv, pairs, vidx, monos


def try_pattern(name, n, adj, cuts):
    Aub, bub, Aeq, beq, nv, pairs, vidx, monos = build_lp(n, adj, cuts)
    res = linprog(np.zeros(nv), A_ub=Aub, b_ub=bub, A_eq=Aeq, b_eq=beq,
                  bounds=[(0, None)] * nv, method='highs')
    print(f"{name}: n={n} cuts={len(cuts)} vars={nv} monomials={len(monos)} -> "
          f"{'FEASIBLE' if res.success else 'INFEASIBLE'} ({res.message.strip()[:60]})")
    if not res.success:
        return None
    # round to rationals with denominator D and re-check exactly
    x = res.x
    for D in (2, 4, 8, 16, 40, 80, 240, 720, 5040):
        L = [[[F(0)] * n for _ in range(n)] for _ in cuts]
        for s in range(len(cuts)):
            for (i, j) in pairs:
                val = F(int(round(x[vidx(s, i, j)] * D)), D)
                L[s][i][j] = val
                L[s][j][i] = val
        # exact check (a): sum_s L_s = J
        if not all(sum(L[s][i][j] for s in range(len(cuts))) == 1 for i in range(n) for j in range(n)):
            continue
        # exact check (b): coefficients of P nonnegative
        coef = {}
        for a in range(n):
            for b in range(n):
                for c in range(n):
                    for d in range(n):
                        t = tuple(sorted((a, b, c, d)))
                        coef[t] = coef.get(t, F(0)) + 1
        for s, inA in enumerate(cuts):
            for (u, v) in mono_edges(n, adj, inA):
                for i in range(n):
                    for j in range(n):
                        t = tuple(sorted((i, j, u, v)))
                        coef[t] = coef.get(t, F(0)) - 25 * L[s][i][j]
        bad = [(t, c) for t, c in coef.items() if c < 0]
        if not bad:
            print(f"   EXACT certificate found with denominator {D}: all {len(coef)} coefficients of P are >= 0")
            return L, D
    print("   rounding failed at every denominator tried (LP solution is not exactly representable there)")
    return None


if __name__ == '__main__':
    print("=== C5: does the LP form already certify?  (psi(C5,x) = min over edges) ===")
    n = 5; adj = cyc(5)
    cuts5 = arc_cuts(5, [2])          # the five rotation cuts {i,i+2}: each leaves one edge mono
    try_pattern("C5 (rotation cuts)", n, adj, cuts5)

    print("\n=== Wagner = Gamma_8 = C8(1,4) ===")
    n = 8; adjw = gamma(8)
    for lens, tag in (([3], "neighbourhood cuts only"),
                      ([3, 4], "neighbourhood + half arcs"),
                      ([2, 3, 4], "arcs of length 2,3,4")):
        try_pattern(f"Wagner ({tag})", n, adjw, arc_cuts(8, lens))
