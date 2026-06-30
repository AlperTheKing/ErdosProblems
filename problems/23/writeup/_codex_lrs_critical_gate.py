"""Critical-battery gate for Load-Rayleigh Bad-Count Slack.

This mirrors the SBC critical battery but checks only:

    (sum_v T(v)^2) / Gamma + |M| <= N + N^2/25.
"""

from __future__ import annotations

import numpy as np
from fractions import Fraction as F

from _bdef_construct import Cn, mycielski
from _M_tailswitch_gate import build_pd
from _stark1 import gmins
from _tail_positive_extra_counterexample import add_cut_path, adj_from_edges
from _verify_two_lane import build_two_lane
from _satzmu_conn import struct_for_side


def adj_of(n, edges):
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    return adj


def blowup(parts):
    count = len(parts)
    off = [0] * (count + 1)
    for idx in range(count):
        off[idx + 1] = off[idx] + parts[idx]
    n = off[count]
    edges = []
    for idx in range(count):
        nxt = (idx + 1) % count
        for a in range(off[idx], off[idx + 1]):
            for b in range(off[nxt], off[nxt + 1]):
                edges.append((min(a, b), max(a, b)))
    return n, sorted(set(edges))


def blowup_with_standard_cut(parts):
    """Odd-cycle blow-up with the standard alternating maximum-cut side.

    Parts are colored by parity; for an odd cycle exactly the wrap edge has
    same-side endpoints.  This is the extremal cut for uniform blow-ups and the
    standard stress cut used throughout this project.
    """
    n, edges = blowup(parts)
    part = []
    for idx, size in enumerate(parts):
        part.extend([idx] * size)
    side = [idx % 2 for idx in part]
    return n, edges, side


def lrs_check(name, n, adj, side, rows):
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    bad_edges, ell, loads_t, _mu, _cyc = st
    m = len(bad_edges)
    if not m:
        return
    gamma = sum(ell[f] * ell[f] for f in bad_edges)
    ray = sum(t * t for t in loads_t) / gamma
    rhs = F(n) + F(n * n, 25) - F(m)
    margin = rhs - ray
    rows.append(
        (
            margin,
            name,
            n,
            m,
            gamma,
            ray,
            rhs,
            min(loads_t),
            max(loads_t),
        )
    )


def main():
    rows = []

    for cyc in (5, 7, 9, 11):
        for t in range(1, 4):
            n, edges, side = blowup_with_standard_cut([t] * cyc)
            lrs_check(f"C{cyc}[{t}]", n, adj_of(n, edges), side, rows)

    for parts in (
        [1, 3, 2, 2, 3],
        [1, 4, 2, 4, 2, 4, 2],
        [3, 3, 3, 3, 2],
        [1, 4, 2, 2, 4],
        [2, 5, 3, 3, 5],
    ):
        n, edges, side = blowup_with_standard_cut(parts)
        lrs_check(f"blow{parts}", n, adj_of(n, edges), side, rows)

    for length in range(8, 21, 2):
        n, edges, side, _bad = build_two_lane(length)
        lrs_check(f"two-lane-L{length}", n, adj_of(n, edges), side, rows)

    grot = mycielski(5, Cn(5))
    for name, (n, edges) in (
        ("Grotzsch", grot),
    ):
        adj, cuts = gmins(n, edges)
        for side in cuts[:3]:
            lrs_check(name, n, adj, side, rows)

    n, edges = build_pd(12, [(0, 8), (2, 6)])
    side = [v % 2 for v in range(n)]
    n, edges, side = add_cut_path(n, list(edges), side, 0, 12, 14)
    edges = sorted(set(edges + [(13, 27)]))
    lrs_check("merged-detour-N39", n, adj_of(n, edges), side, rows)

    for length, copies in ((12, 2), (12, 3), (16, 2), (12, 4)):
        offset = 0
        edges_all = []
        side_all = []
        for _ in range(copies):
            n1, edges1, side1, _bad = build_two_lane(length)
            edges_all.extend((a + offset, b + offset) for a, b in edges1)
            side_all.extend(side1)
            offset += n1
        lrs_check(
            f"stack{copies}x-twolane-L{length}",
            offset,
            adj_of(offset, sorted(set(edges_all))),
            side_all,
            rows,
        )

    rows.sort(key=lambda r: (float(r[0]), r[1]))
    print("=== LRS critical gate ===", flush=True)
    for row in rows[:24]:
        margin, name, n, m, gamma, ray, rhs, tmin, tmax = row
        print(
            f"  margin={margin} name={name} N={n} m={m} Gamma={gamma} "
            f"ray={ray} rhs={rhs} T=[{tmin},{tmax}]",
            flush=True,
        )
    viol = [row for row in rows if row[0] < 0]
    print(f"total={len(rows)} violations={len(viol)}", flush=True)
    if viol:
        print(f"first_violation={viol[0]}", flush=True)


if __name__ == "__main__":
    main()
