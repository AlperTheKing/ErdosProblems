#!/usr/bin/env python3
"""Reproduce Pike's published Z_54 even starter from his two Z_27 starters.

This is a literal, independently executable transcription of Algorithm 1 in
David A. Pike, "A Perfect One-Factorisation of K_56", J. Combin. Des. 27
(2019), 386--390; arXiv:1810.08734v2.  It performs no K_64 search.

The default output is self-contained JSON suitable as input to an independent
even-starter/P1F verifier.  Pair order and the order of pairs are ignored when
the generated output is compared with Pike's published even starter.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterable, NamedTuple


M = 14
STARTER_MODULUS = 2 * M - 1  # 27
EVEN_STARTER_MODULUS = 4 * M - 2  # 54


class TaggedPair(NamedTuple):
    starter: str
    pair: tuple[int, int]
    designation: str


# Table 1 of Pike's paper.  The visual layout gives the first row of S1 as
# High and the second as Low; the complementary S2 rows are Low then High.
S1_HIGH = ((0, 1), (7, 11), (12, 17), (20, 26), (16, 25), (8, 18), (10, 22))
S1_LOW = ((2, 4), (3, 6), (14, 21), (15, 23), (13, 24), (5, 19))
S2_LOW = ((1, 2), (6, 10), (16, 21), (12, 18), (7, 25), (5, 15), (8, 23))
S2_HIGH = ((24, 26), (19, 22), (4, 11), (9, 17), (3, 14), (0, 13))

MISSING_S1 = 9
MISSING_S2 = 20


PUBLISHED_EVEN_STARTER = (
    (36, 17), (44, 12), (39, 45), (18, 35), (8, 50), (23, 15),
    (42, 32), (5, 46), (19, 49), (22, 37), (10, 6), (33, 30),
    (3, 41), (14, 21), (48, 43), (16, 52), (25, 34), (7, 38),
    (11, 31), (4, 2), (29, 28), (1, 27), (0, 40), (13, 24),
    (51, 26), (53, 20),
)


def pair_key(pair: Iterable[int]) -> tuple[int, int]:
    """Canonical key for an unordered pair."""
    x, y = pair
    if x == y:
        raise ValueError(f"pair is not two distinct elements: {(x, y)}")
    return (x, y) if x < y else (y, x)


def cyclic_difference(pair: tuple[int, int], modulus: int) -> int:
    """The representative in 1..floor(modulus/2) of an unsigned difference."""
    x, y = pair
    return min((x - y) % modulus, (y - x) % modulus)


def tagged_source() -> tuple[TaggedPair, ...]:
    return tuple(
        [TaggedPair("S1", pair, "high") for pair in S1_HIGH]
        + [TaggedPair("S1", pair, "low") for pair in S1_LOW]
        + [TaggedPair("S2", pair, "low") for pair in S2_LOW]
        + [TaggedPair("S2", pair, "high") for pair in S2_HIGH]
    )


def validate_starter(
    pairs: tuple[tuple[int, int], ...], missing: int, name: str
) -> None:
    if len(pairs) != M - 1:
        raise AssertionError(f"{name}: expected {M - 1} pairs, got {len(pairs)}")
    vertices = [vertex for pair in pairs for vertex in pair]
    if len(set(vertices)) != 2 * (M - 1):
        raise AssertionError(f"{name}: pairs are not vertex-disjoint")
    if set(vertices) != set(range(STARTER_MODULUS)) - {missing}:
        raise AssertionError(f"{name}: wrong missing vertex")
    directed_differences = {
        difference
        for x, y in pairs
        for difference in ((x - y) % STARTER_MODULUS, (y - x) % STARTER_MODULUS)
    }
    if directed_differences != set(range(1, STARTER_MODULUS)):
        raise AssertionError(f"{name}: not a starter in Z_{STARTER_MODULUS}")


def validate_source() -> None:
    s1 = S1_HIGH + S1_LOW
    s2 = S2_LOW + S2_HIGH
    validate_starter(s1, MISSING_S1, "S1")
    validate_starter(s2, MISSING_S2, "S2")

    all_keys = [pair_key(pair) for pair in s1 + s2]
    if len(set(all_keys)) != len(all_keys):
        raise AssertionError("S1 union S2 contains a repeated unordered pair")

    s1_levels = {
        cyclic_difference(pair, STARTER_MODULUS): level
        for level, pairs in (("high", S1_HIGH), ("low", S1_LOW))
        for pair in pairs
    }
    s2_levels = {
        cyclic_difference(pair, STARTER_MODULUS): level
        for level, pairs in (("low", S2_LOW), ("high", S2_HIGH))
        for pair in pairs
    }
    if set(s1_levels) != set(range(1, M)) or set(s2_levels) != set(range(1, M)):
        raise AssertionError("high/low table does not designate every difference 1..13")
    if any(s1_levels[difference] == s2_levels[difference] for difference in range(1, M)):
        raise AssertionError("S1 and S2 designations are not complementary")


def merge() -> tuple[list[tuple[int, int]], list[dict[str, object]], int]:
    """Execute Pike's Algorithm 1, returning output, trace, and terminal lift."""
    source = tagged_source()
    used: set[tuple[int, int]] = set()
    output: list[tuple[int, int]] = []
    trace: list[dict[str, object]] = []
    a = MISSING_S1 + STARTER_MODULUS

    for iteration in range(1, 2 * M - 1):
        x = a % STARTER_MODULUS
        available = [
            tagged
            for tagged in source
            if x in tagged.pair and pair_key(tagged.pair) not in used
        ]
        if len(available) != 1:
            raise AssertionError(
                f"iteration {iteration}: expected one unused source pair at {x}, "
                f"got {available}"
            )
        tagged = available[0]
        y = tagged.pair[1] if tagged.pair[0] == x else tagged.pair[0]
        difference = cyclic_difference((x, y), STARTER_MODULUS)
        lifts = (y, y + STARTER_MODULUS)
        targets = {(a - difference) % EVEN_STARTER_MODULUS,
                   (a + difference) % EVEN_STARTER_MODULUS}
        intersections = set(lifts) & targets
        if len(intersections) != 1:
            raise AssertionError(
                f"iteration {iteration}: lift/target intersection is {intersections}"
            )
        y_hat = intersections.pop()
        other_lift = lifts[1] if lifts[0] == y_hat else lifts[0]
        b = y_hat if tagged.designation == "low" else other_lift
        next_a = other_lift if b == y_hat else y_hat
        output_pair = (a, b)
        output.append(output_pair)
        used.add(pair_key(tagged.pair))
        trace.append(
            {
                "iteration": iteration,
                "a": a,
                "x": x,
                "starter": tagged.starter,
                "source_pair": list(tagged.pair),
                "designation": tagged.designation,
                "y": y,
                "difference": difference,
                "lifts_of_y": list(lifts),
                "y_hat": y_hat,
                "b": b,
                "output_pair": list(output_pair),
                "next_a": next_a,
            }
        )
        a = next_a

    if len(used) != 2 * M - 2:
        raise AssertionError("merger did not consume every source pair")
    return output, trace, a


