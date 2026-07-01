"""Exact gate for a non-pentagonal row-cap strengthening.

Candidate:

    If a shortest row Q has length L > 5, then
        sum_{v in Q} Tw_C(v) <= N + (N^2/25 - |M|)/2.

Together with OC-PMS for L=5,

    I(P)-N <= (2/3)*(N^2/25-|M|),

this would imply ROWWISE-GERSH:

    sum_{v in Q} Tw_C(v) <= N + N^2/25 - |M|.
"""

import argparse
import subprocess
from collections import Counter, defaultdict
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
    M, _ell, _T, _mu, cyc = st
    if not M:
        return
    eta = F(n * n, 25) - len(M)
    cap = F(n) + eta / 2
    _comp_map, find = kcomponents(n, cyc)
    edges_by_comp = defaultdict(list)
    for f in M:
        edges_by_comp[find(cyc[f][0][0])].append(f)

    for comp, fs in edges_by_comp.items():
        tw = [F(0) for _ in range(n)]
        for g in fs:
            den = F(len(cyc[g]))
            counts = Counter()
            for path in cyc[g]:
                counts.update(path)
            for v, c in counts.items():
                tw[v] += F(c, 1) / den

        for f in fs:
            for path in cyc[f]:
                L = len(path)
                if L <= 5:
                    continue
                val = sum(tw[v] for v in path)
                margin = cap - val
                surplus = F(L * L - 25, 50)
                surplus_margin = margin - surplus
                acc["rows"] += 1
                if margin < acc["min_margin"][0]:
                    acc["min_margin"] = (margin, name, n, len(M), comp, f, tuple(path), cap, val)
                if surplus_margin < acc["min_surplus_margin"][0]:
                    acc["min_surplus_margin"] = (
                        surplus_margin,
                        name,
                        n,
                        len(M),
                        comp,
                        f,
                        tuple(path),
                        cap,
                        val,
                        surplus,
                    )
                old = acc["by_len"].get(L)
                if old is None or margin < old[0]:
                    acc["by_len"][L] = (margin, name, n, len(M), comp, f, tuple(path), cap, val)
                old_surplus = acc["surplus_by_len"].get(L)
                if old_surplus is None or surplus_margin < old_surplus[0]:
                    acc["surplus_by_len"][L] = (
                        surplus_margin,
                        name,
                        n,
                        len(M),
                        comp,
                        f,
                        tuple(path),
                        cap,
                        val,
                        surplus,
                    )
                if surplus_margin < 0:
                    acc["surplus_viol"] += 1
                    if acc["surplus_first"] is None:
                        acc["surplus_first"] = {
                            "name": name,
                            "n": n,
                            "side": "".join(map(str, side)),
                            "m": len(M),
                            "eta": str(eta),
                            "cap": str(cap),
                            "component": comp,
                            "f": f,
                            "row": tuple(path),
                            "row_value": str(val),
                            "surplus": str(surplus),
                            "surplus_margin": str(surplus_margin),
                        }
                if margin < 0:
                    acc["viol"] += 1
                    if acc["first"] is None:
                        acc["first"] = {
                            "name": name,
                            "n": n,
                            "side": "".join(map(str, side)),
                            "m": len(M),
                            "eta": str(eta),
                            "cap": str(cap),
                            "component": comp,
                            "f": f,
                            "row": tuple(path),
                            "row_value": str(val),
                            "margin": str(margin),
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
        "viol": 0,
        "surplus_viol": 0,
        "first": None,
        "surplus_first": None,
        "min_margin": (F(10**18),),
        "min_surplus_margin": (F(10**18),),
        "by_len": {},
        "surplus_by_len": {},
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
        before = acc["viol"]
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            run_gmin(f"cen{g6}", n, edges, acc)
        print(f"census N={nn}: rows={acc['rows']} viol+={acc['viol'] - before}", flush=True)

    print("=== NON5-HALF rowcap gate ===")
    print("rows L>5:", acc["rows"])
    print("violations:", acc["viol"])
    print("LONG-SURPLUS violations:", acc["surplus_viol"])
    print("min_margin:", acc["min_margin"])
    print("min_surplus_margin:", acc["min_surplus_margin"])
    print("min_margin_by_len:")
    for L in sorted(acc["by_len"]):
        print(" ", L, acc["by_len"][L])
    print("min_surplus_margin_by_len:")
    for L in sorted(acc["surplus_by_len"]):
        print(" ", L, acc["surplus_by_len"][L])
    print("first:", acc["first"] or "")
    print("surplus_first:", acc["surplus_first"] or "")
    verdict = acc["viol"] == 0 and acc["surplus_viol"] == 0
    print("VERDICT:", "NON5-HALF+SURPLUS HOLDS" if verdict else "NON5-HALF+SURPLUS FAILS")


if __name__ == "__main__":
    main()
