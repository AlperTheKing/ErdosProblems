"""Gate: banked-UPO interval failure => Gamma descent.

For a unique-geodesic row Q=(x_0,...,x_{L-1}) in a connected-B maximum cut,
put d_i=Tw_C(x_i)-1, where C is the K-component of the bad edge.  Let cap(I)
be the total size of off-row B-components whose attachment span meets I.

The corrected Banked-UPO target is

    sum_{i in I} d_i - cap(I) <= eta/2 - (L^2-25)/50,

where eta=N^2/25-|M|.  This script looks for violations of that banked
inequality on maximum cuts that are not necessarily Gamma-minimal, then tests
the existing singleton/path/closed-interval switch family for a cut-tight,
B-connected Gamma descent.

If every banked violation has such a descent, then Gamma-min cuts cannot have
banked violations for this switch family.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import subprocess
from collections import defaultdict, deque
from fractions import Fraction as F

with contextlib.redirect_stdout(io.StringIO()):
    from _bdef_construct import Cn, mycielski, union_disjoint
    from _codex_banked_upo_gate import greedy_chords
    from _codex_interval_failure_switch_lab import (
        adj_from_edges,
        candidate_switches,
        cut_size,
        gamma_data,
        n26_graph,
        switched,
    )
    from _codex_rowcap_non5_half_gate import blowup
    from _codex_upo_conditional_interval_uncross_scan import component_info
    from _h import Bconn, GENG, dec, maxcut_all
    from _satzmu_conn import kcomponents, struct_for_side
    from _stark1 import gmins
    from _verify_two_lane import build_two_lane
    from _wf_lrsbreak_0 import build_k_lane


def cycle_blowup_side(parts):
    side = []
    for i, p in enumerate(parts):
        side.extend([i % 2] * p)
    return side


def bridge(block1, block2, u, v):
    n, edges = union_disjoint(block1, block2)
    return n, edges + [(u, block1[0] + v)]


def banked_failures(n, adj, side, name):
    st = struct_for_side(n, adj, side)
    if st is None:
        return []
    M, _ell, _T, _mu, cyc = st
    if not M:
        return []

    eta = F(n * n, 25) - len(M)
    _comp_map, find = kcomponents(n, cyc)
    by_comp = defaultdict(list)
    for g in M:
        by_comp[find(cyc[g][0][0])].append(g)

    out = []
    for comp, fs in by_comp.items():
        Tw = [F(0) for _ in range(n)]
        for g in fs:
            den = F(len(cyc[g]))
            for P in cyc[g]:
                for v in P:
                    Tw[v] += F(1, den)

        for f in fs:
            if len(cyc[f]) != 1:
                continue
            path = tuple(cyc[f][0])
            L = len(path)
            if L <= 5:
                continue
            infos = component_info(n, adj, side, path)
            dvec = [Tw[v] - 1 for v in path]
            bank = eta / 2 - F(L * L - 25, 50)
            for a in range(L):
                for b in range(a, L):
                    demand = sum(dvec[a : b + 1])
                    cap = sum(
                        cap
                        for lo, hi, cap, _vs, _att in infos
                        if not (hi < a or lo > b)
                    )
                    margin = F(cap) + bank - demand
                    if margin < 0:
                        out.append(
                            {
                                "name": name,
                                "f": f,
                                "path": path,
                                "interval": (a, b),
                                "demand": demand,
                                "cap": cap,
                                "bank": bank,
                                "margin": margin,
                                "dvec": dvec,
                                "components": infos,
                            }
                        )
    return out


def has_descent(n, edges, adj, side, failure):
    base_cut = cut_size(edges, side)
    base_gamma = gamma_data(n, adj, side)
    if base_gamma is None:
        return []
    hits = []
    for label, verts in candidate_switches(failure["path"], failure["components"]):
        side2 = switched(side, verts)
        if cut_size(edges, side2) != base_cut:
            continue
        if not Bconn(n, adj, side2):
            continue
        gd = gamma_data(n, adj, side2)
        if gd is None:
            continue
        if gd[0] < base_gamma[0]:
            hits.append((gd[0], label, tuple(sorted(verts))))
    return sorted(hits)


def scan_side(name, n, edges, side, acc, report_hits=False):
    adj = adj_from_edges(n, edges)
    if not Bconn(n, adj, side):
        return
    fails = banked_failures(n, adj, side, name)
    acc["sides"] += 1
    acc["failures"] += len(fails)
    for failure in fails:
        hits = has_descent(n, edges, adj, side, failure)
        if hits:
            acc["descents"] += 1
            if report_hits and acc["hit_reported"] < 10:
                acc["hit_reported"] += 1
                best = hits[0]
                print(
                    "DESCENT",
                    name,
                    "side",
                    "".join(map(str, side)),
                    "f",
                    failure["f"],
                    "I",
                    failure["interval"],
                    "margin",
                    failure["margin"],
                    "label",
                    best[1],
                    "W",
                    best[2],
                    flush=True,
                )
        else:
            acc["no_descent"] += 1
            if acc["first"] is None:
                acc["first"] = {
                    "name": name,
                    "n": n,
                    "side": "".join(map(str, side)),
                    "f": failure["f"],
                    "row": failure["path"],
                    "I": failure["interval"],
                    "demand": str(failure["demand"]),
                    "cap": failure["cap"],
                    "bank": str(failure["bank"]),
                    "margin": str(failure["margin"]),
                    "dvec": [str(x) for x in failure["dvec"]],
                    "components": failure["components"],
                }


def scan_gmins(name, n, edges, acc, max_cuts=None, report_hits=False):
    _adj, cuts = gmins(n, edges)
    if max_cuts is not None:
        cuts = cuts[:max_cuts]
    for side in cuts:
        scan_side(name, n, edges, side, acc, report_hits)


def singleton_reachable_sides(n, edges, start_side):
    target_cut = cut_size(edges, start_side)

    def norm(side):
        side = list(side)
        if side[0]:
            side = [1 - x for x in side]
        mask = 0
        for i, bit in enumerate(side):
            if bit:
                mask |= 1 << i
        return mask

    def side_of(mask):
        return [(mask >> i) & 1 for i in range(n)]

    start = norm(start_side)
    seen = {start}
    q = deque([start])
    while q:
        mask = q.popleft()
        side = side_of(mask)
        for v in range(n):
            side2 = side[:]
            side2[v] ^= 1
            if cut_size(edges, side2) != target_cut:
                continue
            mask2 = norm(side2)
            if mask2 not in seen:
                seen.add(mask2)
                q.append(mask2)
    return [side_of(mask) for mask in sorted(seen)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--census-max", type=int, default=0)
    ap.add_argument("--max-cuts", type=int, default=2)
    ap.add_argument("--direct-only", action="store_true")
    ap.add_argument("--report-hits", action="store_true")
    ap.add_argument("--n26-reachable", action="store_true")
    ap.add_argument("--skip-n26", action="store_true")
    args = ap.parse_args()

    acc = {
        "sides": 0,
        "failures": 0,
        "descents": 0,
        "no_descent": 0,
        "first": None,
        "hit_reported": 0,
    }

    if not args.skip_n26:
        n, edges = n26_graph()
        scan_side("N26-parity", n, edges, [v % 2 for v in range(n)], acc, args.report_hits)
        if args.n26_reachable:
            for side in singleton_reachable_sides(n, edges, [v % 2 for v in range(n)]):
                scan_side("N26-reachable", n, edges, side, acc, args.report_hits)

    for L in range(8, 31, 2):
        n, edges, side, _bad = build_two_lane(L)
        scan_side(f"two-lane-L{L}", n, edges, side, acc, args.report_hits)

    for Ll, k, gap in [(12, 4, 6), (14, 4, 8), (16, 5, 8), (20, 6, 10)]:
        bad = greedy_chords(Ll, k, gap)
        n, edges, side, _ = build_k_lane(Ll, k, bad)
        scan_side(f"klane-L{Ll}k{k}", n, edges, side, acc, args.report_hits)

    for c in (5, 7, 9, 11, 13):
        n, edges = blowup([1] * c)
        scan_side(f"C{c}[1]", n, edges, cycle_blowup_side([1] * c), acc, args.report_hits)

    if not args.direct_only:
        named = [
            ("Grotzsch", mycielski(5, Cn(5))),
            ("M(C7)", mycielski(7, Cn(7))),
            ("C7|Grotzsch", bridge((7, Cn(7)), mycielski(5, Cn(5)), 0, 0)),
        ]
        for nm, (n, edges) in named:
            scan_gmins(nm, n, edges, acc, args.max_cuts, args.report_hits)

    if args.census_max and not args.direct_only:
        for nn in range(7, args.census_max + 1):
            before = acc["failures"]
            for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
                n, edges = dec(g6)
                adj = adj_from_edges(n, edges)
                cuts = maxcut_all(n, adj)
                if args.max_cuts is not None:
                    cuts = cuts[: args.max_cuts]
                for side in cuts:
                    scan_side(f"cen{g6}", n, edges, side, acc, args.report_hits)
            print(
                f"census N={nn}: sides={acc['sides']} failures+={acc['failures']-before}",
                flush=True,
            )

    print("=== BANKED-UPO descent gate ===")
    print("sides:", acc["sides"])
    print("banked_failures:", acc["failures"])
    print("descents:", acc["descents"])
    print("no_descent:", acc["no_descent"])
    print("first:", acc["first"] or "")
    print("VERDICT:", "HOLDS" if acc["no_descent"] == 0 else "FAILS")


if __name__ == "__main__":
    main()
