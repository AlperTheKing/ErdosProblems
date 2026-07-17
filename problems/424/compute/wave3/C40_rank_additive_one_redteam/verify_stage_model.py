#!/usr/bin/env python3
"""Brute-force C40 replay using divisors and literal descending stages."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def factor_pairs(n: int, include_equal: bool = False) -> list[tuple[int, int]]:
    product = n + 1
    pairs = []
    for a in range(2, math.isqrt(product) + 1):
        if product % a:
            continue
        b = product // a
        if (a < b or include_equal and a == b) and allowed(a) and allowed(b):
            pairs.append((a, b))
    return pairs


def build_model(limit: int, include_equal: bool = False) -> dict:
    pairs = [factor_pairs(n, include_equal) for n in range(limit + 1)]
    member = [False] * (limit + 1)
    rank: list[int | None] = [None] * (limit + 1)
    member[2] = member[3] = True
    hard: list[tuple[int, int]] = []
    targets: list[tuple[int, int]] = []

    for n in range(4, limit + 1):
        if not allowed(n):
            continue
        if any(member[a] and member[b] for a, b in pairs[n]):
            member[n] = True
            if n % 2:
                q = (n + 1) // 2
                if allowed(q) and not member[q]:
                    assert rank[q] is not None
                    targets.append((n, rank[q]))
            continue

        if not pairs[n]:
            rank[n] = 0
        else:
            blockers = []
            for a, b in pairs[n]:
                missing = [rank[x] for x in (a, b) if not member[x]]
                assert missing and all(x is not None for x in missing)
                blockers.append(min(missing))
            rank[n] = 1 + max(blockers)

        if n % 2 or not pairs[n]:
            continue
        q3 = (n + 1) // 3
        easy = (n + 1) % 3 == 0 and allowed(q3) and (include_equal or q3 != 3)
        if not easy:
            hard.append((n, rank[n]))

    return {
        "pairs": pairs,
        "member": member,
        "rank": rank,
        "hard": hard,
        "targets": targets,
    }


def stage_ranks(model: dict, limit: int) -> dict:
    pairs = model["pairs"]
    current = [allowed(n) for n in range(limit + 1)]
    current[0] = current[1] = False
    death_rank: list[int | None] = [None] * (limit + 1)
    stages = 0
    while True:
        stages += 1
        following = [False] * (limit + 1)
        following[2] = following[3] = True
        for n in range(4, limit + 1):
            if allowed(n) and any(current[a] and current[b] for a, b in pairs[n]):
                following[n] = True
        for n in range(2, limit + 1):
            if current[n] and not following[n]:
                death_rank[n] = stages - 1
        if following == current:
            break
        current = following
        if stages > limit:
            raise AssertionError("descending stages did not stabilize")

    mismatches = []
    for n in range(2, limit + 1):
        if not allowed(n):
            continue
        if current[n] != model["member"][n]:
            mismatches.append({"n": n, "kind": "membership"})
        if not current[n] and death_rank[n] != model["rank"][n]:
            mismatches.append({
                "n": n,
                "kind": "rank",
                "stage": death_rank[n],
                "recursive": model["rank"][n],
            })
    return {"stages_to_fixpoint": stages, "mismatches": mismatches}


def prefix_audit(hard: list[tuple[int, int]], targets: list[tuple[int, int]]) -> dict:
    ranks = 1 + max([0] + [r for _, r in hard] + [r for _, r in targets])
    hc = [0] * ranks
    qc = [0] * ranks
    ti = 0
    strict = []
    plus_one = []
    maximum = {"excess": -10**9, "X": 0, "rank": 0, "H": 0, "Q": 0}
    for x, rank in hard:
        while ti < len(targets) and targets[ti][0] <= x:
            qc[targets[ti][1]] += 1
            ti += 1
        hc[rank] += 1
        hs = qs = 0
        for d in range(ranks):
            hs += hc[d]
            qs += qc[d]
            excess = hs - qs
            if excess > maximum["excess"]:
                maximum = {"excess": excess, "X": x, "rank": d, "H": hs, "Q": qs}
            if excess > 0:
                strict.append({"X": x, "rank": d, "excess": excess})
            if excess > 1:
                plus_one.append({"X": x, "rank": d, "excess": excess})
    return {
        "maximum": maximum,
        "strict_failures": strict,
        "plus_one_failures": plus_one,
    }


def compare_cpp(model: dict, audit: dict, cpp_path: Path | None) -> dict:
    if cpp_path is None:
        return {"requested": False}
    cpp = json.loads(cpp_path.read_text(encoding="ascii"))
    expected = {
        "hard_total": len(model["hard"]),
        "target_total": len(model["targets"]),
        "maximum_excess": audit["maximum"]["excess"],
        "maximum_X": audit["maximum"]["X"],
        "maximum_rank": audit["maximum"]["rank"],
        "plus_one_failures": len(audit["plus_one_failures"]),
    }
    observed = {
        "hard_total": cpp["hard_total"],
        "target_total": cpp["target_total"],
        "maximum_excess": cpp["true_child_coordinate_prefix"]["maximum_excess"],
        "maximum_X": cpp["true_child_coordinate_prefix"]["maximum_X"],
        "maximum_rank": cpp["true_child_coordinate_prefix"]["maximum_rank"],
        "plus_one_failures": cpp["true_child_coordinate_prefix"]["plus_one_failures"],
    }
    return {"requested": True, "expected": expected, "observed": observed,
            "equal": expected == observed}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=5000)
    parser.add_argument("--cpp-json", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.limit < 100:
        raise ValueError("limit must be at least 100")

    actual = build_model(args.limit)
    equal = build_model(args.limit, include_equal=True)
    stages = stage_ranks(actual, args.limit)
    audit = prefix_audit(actual["hard"], actual["targets"])
    first_difference = next(
        (n for n in range(2, args.limit + 1)
         if actual["member"][n] != equal["member"][n]),
        None,
    )

    result = {
        "schema_version": 1,
        "limit": args.limit,
        "algorithm": "trial divisors plus literal descending approximants",
        "hard_total": len(actual["hard"]),
        "target_total": len(actual["targets"]),
        "rank_histogram_hard": dict(sorted(Counter(r for _, r in actual["hard"]).items())),
        "rank_histogram_target": dict(sorted(Counter(r for _, r in actual["targets"]).items())),
        "prefix_audit": audit,
        "descending_stage_audit": stages,
        "conventions": {
            "hard_values_all_even": all(n % 2 == 0 for n, _ in actual["hard"]),
            "target_events_all_odd": all(n % 2 == 1 for n, _ in actual["targets"]),
            "target_parents_distinct_from_seed_2": all((n + 1) // 2 != 2 for n, _ in actual["targets"]),
            "all_hard_ranks_at_least_two": all(r >= 2 for _, r in actual["hard"]),
            "event_coordinate": "generated child 2q-1",
            "pairs_strictly_distinct": all(a < b for rows in actual["pairs"] for a, b in rows),
            "first_equal_factor_membership_difference": first_difference,
            "rank_is_death_stage_minus_one": not stages["mismatches"],
        },
        "cpp_cross_check": compare_cpp(actual, audit, args.cpp_json),
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps({
        "limit": args.limit,
        "hard_total": result["hard_total"],
        "target_total": result["target_total"],
        "maximum": audit["maximum"],
        "plus_one_failures": len(audit["plus_one_failures"]),
        "stage_mismatches": len(stages["mismatches"]),
        "first_equal_factor_membership_difference": first_difference,
        "cpp_equal": result["cpp_cross_check"].get("equal"),
    }, indent=2))


if __name__ == "__main__":
    main()
