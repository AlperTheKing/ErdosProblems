"""Exact falsifier for C29's killed-chain local-limit estimate (LL).

The two recurrence-oriented words 552223 and 232552 define the same affine
map t -> 600*t + 218 and have count vector (3,1,2).  Three independent
copies per k, followed by a fixed filler of count (6k,7k,0), give 8^k
distinct words of target count (15k,10k,6k) with one endpoint.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from fractions import Fraction
from itertools import product
from pathlib import Path

Q = {"2": 0, "3": 1, "5": 3}
U = "552223"
V = "232552"


def affine_map(word: str) -> tuple[int, int]:
    """Return (slope, offset) for an outermost-first recurrence word."""
    slope = 1
    offset = 0
    for letter in reversed(word):
        m = int(letter)
        offset = m * offset + Q[letter]
        slope *= m
    return slope, offset


def counts(word: str) -> tuple[int, int, int]:
    c = Counter(word)
    return c["2"], c["3"], c["5"]


def compose(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int]:
    """Affine map left after right."""
    p, d = left
    q, e = right
    return p * q, d + p * e


def repeated_map(base: tuple[int, int], repetitions: int) -> tuple[int, int]:
    out = (1, 0)
    for _ in range(repetitions):
        out = compose(out, base)
    return out


def family_endpoint(k: int) -> tuple[int, int]:
    block = affine_map(U)
    filler = affine_map("2" * (6 * k) + "3" * (7 * k))
    return compose(repeated_map(block, 3 * k), filler)


def exhaustive_check(k: int) -> dict[str, object]:
    expected = family_endpoint(k)
    expected_counts = (15 * k, 10 * k, 6 * k)
    seen_words: set[str] = set()
    for choices in product((U, V), repeat=3 * k):
        word = "".join(choices) + "2" * (6 * k) + "3" * (7 * k)
        assert word not in seen_words
        seen_words.add(word)
        assert counts(word) == expected_counts
        assert affine_map(word) == expected
    return {
        "k": k,
        "words_checked": len(seen_words),
        "target_counts": list(expected_counts),
        "slope": str(expected[0]),
        "endpoint": str(expected[1]),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-enumerated-k", type=int, default=5)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    assert affine_map(U) == (600, 218)
    assert affine_map(V) == (600, 218)
    assert counts(U) == (3, 1, 2)
    assert counts(V) == (3, 1, 2)

    # rho = 8*(30/31)^31 is the exponential violation factor in LL.
    rho = Fraction(8 * 30**31, 31**31)
    assert rho > 1

    checks = [exhaustive_check(k) for k in range(1, args.max_enumerated_k + 1)]
    for row in checks:
        k = int(row["k"])
        assert int(row["words_checked"]) == 8**k
        assert int(row["slope"]) == 2 ** (15 * k) * 3 ** (10 * k) * 5 ** (6 * k)

    payload = {
        "identity": {
            "word_u": U,
            "word_v": V,
            "map": [600, 218],
            "counts": [3, 1, 2],
        },
        "family": {
            "collision_blocks": "3k",
            "filler_counts": ["6k", "7k", "0"],
            "target_counts": ["15k", "10k", "6k"],
            "fiber_lower_bound": "8^k",
        },
        "ll_violation_base": {
            "numerator": str(rho.numerator),
            "denominator": str(rho.denominator),
            "decimal": float(rho),
            "greater_than_one": rho > 1,
        },
        "exhaustive_checks": checks,
    }
    source_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    payload["script_sha256"] = source_hash
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
