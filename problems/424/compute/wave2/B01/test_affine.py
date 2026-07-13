#!/usr/bin/env python3
"""Independent exact checks for the B01 affine-subsystem probes."""

from __future__ import annotations

import unittest

from analyze_affine import generate


def direct_closure(limit: int) -> set[int]:
    current = {value for value in (2, 3, 5) if value <= limit}
    while True:
        enlarged = current | {
            k * value - 1
            for value in current
            for k in (2, 3, 5)
            if value != k and k * value - 1 <= limit
        }
        if enlarged == current:
            return current
        current = enlarged


def affine_word(word: tuple[int, ...]) -> tuple[int, int]:
    slope, subtracted = 1, 0
    for k in word:
        slope, subtracted = k * slope, k * subtracted + 1
    return slope, subtracted


class AffineTests(unittest.TestCase):
    def test_recurrence_matches_literal_closure(self) -> None:
        for limit in range(1, 301):
            expected = direct_closure(limit)
            actual = generate(limit)
            self.assertEqual({n for n, bit in enumerate(actual) if bit}, expected)

    def test_supplied_counts(self) -> None:
        expected = {1_000: 212, 10_000: 2_061, 100_000: 20_192}
        member = generate(max(expected))
        count = 0
        for n, bit in enumerate(member):
            count += bit
            if n in expected:
                self.assertEqual(count, expected[n])

    def test_equal_parent_sentinels(self) -> None:
        member = generate(24)
        self.assertFalse(member[8])
        self.assertFalse(member[24])

    def test_exact_semigroup_relation(self) -> None:
        self.assertEqual(affine_word((2, 5, 5, 2, 3, 2)), (600, 381))
        self.assertEqual(affine_word((3, 2, 2, 2, 5, 5)), (600, 381))


if __name__ == "__main__":
    unittest.main()
