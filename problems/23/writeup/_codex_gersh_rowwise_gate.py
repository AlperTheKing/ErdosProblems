"""Exact gate for a rowwise strengthening of component GERSH.

Known surviving target (GERSH), per K-component C and bad edge f:

    (1/|cyc[f]|) * sum_{Q in cyc[f]} sum_{v in Q} Tw_C(v) <= A,

where

    A = N + N^2/25 - |M|,
    Tw_C(v) = sum_{g in C} #{Q in cyc[g] : v in Q} / |cyc[g]|.

This script tests the sharper pointwise-row version:

    sum_{v in Q} Tw_C(v) <= A    for every shortest row Q of every f.

If it holds, GERSH reduces to a simpler corridor statement.  If it fails,
the first witness explains why row-averaging is essential.
"""

import argparse
import subprocess
from fractions import Fraction as F

from _h import Bconn, GENG, dec
from _satzmu_conn import kcomponents, struct_for_side
from _stark1 import gmins
from _bdef_construct import Cn, mycielski, union_disjoint
from _verify_two_lane import build_two_lane
from _wf_lrsbreak_0 import build_k_lane
from _wf_lrsbreak_0c import greedy_chords


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


def bridge(block1, block2, u, v):
    n, edges = union_disjoint(block1, block2)
    return n, edges + [(u, block1[0] + v)]


def check_cut(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, _ell, _T, _mu, cyc = st
    if not M:
        return
    A = F(n) + F(n * n, 25) - len(M)
    _comp_map, find = kcomponents(n, cyc)
    edges_by_comp = {}
    for f in M:
        edges_by_comp.setdefault(find(cyc[f][0][0]), []).append(f)

    for comp, fs in edges_by_comp.items():
        tw = [F(0) for _ in range(n)]
        for g in fs:
            denom = F(len(cyc[g]))
            counts = {}
            for path in cyc[g]:
                for v in path:
                    counts[v] = counts.get(v, 0) + 1
            for v, c in counts.items():
                tw[v] += F(c, 1) / denom

        for f in fs:
            total = F(0)
            worst_f = None
            for path in cyc[f]:
                val = sum(tw[v] for v in path)
                total += val
                margin = A - val
                L = len(path)
                old = acc["by_len"].get(L)
                if old is None or margin < old[0]:
                    acc["by_len"][L] = (margin, name, n, len(M), f, tuple(path), A, val)
                acc["rows"] += 1
                if margin < acc["min_row"][0]:
                    acc["min_row"] = (margin, name, n, len(M), comp, f, tuple(path), A, val)
                if margin < 0:
                    acc["viol"] += 1
                    if acc["first"] is None:
                        acc["first"] = {
                            "name": name,
                            "n": n,
                            "side": "".join(map(str, side)),
                            "beta": len(M),
                            "A": str(A),
                            "component": comp,
                            "f": f,
                            "row": tuple(path),
                            "row_value": str(val),
                            "margin": str(margin),
                        }
                    if worst_f is None or val > worst_f:
                        worst_f = val
            avg = total / len(cyc[f])
            acc["edges"] += 1
            avg_margin = A - avg
            if avg_margin < acc["min_avg"][0]:
                acc["min_avg"] = (avg_margin, name, n, len(M), comp, f, A, avg)


def run_gmin(name, n, edges, acc, max_cuts=None):
    adj, cuts = gmins(n, edges)
    if max_cuts is not None:
        cuts = cuts[:max_cuts]
    for side in cuts:
        check_cut(name, n, adj, side, acc)
        if acc["first"] is not None:
            return


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=7)
    ap.add_argument("--max-n", type=int, default=10)
    ap.add_argument("--two-lane-max", type=int, default=20)
    ap.add_argument("--blowup-t", type=int, default=4)
    ap.add_argument("--blowup-nmax", type=int, default=26)
    ap.add_argument("--stop-first", action="store_true")
    ap.add_argument("--fast", action="store_true")
    args = ap.parse_args()

    acc = {
        "rows": 0,
        "edges": 0,
        "viol": 0,
        "first": None,
        "min_row": (F(10**18),),
        "min_avg": (F(10**18),),
        "by_len": {},
    }

    for L in range(8, args.two_lane_max + 1, 2):
        n, edges, side, _ = build_two_lane(L)
        check_cut(f"two-lane-L{L}", n, adj_of(n, edges), side, acc)
        if args.stop_first and acc["first"]:
            break

    if not (args.stop_first and acc["first"]):
        for Ll, k, gap in [(12, 4, 6), (14, 4, 8), (16, 5, 8)]:
            bad = greedy_chords(Ll, k, gap)
            n, edges, side, _bad = build_k_lane(Ll, k, bad)
            check_cut(f"klane-L{Ll}k{k}", n, adj_of(n, edges), side, acc)
            if args.stop_first and acc["first"]:
                break

    if not (args.stop_first and acc["first"]):
        for c in (5, 7, 9):
            for t in range(1, args.blowup_t + 1):
                n, edges = blowup([t] * c)
                if n <= args.blowup_nmax:
                    run_gmin(f"C{c}[{t}]", n, edges, acc, max_cuts=2 if args.fast else None)
                if args.stop_first and acc["first"]:
                    break
            if args.stop_first and acc["first"]:
                break

    if not (args.stop_first and acc["first"]):
        named = [
            ("Grotzsch", mycielski(5, Cn(5))),
            ("M(C7)", mycielski(7, Cn(7))),
            ("C7|Grotzsch", bridge((7, Cn(7)), mycielski(5, Cn(5)), 0, 0)),
            ("C5|C7", bridge((5, Cn(5)), (7, Cn(7)), 0, 0)),
        ]
        grot = named[0][1]
        named.append(("Myc(Grotzsch)", mycielski(grot[0], grot[1])))
        for nm, (n, edges) in named:
            run_gmin(nm, n, edges, acc, max_cuts=2 if args.fast else 3)
            if args.stop_first and acc["first"]:
                break

    if not (args.stop_first and acc["first"]):
        for nn in range(args.min_n, args.max_n + 1):
            before = acc["viol"]
            for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
                n, edges = dec(g6)
                run_gmin(f"cen{g6}", n, edges, acc)
                if args.stop_first and acc["first"]:
                    break
            print(f"census N={nn}: rows={acc['rows']} viol+={acc['viol'] - before}", flush=True)
            if args.stop_first and acc["first"]:
                break

    print("=== rowwise GERSH gate ===")
    print("edge averages checked:", acc["edges"])
    print("individual rows checked:", acc["rows"])
    print("rowwise violations:", acc["viol"])
    print("min row margin:", acc["min_row"])
    print("min average margin:", acc["min_avg"])
    print("min row margin by length:")
    for L in sorted(acc["by_len"]):
        print(" ", L, acc["by_len"][L])
    print("first:", acc["first"] or "")
    print("VERDICT:", "ROWWISE HOLDS" if acc["viol"] == 0 else "ROWWISE FAILS")


if __name__ == "__main__":
    main()
