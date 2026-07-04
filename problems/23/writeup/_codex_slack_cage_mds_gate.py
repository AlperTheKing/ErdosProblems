"""Exact gate for GPT-Pro's minimum-door-square (MDS) cage shortcut.

This is a proof-facing stress gate for the Slack-CAGE switch route.  It reuses
the minimal positive-debt pair and cage-switch definitions from
_codex_slack_cage_switch_gate.py, but replaces the full post-flip Gamma search
by the local certificate

    sum_{e in dB(S)} lambda_S(e)^2 + I(S)
        < sum_{g in dM(S)} ell(g)^2,

where lambda_S(e) is the cheapest crossing counted row witnessing blue exit e,
and I(S) is the exact noncrossing bad-edge square-length penalty after the
flip.  If this holds at sigma(S)=0, the usual replacement argument gives a
Gamma-decreasing connected maximum-cut switch.
"""

import argparse
import contextlib
import io
import subprocess

with contextlib.redirect_stdout(io.StringIO()):
    from _bdef_construct import Cn, mycielski, union_disjoint
    from _codex_rowcap_non5_half_gate import adj_of
    from _h import Bconn, GENG, dec, maxcut_all
    from _stark1 import gmins
    from _verify_two_lane import build_two_lane

    from _codex_slack_cage_switch_gate import (
        all_subsets,
        build_data,
        counted_rows,
        delta,
        first_exit_edges,
        flip_blue,
        gamma_of,
        graph_connected,
        is_minimal_core,
        norm_edge,
        shortest_distance,
        sigma_of,
        subset_tw,
    )


def edge_path_edges(path):
    return {norm_edge((path[i], path[i + 1])) for i in range(len(path) - 1)}


def mds_certificate(n, E, B, M, Mset, cyc, Q, U, counted, S):
    if sigma_of(S, B, Mset) != 0:
        return None

    B_flip = flip_blue(E, B, S)
    if not graph_connected(n, B_flip):
        return None

    crossM = delta(Mset, S)
    blue_boundary = delta(B, S)
    ell = {g: len(cyc[g][0]) for g in M}

    witnesses = {e: [] for e in blue_boundary}
    for g, P, pset in counted:
        if not (pset & S) or pset <= S:
            continue
        if g not in crossM:
            continue
        for e in first_exit_edges(P, S):
            if e in witnesses:
                witnesses[e].append(g)

    if any(not gs for gs in witnesses.values()):
        return None

    lambda_sq_sum = 0
    lambda_by_edge = {}
    for e, gs in witnesses.items():
        lam = min(ell[g] for g in gs)
        lambda_by_edge[e] = lam
        lambda_sq_sum += lam * lam

    old_crossing_sq_sum = sum(ell[g] * ell[g] for g in crossM)

    noncrossing_penalty = 0
    penalty_detail = []
    for h in M:
        if h in crossM:
            continue
        d = shortest_distance(n, B_flip, h[0], h[1])
        if d is None:
            return None
        new_len = d + 1
        old_len = ell[h]
        diff = new_len * new_len - old_len * old_len
        if diff > 0:
            noncrossing_penalty += diff
            penalty_detail.append((h, old_len, new_len, diff))

    margin = old_crossing_sq_sum - lambda_sq_sum - noncrossing_penalty
    return {
        "S": tuple(sorted(S)),
        "crossM": tuple(sorted(crossM)),
        "blue_boundary": tuple(sorted(blue_boundary)),
        "lambda_by_edge": {str(k): v for k, v in sorted(lambda_by_edge.items())},
        "old_crossing_sq_sum": old_crossing_sq_sum,
        "lambda_sq_sum": lambda_sq_sum,
        "noncrossing_penalty": noncrossing_penalty,
        "penalty_detail": penalty_detail,
        "margin": margin,
    }


def find_mds_switch(n, E, B, M, Mset, cyc, Q, U, counted):
    for S in all_subsets(n):
        if not is_minimal_core(n, E, B, Q, U, counted, S):
            continue
        cert = mds_certificate(n, E, B, M, Mset, cyc, Q, U, counted, S)
        if cert is not None and cert["margin"] > 0:
            return cert
    return None


def candidate_subsets(n, cyc, subset_mode, max_u_size):
    if subset_mode == "all":
        out = all_subsets(n)
    elif subset_mode == "rowsets":
        pool = [frozenset(), frozenset(range(n))]
        for rows in cyc.values():
            for P in rows:
                P = tuple(P)
                pool.append(frozenset(P))
                L = len(P)
                for i in range(L):
                    pool.append(frozenset(P[: i + 1]))
                    pool.append(frozenset(P[i:]))
                    for j in range(i, L):
                        pool.append(frozenset(P[i : j + 1]))
        out = sorted(set(pool), key=lambda U: (len(U), tuple(sorted(U))))
    else:
        raise ValueError(f"unknown subset mode: {subset_mode}")

    if max_u_size is not None:
        out = [U for U in out if len(U) <= max_u_size]
    return out


