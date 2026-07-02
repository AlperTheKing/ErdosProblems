"""Exact named-graph guardrail for the C5 fixed-mask-size split gate.

This audits named triangle-free stress graphs using true maximum cuts and then
restricts to connected-B gamma-min cuts.  It reuses the exact Fraction gate in
_codex_c5_masksize_split_gate.py; no heuristic max-cut sides are accepted.
"""

from __future__ import annotations

import argparse
import contextlib
import io
from collections import Counter

with contextlib.redirect_stdout(io.StringIO()):
    from _bdef_construct import Cn, mycielski
    from _codex_c5_masksize_split_gate import check_cut, fmt, mask_s, print_rec
    from _codex_mycgrotzsch_exact_maxcut_c5lift import (
        enumerate_maxcuts_gray,
        gamma_for_side,
        side_list,
        side_string,
    )
    from _codex_rowcap_non5_half_gate import adj_of
    from _h import Bconn


def petersen():
    edges = []
    for i in range(5):
        edges.append((i, (i + 1) % 5))
        edges.append((5 + i, 5 + ((i + 2) % 5)))
        edges.append((i, 5 + i))
    return 10, edges


def blowup(n, edges, t):
    out = []
    for u, v in edges:
        for i in range(t):
            for j in range(t):
                out.append((t * u + i, t * v + j))
    return t * n, out


def empty_acc():
    return {
        "positive_eta": True,
        "cuts": 0,
        "rows": 0,
        "checks": 0,
        "fails": 0,
        "first_fail": None,
        "orbit_counts": Counter(),
        "min_by_orbit": {},
        "min_by_size": {},
    }


def named_graphs():
    pet = petersen()
    grotzsch = mycielski(5, Cn(5))
    return [
        ("Petersen", pet),
        ("Petersen[2]", blowup(*pet, 2)),
        ("Myc(Petersen)", mycielski(*pet)),
        ("Grotzsch", grotzsch),
        ("Myc(Grotzsch)", mycielski(*grotzsch)),
        ("Myc(C7)", mycielski(7, Cn(7))),
        ("Myc(C9)", mycielski(9, Cn(9))),
        ("Myc(C11)", mycielski(11, Cn(11))),
    ]


def gamma_min_sides(n, edges):
    adj = adj_of(n, edges)
    best, max_sides = enumerate_maxcuts_gray(n, edges)
    connected = []
    gammas = []
    for side_int in max_sides:
        side = side_list(n, side_int)
        if not Bconn(n, adj, side):
            continue
        gamma = gamma_for_side(n, adj, side)
        if gamma is None:
            continue
        connected.append(side_int)
        gammas.append(gamma)

    min_gamma = min(gammas) if gammas else None
    gmin = [s for s, g in zip(connected, gammas) if g == min_gamma]
    return {
        "maxcut": best,
        "max_sides": max_sides,
        "connected": connected,
        "min_gamma": min_gamma,
        "gmin": gmin,
    }


def summarize_acc(acc):
    for k in ("cuts", "rows", "checks", "fails"):
        print(f"{k}: {acc[k]}")
    for k in sorted(acc["min_by_size"]):
        print_rec(f"min_size_{k}", acc["min_by_size"][k][0])
    for orb in sorted(acc["min_by_orbit"]):
        print_rec(f"min_orbit_{mask_s(orb)}", acc["min_by_orbit"][orb][0])
    print_rec("first_fail", acc["first_fail"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", action="append", default=[])
    ap.add_argument("--skip-over", type=int, default=None)
    ap.add_argument("--max-gmin-sides", type=int, default=None)
    args = ap.parse_args()

    selected = []
    only = set(args.only)
    for name, graph in named_graphs():
        if only and name not in only:
            continue
        if args.skip_over is not None and graph[0] > args.skip_over:
            continue
        selected.append((name, graph))

    acc = empty_acc()
    print("=== exact named C5 fixed-mask-size split gate ===")
    for name, (n, edges) in selected:
        info = gamma_min_sides(n, edges)
        gmin = info["gmin"]
        if args.max_gmin_sides is not None:
            gmin = gmin[: args.max_gmin_sides]

        print(f"--- {name} ---")
        print("n:", n)
        print("edges:", len(edges))
        print("maxcut:", info["maxcut"])
        print("maxcut_complement_classes:", len(info["max_sides"]))
        print("connected_maxcut_classes:", len(info["connected"]))
        print("min_gamma_connected_maxcuts:", info["min_gamma"])
        print("gamma_min_connected_classes:", len(info["gmin"]))
        if gmin:
            print("first_gamma_min_side:", side_string(n, gmin[0]))

        for side_int in gmin:
            check_cut(name, n, edges, side_list(n, side_int), acc)
            if acc["first_fail"] is not None:
                break
        if acc["first_fail"] is not None:
            break

    summarize_acc(acc)
    print("VERDICT:", "PASS" if acc["fails"] == 0 else "FAIL")


if __name__ == "__main__":
    main()
