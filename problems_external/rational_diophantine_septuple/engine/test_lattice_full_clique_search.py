from __future__ import annotations

import unittest
from fractions import Fraction

from lattice_full_clique_search import (
    find_four_clique,
    fraction_mod,
    modular_square_possible,
    quadratic_residues,
)


class FullCliqueSearchTests(unittest.TestCase):
    def test_fraction_mod_skips_vanishing_denominator(self) -> None:
        self.assertIsNone(fraction_mod(Fraction(1, 5), 5))

    def test_modular_filter_keeps_rational_square_pair(self) -> None:
        primes = (101, 103, 107, 109)
        residues = tuple(quadratic_residues(prime) for prime in primes)
        left = Fraction(3, 2)
        right = Fraction(2)
        left_mod = tuple(fraction_mod(left, prime) for prime in primes)
        right_mod = tuple(fraction_mod(right, prime) for prime in primes)
        possible, rejecting_prime, usable = modular_square_possible(
            left_mod, right_mod, primes, residues
        )
        self.assertTrue(possible)  # left*right+1 = 4
        self.assertIsNone(rejecting_prime)
        self.assertEqual(usable, len(primes))

    def test_quadratic_residue_set_includes_zero(self) -> None:
        self.assertIn(0, quadratic_residues(101))

    def test_four_clique_detection_requires_all_six_edges(self) -> None:
        adjacency = [set() for _ in range(5)]
        for left in range(4):
            for right in range(left + 1, 4):
                adjacency[left].add(right)
                adjacency[right].add(left)
        adjacency[0].add(4)
        adjacency[4].add(0)
        clique, triangle_count = find_four_clique(adjacency)
        self.assertEqual(clique, [0, 1, 2, 3])
        self.assertGreaterEqual(triangle_count, 1)

    def test_no_false_four_clique_from_diamond(self) -> None:
        adjacency = [set() for _ in range(4)]
        for left, right in ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3)):
            adjacency[left].add(right)
            adjacency[right].add(left)
        clique, _ = find_four_clique(adjacency)
        self.assertIsNone(clique)


if __name__ == "__main__":
    unittest.main()
