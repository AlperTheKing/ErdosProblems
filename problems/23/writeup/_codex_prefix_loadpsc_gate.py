"""Exact scout for PREFIX-LOAD-PSC.

For a connected-B gamma-min maximum-cut configuration, LOAD-PSC-25 is

    25 * sum_v T(v)(T(v)-N) + N*(TV_B(T)-TV_M(T))
        <= Gamma * (N^2 - 25|M|).

This script tests the stronger bottom-prefix coarea majorization.  If
0=t_0<t_1<...<t_r are the distinct load values, H_j={v:T(v)>t_j},
sigma_j=delta_B(H_j)-delta_M(H_j), w_j=t_{j+1}-t_j, and D=N^2-25|M|,
then every prefix k should satisfy

    sum_{j<k} w_j * (
        D*|H_j| - 25*(2*t_j+w_j-N)*|H_j| - N*sigma_j
    ) >= 0.

The full prefix is exactly LOAD-PSC-25.
"""

from fractions import Fraction as F
import subprocess

from _h import dec, GENG
from _stark1 import gmins
from _satzmu_conn import struct_for_side
from _codex_psc50_scout import adj_of, build_two_lane, greedy_chords
from _wf_lrsbreak_0 import build_k_lane


def prefix_margins(n, edges, side):
    adj = adj_of(n, edges)
    st = struct_for_side(n, adj, side)
    if st is None:
        return []
    M, _ell, T, _mu, _cyc = st
    if not M:
        return []
    T = [F(t) for t in T]
    D = F(n * n - 25 * len(M))
    cut_edges = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] != side[v]]
    bad_edges = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
    levels = sorted(set([F(0)] + T))
    out = []
    pref = F(0)
    for a, b in zip(levels, levels[1:]):
        H = {i for i, t in enumerate(T) if t > a}
        width = b - a
        sigma = sum(1 for u, v in cut_edges if (u in H) ^ (v in H))
        sigma -= sum(1 for u, v in bad_edges if (u in H) ^ (v in H))
        band = width * (D * len(H) - 25 * (2 * a + width - n) * len(H) - F(n) * sigma)
        pref += band
        out.append((pref, a, b, len(H), sigma, band))
    return out


def check_case(name, n, edges, side, acc):
    rows = prefix_margins(n, edges, side)
    if not rows:
        return
    for idx, row in enumerate(rows, start=1):
        pref, a, b, hsize, sigma, band = row
        if pref < acc["best"][0]:
            acc["best"] = (pref, name, n, idx, a, b, hsize, sigma, band)
        if band < acc["best_band"][0]:
            acc["best_band"] = (band, name, n, idx, a, b, hsize, sigma)
        if pref < 0:
            acc["viol"].append((name, n, idx, pref, a, b, hsize, sigma, band))
            return


def census_cases(max_n):
    for nn in range(7, max_n + 1):
        out = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True, check=True)
        count = 0
        for g6 in out.stdout.split():
            n, edges = dec(g6)
            _adj, cuts = gmins(n, edges)
            for side in cuts:
                count += 1
                yield f"cen{g6}", n, edges, side
        print(f"census N={nn} yielded {count} gamma-min cuts", flush=True)


def structured_cases():
    for L in range(8, 22, 2):
        n, edges, side, _ = build_two_lane(L)
        yield f"two-lane-L{L}", n, edges, side
    for L, k, gap in ((12, 4, 6), (14, 4, 8), (16, 5, 8), (18, 5, 10), (20, 6, 10)):
        bad = greedy_chords(L, k, gap)
        n, edges, side, _ = build_k_lane(L, k, bad)
        yield f"k-lane-L{L}-k{k}-g{gap}", n, edges, side


def main():
    acc = {
        "best": (F(10**18), None, None, None, None, None, None, None, None),
        "best_band": (F(10**18), None, None, None, None, None, None, None),
        "viol": [],
    }
    total = 0
    for case in census_cases(11):
        check_case(*case, acc)
        total += 1
    for case in structured_cases():
        check_case(*case, acc)
        total += 1
    print("=== PREFIX-LOAD-PSC ===")
    print("cases", total)
    print("violations", len(acc["viol"]))
    print("best_prefix", acc["best"])
    print("best_band", acc["best_band"])
    if acc["viol"]:
        print("first_violation", acc["viol"][0])


if __name__ == "__main__":
    main()
