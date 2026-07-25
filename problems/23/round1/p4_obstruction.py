"""OBSTRUCTION witness  W_n = P4[n]  (blow-up of the 4-vertex path) with the cut
   V0 = P1 u P4 ,  V1 = P2 u P3.
Claims verified exactly here:
  (a) W_n is triangle-free (it is bipartite),  N = 4n,  |E| = 3n^2;
  (b) the displayed cut has |M| = n^2 = N^2/16 monochromatic edges;
  (c) sigma(S) >= 0 for EVERY S with |S| <= floor(n/2)+1;
  (d) there is S with |S| = floor(n/2)+2 and sigma(S) = -(n - 2*floor(n/2)) ... < 0,
      so the exact threshold is  minimal |S| with sigma(S)<0  =  floor(n/2)+2 = N/8 + 2;
  (e) bip(W_n) = 0 (the graph is bipartite), so the cut is very far from maximum.
Run:  python p4_obstruction.py
"""
import sys
from itertools import combinations
sys.path.insert(0, __file__.rsplit('\\', 1)[0].rsplit('/', 1)[0])
from switch_lib import blowup, cut_status, sigma, min_negative_set, max_cut_brute

H_EDGES = [(0, 1), (1, 2), (2, 3)]          # path P1-P2-P3-P4
COL = [0, 1, 1, 0]                          # the cut:  P1,P4 -> side 0 ; P2,P3 -> side 1


def build(n):
    N, E, part = blowup(H_EDGES, 4, [n] * 4)
    side = [COL[part[v]] for v in range(N)]
    B, M = cut_status(E, side)
    return N, E, part, side, B, M


def sigma_counts(s, n):
    """sigma of a set with s=(s1,s2,s3,s4) vertices in the four parts (exact integer)."""
    s1, s2, s3, s4 = s
    # pair (1,2): B ; (2,3): M ; (3,4): B
    f12 = s1 * (n - s2) + s2 * (n - s1)
    f23 = s2 * (n - s3) + s3 * (n - s2)
    f34 = s3 * (n - s4) + s4 * (n - s3)
    return f12 - f23 + f34


def brute(n):
    N, E, part, side, B, M = build(n)
    assert len(E) == 3 * n * n
    assert len(M) == n * n, (len(M), n * n)
    # triangle-free check
    adj = [set() for _ in range(N)]
    for (u, v) in E:
        adj[u].add(v); adj[v].add(u)
    for (u, v) in E:
        assert not (adj[u] & adj[v]), "triangle!"
    k, S = min_negative_set(N, B, M)
    mc, _ = max_cut_brute(N, E)
    return N, len(E), len(M), k, S, len(E) - mc


def formula_threshold(n):
    """min |S| with sigma<0, computed from the exact part-count formula."""
    best = None
    for s1 in range(n + 1):
        for s2 in range(n + 1):
            for s3 in range(n + 1):
                for s4 in range(n + 1):
                    if sigma_counts((s1, s2, s3, s4), n) < 0:
                        tot = s1 + s2 + s3 + s4
                        if best is None or tot < best[0]:
                            best = (tot, (s1, s2, s3, s4), sigma_counts((s1, s2, s3, s4), n))
    return best


if __name__ == "__main__":
    print("== full brute force over all 2^N subsets ==")
    for n in (2, 3, 4):
        N, m, mono, k, S, bip = brute(n)
        print(f"n={n}: N={N} |E|={m} |M|={mono} = N^2/16={N*N/16}  bip(G)={bip} "
              f" min |S| with sigma<0 = {k}  (floor(n/2)+2 = {n//2+2})  witness={S}")
    print()
    print("== part-count formula (exact), larger n ==")
    for n in range(2, 25):
        tot, s, val = formula_threshold(n)
        print(f"n={n:3d}  N={4*n:3d}  min|S| with sigma<0 = {tot:3d}"
              f"   predicted floor(n/2)+2 = {n//2+2:3d}   {'OK' if tot == n//2+2 else 'MISMATCH'}"
              f"   witness counts={s} sigma={val}   |M|/N^2 = 1/16")
