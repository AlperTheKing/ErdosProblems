"""Graph-sharded census gate for row-union eta-or-unit split.

This reuses _codex_slack_cage_rowunion_unit_gate.py, but runs over graph6
census graphs with multiprocessing and quiet per-side output.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import multiprocessing as mp
import subprocess
from fractions import Fraction as F

with contextlib.redirect_stdout(io.StringIO()):
    from _h import GENG, dec
    from _stark1 import gmins
    from _codex_slack_cage_rowunion_unit_gate import check_side, fmt_frac


def empty_acc():
    return {
        "graphs": 0,
        "cuts": 0,
        "candidates": 0,
        "positive": 0,
        "eta_paid": 0,
        "unit_eta_paid": 0,
        "nonunit_eta_paid": 0,
        "fails": 0,
        "first_fail": None,
        "first_nonunit_eta_paid": None,
        "min_margin": (F(10**18),),
    }


def merge_acc(dst, src):
    for key in (
        "graphs",
        "cuts",
        "candidates",
        "positive",
        "eta_paid",
        "unit_eta_paid",
        "nonunit_eta_paid",
        "fails",
    ):
        dst[key] += src[key]
    if src["first_fail"] is not None and dst["first_fail"] is None:
        dst["first_fail"] = src["first_fail"]
    if src["first_nonunit_eta_paid"] is not None and dst["first_nonunit_eta_paid"] is None:
        dst["first_nonunit_eta_paid"] = src["first_nonunit_eta_paid"]
    if src["min_margin"][0] < dst["min_margin"][0]:
        dst["min_margin"] = src["min_margin"]


def worker(payload):
    g6, max_cuts, max_candidates, max_union_rows = payload
    n, edges = dec(g6)
    acc = empty_acc()
    acc["graphs"] = 1
    _adj, cuts = gmins(n, edges)
    for idx, side in enumerate(cuts[:max_cuts]):
        before = dict(acc)
        check_side(
            f"cen{g6}#cut{idx}",
            n,
            edges,
            side,
            max_candidates,
            max_union_rows,
            acc,
            verbose=False,
        )
        if acc["candidates"] != before["candidates"] or acc["positive"] != before["positive"]:
            acc["cuts"] += 1
        if acc["first_fail"] is not None:
            break
    return acc


def fmt_min_margin(mm):
    if mm[0] == F(10**18):
        return ""
    margin, name, n, m, Q, U, pre, eta = mm
    return {
        "margin": fmt_frac(margin),
        "name": name,
        "n": n,
        "m": m,
        "Q": Q,
        "U": U,
        "pre": fmt_frac(pre),
        "eta": fmt_frac(eta),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--workers", type=int, default=64)
    ap.add_argument("--chunksize", type=int, default=8)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--max-cuts", type=int, default=8)
    ap.add_argument("--max-candidates", type=int, default=None)
    ap.add_argument("--max-union-rows", type=int, default=2)
    ap.add_argument("--stop-first", action="store_true")
    args = ap.parse_args()

    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    if args.limit is not None:
        graphs = graphs[: args.limit]

    total = empty_acc()
    payloads = [(g6, args.max_cuts, args.max_candidates, args.max_union_rows) for g6 in graphs]
    done = 0
    with mp.Pool(processes=args.workers) as pool:
        for acc in pool.imap_unordered(worker, payloads, chunksize=args.chunksize):
            done += acc["graphs"]
            merge_acc(total, acc)
            if done % 1000 == 0 or done == len(graphs):
                print(
                    f"progress graphs={done}/{len(graphs)} candidates={total['candidates']} "
                    f"positive={total['positive']} fails={total['fails']}",
                    flush=True,
                )
            if args.stop_first and total["first_fail"] is not None:
                pool.terminate()
                break

    print("=== census row-union eta-or-unit gate ===")
    print("n:", args.n)
    print("graphs:", total["graphs"])
    print("cuts:", total["cuts"])
    print("candidates:", total["candidates"])
    print("positive:", total["positive"])
    print("eta_paid:", total["eta_paid"])
    print("unit_eta_paid:", total["unit_eta_paid"])
    print("nonunit_eta_paid:", total["nonunit_eta_paid"])
    print("fails:", total["fails"])
    print("min_margin:", fmt_min_margin(total["min_margin"]))
    print("first_nonunit_eta_paid:", total["first_nonunit_eta_paid"] or "")
    print("first_fail:", total["first_fail"] or "")
    print("VERDICT:", "PASS_CENSUS_ROWUNION_ETA_OR_UNIT" if total["fails"] == 0 else "FAIL_CENSUS_ROWUNION_ETA_OR_UNIT")


if __name__ == "__main__":
    main()
