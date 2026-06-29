"""Test unique-contributor / fan-contributor split for interval Hall.

For a unique row f and target interval I, split demand from g != f into:
  U(I): geodesics of bad edges g with len(cyc[g]) == 1
  F(I): geodesics of bad edges g with len(cyc[g]) > 1

Candidate variants:
  A. U(I) <= base(I), where base is sum active span lengths.
  B. max(0, U(I)+F(I)-base(I)) <= surplus(I), already known.
  C. max(0, F(I)-(base(I)-U(I))) <= surplus(I), same as B if A holds.

The main new check is A; if true, all overrun is fan-originated after unique
paths consume base.
"""
from __future__ import annotations

import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F

from _h import GENG, dec
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _codex_upo_conditional_interval_uncross_scan import component_info


def graph_probe(g6: str):
    n, edges = dec(g6)
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    _adj, cuts = gmins(n, edges)
    rows = intervals = 0
    worst_unique = None
    worst_fan = None
    for ci, side_s in enumerate(cuts):
        side = [int(c) for c in side_s]
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, _ell, _T, _mu, cyc = st
        for f in M:
            if len(cyc[f]) != 1:
                continue
            rows += 1
            path = cyc[f][0]
            pos = {v: i for i, v in enumerate(path)}
            infos = component_info(n, adj, side, path)
            L = len(path)
            for a in range(L):
                for b in range(a, L):
                    uload = F(0)
                    fanload = F(0)
                    contributors = []
                    for g in M:
                        if g == f:
                            continue
                        den = len(cyc[g])
                        for qpath in cyc[g]:
                            hits = [pos[v] for v in qpath if v in pos and a <= pos[v] <= b]
                            if not hits:
                                continue
                            dem = F(len(hits), den)
                            contributors.append((g, len(cyc[g]), tuple(qpath), tuple(hits), dem))
                            if len(cyc[g]) == 1:
                                uload += dem
                            else:
                                fanload += dem
                    if not contributors:
                        continue
                    intervals += 1
                    active = [info for info in infos if not (info[1] < a or b < info[0])]
                    base = sum(F(hi - lo + 1) for lo, hi, _cap, _vs, _att in active)
                    surplus = sum(F(cap - (hi - lo + 1)) for lo, hi, cap, _vs, _att in active)
                    umargin = base - uload
                    urec = (umargin, repr(g6), ci, side_s, f, path, (a, b), str(uload), str(base), active, contributors)
                    if worst_unique is None or umargin < worst_unique[0]:
                        worst_unique = urec
                    if umargin < 0:
                        return {"rows": rows, "intervals": intervals, "worst_unique": worst_unique, "worst_fan": worst_fan, "fail": ("unique_base", urec)}
                    fover = fanload - umargin
                    fmargin = surplus - fover
                    frec = (fmargin, repr(g6), ci, side_s, f, path, (a, b), str(fanload), str(umargin), str(surplus), active, contributors)
                    if worst_fan is None or fmargin < worst_fan[0]:
                        worst_fan = frec
                    if fover > surplus:
                        return {"rows": rows, "intervals": intervals, "worst_unique": worst_unique, "worst_fan": worst_fan, "fail": ("fan_surplus", frec)}
    return {"rows": rows, "intervals": intervals, "worst_unique": worst_unique, "worst_fan": worst_fan, "fail": None}


def clean(rec):
    if rec is None:
        return None
    out = []
    for x in rec:
        if isinstance(x, F):
            out.append(str(x))
        else:
            out.append(x)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=64)
    args = ap.parse_args()
    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    rows = intervals = 0
    worst_unique = worst_fan = fail = None
    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            for res in ex.map(graph_probe, graphs, chunksize=args.chunksize):
                rows += res["rows"]
                intervals += res["intervals"]
                if res["worst_unique"] and (worst_unique is None or res["worst_unique"][0] < worst_unique[0]):
                    worst_unique = res["worst_unique"]
                if res["worst_fan"] and (worst_fan is None or res["worst_fan"][0] < worst_fan[0]):
                    worst_fan = res["worst_fan"]
                if res["fail"] is not None:
                    fail = res["fail"]
                    break
    else:
        for g6 in graphs:
            res = graph_probe(g6)
            rows += res["rows"]
            intervals += res["intervals"]
            if res["worst_unique"] and (worst_unique is None or res["worst_unique"][0] < worst_unique[0]):
                worst_unique = res["worst_unique"]
            if res["worst_fan"] and (worst_fan is None or res["worst_fan"][0] < worst_fan[0]):
                worst_fan = res["worst_fan"]
            if res["fail"] is not None:
                fail = res["fail"]
                break
    print("N", args.n, "rows", rows, "intervals", intervals)
    print("worst_unique", clean(worst_unique))
    print("worst_fan", clean(worst_fan))
    print("fail", fail if fail is None else (fail[0], clean(fail[1])))


if __name__ == "__main__":
    main()
