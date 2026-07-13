#!/usr/bin/env python3
"""Exact word-relation census for the {2,3,5} affine subsystem.

A word is written in application order.  Thus (2, 5) means first apply T_2
and then T_5, and has map T_5(T_2(x)).
"""

from __future__ import annotations

import argparse
from collections import Counter, deque
from dataclasses import dataclass
from fractions import Fraction
import json
from typing import Iterable


LETTERS = (2, 3, 5)


def affine_coefficients(word: Iterable[int]) -> tuple[int, int]:
    """Return (slope, offset) for x |-> slope*x-offset."""
    slope, offset = 1, 0
    for letter in word:
        if letter not in LETTERS:
            raise ValueError(f"invalid letter {letter}")
        slope, offset = letter * slope, letter * offset + 1
    return slope, offset


@dataclass(frozen=True)
class LevelStats:
    depth: int
    words: int
    distinct_maps: int
    maximum_fiber: int
    reciprocal_mass: Fraction


def enumerate_words(depth: int) -> list[tuple[int, int, str]]:
    """Enumerate (slope, offset, word) at one exact depth."""
    level = [(1, 0, "")]
    for _ in range(depth):
        level = [
            (letter * slope, letter * offset + 1, word + str(letter))
            for slope, offset, word in level
            for letter in LETTERS
        ]
    return level


def level_stats(depth: int) -> LevelStats:
    fibers = Counter((slope, offset) for slope, offset, _ in enumerate_words(depth))
    mass = sum((Fraction(1, slope) for slope, _ in fibers), Fraction())
    return LevelStats(
        depth=depth,
        words=3**depth,
        distinct_maps=len(fibers),
        maximum_fiber=max(fibers.values(), default=1),
        reciprocal_mass=mass,
    )


def first_relation(max_depth: int) -> tuple[str, str, tuple[int, int]] | None:
    """Return the lexicographically first collision at the first bad depth."""
    for depth in range(1, max_depth + 1):
        canonical: dict[tuple[int, int], str] = {}
        collisions: list[tuple[str, str, tuple[int, int]]] = []
        for slope, offset, word in enumerate_words(depth):
            key = (slope, offset)
            old = canonical.get(key)
            if old is None:
                canonical[key] = word
            elif old != word:
                collisions.append((old, word, key))
        if collisions:
            return min(collisions)
    return None


def minimal_rewrite_rules(max_depth: int) -> list[tuple[str, str]]:
    """Build map-preserving rules lhs -> rhs, with lhs lexicographically larger."""
    rules: list[tuple[str, str]] = []
    for depth in range(1, max_depth + 1):
        level = enumerate_words(depth)
        canonical: dict[tuple[int, int], str] = {}
        for slope, offset, word in level:
            key = (slope, offset)
            canonical[key] = min(word, canonical.get(key, word))
        old_left = tuple(lhs for lhs, _ in rules)
        for slope, offset, word in level:
            rhs = canonical[(slope, offset)]
            if word == rhs or any(lhs in word for lhs in old_left):
                continue
            assert rhs < word
            assert affine_coefficients(map(int, word)) == affine_coefficients(
                map(int, rhs)
            )
            rules.append((word, rhs))
    return rules


def rewrite(word: str, rules: list[tuple[str, str]]) -> str:
    """Apply the first available rule until an irreducible word is reached."""
    while True:
        for lhs, rhs in rules:
            position = word.find(lhs)
            if position >= 0:
                changed = word[:position] + rhs + word[position + len(lhs) :]
                if not changed < word:
                    raise AssertionError("rewrite did not decrease lexicographic order")
                word = changed
                break
        else:
            return word


