#!/usr/bin/env python3
"""Exact seed-chain pooling diagnostics for C85.

For every hard hole h, enumerate every admissible factor pair, retain every
missing endpoint p, pass to its seed-2 predecessor u=(p+1)/2, and then collapse
u to its even seed-chain root.  All arithmetic and comparisons are integral.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
C67_PATH = ROOT / "problems/424/fanout/wave5/C67_weak_scb.py"


def load_c67():
    spec = importlib.util.spec_from_file_location("c67_weak_scb", C67_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {C67_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def classify_root(root: int, data: dict) -> str:
    if root in data["hard"]:
        return "hard"
    if root in data["splitless"]:
        return "splitless"
    if root in data["seed3_roots"]:
        return "seed3"
    raise AssertionError(("unclassified root", root))


def audit(limit: int) -> dict:
    c67 = load_c67()
    data = c67.build_arithmetic(limit)
    holes: set[int] = data["holes"]
    generated: set[int] = data["generated"]
    roots: dict[int, int] = data["root_of"]
    pairs: dict[int, list[tuple[int, int]]] = data["pairs"]

    first_root_collision = None
    first_many_pair_single_root = None
    first_root_count_below_pair_count = None
    max_pairs_per_root = {"value": 0}
    min_root_pair_ratio = None
    pair_hist = Counter()
    root_hist = Counter()
    type_profile_hist = Counter()

    for h in sorted(data["hard"]):
        witness_roots: dict[int, set[int]] = {}
        missing_endpoints: set[int] = set()
        for a, b in pairs[h]:
            local_missing = [p for p in (a, b) if p in holes]
            if not local_missing:
                raise AssertionError(("generated hard hole", h, a, b))
            for p in local_missing:
                if p % 2 != 1:
                    raise AssertionError(("even endpoint of odd product", h, p))
                u = (p + 1) // 2
                if u not in holes:
                    raise AssertionError(("predecessor is not a hole", h, p, u))
                r = roots[u]
                missing_endpoints.add(p)
                witness_roots.setdefault(r, set()).add(p)

        d = len(pairs[h])
        rcount = len(witness_roots)
        pair_hist[d] += 1
        root_hist[rcount] += 1
        profile = tuple(sorted(Counter(classify_root(r, data) for r in witness_roots).items()))
        type_profile_hist[str(profile)] += 1

        ratio_key = (rcount, d)
        if min_root_pair_ratio is None or ratio_key[0] * min_root_pair_ratio[1] < min_root_pair_ratio[0] * ratio_key[1]:
            min_root_pair_ratio = (rcount, d, h)

        for r, endpoints in witness_roots.items():
            multiplicity = len(endpoints)
            if multiplicity > max_pairs_per_root["value"]:
                max_pairs_per_root = {
                    "value": multiplicity,
                    "h": h,
                    "root": r,
                    "endpoints": sorted(endpoints),
                    "pairs": pairs[h],
                }
            if multiplicity >= 2 and first_root_collision is None:
                first_root_collision = {
                    "h": h,
                    "root": r,
                    "endpoints": sorted(endpoints),
                    "pairs": pairs[h],
                }

        if d >= 2 and rcount == 1 and first_many_pair_single_root is None:
            only_root = next(iter(witness_roots))
            first_many_pair_single_root = {
                "h": h,
                "root": only_root,
                "endpoints": sorted(witness_roots[only_root]),
                "pairs": pairs[h],
            }
        if rcount < d and first_root_count_below_pair_count is None:
            first_root_count_below_pair_count = {
                "h": h,
                "pair_count": d,
                "root_count": rcount,
                "roots": sorted(witness_roots),
                "pairs": pairs[h],
            }

    # A root is healed by X exactly when its terminal hole has a generated
    # seed-2 child at most X.  This is the global Q boundary on that chain.
    healed_roots = set()
    unhealed_roots = set()
    for root, terminal in data["terminal_of_root"].items():
        child = 2 * terminal - 1
        if child <= limit:
            if child not in generated:
                raise AssertionError(("terminal child is neither generated nor hole", root, terminal, child))
            healed_roots.add(root)
        else:
            unhealed_roots.add(root)

    return {
        "limit": limit,
        "hard_count": len(data["hard"]),
        "first_root_collision": first_root_collision,
        "first_many_pair_single_root": first_many_pair_single_root,
        "first_root_count_below_pair_count": first_root_count_below_pair_count,
        "max_missing_endpoints_on_one_root_for_one_hard_hole": max_pairs_per_root,
        "minimum_distinct_root_to_pair_ratio": {
            "roots": min_root_pair_ratio[0] if min_root_pair_ratio else 0,
            "pairs": min_root_pair_ratio[1] if min_root_pair_ratio else 0,
            "h": min_root_pair_ratio[2] if min_root_pair_ratio else None,
        },
        "pair_count_histogram": dict(sorted(pair_hist.items())),
        "distinct_witness_root_histogram": dict(sorted(root_hist.items())),
        "root_type_profile_histogram": dict(sorted(type_profile_hist.items())),
        "healed_root_count": len(healed_roots),
        "unhealed_root_count": len(unhealed_roots),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(args.limit)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")


if __name__ == "__main__":
    main()
