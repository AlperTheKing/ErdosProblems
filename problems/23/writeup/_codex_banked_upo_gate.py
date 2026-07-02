"""Exact gate for a banked UPO position-flow Hall statement.

For a unique-geodesic long row Q=(x_0,...,x_{L-1}), put

    d_i = Tw_C(x_i) - 1.

Let B-components of V\Q have attachment spans on Q and capacities equal to
component size.  The old UPO Hall target was

    sum_{i in I} d_i <= sum_{C: span(C) meets I} |C|.

That proves ROWSUM<=N, which is false in the two-lane regime.  The corrected
banked version allows the LONG-SURPLUS bank

    bank(Q)=eta/2-(L^2-25)/50.

Gate:

    sum_{i in I} d_i <= cap(I) + bank(Q)

for every position subset I.  The full-set case is exactly LONG-SURPLUS for
unique rows.  This is a position-level shadow of the bclosed1 row-union Hall
candidate, but with far smaller Hall state.
"""

import argparse
import contextlib
import io
import itertools
import subprocess
from fractions import Fraction as F

with contextlib.redirect_stdout(io.StringIO()):
    from _bdef_construct import Cn, mycielski, union_disjoint
    from _codex_rowcap_non5_half_gate import adj_of, blowup
    from _h import Bconn, GENG, dec
    from _satzmu_conn import kcomponents, struct_for_side
    from _stark1 import gmins
    from _verify_two_lane import build_two_lane
    from _wf_lrsbreak_0 import build_k_lane


def greedy_chords(L, k, gap):
    base_n, base_E, _, _ = build_k_lane(L, k, [])
    adj = [set() for _ in range(base_n)]
    for a, b in base_E:
        adj[a].add(b)
        adj[b].add(a)
    chords = []
    cand = [
        (a, b)
        for a in range(0, L + 1)
        for b in range(a + gap, L + 1)
        if (a % 2) == (b % 2)
    ]
    for a, b in cand:
        if b in adj[a] or (adj[a] & adj[b]):
            continue
        adj[a].add(b)
        adj[b].add(a)
        chords.append((a, b))
    return chords


def component_spans(n, adj, side, qrow):
    qset = set(qrow)
    pos = {v: i for i, v in enumerate(qrow)}
    rest = [v for v in range(n) if v not in qset]
    par = {v: v for v in rest}

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x

    for u in rest:
        for v in adj[u]:
            if v in qset:
                continue
            if side[u] != side[v]:
                par[find(u)] = find(v)

    comps = {}
    for v in rest:
        comps.setdefault(find(v), set()).add(v)

    out = []
    for C in comps.values():
        attach = {
            pos[x]
            for u in C
            for x in adj[u]
            if x in qset and side[u] != side[x]
        }
        if attach:
            out.append((min(attach), max(attach), len(C), tuple(sorted(C))))
    return out


def position_sets(L, all_subsets):
    if all_subsets:
        for mask in range(1, 1 << L):
            yield {i for i in range(L) if (mask >> i) & 1}
        return
    for a in range(L):
        for b in range(a, L):
            yield set(range(a, b + 1))


def check_cut(
    name,
    n,
    edges,
    side,
    acc,
    stop_first=False,
    all_subsets=False,
    max_row_len=None,
):
    adj = adj_of(n, edges)
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, _ell, _T, _mu, cyc = st
    if not M:
        return
    eta = F(n * n, 25) - len(M)
    _comp_map, find = kcomponents(n, cyc)
    by_comp = {}
    for g in M:
        by_comp.setdefault(find(cyc[g][0][0]), []).append(g)

    Tw_by_comp = {}
    for comp, fs in by_comp.items():
        Tw = [F(0)] * n
        for g in fs:
            den = F(len(cyc[g]))
            for P in cyc[g]:
                for v in P:
                    Tw[v] += F(1, 1) / den
        Tw_by_comp[comp] = Tw

    for comp, fs in by_comp.items():
        Tw = Tw_by_comp[comp]
        for f in fs:
            if len(cyc[f]) != 1:
                continue
            qrow = tuple(cyc[f][0])
            L = len(qrow)
            if L <= 5:
                continue
            if max_row_len is not None and L > max_row_len:
                continue
            d = [Tw[v] - 1 for v in qrow]
            comps = component_spans(n, adj, side, qrow)
            bank = eta / 2 - F(L * L - 25, 50)
            acc["rows"] += 1
            for I in position_sets(L, all_subsets):
                demand = sum(d[i] for i in I)
                cap = sum(c for lo, hi, c, _C in comps if any(lo <= i <= hi for i in I))
                margin = F(cap) + bank - demand
                if margin < acc["min_margin"][0]:
                    acc["min_margin"] = (
                        margin,
                        name,
                        n,
                        len(M),
                        f,
                        qrow,
                        tuple(sorted(I)),
                        demand,
                        cap,
                        bank,
                    )
                if margin < 0:
                    acc["viol"] += 1
                    if acc["first"] is None:
                        acc["first"] = {
                            "name": name,
                            "n": n,
                            "side": "".join(map(str, side)),
                            "m": len(M),
                            "eta": str(eta),
                            "f": f,
                            "row": qrow,
                            "I": tuple(sorted(I)),
                            "demand": str(demand),
                            "cap": cap,
                            "bank": str(bank),
                            "margin": str(margin),
                            "d": [str(x) for x in d],
                            "comps": comps,
                        }
                    if stop_first:
                        return


