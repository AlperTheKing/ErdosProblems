#!/usr/bin/env python3

from __future__ import annotations

from fractions import Fraction
import itertools
import unittest

from affine_relations import (
    AvoidanceAutomaton,
    affine_coefficients,
    first_relation,
    level_stats,
    minimal_rewrite_rules,
    rewrite,
)


class AffineRelationTests(unittest.TestCase):
    def test_coefficients_follow_application_order(self) -> None:
        self.assertEqual(affine_coefficients((2, 5)), (10, 6))
        self.assertEqual(affine_coefficients((2, 5, 5, 2, 3, 2)), (600, 381))

    def test_first_relation_is_exact(self) -> None:
        self.assertIsNone(first_relation(5))
        relation = first_relation(6)
        self.assertEqual(relation, ("255232", "322255", (600, 381)))

    def test_depth_six_statistics(self) -> None:
        stats = level_stats(6)
        self.assertEqual(stats.words, 729)
        self.assertEqual(stats.distinct_maps, 728)
        self.assertEqual(stats.maximum_fiber, 2)
        self.assertEqual(stats.reciprocal_mass, Fraction(886_288_681, 729_000_000))

    def test_rewrites_preserve_maps_and_terminate(self) -> None:
        rules = minimal_rewrite_rules(8)
        self.assertIn(("322255", "255232"), rules)
        word = "53222552"
        normal = rewrite(word, rules)
        self.assertLess(normal, word)
        self.assertEqual(
            affine_coefficients(map(int, word)),
            affine_coefficients(map(int, normal)),
        )
        self.assertEqual(rewrite(normal, rules), normal)

    def test_avoidance_dp_matches_brute_force(self) -> None:
        rules = minimal_rewrite_rules(6)
        forbidden = [lhs for lhs, _ in rules]
        automaton = AvoidanceAutomaton(forbidden)
        masses = automaton.exact_masses(8)
        for length in range(9):
            brute = Fraction()
            for word in itertools.product((2, 3, 5), repeat=length):
                text = "".join(map(str, word))
                if not any(pattern in text for pattern in forbidden):
                    slope, _ = affine_coefficients(word)
                    brute += Fraction(1, slope)
            self.assertEqual(masses[length], brute)

    def test_depth_twelve_rules_remain_supercritical(self) -> None:
        rules = minimal_rewrite_rules(12)
        automaton = AvoidanceAutomaton(lhs for lhs, _ in rules)
        certificate = automaton.uniform_growth_certificate(50)
        self.assertIsNotNone(certificate)
        assert certificate is not None
        self.assertEqual(certificate[0], 50)
        self.assertGreater(certificate[1], 1)


if __name__ == "__main__":
    unittest.main()
