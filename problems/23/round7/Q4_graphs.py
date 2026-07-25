"""Q4 shared infrastructure: Andrasfai circle graphs, cuts, exact psi facts.

Everything here is exact (Fraction / integers).  No floating point on any acceptance path.
"""
from fractions import Fraction
from itertools import combinations, product
import sys


def gamma_graph(m):
    """Circle graph Gamma_m: vertices Z_m at i/m, i~j iff circular distance > 1/3.
    And(k) = Gamma_{3k-1}."""
    E = []
    for i in range(m):
        for j in range(i + 1, m):
            d = min(j - i, m - (j - i))
            # circular distance d/m > 1/3  <=>  3d > m
            if 3 * d > m:
                E.append((i, j))
    return m, sorted(E)


def cycle(m):
    return m, sorted((i, (i + 1) % m) if i + 1 < m else (0, i) for i in range(m))


def adj(n, E):
    A = [[0] * n for _ in range(n)]
    for u, v in E:
        A[u][v] = A[v][u] = 1
    return A


def is_triangle_free(n, E):
    A = adj(n, E)
    for u, v, w in combinations(range(n), 3):
        if A[u][v] and A[v][w] and A[u][w]:
            return False
    return True


def automorphisms(n, E):
    """Brute-force automorphism group (n <= 11 fine with pruning)."""
    A = adj(n, E)
    deg = [sum(A[v]) for v in range(n)]
    res = []
    perm = [-1] * n
    used = [False] * n

    def rec(i):
        if i == n:
            res.append(tuple(perm))
            return
        for c in range(n):
            if used[c] or deg[c] != deg[i]:
                continue
            ok = True
            for j in range(i):
                if A[i][j] != A[c][perm[j]]:
                    ok = False
                    break
            if ok:
                used[c] = True
                perm[i] = c
                rec(i + 1)
                used[c] = False
                perm[i] = -1
    rec(0)
    return res


def all_cuts(n, E):
    """All 2^(n-1) cuts up to complementation, as (mask, frozenset of monochromatic edge indices)."""
    out = []
    for mask in range(1 << (n - 1)):  # vertex 0 always on side 0
        mono = frozenset(k for k, (u, v) in enumerate(E)
                         if ((mask >> (u - 1) & 1) if u else 0) == ((mask >> (v - 1) & 1) if v else 0))
        out.append((mask, mono))
    return out


def nondominated_cuts(cuts):
    """Keep cuts whose monochromatic edge set is minimal under inclusion (and dedupe)."""
    sets = {}
    for mask, mono in cuts:
        if mono not in sets:
            sets[mono] = mask
    keys = list(sets)
    keep = []
    for a in keys:
        if not any(b < a for b in keys if b != a):  # b strictly contained in a
            keep.append((sets[a], a))
    return sorted(keep, key=lambda t: (len(t[1]), sorted(t[1])))


def induced_C5s(n, E):
    A = adj(n, E)
    out = []
    for T in combinations(range(n), 5):
        if sum(A[u][v] for u, v in combinations(T, 2)) != 5:
            continue
        # 2-regular on 5 vertices with 5 edges = C5
        if all(sum(A[u][v] for v in T) == 2 for u in T):
            out.append(T)
    return out


def hom_exists(n1, E1, n2, E2):
    """Is there a graph homomorphism G1 -> G2?  Simple backtracking."""
    A2 = adj(n2, E2)
    nbr1 = [[] for _ in range(n1)]
    for u, v in E1:
        nbr1[u].append(v)
        nbr1[v].append(u)
    f = [-1] * n1

    def rec(i):
        if i == n1:
            return True
        for c in range(n2):
            if all(A2[c][f[j]] for j in nbr1[i] if j < i):
                f[i] = c
                if rec(i + 1):
                    return True
                f[i] = -1
        return False
    return rec(0)


def bip_blowup(n, E, cuts, a):
    """bip(H[a]) = min over cuts of sum_{uv mono} a_u a_v  (exact integers)."""
    best = None
    for mask, mono in cuts:
        s = 0
        for k in mono:
            u, v = E[k]
            s += a[u] * a[v]
        if best is None or s < best:
            best = s
    return best


if __name__ == "__main__":
    for name, (n, E) in [("C5", gamma_graph(5)), ("And(3)=Gamma_8", gamma_graph(8)),
                         ("And(4)=Gamma_11", gamma_graph(11)), ("And(5)=Gamma_14", gamma_graph(14))]:
        print(f"== {name}: n={n} |E|={len(E)} edges={E}")
        print("   triangle-free:", is_triangle_free(n, E),
              " degrees:", sorted(set(sum(adj(n, E)[v]) for v in range(n))))
        aut = automorphisms(n, E)
        print("   |Aut| =", len(aut))
        cuts = all_cuts(n, E)
        nd = nondominated_cuts(cuts)
        print(f"   cuts (up to complement): {len(cuts)}   distinct mono-sets: "
              f"{len(set(m for _, m in cuts))}   non-dominated: {len(nd)}")
        print("   min mono edges (=bip of the graph itself):", min(len(m) for _, m in cuts))
        if n <= 11:
            c5s = induced_C5s(n, E)
            print("   induced C5 count:", len(c5s), c5s[:6])
            print("   hom -> C5 ?", hom_exists(n, E, *gamma_graph(5)))
