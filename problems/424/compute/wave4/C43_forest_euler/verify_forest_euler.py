#!/usr/bin/env python3
"""Independent trial-divisor verification of the C43 structural forest."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def factor_pairs(n: int) -> list[tuple[int, int]]:
    result = []
    for a in range(2, math.isqrt(n + 1) + 1):
        if (n + 1) % a:
            continue
        b = (n + 1) // a
        if a < b and allowed(a) and allowed(b):
            result.append((a, b))
    return result


def is_easy3(n: int) -> bool:
    if n % 2 or (n + 1) % 3:
        return False
    parent = (n + 1) // 3
    return allowed(parent) and parent != 3


def is_hard(n: int, pairs: list[tuple[int, int]]) -> bool:
    return n % 2 == 0 and bool(pairs) and not is_easy3(n)


def prefix_audits(
    hard: list[tuple[int, int]],
    targets: list[dict],
    maximum_rank: int,
) -> dict:
    hard_at = {n: rank for n, rank in hard}
    targets_at = {row["child"]: row for row in targets}
    hard_exact = [0] * (maximum_rank + 1)
    exit_exact = {
        cap: [0] * (maximum_rank + 1) for cap in (1, 2)
    }
    result = {
        cap: {
            "maximum_excess": -10**9,
            "maximum_X": None,
            "maximum_rank": None,
            "first_plus_one": None,
            "strict_events": [],
        }
        for cap in (1, 2)
    }
    for x in range(2, max(hard_at | targets_at, default=2) + 1):
        target = targets_at.get(x)
        if target is not None:
            for cap in (1, 2):
                if target["ordinal"] <= cap:
                    exit_exact[cap][target["rank"]] += 1
        source_rank = hard_at.get(x)
        if source_rank is None:
            continue
        hard_exact[source_rank] += 1
        for cap in (1, 2):
            h = q = 0
            for d in range(maximum_rank + 1):
                h += hard_exact[d]
                q += exit_exact[cap][d]
                excess = h - q
                row = result[cap]
                if excess > row["maximum_excess"]:
                    row.update(
                        maximum_excess=excess,
                        maximum_X=x,
                        maximum_rank=d,
                    )
                if excess > 0 and len(row["strict_events"]) < 20:
                    row["strict_events"].append(
                        {"X": x, "rank": d, "H": h, "Q": q}
                    )
                if excess > 1 and row["first_plus_one"] is None:
                    row["first_plus_one"] = {
                        "X": x,
                        "rank": d,
                        "H": h,
                        "Q": q,
                        "excess": excess,
                    }
    return {str(cap): row for cap, row in result.items()}


def literal_stage_audit(
    values: list[int],
    pairs: dict[int, list[tuple[int, int]]],
    member: list[bool],
    rank: list[int | None],
) -> dict:
    current = set(values)
    first_absent: dict[int, int] = {}
    transitions = 0
    while True:
        following = {2, 3}
        for n in values:
            if n in (2, 3):
                continue
            if any(a in current and b in current for a, b in pairs[n]):
                following.add(n)
        transitions += 1
        for n in current - following:
            first_absent[n] = transitions
        if following == current:
            break
        current = following
    mismatches = []
    for n in values:
        if (n in current) != member[n]:
            mismatches.append({"n": n, "kind": "membership"})
        elif not member[n] and first_absent[n] != rank[n] + 1:
            mismatches.append(
                {
                    "n": n,
                    "kind": "rank",
                    "first_absent": first_absent[n],
                    "recursive_rank": rank[n],
                }
            )
    return {
        "transitions_to_fixpoint": transitions,
        "mismatches": mismatches,
    }


def euler_audit(
    limit: int,
    values: list[int],
    member: list[bool],
    rank: list[int | None],
    pairs: dict[int, list[tuple[int, int]]],
    hard_set: set[int],
    maximum_rank: int,
) -> dict:
    first_mismatch = None
    checked = 0
    for d in range(maximum_rank + 1):
        m = [0] * (limit + 1)
        o = [0] * (limit + 1)
        e = [0] * (limit + 1)
        h = [0] * (limit + 1)
        q2 = [0] * (limit + 1)
        r3 = [0] * (limit + 1)
        a2 = [0] * (limit + 1)
        a3 = [0] * (limit + 1)
        for n in values:
            if member[n] or rank[n] > d:
                continue
            m[n] += 1
            if n % 2:
                o[n] += 1
            if not pairs[n]:
                e[n] += 1
            if n in hard_set:
                h[n] += 1
            for multiplier, healed, escape in (
                (2, q2, a2),
                (3, r3, a3),
            ):
                if multiplier == 3 and n % 2 == 0:
                    continue
                child = multiplier * n - 1
                if child > limit:
                    continue
                if member[child]:
                    healed[child] += 1
                elif rank[child] > d:
                    escape[child] += 1
        arrays = (m, o, e, h, q2, r3, a2, a3)
        for x in range(1, limit + 1):
            for row in arrays:
                row[x] += row[x - 1]
            y = (x + 1) // 2
            z = (x + 1) // 3
            left = h[x] - q2[x]
            right = (
                m[x]
                - e[x]
                - m[y]
                - o[z]
                + r3[x]
                + a2[x]
                + a3[x]
            )
            checked += 1
            if left != right:
                first_mismatch = {
                    "X": x,
                    "rank": d,
                    "left": left,
                    "right": right,
                }
                break
        if first_mismatch is not None:
            break
    return {
        "identity": (
            "H_d-Q2_d=M_d(X)-E(X)-M_d(floor((X+1)/2))"
            "-O_d(floor((X+1)/3))+R3_d+A2_d+A3_d"
        ),
        "prefix_rank_pairs_checked": checked,
        "first_mismatch": first_mismatch,
    }


def audit(limit: int, cpp_json: Path | None) -> dict:
    values = [n for n in range(2, limit + 1) if allowed(n)]
    pairs = {n: factor_pairs(n) for n in values}
    member = [False] * (limit + 1)
    rank: list[int | None] = [None] * (limit + 1)
    root: list[int | None] = [None] * (limit + 1)
    member[2] = member[3] = True
    hard: list[tuple[int, int]] = []
    targets: list[dict] = []
    exit_ordinal: dict[int, int] = defaultdict(int)
    forest_failures = []

    for n in values:
        if n in (2, 3):
            continue
        generated = any(member[a] and member[b] for a, b in pairs[n])
        if generated:
            member[n] = True
            if n % 2:
                parent = (n + 1) // 2
                if not member[parent]:
                    component = root[parent]
                    if component is None:
                        raise AssertionError((n, parent, "missing root"))
                    exit_ordinal[component] += 1
                    targets.append(
                        {
                            "child": n,
                            "parent": parent,
                            "rank": rank[parent],
                            "root": component,
                            "ordinal": exit_ordinal[component],
                        }
                    )
            continue

        if not pairs[n]:
            rank[n] = 0
        else:
            rank[n] = 1 + max(
                min(rank[x] for x in (a, b) if not member[x])
                for a, b in pairs[n]
            )

        parent = None
        if n % 2:
            parent = (n + 1) // 2
        elif is_easy3(n):
            parent = (n + 1) // 3
        if parent is None:
            root[n] = n
            if not (not pairs[n] or is_hard(n, pairs[n])):
                forest_failures.append({"n": n, "kind": "bad root"})
        else:
            if member[parent] or rank[parent] >= rank[n] or root[parent] is None:
                forest_failures.append(
                    {
                        "n": n,
                        "kind": "bad parent",
                        "parent": parent,
                        "parent_member": member[parent],
                        "parent_rank": rank[parent],
                        "rank": rank[n],
                    }
                )
            root[n] = root[parent]
        if is_hard(n, pairs[n]):
            hard.append((n, rank[n]))

    maximum_rank = max(r for r in rank if r is not None)
    prefix = prefix_audits(hard, targets, maximum_rank)
    stages = literal_stage_audit(values, pairs, member, rank)
    hard_set = {n for n, _ in hard}
    euler = euler_audit(
        limit, values, member, rank, pairs, hard_set, maximum_rank
    )

    counterexample = prefix["1"]["first_plus_one"]
    witness = None
    if counterexample is not None:
        x = counterexample["X"]
        d = counterexample["rank"]
        witness = {
            **counterexample,
            "hard": [
                {"value": n, "rank": r}
                for n, r in hard
                if n <= x and r <= d
            ],
            "first_component_exits": [
                row for row in targets
                if row["child"] <= x
                and row["rank"] <= d
                and row["ordinal"] == 1
            ],
            "excluded_later_component_exits": [
                row for row in targets
                if row["child"] <= x
                and row["rank"] <= d
                and row["ordinal"] > 1
            ],
        }

    cpp_cross_check = {"requested": cpp_json is not None}
    if cpp_json is not None:
        cpp = json.loads(cpp_json.read_text(encoding="ascii"))
        cap_rows = {row["cap"]: row for row in cpp["cap_audits"]}
        expected = {
            "hard_total": len(hard),
            "target_total": len(targets),
            "splitless_roots": sum(
                not member[n] and not pairs[n] for n in values
            ),
            "cap1_max": prefix["1"]["maximum_excess"],
            "cap1_first": prefix["1"]["first_plus_one"],
            "cap2_max": prefix["2"]["maximum_excess"],
        }
        observed = {
            "hard_total": cpp["hard_total"],
            "target_total": cpp["healed_seed2_exits_total"],
            "splitless_roots": cpp["splitless_roots"],
            "cap1_max": cap_rows[1]["rank_prefix"]["maximum_excess"],
            "cap1_first": {
                "X": cap_rows[1]["rank_prefix"]["first_plus_one_X"],
                "rank": cap_rows[1]["rank_prefix"]["first_plus_one_rank"],
                "H": cap_rows[1]["rank_prefix"]["first_plus_one_H"],
                "Q": cap_rows[1]["rank_prefix"]["first_plus_one_Q"],
                "excess": 2,
            },
            "cap2_max": cap_rows[2]["rank_prefix"]["maximum_excess"],
        }
        cpp_cross_check.update(
            expected=expected,
            observed=observed,
            equal=expected == observed,
        )

    assertions = {
        "forest_parent_and_rank": not forest_failures,
        "literal_stages": not stages["mismatches"],
        "euler_identity": euler["first_mismatch"] is None,
        "cap1_first_failure_is_1002_rank3": (
            limit < 1002
            or counterexample
            == {"X": 1002, "rank": 3, "H": 35, "Q": 33, "excess": 2}
        ),
        "cap2_has_no_plus_one_failure": prefix["2"]["first_plus_one"] is None,
        "cpp_cross_check": cpp_cross_check.get("equal", True),
    }
    if not all(assertions.values()):
        raise AssertionError(assertions)

    return {
        "schema_version": 1,
        "limit": limit,
        "algorithm": "trial divisors plus literal descending approximants",
        "generated": sum(member),
        "hard_total": len(hard),
        "target_total": len(targets),
        "splitless_roots": sum(
            not member[n] and not pairs[n] for n in values
        ),
        "maximum_rank": maximum_rank,
        "rank_histogram_hard": dict(sorted(Counter(r for _, r in hard).items())),
        "rank_histogram_targets": dict(
            sorted(Counter(row["rank"] for row in targets).items())
        ),
        "forest_failures": forest_failures,
        "literal_stage_audit": stages,
        "euler_audit": euler,
        "prefix_audits": prefix,
        "cap1_counterexample": witness,
        "cpp_cross_check": cpp_cross_check,
        "assertions": assertions,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=5000)
    parser.add_argument("--cpp-json", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.limit < 100:
        raise ValueError("limit must be at least 100")
    result = audit(args.limit, args.cpp_json)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(
        json.dumps(
            {
                "limit": result["limit"],
                "hard_total": result["hard_total"],
                "target_total": result["target_total"],
                "euler_checks": result["euler_audit"][
                    "prefix_rank_pairs_checked"
                ],
                "cap1_first": result["prefix_audits"]["1"][
                    "first_plus_one"
                ],
                "cap2_max": result["prefix_audits"]["2"]["maximum_excess"],
                "assertions": result["assertions"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
