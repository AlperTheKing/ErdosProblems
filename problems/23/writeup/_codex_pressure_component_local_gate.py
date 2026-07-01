"""Exact gate for a component-local strengthening of PRESSURE-SURPLUS-HALL.

For each super-level band H={T>s}, assign each boundary edge of H to the
K-component of the endpoint lying in H.  This decomposes

    sigma(H)=delta_B(H)-delta_M(H)

as a sum of signed component pressures sigma_C(H).

The tested strengthening is:

    Pressure_C(k) <= max(0, Source_C(k)-Volume_C(k))

for every K-component C and prefix k, where Source/Volume are the same
component banks used in _pressure_surplus_hall.py.

If true, it proves PRESSURE-SURPLUS-HALL componentwise.  If false, the witness
shows that the verified global Hall inequality genuinely needs pooling across
K-components.
"""

from __future__ import annotations

import argparse
import subprocess
from collections import defaultdict
from fractions import Fraction as F

from _bdef_construct import Cn, mycielski, union_disjoint
from _h import Bconn, GENG, dec
from _satzmu_conn import kcomponents, struct_for_side
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


def check_cut(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, _ell, T, _mu, cyc = st
    if not M:
        return

    beta = len(M)
    eta = F(n * n, 25) - beta
    theta = (F(n) + eta) / 2
    _comp_map, find = kcomponents(n, cyc)
    comps = sorted({find(v) for v in range(n)})
    levels = sorted(set([F(0), theta] + [F(t) for t in T if t > 0]))

    src = defaultdict(F)
    vol = defaultdict(F)
    press = defaultdict(F)
    acc["cuts"] += 1

    for idx, (a, b) in enumerate(zip(levels, levels[1:]), start=1):
        width = b - a
        if width <= 0:
            continue
        H = {v for v, t in enumerate(T) if F(t) > a}
        if not H:
            continue
        alpha = 25 * (F(n) + eta - (a + b))

        counts = defaultdict(int)
        for v in H:
            counts[find(v)] += 1
        for c in comps:
            amount = width * abs(alpha) * counts[c]
            if alpha > 0:
                src[c] += amount
            elif alpha < 0:
                vol[c] += amount

        sigma_c = defaultdict(int)
        seen = set()
        for u in H:
            cu = find(u)
            for v in adj[u]:
                if v in H:
                    continue
                e = (min(u, v), max(u, v))
                if e in seen:
                    continue
                seen.add(e)
                sigma_c[cu] += 1 if side[u] != side[v] else -1

        for c, sig in sigma_c.items():
            press[c] += 5 * F(n) * width * sig

        for c in comps:
            bank = src[c] - vol[c]
            margin = (bank if bank > 0 else F(0)) - press[c]
            acc["rows"] += 1
            if margin < acc["min"][0]:
                acc["min"] = (margin, name, n, beta, idx, c, str(a), str(b), str(bank), str(press[c]))
            if margin < 0:
                acc["viol"] += 1
                if acc["first"] is None:
                    acc["first"] = acc["min"]
                return


def run(args):
    acc = {
        "cuts": 0,
        "rows": 0,
        "viol": 0,
        "first": None,
        "min": (F(10) ** 30, "", "", "", "", "", "", "", "", ""),
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
        before = acc["viol"]
        for g6 in graph6s:
            n, edges = dec(g6)
            adj, cuts = gmins(n, edges)
            for side in cuts:
                check_cut(f"cen{g6}", n, adj, side, acc)
                if acc["viol"] and args.stop_first:
                    print_summary(acc)
                    return
        print(f"census N={nn}: viol+{acc['viol'] - before}", flush=True)

    for cyc in (5, 7, 9):
        for t in range(1, args.blowup_t + 1):
            n, edges = blowup([t] * cyc)
            if n > args.blowup_nmax:
                continue
            adj, cuts = gmins(n, edges)
            for side in cuts[:1]:
                check_cut(f"C{cyc}[{t}]", n, adj, side, acc)

    if not args.fast:
        grot = mycielski(5, Cn(5))
        extra = [
            ("Grotzsch", grot),
            ("Myc(Grotzsch)", mycielski(grot[0], grot[1])),
            ("M(C7)", mycielski(7, Cn(7))),
            ("C7|Grotzsch", bridge((7, Cn(7)), grot, 0, 0)),
        ]
        for name, (n, edges) in extra:
            adj, cuts = gmins(n, edges)
            for side in cuts[:2]:
                check_cut(name, n, adj, side, acc)

    print_summary(acc)


def print_summary(acc):
    print("=== component-local PRESSURE-SURPLUS gate ===")
    print(f"cuts={acc['cuts']} rows={acc['rows']} violations={acc['viol']}")
    print(f"min={acc['min'][0]} at {acc['min'][1:]}")
    if acc["first"] is not None:
        print(f"first={acc['first']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=7)
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--two-lane-max", type=int, default=20)
    parser.add_argument("--blowup-t", type=int, default=3)
    parser.add_argument("--blowup-nmax", type=int, default=22)
    parser.add_argument("--fast", action="store_true")
    parser.add_argument("--stop-first", action="store_true")
    run(parser.parse_args())
