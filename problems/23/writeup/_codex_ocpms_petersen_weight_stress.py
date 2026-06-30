"""Stress OC-PMS on non-uniform blowups of the N=10 equality atom.

The blowup classes are independent and edges between classes are complete
bipartite.  MaxCut over class-side fractions is multilinear, hence an
optimum exists at a 0/1 quotient assignment.  We therefore test whether the
inherited equality-atom cut is quotient-maximum by enumerating 2^10 class
assignments before doing the expensive explicit OC-PMS scan.
"""

import argparse
import random

from _codex_ocpms_gate import scan_cut
from _codex_ocpms_petersen_blow import base_E, base_n, base_side, blow


def qcut_value(weights, side):
    val = 0
    for a, b in base_E:
        if side[a] != side[b]:
            val += weights[a] * weights[b]
    return val


def qmaxcut(weights):
    best = -1
    bestmask = None
    for mask in range(1 << base_n):
        side = [(mask >> i) & 1 for i in range(base_n)]
        val = qcut_value(weights, side)
        if val > best:
            best = val
            bestmask = mask
    return best, bestmask


def scan_weights(weights):
    inherited = qcut_value(weights, base_side)
    best, mask = qmaxcut(weights)
    if inherited != best:
        return {
            "weights": tuple(weights),
            "ismax": False,
            "gap": best - inherited,
            "rows": 0,
            "over": 0,
            "pfail": 0,
            "cfail": 0,
        }

    n, E, side = blow(weights)
    adj = [set() for _ in range(n)]
    for a, b in E:
        adj[a].add(b)
        adj[b].add(a)
    acc = dict(
        rows=0,
        over_rows=0,
        collapse_fail=0,
        collapse_ex=None,
        pms_rows=0,
        pms_fail=0,
        pms_ex=None,
        pms_min=None,
        pms_min_ex=None,
    )
    scan_cut("weighted_blow", n, adj, side, acc)
    return {
        "weights": tuple(weights),
        "ismax": True,
        "gap": 0,
        "n": n,
        "rows": acc["rows"],
        "over": acc["over_rows"],
        "pfail": acc["pms_fail"],
        "cfail": acc["collapse_fail"],
        "min": acc["pms_min"],
        "min_ex": acc["pms_min_ex"],
        "pms_ex": acc["pms_ex"],
        "collapse_ex": acc["collapse_ex"],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=1000)
    ap.add_argument("--max-w", type=int, default=6)
    ap.add_argument("--seed", type=int, default=20260630)
    args = ap.parse_args()
    rng = random.Random(args.seed)

    tests = []
    for t in range(1, args.max_w + 1):
        tests.append([t] * base_n)
    for _ in range(args.trials):
        tests.append([rng.randint(1, args.max_w) for _ in range(base_n)])

    seen = set()
    total = dict(tests=0, ismax=0, over=0, cfail=0, pfail=0)
    min_rec = None
    first_bad = None
    gap_hist = {}
    for weights in tests:
        key = tuple(weights)
        if key in seen:
            continue
        seen.add(key)
        rec = scan_weights(weights)
        total["tests"] += 1
        if not rec["ismax"]:
            gap_hist[rec["gap"]] = gap_hist.get(rec["gap"], 0) + 1
            continue
        total["ismax"] += 1
        total["over"] += rec["over"]
        total["cfail"] += rec["cfail"]
        total["pfail"] += rec["pfail"]
        if rec.get("min") is not None and (
            min_rec is None or rec["min"] < min_rec["min"]
        ):
            min_rec = rec
        if rec["cfail"] or rec["pfail"]:
            first_bad = rec
            break
        print(
            "ISMAX",
            rec["weights"],
            "n",
            rec["n"],
            "rows",
            rec["rows"],
            "over",
            rec["over"],
            "min",
            rec.get("min"),
            flush=True,
        )

    print("weighted Petersen-blow stress")
    print(total)
    print("gap_hist_small", sorted(gap_hist.items())[:20])
    print("min_rec", min_rec)
    print("first_bad", first_bad)
    print("VERDICT", "FAIL" if first_bad else "no failure")


if __name__ == "__main__":
    main()

