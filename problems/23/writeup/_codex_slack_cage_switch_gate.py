"""Exact gate for GPT-Pro's Slack-CAGE zero-slack cage-switch atom.

This is a falsifier/stress script, not a proof.  For each tested connected-B
maximum cut, it finds the lexicographically minimal positive Slack-CAGE debt
pair (Q,U), if any, then searches for a cage switch S with:

  * S nonempty proper and S subset U;
  * B^S connected;
  * counted rows crossing S cross terminally;
  * every old blue boundary edge of S is witnessed by a counted row first-exit;
  * S inclusion-minimal for those core conditions;
  * sigma(S)=0;
  * Gamma(after flip S) < Gamma(before).

The gate is intentionally small-N because it enumerates U and S subsets.
"""

import argparse
import contextlib
import io
import subprocess
from collections import deque
from fractions import Fraction as F

with contextlib.redirect_stdout(io.StringIO()):
    from _bdef_construct import Cn, mycielski, union_disjoint
    from _codex_rowcap_non5_half_gate import adj_of
    from _h import Bconn, GENG, dec, maxcut_all
    from _satzmu_conn import struct_for_side
    from _stark1 import gmins
    from _verify_two_lane import build_two_lane


def norm_edge(e):
    u, v = e
    return (u, v) if u < v else (v, u)


def bitset_vertices(mask, n):
    return frozenset(i for i in range(n) if (mask >> i) & 1)


def all_subsets(n):
    return [bitset_vertices(mask, n) for mask in range(1 << n)]


def delta(edge_set, S):
    return {e for e in edge_set if ((e[0] in S) ^ (e[1] in S))}


def sigma_of(S, B, M):
    return len(delta(B, S)) - len(delta(M, S))


def graph_connected(n, edges):
    if n == 0:
        return True
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    seen = {0}
    q = deque([0])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                q.append(v)
    return len(seen) == n


def flip_blue(E, B, S):
    dG = delta(E, S)
    return (B - dG) | (dG - B)


def shortest_distance(n, edges, s, t):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    seen = {s}
    q = deque([(s, 0)])
    while q:
        u, d = q.popleft()
        if u == t:
            return d
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                q.append((v, d + 1))
    return None


def gamma_of(n, M, B):
    total = 0
    for e in M:
        d = shortest_distance(n, B, e[0], e[1])
        if d is None:
            return None
        total += (d + 1) * (d + 1)
    return total


def crosses_terminally(P, S):
    inside = [v in S for v in P]
    seen_false = False
    initial_ok = True
    for b in inside:
        if not b:
            seen_false = True
        elif seen_false:
            initial_ok = False
            break
    seen_true = False
    terminal_ok = True
    for b in inside:
        if b:
            seen_true = True
        elif seen_true:
            terminal_ok = False
            break
    return initial_ok or terminal_ok


def first_exit_edges(P, S):
    out = set()
    for i in range(len(P) - 1):
        u, v = P[i], P[i + 1]
        if (u in S) ^ (v in S):
            out.add(norm_edge((u, v)))
    return out


def build_data(n, edges, side):
    adj = adj_of(n, edges)
    if not Bconn(n, adj, side):
        return None
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M_raw, _ell, _T, _mu, cyc_raw = st
    if not M_raw:
        return None
    E = {norm_edge(e) for e in edges}
    M = [norm_edge(e) for e in M_raw]
    Mset = set(M)
    B = E - Mset
    cyc = {norm_edge(g): [tuple(P) for P in rows] for g, rows in cyc_raw.items()}
    return E, B, M, Mset, cyc


def subset_tw(n, M, cyc, U):
    tw = [F(0) for _ in range(n)]
    for g in M:
        rows = cyc[g]
        den = len(rows)
        for P in rows:
            pset = frozenset(P)
            if pset <= U:
                mass = F(1, den)
                for v in P:
                    tw[v] += mass
    return tw


def counted_rows(Q, U, M, cyc):
    qset = frozenset(Q)
    out = []
    for g in M:
        for P in cyc[g]:
            pset = frozenset(P)
            if pset <= U and pset & qset:
                out.append((g, P, pset))
    return out


