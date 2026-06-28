"""Float landscape for the LPD dual maximum on small census instances.

For each gamma-min connected-B max cut, solve the normalized LPD dual

    max sum_f (sum_i sqrt(w[f,i]))^2,  sum_v y_v=1, y>=0.

This is not an acceptance gate.  It identifies near-tight KKT cores and their
support patterns so we can formulate exact-testable structural lemmas.
"""
from __future__ import annotations

import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor

from _codex_lpd_dual_probe import info_for_side, optimize
from _h import GENG, dec
from _stark1 import gmins


def graph_probe(args):
    g6, starts = args
    n, edges = dec(g6)
    adj, cuts = gmins(n, edges)
    if not cuts:
        return {"graphs": 0, "cuts": 0, "best": None}
    best = None
    for idx, side_s in enumerate(cuts):
        info = info_for_side(n, adj, tuple(int(c) for c in side_s))
        val, y, success, _msg = optimize(info, starts=starts, seed=idx + 17)
        support = tuple(i for i, a in enumerate(y) if a > 1e-7)
        gap = n - val
        rec = {
            "gap": gap,
            "val": val,
            "n": n,
            "g6": g6,
            "cut_index": idx,
            "side": side_s,
            "support": support,
            "support_size": len(support),
            "success": success,
            "M": tuple(info["M"]),
            "T_support": tuple(str(info["T"][i]) for i in support),
        }
        if best is None or rec["gap"] < best["gap"]:
            best = rec
    return {"graphs": 1, "cuts": len(cuts), "best": best}


def merge(acc, res, keep):
    acc["graphs"] += res["graphs"]
    acc["cuts"] += res["cuts"]
    if res["best"] is None:
        return
    acc["records"].append(res["best"])
    acc["records"].sort(key=lambda r: r["gap"])
    del acc["records"][keep:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, default=10)
    ap.add_argument("--starts", type=int, default=12)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=32)
    ap.add_argument("--keep", type=int, default=20)
    args = ap.parse_args()

    out = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    print(f"generated N={args.n} graphs={len(out)} starts={args.starts}", flush=True)
    acc = {"graphs": 0, "cuts": 0, "records": []}
    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            items = ((g, args.starts) for g in out)
            for i, res in enumerate(ex.map(graph_probe, items, chunksize=args.chunksize), 1):
                merge(acc, res, args.keep)
                if i % 1000 == 0:
                    print(f"processed={i} graphs={acc['graphs']} cuts={acc['cuts']} best_gap={acc['records'][0]['gap'] if acc['records'] else None}", flush=True)
    else:
        for i, g6 in enumerate(out, 1):
            merge(acc, graph_probe((g6, args.starts)), args.keep)
            if i % 1000 == 0:
                print(f"processed={i} graphs={acc['graphs']} cuts={acc['cuts']} best_gap={acc['records'][0]['gap'] if acc['records'] else None}", flush=True)

    print("=== FINAL ===")
    print({"graphs": acc["graphs"], "cuts": acc["cuts"]})
    for rec in acc["records"]:
        print(rec)


if __name__ == "__main__":
    main()
