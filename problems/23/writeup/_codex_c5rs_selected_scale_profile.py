"""Selected large-graph stress for the C5-RS proper-mask split.

This reuses _codex_c5rs_subset_profile.check_cut on heuristic max cuts for
larger non-C5-hom examples where exact gmins is too expensive.

The diagnostic question is whether sharp C5-LIFT failures, if present, occur
only at the full mask 11111 or already at a proper layer mask.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import random
from collections import Counter

with contextlib.redirect_stdout(io.StringIO()):
    from _bdef_construct import Cn, blow_g, mycielski
    from _codex_c5rs_subset_profile import check_cut, fmt, mask_s, print_rec
    from _codex_rowcap_non5_half_gate import adj_of
    from _h import Bconn


PETERSEN_EDGES = [
    (0, 1), (1, 2), (2, 3), (3, 4), (4, 0),
    (0, 5), (1, 6), (2, 7), (3, 8), (4, 9),
    (5, 7), (7, 9), (9, 6), (6, 8), (8, 5),
]


def cut_value(n, edges, side):
    return sum(1 for u, v in edges if side[u] != side[v])


def maxcut_ls_cuts(n, edges, seeds=200, seed=11):
    adj = adj_of(n, edges)
    rng = random.Random(seed)
    best_val = -1
    best = {}
    for _ in range(seeds):
        side = [rng.randrange(2) for _ in range(n)]
        improved = True
        while improved:
            improved = False
            order = list(range(n))
            rng.shuffle(order)
            for v in order:
                same = sum(1 for w in adj[v] if side[w] == side[v])
                diff = len(adj[v]) - same
                if same > diff:
                    side[v] ^= 1
                    improved = True
        val = cut_value(n, edges, side)
        if val > best_val:
            best_val = val
            best = {}
        if val == best_val and Bconn(n, adj, side):
            key = "".join(map(str, side))
            comp = "".join("1" if x == 0 else "0" for x in side)
            best[min(key, comp)] = side[:]
    return best_val, list(best.values())


def empty_acc():
    return {
        "positive_eta": True,
        "cuts": 0,
        "rows": 0,
        "over_rows": 0,
        "subset_checks": 0,
        "c5_fails": 0,
        "lift_fails": 0,
        "first_c5_fail": None,
        "first_lift_fail": None,
        "orbit_counts": Counter(),
        "min_c5_by_orbit": {},
        "min_lift_by_orbit": {},
    }


def graph_cases():
    grotzsch = mycielski(5, Cn(5))
    myc_grotzsch = mycielski(*grotzsch)
    return [
        ("Petersen[2]", blow_g(10, PETERSEN_EDGES, 2)),
        ("Grotzsch", grotzsch),
        ("MycGrotzsch", myc_grotzsch),
    ]


def summarize_case(name, n, edges, cuts, acc):
    print(f"=== {name} ===")
    print(f"n: {n}")
    print(f"heuristic_best_cut_edges: {cut_value(n, edges, cuts[0]) if cuts else 'none'}")
    print(f"connected_best_cuts_used: {len(cuts)}")
    for k in ("cuts", "rows", "over_rows", "subset_checks", "c5_fails", "lift_fails"):
        print(f"{k}: {acc[k]}")
    for orb in sorted(acc["min_lift_by_orbit"]):
        rec = acc["min_lift_by_orbit"][orb][0]
        print(
            "min_lift_orbit_%s: %s"
            % (mask_s(orb), fmt(rec["lift_margin"]) if rec else "none")
        )
    print_rec("first_lift_fail", acc["first_lift_fail"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=300)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--case", choices=["all", "petersen2", "grotzsch", "mycgrotzsch"], default="all")
    args = ap.parse_args()

    selected = {
        "petersen2": {"Petersen[2]"},
        "grotzsch": {"Grotzsch"},
        "mycgrotzsch": {"MycGrotzsch"},
        "all": None,
    }[args.case]

    total = empty_acc()
    for name, (n, edges) in graph_cases():
        if selected is not None and name not in selected:
            continue
        best_val, cuts = maxcut_ls_cuts(n, edges, seeds=args.seeds, seed=args.seed)
        acc = empty_acc()
        for side in cuts:
            check_cut(name, n, edges, side, acc)
            check_cut(name, n, edges, side, total)
        summarize_case(name, n, edges, cuts, acc)
        print()

    print("=== TOTAL ===")
    for k in ("cuts", "rows", "over_rows", "subset_checks", "c5_fails", "lift_fails"):
        print(f"{k}: {total[k]}")
    for orb in sorted(total["min_lift_by_orbit"]):
        rec = total["min_lift_by_orbit"][orb][0]
        print(
            "min_lift_orbit_%s: %s"
            % (mask_s(orb), fmt(rec["lift_margin"]) if rec else "none")
        )
    print_rec("first_lift_fail", total["first_lift_fail"])


if __name__ == "__main__":
    main()
