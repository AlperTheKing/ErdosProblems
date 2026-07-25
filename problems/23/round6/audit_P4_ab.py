"""audit_P4_ab — independent checks of P4's items (a) blow-up identity and (b) And(k) = Gamma_{3k-1},
plus the prior-art numeric claim bip(And_k) = floor(k^2/4).
"""
import random
from fractions import Fraction as F
from itertools import combinations
from audit_P4_core import (adj_matrix, psi_graph, bip_graph, blowup, triangle_free, normalise)


def rand_triangle_free(n, p=0.5, rng=random):
    adj = [[False] * n for _ in range(n)]
    for u, v in combinations(range(n), 2):
        if rng.random() < p:
            adj[u][v] = adj[v][u] = True
            # undo if it creates a triangle
            if any(adj[u][w] and adj[v][w] for w in range(n)):
                adj[u][v] = adj[v][u] = False
    return adj


def check_blowup(trials=60, seed=7):
    rng = random.Random(seed)
    bad = 0
    for _ in range(trials):
        n = rng.randint(3, 6)
        H = rand_triangle_free(n, rng.choice([0.4, 0.6, 0.8]), rng)
        sizes = [rng.randint(0, 3) for _ in range(n)]
        N = sum(sizes)
        if N < 2 or N > 16:
            continue
        B, idx = blowup(H, sizes)
        if not triangle_free(B):
            print("  *** blow-up NOT triangle-free")
            bad += 1
            continue
        bip, E = bip_graph(B)
        x = [F(s, N) for s in sizes]
        ps = psi_graph(H, x)
        if F(bip, N * N) != ps:
            print(f"  *** MISMATCH n={n} sizes={sizes} bip={bip} N={N} psi={ps}")
            bad += 1
    print(f"(a) blow-up identity bip(H[n]) = N^2 psi(H,n/N): {trials} trials, {bad} mismatches")
    # C5[q]
    C5 = [[abs(i - j) % 5 in (1, 4) for j in range(5)] for i in range(5)]
    for q in range(1, 4):
        B, _ = blowup(C5, [q] * 5)
        bip, E = bip_graph(B)
        print(f"    C5[{q}]: N={5*q} bip={bip} (= q^2 = {q*q}?  {bip == q*q})  N^2/25 = {(5*q)**2/25}")
    return bad


def and_graph(k):
    """Andrasfai graph And(k) = Cay(Z_{3k-1}, {1,4,...,3k-2} u negatives)"""
    m = 3 * k - 1
    S = set()
    for j in range(k):
        S.add((3 * j + 1) % m)
        S.add((-(3 * j + 1)) % m)
    return [[(u != v and (u - v) % m in S) for v in range(m)] for u in range(m)], S


def check_andrasfai(kmax=9):
    print("(b) And(k) vs Gamma_{3k-1}")
    for k in range(2, kmax + 1):
        m = 3 * k - 1
        A, S = and_graph(k)
        G = adj_matrix(m)
        SG = {d for d in range(1, m) if 3 * min(d, m - d) > m}
        mapped = {(k * s) % m for s in S}
        iso = all(A[u][v] == G[(k * u) % m][(k * v) % m] for u in range(m) for v in range(m))
        degA = sum(A[0])
        degG = sum(G[0])
        print(f"  k={k:2d} m={m:3d}  S_And={sorted(S)}  k*S_And={sorted(mapped)}  S_Gamma={sorted(SG)}"
              f"  equal={mapped == SG}  v->k*v iso={iso}  deg {degA}/{degG}"
              f"  tri-free {triangle_free(A)}/{triangle_free(G)}")


def check_bip_andrasfai(kmax=7):
    print("(h) prior-art numeric claim bip(And_k) = floor(k^2/4)")
    for k in range(2, kmax + 1):
        m = 3 * k - 1
        if m > 20:
            print(f"  k={k} m={m}: skipped (2^{m-1} cuts)")
            continue
        A, _ = and_graph(k)
        bip, E = bip_graph(A)
        print(f"  k={k} m={m}: |E|={E} bip={bip}  floor(k^2/4)={k*k//4}  match={bip == k*k//4}"
              f"   bip/m^2={bip/m**2:.5f}  1/36={1/36:.5f}")


if __name__ == "__main__":
    check_blowup()
    print()
    check_andrasfai()
    print()
    check_bip_andrasfai()