def canonical_pairs(pairs: Iterable[tuple[int, int]]) -> list[list[int]]:
    return [list(pair) for pair in sorted(pair_key(pair) for pair in pairs)]


def normalized_pairs_sha256(pairs: Iterable[tuple[int, int]]) -> str:
    encoded = json.dumps(canonical_pairs(pairs), separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def validate_even_starter(pairs: list[tuple[int, int]]) -> list[int]:
    if len(pairs) != 2 * M - 2:
        raise AssertionError("wrong number of output pairs")
    vertices = [vertex for pair in pairs for vertex in pair]
    if len(set(vertices)) != 2 * len(pairs):
        raise AssertionError("output pairs are not vertex-disjoint")
    missing = sorted(set(range(EVEN_STARTER_MODULUS)) - set(vertices))
    if missing != [9, 47]:
        raise AssertionError(f"wrong missing output vertices: {missing}")
    directed_differences = {
        difference
        for x, y in pairs
        for difference in (
            (x - y) % EVEN_STARTER_MODULUS,
            (y - x) % EVEN_STARTER_MODULUS,
        )
    }
    expected = set(range(1, EVEN_STARTER_MODULUS)) - {EVEN_STARTER_MODULUS // 2}
    if directed_differences != expected:
        raise AssertionError("output is not an even starter in Z_54")
    return missing


def build_payload() -> dict[str, object]:
    validate_source()
    generated, trace, terminal_lift = merge()
    if canonical_pairs(generated) != canonical_pairs(PUBLISHED_EVEN_STARTER):
        raise AssertionError("generated output differs from Pike's published even starter")
    missing = validate_even_starter(generated)
    if terminal_lift != MISSING_S2 + STARTER_MODULUS:
        raise AssertionError(f"unexpected terminal lift: {terminal_lift}")

    digest = normalized_pairs_sha256(generated)
    return {
        "schema": "p1f-even-starter-v1",
        "name": "Pike K_56 even starter reproduced from Table 1 by Algorithm 1",
        "modulus": EVEN_STARTER_MODULUS,
        "order": EVEN_STARTER_MODULUS + 2,
        "omitted": missing,
        "pairs": [list(pair) for pair in generated],
        "source": {
            "citation": "David A. Pike, A Perfect One-Factorisation of K_56, arXiv:1810.08734v2, Table 1 and Algorithm 1",
            "starter_modulus": STARTER_MODULUS,
            "even_starter_modulus": EVEN_STARTER_MODULUS,
            "missing_S1": MISSING_S1,
            "missing_S2": MISSING_S2,
            "S1_high": [list(pair) for pair in S1_HIGH],
            "S1_low": [list(pair) for pair in S1_LOW],
            "S2_low": [list(pair) for pair in S2_LOW],
            "S2_high": [list(pair) for pair in S2_HIGH],
        },
        "interpretation": {
            "pair_semantics": "unordered",
            "table_layout": "S1 rows are high then low; complementary S2 rows are low then high",
            "initial_lift_a": MISSING_S1 + STARTER_MODULUS,
            "terminal_lift_a": terminal_lift,
        },
        "generated_pairs_in_algorithm_order": [list(pair) for pair in generated],
        "canonical_generated_pairs": canonical_pairs(generated),
        "published_pairs_in_printed_order": [list(pair) for pair in PUBLISHED_EVEN_STARTER],
        "matches_published_up_to_pair_and_list_order": True,
        "missing_vertices": missing,
        "directed_difference_exception": EVEN_STARTER_MODULUS // 2,
        "normalized_pairs_sha256": digest,
        "algorithm_trace": trace,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        help="write the verifier-ready JSON payload here instead of standard output",
    )
    args = parser.parse_args()
    text = json.dumps(build_payload(), indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(text, end="")
    else:
        args.output.write_text(text, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
