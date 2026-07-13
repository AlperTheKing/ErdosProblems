#!/usr/bin/env python3
"""Exact collision-language census for the {2,3,5} affine orbit.

Words are in application order.  For example, ``53`` means first apply
T_5 and then T_3.  Every equality and census quantity in this module uses
integer or rational arithmetic.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from functools import reduce
from itertools import zip_longest
import json
from math import gcd
from typing import Iterable


LETTERS = (2, 3, 5)
ROOTS = (9, 14)
PAIRS = ((2, 3), (2, 5), (3, 5))


def affine_coefficients(word: Iterable[int] | str) -> tuple[int, int]:
    """Return ``(P,C)`` for the affine map ``x -> P*x-C``."""
    slope, offset = 1, 0
    for raw_letter in word:
        letter = int(raw_letter)
        if letter not in LETTERS:
            raise ValueError(f"invalid letter {letter}")
        slope, offset = letter * slope, letter * offset + 1
    return slope, offset


def affine_value(root: int, word: Iterable[int] | str) -> int:
    slope, offset = affine_coefficients(word)
    return slope * root - offset


@dataclass(frozen=True)
class LinearState:
    """Normalized exact relation ``A*x-B*y=C``."""

    left: int
    right: int
    constant: int

    def __post_init__(self) -> None:
        if self.left <= 0 or self.right <= 0:
            raise ValueError("relation coefficients must be positive")
        common = reduce(gcd, (self.left, self.right, abs(self.constant)))
        if common != 1:
            raise ValueError("LinearState must be primitive")

    @staticmethod
    def normalized(left: int, right: int, constant: int) -> "LinearState":
        common = reduce(gcd, (left, right, abs(constant)))
        return LinearState(left // common, right // common, constant // common)

    def strip(
        self, left_letter: int | None, right_letter: int | None
    ) -> "LinearState":
        """Strip zero, one, or two outer affine letters exactly.

        Substituting ``x=T_k(x')`` adds ``A`` to the right side and
        multiplies ``A`` by ``k``.  Substituting ``y=T_l(y')`` subtracts
        ``B`` and multiplies ``B`` by ``l``.
        """
        if left_letter is None and right_letter is None:
            raise ValueError("at least one letter must be stripped")
        if left_letter is not None and left_letter not in LETTERS:
            raise ValueError(f"invalid left letter {left_letter}")
        if right_letter is not None and right_letter not in LETTERS:
            raise ValueError(f"invalid right letter {right_letter}")

        left = self.left
        right = self.right
        constant = self.constant
        if left_letter is not None:
            constant += left
            left *= left_letter
        if right_letter is not None:
            constant -= right
            right *= right_letter
        return LinearState.normalized(left, right, constant)


def residual_state(i: int, j: int, left_word: str, right_word: str) -> LinearState:
    """Read a representation pair from outermost to innermost."""
    state = LinearState.normalized(j, i, 0)
    for left, right in zip_longest(reversed(left_word), reversed(right_word)):
        state = state.strip(
            None if left is None else int(left),
            None if right is None else int(right),
        )
    return state


def is_orbit_collision_witness(
    i: int,
    j: int,
    left_root: int,
    left_word: str,
    right_root: int,
    right_word: str,
) -> bool:
    """Check ``j*F_u(a)=i*F_v(b)`` in two independent exact forms."""
    left_value = affine_value(left_root, left_word)
    right_value = affine_value(right_root, right_word)
    direct = j * left_value == i * right_value
    state = residual_state(i, j, left_word, right_word)
    residual = (
        state.left * left_root - state.right * right_root == state.constant
    )
    if direct != residual:
        raise AssertionError("direct and residual collision checks disagree")
    return direct


@dataclass(frozen=True)
class MapNormalForm:
    word: str
    fiber: int


@dataclass(frozen=True)
class PairedBlock:
    """A universal collision morphism ``t -> slope*t-shift``."""

    depth: int
    slope: int
    shift: int
    left_word: str
    right_word: str
    left_fiber: int
    right_fiber: int

    @property
    def word_pair_fiber(self) -> int:
        return self.left_fiber * self.right_fiber


def enumerate_map_normal_forms(max_depth: int) -> list[dict[tuple[int, int], MapNormalForm]]:
    """Enumerate canonical affine maps and exact word fibers by depth."""
    if max_depth < 0:
        raise ValueError("max_depth must be nonnegative")
    levels: list[dict[tuple[int, int], MapNormalForm]] = []
    raw_level = [(1, 0, "")]
    for depth in range(max_depth + 1):
        fibers: dict[tuple[int, int], tuple[str, int]] = {}
        for slope, offset, word in raw_level:
            key = (slope, offset)
            old = fibers.get(key)
            if old is None:
                fibers[key] = (word, 1)
            else:
                fibers[key] = (min(old[0], word), old[1] + 1)
        levels.append(
            {
                key: MapNormalForm(word=word, fiber=fiber)
                for key, (word, fiber) in fibers.items()
            }
        )
        if depth != max_depth:
            raw_level = [
                (letter * slope, letter * offset + 1, word + str(letter))
                for slope, offset, word in raw_level
                for letter in LETTERS
            ]
    return levels


def paired_blocks_at_depth(
    maps: dict[tuple[int, int], MapNormalForm], depth: int, i: int, j: int
) -> dict[tuple[int, int], PairedBlock]:
    """Return all distinct paired affine states at one depth."""
    if depth == 0:
        return {}
    blocks: dict[tuple[int, int], PairedBlock] = {}
    for (slope, left_offset), left_normal in maps.items():
        if left_offset % i:
            continue
        shift = left_offset // i
        right_normal = maps.get((slope, j * shift))
        if right_normal is None:
            continue
        block = PairedBlock(
            depth=depth,
            slope=slope,
            shift=shift,
            left_word=left_normal.word,
            right_word=right_normal.word,
            left_fiber=left_normal.fiber,
            right_fiber=right_normal.fiber,
        )
        state = residual_state(i, j, block.left_word, block.right_word)
        if state != LinearState.normalized(j, i, 0):
            raise AssertionError("paired block is not an automaton loop")
        blocks[(slope, shift)] = block
    return blocks


def enumerate_paired_blocks(
    map_levels: list[dict[tuple[int, int], MapNormalForm]], i: int, j: int
) -> list[dict[tuple[int, int], PairedBlock]]:
    return [
        paired_blocks_at_depth(maps, depth, i, j)
        for depth, maps in enumerate(map_levels)
    ]


def primitive_block_keys(
    block_levels: list[dict[tuple[int, int], PairedBlock]], depth: int
) -> set[tuple[int, int]]:
    """Find states not factoring as a composition of two nonidentity blocks."""
    primitive: set[tuple[int, int]] = set()
    for slope, shift in block_levels[depth]:
        decomposable = False
        for first_depth in range(1, depth):
            second_depth = depth - first_depth
            for first_slope, first_shift in block_levels[first_depth]:
                if slope % first_slope:
                    continue
                second_slope = slope // first_slope
                second_shift = shift - second_slope * first_shift
                if (second_slope, second_shift) in block_levels[second_depth]:
                    decomposable = True
                    break
            if decomposable:
                break
        if not decomposable:
            primitive.add((slope, shift))
    return primitive


def block_census_payload(
    block_levels: list[dict[tuple[int, int], PairedBlock]]
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for depth, blocks in enumerate(block_levels):
        if not blocks:
            continue
        primitive = primitive_block_keys(block_levels, depth)
        reciprocal_mass = sum(
            (Fraction(1, block.slope) for block in blocks.values()), Fraction()
        )
        first = min(
            blocks.values(),
            key=lambda block: (
                block.slope,
                block.shift,
                block.left_word,
                block.right_word,
            ),
        )
        rows.append(
            {
                "depth": depth,
                "states": len(blocks),
                "word_pairs": sum(
                    block.word_pair_fiber for block in blocks.values()
                ),
                "maximum_word_pair_fiber": max(
                    block.word_pair_fiber for block in blocks.values()
                ),
                "primitive_states": len(primitive),
                "reciprocal_mass": str(reciprocal_mass),
                "first": {
                    "slope": first.slope,
                    "shift": first.shift,
                    "left_word": first.left_word,
                    "right_word": first.right_word,
                },
            }
        )
    return rows


def residual_state_census(
    block_levels: list[dict[tuple[int, int], PairedBlock]], i: int, j: int
) -> list[dict[str, int]]:
    """Count exact linear states on canonical accepting block paths."""
    start = LinearState.normalized(j, i, 0)
    states = {start}
    prefix_occurrences = 0
    rows: list[dict[str, int]] = []
    for depth, blocks in enumerate(block_levels):
        if not blocks:
            continue
        for block in blocks.values():
            state = start
            for left, right in zip(
                reversed(block.left_word), reversed(block.right_word)
            ):
                state = state.strip(int(left), int(right))
                states.add(state)
                prefix_occurrences += 1
            if state != start:
                raise AssertionError("canonical block path did not return to start")
        maximum_bits = max(
            max(
                state.left.bit_length(),
                state.right.bit_length(),
                abs(state.constant).bit_length(),
            )
            for state in states
        )
        rows.append(
            {
                "maximum_block_depth": depth,
                "coaccessible_linear_states": len(states),
                "canonical_prefix_occurrences": prefix_occurrences,
                "maximum_coefficient_bits": maximum_bits,
            }
        )
    return rows


def c25_family_words(m: int, q: int) -> tuple[str, str]:
    """The explicit primitive C25 family from Proposition 4.1."""
    if m < 4 or not 0 <= q <= m - 4:
        raise ValueError("require m >= 4 and 0 <= q <= m-4")
    left = "5" + "2" * q + "3" + "2" * (m - q) + "3"
    right = "2" * (q + 2) + "53" + "2" * (m - q - 4) + "322"
    return left, right


def c25_family_block(m: int, q: int) -> PairedBlock:
    left_word, right_word = c25_family_words(m, q)
    left_slope, left_offset = affine_coefficients(left_word)
    right_slope, right_offset = affine_coefficients(right_word)
    expected_slope = 45 * 2**m
    expected_shift = 9 * 2**m - 3 * 2 ** (m - q - 1) - 1
    exact = (
        left_slope == right_slope == expected_slope
        and left_offset == 2 * expected_shift
        and right_offset == 5 * expected_shift
    )
    if not exact:
        raise AssertionError("C25 family formula failed exact coefficient check")
    if residual_state(2, 5, left_word, right_word) != LinearState(5, 2, 0):
        raise AssertionError("C25 family word pair does not close the automaton")
    return PairedBlock(
        depth=m + 3,
        slope=expected_slope,
        shift=expected_shift,
        left_word=left_word,
        right_word=right_word,
        left_fiber=1,
        right_fiber=1,
    )


def two_three_ratio_bounds(number_of_twos: int, number_of_threes: int) -> tuple[Fraction, Fraction]:
    """Minimum and maximum of C/P for a fixed {2,3} multiset."""
    if number_of_twos < 0 or number_of_threes < 0:
        raise ValueError("letter counts must be nonnegative")
    if number_of_twos + number_of_threes == 0:
        return Fraction(), Fraction()
    a = number_of_twos
    b = number_of_threes
    maximum = Fraction(1) - Fraction(1, 2 ** (a + 1)) * (
        1 + Fraction(1, 3**b)
    )
    minimum = (
        Fraction(1, 2)
        + Fraction(1, 2 * 3**b)
        - Fraction(1, 2**a * 3**b)
    )
    if not maximum < 2 * minimum:
        raise AssertionError("the exact two-three ratio bound failed")
    return minimum, maximum


def fixed_orbit_membership(limit: int) -> bytearray:
    """Compute the fixed subsystem by its exact Boolean recurrence."""
    if limit < 0:
        raise ValueError("limit must be nonnegative")
    member = bytearray(limit + 1)
    for seed in (2, 3, 5):
        if seed <= limit:
            member[seed] = 1
    for value in range(6, limit + 1):
        shifted = value + 1
        for letter in LETTERS:
            if shifted % letter:
                continue
            parent = shifted // letter
            if parent != letter and member[parent]:
                member[value] = 1
                break
    return member


def orbit_depth_census(
    map_levels: list[dict[tuple[int, int], MapNormalForm]]
) -> tuple[list[dict[str, object]], dict[int, tuple[int, int, str]]]:
    """Census actual orbit values, deduplicating all map/root collisions."""
    multiplicity: Counter[int] = Counter({2: 1, 3: 1, 5: 1})
    canonical: dict[int, tuple[int, int, str]] = {
        2: (-1, 2, "seed"),
        3: (-1, 3, "seed"),
        5: (-1, 5, "seed"),
    }
    rows: list[dict[str, object]] = []
    for depth, maps in enumerate(map_levels):
        for (slope, offset), normal in maps.items():
            for root in ROOTS:
                value = slope * root - offset
                multiplicity[value] += normal.fiber
                candidate = (depth, root, normal.word)
                old = canonical.get(value)
                if old is None or candidate < old:
                    canonical[value] = candidate

        pair_rows: dict[str, dict[str, int]] = {}
        for i, j in PAIRS:
            distinct = 0
            raw_pairs = 0
            for value, left_fiber in multiplicity.items():
                if value % i:
                    continue
                right_fiber = multiplicity.get(j * (value // i), 0)
                if right_fiber:
                    distinct += 1
                    raw_pairs += left_fiber * right_fiber
            pair_rows[f"{i}{j}"] = {
                "distinct_t": distinct,
                "raw_representation_pairs": raw_pairs,
            }
        rows.append(
            {
                "maximum_word_depth": depth,
                "raw_representations": sum(multiplicity.values()),
                "distinct_orbit_values": len(multiplicity),
                "pairs": pair_rows,
            }
        )
    return rows, canonical


def projected_collision_census(
    t_limit: int,
    member: bytearray,
    all_block_levels: dict[tuple[int, int], list[dict[tuple[int, int], PairedBlock]]],
) -> dict[str, object]:
    """Count projected collision integers and images of safe smaller collisions."""
    output: dict[str, object] = {}
    for i, j in PAIRS:
        collision = bytearray(t_limit + 1)
        values: list[int] = []
        for t in range(1, t_limit + 1):
            if member[i * t] and member[j * t]:
                collision[t] = 1
                values.append(t)

        covered = bytearray(t_limit + 1)
        coverage_rows: list[dict[str, int]] = []
        block_count = 0
        for depth, blocks in enumerate(all_block_levels[(i, j)]):
            if not blocks:
                continue
            block_count += len(blocks)
            for slope, shift in blocks:
                maximum_parent = (t_limit + shift) // slope
                for parent in values:
                    if parent > maximum_parent:
                        break
                    if i * parent <= 5 or j * parent <= 5:
                        continue
                    image = slope * parent - shift
                    if image > t_limit:
                        continue
                    if not collision[image]:
                        raise AssertionError("paired block image failed membership check")
                    covered[image] = 1
            coverage_rows.append(
                {
                    "maximum_block_depth": depth,
                    "block_states": block_count,
                    "covered_t": sum(covered),
                    "not_covered_t": len(values) - sum(covered),
                }
            )
        output[f"{i}{j}"] = {
            "collision_t": len(values),
            "first_t": values[:20],
            "coverage": coverage_rows,
        }
    return output


def first_nonseed_witnesses(
    canonical: dict[int, tuple[int, int, str]]
) -> dict[str, object]:
    witnesses: dict[str, object] = {}
    support = set(canonical)
    for i, j in PAIRS:
        candidates = sorted(
            value // i
            for value in support
            if value % i == 0 and value // i > 1 and j * (value // i) in support
        )
        if not candidates:
            continue
        t = candidates[0]
        left_depth, left_root, left_word = canonical[i * t]
        right_depth, right_root, right_word = canonical[j * t]
        if left_word == "seed" or right_word == "seed":
            raise AssertionError("unexpected seed in nonseed witness")
        if not is_orbit_collision_witness(
            i, j, left_root, left_word, right_root, right_word
        ):
            raise AssertionError("canonical collision witness failed")
        witnesses[f"{i}{j}"] = {
            "t": t,
            "left": {"root": left_root, "word": left_word, "depth": left_depth},
            "right": {
                "root": right_root,
                "word": right_word,
                "depth": right_depth,
            },
        }
    return witnesses


def payload(max_depth: int, t_limit: int) -> dict[str, object]:
    map_levels = enumerate_map_normal_forms(max_depth)
    all_blocks = {
        pair: enumerate_paired_blocks(map_levels, *pair) for pair in PAIRS
    }
    depth_rows, canonical = orbit_depth_census(map_levels)

    family_checks = []
    for m in range(4, max(5, max_depth - 2)):
        for q in range(m - 3):
            block = c25_family_block(m, q)
            family_checks.append((block.slope, block.shift))

    result: dict[str, object] = {
        "schema_version": 1,
        "alphabet": list(LETTERS),
        "word_order": "application order",
        "linear_state": {
            "meaning": "A*x-B*y=C, normalized by gcd",
            "start_23": [3, 2, 0],
            "start_25": [5, 2, 0],
            "start_35": [5, 3, 0],
            "paired_transition": "(A,B,C)->(A*k,B*l,C+A-B), then gcd-normalize",
        },
        "map_levels": [
            {
                "depth": depth,
                "words": 3**depth,
                "distinct_maps": len(maps),
                "maximum_map_fiber": max(normal.fiber for normal in maps.values()),
            }
            for depth, maps in enumerate(map_levels)
        ],
        "block_census": {
            f"{i}{j}": block_census_payload(all_blocks[(i, j)])
            for i, j in PAIRS
        },
        "linear_state_census": {
            f"{i}{j}": residual_state_census(all_blocks[(i, j)], i, j)
            for i, j in PAIRS
        },
        "orbit_depth_census": depth_rows,
        "first_nonseed_witnesses": first_nonseed_witnesses(canonical),
        "c25_primitive_family": {
            "verified_states": len(set(family_checks)),
            "maximum_verified_m": max(4, max_depth - 3),
            "cumulative_lower_bound_through_depth": max(
                0, (max_depth - 6) * (max_depth - 5) // 2
            ),
            "all_depth_reciprocal_mass": "1/180",
        },
    }
    if t_limit:
        member = fixed_orbit_membership(5 * t_limit)
        result["projected_census"] = {
            "t_limit": t_limit,
            "pairs": projected_collision_census(
                t_limit, member, all_blocks
            ),
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-depth", type=int, default=12)
    parser.add_argument("--t-limit", type=int, default=1_000_000)
    args = parser.parse_args()
    if not 1 <= args.max_depth <= 13:
        raise SystemExit("max-depth must lie in [1,13]")
    if args.t_limit < 0:
        raise SystemExit("t-limit must be nonnegative")
    print(json.dumps(payload(args.max_depth, args.t_limit), indent=2))


if __name__ == "__main__":
    main()
