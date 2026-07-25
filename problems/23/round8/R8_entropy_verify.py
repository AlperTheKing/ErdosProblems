"""Independent re-verification of the round-8 claims.

Deliberately written with different data structures from R8_entropy_core.py /
R8_entropy_rigidity.py: cuts are bitmasks over EDGES, bipartiteness is checked
by explicit 2-colouring BFS, induced C5s are found by walking cycles, and every
number is an exact Python integer or Fraction.
"""

from fractions import Fraction
from itertools import combinations, product


# ---------------------------------------------------------------- graphs
def _nrm(E):
    return sorted(set((min(u, v), max(u, v)) for u, v in E))


def G_grotzsch():
    E = []
    for i in range(5):
        E.append((i, (i + 1) % 5))
    for i in range(5):
        E.append((5 + i, (i + 1) % 5))
        E.append((5 + i, (i - 1) % 5))
        E.append((5 + i, 10))
    return 11, _nrm(E)


def G_wagner():
    E = [(u, v) for u in range(8) for v in range(u + 1, 8)
         if 3 * min((u - v) % 8, (v - u) % 8) > 8]
    return 8, sorted(E)


def G_petersen():
    E = set()
    for i in range(5):
        for (u, v) in [(i, (i + 1) % 5), (i, 5 + i), (5 + i, 5 + (i + 2) % 5)]:
            E.add((min(u, v), max(u, v)))
    return 10, sorted(E)


def G_and(k):
    p = 3 * k - 1
    E = set()
    for v in range(p):
        for s in range(1, p):
            if s % 3 == 1:
                u = (v + s) % p
                E.add((min(u, v), max(u, v)))
    return p, sorted(E)


# ------------------------------------------------------------- utilities
def neighbours(n, E):
    adj = [[] for _ in range(n)]
    for u, v in E:
        adj[u].append(v)
        adj[v].append(u)
    return adj


def triangle_free(n, E):
    adj = [set() for _ in range(n)]
    for u, v in E:
        adj[u].add(v)
        adj[v].add(u)
    return all(not (adj[u] & adj[v]) for u, v in E)


def bipartite(n, E):
    adj = neighbours(n, E)
    col = [-1] * n
    for s in range(n):
        if col[s] != -1:
            continue
        col[s] = 0
        st = [s]
        while st:
            v = st.pop()
            for u in adj[v]:
                if col[u] == -1:
                    col[u] = 1 - col[v]
                    st.append(u)
                elif col[u] == col[v]:
                    return False, None
    return True, col


def all_induced_c5(n, E):
    """5-subsets inducing exactly a C5, found by explicit cycle walking."""
    Eset = set(E)

    def adjq(u, v):
        return (min(u, v), max(u, v)) in Eset

    out = set()
    for S in combinations(range(n), 5):
        cnt = sum(1 for u, v in combinations(S, 2) if adjq(u, v))
        if cnt != 5:
            continue
        # 5 vertices, 5 edges, 2-regular and connected  <=>  C5
        if any(sum(1 for u in S if adjq(v, u)) != 2 for v in S):
            continue
        seen, st = {S[0]}, [S[0]]
        while st:
            v = st.pop()
            for u in S:
                if adjq(u, v) and u not in seen:
                    seen.add(u)
                    st.append(u)
        if len(seen) == 5:
            out.add(S)
    return sorted(out)


def mono_edges(E, side):
    return [(u, v) for (u, v) in E if side[u] == side[v]]


def rainbow1(n, E, pents):
    """All cuts whose mono set meets every induced C5 exactly once."""
    Eset = set(E)
    pent_edges = []
    for S in pents:
        s = set(S)
        pent_edges.append(set(e for e in E if e[0] in s and e[1] in s))
    res = []
    for mask in range(1 << (n - 1)):
        side = [(mask >> v) & 1 if v < n - 1 else 0 for v in range(n)]
        M = set(mono_edges(E, side))
        if all(len(M & pe) == 1 for pe in pent_edges):
            res.append((side[:], sorted(M)))
    return res


