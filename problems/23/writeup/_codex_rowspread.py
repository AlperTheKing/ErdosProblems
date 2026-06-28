"""Exact row-spread diagnostics for the Gram matrix O=P^T P.

Claude verified the average row-sum bound

    (1/|M|) sum_f (O1)_f = ||S||^2 / |M| <= N.

ROWSUM-O asks for max_f (O1)_f <= N.  This script measures the remaining
average-to-maximum gap and tests simple exact spread inequalities.
"""
from __future__ import annotations

import argparse
import subprocess
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


def analyze_side(n, adj, side):
    st = struct_for_side(n, adj, list(side))
    if st is None:
        return None
    M, ell, T, mu, cyc = st
    info = {"n": n, "adj": adj, "side": list(side), "M": M, "ell": ell, "T": T, "mu": mu, "cyc": cyc}
    if not M:
        return None
    pfs, S = pfs_for(info)
    rows = []
    for f in M:
        row = sum(x * S[v] for v, x in pfs[f].items())
        self = sum(x * x for x in pfs[f].values())
        rows.append((f, row, self, F(ell[f])))
    avg = sum(r for _f, r, _s, _l in rows) / len(rows)
    mx = max(r for _f, r, _s, _l in rows)
    mn = min(r for _f, r, _s, _l in rows)
    var_num = sum((r - avg) * (r - avg) for _f, r, _s, _l in rows)
    # Candidate spreads:
    # S1: max - avg <= N - avg (tautologically equivalent to max<=N, recorded as target gap).
    # S2: max - avg <= average self-overlap slack avg(ell-self).
    avg_dilution = sum(l - s for _f, _r, s, l in rows) / len(rows)
    max_over_avg = mx - avg
    return {
        "m": len(M),
        "avg": avg,
        "max": mx,
        "min": mn,
        "target_gap": F(n) - mx,
        "avg_slack": F(n) - avg,
        "spread": max_over_avg,
        "var_num": var_num,
        "avg_dilution": avg_dilution,
        "s2_margin": avg_dilution - max_over_avg,
        "rows": rows,
    }


def graph_probe(args):
    g6, keep_rows = args
    n, edges = dec(g6)
    adj, cuts = gmins(n, edges)
    best = None
    for idx, side_s in enumerate(cuts):
        rec = analyze_side(n, adj, tuple(int(c) for c in side_s))
        if rec is None:
            continue
        rec.update({"n": n, "g6": g6, "cut_index": idx, "side": side_s})
        if not keep_rows:
            rec.pop("rows", None)
        if best is None or rec["target_gap"] < best["target_gap"]:
            best = rec
    return {"graphs": 1 if cuts else 0, "cuts": len(cuts), "best": best}


def fmt_frac(x):
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def fmt_rec(rec):
    out = {}
    for k, v in rec.items():
        if isinstance(v, F):
            out[k] = fmt_frac(v)
        elif k == "rows":
            out[k] = [(f, fmt_frac(r), fmt_frac(s), fmt_frac(l)) for f, r, s, l in v]
        else:
            out[k] = v
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, default=10)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=64)
    ap.add_argument("--keep", type=int, default=20)
    args = ap.parse_args()

    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    print(f"generated N={args.n} graphs={len(graphs)}", flush=True)
    acc = {"graphs": 0, "cuts": 0, "records": []}
    items = ((g, True) for g in graphs)
    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            iterator = ex.map(graph_probe, items, chunksize=args.chunksize)
            for i, res in enumerate(iterator, 1):
                acc["graphs"] += res["graphs"]
                acc["cuts"] += res["cuts"]
                if res["best"]:
                    acc["records"].append(res["best"])
                    acc["records"].sort(key=lambda r: r["target_gap"])
                    del acc["records"][args.keep:]
                if i % 1000 == 0:
                    print(f"processed={i} cuts={acc['cuts']} best_gap={fmt_frac(acc['records'][0]['target_gap']) if acc['records'] else None}", flush=True)
    else:
        for i, g in enumerate(graphs, 1):
            res = graph_probe((g, True))
            acc["graphs"] += res["graphs"]
            acc["cuts"] += res["cuts"]
            if res["best"]:
                acc["records"].append(res["best"])
                acc["records"].sort(key=lambda r: r["target_gap"])
                del acc["records"][args.keep:]
            if i % 1000 == 0:
                print(f"processed={i} cuts={acc['cuts']} best_gap={fmt_frac(acc['records'][0]['target_gap']) if acc['records'] else None}", flush=True)

    print("=== FINAL ===")
    print({"graphs": acc["graphs"], "cuts": acc["cuts"]})
    for rec in acc["records"]:
        print(fmt_rec(rec))


if __name__ == "__main__":
    main()