def find_min_positive_pair(n, B, M, cyc, max_u_size=None):
    eta = F(n * n, 25) - len(M)
    subsets = all_subsets(n)
    if max_u_size is not None:
        subsets = [U for U in subsets if len(U) <= max_u_size]
    slack = {U: sigma_of(U, B, set(M)) for U in subsets}
    size = {U: len(U) for U in subsets}
    tw = {U: subset_tw(n, M, cyc, U) for U in subsets}

    best = None
    best_key = None
    for f in M:
        for Q in cyc[f]:
            for U in subsets:
                lhs = sum(tw[U][v] for v in Q)
                eps = lhs - size[U] - slack[U] - eta
                if eps <= 0:
                    continue
                rows = counted_rows(Q, U, M, cyc)
                key = (len(U), len(rows), str(f), tuple(Q), tuple(sorted(U)))
                if best is None or key < best_key:
                    best = (f, Q, U, eps, rows)
                    best_key = key
    return best


def core_conditions(n, E, B, Q, U, counted, S):
    if not S or len(S) == n:
        return False
    if not S <= U:
        return False
    BS = flip_blue(E, B, S)
    if not graph_connected(n, BS):
        return False
    for _g, P, pset in counted:
        if pset & S and not pset <= S:
            if not crosses_terminally(P, S):
                return False
    blue_boundary = delta(B, S)
    witnessed = set()
    for _g, P, _pset in counted:
        witnessed |= first_exit_edges(P, S)
    return blue_boundary <= witnessed


def is_minimal_core(n, E, B, Q, U, counted, S):
    if not core_conditions(n, E, B, Q, U, counted, S):
        return False
    for x in S:
        S2 = frozenset(set(S) - {x})
        if S2 and core_conditions(n, E, B, Q, U, counted, S2):
            return False
    return True


def find_switch(n, E, B, Mset, Q, U, counted):
    old_gamma = gamma_of(n, Mset, B)
    if old_gamma is None:
        return None
    for S in all_subsets(n):
        if not is_minimal_core(n, E, B, Q, U, counted, S):
            continue
        if sigma_of(S, B, Mset) != 0:
            continue
        BS = flip_blue(E, B, S)
        MS = E - BS
        new_gamma = gamma_of(n, MS, BS)
        if new_gamma is not None and new_gamma < old_gamma:
            return S, new_gamma - old_gamma
    return None


def maxcut_sides(n, edges, mode, max_cuts):
    adj = adj_of(n, edges)
    if mode == "gmins":
        _adj, cuts = gmins(n, edges)
    else:
        cuts = [s for s in maxcut_all(n, adj) if Bconn(n, adj, s)]
    if max_cuts is not None:
        cuts = cuts[:max_cuts]
    return cuts


def run_instance(name, n, edges, args, acc):
    cuts = maxcut_sides(n, edges, args.cut_mode, args.max_cuts)
    for ci, side in enumerate(cuts):
        data = build_data(n, edges, side)
        if data is None:
            continue
        E, B, M, Mset, cyc = data
        acc["cuts"] += 1
        pair = find_min_positive_pair(n, B, M, cyc, args.max_u_size)
        if pair is None:
            acc["no_debt"] += 1
            continue
        f, Q, U, eps, counted = pair
        acc["positive"] += 1
        sw = find_switch(n, E, B, Mset, Q, U, counted)
        if sw is None:
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
            if args.stop_first:
                return False
        else:
            S, dgamma = sw
            acc["switch"] += 1
            rec = (str(eps), name, n, len(M), tuple(Q), tuple(sorted(U)), tuple(sorted(S)), dgamma)
            if acc["first_switch"] is None:
                acc["first_switch"] = rec
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
    ap.add_argument("--stop-first", action="store_true")
    args = ap.parse_args()

    acc = {"cuts": 0, "no_debt": 0, "positive": 0, "switch": 0, "fails": 0, "first_fail": None, "first_switch": None}

    if not args.skip_two_lane:
        for L in range(8, args.two_lane_max + 1, 2):
            n, edges, _side, _bad = build_two_lane(L)
            if not run_instance(f"two-lane-L{L}", n, edges, args, acc) and args.stop_first:
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

    print("=== slack-CAGE zero-slack cage-switch gate ===")
    for k in ("cuts", "no_debt", "positive", "switch", "fails"):
        print(f"{k}: {acc[k]}")
    print("first_switch:", acc["first_switch"] or "")
    print("first_fail:", acc["first_fail"] or "")
    if acc["fails"]:
        print("VERDICT: FAILS")
    elif acc["positive"]:
        print("VERDICT: PASSES_ON_POSITIVE_DEBT_CASES")
    else:
        print("VERDICT: VACUOUS_NO_POSITIVE_DEBT")


if __name__ == "__main__":
    main()