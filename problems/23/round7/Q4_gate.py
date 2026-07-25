"""Q4 ROOT GATE: independent exact verification of the Gamma_m certificate.

Shares NO code with the constructor: the graph, the cuts, polynomial arithmetic, the substitution
x = y^2, and positive semidefiniteness are all re-done here from the definitions, with Fractions
only.  Reads Q4_cert_g<m>_d<d>.pkl and checks, from scratch:

  G1  the vertex set / edge set really is the circle graph Gamma_m (circular distance > 1/3), and
      it is triangle-free;
  G2  every cut used in the certificate really is a cut of that graph, and q_S is its monochromatic
      quadratic form;
  G3  every multiplier coefficient is >= 0;
  G4  sum_S nu_S == 25 * (sum_j x_j)^2  as polynomials;
  G5  (sum_j x_j)^4 - sum_S nu_S * q_S  equals, after x_j -> y_j^2, the quadratic form
      sum_b v_b^T Q_b v_b  in the y-monomials -- as polynomials in y;
  G6  every Q_b is positive semidefinite (own rational LDL^T with symmetric pivoting).

G3-G6 imply, for every x >= 0 with L = sum x_j:  sum_S (nu_S(x)/(25 L^2)) q_S(x) <= L^2/25 with
nu_S(x)/(25L^2) a probability distribution, hence min_S q_S(x) <= L^2/25, hence
psi(Gamma_m, x) <= L^2/25 (the true psi is a minimum over ALL cuts, so using a subfamily is
conservative), i.e. max_x psi <= 1/25 and bip(Gamma_m[a]) <= (sum a)^2/25 for every blow-up.
"""
import sys, pickle
from fractions import Fraction as F
from itertools import combinations


def pmul(a, b):
    out = {}
    for ea, ca in a.items():
        for eb, cb in b.items():
            e = tuple(x + y for x, y in zip(ea, eb))
            out[e] = out.get(e, F(0)) + ca * cb
    return {e: c for e, c in out.items() if c != 0}


def padd(a, b):
    out = dict(a)
    for e, c in b.items():
        out[e] = out.get(e, F(0)) + c
    return {e: c for e, c in out.items() if c != 0}


def psub(a, b):
    return padd(a, {e: -c for e, c in b.items()})


def ppow(a, k):
    r = {tuple([0] * len(next(iter(a)))): F(1)}
    for _ in range(k):
        r = pmul(r, a)
    return r


def subst_squares(p, n):
    """x_j -> y_j^2."""
    return {tuple(2 * e for e in ex): c for ex, c in p.items()}


def ldl_psd(M):
    k = len(M)
    A = [[F(M[i][j]) for j in range(k)] for i in range(k)]
    for step in range(k):
        p = max(range(step, k), key=lambda i: A[i][i])
        if A[p][p] < 0:
            return False, f"negative pivot {A[p][p]}"
        if A[p][p] == 0:
            for i in range(step, k):
                for j in range(step, k):
                    if A[i][j] != 0:
                        return False, "zero diagonal with nonzero off-diagonal"
            return True, "psd"
        A[step], A[p] = A[p], A[step]
        for r in range(k):
            A[r][step], A[r][p] = A[r][p], A[r][step]
        d = A[step][step]
        for i in range(step + 1, k):
            f = A[i][step] / d
            if f:
                for j in range(step, k):
                    A[i][j] -= f * A[step][j]
    return True, "psd"


def main(path):
    C = pickle.load(open(path, "rb"))
    m, n, d, c = C['m'], C['n'], C['d'], C['c']
    print(f"GATE on {path}: pattern {m}, n={n}, multiplier degree {2*d}, c={c}")
    assert d == 1 and c == F(25)

    # G1 -- rebuild the graph from its own definition
    if str(m).lower() == 'petersen':
        V = sorted(combinations(range(5), 2))          # Kneser graph K(5,2)
        idx = {v: i for i, v in enumerate(V)}
        edges = sorted((idx[a], idx[b]) for a, b in combinations(V, 2) if not set(a) & set(b))
        assert n == 10
    else:
        assert n == int(m)
        edges = []                                     # circle graph Gamma_m
        for i in range(n):
            for j in range(i + 1, n):
                if 3 * min(j - i, n - (j - i)) > n:
                    edges.append((i, j))
    assert sorted(map(tuple, C['E'])) == sorted(edges), "edge set does not match the pattern"
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = adj[v][u] = True
    for u, v, w in combinations(range(n), 3):
        assert not (adj[u][v] and adj[v][w] and adj[u][w]), "graph has a triangle"
    print(f"  G1 ok: pattern {m} rebuilt from its own definition, triangle-free, {len(edges)} edges")

    # G2 -- every listed cut is a genuine cut and its monochromatic edge list is right
    qpolys = []
    for mask, mono in C['cuts']:
        side = [0 if v == 0 else (mask >> (v - 1)) & 1 for v in range(n)]
        want = {k for k, (u, v) in enumerate(C['E']) if side[u] == side[v]}
        assert set(mono) == want, "monochromatic edge set does not match the stated cut"
        q = {}
        for k in mono:
            u, v = C['E'][k]
            e = [0] * n
            e[u] += 1
            e[v] += 1
            q[tuple(e)] = q.get(tuple(e), F(0)) + 1
        qpolys.append(q)
    print(f"  G2 ok: all {len(qpolys)} cuts verified as bipartitions of the vertex set")

    # G3/G4
    nu = [{} for _ in qpolys]
    for (S, mm), val in C['nu'].items():
        assert val >= 0, "negative multiplier coefficient"
        nu[S][tuple(mm)] = nu[S].get(tuple(mm), F(0)) + val
    print(f"  G3 ok: {sum(len(x) for x in nu)} multiplier coefficients, all >= 0, "
          f"max denominator {max((v.denominator for v in C['nu'].values()))}")
    L = {tuple(1 if i == j else 0 for i in range(n)): F(1) for j in range(n)}
    tot = {}
    for x in nu:
        tot = padd(tot, x)
    assert tot == {e: F(25) * cc for e, cc in ppow(L, 2).items()}, "sum of multipliers != 25 L^2"
    print("  G4 ok: sum_S nu_S == 25 * L^2 as polynomials")

    # G5
    T = ppow(L, 4)
    for x, q in zip(nu, qpolys):
        T = psub(T, pmul(x, q))
    Ty = subst_squares(T, n)
    G = {}
    for B, M in C['Q']:
        k = len(B)
        for i in range(k):
            for j in range(k):
                if M[i][j]:
                    e = tuple(B[i][t] + B[j][t] for t in range(n))
                    G[e] = G.get(e, F(0)) + M[i][j]
    G = {e: v for e, v in G.items() if v != 0}
    assert Ty == G, f"polynomial identity fails ({len(set(Ty) ^ set(G))} differing monomials)"
    print(f"  G5 ok: L^4 - sum nu_S q_S == sum_b v_b^T Q_b v_b after x = y^2 "
          f"({len(Ty)} monomials matched)")

    # G6
    for bi, (B, M) in enumerate(C['Q']):
        ok, info = ldl_psd(M)
        assert ok, f"block {bi} not PSD: {info}"
    print(f"  G6 ok: all {len(C['Q'])} Gram blocks positive semidefinite "
          f"(sizes {sorted({len(B) for B, _ in C['Q']}, reverse=True)})")
    print(f"GATE PASSED: max_x psi({m}, x) <= 1/25, hence bip({m}[a]) <= (sum a)^2/25 for every blow-up.")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "Q4_cert_g8_d1.pkl")
