#!/usr/bin/env python3
"""Independent trial-division checks for the C23 grounded Horn audit."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LIMIT = 500
INFINITY = 10**9


def allowed(value: int) -> bool:
    return value >= 2 and value % 3 != 1


def pairs(value: int) -> list[tuple[int, int]]:
    product = value + 1
    result = []
    left = 2
    while left * left < product:
        if product % left == 0:
            right = product // left
            if allowed(left) and allowed(right):
                result.append((left, right))
        left += 1
    return result


PAIRS = {
    value: pairs(value)
    for value in range(2, LIMIT + 1)
    if allowed(value)
}


def hard_shape(value: int) -> bool:
    local = PAIRS[value]
    if value % 2 or not local:
        return False
    if (value + 1) % 3:
        return True
    parent = (value + 1) // 3
    return not (allowed(parent) and parent != 3)


def forward_closed(members: set[int], limit: int = LIMIT) -> bool:
    for value, local in PAIRS.items():
        if value > limit:
            continue
        for left, right in local:
            if left in members and right in members and value not in members:
                return False
    return True


def support_core(members: set[int], limit: int = LIMIT) -> set[int]:
    result = {value for value in (2, 3) if value <= limit}
    for value in range(4, limit + 1):
        if not allowed(value):
            continue
        if any(
            left in members and right in members
            for left, right in PAIRS[value]
        ):
            result.add(value)
    return result


def ascending_closure(limit: int = LIMIT) -> set[int]:
    result = {2, 3}
    for value in range(4, limit + 1):
        if not allowed(value):
            continue
        if any(
            left in result and right in result
            for left, right in PAIRS[value]
        ):
            result.add(value)
    return result


def stage_sequence(limit: int = LIMIT) -> list[set[int]]:
    current = {
        value for value in range(2, limit + 1) if allowed(value)
    }
    stages = [current]
    while True:
        following = support_core(current, limit)
        stages.append(following)
        if following == current:
            return stages
        if not following < current:
            raise AssertionError("support stages are not strictly descending")
        current = following


def hard_and_q(
    members: set[int],
    cutoff: int,
) -> tuple[list[int], list[int]]:
    hard = [
        value
        for value in range(2, cutoff + 1)
        if allowed(value) and hard_shape(value) and value not in members
    ]
    q_children = [
        child
        for parent in range(2, (cutoff + 1) // 2 + 1)
        if allowed(parent)
        for child in [2 * parent - 1]
        if parent not in members and child in members
    ]
    return hard, q_children


def explicit_death_ranks(
    stages: list[set[int]],
    limit: int = LIMIT,
) -> dict[int, int]:
    ranks = {}
    for value in range(2, limit + 1):
        if not allowed(value):
            continue
        ranks[value] = INFINITY
        for stage in range(1, len(stages)):
            if value not in stages[stage]:
                ranks[value] = stage
                break
    return ranks


class GroundedHornChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.stages = stage_sequence()
        cls.generated = ascending_closure()
        cls.death = explicit_death_ranks(cls.stages)

    def test_stabilization_is_least_closure(self) -> None:
        self.assertEqual(self.stages[-1], self.generated)
        self.assertTrue(all(forward_closed(stage) for stage in self.stages))

    def test_death_rank_recurrence(self) -> None:
        recursive = {}
        for value in range(2, LIMIT + 1):
            if not allowed(value):
                continue
            if value in self.generated:
                recursive[value] = INFINITY
            elif not PAIRS[value]:
                recursive[value] = 1
            else:
                recursive[value] = 1 + max(
                    min(recursive[left], recursive[right])
                    for left, right in PAIRS[value]
                )
        self.assertEqual(recursive, self.death)

    def test_chain_threshold_motion(self) -> None:
        for current, following in zip(self.stages, self.stages[1:]):
            removed = current - following
            seen_roots = set()
            for value in removed:
                root = 1 + (value - 1) // ((value - 1) & -(value - 1))
                self.assertNotIn(root, seen_roots)
                seen_roots.add(root)
                if value % 2:
                    self.assertNotIn((value + 1) // 2, current)
                child = 2 * value - 1
                if child <= LIMIT:
                    self.assertIn(child, following)

    def test_stage_contraction_and_threshold_identity(self) -> None:
        for current, following in zip(self.stages, self.stages[1:]):
            removed = current - following
            for cutoff in range(2, LIMIT + 1):
                old_h, old_q = hard_and_q(current, cutoff)
                new_h, new_q = hard_and_q(following, cutoff)
                old_slack = len(old_q) - len(old_h)
                new_slack = len(new_q) - len(new_h)
                half = (cutoff + 1) // 2
                exposed = [
                    value
                    for value in removed
                    if half < value <= cutoff
                    and (value % 2 or hard_shape(value))
                ]
                helpers = [
                    value
                    for value in removed
                    if value <= half
                    and value % 2 == 0
                    and not hard_shape(value)
                ]
                self.assertGreaterEqual(old_slack, len(exposed))
                self.assertEqual(
                    new_slack,
                    old_slack - len(exposed) + len(helpers),
                )
                self.assertGreaterEqual(new_slack, 0)

    def test_transition_identity_for_all_small_sources(self) -> None:
        small_limit = 26
        optional = [
            value
            for value in range(4, small_limit + 1)
            if allowed(value)
        ]
        local_pairs = {
            value: PAIRS[value]
            for value in range(2, small_limit + 1)
            if allowed(value)
        }
        closed_count = 0
        for mask in range(1 << len(optional)):
            source = {2, 3}
            source.update(
                value
                for index, value in enumerate(optional)
                if mask & (1 << index)
            )
            if any(
                left in source
                and right in source
                and value not in source
                for value, local in local_pairs.items()
                for left, right in local
            ):
                continue
            closed_count += 1
            image = support_core(source, small_limit)
            removed = source - image
            for cutoff in range(2, small_limit + 1):
                source_h, source_q = hard_and_q(source, cutoff)
                image_h, image_q = hard_and_q(image, cutoff)
                half = (cutoff + 1) // 2
                removed_odd = sum(
                    value <= cutoff and value % 2
                    for value in removed
                )
                removed_hard = sum(
                    value <= cutoff
                    and value % 2 == 0
                    and hard_shape(value)
                    for value in removed
                )
                births = sum(value <= half for value in removed)
                self.assertEqual(
                    len(image_q),
                    len(source_q) - removed_odd + births,
                )
                self.assertEqual(
                    len(image_h),
                    len(source_h) + removed_hard,
                )
        self.assertGreater(closed_count, 100)

    def test_rank_falsifiers(self) -> None:
        cutoff = 362
        hard_rank_prefix = [
            value
            for value in range(2, cutoff + 1)
            if allowed(value)
            and hard_shape(value)
            and value not in self.generated
            and self.death[value] <= 3
        ]
        q_rank_prefix = [
            parent
            for parent in range(2, (cutoff + 1) // 2 + 1)
            if allowed(parent)
            and parent not in self.generated
            and 2 * parent - 1 in self.generated
            and self.death[parent] <= 3
        ]
        self.assertEqual(len(hard_rank_prefix), 11)
        self.assertEqual(len(q_rank_prefix), 10)

        layer_cutoff = 74
        hard_layer = [
            value
            for value in range(2, layer_cutoff + 1)
            if allowed(value)
            and hard_shape(value)
            and value not in self.generated
            and self.death[value] == 3
        ]
        q_layer = [
            parent
            for parent in range(2, (layer_cutoff + 1) // 2 + 1)
            if allowed(parent)
            and parent not in self.generated
            and 2 * parent - 1 in self.generated
            and self.death[parent] == 3
        ]
        self.assertEqual(hard_layer, [54, 74])
        self.assertEqual(q_layer, [21])

    def test_forward_closure_is_essential(self) -> None:
        predecessor = {2, 3, 5, 54}
        following = support_core(predecessor, 54)
        old_h, old_q = hard_and_q(predecessor, 54)
        new_h, new_q = hard_and_q(following, 54)
        self.assertFalse(forward_closed(predecessor, 54))
        self.assertGreaterEqual(len(old_q), len(old_h))
        self.assertLess(len(new_q), len(new_h))

    def test_large_rank_artifacts(self) -> None:
        million = json.loads((ROOT / "result_1e6.json").read_text())
        self.assertEqual(million["generated"], 457599)
        self.assertEqual(million["hard_holes"], 45583)
        self.assertEqual(million["final_healed_parents"], 67537)
        self.assertTrue(million["stagewise_gate"]["passed"])
        self.assertTrue(
            million["chain_threshold_transition_gate"]["passed"]
        )
        self.assertTrue(
            all(
                row["no_nonhard_helper"]["first_failure"] is None
                for row in million[
                    "chain_threshold_transition_gate"
                ]["rows"]
            )
        )

        ten_million = json.loads(
            (ROOT / "result_1e7.json").read_text()
        )
        self.assertEqual(ten_million["generated"], 4952270)
        self.assertEqual(ten_million["hard_holes"], 392961)
        self.assertEqual(ten_million["final_healed_parents"], 637270)
        self.assertTrue(ten_million["stagewise_gate"]["passed"])

    def test_selected_cutoff_sat_certificate(self) -> None:
        result = json.loads(
            (ROOT / "selected_preservation_5000.json").read_text()
        )
        self.assertEqual(result["status"], "OPTIMAL")
        self.assertEqual(result["objective_excess"], 0)
        threshold = result["threshold_shift_identity"]
        self.assertEqual(
            threshold["new_slack_Q_minus_H"],
            threshold["old_slack_Q_minus_H"]
            - len(threshold["dangerous_moved_boundaries"])
            - len(threshold["dangerous_removed_hard_roots"])
            + len(threshold["helpful_removed_nonhard_roots"]),
        )

    def test_unconditional_image_certificates(self) -> None:
        selected = json.loads(
            (ROOT / "unconditional_selected_5000.json").read_text()
        )
        self.assertEqual(selected["status"], "OPTIMAL")
        self.assertEqual(selected["objective_excess"], 0)
        self.assertEqual(selected["best_objective_bound"], 0)
        self.assertIsNone(
            selected["sorted_event_dominance"]["first_violation"]
        )

        endpoint = json.loads(
            (ROOT / "unconditional_endpoint_10000.json").read_text()
        )
        self.assertEqual(endpoint["status"], "OPTIMAL")
        self.assertEqual(endpoint["objective_excess"], -68)
        self.assertEqual(endpoint["best_objective_bound"], -68)

        cutoff = endpoint["selected_cutoff"]
        source = set(endpoint["previous_members"])
        image = set(endpoint["following_members"])
        source_hard = []
        source_q = []
        replay_image = {2, 3}
        for value in range(2, cutoff + 1):
            if not allowed(value):
                continue
            local_pairs = pairs(value)
            supported = any(
                left in source and right in source
                for left, right in local_pairs
            )
            if value > 3 and supported:
                replay_image.add(value)
            for left, right in local_pairs:
                self.assertFalse(
                    left in source
                    and right in source
                    and value not in source
                )
            local_hard = (
                value % 2 == 0
                and bool(local_pairs)
                and (
                    (value + 1) % 3 != 0
                    or not (
                        allowed((value + 1) // 3)
                        and (value + 1) // 3 != 3
                    )
                )
            )
            if local_hard and value not in source:
                source_hard.append(value)
            if value % 2:
                parent = (value + 1) // 2
                if parent not in source and value in source:
                    source_q.append(value)
        self.assertEqual(replay_image, image)

        removed = source - image
        credit_keys = sorted(
            source_q
            + [
                2 * value - 1
                for value in removed
                if 2 * value - 1 <= cutoff
            ]
        )
        demand_keys = list(source_hard)
        for value in removed:
            if value % 2:
                demand_keys.append(value)
                continue
            local_pairs = pairs(value)
            if (
                local_pairs
                and (
                    (value + 1) % 3 != 0
                    or not (
                        allowed((value + 1) // 3)
                        and (value + 1) // 3 != 3
                    )
                )
            ):
                demand_keys.append(value)
        demand_keys.sort()
        self.assertEqual(
            credit_keys,
            endpoint["sorted_event_dominance"]["credit_keys"],
        )
        self.assertEqual(
            demand_keys,
            endpoint["sorted_event_dominance"]["demand_keys"],
        )
        self.assertEqual(
            len(demand_keys) - len(credit_keys),
            endpoint["objective_excess"],
        )
        self.assertTrue(
            all(
                credit <= demand
                for credit, demand in zip(credit_keys, demand_keys)
            )
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
