#!/usr/bin/env python3
"""Independent small oracle for the {2,3,5} affine subsystem."""

from __future__ import annotations

from collections import deque
import unittest


SEEDS = {2, 3, 5}
MULTIPLIERS = (2, 3, 5)


def direct_closure(limit: int) -> set[int]:
    current = {x for x in SEEDS if x <= limit}
    while True:
        additions = {
            k * x - 1
            for k in MULTIPLIERS
            for x in current
            if x != k and k * x - 1 <= limit
        }
        enlarged = current | additions
        if enlarged == current:
            return current
        current = enlarged


def reverse_recurrence(limit: int) -> bytearray:
    member = bytearray(limit + 1)
    for seed in SEEDS:
        if seed <= limit:
            member[seed] = 1
    for n in range(6, limit + 1):
        shifted = n + 1
        member[n] = any(
            shifted % k == 0
            and shifted // k != k
            and member[shifted // k]
            for k in MULTIPLIERS
        )
    return member


def residue_closure(modulus: int) -> set[int]:
    seen = {9 % modulus, 14 % modulus}
    queue = deque(seen)
    while queue:
        x = queue.popleft()
        for k in MULTIPLIERS:
            child = (k * x - 1) % modulus
            if child not in seen:
                seen.add(child)
                queue.append(child)
    return seen | {seed % modulus for seed in SEEDS}


class AffineCensusTests(unittest.TestCase):
    def test_recurrence_matches_literal_closure(self) -> None:
        for limit in range(1, 501):
            expected = direct_closure(limit)
            actual = reverse_recurrence(limit)
            self.assertEqual({n for n, bit in enumerate(actual) if bit}, expected)

    def test_given_counts(self) -> None:
        expected = {1000: 212, 10000: 2061, 100000: 20192}
        member = reverse_recurrence(max(expected))
        count = 0
        for n in range(1, len(member)):
            count += member[n]
            if n in expected:
                self.assertEqual(count, expected[n])

    def test_equal_input_sentinels_are_absent(self) -> None:
        member = reverse_recurrence(24)
        self.assertFalse(member[3 * 3 - 1])
        self.assertFalse(member[5 * 5 - 1])

    def test_residue_orbit_counts(self) -> None:
        self.assertEqual(
            [len(residue_closure(30**a)) for a in range(1, 4)],
            [16, 389, 10144],
        )


if __name__ == "__main__":
    unittest.main()
