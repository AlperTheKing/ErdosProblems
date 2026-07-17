"""Residue-state upper bounds for affine-word endpoint multiplicity.

Let R_v(d) count words with count vector v and offset d.  For a modulus Q,
U_v(r) is defined recursively by replacing each actual parent residue with the
maximum over every compatible residue modulo Q:

  U_v(r) = sum_m max_{s: m*s+q_m = r (mod Q)} U_(v-e_m)(s).

Induction gives R_v(d) <= U_v(d mod Q).  This is a rigorous finite carry
relaxation.  The script exact-checks the inequality against full word
enumeration at small length, then evaluates it on the ray v=k(3,2,1).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from math import comb
from pathlib import Path


LETTERS = ((2, 0, 0), (3, 1, 1), (5, 3, 2))
RAY = (3, 2, 1)
RAY_SLOPE = 360


def multinomial(a: int, b: int, c: int) -> int:
    return comb(a + b + c, a) * comb(b + c, b)


def brute_layers(max_length: int):
    layers: list[dict[tuple[int, int, int], dict[int, int]]] = [
        {(0, 0, 0): {0: 1}}
    ]
    for _ in range(max_length):
        current: dict[tuple[int, int, int], dict[int, int]] = {}
        for counts, offsets in layers[-1].items():
            for multiplier, shift, index in LETTERS:
                new_counts = list(counts)
                new_counts[index] += 1
                key = tuple(new_counts)
                target = current.setdefault(key, {})
                for old_offset, multiplicity in offsets.items():
                    new_offset = multiplier * old_offset + shift
                    target[new_offset] = (
                        target.get(new_offset, 0) + multiplicity
                    )
        layers.append(current)
    return layers


def parent_residues(modulus: int):
    result = {}
    for multiplier, shift, _ in LETTERS:
        by_target = [[] for _ in range(modulus)]
        for parent in range(modulus):
            target = (multiplier * parent + shift) % modulus
            by_target[target].append(parent)
        result[multiplier] = by_target
    return result


def branch_bound(values: list[int], parents: list[list[int]]) -> list[int]:
    return [
        max((values[parent] for parent in compatible), default=0)
        for compatible in parents
    ]


def run_modulus(
    modulus: int,
    kmax: int,
    brute,
    brute_length: int,
):
    parents = parent_residues(modulus)
    previous = {(0, 0, 0): [1] + [0] * (modulus - 1)}
    target_rows = []
    exact_checks = 0
    equality_checks = 0
    max_small_ratio = 1.0

    for length in range(1, 6 * kmax + 1):
        current = {}
        for a in range(min(3 * kmax, length), -1, -1):
            for b in range(min(2 * kmax, length - a), -1, -1):
                c = length - a - b
                if c < 0 or c > kmax:
                    continue
                counts = (a, b, c)
                value = [0] * modulus
                for multiplier, _, index in LETTERS:
                    if counts[index] == 0:
                        continue
                    parent_counts = list(counts)
                    parent_counts[index] -= 1
                    bounded = branch_bound(
                        previous[tuple(parent_counts)],
                        parents[multiplier],
                    )
                    value = [
                        old + addition
                        for old, addition in zip(value, bounded)
                    ]
                current[counts] = value

                if length <= brute_length:
                    exact = brute[length][counts]
                    for offset, multiplicity in exact.items():
                        bound = value[offset % modulus]
                        assert multiplicity <= bound
                        exact_checks += 1
                        equality_checks += multiplicity == bound
                        max_small_ratio = max(
                            max_small_ratio, bound / multiplicity
                        )

                if (
                    length % 6 == 0
                    and counts
                    == tuple((length // 6) * entry for entry in RAY)
                ):
                    k = length // 6
                    upper = max(value)
                    words = multinomial(a, b, c)
                    log_normalized = (
                        math.log(upper)
                        + k * math.log(RAY_SLOPE)
                        - math.log(words)
                        - 0.5 * math.log(k)
                    )
                    target_rows.append(
                        {
                            "k": k,
                            "multiplicity_upper": str(upper),
                            "normalization_U_M_over_W_sqrt_k": math.exp(
                                log_normalized
                            ),
                        }
                    )
        previous = current

    return {
        "modulus": modulus,
        "exact_endpoint_checks": exact_checks,
        "exact_equalities": equality_checks,
        "max_small_bound_to_exact_ratio": max_small_ratio,
        "target_rows": target_rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--moduli", default="30,150")
    parser.add_argument("--kmax", type=int, default=20)
    parser.add_argument("--brute-length", type=int, default=10)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    moduli = [int(item) for item in args.moduli.split(",")]
    brute = brute_layers(args.brute_length)
    results = [
        run_modulus(
            modulus,
            args.kmax,
            brute,
            args.brute_length,
        )
        for modulus in moduli
    ]

    result = {
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "ray": RAY,
        "ray_slope": RAY_SLOPE,
        "kmax": args.kmax,
        "brute_length": args.brute_length,
        "results": results,
    }
    rendered = json.dumps(result, indent=2, sort_keys=True)
    print(rendered)
    if args.output is not None:
        args.output.write_text(rendered + "\n", encoding="ascii")


if __name__ == "__main__":
    main()
