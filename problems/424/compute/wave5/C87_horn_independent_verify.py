#!/usr/bin/env python3
"""Independent exact verifier for the C87 Horn implication graph.

This verifier intentionally does not import the C83/C87 implementations and
does not use a SAT/CP-SAT solver.  It builds product rules by enumerating
allowed input pairs, computes least closures with an event-driven fixed point,
reconstructs every Horn edge, and proves the reported matching defect using
both a matching lower bound and a Hall-set upper bound.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import deque
from pathlib import Path
from typing import Iterable


class VerificationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def require_equal(label: str, actual: object, expected: object) -> None:
    if actual != expected:
        raise VerificationError(
            f"{label} mismatch: actual={actual!r}, expected={expected!r}"
        )


def allowed(value: int) -> bool:
    return value >= 2 and value % 3 != 1


class RuleSystem:
    """Finite prefix of the distinct-input product-minus-one Horn system."""

    def __init__(self, cutoff: int) -> None:
        require(cutoff >= 3, "cutoff must be at least 3")
        self.cutoff = cutoff
        self.values = tuple(value for value in range(2, cutoff + 1) if allowed(value))
        self.value_set = frozenset(self.values)

        rules: list[tuple[int, int, int]] = []
        limit = cutoff + 1
        for left in self.values:
            if left * (left + 1) > limit:
                break
            for right in range(left + 1, limit // left + 1):
                if not allowed(right):
                    continue
                output = left * right - 1
                require(output <= cutoff, "rule enumeration exceeded cutoff")
                require(allowed(output), f"rule produced forbidden output {output}")
                rules.append((output, left, right))

        self.rules = tuple(sorted(rules))
        pairs_by_output: dict[int, list[tuple[int, int]]] = {
            value: [] for value in self.values
        }
        incident: dict[int, list[int]] = {value: [] for value in self.values}
        for index, (output, left, right) in enumerate(self.rules):
            require(left < right, f"non-distinct or unordered rule {(left, right)}")
            pairs_by_output[output].append((left, right))
            incident[left].append(index)
            incident[right].append(index)
        self.pairs_by_output = {
            value: tuple(pairs_by_output[value]) for value in self.values
        }
        self.incident = {value: tuple(incident[value]) for value in self.values}

    def closure(self, seeds: Iterable[int]) -> frozenset[int]:
        """Least fixed point via factor-triggered rule activation."""
        active: set[int] = set()
        queue: deque[int] = deque()
        remaining = [2] * len(self.rules)

        for seed in sorted(set(seeds)):
            require(seed in self.value_set, f"seed {seed} is outside the allowed prefix")
            active.add(seed)
            queue.append(seed)

        while queue:
            factor = queue.popleft()
            for rule_index in self.incident[factor]:
                remaining[rule_index] -= 1
                require(
                    remaining[rule_index] >= 0,
                    f"rule {rule_index} received duplicate activation",
                )
                if remaining[rule_index] != 0:
                    continue
                output = self.rules[rule_index][0]
                if output not in active:
                    active.add(output)
                    queue.append(output)

        self.verify_closed(active)
        return frozenset(active)

    def verify_closed(self, active: set[int] | frozenset[int]) -> None:
        for output, left, right in self.rules:
            if left in active and right in active and output not in active:
                raise VerificationError(
                    f"fixed point is not closed at {left}*{right}-1={output}"
                )

    def image(self, source: set[int] | frozenset[int]) -> frozenset[int]:
        image = {2, 3}
        for output, left, right in self.rules:
            if left in source and right in source:
                image.add(output)
        return frozenset(image)

    def top(self, root: int) -> int:
        value = root
        while 2 * value - 1 <= self.cutoff:
            value = 2 * value - 1
        return value

    def hard_shape(self, root: int) -> bool:
        pairs = self.pairs_by_output[root]
        if root % 2 != 0 or not pairs:
            return False
        if (root + 1) % 3 != 0:
            return True
        seed3_parent = (root + 1) // 3
        return not (allowed(seed3_parent) and seed3_parent != 3)


def hopcroft_karp(
    lefts: tuple[int, ...], adjacency: dict[int, frozenset[int]]
) -> dict[int, int]:
    """Maximum matching as left-to-right pairs."""
    left_match: dict[int, int] = {}
    right_match: dict[int, int] = {}
    infinity = len(lefts) + 1

    def breadth_first() -> tuple[dict[int, int], bool]:
        distance: dict[int, int] = {}
        queue: deque[int] = deque()
        for left in lefts:
            if left not in left_match:
                distance[left] = 0
                queue.append(left)
            else:
                distance[left] = infinity
        found_free_right = False
        while queue:
            left = queue.popleft()
            for right in sorted(adjacency[left]):
                mate = right_match.get(right)
                if mate is None:
                    found_free_right = True
                elif distance[mate] == infinity:
                    distance[mate] = distance[left] + 1
                    queue.append(mate)
        return distance, found_free_right

    def depth_first(left: int, distance: dict[int, int]) -> bool:
        for right in sorted(adjacency[left]):
            mate = right_match.get(right)
            if mate is None or (
                distance.get(mate, infinity) == distance[left] + 1
                and depth_first(mate, distance)
            ):
                left_match[left] = right
                right_match[right] = left
                return True
        distance[left] = infinity
        return False

    while True:
        distance, has_augmenting_layer = breadth_first()
        if not has_augmenting_layer:
            break
        augmented = False
        for left in lefts:
            if left not in left_match and depth_first(left, distance):
                augmented = True
        require(augmented, "Hopcroft-Karp exposed a layer but found no augmenting path")

    require_equal("left/right matching size", len(left_match), len(right_match))
    for left, right in left_match.items():
        require(right in adjacency[left], f"independent matching uses nonedge {left}->{right}")
        require_equal("matching inverse", right_match[right], left)
    return left_match


def alternating_hall_set(
    lefts: tuple[int, ...],
    adjacency: dict[int, frozenset[int]],
    matching: dict[int, int],
) -> tuple[frozenset[int], frozenset[int]]:
    reverse = {right: left for left, right in matching.items()}
    reached_left = {left for left in lefts if left not in matching}
    reached_right: set[int] = set()
    queue: deque[int] = deque(sorted(reached_left))
    while queue:
        left = queue.popleft()
        for right in sorted(adjacency[left]):
            if matching.get(left) == right or right in reached_right:
                continue
            reached_right.add(right)
            mate = reverse.get(right)
            require(mate is not None, "maximum matching has an augmenting path")
            if mate not in reached_left:
                reached_left.add(mate)
                queue.append(mate)
    neighbor_union = set().union(*(adjacency[left] for left in reached_left))
    require_equal("alternating Hall neighborhood", neighbor_union, reached_right)
    return frozenset(reached_left), frozenset(reached_right)


def reconstruct(cutoff: int) -> dict[str, object]:
    system = RuleSystem(cutoff)
    ground = system.closure({2, 3})

    hard_roots = tuple(
        root
        for root in system.values
        if root % 2 == 0
        and root not in ground
        and system.hard_shape(root)
        and system.top(root) not in ground
    )
    target_roots = tuple(
        root
        for root in system.values
        if root % 2 == 0
        and root not in ground
        and not system.hard_shape(root)
        and system.top(root) > root
    )

    hard_tops = {system.top(root) for root in hard_roots}
    adjacency: dict[int, frozenset[int]] = {
        root: frozenset() for root in hard_roots
    }
    mutable_adjacency = {root: set() for root in hard_roots}
    target_data: dict[int, dict[str, object]] = {}
    closure_count = 0

    for target in target_roots:
        target_top = system.top(target)
        if target_top not in ground:
            target_data[target] = {
                "top": target_top,
                "grounded_top": False,
                "supported_hard_tops": [],
            }
            continue

        pairs = system.pairs_by_output[target]
        supported_tops = set(hard_tops)
        for pair in pairs:
            pair_closure = system.closure(set(ground) | set(pair))
            pair_image = system.image(pair_closure)
            supported_tops.intersection_update(pair_image)
            closure_count += 1

        for hard in hard_roots:
            if system.top(hard) in supported_tops:
                mutable_adjacency[hard].add(target)
        target_data[target] = {
            "top": target_top,
            "grounded_top": True,
            "supported_hard_tops": sorted(supported_tops),
        }

    adjacency = {
        hard: frozenset(mutable_adjacency[hard]) for hard in hard_roots
    }
    common_neighbors = (
        set.intersection(*(set(adjacency[hard]) for hard in hard_roots))
        if hard_roots
        else set()
    )
    nested_count = 0
    incomparable_pairs: list[list[int]] = []
    for index, left in enumerate(hard_roots):
        for right in hard_roots[index + 1 :]:
            if adjacency[left] <= adjacency[right] or adjacency[right] <= adjacency[left]:
                nested_count += 1
            else:
                incomparable_pairs.append([left, right])

    matching = hopcroft_karp(hard_roots, adjacency)
    hall_left, hall_right = alternating_hall_set(hard_roots, adjacency, matching)

    return {
        "system": system,
        "ground": ground,
        "hard_roots": hard_roots,
        "target_roots": target_roots,
        "adjacency": adjacency,
        "target_data": target_data,
        "common_neighbors": frozenset(common_neighbors),
        "nested_count": nested_count,
        "incomparable_pairs": incomparable_pairs,
        "matching": matching,
        "hall_left": hall_left,
        "hall_right": hall_right,
        "pair_closures": closure_count,
    }


def verify_claim(input_path: Path) -> dict[str, object]:
    raw = input_path.read_bytes()
    try:
        claim = json.loads(raw)
    except json.JSONDecodeError as error:
        raise VerificationError(f"invalid JSON: {error}") from error
    require(isinstance(claim, dict), "top-level JSON value must be an object")
    require_equal("schema", claim.get("schema"), "C87-horn-implication-v1")
    cutoff = claim.get("cutoff")
    require(isinstance(cutoff, int), "cutoff must be an integer")

    rebuilt = reconstruct(cutoff)
    system = rebuilt["system"]
    require(isinstance(system, RuleSystem), "internal rule-system type failure")
    ground = rebuilt["ground"]
    hard_roots = rebuilt["hard_roots"]
    target_roots = rebuilt["target_roots"]
    adjacency = rebuilt["adjacency"]
    target_data = rebuilt["target_data"]
    require(isinstance(ground, frozenset), "internal ground type failure")
    require(isinstance(hard_roots, tuple), "internal hard-root type failure")
    require(isinstance(target_roots, tuple), "internal target-root type failure")
    require(isinstance(adjacency, dict), "internal adjacency type failure")
    require(isinstance(target_data, dict), "internal target-data type failure")

    expected_adjacency = {
        str(hard): sorted(adjacency[hard]) for hard in hard_roots
    }
    expected_target_data = {
        str(target): target_data[target] for target in target_roots
    }
    edge_count = sum(len(adjacency[hard]) for hard in hard_roots)

    require_equal("grounded size", len(ground), claim.get("grounded_size"))
    require_equal("hard roots", list(hard_roots), claim.get("hard_roots"))
    require_equal("target roots", list(target_roots), claim.get("target_roots"))
    require_equal("edge count", edge_count, claim.get("edge_count"))
    require_equal("adjacency", expected_adjacency, claim.get("adjacency"))
    require_equal("target data", expected_target_data, claim.get("target_data"))
    common_neighbors = rebuilt["common_neighbors"]
    require(isinstance(common_neighbors, frozenset), "internal common-neighbor type failure")
    require_equal(
        "common-neighbor count", len(common_neighbors), claim.get("common_neighbor_count")
    )
    require_equal(
        "common neighbors", sorted(common_neighbors), claim.get("common_neighbors")
    )
    require_equal("nested-pair count", rebuilt["nested_count"], claim.get("nested_hard_pairs"))
    require_equal(
        "incomparable pairs", rebuilt["incomparable_pairs"], claim.get("incomparable_hard_pairs")
    )

    claimed_matching = claim.get("matching")
    require(isinstance(claimed_matching, list), "matching must be a list")
    seen_left: set[int] = set()
    seen_right: set[int] = set()
    for entry in claimed_matching:
        require(
            isinstance(entry, list)
            and len(entry) == 2
            and all(isinstance(value, int) for value in entry),
            f"malformed matching entry {entry!r}",
        )
        left, right = entry
        require(left in adjacency, f"matching has unknown hard root {left}")
        require(right in adjacency[left], f"matching uses nonedge {left}->{right}")
        require(left not in seen_left, f"matching repeats hard root {left}")
        require(right not in seen_right, f"matching repeats target root {right}")
        seen_left.add(left)
        seen_right.add(right)
    require_equal("claimed matching size field", len(claimed_matching), claim.get("matching_size"))

    independent_matching = rebuilt["matching"]
    require(isinstance(independent_matching, dict), "internal matching type failure")
    require_equal("independent maximum matching size", len(independent_matching), 82)
    require_equal("claimed matching lower bound", len(claimed_matching), 82)

    hall = claim.get("hall")
    require(isinstance(hall, dict), "hall field must be an object")
    hall_left_claim = hall.get("hard_set")
    hall_right_claim = hall.get("neighbor_set")
    require(isinstance(hall_left_claim, list), "Hall hard set must be a list")
    require(isinstance(hall_right_claim, list), "Hall neighbor set must be a list")
    require(
        all(isinstance(value, int) for value in hall_left_claim),
        "Hall hard set contains a noninteger",
    )
    require(
        all(isinstance(value, int) for value in hall_right_claim),
        "Hall neighbor set contains a noninteger",
    )
    require_equal("Hall hard-set uniqueness", len(set(hall_left_claim)), len(hall_left_claim))
    require_equal("Hall neighbor uniqueness", len(set(hall_right_claim)), len(hall_right_claim))
    require(set(hall_left_claim) <= set(hard_roots), "Hall set contains an unknown hard root")
    computed_neighbors = set().union(*(adjacency[root] for root in hall_left_claim))
    require_equal("Hall neighborhood", sorted(computed_neighbors), hall_right_claim)
    require_equal("Hall hard count", len(hall_left_claim), 80)
    require_equal("Hall neighbor count", len(hall_right_claim), 79)
    require_equal("Hall deficit field", hall.get("deficit"), 1)
    require_equal("Hall deficit arithmetic", len(hall_left_claim) - len(hall_right_claim), 1)

    # A size-82 matching is a lower bound.  The 80-to-79 Hall set gives the
    # upper bound (83-80)+79=82, so the optimum and maximum deficit are exact.
    hall_upper_bound = len(hard_roots) - len(hall_left_claim) + len(hall_right_claim)
    require_equal("Hall upper bound", hall_upper_bound, 82)
    require_equal("matching/Hall squeeze", len(independent_matching), hall_upper_bound)

    independent_hall_left = rebuilt["hall_left"]
    independent_hall_right = rebuilt["hall_right"]
    require(isinstance(independent_hall_left, frozenset), "internal Hall-left type failure")
    require(isinstance(independent_hall_right, frozenset), "internal Hall-right type failure")
    require_equal("independent Hall hard count", len(independent_hall_left), 80)
    require_equal("independent Hall neighbor count", len(independent_hall_right), 79)
    require_equal("independent Hall hard set", sorted(independent_hall_left), hall_left_claim)
    require_equal("independent Hall neighbor set", sorted(independent_hall_right), hall_right_claim)

    summary: dict[str, object] = {
        "schema": "C87-horn-independent-audit-v1",
        "input_sha256": hashlib.sha256(raw).hexdigest().upper(),
        "cutoff": cutoff,
        "allowed_values": len(system.values),
        "distinct_input_rules": len(system.rules),
        "grounded_size": len(ground),
        "pair_closures_replayed": rebuilt["pair_closures"],
        "hard_roots": len(hard_roots),
        "target_roots": len(target_roots),
        "grounded_top_targets": sum(
            1 for data in target_data.values() if data["grounded_top"]
        ),
        "horn_edges": edge_count,
        "maximum_matching": len(independent_matching),
        "hall_hard_roots": len(hall_left_claim),
        "hall_neighbors": len(hall_right_claim),
        "hall_deficit": 1,
        "hall_upper_bound": hall_upper_bound,
        "status": "VERIFIED_FINITE_OBSTRUCTION",
    }
    canonical = json.dumps(summary, sort_keys=True, separators=(",", ":")).encode("ascii")
    summary["canonical_sha256"] = hashlib.sha256(canonical).hexdigest().upper()
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()
    summary = verify_claim(args.input)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
