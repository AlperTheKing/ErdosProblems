"""Catalog exact ROWSUM(f)=N rows.

The average-to-max attempts showed that equality rows are not only uniform
odd-blowup rows.  This script groups equality rows by exact row geometry.
"""
from __future__ import annotations

import argparse
import subprocess
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F

from _h import GENG, dec
from _stark1 import gmins
from _satzmu_conn import struct_for_side


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
        pf = {v: F(c, den) for v, c in cnt.items()}
        pfs[f] = pf
        for v, x in pf.items():
            S[v] += x
    return pfs, S


def fmt(x):
    if isinstance(x, F):
        return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"
    if isinstance(x, tuple):
        return "(" + ",".join(fmt(y) for y in x) + ")"
    return str(x)


def frac_key(x):
    return (x.numerator, x.denominator)


def graph_probe(g6):
    n, edges = dec(g6)
    adj, cuts = gmins(n, edges)
    sigs = Counter()
    examples = {}
    eq_count = 0
    rows = 0
    for ci, side_s in enumerate(cuts):
        side = [int(c) for c in side_s]
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, ell, T, mu, cyc = st
        if not M:
            continue
        pfs, S = pfs_for({"n": n, "M": M, "cyc": cyc})
        for f in M:
            rows += 1
            pf = pfs[f]
            row = sum(x * S[v] for v, x in pf.items())
            if row != n:
                continue
            eq_count += 1
            support = tuple(sorted(pf))
            unique = len(cyc[f]) == 1
            self = sum(x * x for x in pf.values())
            row_parts = []
            for g in M:
                inter = sum(pf.get(v, F(0)) * pfs[g].get(v, F(0)) for v in support)
                if inter:
                    row_parts.append(inter)
            row_parts_sig = tuple(sorted((frac_key(x) for x in row_parts), reverse=True))
            weighted_loads = tuple(sorted((frac_key(pf[v]), frac_key(S[v])) for v in support))
            sig = (
                ell[f],
                len(M),
                len(cyc[f]),
                len(support),
                frac_key(self),
                row_parts_sig,
                weighted_loads,
            )
            sigs[sig] += 1
            examples.setdefault(sig, (g6, ci, side_s, f, cyc[f], [S[v] for v in support]))
    return {"graphs": 1 if cuts else 0, "cuts": len(cuts), "rows": rows, "eq": eq_count, "sigs": sigs, "examples": examples}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=64)
    ap.add_argument("--keep", type=int, default=30)
    args = ap.parse_args()

    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    total = {"graphs": 0, "cuts": 0, "rows": 0, "eq": 0}
    sigs = Counter()
    examples = {}
    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            iterator = ex.map(graph_probe, graphs, chunksize=args.chunksize)
            for i, res in enumerate(iterator, 1):
                for k in total:
                    total[k] += res[k]
                sigs.update(res["sigs"])
                for sig, exa in res["examples"].items():
                    examples.setdefault(sig, exa)
                if i % 10000 == 0:
                    print("processed", i, "eq", total["eq"], "sigs", len(sigs), flush=True)
    else:
        for i, g in enumerate(graphs, 1):
            res = graph_probe(g)
            for k in total:
                total[k] += res[k]
            sigs.update(res["sigs"])
            for sig, exa in res["examples"].items():
                examples.setdefault(sig, exa)

    print("N", args.n, total, "signature_count", len(sigs))
    for sig, count in sigs.most_common(args.keep):
        ell, m, path_count, supp_size, self_key, parts, weighted_loads = sig
        exa = examples[sig]
        print("SIG count", count, "ell", ell, "m", m, "paths", path_count, "supp", supp_size, "self", fmt(F(*self_key)))
        print(" parts", [fmt(F(*x)) for x in parts])
        print(" weighted_loads", [(fmt(F(*p)), fmt(F(*s))) for p, s in weighted_loads])
        print(" ex", exa[0], "cut", exa[1], "side", exa[2], "f", exa[3], "paths", exa[4], "S_support", [fmt(x) for x in exa[5]])


if __name__ == "__main__":
    main()
