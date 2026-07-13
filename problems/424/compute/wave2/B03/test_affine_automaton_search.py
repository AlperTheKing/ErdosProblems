#!/usr/bin/env python3

import itertools
import unittest

from affine_automaton_search import (
    LETTERS,
    affine_coefficients,
    affine_orbit_counts,
    exhaustive_selector_search,
    natural_block_cover_search,
)


class AffineAutomatonSearchTests(unittest.TestCase):
    def test_affine_coefficients(self) -> None:
        for length in range(1, 6):
            for word in itertools.product(LETTERS, repeat=length):
                slope, offset = affine_coefficients(word)
                for x in (-7, 0, 1, 9, 14):
                    direct = x
                    for k in word:
                        direct = k * direct - 1
                    self.assertEqual(direct, slope * x - offset)
                self.assertLess(0, offset)
                self.assertLess(offset, slope)

    def test_all_mod_30_selectors_are_subcritical(self) -> None:
        result = exhaustive_selector_search(30)
        self.assertEqual(result["policy_count"], 384)
        self.assertEqual(result["maximum_critical_core_size"], 0)

    def test_natural_block_covers_die(self) -> None:
        for cap in (1, 2, 3):
            result = natural_block_cover_search(30, cap)
            self.assertEqual(result["fixed_point_sizes"], [30, 22, 15, 7, 0])
            self.assertEqual(result["critical_state_residues"], [])

    def test_orbit_census(self) -> None:
        self.assertEqual(
            affine_orbit_counts(100_000, (1_000, 10_000, 100_000)),
            {1_000: 212, 10_000: 2_061, 100_000: 20_192},
        )


if __name__ == "__main__":
    unittest.main()
