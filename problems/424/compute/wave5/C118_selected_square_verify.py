#!/usr/bin/env python3
"""Independent replay for the C118 selected-square probe."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from functools import lru_cache
from fractions import Fraction
from pathlib import Path


OTHER = 0
GENERATED = 1
SPLITLESS = 2
HARD = 3


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def trial_pairs(value: int) -> list[tuple[int, int]]:
    product = value + 1
    result = []
    for left in range(2, math.isqrt(product) + 1):
        if product % left:
            continue
        right = product // left
        if left < right and allowed(left) and allowed(right):
            result.append((left, right))
    return result


@lru_cache(maxsize=None)
def classify(value: int) -> int:
    if value in (2, 3):
        return GENERATED
    if not allowed(value):
        return OTHER
    pairs = trial_pairs(value)
    if any(classify(left) == GENERATED and classify(right) == GENERATED for left, right in pairs):
        return GENERATED
    if not pairs:
        return SPLITLESS
    if value % 2 == 0:
        product = value + 1
        seed_three_easy = (
            product % 3 == 0
            and product // 3 != 3
            and allowed(product // 3)
        )
        if not seed_three_easy:
            return HARD
    return OTHER


def seed_root(endpoint: int) -> int:
    shifted = endpoint - 1
    return 1 + shifted // (shifted & -shifted)


def trial_tau(value: int) -> int:
    result = 1
    divisor = 2
    while divisor * divisor <= value:
        exponent = 0
        while value % divisor == 0:
            value //= divisor
            exponent += 1
        if exponent:
            result *= exponent + 1
        divisor = 3 if divisor == 2 else divisor + 2
    if value > 1:
        result *= 2
    return result


def as_fraction(row: dict[str, int]) -> Fraction:
    return Fraction(row["numerator"], row["denominator"])


def verify_failure(row: dict, expected_h: int, expected_root: int) -> bool:
    h = row["h"]
    root = row["root"]
    endpoint = row["endpoint"]
    product = h + 1
    pairs = trial_pairs(h)
    return all(
        (
            h == expected_h,
            root == expected_root,
            classify(h) == HARD,
            len(pairs) == row["d"],
            endpoint in {item for pair in pairs for item in pair},
            classify(endpoint) != GENERATED,
            seed_root(endpoint) == root,
            classify(root) != SPLITLESS,
            product % endpoint == 0,
            trial_tau(endpoint) == row["tau_endpoint"],
            trial_tau(product // endpoint) == row["tau_cofactor"],
        )
    )


def recompute_square_blocks(reference: dict, maximum_m: int) -> dict[int, Fraction]:
    result = {}
    for m in range(1, maximum_m + 1):
        block = Fraction()
        for bin_row in reference["bins"]:
            j = bin_row["j"]
            counts = bin_row["threshold_counts"]
            for threshold in range(m * m + 1, (m + 1) * (m + 1) + 1):
                if threshold <= len(counts) and threshold <= j * j:
                    block += Fraction(counts[threshold - 1], 1 << j)
        result[m] = block
    return result


def verify_synthetic(row: dict) -> bool:
    primes = row["minus_primes"]
    multiplier = math.prod(primes)
    j = row["j"]
    roots = []
    for denominator in range(1 << j, 1 << (j + 1)):
        root = denominator + 1
        endpoint = 2 * root - 1
        if root % 6 == 0 and math.gcd(endpoint, multiplier) == 1:
            roots.append(root)
    t_min = ((1 << j) + 6) // 6
    t_max = (1 << (j + 1)) // 6
    interval_length = t_max - t_min + 1
    crt_density = Fraction(1)
    for prime in primes:
        crt_density *= Fraction(prime - 1, prime)
    crt_error = abs(Fraction(len(roots)) - interval_length * crt_density)
    sample_ok = True
    for sample in row["sample_rows"]:
        root = sample["root"]
        endpoint = sample["endpoint"]
        product = sample["source_plus_1"]
        pairs = sample["certified_admissible_pairs"]
        sample_ok = sample_ok and all(
            (
                endpoint == 2 * root - 1,
                seed_root(endpoint) == root,
                product == endpoint * multiplier,
                len(pairs) == 16,
                len({tuple(pair) for pair in pairs}) == 16,
                all(
                    left * right == product
                    and left < right
                    and allowed(left)
                    and allowed(right)
                    for left, right in pairs
                ),
            )
        )
    return all(
        (
            all(prime % 3 == 2 for prime in primes),
            len(primes) % 2 == 1,
            multiplier == row["fixed_multiplier"],
            len(roots) == row["valid_root_count"],
            Fraction(len(roots), 1 << j) == as_fraction(row["valid_root_density"]),
            crt_error <= 1 << len(primes),
            crt_density >= Fraction(4, len(primes) + 4),
            sample_ok,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    claim_bytes = args.claim.read_bytes()
    claim = json.loads(claim_bytes)
    reference = json.loads(args.reference.read_bytes())
    prefix = claim["prefix"]
    failures = prefix["first_failures"]
    reference_blocks = recompute_square_blocks(reference, len(prefix["square_blocks"]))
    checks = {
        "schema": claim["schema"] == "C118-selected-square-probe-v1",
        "claim_sha256": hashlib.sha256(claim_bytes).hexdigest().upper()
        == "715098CACB3A408D73BED62240C043CD3B80827A06F6F0B3DF31EB5956FA6DB3",
        "hard_sources_match_C108": prefix["hard_sources"] == reference["hard_sources"],
        "all_upgrades_match_C108": prefix["all_root_upgrade_events"]
        == reference["root_upgrade_events"],
        "maximum_d_matches_C108": prefix["maximum_d"]
        == reference["maximum_pair_count"],
        "positive_roots_match_C108": prefix["distinct_reducible_roots"]
        == sum(row["positive_root_count"] for row in reference["bins"]),
        "square_blocks_match_C108": all(
            as_fraction(row["B_m"]) == reference_blocks[row["m"]]
            for row in prefix["square_blocks"]
        ),
        "cofactor_failure_replayed": verify_failure(
            failures["cofactor_tau_ge_d"], 1154, 116
        ),
        "endpoint_failure_replayed": verify_failure(
            failures["endpoint_tau_ge_d"], 52436, 114
        ),
        "synthetic_bank_replayed": verify_synthetic(
            claim["divisor_rich_multiple_obstruction"]
        ),
    }
    result = {
        "schema": "C118-selected-square-verify-v1",
        "arithmetic": "exact integers and Fraction only",
        "checks": checks,
        "status": "PASS" if all(checks.values()) else "FAIL",
    }
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    args.output.write_bytes(payload.encode("ascii"))
    print(hashlib.sha256(payload.encode("ascii")).hexdigest().upper())


if __name__ == "__main__":
    main()
