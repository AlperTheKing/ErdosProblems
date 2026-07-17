"""Exact checks for the C36 fixed-block orbit-compression audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from fractions import Fraction
from math import factorial, log
from pathlib import Path
from typing import Iterator


Q = {"2": 0, "3": 1, "5": 3}
U = "552223"
V = "232552"
P0 = Fraction(2 * 12**3 * 7 * 3**2, 31**6)
CANONICAL_SLOPE = 2**15 * 3**10 * 5**6


def affine_outermost(word: str) -> tuple[int, int]:
    """Return L_{w_1} o ... o L_{w_n} as (slope, offset)."""
    slope = 1
    offset = 0
    for letter in word:
        offset += slope * Q[letter]
        slope *= int(letter)
    return slope, offset


def affine_chronological(word: str) -> tuple[int, int]:
    """Apply the displayed letters from left to right, for orientation audit."""
    slope = 1
    offset = 0
    for letter in word:
        multiplier = int(letter)
        offset = multiplier * offset + Q[letter]
        slope *= multiplier
    return slope, offset


def counts(word: str) -> tuple[int, int, int]:
    frequencies = Counter(word)
    return frequencies["2"], frequencies["3"], frequencies["5"]


def falling(value: int, length: int) -> int:
    product = 1
    for shift in range(length):
        product *= value - shift
    return product


def block_probability(n2: int, n3: int, n5: int) -> Fraction:
    total = n2 + n3 + n5
    return Fraction(
        2 * falling(n2, 3) * n3 * falling(n5, 2),
        falling(total, 6),
    )


def exact_conditional_minimum(k: int) -> dict[str, object]:
    """Minimize over every feasible exact history before a selected block."""
    block_count = k // 2
    best: Fraction | None = None
    witness: tuple[int, int, int, int] | None = None

    for block_index in range(1, block_count + 1):
        exposed = 6 * (block_index - 1)
        for used2 in range(exposed + 1):
            for used3 in range(exposed - used2 + 1):
                used5 = exposed - used2 - used3
                if used2 > 15 * k or used3 > 10 * k or used5 > 6 * k:
                    continue
                probability = block_probability(
                    15 * k - used2,
                    10 * k - used3,
                    6 * k - used5,
                )
                if best is None or probability < best:
                    best = probability
                    witness = (block_index, used2, used3, used5)

    assert best is not None and witness is not None
    assert best >= P0
    return {
        "k": k,
        "selected_blocks": block_count,
        "minimum": f"{best.numerator}/{best.denominator}",
        "minimum_decimal": float(best),
        "witness_block_and_used_2_3_5": list(witness),
    }


def multiset_words(n2: int, n3: int, n5: int) -> Iterator[str]:
    remaining = {"2": n2, "3": n3, "5": n5}
    letters: list[str] = []

    def generate() -> Iterator[str]:
        if sum(remaining.values()) == 0:
            yield "".join(letters)
            return
        for letter in ("2", "3", "5"):
            if remaining[letter] == 0:
                continue
            remaining[letter] -= 1
            letters.append(letter)
            yield from generate()
            letters.pop()
            remaining[letter] += 1

    yield from generate()


def avoid_552_inclusion_exclusion(n2: int, n3: int, n5: int) -> int:
    """Count fixed-content words avoiding 552 by exact inclusion-exclusion."""
    total = n2 + n3 + n5
    answer = 0
    for marked in range(min(n2, n5 // 2) + 1):
        arrangements = factorial(total - 2 * marked) // (
            factorial(marked)
            * factorial(n2 - marked)
            * factorial(n3)
            * factorial(n5 - 2 * marked)
        )
        answer += (-1) ** marked * arrangements
    return answer


def verify_unbordered_formula() -> dict[str, int]:
    vectors = 0
    words = 0
    for n2 in range(5):
        for n3 in range(3):
            for n5 in range(5):
                brute = 0
                for word in multiset_words(n2, n3, n5):
                    brute += "552" not in word
                    words += 1
                assert brute == avoid_552_inclusion_exclusion(n2, n3, n5)
                vectors += 1
    return {"count_vectors": vectors, "words_checked": words}


def isolated_block_count(k: int) -> int:
    """Count canonical words starting with 3 and avoiding 552."""
    return avoid_552_inclusion_exclusion(15 * k, 10 * k - 1, 6 * k)


def canonical_block_key(word: str) -> tuple[str, int]:
    pieces = [word[:6], word[6:12]]
    good = sum(piece in (U, V) for piece in pieces)
    key = "".join(U if piece in (U, V) else piece for piece in pieces)
    return key, good


def toy_orbit_check() -> dict[str, object]:
    """Exhaust the count vector of two relation blocks: (6,2,4)."""
    orbits: dict[str, list[tuple[str, int, tuple[int, int]]]] = defaultdict(list)
    offsets: set[int] = set()
    weighted_orbit_count = Fraction(0)
    word_count = 0

    for word in multiset_words(6, 2, 4):
        key, good = canonical_block_key(word)
        affine_map = affine_outermost(word)
        orbits[key].append((word, good, affine_map))
        offsets.add(affine_map[1])
        weighted_orbit_count += Fraction(1, 2**good)
        word_count += 1

    orbit_sizes: Counter[int] = Counter()
    for members in orbits.values():
        good_values = {member[1] for member in members}
        map_values = {member[2] for member in members}
        assert len(good_values) == 1
        assert len(map_values) == 1
        good = next(iter(good_values))
        assert len(members) == 2**good
        orbit_sizes[len(members)] += 1

    assert weighted_orbit_count.denominator == 1
    assert weighted_orbit_count.numerator == len(orbits)
    assert len(offsets) <= len(orbits)
    return {
        "counts": [6, 2, 4],
        "words": word_count,
        "orbits": len(orbits),
        "distinct_offsets": len(offsets),
        "orbit_sizes": {str(size): count for size, count in sorted(orbit_sizes.items())},
        "sum_word_weight_2_to_minus_r": weighted_orbit_count.numerator,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-k", type=int, default=50)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assert args.max_k >= 2

    assert counts(U) == counts(V) == (3, 1, 2)
    assert affine_outermost(U) == affine_outermost(V) == (600, 218)
    assert affine_chronological(U) == (600, 433)
    assert affine_chronological(V) == (600, 136)

    parity_checks = []
    conditional_minima = []
    for k in range(2, args.max_k + 1):
        selected = k // 2
        assert 6 * selected <= 3 * k
        assert selected * 3 >= k
        assert 6 * (selected - 1) <= 3 * k - 6
        parity_checks.append(
            {
                "k": k,
                "selected_blocks": selected,
                "selected_positions": 6 * selected,
            }
        )
        conditional_minima.append(exact_conditional_minimum(k))

    contraction = 1 - P0 / 2
    entropy_ratio = Fraction(31**31, 30**31)
    # For even k, the upper bound relative to Q^k has exponential base
    # (31/30)^31 * sqrt(contraction).  Its square is rational and exceeds 1.
    relative_q_base_squared = entropy_ratio**2 * contraction
    assert relative_q_base_squared > 1

    relation_check_limit = max(args.max_k, 25)
    isolated_counts = [
        isolated_block_count(k) for k in range(1, relation_check_limit + 1)
    ]
    crossings = [
        k
        for k, isolated in enumerate(isolated_counts, start=1)
        if isolated > CANONICAL_SLOPE**k
    ]
    assert crossings[0] == 25
    isolated_25 = isolated_block_count(25)
    exact_margin = 6 * isolated_25 - 7 * CANONICAL_SLOPE**25
    assert exact_margin > 0

    payload = {
        "identity": {
            "u": U,
            "v": V,
            "counts": list(counts(U)),
            "outermost_first_u": list(affine_outermost(U)),
            "outermost_first_v": list(affine_outermost(V)),
            "chronological_u": list(affine_chronological(U)),
            "chronological_v": list(affine_chronological(V)),
        },
        "uniform_bound": {
            "p0": f"{P0.numerator}/{P0.denominator}",
            "p0_decimal": float(P0),
            "one_minus_p0_over_2": (
                f"{contraction.numerator}/{contraction.denominator}"
            ),
            "exponential_rate_p0_over_6": str(P0 / 6),
        },
        "toy_action": toy_orbit_check(),
        "unbordered_formula_replay": verify_unbordered_formula(),
        "parity_checks": parity_checks,
        "conditional_minima": conditional_minima,
        "normalization_audit": {
            "canonical_slope_Q": CANONICAL_SLOPE,
            "surplus_log_per_k": 31 * log(31 / 30),
            "fixed_block_log_reduction_per_k_limit": -0.5 * log(float(contraction)),
            "word_to_Q_entropy_base": float(entropy_ratio),
            "orbit_upper_bound_to_Q_base_even_k": float(
                relative_q_base_squared
            )
            ** 0.5,
            "orbit_upper_bound_to_Q_base_squared_exact": (
                f"{relative_q_base_squared.numerator}/"
                f"{relative_q_base_squared.denominator}"
            ),
            "base_exceeds_one": relative_q_base_squared > 1,
        },
        "relation_only_obstruction": {
            "language": "canonical-count words starting with 3 and avoiding 552",
            "first_k_checked_with_count_above_Q_to_k": crossings[0],
            "A_25": str(isolated_25),
            "A_25_over_Q_25": float(Fraction(isolated_25, CANONICAL_SLOPE**25)),
            "certificate": "6*A_25 > 7*Q^25",
            "positive_integer_margin": str(exact_margin),
            "certified_per_k_base_over_Q": float(Fraction(7, 6)) ** (1 / 25),
            "exact_formula": (
                "A_k=sum_{j=0}^{3k}(-1)^j(31k-1-2j)!/"
                "(j!(15k-j)!(10k-1)!(6k-2j)!)"
            ),
        },
        "max_k_checked": args.max_k,
    }
    payload["script_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
