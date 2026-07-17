#!/usr/bin/env python3
"""Exact grounded-Horn rank audit for the C16 hole contraction.

For allowed n, let S_0 contain every allowed integer and recursively put

    S_{k+1} = {2, 3} union
              {ab - 1 : a < b, a,b in S_k, a,b allowed}.

Because every admissible factor of n + 1 is smaller than n, the intersection
of the S_k is exactly the least generated set G. A hole's death rank is the
least k for which it is absent from S_k.

This program tests the C16 hard-hole/healed-parent inequality not only at G,
but at every finite approximant S_k. It also tests the weaker rank-filtered
terminal statement obtained by retaining only holes of death rank at most k.
All membership, ranks, and prefix inequalities are computed with integers.
"""

from __future__ import annotations

import argparse
import json
import time
from array import array
from collections import Counter
from pathlib import Path


INFINITY = 65535


def allowed(value: int) -> bool:
    return value >= 2 and value % 3 != 1


def smallest_prime_factors(limit: int) -> array:
    spf = array("I", range(limit + 1))
    for prime in range(2, int(limit**0.5) + 1):
        if spf[prime] != prime:
            continue
        start = prime * prime
        for multiple in range(start, limit + 1, prime):
            if spf[multiple] == multiple:
                spf[multiple] = prime
    return spf


def divisors(value: int, spf: array) -> list[int]:
    result = [1]
    remaining = value
    while remaining > 1:
        prime = spf[remaining]
        power = 1
        old_size = len(result)
        while remaining % prime == 0:
            remaining //= prime
            power *= prime
            for index in range(old_size):
                result.append(result[index] * power)
    return result


def admissible_pairs(value: int, spf: array) -> list[tuple[int, int]]:
    product = value + 1
    result = []
    for left in divisors(product, spf):
        if left < 2:
            continue
        right = product // left
        if left >= right:
            continue
        if allowed(left) and allowed(right):
            result.append((left, right))
    result.sort()
    return result


def is_hard_shape(value: int, pairs: list[tuple[int, int]]) -> bool:
    if value % 2 != 0 or not pairs:
        return False
    if (value + 1) % 3 != 0:
        return True
    parent = (value + 1) // 3
    return not (allowed(parent) and parent != 3)


def prefix_gate(
    hard_events: list[tuple[int, int]],
    q_events: list[tuple[int, int, int]],
    stage: int,
    mode: str,
) -> dict:
    """Check Q-prefix minus H-prefix for one rank threshold."""
    changes: list[tuple[int, int, str, int]] = []
    for value, death in hard_events:
        include = death <= stage
        if mode in {"stage_layer", "terminal_layer"}:
            include = death == stage
        if include:
            changes.append((value, -1, "H", death))
    for child, parent_death, child_death in q_events:
        if mode in {"stage", "stage_layer"}:
            include = parent_death <= stage < child_death
        elif mode == "terminal_filtered":
            include = parent_death <= stage and child_death == INFINITY
        elif mode == "terminal_layer":
            include = parent_death == stage and child_death == INFINITY
        else:
            raise ValueError(mode)
        if include:
            changes.append((child, 1, "Q", parent_death))

    changes.sort()
    surplus = 0
    minimum = 0
    minimum_x = 2
    first_failure = None
    hard_count = 0
    q_count = 0
    for value, delta, kind, rank in changes:
        surplus += delta
        if kind == "H":
            hard_count += 1
        else:
            q_count += 1
        if surplus < minimum:
            minimum = surplus
            minimum_x = value
        if surplus < 0 and first_failure is None:
            first_failure = {
                "X": value,
                "surplus": surplus,
                "event": kind,
                "rank": rank,
                "H": hard_count,
                "Q": q_count,
            }
    return {
        "stage": stage,
        "H": hard_count,
        "Q": q_count,
        "terminal_surplus": surplus,
        "minimum_surplus": minimum,
        "minimum_X": minimum_x,
        "first_failure": first_failure,
    }


