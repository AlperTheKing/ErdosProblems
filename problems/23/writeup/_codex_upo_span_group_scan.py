"""Probe grouped span charging variants for unique-path UPO.

The component-local contained-load inequality is false, but its first failures
have several components with the same span.  This script tests grouped
versions before we try to prove any of them.
"""
from __future__ import annotations

import argparse
import subprocess
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F

from _h import GENG, dec
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _codex_upo_conditional_interval_uncross_scan import component_info


def demands_for_row(M, cyc, f, path):
    pos = {v: i for i, v in enumerate(path)}
    out = []
    for g in M:
        if g == f:
            continue
        den = len(cyc[g])
        for qpath in cyc[g]:
            hits = sorted(pos[v] for v in qpath if v in pos)
            if hits:
                out.append((hits[0], hits[-1], F(len(hits), den), g, tuple(qpath)))
    return out


def fail_record(kind, margin, g6, ci, side_s, f, path, interval, lhs, rhs, extra):
    return {
        "kind": kind,
        "margin": str(margin),
        "g6": repr(g6),
        "cut_index": ci,
        "side": side_s,
        "f": f,
        "path": path,
        "interval": interval,
        "lhs": str(lhs),
        "rhs": str(rhs),
        "extra": extra,
    }


def graph_probe(task):
    g6, variants = task
    n, edges = dec(g6)
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    _adj, cuts = gmins(n, edges)
    rows = 0
    tests = defaultdict(int)
    worst = {}
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
            infos = component_info(n, adj, side, path)
            demands = demands_for_row(M, cyc, f, path)

            cap_exact = defaultdict(F)
            cap_contained = defaultdict(F)
            cap_containing = defaultdict(F)
            for lo, hi, cap, _vs, _att in infos:
                cap_exact[(lo, hi)] += F(cap)
            L = len(path)
            for a in range(L):
                for b in range(a, L):
                    cap_contained[(a, b)] = sum(
                        F(cap) for lo, hi, cap, _vs, _att in infos if a <= lo and hi <= b
                    )
                    cap_containing[(a, b)] = sum(
                        F(cap) for lo, hi, cap, _vs, _att in infos if lo <= a and b <= hi
                    )

            if "exact_exact" in variants:
                # Variant A: demands with exact overlap [a,b] paid by components with exact same span.
                exact_load = defaultdict(F)
                for lo, hi, dem, _g, _q in demands:
                    exact_load[(lo, hi)] += dem
                for interval, lhs in exact_load.items():
                    rhs = cap_exact[interval]
                    margin = rhs - lhs
                    tests["exact_exact"] += 1
                    rec = fail_record(
                        "exact_exact", margin, g6, ci, side_s, f, path, interval, lhs, rhs,
                        {"infos": infos, "demands": [(lo, hi, str(d), g, q) for lo, hi, d, g, q in demands]},
                    )
                    if "exact_exact" not in worst or margin < worst["exact_exact"]["margin_value"]:
                        rec["margin_value"] = margin
                        worst["exact_exact"] = rec
                    if margin < 0:
                        return {"rows": rows, "tests": dict(tests), "worst": worst, "fail": rec}

            if "contained_contained" in variants:
                # Variant B: demands contained in [a,b] paid by components with span contained in [a,b].
                for a in range(L):
                    for b in range(a, L):
                        lhs = sum(dem for lo, hi, dem, _g, _q in demands if a <= lo and hi <= b)
                        if lhs == 0:
                            continue
                        rhs = cap_contained[(a, b)]
                        margin = rhs - lhs
                        tests["contained_contained"] += 1
                        rec = fail_record(
                            "contained_contained", margin, g6, ci, side_s, f, path, (a, b), lhs, rhs,
                            {"infos": infos, "demands": [(lo, hi, str(d), g, q) for lo, hi, d, g, q in demands]},
                        )
                        if "contained_contained" not in worst or margin < worst["contained_contained"]["margin_value"]:
                            rec["margin_value"] = margin
                            worst["contained_contained"] = rec
                        if margin < 0:
                            return {"rows": rows, "tests": dict(tests), "worst": worst, "fail": rec}

            if "contained_containing" in variants:
                # Variant C: demands contained in [a,b] paid by components whose span contains [a,b].
                for a in range(L):
                    for b in range(a, L):
                        lhs = sum(dem for lo, hi, dem, _g, _q in demands if a <= lo and hi <= b)
                        if lhs == 0:
                            continue
                        rhs = cap_containing[(a, b)]
                        margin = rhs - lhs
                        tests["contained_containing"] += 1
                        rec = fail_record(
                            "contained_containing", margin, g6, ci, side_s, f, path, (a, b), lhs, rhs,
                            {"infos": infos, "demands": [(lo, hi, str(d), g, q) for lo, hi, d, g, q in demands]},
                        )
                        if "contained_containing" not in worst or margin < worst["contained_containing"]["margin_value"]:
                            rec["margin_value"] = margin
                            worst["contained_containing"] = rec
                        if margin < 0:
                            return {"rows": rows, "tests": dict(tests), "worst": worst, "fail": rec}
    clean_worst = {}
    for k, rec in worst.items():
        rec = dict(rec)
        rec["margin_value"] = str(rec["margin_value"])
        clean_worst[k] = rec
    return {"rows": rows, "tests": dict(tests), "worst": clean_worst, "fail": None}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=64)
    ap.add_argument(
        "--variant",
        action="append",
        choices=["exact_exact", "contained_contained", "contained_containing"],
        help="Variant to test; may be repeated. Defaults to all variants.",
    )
    args = ap.parse_args()
    variants = set(args.variant or ["exact_exact", "contained_contained", "contained_containing"])
    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    rows = 0
    tests = defaultdict(int)
    fail = None
    worst = {}
    iterator = graphs
    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            iterator = ex.map(graph_probe, ((g6, variants) for g6 in graphs), chunksize=args.chunksize)
            for res in iterator:
                rows += res["rows"]
                for k, v in res["tests"].items():
                    tests[k] += v
                for k, rec in res["worst"].items():
                    margin = F(rec["margin_value"])
                    if k not in worst or margin < F(worst[k]["margin_value"]):
                        worst[k] = rec
                if res["fail"] is not None:
                    fail = res["fail"]
                    break
    else:
        for g6 in iterator:
            res = graph_probe((g6, variants))
            rows += res["rows"]
            for k, v in res["tests"].items():
                tests[k] += v
            for k, rec in res["worst"].items():
                margin = F(rec["margin_value"])
                if k not in worst or margin < F(worst[k]["margin_value"]):
                    worst[k] = rec
            if res["fail"] is not None:
                fail = res["fail"]
                break
    print("N", args.n, "rows", rows, "tests", dict(tests))
    print("worst", worst)
    print("fail", fail)


if __name__ == "__main__":
    main()
