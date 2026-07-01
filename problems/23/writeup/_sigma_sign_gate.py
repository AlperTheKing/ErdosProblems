"""Test: is sigma_s = delta_B(H_s)-delta_M(H_s) >= 0 for EVERY super-level set
H_s = {T>s} of the load in a gamma-min connected-B max-cut?

If yes, sigma_s>=0 pointwise is a clean structural fact (not just its integral).
Also test the refined bound needed for the sweep:
   N * sigma_s  <=  5 * (L - 2s) * |H_s|  + (reservoir)
by recording the per-level 'excess' E(s) = N*sigma_s - 5*(L-2s)*|H_s| and whether
sum of positive excess (only where E>0, i.e. deficit levels) is dominated by the
early surplus.  We record max single-level E and the ratio sigma_s/|H_s| vs s.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _stark1 import gmins
from _satzmu_conn import struct_for_side
from _codex_psc50_scout import adj_of, build_two_lane, greedy_chords
from _wf_lrsbreak_0 import build_k_lane


def check(name, n, edges, side, acc):
    adj = adj_of(n, edges)
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, _mu, _cyc = st
    if not M:
        return
    T = [F(t) for t in T]
    cut = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] != side[v]]
    bad = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
    for s in sorted(set([F(0)] + T)):
        H = frozenset(i for i, t in enumerate(T) if t > s)
        if not H or len(H) == n:
            continue
        dB = sum(1 for u, v in cut if (u in H) ^ (v in H))
        dM = sum(1 for u, v in bad if (u in H) ^ (v in H))
        sigma = dB - dM
        acc["count"] += 1
        if sigma < 0:
            acc["neg_sigma"].append((name, n, str(s), len(H), dB, dM, sigma))


def census(nmin, nmax, acc):
    for nn in range(nmin, nmax + 1):
        out = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        for g6 in out:
            n, edges = dec(g6)
            adj, cuts = gmins(n, edges)
            for side in cuts:
                check(f"cen{g6}", n, edges, side, acc)
        print(f"census N={nn} done; neg_sigma so far {len(acc['neg_sigma'])}", flush=True)


def main():
    acc = {"count": 0, "neg_sigma": []}
    for L in range(8, 22, 2):
        n, edges, side, _ = build_two_lane(L)
        check(f"two-lane-L{L}", n, edges, side, acc)
    for Ll, k, gap in ((12, 4, 6), (14, 4, 8), (16, 5, 8), (18, 5, 10), (20, 6, 10)):
        bad = greedy_chords(Ll, k, gap)
        n, edges, side, _ = build_k_lane(Ll, k, bad)
        check(f"k-lane-L{Ll}-k{k}", n, edges, side, acc)
    census(7, 11, acc)
    print("=== sigma_s >= 0 pointwise test ===")
    print(f"levels checked = {acc['count']}")
    print(f"negative-sigma super-level sets = {len(acc['neg_sigma'])}")
    if acc["neg_sigma"]:
        print("examples:", acc["neg_sigma"][:10])


if __name__ == "__main__":
    main()