def run_gmin(
    name,
    n,
    edges,
    acc,
    max_cuts=None,
    stop_first=False,
    all_subsets=False,
    max_row_len=None,
):
    _adj, cuts = gmins(n, edges)
    if max_cuts is not None:
        cuts = cuts[:max_cuts]
    for side in cuts:
        check_cut(name, n, edges, side, acc, stop_first, all_subsets, max_row_len)
        if stop_first and acc["first"]:
            return


def cycle_blowup_side(parts):
    side = []
    for i, p in enumerate(parts):
        side.extend([i % 2] * p)
    return side


def bridge(block1, block2, u, v):
    n, edges = union_disjoint(block1, block2)
    return n, edges + [(u, block1[0] + v)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=7)
    ap.add_argument("--max-n", type=int, default=10)
    ap.add_argument("--two-lane-max", type=int, default=30)
    ap.add_argument("--direct-only", action="store_true")
    ap.add_argument("--skip-census", action="store_true")
    ap.add_argument("--fast", action="store_true")
    ap.add_argument("--stop-first", action="store_true")
    ap.add_argument("--max-cuts", type=int, default=None)
    ap.add_argument("--all-subsets", action="store_true")
    ap.add_argument("--max-row-len", type=int, default=None)
    args = ap.parse_args()

    acc = {"rows": 0, "viol": 0, "first": None, "min_margin": (F(10**18),)}

    for L in range(8, args.two_lane_max + 1, 2):
        n, edges, side, _bad = build_two_lane(L)
        check_cut(
            f"two-lane-L{L}",
            n,
            edges,
            side,
            acc,
            args.stop_first,
            args.all_subsets,
            args.max_row_len,
        )
        if args.stop_first and acc["first"]:
            break

    for Ll, k, gap in [(12, 4, 6), (14, 4, 8), (16, 5, 8), (20, 6, 10)]:
        bad = greedy_chords(Ll, k, gap)
        n, edges, side, _ = build_k_lane(Ll, k, bad)
        check_cut(
            f"klane-L{Ll}k{k}",
            n,
            edges,
            side,
            acc,
            args.stop_first,
            args.all_subsets,
            args.max_row_len,
        )
        if args.stop_first and acc["first"]:
            break

    for c in (7, 9, 11, 13, 15, 17, 19):
        n, edges = blowup([1] * c)
        check_cut(
            f"C{c}[1]",
            n,
            edges,
            cycle_blowup_side([1] * c),
            acc,
            args.stop_first,
            args.all_subsets,
            args.max_row_len,
        )
        if args.stop_first and acc["first"]:
            break

    if not args.direct_only and not (args.stop_first and acc["first"]):
        named = [
            ("Grotzsch", mycielski(5, Cn(5))),
            ("M(C7)", mycielski(7, Cn(7))),
            ("C7|Grotzsch", bridge((7, Cn(7)), mycielski(5, Cn(5)), 0, 0)),
        ]
        for nm, (n, edges) in named:
            max_cuts = args.max_cuts
            if max_cuts is None and args.fast:
                max_cuts = 2
            elif max_cuts is None:
                max_cuts = 3
            run_gmin(
                nm,
                n,
                edges,
                acc,
                max_cuts,
                args.stop_first,
                args.all_subsets,
                args.max_row_len,
            )
            if args.stop_first and acc["first"]:
                break

    if not args.direct_only and not args.skip_census and not (args.stop_first and acc["first"]):
        for nn in range(args.min_n, args.max_n + 1):
            before = acc["viol"]
            for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
                n, edges = dec(g6)
                run_gmin(
                    f"cen{g6}",
                    n,
                    edges,
                    acc,
                    max_cuts=args.max_cuts,
                    stop_first=args.stop_first,
                    all_subsets=args.all_subsets,
                    max_row_len=args.max_row_len,
                )
                if args.stop_first and acc["first"]:
                    break
            print(f"census N={nn}: rows={acc['rows']} viol+={acc['viol'] - before}", flush=True)
            if args.stop_first and acc["first"]:
                break

    print("=== BANKED-UPO unique-row gate ===")
    print("rows:", acc["rows"])
    print("violations:", acc["viol"])
    print("min_margin:", acc["min_margin"])
    print("first:", acc["first"] or "")
    print("VERDICT:", "BANKED-UPO HOLDS" if acc["viol"] == 0 else "BANKED-UPO FAILS")


if __name__ == "__main__":
    main()