def transition_gate(
    hard_events: list[tuple[int, int]],
    q_events: list[tuple[int, int, int]],
    death: array,
    limit: int,
    stage: int,
) -> dict:
    """Replay one seed-2-chain threshold shift S_stage -> S_(stage+1)."""
    predicted_changes = array("i", [0]) * (limit + 1)
    no_helper_changes = array("i", [0]) * (limit + 1)
    following_changes = array("i", [0]) * (limit + 1)
    hard_lookup = bytearray(limit + 1)
    for value, value_death in hard_events:
        hard_lookup[value] = 1
        if value_death <= stage:
            predicted_changes[value] -= 1
            no_helper_changes[value] -= 1
        if value_death <= stage + 1:
            following_changes[value] -= 1
    for child, parent_death, child_death in q_events:
        if parent_death <= stage < child_death:
            predicted_changes[child] += 1
            no_helper_changes[child] += 1
        if parent_death <= stage + 1 < child_death:
            following_changes[child] += 1

    removed_odd_thresholds = 0
    removed_hard_roots = 0
    removed_nonhard_roots = 0
    removal_rank = stage + 1
    for value in range(2, limit + 1):
        if death[value] != removal_rank:
            continue
        child = 2 * value - 1
        if value % 2:
            removed_odd_thresholds += 1
            predicted_changes[value] -= 1
            no_helper_changes[value] -= 1
            if child <= limit:
                predicted_changes[child] += 1
                no_helper_changes[child] += 1
        elif hard_lookup[value]:
            removed_hard_roots += 1
            predicted_changes[value] -= 1
            no_helper_changes[value] -= 1
            if child <= limit:
                predicted_changes[child] += 1
                no_helper_changes[child] += 1
        else:
            removed_nonhard_roots += 1
            if child <= limit:
                predicted_changes[child] += 1

    predicted = 0
    following = 0
    no_helper = 0
    minimum = 0
    minimum_x = 2
    no_helper_minimum = 0
    no_helper_minimum_x = 2
    first_failure = None
    no_helper_first_failure = None
    no_helper_first_tight_event_x = None
    no_helper_last_tight_event_x = None
    for value in range(2, limit + 1):
        predicted += predicted_changes[value]
        following += following_changes[value]
        no_helper += no_helper_changes[value]
        if predicted != following:
            raise AssertionError(
                f"threshold identity failed at stage={stage}, X={value}: "
                f"{predicted} != {following}"
            )
        if predicted < minimum:
            minimum = predicted
            minimum_x = value
        if predicted < 0 and first_failure is None:
            first_failure = {"X": value, "slack": predicted}
        if no_helper < no_helper_minimum:
            no_helper_minimum = no_helper
            no_helper_minimum_x = value
        if no_helper < 0 and no_helper_first_failure is None:
            no_helper_first_failure = {"X": value, "slack": no_helper}
        if (
            no_helper_changes[value] != 0
            and no_helper == 0
            and value > 2
        ):
            if no_helper_first_tight_event_x is None:
                no_helper_first_tight_event_x = value
            no_helper_last_tight_event_x = value

    return {
        "from_stage": stage,
        "to_stage": stage + 1,
        "removed_odd_thresholds": removed_odd_thresholds,
        "removed_hard_roots": removed_hard_roots,
        "removed_nonhard_roots": removed_nonhard_roots,
        "terminal_slack": predicted,
        "minimum_slack": minimum,
        "minimum_X": minimum_x,
        "first_failure": first_failure,
        "no_nonhard_helper": {
            "inequality": (
                "H_stage(X)+next exposed odd/hard thresholds "
                "in (floor((X+1)/2),X] <= Q_stage(X)"
            ),
            "terminal_slack": no_helper,
            "minimum_slack": no_helper_minimum,
            "minimum_X": no_helper_minimum_x,
            "first_failure": no_helper_first_failure,
            "first_tight_event_X": no_helper_first_tight_event_x,
            "last_tight_event_X": no_helper_last_tight_event_x,
        },
    }


