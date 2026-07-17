#!/usr/bin/env python3
"""Solver-free replay and exhaustive small audit for C81 blocker gates."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path


def allowed(value: int) -> bool:
    return value >= 2 and value % 3 != 1


def pair_table(limit: int) -> list[list[tuple[int, int]]]:
    pairs: list[list[tuple[int, int]]] = [[] for _ in range(limit + 1)]
    for left in range(2, math.isqrt(limit + 1) + 1):
        if not allowed(left):
            continue
        for right in range(left + 1, (limit + 1) // left + 1):
            if allowed(right):
                pairs[left * right - 1].append((left, right))
    return pairs


def hard_values(limit: int, pairs: list[list[tuple[int, int]]]) -> list[int]:
    result = []
    for value in range(2, limit + 1):
        if not allowed(value) or value % 2 or not pairs[value]:
            continue
        if (value + 1) % 3:
            result.append(value)
            continue
        parent = (value + 1) // 3
        if not (allowed(parent) and parent != 3):
            result.append(value)
    return result


def chain_top(root: int, cutoff: int) -> int:
    value = root
    while 2 * value - 1 <= cutoff:
        value = 2 * value - 1
    return value


def forward_closed(
    source: set[int], cutoff: int, pairs: list[list[tuple[int, int]]]
) -> bool:
    if not {2, 3}.issubset(source):
        return False
    return all(
        value in source
        for value in range(4, cutoff + 1)
        if allowed(value)
        for left, right in pairs[value]
        if left in source and right in source
    )


def image_of(
    source: set[int], cutoff: int, pairs: list[list[tuple[int, int]]]
) -> set[int]:
    return {2, 3} | {
        value
        for value in range(4, cutoff + 1)
        if allowed(value)
        and any(left in source and right in source for left, right in pairs[value])
    }


def excess_direct(
    image: set[int],
    cutoff: int,
    hard_set: set[int],
) -> tuple[int, int, int]:
    hard_holes = sum(
        value <= cutoff and value not in image for value in hard_set
    )
    boundaries = sum(
        parent not in image and 2 * parent - 1 in image
        for parent in range(2, (cutoff + 1) // 2 + 1)
        if allowed(parent)
    )
    return hard_holes - boundaries, hard_holes, boundaries


def shell_counts(
    image: set[int], cutoff: int, hard_set: set[int]
) -> tuple[int, int]:
    unhealed = 0
    healed = 0
    for root in range(2, cutoff + 1, 2):
        if not allowed(root):
            continue
        top = chain_top(root, cutoff)
        if root in hard_set:
            unhealed += top not in image
        else:
            healed += root not in image and top in image
    return unhealed, healed


def excess_shell(image: set[int], cutoff: int, hard_set: set[int]) -> int:
    unhealed, healed = shell_counts(image, cutoff, hard_set)
    return unhealed - healed


def blocker_statistics(
    source: set[int],
    image: set[int],
    cutoff: int,
    pairs: list[list[tuple[int, int]]],
) -> dict:
    values = {value for value in range(2, cutoff + 1) if allowed(value)}
    missing = values - source
    image_holes = values - image
    factorable_holes = {value for value in image_holes if pairs[value]}
    single_hit = 0
    double_hit = 0
    blockers_used = set()
    for value in factorable_holes:
        for left, right in pairs[value]:
            hits = int(left in missing) + int(right in missing)
            if hits == 0:
                raise RuntimeError(f"unblocked image hole at {value}")
            single_hit += hits == 1
            double_hit += hits == 2
            if left in missing:
                blockers_used.add(left)
            if right in missing:
                blockers_used.add(right)
    return {
        "source_value_count": len(values),
        "source_missing_count": len(missing),
        "source_member_count": len(source),
        "image_member_count": len(image),
        "image_hole_count": len(image_holes),
        "factorable_image_hole_count": len(factorable_holes),
        "unsupported_source_count": len((source - image) - {2, 3}),
        "blocked_pair_count": single_hit + double_hit,
        "single_hit_pair_count": single_hit,
        "double_hit_pair_count": double_hit,
        "distinct_source_blockers_used": len(blockers_used),
    }


def exhaustive(limit: int) -> dict:
    values = [value for value in range(2, limit + 1) if allowed(value)]
    source_limit = (limit + 1) // 2
    optional = [
        value
        for value in values
        if value <= source_limit and value not in (2, 3)
    ]
    fixed_present = {value for value in values if value > source_limit}
    pairs = pair_table(limit)
    hard = hard_values(limit, pairs)
    hard_set = set(hard)
    maxima = {cutoff: -len(values) for cutoff in hard}
    maximizers = {cutoff: None for cutoff in hard}
    closed_sources = 0
    identity_checks = 0
    for mask in range(1 << len(optional)):
        source = {2, 3} | fixed_present | {
            value
            for index, value in enumerate(optional)
            if mask & (1 << index)
        }
        if not forward_closed(source, limit, pairs):
            continue
        closed_sources += 1
        image = image_of(source, limit, pairs)
        for cutoff in range(2, limit + 1):
            direct, _, _ = excess_direct(image, cutoff, hard_set)
            shell = excess_shell(image, cutoff, hard_set)
            identity_checks += 1
            if direct != shell:
                raise RuntimeError(
                    f"exhaustive shell failure mask={mask} cutoff={cutoff}"
                )
        for cutoff in hard:
            value, _, _ = excess_direct(image, cutoff, hard_set)
            if value > maxima[cutoff]:
                maxima[cutoff] = value
                maximizers[cutoff] = sorted(source)
    return {
        "limit": limit,
        "source_variable_limit": source_limit,
        "subset_count": 1 << len(optional),
        "closed_source_count": closed_sources,
        "identity_checks": identity_checks,
        "hard_cutoffs": hard,
        "maxima": {str(key): value for key, value in maxima.items()},
        "maximizers": {str(key): value for key, value in maximizers.items()},
    }


def replay_gate(path: Path, exhaustive_result: dict) -> dict:
    gate = json.loads(path.read_text(encoding="ascii"))
    if gate.get("exact_arithmetic") is not True:
        raise RuntimeError("gate does not declare exact arithmetic")
    stop = int(gate["target_cutoff_last"])
    pairs = pair_table(stop)
    hard = hard_values(stop, pairs)
    hard_set = set(hard)
    expected = [
        value
        for value in hard
        if int(gate["target_cutoff_first"]) <= value <= stop
    ]
    covered = []
    replays = 0
    verified_rows = []
    for row in gate["rows"]:
        cutoffs = list(map(int, row["cutoffs"]))
        covered.extend(cutoffs)
        if row["status"] != "OPTIMAL":
            raise RuntimeError(f"nonoptimal row ending {row['cutoff_last']}")
        if int(row["objective_excess"]) != int(row["best_objective_bound"]):
            raise RuntimeError("objective and bound differ")
        selected = int(row["selected_cutoff"])
        local_values = {
            value for value in range(2, selected + 1) if allowed(value)
        }
        missing = {
            int(value)
            for value in row["source_missing"]
            if int(value) <= selected
        }
        source = local_values - missing
        if not forward_closed(source, selected, pairs):
            raise RuntimeError(f"source replay fails at {selected}")
        image = image_of(source, selected, pairs)
        direct, hard_count, boundary_count = excess_direct(
            image, selected, hard_set
        )
        unhealed, healed = shell_counts(image, selected, hard_set)
        shell = unhealed - healed
        if direct != shell or direct != int(row["objective_excess"]):
            raise RuntimeError(f"objective replay fails at {selected}")
        replay = row["replay"]
        if hard_count != int(replay["hard_hole_count"]):
            raise RuntimeError("hard count replay mismatch")
        if boundary_count != int(replay["boundary_count"]):
            raise RuntimeError("boundary count replay mismatch")
        blocker = blocker_statistics(source, image, selected, pairs)
        for key, value in blocker.items():
            if value != int(replay[key]):
                raise RuntimeError(f"blocker replay mismatch for {key}")
        if max(map(int, row["witness_excess_by_cutoff"].values())) != direct:
            raise RuntimeError("selected witness does not maximize its group")
        if max(cutoffs) <= int(exhaustive_result["limit"]):
            exact_group = max(
                int(exhaustive_result["maxima"][str(cutoff)])
                for cutoff in cutoffs
            )
            if exact_group != int(row["objective_excess"]):
                raise RuntimeError(
                    f"CP-SAT/brute mismatch for group ending {max(cutoffs)}"
                )
        verified_rows.append(
            {
                "cutoff": selected,
                "objective_excess": direct,
                "hard_hole_count": hard_count,
                "boundary_count": boundary_count,
                "unhealed_hard_count": unhealed,
                "healed_nonhard_count": healed,
                "blocker": blocker,
                "model": {
                    key: int(row[key])
                    for key in (
                        "source_limit",
                        "source_variables",
                        "image_target_count",
                        "support_pair_gates",
                        "support_selectors",
                        "self_blocking_clauses",
                        "model_proto_bytes",
                    )
                },
            }
        )
        replays += 1
    if covered != expected:
        raise RuntimeError("hard-cutoff coverage is not exact")
    if not gate["all_groups_optimal"]:
        raise RuntimeError("gate summary is not all-optimal")
    if gate["global_optimum"] != max(
        int(row["objective_excess"]) for row in gate["rows"]
    ):
        raise RuntimeError("global optimum summary mismatch")
    individual_optima = all(int(row["cutoff_count"]) == 1 for row in gate["rows"])
    structural = None
    if individual_optima:
        equality = [
            row["cutoff"]
            for row in verified_rows
            if row["objective_excess"] == 0
        ]
        minimum = min(row["objective_excess"] for row in verified_rows)
        tail_maxima = {}
        for threshold in (1001, 2001, 5001, 7501, 9001):
            tail = [row for row in verified_rows if row["cutoff"] >= threshold]
            if not tail:
                continue
            optimum = max(row["objective_excess"] for row in tail)
            tail_maxima[str(threshold)] = {
                "objective_excess": optimum,
                "cutoffs": [
                    row["cutoff"]
                    for row in tail
                    if row["objective_excess"] == optimum
                ],
            }
        structural = {
            "zero_excess_cutoffs": equality,
            "last_zero_excess_cutoff": equality[-1] if equality else None,
            "minimum_objective_excess": minimum,
            "minimum_cutoffs": [
                row["cutoff"]
                for row in verified_rows
                if row["objective_excess"] == minimum
            ],
            "objective_histogram": {
                str(value): count
                for value, count in sorted(
                    Counter(
                        row["objective_excess"] for row in verified_rows
                    ).items()
                )
            },
            "tail_maxima": tail_maxima,
            "last_hard_cutoff": verified_rows[-1],
        }
    return {
        "file": str(path),
        "groups_replayed": replays,
        "hard_cutoffs_covered": len(covered),
        "first_cutoff": covered[0],
        "last_cutoff": covered[-1],
        "global_optimum": gate["global_optimum"],
        "individual_cutoff_optima": individual_optima,
        "all_objective_bounds_nonpositive": all(
            int(row["best_objective_bound"]) <= 0 for row in gate["rows"]
        ),
        "status_counts": dict(Counter(row["status"] for row in gate["rows"])),
        "structural_statistics": structural,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", type=Path, required=True)
    parser.add_argument("--exhaustive-limit", type=int, default=54)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.exhaustive_limit > 54:
        parser.error("exhaustive limit above 54 is intentionally disabled")
    exhaustive_result = exhaustive(args.exhaustive_limit)
    replay = replay_gate(args.gate, exhaustive_result)
    result = {
        "schema_version": 1,
        "solver_free": True,
        "exhaustive": exhaustive_result,
        "gate_replay": replay,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(
        f"closed={exhaustive_result['closed_source_count']} "
        f"identities={exhaustive_result['identity_checks']} "
        f"groups={replay['groups_replayed']} cutoffs={replay['hard_cutoffs_covered']}"
    )


if __name__ == "__main__":
    main()
