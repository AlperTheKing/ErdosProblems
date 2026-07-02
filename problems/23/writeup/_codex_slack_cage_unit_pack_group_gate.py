"""Group UNIT-FLAT5 row-union atoms by graph/cut and test UNIT-PACK.

This is a stress/falsifier for the proposed global bank statement:

    |M| + (# selected UNIT-FLAT5 atoms) <= N^2/25.

It deliberately starts with a naive graph/cut-level unique atom count.  A unit
atom is keyed by its two counted row paths, so the same two-row overlap is not
counted twice for the two choices of Q.  If this overcounts and fails, the
proof needs a more restrictive laminar/terminal selected family.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import multiprocessing as mp
import subprocess
from collections import Counter
from fractions import Fraction as F

with contextlib.redirect_stdout(io.StringIO()):
    from _h import GENG, dec
    from _stark1 import gmins
    from _codex_slack_cage_rowunion_unit_gate import (
        candidate_unions_for_Q,
        unit_flat5_signature,
        fmt_frac,
    )
    from _codex_slack_cage_prebank_classifier import subset_tw
    from _codex_slack_cage_switch_gate import build_data, counted_rows, sigma_of


def atom_key(rows):
    return tuple(sorted(tuple(P) for _g, P, _pset in rows))


def empty_acc():
    return {
        "graphs": 0,
        "cuts": 0,
        "candidates": 0,
        "positive": 0,
        "unit_cases": 0,
        "nonunit_positive": 0,
        "fails": 0,
        "first_fail": None,
        "first_nonunit": None,
        "max_atoms": None,
        "min_margin": None,
        "atom_count_hist": Counter(),
    }


def merge_acc(dst, src):
    for key in ("graphs", "cuts", "candidates", "positive", "unit_cases", "nonunit_positive", "fails"):
        dst[key] += src[key]
    dst["atom_count_hist"].update(src["atom_count_hist"])
    for key in ("first_fail", "first_nonunit"):
        if dst[key] is None and src[key] is not None:
            dst[key] = src[key]
    if src["max_atoms"] is not None and (dst["max_atoms"] is None or src["max_atoms"]["atoms"] > dst["max_atoms"]["atoms"]):
        dst["max_atoms"] = src["max_atoms"]
    if src["min_margin"] is not None and (
        dst["min_margin"] is None or src["min_margin"]["margin"] < dst["min_margin"]["margin"]
    ):
        dst["min_margin"] = src["min_margin"]


def check_side(name, n, edges, side, max_union_rows):
    acc = empty_acc()
    data = build_data(n, edges, [int(c) for c in side])
    if data is None:
        return acc
    E, B, M, Mset, cyc = data
    if not M:
        return acc
    acc["cuts"] = 1
    eta = F(n * n, 25) - len(M)
    all_rows = [(g, tuple(P), frozenset(P)) for g in M for P in cyc[g]]
    atoms = set()
    seen_cases = set()
    for f in M:
        for Q in cyc[f]:
            Q = tuple(Q)
            for U in candidate_unions_for_Q(all_rows, Q, max_union_rows):
                if not U or len(U) == n:
                    continue
                case_key = (Q, tuple(sorted(U)))
                if case_key in seen_cases:
                    continue
                seen_cases.add(case_key)
                acc["candidates"] += 1
                tw = subset_tw(n, M, cyc, U)
                pre = sum(tw[v] for v in Q) - len(U) - sigma_of(U, B, Mset)
                if pre <= 0:
                    continue
                acc["positive"] += 1
                rows = counted_rows(Q, U, M, cyc)
                sig = unit_flat5_signature(n, E, B, M, Mset, cyc, Q, U, rows)
                if sig["is_unit"]:
                    acc["unit_cases"] += 1
                    atoms.add(atom_key(rows))
                else:
                    acc["nonunit_positive"] += 1
                    if acc["first_nonunit"] is None:
                        acc["first_nonunit"] = {
                            "name": name,
                            "n": n,
                            "m": len(M),
                            "eta": eta,
                            "Q": Q,
                            "U": tuple(sorted(U)),
                            "pre": pre,
                            "sig": {k: v for k, v in sig.items() if k != "flat5_banks"},
                        }
    atom_count = len(atoms)
    margin = eta - atom_count
    acc["atom_count_hist"][atom_count] += 1
    rec = {
        "name": name,
        "n": n,
        "m": len(M),
        "eta": eta,
        "atoms": atom_count,
        "margin": margin,
        "atom_keys": tuple(sorted(atoms))[:8],
    }
    acc["max_atoms"] = rec
    acc["min_margin"] = rec
    if margin < 0:
        acc["fails"] += 1
        acc["first_fail"] = rec
    return acc


def worker(payload):
    g6, max_cuts, max_union_rows = payload
    n, edges = dec(g6)
    out = empty_acc()
    out["graphs"] = 1
    _adj, cuts = gmins(n, edges)
    for idx, side in enumerate(cuts[:max_cuts]):
        merge_acc(out, check_side(f"cen{g6}#cut{idx}", n, edges, side, max_union_rows))
        if out["first_fail"] is not None:
            break
    return out


def fmt_rec(rec):
    if rec is None:
        return ""
    out = dict(rec)
    for key in ("eta", "margin", "pre"):
        if key in out:
            out[key] = fmt_frac(out[key])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--workers", type=int, default=60)
    ap.add_argument("--chunksize", type=int, default=8)
    ap.add_argument("--max-cuts", type=int, default=8)
    ap.add_argument("--max-union-rows", type=int, default=2)
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    if args.limit is not None:
        graphs = graphs[: args.limit]

    total = empty_acc()
    payloads = [(g6, args.max_cuts, args.max_union_rows) for g6 in graphs]
    done = 0
    with mp.Pool(processes=args.workers) as pool:
        for acc in pool.imap_unordered(worker, payloads, chunksize=args.chunksize):
            done += acc["graphs"]
            merge_acc(total, acc)
            if done % 1000 == 0 or done == len(graphs):
                print(
                    f"progress graphs={done}/{len(graphs)} positive={total['positive']} "
                    f"unit_cases={total['unit_cases']} fails={total['fails']}",
                    flush=True,
                )
            if total["first_fail"] is not None:
                pool.terminate()
                break

    print("=== UNIT-FLAT5 group UNIT-PACK gate ===")
    print("n:", args.n)
    print("graphs:", total["graphs"])
    print("cuts:", total["cuts"])
    print("candidates:", total["candidates"])
    print("positive:", total["positive"])
    print("unit_cases:", total["unit_cases"])
    print("nonunit_positive:", total["nonunit_positive"])
    print("fails:", total["fails"])
    print("atom_count_hist:", dict(sorted(total["atom_count_hist"].items())))
    print("max_atoms:", fmt_rec(total["max_atoms"]))
    print("min_margin:", fmt_rec(total["min_margin"]))
    print("first_nonunit:", fmt_rec(total["first_nonunit"]))
    print("first_fail:", fmt_rec(total["first_fail"]))
    print("VERDICT:", "PASS_UNIT_PACK_GROUP_GATE" if total["fails"] == 0 else "FAIL_UNIT_PACK_GROUP_GATE")


if __name__ == "__main__":
    main()
