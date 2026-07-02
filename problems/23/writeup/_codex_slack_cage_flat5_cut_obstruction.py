"""Separate maxcut and Gamma-min obstructions for UNIT-FLAT5 guardrails.

The t=2 shared-path fan has the same local UNIT-FLAT5 atom as the good N=10
census atom, but it is not a gmins cut.  This diagnostic tells whether the
obstruction is already maxcut (some sigma(S)<0) or only Gamma-minimality.
"""

from __future__ import annotations

import argparse
import contextlib
import io
from collections import Counter

with contextlib.redirect_stdout(io.StringIO()):
    from _h import dec, maxcut_all, Bconn
    from _codex_rowcap_non5_half_gate import adj_of
    from _codex_slack_cage_switch_gate import all_subsets, build_data, gamma_of, sigma_of
    from _codex_slack_cage_unit_atom_boundary_dump import (
        build_base_case,
        build_glued_case,
        build_intended_fan_case,
        edge_list,
    )
    from _codex_slack_cage_flat5_fan_stress import build_theta


def norm_edge(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def bad_count(edges, side):
    return sum(1 for u, v in edges if side[u] == side[v])


def side_key(side):
    return "".join(str(int(c)) for c in side)


def analyze_case(case):
    n = case["n"]
    edges = sorted({norm_edge(u, v) for u, v in case["edges"]})
    side = list(case["side"])
    adj = adj_of(n, edges)
    all_max = maxcut_all(n, adj)
    conn_max = [s for s in all_max if Bconn(n, adj, s)]
    max_bad = bad_count(edges, all_max[0]) if all_max else None
    intended_bad = bad_count(edges, side)

    data = build_data(n, edges, side)
    if data is None:
        intended_gamma = None
        intended_min_sigma = None
        intended_min_sets = []
        intended_M = set()
    else:
        E, B, M, Mset, _cyc = data
        intended_M = Mset
        intended_gamma = gamma_of(n, Mset, B)
        sigs = [(sigma_of(S, B, Mset), tuple(sorted(S))) for S in all_subsets(n) if S and len(S) < n]
        intended_min_sigma = min(v for v, _S in sigs)
        intended_min_sets = [S for v, S in sigs if v == intended_min_sigma][:8]

    gamma_records = []
    for s in conn_max:
        d = build_data(n, edges, [int(c) for c in s])
        if d is None:
            continue
        _E, B, _M, Mset, _cyc = d
        gamma_records.append((gamma_of(n, Mset, B), side_key(s), len(Mset), Mset))
    min_gamma = min((g for g, _s, _m, _M in gamma_records if g is not None), default=None)
    gamma_hist = Counter(g for g, _s, _m, _M in gamma_records)
    intended_is_conn_max = any(side_key(side) == side_key(s) for s in conn_max)
    intended_is_gmin = intended_is_conn_max and intended_gamma == min_gamma

    print(f"=== {case['name']} ===")
    print("n:", n)
    print("edges:", len(edges))
    print("intended_side:", side_key(side))
    print("intended_M:", edge_list(intended_M))
    print("maxcut_bad_edges:", max_bad)
    print("intended_bad_edges:", intended_bad)
    print("connected_maxcuts:", len(conn_max))
    print("intended_is_connected_maxcut:", intended_is_conn_max)
    print("intended_gamma:", intended_gamma)
    print("min_connected_maxcut_gamma:", min_gamma)
    print("intended_is_gmin:", intended_is_gmin)
    print("gamma_hist:", dict(sorted(gamma_hist.items())))
    print("min_sigma_over_switches:", intended_min_sigma)
    print("min_sigma_sets:", intended_min_sets)
    if gamma_records:
        print("sample_gmins:")
        for g, s, m, Mset in sorted(gamma_records)[:6]:
            if g == min_gamma:
                print("  side:", s, "m:", m, "Gamma:", g, "M:", edge_list(Mset))
    print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--theta-max-t", type=int, default=0)
    args = ap.parse_args()

    cases = [build_base_case(), build_glued_case(), build_intended_fan_case()]
    for t in range(2, args.theta_max_t + 1):
        n, edges, side = build_theta(t)
        cases.append({"name": f"theta-t{t}", "n": n, "edges": edges, "side": [int(c) for c in side]})

    for case in cases:
        analyze_case(case)


if __name__ == "__main__":
    main()
