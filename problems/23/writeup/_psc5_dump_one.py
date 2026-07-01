"""Dump full PSC-5 sweep for a single named census graph6, all gamma-min cuts."""
import sys
from fractions import Fraction as F
from _h import dec
from _stark1 import gmins
from _satzmu_conn import struct_for_side
from _codex_psc50_scout import adj_of


def dump(g6):
    n, edges = dec(g6)
    adj, cuts = gmins(n, edges)
    for ci, side in enumerate(cuts):
        st = struct_for_side(n, adj_of(n, edges), side)
        if st is None:
            continue
        M, ell, T, _mu, _cyc = st
        if not M:
            continue
        T = [F(t) for t in T]
        m = len(M)
        L = F(n) + F(n * n, 25) - m
        cut = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] != side[v]]
        bad = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
        levels = sorted(set([F(0)] + T))
        cum = F(0)
        recs = []
        for a, b in zip(levels, levels[1:]):
            H = {i for i, t in enumerate(T) if t > a}
            w = b - a
            dB = sum(1 for u, v in cut if (u in H) ^ (v in H))
            dM = sum(1 for u, v in bad if (u in H) ^ (v in H))
            sigma = dB - dM
            hs = len(H)
            band = 5 * hs * w * (L - (a + b)) - F(n) * sigma * w
            cum += band
            recs.append((a, b, hs, dB, dM, sigma, band, cum))
        # only print cuts that have an upcross or a low prefix
        mn = min(r[7] for r in recs)
        has_neg_band = any(r[6] < 0 for r in recs)
        if not has_neg_band:
            continue
        print(f"--- {g6} cut#{ci} n={n} m={m} L={L} T={sorted(set(str(t) for t in T))}")
        print(" a    b   H  dB  dM  sig    band       cumPhi")
        for a, b, hs, dB, dM, sigma, band, cum in recs:
            print(f"{str(a):>4} {str(b):>4} {hs:>3} {dB:>3} {dM:>3} {sigma:>4} {str(band):>10} {str(cum):>10}")
        print(f"  min prefix = {mn}")


if __name__ == "__main__":
    for g6 in sys.argv[1:]:
        dump(g6)
