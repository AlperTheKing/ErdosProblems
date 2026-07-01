"""Classify rows where the rowwise GERSH load exceeds N.

ROWWISE-GERSH target:

    rowval(Q,C) := sum_{v in Q} Tw_C(v) <= A = N + N^2/25 - |M|.

This diagnostic records the sharper overload regime rowval(Q,C) > N.  If
overload only occurs in length-5 / pentagonal components, the proof can split:
long rows have surplus, and length-5 rows use a row-cap stability theorem.
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


def comp_vertices(fs, cyc):
    out = set()
    for f in fs:
        for path in cyc[f]:
            out.update(path)
    return out


def check_cut(name, n, adj, side, acc, examples):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, _T, _mu, cyc = st
    if not M:
        return
    eta = F(n * n, 25) - len(M)
    A = F(n) + eta
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

        cverts = comp_vertices(fs, cyc)
        comp_lens = tuple(sorted(set(ell[g] for g in fs)))
        global_comp = len(cverts) == n
        for f in fs:
            for path in cyc[f]:
                val = sum(tw[v] for v in path)
                margin = A - val
                acc["rows"] += 1
                if margin < acc["min_margin"][0]:
                    acc["min_margin"] = (
                        margin,
                        name,
                        n,
                        len(M),
                        f,
                        tuple(path),
                        A,
                        val,
                        comp_lens,
                        len(cverts),
                    )
                if val <= n:
                    continue
                over = val - n
                acc["over_rows"] += 1
                key = (len(path), comp_lens, global_comp)
                acc["groups"][key] += 1
                if eta > 0:
                    ratio = over / eta
                    if ratio > acc["max_ratio"][0]:
                        acc["max_ratio"] = (
                            ratio,
                            name,
                            n,
                            len(M),
                            f,
                            tuple(path),
                            val,
                            A,
                            comp_lens,
                            len(cverts),
                        )
                    old = acc["max_ratio_by_len"].get(len(path))
                    if old is None or ratio > old[0]:
                        acc["max_ratio_by_len"][len(path)] = (
                            ratio,
                            name,
                            n,
                            len(M),
                            f,
                            tuple(path),
                            val,
                            A,
                            comp_lens,
                            len(cverts),
                        )
                else:
                    acc["eta_zero_over"] += 1
                if len(examples) < 20:
                    examples.append(
                        {
                            "name": name,
                            "n": n,
                            "m": len(M),
                            "side": "".join(map(str, side)),
                            "f": f,
                            "row": tuple(path),
                            "row_len": len(path),
                            "rowval": str(val),
                            "A": str(A),
                            "overN": str(over),
                            "margin": str(margin),
                            "comp_lens": comp_lens,
                            "comp_vertices": len(cverts),
                            "global_comp": global_comp,
                        }
                    )


def run_gmin(name, n, edges, acc, examples, max_cuts=None):
    adj, cuts = gmins(n, edges)
    if max_cuts is not None:
        cuts = cuts[:max_cuts]
    for side in cuts:
        check_cut(name, n, adj, side, acc, examples)


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
        "over_rows": 0,
        "eta_zero_over": 0,
        "groups": Counter(),
        "max_ratio": (F(-1),),
        "max_ratio_by_len": {},
        "min_margin": (F(10**18),),
    }
    examples = []

    for L in range(8, args.two_lane_max + 1, 2):
        n, edges, side, _ = build_two_lane(L)
        check_cut(f"two-lane-L{L}", n, adj_of(n, edges), side, acc, examples)

    for Ll, k, gap in [(12, 4, 6), (14, 4, 8), (16, 5, 8)]:
        bad = greedy_chords(Ll, k, gap)
        n, edges, side, _bad = build_k_lane(Ll, k, bad)
        check_cut(f"klane-L{Ll}k{k}", n, adj_of(n, edges), side, acc, examples)

    for c in (5, 7, 9):
        for t in range(1, args.blowup_t + 1):
            n, edges = blowup([t] * c)
            if n <= args.blowup_nmax:
                run_gmin(f"C{c}[{t}]", n, edges, acc, examples, max_cuts=2 if args.fast else None)

    named = [
        ("Grotzsch", mycielski(5, Cn(5))),
        ("M(C7)", mycielski(7, Cn(7))),
        ("C7|Grotzsch", bridge((7, Cn(7)), mycielski(5, Cn(5)), 0, 0)),
        ("C5|C7", bridge((5, Cn(5)), (7, Cn(7)), 0, 0)),
    ]
    grot = named[0][1]
    named.append(("Myc(Grotzsch)", mycielski(grot[0], grot[1])))
    for nm, (n, edges) in named:
        run_gmin(nm, n, edges, acc, examples, max_cuts=2 if args.fast else 3)

    for nn in range(args.min_n, args.max_n + 1):
        before = acc["over_rows"]
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            run_gmin(f"cen{g6}", n, edges, acc, examples)
        print(f"census N={nn}: rows={acc['rows']} over+={acc['over_rows'] - before}", flush=True)

    print("=== rowwise overload classifier ===")
    print("rows:", acc["rows"])
    print("over_rows:", acc["over_rows"])
    print("eta_zero_over:", acc["eta_zero_over"])
    print("min_margin:", acc["min_margin"])
    print("max_over_eta_ratio:", acc["max_ratio"])
    print("max_over_eta_ratio_by_len:")
    for L in sorted(acc["max_ratio_by_len"]):
        print(" ", L, acc["max_ratio_by_len"][L])
    print("groups:")
    for key, count in sorted(acc["groups"].items(), key=lambda kv: (-kv[1], kv[0])):
        print(" ", count, key)
    print("examples:")
    for ex in examples:
        print(" ", ex)


if __name__ == "__main__":
    main()
