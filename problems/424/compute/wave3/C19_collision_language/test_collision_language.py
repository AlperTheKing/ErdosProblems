#!/usr/bin/env python3

from __future__ import annotations

from fractions import Fraction
import itertools
import unittest

from collision_language import (
    PAIRS,
    LinearState,
    affine_coefficients,
    block_census_payload,
    c25_family_block,
    enumerate_map_normal_forms,
    enumerate_paired_blocks,
    first_nonseed_witnesses,
    fixed_orbit_membership,
    is_orbit_collision_witness,
    orbit_depth_census,
    primitive_block_keys,
    projected_collision_census,
    residual_state,
    residual_state_census,
    two_three_ratio_bounds,
)


class CollisionLanguageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.map_levels = enumerate_map_normal_forms(8)
        cls.blocks = {
            pair: enumerate_paired_blocks(cls.map_levels, *pair) for pair in PAIRS
        }

    def test_linear_automaton_closes_exact_first_blocks(self) -> None:
        examples = {
            (2, 3): ("53", "35", (15, 4), (15, 6)),
            (2, 5): ("532225", "225523", (600, 196), (600, 490)),
            (3, 5): ("522252", "255222", (400, 153), (400, 255)),
        }
        for (i, j), (left, right, left_map, right_map) in examples.items():
            self.assertEqual(affine_coefficients(left), left_map)
            self.assertEqual(affine_coefficients(right), right_map)
            self.assertEqual(residual_state(i, j, left, right), LinearState(j, i, 0))

    def test_known_orbit_collision_witnesses(self) -> None:
        self.assertTrue(is_orbit_collision_witness(2, 3, 14, "25", 9, "3222"))
        self.assertTrue(is_orbit_collision_witness(2, 5, 9, "3", 9, "222"))
        self.assertTrue(is_orbit_collision_witness(3, 5, 9, "55", 14, "333"))

    def test_normal_forms_reproduce_first_map_collision(self) -> None:
        depth_six = self.map_levels[6]
        self.assertEqual(len(depth_six), 728)
        normal = depth_six[(600, 381)]
        self.assertEqual(normal.word, "255232")
        self.assertEqual(normal.fiber, 2)

    def test_block_census_through_depth_eight(self) -> None:
        expected = {
            (2, 3): {
                2: (1, 1, 1),
                4: (2, 2, 1),
                5: (4, 4, 4),
                6: (5, 5, 2),
                7: (15, 15, 7),
                8: (37, 37, 28),
            },
            (2, 5): {6: (1, 1, 1), 7: (4, 4, 4), 8: (14, 14, 14)},
            (3, 5): {6: (2, 2, 2), 7: (4, 4, 4), 8: (18, 18, 18)},
        }
        for pair, depth_expected in expected.items():
            self.assertFalse(self.blocks[pair][0])
            rows = {
                row["depth"]: (
                    row["states"],
                    row["word_pairs"],
                    row["primitive_states"],
                )
                for row in block_census_payload(self.blocks[pair])
            }
            self.assertEqual(rows, depth_expected)

    def test_depth_four_23_composite_is_detected(self) -> None:
        primitives = primitive_block_keys(self.blocks[(2, 3)], 4)
        self.assertEqual(primitives, {(60, 11)})
        self.assertIn((225, 32), self.blocks[(2, 3)][4])

    def test_coaccessible_linear_state_census(self) -> None:
        expected = {
            (2, 3): (41, 461),
            (2, 5): (11, 146),
            (3, 5): (38, 184),
        }
        for pair, (states, prefixes) in expected.items():
            last = residual_state_census(self.blocks[pair], *pair)[-1]
            self.assertEqual(last["maximum_block_depth"], 8)
            self.assertEqual(last["coaccessible_linear_states"], states)
            self.assertEqual(last["canonical_prefix_occurrences"], prefixes)

    def test_c25_family_is_exact_for_many_parameters(self) -> None:
        states = set()
        for m in range(4, 16):
            for q in range(m - 3):
                block = c25_family_block(m, q)
                self.assertEqual(block.depth, m + 3)
                self.assertEqual(block.slope, 45 * 2**m)
                self.assertEqual(block.slope % 5, 0)
                self.assertNotEqual(block.slope % 25, 0)
                states.add((block.slope, block.shift))
        self.assertEqual(len(states), sum(range(1, 13)))

    def test_two_three_ratio_bounds_match_brute_force(self) -> None:
        for twos in range(5):
            for threes in range(5):
                if twos + threes == 0:
                    continue
                words = set(
                    itertools.permutations((2,) * twos + (3,) * threes)
                )
                ratios = []
                for word in words:
                    slope, offset = affine_coefficients(word)
                    ratios.append(Fraction(offset, slope))
                minimum, maximum = two_three_ratio_bounds(twos, threes)
                self.assertEqual(minimum, min(ratios))
                self.assertEqual(maximum, max(ratios))
                self.assertLess(maximum, 2 * minimum)

    def test_no_25_block_without_letter_five_through_depth_ten(self) -> None:
        for depth in range(1, 11):
            maps = {}
            for word_tuple in itertools.product((2, 3), repeat=depth):
                word = "".join(map(str, word_tuple))
                maps[affine_coefficients(word)] = word
            for (slope, offset), _word in maps.items():
                if offset % 2:
                    continue
                self.assertNotIn((slope, 5 * (offset // 2)), maps)

    def test_orbit_normal_form_census_and_first_witnesses(self) -> None:
        rows, canonical = orbit_depth_census(self.map_levels[:5])
        self.assertEqual(
            rows[-1],
            {
                "maximum_word_depth": 4,
                "raw_representations": 245,
                "distinct_orbit_values": 242,
                "pairs": {
                    "23": {"distinct_t": 5, "raw_representation_pairs": 5},
                    "25": {"distinct_t": 6, "raw_representation_pairs": 6},
                    "35": {"distinct_t": 4, "raw_representation_pairs": 4},
                },
            },
        )
        witnesses = first_nonseed_witnesses(canonical)
        self.assertEqual(witnesses["23"]["t"], 67)
        self.assertEqual(witnesses["25"]["t"], 13)
        self.assertEqual(witnesses["35"]["t"], 73)

    def test_projected_collision_counts_through_one_thousand(self) -> None:
        member = fixed_orbit_membership(5_000)
        census = projected_collision_census(1_000, member, self.blocks)
        self.assertEqual(census["23"]["collision_t"], 15)
        self.assertEqual(census["25"]["collision_t"], 34)
        self.assertEqual(census["35"]["collision_t"], 25)
        for pair in ("23", "25", "35"):
            self.assertEqual(census[pair]["coverage"][-1]["covered_t"], 0)


if __name__ == "__main__":
    unittest.main()
