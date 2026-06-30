"""Codex gate: path-average crude cap.

Candidate:
  (PAVG2N) for every bad edge f and every shortest B-geodesic P for f,
      (1/ell(f)) * sum_{v in P} T(v) <= 2N.

This is weaker than the false pointwise B2 cap max_v T(v) <= 2N,
but strong enough for the same low-|M| bulk split for PATH/ROW/LRS:
when |M| <= N^2/25 - N, PATH-LRS follows from PAVG2N.

Run from repo root:
  python problems/23/writeup/_codex_pathavg2n_gate.py
"""

import argparse
import subprocess
from fractions import Fraction as F

from _h import Bconn, GENG, dec
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import Cn, mycielski
from _verify_two_lane import build_two_lane
from _wf_lrsbreak_0 import build_k_lane, trifree, cpmax


def adj_of(n, edges):
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    return adj


def blowup(parts):
    m = len(parts)
    off = [0] * (m + 1)
    for i in range(m):
        off[i + 1] = off[i] + parts[i]
    n = off[m]
    edges = []
    for i in range(m):
        j = (i + 1) % m
        for a in range(off[i], off[i + 1]):
            for b in range(off[j], off[j + 1]):
                edges.append((min(a, b), max(a, b)))
    return n, sorted(set(edges))


def greedy_chords(L, k, gap):
    base_n, base_edges, _, _ = build_k_lane(L, k, [])
    adj = adj_of(base_n, base_edges)
    chords = []
    cand = [(a, b) for a in range(L + 1) for b in range(a + gap, L + 1) if (a % 2) == (b % 2)]
    for a, b in cand:
        if b in adj[a] or (adj[a] & adj[b]):
            continue
        adj[a].add(b)
        adj[b].add(a)
        chords.append((a, b))
    return chords


def check_case(name, n, adj, side, acc, require_global=False, edges=None):
    if not Bconn(n, adj, side):
        return
    if require_global:
        opt, bound, optimal = cpmax(n, edges, 120)
        cut = sum(1 for u in range(n) for v in adj[u] if v > u and side[u] != side[v])
        if not (optimal and cut == opt == bound):
            return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, mu, cyc = st
    for f in M:
        for P in cyc[f]:
            avg = sum(T[v] for v in P) / F(ell[f])
            margin = F(2 * n) - avg
            acc["paths"] += 1
            if margin < acc["min"][0]:
                acc["min"] = (margin, name, n, len(M), f, ell[f], avg, P)
            if margin < 0:
                acc["viol"] += 1
                if acc["first"] is None:
                    acc["first"] = (name, n, len(M), f, ell[f], avg, F(2 * n), P)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fast", action="store_true", help="skip slow exhaustive census; test constructive families only")
    args = parser.parse_args()
    acc = {"paths": 0, "viol": 0, "first": None, "min": (F(10**18), "", 0, 0, None, 0, F(0), None)}

    for L in range(8, 22, 2):
        n, edges, side, _ = build_two_lane(L)
        check_case(f"two-lane-L{L}", n, adj_of(n, edges), side, acc)

    if not args.fast:
        for n0 in range(7, 12):
            graphs = subprocess.run([GENG, "-tc", str(n0)], capture_output=True, text=True, check=True).stdout.split()
            for g6 in graphs:
                n, edges = dec(g6)
                adj, cuts = gmins(n, edges)
                for side in cuts:
                    check_case(f"cen-{g6}", n, adj, side, acc)
            print(f"census N={n0} done; paths={acc['paths']} violations={acc['viol']}", flush=True)

    if not args.fast:
        for cyc in (5, 7, 9):
            for t in range(1, 6):
                n, edges = blowup([t] * cyc)
                if n > 28:
                    continue
                adj, cuts = gmins(n, edges)
                for side in cuts[:1]:
                    check_case(f"C{cyc}[{t}]", n, adj, side, acc)

        for parts in ([2, 2, 2, 2, 3], [1, 5, 2, 2, 5], [1, 4, 2, 4, 2, 4, 2], [3, 3, 3, 3, 2]):
            n, edges = blowup(parts)
            if n > 28:
                continue
            adj, cuts = gmins(n, edges)
            for side in cuts[:1]:
                check_case(f"blow-{parts}", n, adj, side, acc)

        for name, (n, edges) in [
            ("Grotzsch", mycielski(5, Cn(5))),
            ("Myc(Grotzsch)", mycielski(*mycielski(5, Cn(5)))),
            ("M(C7)", mycielski(7, Cn(7))),
            ("M(C9)", mycielski(9, Cn(9))),
        ]:
            adj, cuts = gmins(n, edges)
            for side in cuts[:2]:
                check_case(name, n, adj, side, acc)

    # CP-SAT-certified B2 breakers from _wf_lrsbreak_0c.
    for L, k, gap in ((12, 4, 6), (14, 4, 8)):
        bad = greedy_chords(L, k, gap)
        n, edges, side, _ = build_k_lane(L, k, bad)
        adj = adj_of(n, edges)
        assert trifree(n, adj)
        check_case(f"klane-L{L}-k{k}-g{gap}", n, adj, side, acc, require_global=True, edges=edges)

    print("=== PAVG2N exact gate ===")
    print(f"paths={acc['paths']} violations={acc['viol']}")
    margin, name, n, m, f, ell, avg, path = acc["min"]
    print(f"min margin={margin} = {float(margin):.6f}")
    print(f"arg name={name} N={n} |M|={m} f={f} ell={ell} avg={avg} path={path}")
    if acc["first"] is not None:
        print(f"first violation={acc['first']}")


if __name__ == "__main__":
    main()
