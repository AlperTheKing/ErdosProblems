"""(a) the blow-up identity and the equivalence  conjecture <=> max_x psi(H,x) <= 1/25.

Claims audited
  A1  a blow-up of a triangle-free graph is triangle-free
  A2  bip(H[n]) = min over BLOB-RESPECTING cuts  (the optimum can be taken blob-respecting)
  A3  bip(H[n]) = N^2 * psi(H, n/N)   exactly
  A4  conjecture => max_x psi <= 1/25   (needs A1+A3 and density of rationals)
  A5  max_x psi <= 1/25 => conjecture   (take H = G, x uniform)
  A6  the strict d > 1/3 convention on the circle is FORCED by triangle-freeness
"""
import random
from fractions import Fraction as F
from itertools import combinations
from P4_core import (gamma_graph, has_triangle, blowup, bip_bruteforce, psi_graph, circdist)

random.seed(20260725)


def random_trianglefree(n, p=0.5):
    adj = [[False] * n for _ in range(n)]
    edges = list(combinations(range(n), 2))
    random.shuffle(edges)
    for u, v in edges:
        if random.random() > p:
            continue
        ok = not any(adj[u][w] and adj[v][w] for w in range(n))
        if ok:
            adj[u][v] = adj[v][u] = True
    return adj


def blob_respecting_min(adjm, sizes):
    """min over cuts of H[sizes] that put every blob entirely on one side"""
    n = len(adjm)
    E = [(u, v) for u, v in combinations(range(n), 2) if adjm[u][v]]
    best = None
    for msk in range(1 << (n - 1)):
        side = [(msk >> i) & 1 for i in range(n - 1)] + [0]
        c = sum(sizes[u] * sizes[v] for u, v in E if side[u] == side[v])
        if best is None or c < best:
            best = c
    return best


def main():
    print("=" * 78)
    print("(a) BLOW-UP IDENTITY")
    print("=" * 78)

    # ---------------------------------------------------------------- A1 + A2 + A3
    bad1 = bad2 = bad3 = 0
    trials = 0
    for _ in range(120):
        n = random.randint(3, 6)
        H = random_trianglefree(n, p=random.choice([0.4, 0.6, 0.9]))
        if not any(any(r) for r in H):
            continue
        sizes = [random.randint(1, 3) for _ in range(n)]
        N = sum(sizes)
        if N > 15:
            continue
        trials += 1
        G, _ = blowup(H, sizes)
        if has_triangle(H):
            raise SystemExit("generator produced a triangle")
        if has_triangle(G):
            bad1 += 1
            print("  A1 FAIL", sizes)
        b_all = bip_bruteforce(G)                       # min over ALL cuts of the blow-up
        b_blob = blob_respecting_min(H, sizes)          # min over blob-respecting cuts
        if b_all != b_blob:
            bad2 += 1
            print("  A2 FAIL", H, sizes, b_all, b_blob)
        x = [F(s, N) for s in sizes]
        rhs = N * N * psi_graph(H, x)
        if F(b_all) != rhs:
            bad3 += 1
            print("  A3 FAIL", H, sizes, b_all, rhs)
    print(f"  A1 blow-up triangle-free              : {trials - bad1}/{trials} ok")
    print(f"  A2 optimum attained blob-respecting   : {trials - bad2}/{trials} ok")
    print(f"  A3 bip(H[n]) == N^2 psi(H, n/N)       : {trials - bad3}/{trials} ok")

    # A2/A3 on the extremal family C5[q] (the sharpness case)
    C5 = gamma_graph(5)
    print("\n  C5[q] check (extremal family):")
    for q in range(1, 5):
        sizes = [q] * 5
        G, _ = blowup(C5, sizes)
        N = 5 * q
        b = bip_bruteforce(G)
        x = [F(1, 5)] * 5
        print(f"    q={q}  N={N:2d}  bip={b:3d}  q^2={q*q:3d}  N^2/25={N*N/25:6.2f}  "
              f"N^2 psi={N*N*psi_graph(C5,x)}   bip == q^2 : {b == q*q}")

    # unbalanced blow-ups of C5 - is bip still <= N^2/25?
    print("\n  unbalanced C5 blow-ups (bip vs N^2/25):")
    worst = None
    for sizes in [(1, 1, 1, 1, 1), (2, 1, 1, 1, 1), (2, 2, 1, 1, 1), (3, 2, 2, 1, 1),
                  (2, 2, 2, 2, 1), (3, 3, 2, 2, 2), (2, 3, 2, 3, 2)]:
        G, _ = blowup(C5, list(sizes))
        N = sum(sizes)
        b = bip_bruteforce(G)
        r = F(b * 25, N * N)
        worst = r if worst is None or r > worst else worst
        print(f"    {sizes}  N={N:2d}  bip={b:2d}  25*bip/N^2 = {r} = {float(r):.4f}")
    print(f"    worst ratio seen: {worst} = {float(worst):.4f}  (must be <= 1)")

    # ---------------------------------------------------------------- A5
    print("\n  A5  (max_x psi <= 1/25) => conjecture:  psi(G, uniform) == bip(G)/N^2")
    ok = True
    for _ in range(40):
        n = random.randint(4, 8)
        H = random_trianglefree(n, 0.6)
        b = bip_bruteforce(H)
        x = [F(1, n)] * n
        if F(b, n * n) != psi_graph(H, x):
            ok = False
            print("    FAIL", H)
    print(f"    identity bip(G) = N^2 psi(G,uniform): {'ok on 40 random graphs' if ok else 'FAILED'}")

    # ---------------------------------------------------------------- A6
    print("\n  A6  convention check on the circle:")
    pts = [F(0), F(1, 3), F(2, 3)]
    d = [circdist(a, b) for a, b in combinations(pts, 2)]
    print(f"    the three points 0, 1/3, 2/3 have pairwise distances {d}")
    print(f"    non-strict convention (d >= 1/3) makes them a TRIANGLE -> the circle graph would "
          f"not be triangle-free")
    print(f"    => adjacency MUST be strict (d > 1/3); every downstream object inherits this.")
    # and with the strict convention no three points are pairwise adjacent
    worst = 0
    for _ in range(4000):
        p = sorted(F(random.randint(0, 719), 720) for _ in range(3))
        if all(circdist(a, b) > F(1, 3) for a, b in combinations(p, 2)):
            worst += 1
    print(f"    random triples that are pairwise > 1/3 apart (must be 0): {worst}")


if __name__ == '__main__':
    main()
