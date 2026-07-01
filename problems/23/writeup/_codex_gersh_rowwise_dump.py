"""Dump the worst ROWWISE-GERSH row for a specific graph6 string."""

import argparse
from fractions import Fraction as F

from _h import dec, Bconn
from _satzmu_conn import kcomponents, struct_for_side
from _stark1 import gmins


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("g6")
    args = ap.parse_args()
    n, edges = dec(args.g6)
    adj, cuts = gmins(n, edges)
    best = None
    for side in cuts:
        if not Bconn(n, adj, side):
            continue
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, ell, T, _mu, cyc = st
        if not M:
            continue
        A = F(n) + F(n * n, 25) - len(M)
        _comp_map, find = kcomponents(n, cyc)
        edges_by_comp = {}
        for f in M:
            edges_by_comp.setdefault(find(cyc[f][0][0]), []).append(f)
        for comp, fs in edges_by_comp.items():
            tw = [F(0) for _ in range(n)]
            counts_by_edge = {}
            for g in fs:
                denom = F(len(cyc[g]))
                counts = {}
                for path in cyc[g]:
                    for v in path:
                        counts[v] = counts.get(v, 0) + 1
                counts_by_edge[g] = counts
                for v, c in counts.items():
                    tw[v] += F(c, 1) / denom
            for f in fs:
                for path in cyc[f]:
                    val = sum(tw[v] for v in path)
                    margin = A - val
                    rec = (margin, val, side, M, ell, T, cyc, comp, fs, tw, f, tuple(path), counts_by_edge)
                    if best is None or margin < best[0]:
                        best = rec
    if best is None:
        print("no connected-B bad-edge cut found")
        return
    margin, val, side, M, ell, T, cyc, comp, fs, tw, f, path, counts_by_edge = best
    print("g6:", args.g6)
    print("N:", n, "edges:", len(edges), "maxcuts:", len(cuts))
    print("side:", "".join(map(str, side)))
    print("|M|:", len(M), "A:", A)
    print("bad edges:", sorted(M))
    print("ell:", {e: ell[e] for e in sorted(M)})
    print("component:", comp, "component bad edges:", sorted(fs))
    print("worst f:", f, "row:", path)
    print("row value:", val, "margin:", margin)
    print("T:", [str(T[v]) for v in range(n)])
    print("Tw_C:", [str(tw[v]) for v in range(n)])
    print("row Tw terms:", [(v, str(tw[v])) for v in path])
    print("cyc sizes:", {e: len(cyc[e]) for e in sorted(fs)})
    print("counts on worst row component edges:")
    for g in sorted(fs):
        print(" ", g, {v: counts_by_edge[g].get(v, 0) for v in path if counts_by_edge[g].get(v, 0)})


if __name__ == "__main__":
    main()
