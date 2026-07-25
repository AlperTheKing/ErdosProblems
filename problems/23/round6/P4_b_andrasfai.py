"""(b) And(k) = Gamma_{3k-1} for k = 2..8, with the multiplier map written out.

And(k) is DEFINED (Andrasfai 1962; standard reference definition) as the circulant graph on
Z_{3k-1} in which i ~ j iff  j - i = 1 (mod 3), i.e. connection set
        S_A = {1, 4, 7, ..., 3k-2}   (k elements, symmetric because -(3j+1) = 3(k-1-j)+1 mod 3k-1)
Gamma_m is the circle graph: i ~ j iff 3*dist(i,j) > m, i.e. for m = 3k-1
        S_G = {k, k+1, ..., 2k-1}    (k elements, symmetric because -(k+j) = 2k-1-j mod 3k-1)
Claimed multiplier: v -> k*v  (gcd(k, 3k-1) = 1 since 3k-1 = 3*k - 1).
    k*(3j+1) = 3jk + k = j*(3k-1) + j + k = k + j  (mod 3k-1),   j = 0..k-1,
so k*S_A = S_G exactly.  Checked below elementwise, plus a full adjacency check, plus an
independent brute-force isomorphism search for k = 2..5.
"""
from itertools import permutations
from P4_core import gamma_graph, has_triangle


def andrasfai(k):
    m = 3 * k - 1
    S = set((1 + 3 * j) % m for j in range(k))
    assert S == set((-s) % m for s in S), "connection set not symmetric"
    adj = [[False] * m for _ in range(m)]
    for i in range(m):
        for s in S:
            adj[i][(i + s) % m] = True
    return adj, S


def gamma_conn(m):
    return set(s for s in range(1, m) if 3 * min(s, m - s) > m)


def check(k, brute=False):
    m = 3 * k - 1
    A, SA = andrasfai(k)
    G = gamma_graph(m)
    SG = gamma_conn(m)
    mapped = set((k * s) % m for s in SA)
    iso = all(A[u][v] == G[(k * u) % m][(k * v) % m] for u in range(m) for v in range(m))
    deg_A = sum(A[0])
    deg_G = sum(G[0])
    tf = (not has_triangle(A)) and (not has_triangle(G))
    line = (f"  k={k}  m={3*k-1:2d}  S_And={sorted(SA)}\n"
            f"          S_Gamma={sorted(SG)}   k*S_And={sorted(mapped)}   "
            f"equal: {mapped == SG}\n"
            f"          degrees {deg_A}/{deg_G} (=k? {deg_A == k == deg_G})  "
            f"both triangle-free: {tf}   v->k*v is an isomorphism: {iso}   "
            f"delta>m/3: {3*deg_G > m}")
    print(line)
    ok = (mapped == SG) and iso and deg_A == k == deg_G and tf and 3 * deg_G > m
    if brute:
        found = any(all(A[u][v] == G[p[u]][p[v]] for u in range(m) for v in range(m))
                    for p in permutations(range(m)))
        print(f"          brute-force isomorphism search over all {m}! relabelings: {found}")
        ok = ok and found
    return ok


if __name__ == '__main__':
    print("=" * 78)
    print("(b) And(k) == Gamma_{3k-1}")
    print("=" * 78)
    allok = True
    for k in range(2, 9):
        allok &= check(k, brute=(k <= 4))
    print(f"\n  ALL k=2..8: {'CONFIRMED' if allok else 'FAILED'}")

    print("\n  which Gamma_m are Andrasfai (i.e. have delta > m/3)?")
    for m in range(4, 31):
        d = sum(gamma_graph(m)[0])
        tag = "And(k), k=%d" % ((m + 1) // 3) if (m % 3 == 2 and 3 * d > m) else ""
        print(f"    m={m:2d}  degree={d:2d}  3*delta-m = {3*d-m:3d}  {'delta>m/3' if 3*d>m else 'delta<=m/3'}   {tag}")
