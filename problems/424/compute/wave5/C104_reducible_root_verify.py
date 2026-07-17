#!/usr/bin/env python3
"""Independent small-limit verifier for the C104 reducible-root census.

This implementation deliberately uses a full smallest-prime-factor table and
Fraction arithmetic.  It does not import the C85, C99, or C104 census code.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path


GENERATED = 1
SPLITLESS = 2
HARD = 3
K_MAX = 16
FIXED_BITS = 56
FIXED_SCALE = 1 << FIXED_BITS


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def full_spf(limit: int) -> list[int]:
    spf = list(range(limit + 1))
    for p in range(2, int(limit**0.5) + 1):
        if spf[p] != p:
            continue
        for multiple in range(p * p, limit + 1, p):
            if spf[multiple] == multiple:
                spf[multiple] = p
    return spf


def divisors(n: int, spf: list[int]) -> list[int]:
    factors: list[tuple[int, int]] = []
    while n > 1:
        p = spf[n]
        exponent = 0
        while n % p == 0:
            n //= p
            exponent += 1
        factors.append((p, exponent))
    result = [1]
    for p, exponent in factors:
        old = tuple(result)
        power = 1
        for _ in range(exponent):
            power *= p
            result.extend(d * power for d in old)
    return result


def admissible_pairs(n: int, spf: list[int]) -> list[tuple[int, int]]:
    product = n + 1
    result = []
    for left in divisors(product, spf):
        if left < 2 or left * left >= product:
            continue
        right = product // left
        if allowed(left) and allowed(right):
            result.append((left, right))
    return sorted(result)


def root_by_parent_iteration(endpoint: int) -> int:
    if endpoint <= 1 or endpoint % 2 == 0:
        raise AssertionError(("non-odd witness endpoint", endpoint))
    value = (endpoint + 1) // 2
    while value % 2:
        value = (value + 1) // 2
    return value


def checkpoint_cutoffs(limit: int) -> list[int]:
    values = {
        1_000,
        3_000,
        10_000,
        30_000,
        100_000,
        300_000,
        1_000_000,
        3_000_000,
        10_000_000,
        30_000_000,
        100_000_000,
        limit,
    }
    return sorted(x for x in values if x <= limit)


def fraction_from_json(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def build_independent(limit: int) -> tuple[list[dict], dict]:
    spf = full_spf(limit + 1)
    state = bytearray(limit + 1)
    maximum_d: dict[int, int] = {}
    hard_source_counts = [0] * (K_MAX + 1)
    wanted = checkpoint_cutoffs(limit)
    wanted_set = set(wanted)
    checkpoints = []
    totals = {
        "generated": 0,
        "structural_splitless": 0,
        "hard": 0,
        "hard_with_reducible_root": 0,
        "maximum_pair_count": 0,
    }

    for n in range(2, limit + 1):
        pairs: list[tuple[int, int]] = []
        current = 0
        if n in (2, 3):
            current = GENERATED
        elif allowed(n):
            pairs = admissible_pairs(n, spf)
            if any(state[a] == GENERATED and state[b] == GENERATED for a, b in pairs):
                current = GENERATED
            elif not pairs:
                current = SPLITLESS
            elif n % 2 == 0:
                product = n + 1
                seed_three_easy = (
                    product % 3 == 0
                    and product // 3 != 3
                    and allowed(product // 3)
                )
                if not seed_three_easy:
                    current = HARD
        state[n] = current
        if current == GENERATED:
            totals["generated"] += 1
        elif current == SPLITLESS:
            totals["structural_splitless"] += 1
        elif current == HARD:
            totals["hard"] += 1
            d = len(pairs)
            totals["maximum_pair_count"] = max(totals["maximum_pair_count"], d)
            for k in range(1, min(d, K_MAX) + 1):
                hard_source_counts[k] += 1
            roots = set()
            for a, b in pairs:
                blocked = False
                for endpoint in (a, b):
                    if state[endpoint] != GENERATED:
                        blocked = True
                        root = root_by_parent_iteration(endpoint)
                        if state[root] == GENERATED:
                            raise AssertionError(("generated root", n, endpoint, root))
                        if state[root] != SPLITLESS:
                            roots.add(root)
                if not blocked:
                    raise AssertionError(("unblocked hard pair", n, a, b))
            totals["hard_with_reducible_root"] += bool(roots)
            for root in roots:
                maximum_d[root] = max(maximum_d.get(root, 0), d)

        if n % 2 and allowed(n) and current != GENERATED:
            parent = (n + 1) // 2
            if not allowed(parent) or state[parent] == GENERATED:
                raise AssertionError(("odd-hole parent", n, parent))

        if n in wanted_set:
            rows = []
            for k in range(1, K_MAX + 1):
                roots = sorted(root for root, d in maximum_d.items() if d >= k)
                reciprocal = sum((Fraction(1, root - 1) for root in roots), Fraction())
                lower_numerator = sum(FIXED_SCALE // (root - 1) for root in roots)
                bins: dict[int, list[int]] = {}
                for root in roots:
                    denominator = root - 1
                    j = denominator.bit_length() - 1
                    row = bins.setdefault(j, [0, 0])
                    row[0] += 1
                    row[1] += FIXED_SCALE // denominator
                rows.append(
                    {
                        "k": k,
                        "hard_sources": hard_source_counts[k],
                        "roots": roots,
                        "reciprocal": reciprocal,
                        "lower_numerator": lower_numerator,
                        "bins": bins,
                    }
                )
            checkpoints.append({"X": n, "thresholds": rows})
    return checkpoints, totals


def verify(raw_path: Path) -> dict:
    raw_bytes = raw_path.read_bytes()
    raw = json.loads(raw_bytes)
    limit = int(raw["limit"])
    if limit > 300_000:
        raise ValueError("independent verifier is intentionally limited to 300000")
    checkpoints, totals = build_independent(limit)
    if totals != raw["totals"]:
        raise AssertionError(("totals mismatch", totals, raw["totals"]))
    if len(checkpoints) != len(raw["checkpoints"]):
        raise AssertionError("checkpoint-count mismatch")

    verified_rows = 0
    exact_mass_samples = []
    for expected_cp, actual_cp in zip(checkpoints, raw["checkpoints"], strict=True):
        if expected_cp["X"] != actual_cp["X"]:
            raise AssertionError(("checkpoint X mismatch", expected_cp["X"], actual_cp["X"]))
        for expected, actual in zip(
            expected_cp["thresholds"], actual_cp["thresholds"], strict=True
        ):
            if expected["k"] != actual["k"]:
                raise AssertionError("threshold mismatch")
            if expected["hard_sources"] != actual["hard_sources"]:
                raise AssertionError(("source-count mismatch", expected_cp["X"], expected["k"]))
            if len(expected["roots"]) != actual["root_count"]:
                raise AssertionError(("root-count mismatch", expected_cp["X"], expected["k"]))
            interval = actual["reciprocal_interval"]
            lower = fraction_from_json(interval["lower"])
            upper = fraction_from_json(interval["upper"])
            exact = expected["reciprocal"]
            if not lower <= exact <= upper or expected["lower_numerator"] != interval["floor_numerator"]:
                raise AssertionError(("reciprocal interval mismatch", expected_cp["X"], expected["k"]))
            actual_bins = {
                row["j"]: [row["count"], row["fixed_floor_numerator"]]
                for row in actual["dyadic_bins"]
            }
            if expected["bins"] != actual_bins:
                raise AssertionError(("dyadic-bin mismatch", expected_cp["X"], expected["k"]))
            verified_rows += 1
            if expected_cp["X"] == limit and expected["k"] in (1, 5, 6, 7):
                exact_mass_samples.append(
                    {
                        "X": expected_cp["X"],
                        "k": expected["k"],
                        "numerator": exact.numerator,
                        "denominator": exact.denominator,
                    }
                )

    return {
        "schema": "C104-independent-small-verifier-v1",
        "raw_file": raw_path.name,
        "raw_sha256": hashlib.sha256(raw_bytes).hexdigest().upper(),
        "limit": limit,
        "verified_checkpoint_threshold_rows": verified_rows,
        "totals_exact_match": True,
        "root_counts_exact_match": True,
        "dyadic_bins_exact_match": True,
        "fixed_point_intervals_contain_exact_Fraction_sums": True,
        "exact_mass_samples": exact_mass_samples,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.raw)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    args.output.write_text(payload, encoding="ascii")
    print(payload, end="")


if __name__ == "__main__":
    main()
