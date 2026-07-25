"""AUDIT of the graph-level EXACT VALUES claimed in Q4.md.  Own everything, exact integers.

Checks:
  F1  Gamma_8 = Wagner (Moebius ladder on 8 vertices), 12 edges, maxcut, bip
  F2  Petersen = Kneser K(5,2), 15 edges, maxcut, bip
  F3  induced C5 counts
  F4  homomorphism to C5: exhaustive backtracking (own)
  F5  the ten round5 witnesses evaluated against the certified bound psi <= L^2/25
  F6  exact tightness on C5[n]: 25*bip(C5[n]) - N^2 == 0
"""
from fractions import Fraction as F
from itertools import combinations, product


def gamma_graph(n):
    third = F(1, 3)
    return [[(i != j and min(F((i - j) % n, n), F((j - i) % n, n)) > third) for j in range(n)]
            for i in range(n)]


def petersen():
    V = sorted(combinations(range(5), 2))
    return [[(i != j and not (set(V[i]) & set(V[j]))) for j in range(len(V))] for i in range(len(V))]


def cycle(n):
    return [[(abs(i - j) % n == 1 or abs(i - j) % n == n - 1) for j in range(n)] for i in range(n)]


def edges_of(adj):
    n = len(adj)
    return [(i, j) for i in range(n) for j in range(i + 1, n) if adj[i][j]]


def maxcut_bruteforce(adj):
    """own max-cut: exhaustive over 2^(n-1) bipartitions, integer counting."""
    n = len(adj)
    E = edges_of(adj)
    best = -1
    for mask in range(1 << (n - 1)):
        side = [0] + [(mask >> (v - 1)) & 1 for v in range(1, n)]
        c = sum(1 for u, v in E if side[u] != side[v])
        if c > best:
            best = c
    return best, len(E)


def blowup_bip(adj, a):
    """bip(H[a]) = min over cuts of H of sum over monochromatic uv of a_u a_v  (exact integers)."""
    n = len(adj)
    E = edges_of(adj)
    best = None
    for mask in range(1 << (n - 1)):
        side = [0] + [(mask >> (v - 1)) & 1 for v in range(1, n)]
        s = sum(a[u] * a[v] for u, v in E if side[u] == side[v])
        if best is None or s < best:
            best = s
    return best


def blowup_bip_direct(adj, a):
    """independent cross-check: build the blow-up graph explicitly and brute-force its max cut."""
    n = len(adj)
    verts = []
    for v in range(n):
        verts += [v] * a[v]
    N = len(verts)
    E = [(i, j) for i in range(N) for j in range(i + 1, N) if adj[verts[i]][verts[j]]]
    best = -1
    for mask in range(1 << (N - 1)):
        side = [0] + [(mask >> (t - 1)) & 1 for t in range(1, N)]
        c = sum(1 for u, v in E if side[u] != side[v])
        best = max(best, c)
    return len(E) - best


def induced_c5s(adj):
    n = len(adj)
    out = []
    for S in combinations(range(n), 5):
        sub = [[adj[u][v] for v in S] for u in S]
        deg = [sum(r) for r in sub]
        ne = sum(sum(r) for r in sub) // 2
        if ne == 5 and all(d == 2 for d in deg):
            out.append(S)             # 2-regular on 5 vertices and connected => C5
    return out


def hom_to_c5(adj):
    """exhaustive backtracking search for a homomorphism H -> C5."""
    n = len(adj)
    c5 = cycle(5)
    col = [-1] * n

    def rec(v):
        if v == n:
            return True
        for k in range(5):
            if all(not (adj[v][u] and col[u] >= 0 and not c5[k][col[u]]) for u in range(v)):
                col[v] = k
                if rec(v + 1):
                    return True
                col[v] = -1
        return False
    return rec(0)


