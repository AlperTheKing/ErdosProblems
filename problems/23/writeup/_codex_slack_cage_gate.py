"""Exact gate for the slack-CAGE row inequality.

For a fixed row Q, define

    D_Q(U) = sum_g 1/|cyc[g]| * sum_{P in cyc[g], P subset U} |P cap Q|.

Candidate:

    D_Q(U) <= |U| + (delta_B(U)-delta_M(U)) + eta,
    eta = N^2/25 - |M|.

At U=V this gives ROWWISE-GERSH:

    sum_v in Q Tw(v) <= N + eta.

Unlike the false uniform Hall certificate, this lets max-cut slack localize
capacity around a row cage while preserving the global deficit term at U=V.
"""

import argparse
import contextlib
import io
import subprocess
from fractions import Fraction as F

with contextlib.redirect_stdout(io.StringIO()):
    from _bdef_construct import Cn, mycielski, union_disjoint
    from _codex_rowcap_non5_half_gate import adj_of, blowup
    from _h import Bconn, GENG, dec
    from _satzmu_conn import struct_for_side
    from _stark1 import gmins
    from _verify_two_lane import build_two_lane


def bit_vertices(mask, n):
    return [i for i in range(n) if (mask >> i) & 1]


def build_subsets(n, row_sets, subset_mode, max_subsets):
    if subset_mode == "all":
        subset_limit = 1 << n
        if max_subsets is not None:
            subset_limit = min(subset_limit, max_subsets)
        return [set(bit_vertices(mask, n)) for mask in range(subset_limit)]

    if subset_mode != "rowsets":
        raise ValueError(f"unknown subset mode: {subset_mode}")

    subsets = [set(), set(range(n))]
    for rows in row_sets.values():
        for P, pset in rows:
            subsets.append(set(pset))
            L = len(P)
            for i in range(L):
                subsets.append(set(P[: i + 1]))
                subsets.append(set(P[i:]))
                for j in range(i, L):
                    subsets.append(set(P[i : j + 1]))

    uniq = []
    seen = set()
    for S in subsets:
        key = tuple(sorted(S))
        if key in seen:
            continue
        seen.add(key)
        uniq.append(S)
        if max_subsets is not None and len(uniq) >= max_subsets:
            break
    return uniq


def check_cut(name, n, edges, side, max_subsets, subset_mode, acc):
    adj = adj_of(n, edges)
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, _ell, _T, _mu, cyc = st
    if not M:
        return

    bad = {tuple(sorted(e)) for e in M}
    blue = set()
    for u, v in edges:
        e = tuple(sorted((u, v)))
        if side[u] != side[v]:
            blue.add(e)

    eta = F(n * n, 25) - len(M)
    row_sets = {}
    for g in M:
        row_sets[g] = [(tuple(P), set(P)) for P in cyc[g]]

    subsets = build_subsets(n, row_sets, subset_mode, max_subsets)

    # Precompute subset boundary slack for the tested subset range.
    slack_by_idx = []
    size_by_idx = []
    for U in subsets:
        dB = sum(((u in U) ^ (v in U)) for u, v in blue)
        dM = sum(((u in U) ^ (v in U)) for u, v in bad)
        slack_by_idx.append(dB - dM)
        size_by_idx.append(len(U))

    tw_by_subset = []
    for U in subsets:
        tw = [F(0) for _ in range(n)]
        for g in M:
            den = len(cyc[g])
            for P, pset in row_sets[g]:
                if pset <= U:
                    mass = F(1, den)
                    for v in P:
                        tw[v] += mass
        tw_by_subset.append(tw)

    for f in M:
        for Q in cyc[f]:
            for idx, U in enumerate(subsets):
                lhs = sum(tw_by_subset[idx][v] for v in Q)
                rhs = F(size_by_idx[idx] + slack_by_idx[idx]) + eta
                acc["checks"] += 1
                margin = rhs - lhs
                if margin < acc["min"][0]:
                    acc["min"] = (
                        margin,
                        name,
                        n,
                        len(M),
                        f,
                        tuple(Q),
                        tuple(sorted(U)),
                        lhs,
                        rhs,
                        size_by_idx[idx],
                        slack_by_idx[idx],
                        eta,
                    )
                if lhs > rhs:
                    acc["viol"] += 1
                    if acc["first"] is None:
                        acc["first"] = {
                            "name": name,
                            "n": n,
                            "side": "".join(map(str, side)),
                            "m": len(M),
                            "eta": str(eta),
                            "f": f,
                            "Q": tuple(Q),
                            "U": tuple(sorted(U)),
                            "lhs": str(lhs),
                            "rhs": str(rhs),
                            "size": size_by_idx[idx],
                            "slack": slack_by_idx[idx],
                            "excess": str(lhs - rhs),
                        }
                    return


