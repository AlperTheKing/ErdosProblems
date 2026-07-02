"""Exact max-cut C5 subset-profile audit for MycGrotzsch.

This resolves whether heuristic C5-LIFT/proper-mask failures on MycGrotzsch
come from a true connected maximum cut or from a suboptimal local-search cut.
"""

from __future__ import annotations

import argparse
import contextlib
import io
from collections import Counter

with contextlib.redirect_stdout(io.StringIO()):
    from _bdef_construct import Cn, mycielski
    from _codex_c5rs_subset_profile import check_cut, fmt, mask_s, print_rec
    from _codex_rowcap_non5_half_gate import adj_of
    from _h import Bconn
    from _satzmu_conn import struct_for_side


def cut_value(edges, side_int):
    return sum(1 for u, v in edges if ((side_int >> u) ^ (side_int >> v)) & 1)


def side_list(n, side_int):
    return [(side_int >> v) & 1 for v in range(n)]


def side_string(n, side_int):
    return "".join(str((side_int >> v) & 1) for v in range(n))


def enumerate_maxcuts_gray(n, edges):
    """Enumerate complement classes with vertex 0 fixed to side 0."""
    adj_bits = [0] * n
    deg = [0] * n
    for u, v in edges:
        adj_bits[u] |= 1 << v
        adj_bits[v] |= 1 << u
        deg[u] += 1
        deg[v] += 1

    all_bits = (1 << n) - 1
    total = 1 << (n - 1)
    side = 0
    val = 0
    prev_g = 0
    best = 0
    best_sides = [0]

    for i in range(1, total):
        g = i ^ (i >> 1)
        diff_bit = g ^ prev_g
        bit_index = diff_bit.bit_length() - 1
        v = bit_index + 1
        if (side >> v) & 1:
            cut_incident = (adj_bits[v] & (~side) & all_bits).bit_count()
        else:
            cut_incident = (adj_bits[v] & side).bit_count()
        val += deg[v] - 2 * cut_incident
        side ^= 1 << v
        prev_g = g

        if val > best:
            best = val
            best_sides = [side]
        elif val == best:
            best_sides.append(side)

    return best, best_sides


def gamma_for_side(n, adj, side):
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, ell = st[0], st[1]
    return sum(ell[f] * ell[f] for f in M)


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


def summarize(label, acc):
    print(f"=== {label} ===")
    for k in ("cuts", "rows", "over_rows", "subset_checks", "c5_fails", "lift_fails"):
        print(f"{k}: {acc[k]}")
    for orb in sorted(acc["min_lift_by_orbit"]):
        rec = acc["min_lift_by_orbit"][orb][0]
        print("min_lift_orbit_%s: %s" % (mask_s(orb), fmt(rec["lift_margin"]) if rec else "none"))
    print_rec("first_lift_fail", acc["first_lift_fail"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile-all-connected", action="store_true")
    args = ap.parse_args()

    grotzsch = mycielski(5, Cn(5))
    n, edges = mycielski(*grotzsch)
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
    gamma_min_sides = [s for s, g in zip(connected, gammas) if g == min_gamma]

    print("=== MycGrotzsch exact max-cut audit ===")
    print("n:", n)
    print("edges:", len(edges))
    print("exact_maxcut_value:", best)
    print("maxcut_complement_classes:", len(max_sides))
    print("connected_maxcut_classes:", len(connected))
    print("min_gamma_connected_maxcuts:", min_gamma)
    print("gamma_min_connected_classes:", len(gamma_min_sides))
    if gamma_min_sides:
        print("first_gamma_min_side:", side_string(n, gamma_min_sides[0]))

    if args.profile_all_connected:
        acc_all = empty_acc()
        for side_int in connected:
            check_cut("MycGrotzsch_exact_connected_max", n, edges, side_list(n, side_int), acc_all)
        summarize("all connected max cuts", acc_all)

    acc_gmin = empty_acc()
    for side_int in gamma_min_sides:
        check_cut("MycGrotzsch_exact_gamma_min", n, edges, side_list(n, side_int), acc_gmin)
    summarize("connected gamma-min max cuts", acc_gmin)


if __name__ == "__main__":
    main()
