"""Exact finite-block pressure test for the fixed-count affine offset gate.

For L_m(t) = m*t + q_m with (q_2,q_3,q_5) = (0,1,3), let D_v be
the set of offsets of words with count vector v.  The polynomial

    P_L(x,y,z) = sum_{a+b+c=L} |D_(a,b,c)| x^a y^b z^c

gives an exact upper bound after splitting a word into length-L blocks.
For the ray r=(3,2,1), a positive rational evaluation of P_L whose
coefficient bound has base below 360 is an exact exponential falsifier.

The script also exhaustively checks the concatenation injection and the
adjacent-swap identity on the enumerated layers.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path


LETTERS = (2, 3, 5)
SHIFT = {2: 0, 3: 1, 5: 3}
INDEX = {2: 0, 3: 1, 5: 2}
TARGET = (3, 2, 1)
TARGET_SLOPE = 360


def slope(counts: tuple[int, int, int]) -> int:
    a, b, c = counts
    return (2**a) * (3**b) * (5**c)


def offset(word: str) -> int:
    value = 0
    for letter in reversed(word):
        m = int(letter)
        value = m * value + SHIFT[m]
    return value


def add_count(
    counts: tuple[int, int, int], letter: int
) -> tuple[int, int, int]:
    result = list(counts)
    result[INDEX[letter]] += 1
    return tuple(result)


def enumerate_layers(max_length: int):
    layers: list[dict[tuple[int, int, int], dict[int, str]]] = [
        {(0, 0, 0): {0: ""}}
    ]
    collisions: list[dict[str, object]] = []

    for length in range(1, max_length + 1):
        current: dict[tuple[int, int, int], dict[int, str]] = {}
        for counts, representatives in layers[-1].items():
            for letter in LETTERS:
                new_counts = add_count(counts, letter)
                target = current.setdefault(new_counts, {})
                for old_offset, old_word in representatives.items():
                    new_offset = letter * old_offset + SHIFT[letter]
                    new_word = str(letter) + old_word
                    previous = target.get(new_offset)
                    if previous is None:
                        target[new_offset] = new_word
                    elif previous != new_word and len(collisions) < 64:
                        collisions.append(
                            {
                                "length": length,
                                "counts": new_counts,
                                "offset": new_offset,
                                "left": previous,
                                "right": new_word,
                            }
                        )
        layers.append(current)
    return layers, collisions


def pressure(
    support_sizes: dict[tuple[int, int, int], int], length: int
) -> dict[str, object]:
    target_b = length / 3.0
    target_c = length / 6.0
    theta_b = math.log(2.0 / 3.0)
    theta_c = math.log(1.0 / 3.0)

    for _ in range(100):
        terms = [
            (counts, math.log(size) + theta_b * counts[1] + theta_c * counts[2])
            for counts, size in support_sizes.items()
        ]
        peak = max(value for _, value in terms)
        weighted = [
            (counts, math.exp(value - peak)) for counts, value in terms
        ]
        total = sum(value for _, value in weighted)
        mean_b = sum(counts[1] * value for counts, value in weighted) / total
        mean_c = sum(counts[2] * value for counts, value in weighted) / total
        error_b = mean_b - target_b
        error_c = mean_c - target_c
        if max(abs(error_b), abs(error_c)) < 1e-14:
            break

        var_b = (
            sum((counts[1] - mean_b) ** 2 * value for counts, value in weighted)
            / total
        )
        var_c = (
            sum((counts[2] - mean_c) ** 2 * value for counts, value in weighted)
            / total
        )
        cov_bc = (
            sum(
                (counts[1] - mean_b)
                * (counts[2] - mean_c)
                * value
                for counts, value in weighted
            )
            / total
        )
        determinant = var_b * var_c - cov_bc * cov_bc
        step_b = (var_c * error_b - cov_bc * error_c) / determinant
        step_c = (-cov_bc * error_b + var_b * error_c) / determinant
        theta_b -= step_b
        theta_c -= step_c

    y_float = math.exp(theta_b)
    z_float = math.exp(theta_c)
    y = Fraction(y_float).limit_denominator(1_000_000)
    z = Fraction(z_float).limit_denominator(1_000_000)
    polynomial = sum(
        Fraction(size) * y ** counts[1] * z ** counts[2]
        for counts, size in support_sizes.items()
    )

    k0 = length // math.gcd(length, 6)
    blocks = 6 * k0 // length
    bound = polynomial**blocks / (y ** (2 * k0) * z**k0)
    target = Fraction(TARGET_SLOPE**k0)
    ratio = bound / target

    log_polynomial = math.log(float(polynomial))
    log_bound_per_k = (
        blocks * log_polynomial
        - 2 * k0 * math.log(float(y))
        - k0 * math.log(float(z))
    ) / k0

    return {
        "length": length,
        "rational_y": f"{y.numerator}/{y.denominator}",
        "rational_z": f"{z.numerator}/{z.denominator}",
        "macro_k": k0,
        "blocks_per_macro": blocks,
        "base_per_k": math.exp(log_bound_per_k),
        "base_ratio_to_360": math.exp(log_bound_per_k) / TARGET_SLOPE,
        "exact_below_360": bound < target,
        "exact_ratio_numerator_digits": len(str(ratio.numerator)),
        "exact_ratio_denominator_digits": len(str(ratio.denominator)),
    }


def verify_swap_identity(max_length: int) -> int:
    checked = 0
    for number in range(3**max_length):
        value = number
        letters = []
        for _ in range(max_length):
            letters.append(LETTERS[value % 3])
            value //= 3
        word = "".join(str(letter) for letter in letters)
        for position in range(max_length - 1):
            left = letters[position]
            right = letters[position + 1]
            if left == right:
                continue
            swapped = letters.copy()
            swapped[position], swapped[position + 1] = right, left
            swapped_word = "".join(str(letter) for letter in swapped)
            prefix = math.prod(letters[:position])
            predicted = prefix * (
                (left - 1) * SHIFT[right] - (right - 1) * SHIFT[left]
            )
            actual = offset(word) - offset(swapped_word)
            assert actual == predicted, (word, swapped_word, actual, predicted)
            checked += 1
    return checked


def verify_concatenation(layers, max_total_length: int) -> int:
    checked = 0
    for left_length in range(max_total_length + 1):
        for right_length in range(max_total_length - left_length + 1):
            for left_counts, left_values in layers[left_length].items():
                left_slope = slope(left_counts)
                for right_counts, right_values in layers[right_length].items():
                    total_counts = tuple(
                        left_counts[index] + right_counts[index]
                        for index in range(3)
                    )
                    combined = {
                        left_offset + left_slope * right_offset
                        for left_offset in left_values
                        for right_offset in right_values
                    }
                    expected = len(left_values) * len(right_values)
                    assert len(combined) == expected
                    assert combined <= layers[left_length + right_length][
                        total_counts
                    ].keys()
                    checked += expected
    return checked


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-length", type=int, default=12)
    parser.add_argument("--swap-length", type=int, default=8)
    parser.add_argument("--concat-length", type=int, default=8)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    layers, collisions = enumerate_layers(args.max_length)
    swap_checks = verify_swap_identity(args.swap_length)
    concatenation_checks = verify_concatenation(layers, args.concat_length)

    layer_stats = []
    pressures = []
    for length, layer in enumerate(layers):
        total_support = sum(len(values) for values in layer.values())
        layer_stats.append(
            {
                "length": length,
                "formal_words": 3**length,
                "distinct_affine_maps": total_support,
                "collisions": 3**length - total_support,
            }
        )
        if length >= 2:
            sizes = {counts: len(values) for counts, values in layer.items()}
            pressures.append(pressure(sizes, length))

    target_counts = {}
    for k in range(1, args.max_length // 6 + 1):
        counts = tuple(k * value for value in TARGET)
        target_counts[str(k)] = {
            "counts": counts,
            "slope": TARGET_SLOPE**k,
            "support": len(layers[6 * k][counts]),
        }

    known_left = "322255"
    known_right = "255232"
    recurrence_left = known_left[::-1]
    recurrence_right = known_right[::-1]
    result = {
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "max_length": args.max_length,
        "layer_stats": layer_stats,
        "target_counts": target_counts,
        "first_recorded_collisions": collisions,
        "known_identity": {
            "repository_inner_to_outer": [known_left, known_right],
            "recurrence_outer_to_inner": [recurrence_left, recurrence_right],
            "left_offset": offset(recurrence_left),
            "right_offset": offset(recurrence_right),
            "verified": offset(recurrence_left) == offset(recurrence_right),
        },
        "swap_identity_checks": swap_checks,
        "concatenation_injection_pairs_checked": concatenation_checks,
        "pressures": pressures,
    }
    rendered = json.dumps(result, indent=2, sort_keys=True)
    print(rendered)
    if args.output is not None:
        args.output.write_text(rendered + "\n", encoding="ascii")


if __name__ == "__main__":
    main()
