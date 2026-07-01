"""Gate a coarse scalar budget for non-pentagonal rowwise GERSH.

For any K-component C and row Q of length L,

    sum_{v in Q} Tw_C(v)
      = sum_{g in M_C} E_{P in cyc[g]} |Q cap P|
      <= sum_{g in M_C} min(L, ell(g)).

So ROWWISE-GERSH follows from the scalar budget

    sum_{g in M_C} min(L, ell(g)) <= A = N + N^2/25 - |M|.

This script tests whether that coarse budget is enough away from L=5.
"""

import argparse
import subprocess
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
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    return adj


def blowup(parts):
    off = [0]
    for p in parts:
        off.append(off[-1] + p)
    edges = []
    m = len(parts)
    for i in range(m):
        j = (i + 1) % m
        for a in range(off[i], off[i + 1]):
            for b in range(off[j], off[j + 1]):
                edges.append((min(a, b), max(a, b)))
    return off[-1], sorted(set(edges))


def bridge(block1, block2, u, v):
    n, edges = union_disjoint(block1, block2)
    return n, edges + [(u, block1[0] + v)]


def check_cut(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, _T, _mu, cyc = st
    if not M:
        return
    A = F(n) + F(n * n, 25) - len(M)
    _comp_map, find = kcomponents(n, cyc)
    edges_by_comp = {}
    for f in M:
        edges_by_comp.setdefault(find(cyc[f][0][0]), []).append(f)

    for _comp, fs in edges_by_comp.items():
        for f in fs:
            for path in cyc[f]:
                L = len(path)
                budget = sum(min(L, ell[g]) for g in fs)
                margin = A - budget
                acc["rows"] += 1
                if L == 5:
                    acc["rows5"] += 1
                    if margin < acc["min5"][0]:
                        acc["min5"] = (margin, name, n, len(M), f, tuple(path), A, budget)
                    continue
                acc["rows_non5"] += 1
                if margin < acc["min_non5"][0]:
                    acc["min_non5"] = (margin, name, n, len(M), f, tuple(path), A, budget, tuple(sorted(ell[g] for g in fs)))
                if margin < 0:
                    acc["viol_non5"] += 1
                    if acc["first"] is None:
                        acc["first"] = {
                            "name": name,
                            "n": n,
                            "side": "".join(map(str, side)),
                            "m": len(M),
                            "A": str(A),
                            "f": f,
                            "row": tuple(path),
                            "L": L,
                            "budget": budget,
                            "margin": str(margin),
                            "component_lengths": tuple(sorted(ell[g] for g in fs)),
                        }


def run_gmin(name, n, edges, acc, max_cuts=None):
    adj, cuts = gmins(n, edges)
    if max_cuts is not None:
        cuts = cuts[:max_cuts]
    for side in cuts:
        check_cut(name, n, adj, side, acc)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=7)
    ap.add_argument("--max-n", type=int, default=10)
    ap.add_argument("--two-lane-max", type=int, default=30)
    ap.add_argument("--blowup-t", type=int, default=4)
    ap.add_argument("--blowup-nmax", type=int, default=26)
    ap.add_argument("--fast", action="store_true")
    args = ap.parse_args()

    acc = {
        "rows": 0,
        "rows5": 0,
        "rows_non5": 0,
        "viol_non5": 0,
        "first": None,
        "min_non5": (F(10**18),),
        "min5": (F(10**18),),
    }

    for L in range(8, args.two_lane_max + 1, 2):
        n, edges, side, _ = build_two_lane(L)
        check_cut(f"two-lane-L{L}", n, adj_of(n, edges), side, acc)

    for Ll, k, gap in [(12, 4, 6), (14, 4, 8), (16, 5, 8)]:
        bad = greedy_chords(Ll, k, gap)
        n, edges, side, _bad = build_k_lane(Ll, k, bad)
        check_cut(f"klane-L{Ll}k{k}", n, adj_of(n, edges), side, acc)

    for c in (5, 7, 9):
        for t in range(1, args.blowup_t + 1):
            n, edges = blowup([t] * c)
            if n <= args.blowup_nmax:
                run_gmin(f"C{c}[{t}]", n, edges, acc, max_cuts=2 if args.fast else None)

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

    for nn in range(args.min_n, args.max_n + 1):
        before = acc["viol_non5"]
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            run_gmin(f"cen{g6}", n, edges, acc)
        print(f"census N={nn}: rows={acc['rows']} non5_viol+={acc['viol_non5'] - before}", flush=True)

    print("=== coarse rowcap budget gate ===")
    print("rows:", acc["rows"])
    print("rows5:", acc["rows5"])
    print("rows_non5:", acc["rows_non5"])
    print("non5 violations:", acc["viol_non5"])
    print("min_non5:", acc["min_non5"])
    print("min5:", acc["min5"])
    print("first:", acc["first"] or "")
    print("VERDICT:", "NON5 COARSE HOLDS" if acc["viol_non5"] == 0 else "NON5 COARSE FAILS")


if __name__ == "__main__":
    main()