class AvoidanceAutomaton:
    """Aho-Corasick automaton for words avoiding relation left-hand sides."""

    def __init__(self, forbidden: Iterable[str]) -> None:
        self.next: list[dict[str, int]] = [{}]
        self.terminal = [False]
        for pattern in forbidden:
            state = 0
            for symbol in pattern:
                if symbol not in self.next[state]:
                    self.next[state][symbol] = len(self.next)
                    self.next.append({})
                    self.terminal.append(False)
                state = self.next[state][symbol]
            self.terminal[state] = True

        failure = [0] * len(self.next)
        queue: deque[int] = deque()
        for letter in LETTERS:
            symbol = str(letter)
            if symbol in self.next[0]:
                queue.append(self.next[0][symbol])
            else:
                self.next[0][symbol] = 0
        while queue:
            state = queue.popleft()
            self.terminal[state] |= self.terminal[failure[state]]
            for letter in LETTERS:
                symbol = str(letter)
                child = self.next[state].get(symbol)
                if child is None:
                    self.next[state][symbol] = self.next[failure[state]][symbol]
                    continue
                failure[child] = self.next[failure[state]][symbol]
                queue.append(child)

    def exact_masses(self, max_length: int) -> list[Fraction]:
        """Return sum(P_w^-1) over accepted words at every exact length."""
        vector = [Fraction()] * len(self.next)
        vector[0] = Fraction(1)
        masses = [Fraction(1)]
        for _ in range(max_length):
            following = [Fraction()] * len(self.next)
            for state, value in enumerate(vector):
                if not value or self.terminal[state]:
                    continue
                for letter in LETTERS:
                    target = self.next[state][str(letter)]
                    if not self.terminal[target]:
                        following[target] += value / letter
            vector = following
            masses.append(sum(vector, Fraction()))
        return masses

    def uniform_growth_certificate(
        self, max_length: int
    ) -> tuple[int, Fraction] | None:
        """Find n and q>1 such that A(1)^n * 1 >= q * 1 exactly."""
        vector = [
            Fraction(0) if terminal else Fraction(1)
            for terminal in self.terminal
        ]
        for length in range(1, max_length + 1):
            vector = [
                Fraction(0)
                if self.terminal[state]
                else sum(
                    (
                        vector[self.next[state][str(letter)]] / letter
                        for letter in LETTERS
                        if not self.terminal[self.next[state][str(letter)]]
                    ),
                    Fraction(),
                )
                for state in range(len(self.next))
            ]
            minimum = min(
                value
                for state, value in enumerate(vector)
                if not self.terminal[state]
            )
            if minimum > 1:
                return length, minimum
        return None


def payload(max_depth: int, normal_length: int) -> dict[str, object]:
    relation = first_relation(max_depth)
    rules = minimal_rewrite_rules(max_depth)
    automaton = AvoidanceAutomaton(lhs for lhs, _ in rules)
    masses = automaton.exact_masses(normal_length)
    growth = automaton.uniform_growth_certificate(max(100, normal_length))
    stats = [level_stats(depth) for depth in range(1, max_depth + 1)]
    return {
        "schema_version": 1,
        "alphabet": list(LETTERS),
        "word_order": "application order",
        "first_relation": None
        if relation is None
        else {
            "words": [relation[0], relation[1]],
            "slope": relation[2][0],
            "offset": relation[2][1],
        },
        "levels": [
            {
                "depth": item.depth,
                "words": item.words,
                "distinct_maps": item.distinct_maps,
                "maximum_fiber": item.maximum_fiber,
                "reciprocal_mass": str(item.reciprocal_mass),
                "reciprocal_mass_decimal": float(item.reciprocal_mass),
            }
            for item in stats
        ],
        "minimal_rules": len(rules),
        "avoidance_states": len(automaton.next),
        "uniform_growth_certificate": None
        if growth is None
        else {
            "length": growth[0],
            "minimum_exact": str(growth[1]),
            "minimum_decimal": float(growth[1]),
        },
        "normal_masses": {
            str(index): {
                "exact": str(masses[index]),
                "decimal": float(masses[index]),
            }
            for index in sorted({0, max_depth, normal_length})
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-depth", type=int, default=12)
    parser.add_argument("--normal-length", type=int, default=40)
    args = parser.parse_args()
    if not 1 <= args.max_depth <= 14:
        raise SystemExit("max-depth must lie in [1,14]")
    if args.normal_length < args.max_depth:
        raise SystemExit("normal-length must be at least max-depth")
    print(json.dumps(payload(args.max_depth, args.normal_length), indent=2))


if __name__ == "__main__":
    main()
