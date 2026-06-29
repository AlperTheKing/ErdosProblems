"""Exact exploratory gate for interval-Hall failure => Gamma descent.

This is not a proof checker.  It tests the switch-descent hypothesis that is
now the live unique-path route:

    if a connected-B maximum cut has a unique-row interval-Hall failure, then
    a natural path/corridor switch preserves max-cut size, keeps B connected,
    and strictly lowers Gamma.

The switch family is intentionally small and geometric:

  * singletons on the unique path P_f;
  * contiguous path intervals;
  * path intervals plus every off-path B-component whose span is contained in
    the interval.

Any no-descent output is a real obstruction to this proposed switch family.
"""
from __future__ import annotations

import argparse
import subprocess
from collections import Counter, deque

from _h import Bconn, GENG, dec, maxcut_all
from _codex_interval_failure_switch_lab import (
    adj_from_edges,
    candidate_switches,
    cut_size,
    gamma_data,
    interval_failures,
    n26_graph,
    switched,
)


def has_descent(n, edges, adj, side, failure):
    base_cut = cut_size(edges, side)
    base_gamma = gamma_data(n, adj, side)
    if base_gamma is None:
        return None
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
            hits.append((gd[0], label, tuple(sorted(verts)), gd[1]))
    return sorted(hits)


def scan_side(name, n, edges, side, max_bad_reports=5, report_hits=False):
    adj = adj_from_edges(n, edges)
    failures = interval_failures(n, adj, side, name)
    checked = len(failures)
    no_descent = []
    for failure in failures:
        hits = has_descent(n, edges, adj, side, failure)
        if not hits:
            no_descent.append(failure)
            if len(no_descent) <= max_bad_reports:
                print(
                    "NO_DESCENT",
                    name,
                    "side",
                    "".join(map(str, side)),
                    "f",
                    failure["f"],
                    "I",
                    failure["interval"],
                    "demand",
                    failure["demand"],
                    "cap",
                    failure["cap"],
                    flush=True,
                )
        elif report_hits:
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
                "demand",
                failure["demand"],
                "cap",
                failure["cap"],
                "best_gamma",
                best[0],
                "label",
                best[1],
                "W",
                best[2],
                flush=True,
            )
    return checked, len(no_descent)


def scan_n26_parity(report_hits=False):
    n, edges = n26_graph()
    side = [v % 2 for v in range(n)]
    checked, bad = scan_side("N26-parity", n, edges, side, report_hits=report_hits)
    print(f"N26 parity: interval-failures={checked} no-descent={bad}", flush=True)
    return checked, bad


def scan_n26_singleton_reachable(report_hits=False):
    n, edges = n26_graph()
    adj = adj_from_edges(n, edges)
    target_cut = cut_size(edges, [v % 2 for v in range(n)])

    def norm(side):
        side = list(side)
        if side[0]:
            side = [1 - x for x in side]
        m = 0
        for i, bit in enumerate(side):
            if bit:
                m |= 1 << i
        return m

    def side_of(mask):
        return [(mask >> i) & 1 for i in range(n)]

    start = norm([v % 2 for v in range(n)])
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

    total_failures = total_bad = active = 0
    gammas = Counter()
    for mask in sorted(seen):
        side = side_of(mask)
        if not Bconn(n, adj, side):
            continue
        gd = gamma_data(n, adj, side)
        if gd is None or not gd[1]:
            continue
        active += 1
        gammas[gd[0]] += 1
        checked, bad = scan_side(
            "N26-singleton-reachable", n, edges, side, report_hits=report_hits
        )
        total_failures += checked
        total_bad += bad

    print(
        "N26 singleton-reachable:",
        f"cuts={len(seen)}",
        f"connectedB-bad={active}",
        f"gamma-counts={sorted(gammas.items())}",
        f"interval-failures={total_failures}",
        f"no-descent={total_bad}",
        flush=True,
    )
    return total_failures, total_bad


def scan_census(max_n: int, report_hits=False):
    total_failures = 0
    total_no_descent = 0
    for nn in range(7, max_n + 1):
        outg = subprocess.run(
            [GENG, "-tc", str(nn)], capture_output=True, text=True, check=True
        ).stdout.split()
        graph_count = 0
        side_count = 0
        failures = 0
        no_descent = 0
        for g6 in outg:
            n, edges = dec(g6)
            adj = adj_from_edges(n, edges)
            cuts = maxcut_all(n, adj)
            graph_count += 1
            for side in cuts:
                if not Bconn(n, adj, side):
                    continue
                gd = gamma_data(n, adj, side)
                if gd is None or not gd[1]:
                    continue
                side_count += 1
                c, b = scan_side(
                    g6, n, edges, side, max_bad_reports=1, report_hits=report_hits
                )
                failures += c
                no_descent += b
        total_failures += failures
        total_no_descent += no_descent
        print(
            f"census N={nn}: graphs={graph_count} sides={side_count} "
            f"interval-failures={failures} no-descent={no_descent}",
            flush=True,
        )
        if no_descent:
            break
    return total_failures, total_no_descent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--census-max", type=int, default=0)
    ap.add_argument("--skip-n26", action="store_true")
    ap.add_argument("--n26-reachable", action="store_true")
    ap.add_argument("--report-hits", action="store_true")
    args = ap.parse_args()

    total_failures = total_bad = 0
    if not args.skip_n26:
        f, b = scan_n26_parity(report_hits=args.report_hits)
        total_failures += f
        total_bad += b
    if args.n26_reachable:
        f, b = scan_n26_singleton_reachable(report_hits=args.report_hits)
        total_failures += f
        total_bad += b
    if args.census_max:
        f, b = scan_census(args.census_max, report_hits=args.report_hits)
        total_failures += f
        total_bad += b
    print(f"TOTAL interval-failures={total_failures} no-descent={total_bad}")


if __name__ == "__main__":
    main()