def run_gmins(name, n, edges, max_cuts, max_subsets, subset_mode, acc):
    _adj, cuts = gmins(n, edges)
    if max_cuts is not None:
        cuts = cuts[:max_cuts]
    for side in cuts:
        check_cut(name, n, edges, side, max_subsets, subset_mode, acc)
        if acc["first"]:
            return


def cycle_blowup_side(parts):
    side = []
    for i, p in enumerate(parts):
        side.extend([i % 2] * p)
    return side


def bridge(block1, block2, u, v):
    n, edges = union_disjoint(block1, block2)
    return n, edges + [(u, block1[0] + v)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=7)
    ap.add_argument("--max-n", type=int, default=10)
    ap.add_argument("--two-lane-max", type=int, default=20)
    ap.add_argument("--blowup-t", type=int, default=3)
    ap.add_argument("--blowup-nmax", type=int, default=20)
    ap.add_argument("--max-cuts", type=int, default=None)
    ap.add_argument("--max-subsets", type=int, default=None)
    ap.add_argument("--subset-mode", choices=("all", "rowsets"), default="all")
    ap.add_argument("--skip-two-lane", action="store_true")
    ap.add_argument("--skip-blowups", action="store_true")
    ap.add_argument("--skip-named", action="store_true")
    ap.add_argument("--skip-census", action="store_true")
    ap.add_argument("--stop-first", action="store_true")
    args = ap.parse_args()

    acc = {"checks": 0, "viol": 0, "first": None, "min": (F(10**18),)}

    if not args.skip_two_lane:
        for L in range(8, args.two_lane_max + 1, 2):
            n, edges, side, _bad = build_two_lane(L)
            check_cut(f"two-lane-L{L}", n, edges, side, args.max_subsets, args.subset_mode, acc)
            if args.stop_first and acc["first"]:
                break

    if not args.skip_blowups and not (args.stop_first and acc["first"]):
        for c in (5, 7, 9):
            for t in range(1, args.blowup_t + 1):
                n, edges = blowup([t] * c)
                if n <= args.blowup_nmax:
                    check_cut(
                        f"direct-C{c}[{t}]",
                        n,
                        edges,
                        cycle_blowup_side([t] * c),
                        args.max_subsets,
                        args.subset_mode,
                        acc,
                    )
                    if args.stop_first and acc["first"]:
                        break
            if args.stop_first and acc["first"]:
                break

    if not args.skip_named and not (args.stop_first and acc["first"]):
        named = [
            ("Grotzsch", mycielski(5, Cn(5))),
            ("M(C7)", mycielski(7, Cn(7))),
            ("C7|Grotzsch", bridge((7, Cn(7)), mycielski(5, Cn(5)), 0, 0)),
        ]
        for nm, (n, edges) in named:
            run_gmins(nm, n, edges, args.max_cuts, args.max_subsets, args.subset_mode, acc)
            if args.stop_first and acc["first"]:
                break

    if not args.skip_census and not (args.stop_first and acc["first"]):
        for nn in range(args.min_n, args.max_n + 1):
            for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
                n, edges = dec(g6)
                run_gmins(f"cen{g6}", n, edges, args.max_cuts, args.max_subsets, args.subset_mode, acc)
                if args.stop_first and acc["first"]:
                    break
            if args.stop_first and acc["first"]:
                break

    print("=== slack-CAGE row gate ===")
    print("checks:", acc["checks"])
    print("violations:", acc["viol"])
    print("min_margin:", acc["min"])
    print("first:", acc["first"] or "")
    print("VERDICT:", "HOLDS" if acc["viol"] == 0 else "FAILS")


if __name__ == "__main__":
    main()
