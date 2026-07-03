#!/usr/bin/env python3
"""Parallel exact weighted-blowup hunt for NCH T=1 on Mycielskian supports."""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
from fractions import Fraction
from pathlib import Path

from _codex_nch_sanity_gate import named_graphs, gamma_min_structs, side_string, frac_s
from _codex_nch_weighted_blowup_hunt import terminal_values

_G = {}


def _init_worker(cyc, n: int, max_weight: int, terminals):
    _G["cyc"] = cyc
    _G["n"] = n
    _G["max_weight"] = max_weight
    _G["terminals"] = terminals


def _suffixes(prefix, n: int, max_weight: int):
    point = list(prefix) + [1] * (n - len(prefix))

    def rec(i: int):
        if i == n:
            yield tuple(point)
            return
        for value in range(1, max_weight + 1):
            point[i] = value
            yield from rec(i + 1)
        point[i] = 1

    yield from rec(len(prefix))


def _scan_prefix(prefix):
    cyc = _G["cyc"]
    n = _G["n"]
    max_weight = _G["max_weight"]
    terminals = _G["terminals"]
    checked = 0
    best_gap = None
    best_rec = None
    violations = []
    for weights in _suffixes(prefix, n, max_weight):
        checked += 1
        bound = sum(weights) - 1
        for t, value in terminal_values(cyc, n, weights, terminals):
            gap = value - bound
            if best_gap is None or gap > best_gap:
                best_gap = gap
                best_rec = {
                    "terminal": t,
                    "weights": list(weights),
                    "sH": frac_s(value),
                    "bound": str(bound),
                    "gap": frac_s(gap),
                    "gap_num": gap.numerator,
                    "gap_den": gap.denominator,
                }
            if gap > 0 and len(violations) < 5:
                violations.append({
                    "terminal": t,
                    "weights": list(weights),
                    "sH": frac_s(value),
                    "bound": str(bound),
                    "gap": frac_s(gap),
                })
    return checked, best_gap, best_rec, violations


def prefixes(length: int, max_weight: int):
    if length <= 0:
        yield ()
        return
    point = [1] * length

    def rec(i: int):
        if i == length:
            yield tuple(point)
            return
        for value in range(1, max_weight + 1):
            point[i] = value
            yield from rec(i + 1)
        point[i] = 1

    yield from rec(0)


def scan_cut_parallel(name, n, side, gamma, cyc, max_weight, terminals, workers, prefix_len):
    tasks = list(prefixes(min(prefix_len, n), max_weight))
    checked = 0
    best_gap = None
    best_rec = None
    violations = []
    done = 0
    with mp.Pool(processes=workers, initializer=_init_worker, initargs=(cyc, n, max_weight, terminals)) as pool:
        for sub_checked, sub_gap, sub_best, sub_violations in pool.imap_unordered(_scan_prefix, tasks, chunksize=1):
            done += 1
            checked += sub_checked
            if sub_gap is not None and (best_gap is None or sub_gap > best_gap):
                best_gap = sub_gap
                best_rec = sub_best
            if len(violations) < 5:
                violations.extend(sub_violations[: 5 - len(violations)])
            if done % max(1, len(tasks) // 20) == 0 or done == len(tasks):
                print("prefixes", done, "/", len(tasks), "checked", checked, flush=True)
    return {
        "name": name,
        "n": n,
        "side": side,
        "gamma": gamma,
        "max_weight": max_weight,
        "workers": workers,
        "prefix_len": min(prefix_len, n),
        "prefix_tasks": len(tasks),
        "checked_weight_vectors": checked,
        "best": best_rec,
        "violations": violations,
    }


def parse_ints(text: str):
    return [int(x) for x in text.split(",") if x.strip()]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="MycC7")
    ap.add_argument("--max-myc-cycle", type=int, default=11)
    ap.add_argument("--max-weight", type=int, default=3)
    ap.add_argument("--cut-limit", type=int, default=0)
    ap.add_argument("--cut-indices", default="")
    ap.add_argument("--terminals", default="")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--prefix-len", type=int, default=4)
    ap.add_argument("--summary", default="tmp/nch_weighted_myc_parallel_v1.json")
    args = ap.parse_args()

    terminals = None if not args.terminals else parse_ints(args.terminals)
    cut_indices = None if not args.cut_indices else set(parse_ints(args.cut_indices))
    out = {
        "schema": "nch_t1_weighted_myc_blowup_hunt_parallel_v1",
        "terminal_convention": "fixed clone; bound=sum(weights)-1",
        "only": args.only,
        "max_weight": args.max_weight,
        "workers": args.workers,
        "prefix_len": args.prefix_len,
        "cuts": [],
        "verdict": "PASS",
    }
    for name, n, edges in named_graphs(args.max_myc_cycle):
        if args.only and name != args.only:
            continue
        _best_cut, structs = gamma_min_structs(name, n, edges)
        for idx, (side_int, _side, st, gamma) in enumerate(structs):
            if cut_indices is not None and idx not in cut_indices:
                continue
            if args.cut_limit and idx >= args.cut_limit:
                break
            M, ell, _T, _mu, cyc = st
            rec = scan_cut_parallel(name, n, side_string(n, side_int), gamma, cyc, args.max_weight, terminals, args.workers, args.prefix_len)
            rec["cut_index"] = idx
            rec["bad_edges"] = len(M)
            rec["ell_values"] = sorted(set(ell.values()))
            print(name, "cut", idx, "B", args.max_weight, "checked", rec["checked_weight_vectors"], "best_gap", rec["best"]["gap"], "terminal", rec["best"]["terminal"], flush=True)
            if rec["violations"]:
                out["verdict"] = "FAIL"
            out["cuts"].append(rec)
    Path(args.summary).write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print("VERDICT", out["verdict"], args.summary)
    if out["verdict"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
