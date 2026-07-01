"""Find the correct Abel-summation invariant for the PSC-5 sweep.

The integrand I(s)=5(L-2s)|H_s| - N sigma_s. We know int_0^tau I >=0 for all tau
(verified). We want a MONOTONE quantity whose nonnegativity is provable.

Test A (suffix integral): J(tau)=int_tau^{maxT} I(s) ds. If J(tau)<=0 for all
tau>=tau0 and the head is positive, unimodal-from-below fails (already knew).

Test B (Abel with |H| as the summation-by-parts weight): since |H_s| is a
decreasing step function, write I(s)=|H_s|*g(s) - N*sigma_s with g=5(L-2s).
The 'capacity potential' is Cap(tau)=int_0^tau 5(L-2s)|H_s| ds = 5 sum a(L-a).
The 'pressure potential' Pr(tau)=N int_0^tau sigma_s ds = N(TV_B-TV_M)(a_tau).
Target: Cap(tau)>=Pr(tau).

Key provable-looking sub-claim to test:  the pressure RATE per unit capacity
mass is bounded:  along the sweep, whenever we add capacity we can 'prepay'
pressure. Formally test:  is  sigma_s / |H_s|  <= (5/N)*(L-2s) + slack, where
the slack integrates to <= the head surplus?  i.e. test the DIFFERENTIAL ratio
  d Pr / d Cap = N sigma_s / (5(L-2s)|H_s|)  --- but (L-2s) changes sign.

Cleanest: test whether  Pr(tau) <= (N/(5L)) * <something monotone>.
Concretely test the GLOBAL clean bound that may be provable:
  (G)  N*(TV_B(a)-TV_M(a)) <= 5*L*sum_v a  -  5*sum_v a^2 *K ...
Just measure, at each tau, the ratio  Pr(tau)/Cap(tau)  and its max (<1 needed),
and the ratio  Pr(tau) / (N * sum_v a)   [pressure per unit load].
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
    m = len(M)
    L = F(n) + F(n * n, 25) - m
    cut = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] != side[v]]
    bad = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
    levels = sorted(set([F(0)] + T))
    # build sweep bands
    bands = []
    for a, b in zip(levels, levels[1:]):
        H = frozenset(i for i, t in enumerate(T) if t > a)
        dB = sum(1 for u, v in cut if (u in H) ^ (v in H))
        dM = sum(1 for u, v in bad if (u in H) ^ (v in H))
        bands.append((a, b, len(H), dB - dM))
    # running Cap, Pr and their ratio; also pressure per unit load
    Cap = F(0)
    Pr = F(0)
    loadmass = F(0)  # sum_v a_tau = int |H_s| ds
    for a, b, hs, sigma in bands:
        w = b - a
        Cap += 5 * hs * w * (L - (a + b))
        Pr += F(n) * sigma * w
        loadmass += hs * w
        if Cap > 0:
            r = Pr / Cap
            if r > acc["max_prcap"][0]:
                acc["max_prcap"] = (r, name, str(b))
        if loadmass > 0:
            r2 = Pr / (F(n) * loadmass)  # pressure per (N * load)
            if r2 > acc["max_prload"][0]:
                acc["max_prload"] = (r2, name, str(b))


def census(nmin, nmax, acc):
    for nn in range(nmin, nmax + 1):
        out = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        for g6 in out:
            n, edges = dec(g6)
            adj, cuts = gmins(n, edges)
            for side in cuts:
                check(f"cen{g6}", n, edges, side, acc)
        print(f"N={nn} done", flush=True)


def main():
    acc = {"max_prcap": (F(0), "", ""), "max_prload": (F(0), "", "")}
    for L in range(8, 22, 2):
        n, edges, side, _ = build_two_lane(L)
        check(f"two-lane-L{L}", n, edges, side, acc)
    for Ll, k, gap in ((12, 4, 6), (14, 4, 8), (16, 5, 8), (18, 5, 10), (20, 6, 10)):
        bad = greedy_chords(Ll, k, gap)
        n, edges, side, _ = build_k_lane(Ll, k, bad)
        check(f"k-lane-L{Ll}-k{k}", n, edges, side, acc)
    census(7, 11, acc)
    print("=== Abel-direction ratios ===")
    print(f"max Pr/Cap (must be <=1) = {float(acc['max_prcap'][0]):.6f} at {acc['max_prcap'][1:]}")
    print(f"max Pr/(N*loadmass)      = {float(acc['max_prload'][0]):.6f} at {acc['max_prload'][1:]}")


if __name__ == "__main__":
    main()
