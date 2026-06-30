"""Exact scout for the actual-load PSC strengthening of LRS.

This avoids algebraic Perron data.  For a connected-B gamma-min cut, let

    R = sum_v T(v)^2 / Gamma,
    h_T(v) = N*T(v)/Gamma,
    Xi(h_T) = TV_B(h_T) - TV_M(h_T).

LRS is R + |M| <= N + N^2/25.  This script tests the stronger rational
family

    R + |M| + Xi(h_T)/c <= N + N^2/25

for c=25 and c=50 on the small census and hard structured witnesses.
"""

from fractions import Fraction as F
import subprocess

from _h import dec, GENG
from _stark1 import gmins
from _satzmu_conn import struct_for_side
from _codex_psc50_scout import adj_of, build_two_lane, greedy_chords
from _wf_lrsbreak_0 import build_k_lane


def check_case(name, n, edges, side, acc):
    adj = adj_of(n, edges)
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, _mu, _cyc = st
    if not M:
        return
    gamma = sum(F(v) * F(v) for v in ell.values())
    rload = sum(F(t) * F(t) for t in T) / gamma
    m = len(M)
    budget = F(n) + F(n * n, 25) - m
    b_edges = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] != side[v]]
    bad_edges = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
    xi_t = sum(abs(F(T[u]) - F(T[v])) for u, v in b_edges)
    xi_t -= sum(abs(F(T[u]) - F(T[v])) for u, v in bad_edges)
    xi_h = F(n, 1) * xi_t / gamma
    if xi_h < 0:
        acc["xi_neg"].append((name, xi_h))
    for c in (25, 50):
        margin = budget - rload - xi_h / c
        key = f"c{c}"
        if margin < acc[key][0]:
            acc[key] = (margin, name, n, m, gamma, rload, xi_h, budget)
        if margin < 0:
            acc[f"{key}_viol"].append((name, n, m, margin, rload, xi_h, budget))


def census_cases(max_n):
    for nn in range(7, max_n + 1):
        out = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True, check=True)
        count = 0
        for g6 in out.stdout.split():
            n, edges = dec(g6)
            adj, cuts = gmins(n, edges)
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
        "c25": (F(10**18), None, None, None, None, None, None, None),
        "c50": (F(10**18), None, None, None, None, None, None, None),
        "c25_viol": [],
        "c50_viol": [],
        "xi_neg": [],
    }
    total = 0
    for case in census_cases(10):
        check_case(*case, acc)
        total += 1
    for case in structured_cases():
        check_case(*case, acc)
        total += 1
    print("=== actual-load PSC gate ===")
    print("cases", total)
    for c in (25, 50):
        key = f"c{c}"
        margin, name, n, m, gamma, rload, xi_h, budget = acc[key]
        print(
            f"{key}: violations={len(acc[key + '_viol'])} min_margin={margin} "
            f"at={name} N={n} m={m} Gamma={gamma} R={rload} Xi_h={xi_h} budget={budget}"
        )
    print("xi_neg", len(acc["xi_neg"]))
    if acc["c25_viol"] or acc["c50_viol"]:
        print("first violations:")
        for row in (acc["c25_viol"] + acc["c50_viol"])[:10]:
            print(row)


if __name__ == "__main__":
    main()
