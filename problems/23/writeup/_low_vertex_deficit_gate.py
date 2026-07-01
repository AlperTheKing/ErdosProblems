"""Diagnostic gate for a vertex-local proof attempt of LOW-GAMMA-CAP.

For a full-low band [a,b] with 2b<=N and H={T>a}, LOW-GAMMA-CAP would follow
from the stronger outside-vertex inequality

    N * max(0, net_H(w)) <= |H| * (N - T(w))        for every w notin H,

where net_H(w) is the signed boundary contribution from edges w--H:
+1 for cut/B edges and -1 for bad/M edges.

This is deliberately marked diagnostic: if it fails, the low deposit cannot be
proved by a purely vertex-local outside-deficit payment.
"""

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


def chk(name, n, adj, side, acc, stop_first=False):
    if not Bconn(n, adj, side):
        return False
    st = struct_for_side(n, adj, side)
    if st is None:
        return False
    M, _ell, T, _mu, _cyc = st
    if not M:
        return False

    levels = [F(0)] + sorted(set(F(t) for t in T if t > 0))
    for a, b in zip(levels, levels[1:]):
        if 2 * b > n:
            continue
        H = {v for v in range(n) if F(T[v]) > a}
        if not H:
            continue
        h = len(H)
        for w in range(n):
            if w in H:
                continue
            net = 0
            for u in adj[w]:
                if u not in H:
                    continue
                net += 1 if side[u] != side[w] else -1
            if net <= 0:
                continue
            margin = F(h) * (n - F(T[w])) - F(n) * net
            acc["rows"] += 1
            if margin < acc["minm"][0]:
                acc["minm"] = (margin, name, n, len(M), str(a), str(b), h, w, str(T[w]), net)
            if margin < 0:
                acc["viol"] += 1
                if acc["first"] is None:
                    acc["first"] = (name, "".join(map(str, side)), n, len(M), str(a), str(b), h, w, str(T[w]), net, str(margin))
                if stop_first:
                    return True
    return False


def blowup(parts):
    offsets = [0]
    for part in parts:
        offsets.append(offsets[-1] + part)
    n = offsets[-1]
    edges = []
    for i in range(len(parts)):
        j = (i + 1) % len(parts)
        for u in range(offsets[i], offsets[i + 1]):
            for v in range(offsets[j], offsets[j + 1]):
                edges.append((min(u, v), max(u, v)))
    return n, sorted(set(edges))


def bridge(block1, block2, u, v):
    n, edges = union_disjoint(block1, block2)
    return n, edges + [(u, block1[0] + v)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=7)
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--two-lane-max", type=int, default=40)
    parser.add_argument("--fast", action="store_true")
    parser.add_argument("--stop-first", action="store_true")
    args = parser.parse_args()

    acc = {"rows": 0, "viol": 0, "first": None, "minm": (F(10**18), None)}

    for L in range(8, args.two_lane_max + 1, 2):
        n, edges, side, _bad = build_two_lane(L)
        if chk(f"two-lane-L{L}", n, adj_of(n, edges), side, acc, args.stop_first):
            break

    for L, k, gap in ((12, 4, 6), (14, 4, 8), (16, 5, 8), (18, 5, 10), (20, 6, 10)):
        bad = greedy_chords(L, k, gap)
        n, edges, side, _bad = build_k_lane(L, k, bad)
        if chk(f"k-lane-L{L}-k{k}", n, adj_of(n, edges), side, acc, args.stop_first):
            break
    print(f"  lane diagnostics done: viol={acc['viol']}", flush=True)

    for n0 in range(args.min_n, args.max_n + 1):
        before = acc["viol"]
        for g6 in subprocess.run([GENG, "-tc", str(n0)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            adj, cuts = gmins(n, edges)
            for side in cuts:
                if chk(f"cen{g6}", n, adj, side, acc, args.stop_first):
                    break
            if args.stop_first and acc["first"] is not None:
                break
        print(f"  census N={n0} (viol+{acc['viol']-before})", flush=True)
        if args.stop_first and acc["first"] is not None:
            break

    if not args.fast:
        for cyc in (5, 7, 9):
            for t in range(1, 6):
                n, edges = blowup([t] * cyc)
                if n > 26:
                    continue
                adj, cuts = gmins(n, edges)
                for side in cuts[:2]:
                    chk(f"C{cyc}[{t}]", n, adj, side, acc, args.stop_first)

        grot = mycielski(5, Cn(5))
        named = [
            ("Grotzsch", grot),
            ("Myc(Grotzsch)", mycielski(grot[0], grot[1])),
            ("M(C7)", mycielski(7, Cn(7))),
            ("C7|Grotzsch", bridge((7, Cn(7)), grot, 0, 0)),
        ]
        for name, (n, edges) in named:
            adj, cuts = gmins(n, edges)
            for side in cuts[:3]:
                chk(name, n, adj, side, acc, args.stop_first)
        print("  blow-ups + Mycielskians + glued done", flush=True)

    print("\n=== LOW-VERTEX-DEFICIT diagnostic ===")
    print(f"  positive outside vertex rows={acc['rows']} violations={acc['viol']}")
    print(f"  min margin={acc['minm'][0]} at {acc['minm'][1:]}")
    if acc["first"]:
        print(f"  first violation={acc['first']}")
    print(f"  === LOW-VERTEX-DEFICIT {'HOLDS' if not acc['viol'] else 'FAILS'} ===")


if __name__ == "__main__":
    main()
