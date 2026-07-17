"""Exact verifier for the tensor-power affine collision obstruction."""

from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from pathlib import Path


LEFT = "322255"
RIGHT = "255232"
CANONICAL_COUNTS = {"2": 15, "3": 10, "5": 6}


def affine_map(word: str) -> tuple[int, int]:
    """Return (slope, intercept) after applying T_d(x)=d*x-1 left to right."""
    slope, intercept = 1, 0
    for letter in word:
        multiplier = int(letter)
        slope, intercept = multiplier * slope, multiplier * intercept - 1
    return slope, intercept


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-k", type=int, default=5)
    args = parser.parse_args()
    if args.max_k < 1:
        raise ValueError("--max-k must be positive")

    left_map = affine_map(LEFT)
    right_map = affine_map(RIGHT)
    assert left_map == right_map == (600, -381)
    assert Counter(LEFT) == Counter(RIGHT) == Counter({"2": 3, "3": 1, "5": 2})

    q = 2**15 * 3**10 * 5**6
    rows = []
    for k in range(1, args.max_k + 1):
        block_count = 3 * k
        tail = "2" * (6 * k) + "3" * (7 * k)
        words = {
            "".join(blocks) + tail
            for blocks in itertools.product((LEFT, RIGHT), repeat=block_count)
        }
        expected_size = 2**block_count
        assert len(words) == expected_size == 8**k

        maps = {affine_map(word) for word in words}
        assert len(maps) == 1
        slope, intercept = maps.pop()
        assert slope == q**k
        expected_counts = Counter(
            {
                letter: multiplicity * k
                for letter, multiplicity in CANONICAL_COUNTS.items()
            }
        )
        assert all(Counter(word) == expected_counts for word in words)
        rows.append(
            {
                "k": k,
                "distinct_words": len(words),
                "common_slope": str(slope),
                "common_intercept": str(intercept),
                "word_length": 31 * k,
                "letter_counts": {letter: expected_counts[letter] for letter in "235"},
            }
        )

    numerator = 8 * 30**31
    denominator = 31**31
    assert numerator > denominator
    result = {
        "identity": {
            "left": LEFT,
            "right": RIGHT,
            "map": {"slope": left_map[0], "intercept": left_map[1]},
            "letter_counts": dict(Counter(LEFT)),
        },
        "canonical_counts_per_k": CANONICAL_COUNTS,
        "Q": str(q),
        "tensor_family": rows,
        "base_comparison": {
            "claim": "8 > (31/30)^31",
            "ratio_numerator": str(numerator),
            "ratio_denominator": str(denominator),
            "ratio_decimal": numerator / denominator,
        },
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")


if __name__ == "__main__":
    main()
