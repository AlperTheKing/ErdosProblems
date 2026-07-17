#!/usr/bin/env python3
"""Exact least-closure oracle for the C24 healed-factor gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from array import array
from pathlib import Path


NO_RANK = 65535
MAX_RANK_OFFSET = 8


def is_allowed(value: int) -> bool:
    return value >= 2 and value % 3 != 1


def build_spf(limit: int) -> array:
    spf = array("I", [0]) * (limit + 2)
    primes: list[int] = []
    for value in range(2, limit + 2):
        if spf[value] == 0:
            spf[value] = value
            primes.append(value)
        for prime in primes:
            product = value * prime
            if product > limit + 1 or prime > spf[value]:
                break
            spf[product] = prime
    return spf


def proper_allowed_pairs(product: int, spf: array) -> list[tuple[int, int]]:
    remaining = product
    factors: list[tuple[int, int]] = []
    while remaining > 1:
        prime = spf[remaining]
        exponent = 0
        while remaining % prime == 0:
            remaining //= prime
            exponent += 1
        factors.append((prime, exponent))

    divisors = [1]
    for prime, exponent in factors:
        old = tuple(divisors)
        power = 1
        for _ in range(exponent):
            power *= prime
            divisors.extend(value * power for value in old)

    pairs = []
    for left in divisors:
        if left < 2:
            continue
        right = product // left
        if left >= right:
            continue
        if is_allowed(left) and is_allowed(right):
            pairs.append((left, right))
    pairs.sort()
    return pairs


def generation_tree(
    value: int,
    witness_left: array,
    witness_right: array,
    rank: array,
) -> dict[str, object]:
    if value in (2, 3):
        return {"value": value, "rank": 0, "seed": True}
    left = witness_left[value]
    right = witness_right[value]
    if left == 0 or right == 0 or rank[value] == NO_RANK:
        raise AssertionError(f"no generation witness for {value}")
    return {
        "value": value,
        "rank": rank[value],
        "left": generation_tree(left, witness_left, witness_right, rank),
        "right": generation_tree(right, witness_left, witness_right, rank),
    }


def obstruction_chain(
    value: int,
    obstruction_parent: array,
    obstruction_rank: array,
) -> list[dict[str, int]]:
    chain = []
    current = value
    while current:
        parent = obstruction_parent[current]
        chain.append(
            {
                "value": current,
                "obstruction_rank": obstruction_rank[current],
                "chosen_missing_parent": parent,
            }
        )
        current = parent
    return chain


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=1_000_000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.limit < 54:
        raise SystemExit("--limit must be at least 54")

    started = time.perf_counter()
    limit = args.limit
    spf = build_spf(limit)
    member = bytearray(limit + 1)
    member[2] = member[3] = 1
    generation_rank = array("H", [NO_RANK]) * (limit + 1)
    generation_rank[2] = generation_rank[3] = 0
    witness_left = array("I", [0]) * (limit + 1)
    witness_right = array("I", [0]) * (limit + 1)
    obstruction_rank = array("H", [0]) * (limit + 1)
    obstruction_parent = array("I", [0]) * (limit + 1)

    generated_count = 2
    missing_count = 0
    splitless_count = 0
    reducible_count = 0
    hard_count = 0
    gate_pass_count = 0
    gate_fail_count = 0
    first_hard = 0
    first_failure: dict[str, object] | None = None
    failure_sample: list[dict[str, object]] = []
    hard_rank_counts: list[int] = []
    healed_rank_counts: list[int] = []
    hard_ranked_values: list[tuple[int, int]] = []
    healed_ranked_values: list[tuple[int, int]] = []
    rank_hall_audits = [
        {
            "offset": offset,
            "event_cutoffs_checked": 0,
            "failure_events": 0,
            "first_failure": None,
            "maximum_excess": 0,
            "maximum_excess_cutoff": 0,
            "maximum_excess_depth": 0,
        }
        for offset in range(MAX_RANK_OFFSET + 1)
    ]

    def increment_rank(histogram: list[int], depth: int) -> None:
        if depth >= len(histogram):
            histogram.extend([0] * (depth + 1 - len(histogram)))
        histogram[depth] += 1

    def observe_rank_hall(cutoff: int) -> None:
        depth_count = max(len(hard_rank_counts), len(healed_rank_counts))
        hard_prefix = []
        healed_prefix = []
        running = 0
        for depth in range(depth_count):
            running += hard_rank_counts[depth] if depth < len(hard_rank_counts) else 0
            hard_prefix.append(running)
        running = 0
        for depth in range(depth_count + MAX_RANK_OFFSET):
            running += (
                healed_rank_counts[depth]
                if depth < len(healed_rank_counts)
                else 0
            )
            healed_prefix.append(running)

        for audit in rank_hall_audits:
            audit["event_cutoffs_checked"] += 1
            offset = audit["offset"]
            excess = 0
            excess_depth = 0
            for depth, hard_total in enumerate(hard_prefix):
                candidate = hard_total - healed_prefix[depth + offset]
                if candidate > excess:
                    excess = candidate
                    excess_depth = depth
            if excess <= 0:
                continue
            audit["failure_events"] += 1
            if audit["first_failure"] is None:
                left_values = [
                    value
                    for value, depth in hard_ranked_values
                    if depth <= excess_depth
                ]
                right_values = [
                    value
                    for value, depth in healed_ranked_values
                    if depth <= excess_depth + offset
                ]
                if len(left_values) - len(right_values) != excess:
                    raise AssertionError("rank Hall witness count mismatch")
                audit["first_failure"] = {
                    "cutoff": cutoff,
                    "depth": excess_depth,
                    "excess": excess,
                    "left_count": len(left_values),
                    "neighbor_count": len(right_values),
                    "left_values": left_values,
                    "neighbor_values": right_values,
                }
            if excess > audit["maximum_excess"]:
                audit["maximum_excess"] = excess
                audit["maximum_excess_cutoff"] = cutoff
                audit["maximum_excess_depth"] = excess_depth

    for n in range(4, limit + 1):
        pairs = proper_allowed_pairs(n + 1, spf)
        best_rank = NO_RANK
        best_pair = (0, 0)
        for left, right in pairs:
            if member[left] and member[right]:
                candidate = 1 + max(generation_rank[left], generation_rank[right])
                if candidate < best_rank or (
                    candidate == best_rank and (left, right) < best_pair
                ):
                    best_rank = candidate
                    best_pair = (left, right)

        if best_rank != NO_RANK:
            member[n] = 1
            generation_rank[n] = best_rank
            witness_left[n], witness_right[n] = best_pair
            generated_count += 1
            if n % 2:
                parent = (n + 1) // 2
                if is_allowed(parent) and not member[parent]:
                    increment_rank(healed_rank_counts, obstruction_rank[parent])
                    healed_ranked_values.append(
                        (parent, obstruction_rank[parent])
                    )
                    observe_rank_hall(n)
            continue

        if not is_allowed(n):
            continue

        missing_count += 1
        if not pairs:
            splitless_count += 1
            obstruction_rank[n] = 0
            continue

        reducible_count += 1
        blocking_rank = 0
        blocking_parent = 0
        for left, right in pairs:
            missing = [
                endpoint for endpoint in (left, right) if not member[endpoint]
            ]
            if not missing:
                raise AssertionError(f"hole {n} has an unblocked pair")
            pair_parent = min(
                missing,
                key=lambda endpoint: (obstruction_rank[endpoint], endpoint),
            )
            pair_rank = obstruction_rank[pair_parent]
            if pair_rank > blocking_rank or (
                pair_rank == blocking_rank
                and (blocking_parent == 0 or pair_parent < blocking_parent)
            ):
                blocking_rank = pair_rank
                blocking_parent = pair_parent
        obstruction_rank[n] = blocking_rank + 1
        obstruction_parent[n] = blocking_parent

        is_seed3 = (
            n % 2 == 0
            and (n + 1) % 3 == 0
            and is_allowed((n + 1) // 3)
            and (n + 1) // 3 != 3
        )
        is_hard = n % 2 == 0 and not is_seed3
        if not is_hard:
            continue

        hard_count += 1
        if first_hard == 0:
            first_hard = n
        increment_rank(hard_rank_counts, obstruction_rank[n])
        hard_ranked_values.append((n, obstruction_rank[n]))
        observe_rank_hall(n)

        pair_rows = []
        healed_neighbors: set[int] = set()
        for left, right in pairs:
            endpoint_rows = []
            for endpoint in (left, right):
                child = 2 * endpoint - 1
                generated = bool(member[endpoint])
                child_generated = child <= limit and bool(member[child])
                endpoint_rows.append(
                    {
                        "value": endpoint,
                        "generated": generated,
                        "generation_rank": (
                            generation_rank[endpoint] if generated else None
                        ),
                        "obstruction_rank": (
                            None if generated else obstruction_rank[endpoint]
                        ),
                        "seed2_child": child,
                        "seed2_child_generated": child_generated,
                    }
                )
                if not generated and child_generated:
                    healed_neighbors.add(endpoint)
            pair_rows.append(
                {"left": left, "right": right, "endpoints": endpoint_rows}
            )

        if healed_neighbors:
            gate_pass_count += 1
            continue

        gate_fail_count += 1
        row: dict[str, object] = {
            "n": n,
            "product": n + 1,
            "admissible_pairs": pair_rows,
            "healed_missing_neighbors": [],
            "obstruction_rank": obstruction_rank[n],
            "obstruction_chain": obstruction_chain(
                n, obstruction_parent, obstruction_rank
            ),
        }
        present = sorted(
            {
                endpoint
                for left, right in pairs
                for endpoint in (left, right)
                if member[endpoint]
            }
        )
        row["present_factor_trees"] = [
            generation_tree(
                endpoint, witness_left, witness_right, generation_rank
            )
            for endpoint in present
        ]
        if first_failure is None:
            first_failure = row
        if len(failure_sample) < 16:
            failure_sample.append(row)

    if first_failure is None:
        matching_witness = None
    else:
        cutoff = int(first_failure["n"])
        half = (cutoff + 1) // 2
        half_holes = [
            value
            for value in range(2, half + 1)
            if is_allowed(value) and not member[value]
        ]
        healed_capacity = [
            value for value in half_holes if member[2 * value - 1]
        ]
        odd_reducible = [
            2 * value - 1
            for value in half_holes
            if not member[2 * value - 1]
        ]
        first_failure["cutoff_capacity"] = {
            "half": half,
            "half_holes": half_holes,
            "odd_reducible_holes": odd_reducible,
            "healed_holes": healed_capacity,
            "identity": (
                f"M({half})={len(odd_reducible)}+{len(healed_capacity)}"
            ),
        }
        matching_witness = {
            "cutoff": first_failure["n"],
            "left_set": [first_failure["n"]],
            "neighbor_set": first_failure["healed_missing_neighbors"],
            "hall_deficit": 1,
        }

    bitmap_sha256 = hashlib.sha256(member).hexdigest()
    surviving_offsets = [
        audit["offset"]
        for audit in rank_hall_audits
        if audit["failure_events"] == 0
    ]
    result = {
        "schema_version": 1,
        "limit": limit,
        "closure": (
            "least set generated in increasing order from seeds 2,3 by "
            "distinct allowed factors"
        ),
        "generation_rank": (
            "seeds rank 0; minimum 1+max(parent ranks) over witness pairs"
        ),
        "obstruction_rank": (
            "splitless rank 0; 1+max over pairs of the least missing-endpoint rank"
        ),
        "gate": (
            "every hard hole has a direct missing factor q with generated 2q-1"
        ),
        "counts": {
            "generated": generated_count,
            "allowed_missing": missing_count,
            "splitless": splitless_count,
            "reducible": reducible_count,
            "hard": hard_count,
            "gate_pass_hard": gate_pass_count,
            "gate_fail_hard": gate_fail_count,
        },
        "first_hard": first_hard,
        "first_failure": first_failure,
        "first_matching_hall_witness": matching_witness,
        "rank_hall_relation": (
            "hard hole of obstruction rank r is adjacent to every healed hole "
            "of obstruction rank at most r+offset; nested Hall is equivalent to "
            "H(<=d)<=Q(<=d+offset) for every d"
        ),
        "rank_hall_audits": rank_hall_audits,
        "smallest_surviving_rank_offset": (
            surviving_offsets[0] if surviving_offsets else None
        ),
        "hard_rank_histogram": hard_rank_counts,
        "healed_rank_histogram": healed_rank_counts,
        "failure_sample": failure_sample,
        "member_bitmap_sha256": bitmap_sha256,
        "elapsed_seconds": time.perf_counter() - started,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(
        f"limit={limit} hard={hard_count} pass={gate_pass_count} "
        f"fail={gate_fail_count} first_failure={first_failure['n'] if first_failure else 0}"
    )


if __name__ == "__main__":
    main()