def psi_all_cuts(n, E, a):
    best = None
    for mask in range(1 << (n - 1)):
        side = [(mask >> v) & 1 if v < n - 1 else 0 for v in range(n)]
        t = sum(a[u] * a[v] for (u, v) in E if side[u] == side[v])
        best = t if best is None else min(best, t)
    return best


# ------------------------------------------------------------------ main
if __name__ == "__main__":
    print("### 1. Grotzsch: the kill of every fixed cut certificate\n")
    n, E = G_grotzsch()
    assert triangle_free(n, E), "Grotzsch must be triangle-free"
    print(f"n={n}, |E|={len(E)}, triangle-free={triangle_free(n,E)}, "
          f"bipartite={bipartite(n,E)[0]}")
    pents = all_induced_c5(n, E)
    print(f"induced C5s: {len(pents)}")
    R = rainbow1(n, E, pents)
    print(f"rainbow-1 cuts: {len(R)}")
    classes = [M for _, M in R]
    for j, (side, M) in enumerate(R):
        rest = [e for e in E if e not in set(M)]
        ok, _ = bipartite(n, rest)
        print(f"  F_{j+1} = {M}\n"
              f"        side = {side}, |F|={len(M)}, E\\F bipartite = {ok}")
    flat = [e for M in classes for e in M]
    print(f"  classes partition E : {sorted(flat) == sorted(E)} "
          f"(|union|={len(set(flat))}, |E|={len(E)})")

    a = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 5]
    q = sum(a)
    print(f"\n  killing weighting a = {a}, sum a = {q}")
    print(f"  support induces:  vertices with a>0 = "
          f"{[v for v in range(n) if a[v]>0]}")
    sub = [(u, v) for (u, v) in E if a[u] > 0 and a[v] > 0]
    print(f"  induced subgraph on the support: {sub}  bipartite="
          f"{bipartite(n, sub)[0]}  -> psi = "
          f"{psi_all_cuts(n,E,a)} (exact, all {2**(n-1)} cuts)")
    vals = [sum(a[u] * a[v] for (u, v) in M) for M in classes]
    print(f"  m_S(a) for the five rainbow-1 cuts: {vals}")
    print(f"  min over rainbow-1 cuts = {min(vals)} = "
          f"{Fraction(min(vals), q*q)} of (sum a)^2")
    print(f"  1/25 of (sum a)^2       = {Fraction(q*q,25)}")
    print(f"  VERDICT: min over the admissible support is "
          f"{Fraction(min(vals), q*q)} > 1/25 = {Fraction(1,25)}   -> "
          f"{'KILL' if Fraction(min(vals), q*q) > Fraction(1,25) else 'no kill'}")

    print("\n### 2. And(4): no rainbow-1 cut at all\n")
    n4, E4 = G_and(4)
    p4 = all_induced_c5(n4, E4)
    R4 = rainbow1(n4, E4, p4)
    print(f"And(4): n={n4} |E|={len(E4)} triangle-free={triangle_free(n4,E4)} "
          f"induced C5s={len(p4)} rainbow-1 cuts={len(R4)}")

    print("\n### 3. Wagner and Petersen: the route survives the rigidity test\n")
    for nm, (n2, E2) in [("Wagner", G_wagner()), ("Petersen", G_petersen())]:
        p2 = all_induced_c5(n2, E2)
        R2 = rainbow1(n2, E2, p2)
        cl = [M for _, M in R2]
        flat = [e for M in cl for e in M]
        maxdeg = max(sum(1 for e in E2 if v in e) for v in range(n2))
        print(f"{nm}: n={n2} |E|={len(E2)} indC5={len(p2)} rainbow-1={len(R2)} "
              f"partition={sorted(flat)==sorted(E2)} maxdeg={maxdeg}")
        for j, M in enumerate(cl):
            rest = [e for e in E2 if e not in set(M)]
            print(f"   F_{j+1} = {M}   E\\F bipartite={bipartite(n2,rest)[0]}")
