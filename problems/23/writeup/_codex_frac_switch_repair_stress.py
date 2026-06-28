"""Detailed stress test for selected fractional-SPLIT repair patterns.

Checks Claude's current local-descent crux:
  (a) whether any SPLIT-bad row has ell > 5,
  (b) whether any SPLIT-bad cut needs Hamming repair radius > 2 inside the
      gamma-min connected-B max-cut family,
  (c) whether a SPLIT-bad row breaks the endpoint d_same=1 pattern.

All arithmetic in split rows uses Fraction.
"""
from __future__ import annotations

import argparse
import itertools
import subprocess
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F

from _frac_selected_gate import frac_ok_cut
from _h import GENG, dec
from _satzmu_conn import struct_for_side
from _stark1 import gmins


def flip(side: tuple[int, ...], vertices: tuple[int, ...]) -> tuple[int, ...]:
    out = list(side)
    for v in vertices:
        out[v] = 1 - out[v]
    return tuple(out)


def split_bad_rows(n: int, adj, side: tuple[int, ...]):
    st = struct_for_side(n, adj, list(side))
    if st is None:
        return []
    M, ell, _T, _mu, cyc = st
    S = [F(0) for _ in range(n)]
    pf = {}
    for g in M:
        paths = cyc[g]
        d = {}
        for path in paths:
            for v in path:
                d[v] = d.get(v, F(0)) + F(1, len(paths))
        pf[g] = d
        for v, x in d.items():
            S[v] += x

    rows = []
    for f in sorted(M):
        L = ell[f]
        layer = {}
        for path in cyc[f]:
            for i, v in enumerate(path):
                layer[v] = i
        A = [F(0) for _ in range(L)]
        for v, x in pf[f].items():
            A[layer[v]] += x * S[v]
        R = sum(A) - n
        bvals = []
        for t in range(1, L // 2 + 1):
            outer = sum(A[:t]) + sum(A[L - t :])
            bvals.append(outer - F(2 * t * n, L))
        if R > 0 or min(bvals) > 0 or max(bvals) < R:
            rows.append((f, L, tuple(A), R, tuple(bvals), len(cyc[f])))
    return rows


def endpoint_bad_degrees(adj, side: tuple[int, ...], f):
    ans = []
    for v in f:
        d_same = sum(1 for u in adj[v] if side[u] == side[v])
        d_cross = sum(1 for u in adj[v] if side[u] != side[v])
        ans.append((v, d_same, d_cross))
    return tuple(ans)


def min_good_radius(n: int, sides, side: tuple[int, ...], good):
    side_set = set(sides)
    if any(good):
        # Exact minimum in the enumerated gamma-min family, for diagnostics.
        min_ham = min(
            sum(a != b for a, b in zip(side, target))
            for target, ok in zip(sides, good)
            if ok
        )
    else:
        min_ham = None

    for radius in (1, 2):
        for vertices in itertools.combinations(range(n), radius):
            target = flip(side, vertices)
            if target in side_set:
                idx = sides.index(target)
                if good[idx]:
                    return radius, vertices, min_ham
    return None, None, min_ham


def graph_probe(g6: str):
    n, edges = dec(g6)
    adj, cuts = gmins(n, edges)
    if not cuts:
        return {
            "graphs": 0,
            "cuts": 0,
            "no_good_graphs": 0,
            "bad_cuts": 0,
            "bad_rows": 0,
            "ell_gt5": 0,
            "endpoint_pattern_fail": 0,
            "radius_gt2": 0,
            "max_min_ham": 0,
            "min_ham_hist": {},
            "category_witnesses": {},
            "witnesses": [],
        }
    sides = [tuple(int(x) for x in s) for s in cuts]
    good = [bool(frac_ok_cut(n, adj, list(s))) for s in sides]
    has_good = any(good)
    witnesses = []
    bad_cuts = bad_rows = ell_gt5 = endpoint_fail = radius_gt2 = 0
    category_witnesses = {}
    min_ham_hist = Counter()
    max_min_ham = 0

    for side, ok in zip(sides, good):
        if ok:
            continue
        rows = split_bad_rows(n, adj, side)
        if not rows:
            continue
        bad_cuts += 1
        radius, repair, min_ham = min_good_radius(n, sides, side, good)
        min_ham_key = "none" if min_ham is None else str(min_ham)
        min_ham_hist[min_ham_key] += 1
        if min_ham is not None:
            max_min_ham = max(max_min_ham, min_ham)
        if radius is None or radius > 2:
            radius_gt2 += 1
            category_witnesses.setdefault(
                "radius_gt2",
                {
                    "g6": g6,
                    "side": "".join(map(str, side)),
                    "radius": radius,
                    "repair": repair,
                    "min_ham": min_ham,
                    "rows": [],
                },
            )
        for f, L, A, R, bvals, path_count in rows:
            bad_rows += 1
            degrees = endpoint_bad_degrees(adj, side, f)
            pattern_ok = all(d_same == 1 for _v, d_same, _d_cross in degrees)
            if L > 5:
                ell_gt5 += 1
                category_witnesses.setdefault(
                    "ell_gt5",
                    {
                        "g6": g6,
                        "side": "".join(map(str, side)),
                        "f": f,
                        "L": L,
                        "A": tuple(str(x) for x in A),
                        "R": str(R),
                        "B": tuple(str(x) for x in bvals),
                        "path_count": path_count,
                        "degrees": degrees,
                        "radius": radius,
                        "repair": repair,
                        "min_ham": min_ham,
                    },
                )
            if not pattern_ok:
                endpoint_fail += 1
                category_witnesses.setdefault(
                    "endpoint_pattern_fail",
                    {
                        "g6": g6,
                        "side": "".join(map(str, side)),
                        "f": f,
                        "L": L,
                        "A": tuple(str(x) for x in A),
                        "R": str(R),
                        "B": tuple(str(x) for x in bvals),
                        "path_count": path_count,
                        "degrees": degrees,
                        "radius": radius,
                        "repair": repair,
                        "min_ham": min_ham,
                    },
                )
            if radius is None or radius > 2:
                category_witnesses["radius_gt2"]["rows"].append(
                    {
                        "f": f,
                        "L": L,
                        "A": tuple(str(x) for x in A),
                        "R": str(R),
                        "B": tuple(str(x) for x in bvals),
                        "path_count": path_count,
                        "degrees": degrees,
                    }
                )
            if L > 5 or not pattern_ok or radius is None or radius > 2 or len(witnesses) < 5:
                witnesses.append(
                    {
                        "g6": g6,
                        "side": "".join(map(str, side)),
                        "f": f,
                        "L": L,
                        "A": tuple(str(x) for x in A),
                        "R": str(R),
                        "B": tuple(str(x) for x in bvals),
                        "path_count": path_count,
                        "degrees": degrees,
                        "radius": radius,
                        "repair": repair,
                        "min_ham": min_ham,
                    }
                )

    return {
        "graphs": 1,
        "cuts": len(sides),
        "no_good_graphs": 0 if has_good else 1,
        "bad_cuts": bad_cuts,
        "bad_rows": bad_rows,
        "ell_gt5": ell_gt5,
        "endpoint_pattern_fail": endpoint_fail,
        "radius_gt2": radius_gt2,
        "max_min_ham": max_min_ham,
        "min_ham_hist": dict(min_ham_hist),
        "category_witnesses": category_witnesses,
        "witnesses": witnesses[:10],
    }


def merge(acc, res):
    for key in (
        "graphs",
        "cuts",
        "no_good_graphs",
        "bad_cuts",
        "bad_rows",
        "ell_gt5",
        "endpoint_pattern_fail",
        "radius_gt2",
    ):
        acc[key] += res[key]
    acc["max_min_ham"] = max(acc["max_min_ham"], res["max_min_ham"])
    for key, value in res["min_ham_hist"].items():
        acc["min_ham_hist"][key] = acc["min_ham_hist"].get(key, 0) + value
    for key, value in res["category_witnesses"].items():
        acc["category_witnesses"].setdefault(key, value)
    room = 20 - len(acc["witnesses"])
    if room > 0:
        acc["witnesses"].extend(res["witnesses"][:room])


def compact(acc):
    return {
        "graphs": acc["graphs"],
        "cuts": acc["cuts"],
        "bad_cuts": acc["bad_cuts"],
        "bad_rows": acc["bad_rows"],
        "ell_gt5": acc["ell_gt5"],
        "endpoint_pattern_fail": acc["endpoint_pattern_fail"],
        "radius_gt2": acc["radius_gt2"],
        "no_good_graphs": acc["no_good_graphs"],
        "max_min_ham": acc["max_min_ham"],
        "min_ham_hist": acc["min_ham_hist"],
        "category_witness_keys": sorted(acc["category_witnesses"]),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, default=12)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=64)
    args = ap.parse_args()

    out = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    print(f"generated N={args.n} graphs={len(out)}", flush=True)
    acc = {
        "graphs": 0,
        "cuts": 0,
        "bad_cuts": 0,
        "bad_rows": 0,
        "ell_gt5": 0,
        "endpoint_pattern_fail": 0,
        "radius_gt2": 0,
        "no_good_graphs": 0,
        "max_min_ham": 0,
        "min_ham_hist": {},
        "category_witnesses": {},
        "witnesses": [],
    }

    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            for i, res in enumerate(ex.map(graph_probe, out, chunksize=args.chunksize), 1):
                merge(acc, res)
                if i % 50000 == 0:
                    print(f"processed={i} acc={compact(acc)}", flush=True)
    else:
        for i, g6 in enumerate(out, 1):
            merge(acc, graph_probe(g6))
            if i % 50000 == 0:
                print(f"processed={i} acc={compact(acc)}", flush=True)

    print("=== FINAL ===")
    print(acc)


if __name__ == "__main__":
    main()