def find_min_positive_pair_limited(n, B, M, cyc, subset_mode, max_u_size):
    eta = n * n // 25 if n * n % 25 == 0 else None
    from fractions import Fraction as F

    eta = F(n * n, 25) - len(M)
    subsets = candidate_subsets(n, cyc, subset_mode, max_u_size)
    Mset = set(M)
    slack = {U: sigma_of(U, B, Mset) for U in subsets}
    tw = {U: subset_tw(n, M, cyc, U) for U in subsets}

    best = None
    best_key = None
    for f in M:
        for Q in cyc[f]:
            for U in subsets:
                lhs = sum(tw[U][v] for v in Q)
                eps = lhs - len(U) - slack[U] - eta
                if eps <= 0:
                    continue
                rows = counted_rows(Q, U, M, cyc)
                key = (len(U), len(rows), str(f), tuple(Q), tuple(sorted(U)))
                if best is None or key < best_key:
                    best = (f, Q, U, eps, rows)
                    best_key = key
    return best


def maxcut_sides(n, edges, mode, max_cuts):
    adj = adj_of(n, edges)
    if mode == "gmins":
        _adj, cuts = gmins(n, edges)
    else:
        cuts = [s for s in maxcut_all(n, adj) if Bconn(n, adj, s)]
    if max_cuts is not None:
        cuts = cuts[:max_cuts]
    return cuts


def run_cut(name, n, edges, side, args, acc, ci=0):
    data = build_data(n, edges, side)
    if data is None:
        return True
    E, B, M, Mset, cyc = data
    acc["cuts"] += 1
    pair = find_min_positive_pair_limited(n, B, M, cyc, args.subset_mode, args.max_u_size)
    if pair is None:
        acc["no_debt"] += 1
        return True
    f, Q, U, eps, counted = pair
    acc["positive"] += 1
    cert = find_mds_switch(n, E, B, M, Mset, cyc, Q, U, counted)
    if cert is None:
        acc["fails"] += 1
        rec = {
            "name": name,
            "cut_index": ci,
            "n": n,
            "m": len(M),
            "side": "".join(map(str, side)),
            "f": f,
            "Q": Q,
            "U": tuple(sorted(U)),
            "eps": str(eps),
            "counted_rows": len(counted),
        }
        if acc["first_fail"] is None:
            acc["first_fail"] = rec
        return not args.stop_first

    acc["mds"] += 1
    rec = {
        "eps": str(eps),
        "name": name,
        "n": n,
        "m": len(M),
        "Q": Q,
        "U": tuple(sorted(U)),
        "cert": cert,
    }
    if acc["first_mds"] is None:
        acc["first_mds"] = rec
    return True


def run_instance(name, n, edges, args, acc):
    cuts = maxcut_sides(n, edges, args.cut_mode, args.max_cuts)
    for ci, side in enumerate(cuts):
        if not run_cut(name, n, edges, side, args, acc, ci):
            return False
    return True


def bridge(block1, block2, u, v):
    n, edges = union_disjoint(block1, block2)
    return n, edges + [(u, block1[0] + v)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=7)
    ap.add_argument("--max-n", type=int, default=9)
    ap.add_argument("--max-cuts", type=int, default=16)
    ap.add_argument("--cut-mode", choices=("max", "gmins"), default="max")
    ap.add_argument("--max-u-size", type=int, default=None)
    ap.add_argument("--skip-census", action="store_true")
    ap.add_argument("--skip-two-lane", action="store_true")
    ap.add_argument("--skip-named", action="store_true")
    ap.add_argument("--two-lane-max", type=int, default=12)
    ap.add_argument("--provided-two-lane", action="store_true")
    ap.add_argument("--subset-mode", choices=("all", "rowsets"), default="all")
    ap.add_argument("--stop-first", action="store_true")
    args = ap.parse_args()

    acc = {
        "cuts": 0,
        "no_debt": 0,
        "positive": 0,
        "mds": 0,
        "fails": 0,
        "first_fail": None,
        "first_mds": None,
    }

    if not args.skip_two_lane:
        for L in range(8, args.two_lane_max + 1, 2):
            n, edges, _side, _bad = build_two_lane(L)
            ok = run_cut(f"two-lane-L{L}", n, edges, _side, args, acc) if args.provided_two_lane else run_instance(f"two-lane-L{L}", n, edges, args, acc)
            if not ok and args.stop_first:
                break

    if not args.skip_named and not (args.stop_first and acc["first_fail"]):
        named = [
            ("Grotzsch", mycielski(5, Cn(5))),
            ("M(C7)", mycielski(7, Cn(7))),
            ("C7|Grotzsch", bridge((7, Cn(7)), mycielski(5, Cn(5)), 0, 0)),
        ]
        for name, (n, edges) in named:
            if n <= 20:
                if not run_instance(name, n, edges, args, acc) and args.stop_first:
                    break

    if not args.skip_census and not (args.stop_first and acc["first_fail"]):
        for nn in range(args.min_n, args.max_n + 1):
            for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
                n, edges = dec(g6)
                if not run_instance(f"cen{g6}", n, edges, args, acc) and args.stop_first:
                    break
            if args.stop_first and acc["first_fail"]:
                break

    print("=== slack-CAGE MDS cage-switch gate ===")
    for k in ("cuts", "no_debt", "positive", "mds", "fails"):
        print(f"{k}: {acc[k]}")
    print("first_mds:", acc["first_mds"] or "")
    print("first_fail:", acc["first_fail"] or "")
    if acc["fails"]:
        print("VERDICT: FAILS")
    elif acc["positive"]:
        print("VERDICT: PASSES_ON_POSITIVE_DEBT_CASES")
    else:
        print("VERDICT: VACUOUS_NO_POSITIVE_DEBT")


if __name__ == "__main__":
    main()
