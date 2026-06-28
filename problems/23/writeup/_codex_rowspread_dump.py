"""Dump exact ROWSUM-O row-spread data for one graph/cut."""
from __future__ import annotations

import argparse
from fractions import Fraction as F

from _h import dec
from _stark1 import gmins
from _satzmu_conn import struct_for_side


def fmt(x):
    if isinstance(x, F):
        return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"
    return str(x)


def pfs_for(info):
    pfs = {}
    S = [F(0) for _ in range(info["n"])]
    for f in info["M"]:
        paths = info["cyc"][f]
        den = len(paths)
        cnt = {}
        for path in paths:
            for v in path:
                cnt[v] = cnt.get(v, 0) + 1
        pf = {v: F(c, den) for v, c in sorted(cnt.items())}
        pfs[f] = pf
        for v, x in pf.items():
            S[v] += x
    return pfs, S


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("g6")
    ap.add_argument("--cut-index", type=int, default=None)
    ap.add_argument("--side", default=None)
    args = ap.parse_args()

    n, edges = dec(args.g6)
    adj, cuts = gmins(n, edges)
    if args.side is not None:
        side = [int(c) for c in args.side]
        cut_index = None
    else:
        if args.cut_index is None:
            raise SystemExit("pass --cut-index or --side")
        side = [int(c) for c in cuts[args.cut_index]]
        cut_index = args.cut_index

    st = struct_for_side(n, adj, side)
    if st is None:
        raise SystemExit("side is not a connected-B max-cut structure")
    M, ell, T, mu, cyc = st
    info = {"n": n, "adj": adj, "side": side, "M": M, "ell": ell, "T": T, "mu": mu, "cyc": cyc}
    pfs, S = pfs_for(info)

    rows = []
    for f in M:
        row = sum(x * S[v] for v, x in pfs[f].items())
        self = sum(x * x for x in pfs[f].values())
        rows.append((f, row, self, F(ell[f])))
    avg = sum(r for _f, r, _s, _l in rows) / len(rows)

    print("g6", args.g6)
    print("n", n)
    print("cut_index", cut_index)
    print("side", "".join(map(str, side)))
    print("edges", sorted(tuple(sorted(e)) for e in edges))
    print("bad_edges", sorted(M))
    print("T", [fmt(x) for x in T])
    print("S", [fmt(x) for x in S])
    print("avg_row", fmt(avg), "N-avg", fmt(F(n) - avg))
    print("rows:")
    for f, row, self, length in sorted(rows, key=lambda r: (-r[1], r[0])):
        pf = pfs[f]
        print(
            " row",
            f,
            "ell",
            fmt(length),
            "rowsum",
            fmt(row),
            "gap",
            fmt(F(n) - row),
            "spread",
            fmt(row - avg),
            "self",
            fmt(self),
            "dilution",
            fmt(length - self),
        )
        print("  pf", [(v, fmt(x)) for v, x in pf.items()])
        print("  pS", [(v, fmt(x * S[v])) for v, x in pf.items()])
        print("  paths", cyc[f])
    print("O:")
    for f in M:
        vals = []
        for g in M:
            vals.append(sum(pfs[f].get(v, F(0)) * pfs[g].get(v, F(0)) for v in range(n)))
        print(f, [fmt(x) for x in vals])


if __name__ == "__main__":
    main()