def audit(limit: int) -> dict:
    started = time.perf_counter()
    spf = smallest_prime_factors(limit + 1)
    member = bytearray(limit + 1)
    death = array("H", [0]) * (limit + 1)
    generation_rank = array("H", [INFINITY]) * (limit + 1)
    member[2] = 1
    member[3] = 1
    death[2] = INFINITY
    death[3] = INFINITY
    generation_rank[2] = 0
    generation_rank[3] = 0

    hard_events: list[tuple[int, int]] = []
    splitless_holes = 0
    reducible_holes = 0
    max_pair_count = 0
    pair_count_arg = 0

    for value in range(4, limit + 1):
        if not allowed(value):
            continue
        pairs = admissible_pairs(value, spf)
        if len(pairs) > max_pair_count:
            max_pair_count = len(pairs)
            pair_count_arg = value

        best_generation_rank = INFINITY
        for left, right in pairs:
            if member[left] and member[right]:
                candidate = 1 + max(
                    generation_rank[left], generation_rank[right]
                )
                if candidate < best_generation_rank:
                    best_generation_rank = candidate

        if best_generation_rank != INFINITY:
            member[value] = 1
            death[value] = INFINITY
            generation_rank[value] = best_generation_rank
            continue

        if not pairs:
            death[value] = 1
            splitless_holes += 1
            continue

        blocking_round = 0
        for left, right in pairs:
            blocker = min(death[left], death[right])
            if blocker == INFINITY:
                raise AssertionError(
                    f"hole {value} has generated witness {left},{right}"
                )
            blocking_round = max(blocking_round, blocker)
        if blocking_round + 1 >= INFINITY:
            raise OverflowError(f"death rank overflow at {value}")
        death[value] = blocking_round + 1
        reducible_holes += 1
        if is_hard_shape(value, pairs):
            hard_events.append((value, death[value]))

    q_events: list[tuple[int, int, int]] = []
    for parent in range(2, (limit + 1) // 2 + 1):
        if not allowed(parent) or death[parent] == INFINITY:
            continue
        child = 2 * parent - 1
        if child > limit:
            continue
        child_death = death[child]
        if child_death == 0:
            raise AssertionError(f"unranked seed-2 child {child}")
        if death[parent] < child_death:
            q_events.append((child, death[parent], child_death))

    finite_deaths = [
        death[value]
        for value in range(2, limit + 1)
        if allowed(value) and death[value] != INFINITY
    ]
    maximum_death = max(finite_deaths, default=0)

    stage_gates = [
        prefix_gate(hard_events, q_events, stage, "stage")
        for stage in range(1, maximum_death + 1)
    ]
    terminal_filtered_gates = [
        prefix_gate(hard_events, q_events, stage, "terminal_filtered")
        for stage in range(1, maximum_death + 1)
    ]
    stage_layer_gates = [
        prefix_gate(hard_events, q_events, stage, "stage_layer")
        for stage in range(1, maximum_death + 1)
    ]
    terminal_layer_gates = [
        prefix_gate(hard_events, q_events, stage, "terminal_layer")
        for stage in range(1, maximum_death + 1)
    ]
    transition_gates = [
        transition_gate(
            hard_events,
            q_events,
            death,
            limit,
            stage,
        )
        for stage in range(0, maximum_death)
    ]

    final_q = [
        (child, parent_death)
        for child, parent_death, child_death in q_events
        if child_death == INFINITY
    ]
    terminal_gate = stage_gates[-1] if stage_gates else {
        "stage": 0,
        "H": 0,
        "Q": 0,
        "terminal_surplus": 0,
        "minimum_surplus": 0,
        "minimum_X": 2,
        "first_failure": None,
    }

    member_count = sum(member)
    allowed_count = sum(allowed(value) for value in range(2, limit + 1))
    death_histogram = Counter(finite_deaths)
    hard_death_histogram = Counter(rank for _, rank in hard_events)
    final_q_death_histogram = Counter(rank for _, rank in final_q)
    final_q_generation_histogram = Counter(
        generation_rank[child] for child, _ in final_q
    )

    def first_failed(rows: list[dict]) -> dict | None:
        return next((row for row in rows if row["first_failure"]), None)

    result = {
        "schema_version": 1,
        "limit": limit,
        "approximants": (
            "S_0=all allowed; S_(k+1)=seeds union supported outputs in S_k"
        ),
        "death_rank_recurrence": (
            "splitless=1; hole=1+max_pairs min(death of missing endpoints)"
        ),
        "allowed": allowed_count,
        "generated": member_count,
        "holes": allowed_count - member_count,
        "splitless_holes": splitless_holes,
        "reducible_holes": reducible_holes,
        "hard_holes": len(hard_events),
        "final_healed_parents": len(final_q),
        "maximum_death_rank": maximum_death,
        "maximum_generation_rank": max(
            generation_rank[value]
            for value in range(2, limit + 1)
            if member[value]
        ),
        "maximum_pair_count": {
            "count": max_pair_count,
            "value": pair_count_arg,
        },
        "terminal_gate": terminal_gate,
        "stagewise_gate": {
            "passed": first_failed(stage_gates) is None,
            "first_failed_stage": first_failed(stage_gates),
            "rows": stage_gates,
        },
        "terminal_rank_filtered_gate": {
            "passed": first_failed(terminal_filtered_gates) is None,
            "first_failed_stage": first_failed(terminal_filtered_gates),
            "rows": terminal_filtered_gates,
        },
        "stage_exact_layer_gate": {
            "passed": first_failed(stage_layer_gates) is None,
            "first_failed_stage": first_failed(stage_layer_gates),
            "rows": stage_layer_gates,
        },
        "terminal_exact_layer_gate": {
            "passed": first_failed(terminal_layer_gates) is None,
            "first_failed_stage": first_failed(terminal_layer_gates),
            "rows": terminal_layer_gates,
        },
        "chain_threshold_transition_gate": {
            "identity": (
                "boundary c stays or moves to 2c-1; removed even roots "
                "create boundary 2r-1"
            ),
            "passed": all(
                row["first_failure"] is None for row in transition_gates
            ),
            "rows": transition_gates,
        },
        "death_histogram": dict(sorted(death_histogram.items())),
        "hard_death_histogram": dict(sorted(hard_death_histogram.items())),
        "final_q_parent_death_histogram": dict(
            sorted(final_q_death_histogram.items())
        ),
        "final_q_child_generation_histogram": dict(
            sorted(final_q_generation_histogram.items())
        ),
        "hard_sample": [
            {"value": value, "death_rank": rank}
            for value, rank in hard_events[:64]
        ],
        "final_q_sample": [
            {
                "parent": (child + 1) // 2,
                "child": child,
                "parent_death_rank": parent_rank,
                "child_generation_rank": generation_rank[child],
            }
            for child, parent_rank in final_q[:64]
        ],
        "transient_q_sample": [
            {
                "parent": (child + 1) // 2,
                "child": child,
                "parent_death_rank": parent_rank,
                "child_death_rank": child_rank,
            }
            for child, parent_rank, child_rank in q_events[:64]
            if child_rank != INFINITY
        ],
        "elapsed_seconds": time.perf_counter() - started,
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.limit < 4:
        raise ValueError("limit must be at least 4")

    result = audit(args.limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2) + "\n",
        encoding="ascii",
    )
    print(
        f"limit={result['limit']} generated={result['generated']} "
        f"hard={result['hard_holes']} Q={result['final_healed_parents']} "
        f"max_death={result['maximum_death_rank']} "
        f"stagewise={result['stagewise_gate']['passed']} "
        f"rank_filtered={result['terminal_rank_filtered_gate']['passed']} "
        f"elapsed={result['elapsed_seconds']:.3f}s"
    )


if __name__ == "__main__":
    main()