def report():
    print("== F1/F2 basic invariants ==")
    for name, adj in [("Gamma_8", gamma_graph(8)), ("Gamma_11", gamma_graph(11)),
                      ("Petersen", petersen()), ("C5", cycle(5))]:
        mc, ne = maxcut_bruteforce(adj)
        degs = sorted(sum(r) for r in adj)
        print(f"  {name:9s} n={len(adj):2d} |E|={ne:3d} maxcut={mc:3d} bip={ne-mc:2d} "
              f"degrees={degs[0]}..{degs[-1]}  triangle-free="
              f"{not any(adj[a][b] and adj[b][c] and adj[a][c] for a,b,c in combinations(range(len(adj)),3))}")

    print("== F3 induced C5s ==")
    for name, adj in [("Gamma_8", gamma_graph(8)), ("Petersen", petersen()),
                      ("Gamma_11", gamma_graph(11))]:
        c = induced_c5s(adj)
        print(f"  {name:9s} induced C5 count = {len(c)}   example {c[0] if c else None}")

    print("== F4 homomorphism to C5 ==")
    for name, adj in [("Gamma_8", gamma_graph(8)), ("Petersen", petersen()),
                      ("Gamma_11", gamma_graph(11)), ("C5", cycle(5))]:
        print(f"  {name:9s} hom to C5: {hom_to_c5(adj)}")

    print("== F5 the ten round5 witnesses, exact psi (min over ALL cuts) vs 1/25 ==")
    WIT = [("W1 half-arc killer", 8, [0, 1, 0, 1, 2, 0, 2, 1]),
           ("W1' Gamma_11", 11, [0, 0, 1, 0, 0, 1, 2, 0, 0, 2, 1]),
           ("W1'' Gamma_16", 16, [0, 0, 0, 1, 0, 0, 0, 1, 0, 2, 0, 0, 0, 2, 0, 1]),
           ("W2 five-atom extremal", 5, [1, 1, 1, 1, 1]),
           ("W3 uniform Gamma_18", 18, [1] * 18),
           ("W4 uniform Gamma_20", 20, [1] * 20),
           ("W5 three-atom near-path", 12, [3, 0, 0, 0, 3, 0, 0, 0, 0, 3, 0, 0]),
           ("W6 seven-atom", 7, [1] * 7),
           ("W8 far-regular Wagner", 14, [1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0]),
           ("W7 unequal five-atom", 20, [0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 1, 3, 0, 0, 0, 0, 0, 1, 3])]
    for wname, m, w in WIT:
        adj = gamma_graph(m)
        N = sum(w)
        b = blowup_bip(adj, w)
        psi = F(b, N * N)
        flag = "OK" if psi <= F(1, 25) else "*** EXCEEDS 1/25 -> CONJECTURE FALSE ***"
        print(f"  {wname:24s} m={m:3d} N={N:3d} bip={b:4d} psi={psi} = {float(psi):.6f}  {flag}")

    print("== F6 exact tightness on C5[n] (any bound must be tight here) ==")
    for k in range(1, 9):
        a = [k] * 5
        b = blowup_bip(cycle(5), a)
        print(f"  C5[{k}^5]: N={5*k} bip={b}  25*bip-N^2 = {25*b - (5*k)**2}")
    for a in [[1, 2, 1, 1, 2], [2, 3, 2, 3, 2], [1, 1, 2, 1, 1]]:
        N = sum(a)
        b = blowup_bip(cycle(5), a)
        print(f"  C5{a}: N={N} bip={b}  25*bip-N^2 = {25*b - N*N}")

    print("== F7 cross-check of the blow-up identity against a direct max-cut of the blow-up ==")
    for a in [[1, 1, 1, 1, 1, 0, 0, 0], [2, 1, 1, 1, 1, 1, 1, 2], [0, 2, 0, 2, 2, 0, 2, 2]]:
        adj = gamma_graph(8)
        b1 = blowup_bip(adj, a)
        b2 = blowup_bip_direct(adj, a)
        print(f"  a={a}  identity={b1}  direct max-cut={b2}  {'MATCH' if b1 == b2 else '*** MISMATCH ***'}")


if __name__ == '__main__':
    report()
