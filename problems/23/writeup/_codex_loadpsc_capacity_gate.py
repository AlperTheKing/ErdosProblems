"""Direct exact gate for the LOAD-PSC capacity formulation.

For each tested connected-B max-cut structure, and for each critical threshold
tau in {0} union {T(v)}, set a(v)=min(T(v), tau).  Check

  c * sum_v a(v) * (L - a(v)) >= N * (TV_B(a) - TV_M(a))

for c=5 and c=25, where L=N+N^2/25-|M|.

This is the capacity form of PREFIX-LOAD-PSC-c.  It is intentionally small and
independent of the older running-balance script, so mismatches are easier to
audit.
"""

from __future__ import annotations

import argparse
import subprocess
from fractions import Fraction as F

from _bdef_construct import Cn, mycielski, union_disjoint
from _h import Bconn, GENG, dec
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _verify_two_lane import build_two_lane
from _wf_lrsbreak_0 import build_k_lane
from _wf_lrsbreak_0c import greedy_chords


def adj_of(n, edges):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def blowup(parts):
    offsets = [0]
    for x in parts:
        offsets.append(offsets[-1] + x)
    n = offsets[-1]
    edges = []
    q = len(parts)
    for i in range(q):
        j = (i + 1) % q
        for u in range(offsets[i], offsets[i + 1]):
            for v in range(offsets[j], offsets[j + 1]):
                edges.append((min(u, v), max(u, v)))
    return n, sorted(set(edges))


def bridge(block1, block2, u, v):
    n, edges = union_disjoint(block1, block2)
    return n, edges + [(u, block1[0] + v)]


def tv_gap(n, adj, side, values):
    tv_b = F(0)
    tv_m = F(0)
    for u in range(n):
        for v in adj[u]:
            if v <= u:
                continue
            d = abs(values[u] - values[v])
            if side[u] != side[v]:
                tv_b += d
            else:
                tv_m += d
    return tv_b - tv_m


def check_cut(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, _mu, _cyc = st
    if not M:
        return

    m = len(M)
    L = F(n) + F(n * n, 25) - m
    levels = sorted(set([F(0)] + list(T)))
    for tau in levels:
        a = [min(t, tau) for t in T]
        cap = sum(x * (L - x) for x in a)
        gap = tv_gap(n, adj, side, a)
        if gap < 0:
            acc["negative_gap"] += 1
        for c in (5, 25):
            margin = c * cap - n * gap
            key = f"min{c}"
            if margin < acc[key][0]:
                acc[key] = (margin, name, n, m, str(tau), str(cap), str(gap))
            if tau > 0:
                pos_key = f"min{c}_pos"
                if margin < acc[pos_key][0]:
                    acc[pos_key] = (margin, name, n, m, str(tau), str(cap), str(gap))
            if margin < 0:
                acc[f"viol{c}"] += 1
                if acc[f"first{c}"] is None:
                    acc[f"first{c}"] = (name, n, m, str(tau), str(margin))
        acc["levels"] += 1
    acc["cuts"] += 1


def run(args):
    acc = {
        "cuts": 0,
        "levels": 0,
        "negative_gap": 0,
        "viol5": 0,
        "viol25": 0,
        "first5": None,
        "first25": None,
        "min5": (F(10) ** 30, "", "", "", "", "", ""),
        "min25": (F(10) ** 30, "", "", "", "", "", ""),
        "min5_pos": (F(10) ** 30, "", "", "", "", "", ""),
        "min25_pos": (F(10) ** 30, "", "", "", "", "", ""),
    }

    for L in range(8, args.two_lane_max + 1, 2):
        n, edges, side, _ = build_two_lane(L)
        check_cut(f"two-lane-L{L}", n, adj_of(n, edges), side, acc)

    for Ll, k, gap in [(12, 4, 6), (14, 4, 8), (16, 5, 8)]:
        bad = greedy_chords(Ll, k, gap)
        n, edges, side, _bad = build_k_lane(Ll, k, bad)
        check_cut(f"klane-L{Ll}k{k}", n, adj_of(n, edges), side, acc)

    for nn in range(args.min_n, args.max_n + 1):
        graph6s = subprocess.run(
            [GENG, "-tc", str(nn)], capture_output=True, text=True, check=False
        ).stdout.split()
        before5 = acc["viol5"]
        for g6 in graph6s:
            n, edges = dec(g6)
            adj, cuts = gmins(n, edges)
            for side in cuts:
                check_cut(f"cen{g6}", n, adj, side, acc)
        print(f"census N={nn}: viol5+{acc['viol5'] - before5}", flush=True)

    for cyc in (5, 7, 9):
        for t in range(1, args.blowup_t + 1):
            n, edges = blowup([t] * cyc)
            if n > args.blowup_nmax:
                continue
            adj, cuts = gmins(n, edges)
            for side in cuts[:1]:
                check_cut(f"C{cyc}[{t}]", n, adj, side, acc)

    for parts in ([2, 2, 2, 2, 3], [1, 5, 2, 2, 5], [1, 4, 2, 4, 2, 4, 2], [3, 3, 3, 3, 2], [1, 3, 2, 2, 3]):
        n, edges = blowup(list(parts))
        if n > args.blowup_nmax:
            continue
        adj, cuts = gmins(n, edges)
        for side in cuts[:1]:
            check_cut(f"nu{parts}", n, adj, side, acc)

    if not args.fast:
        grot = mycielski(5, Cn(5))
        extra = [
            ("Grotzsch", grot),
            ("Myc(Grotzsch)", mycielski(grot[0], grot[1])),
            ("M(C7)", mycielski(7, Cn(7))),
            ("M(C9)", mycielski(9, Cn(9))),
            ("C7|Grotzsch", bridge((7, Cn(7)), grot, 0, 0)),
            ("C9|C9", bridge((9, Cn(9)), (9, Cn(9)), 0, 0)),
        ]
        for name, (n, edges) in extra:
            adj, cuts = gmins(n, edges)
            for side in cuts[:2]:
                check_cut(name, n, adj, side, acc)

    print("=== direct LOAD-PSC capacity gate ===")
    print(f"cuts={acc['cuts']} levels={acc['levels']} negative_tv_gap={acc['negative_gap']}")
    print(f"viol5={acc['viol5']} first5={acc['first5']}")
    print(f"viol25={acc['viol25']} first25={acc['first25']}")
    print(f"min5={acc['min5'][0]} at {acc['min5'][1:]}")
    print(f"min25={acc['min25'][0]} at {acc['min25'][1:]}")
    print(f"min5_pos={acc['min5_pos'][0]} at {acc['min5_pos'][1:]}")
    print(f"min25_pos={acc['min25_pos'][0]} at {acc['min25_pos'][1:]}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=7)
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--two-lane-max", type=int, default=20)
    parser.add_argument("--blowup-t", type=int, default=5)
    parser.add_argument("--blowup-nmax", type=int, default=26)
    parser.add_argument("--fast", action="store_true", help="skip Mycielskian/glued gmins calls")
    run(parser.parse_args())
