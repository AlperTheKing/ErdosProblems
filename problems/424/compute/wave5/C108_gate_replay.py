#!/usr/bin/env python3
"""Solver-free exact replay for the C108 C104-BIN adversarial gates."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path


def load(path: Path) -> tuple[dict, str]:
    payload = path.read_bytes()
    return json.loads(payload), hashlib.sha256(payload).hexdigest().upper()


def fraction_json(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def threshold_counts_from_roots(roots: list[dict], maximum_q: int) -> list[int]:
    return [sum(root["q"] >= d for root in roots) for d in range(1, maximum_q + 1)]


def moving_weight(q: int, j: int) -> int:
    return min(math.isqrt(q - 1) + 1, j) if q else 0


def verify_independent_small(small: dict, fast: dict) -> dict:
    if small["limit"] != fast["limit"]:
        raise AssertionError("small/fast limit mismatch")
    if small["hard_sources"] != fast["hard_sources"]:
        raise AssertionError("small/fast hard-source mismatch")
    fast_bins = {row["j"]: row for row in fast["bins"]}
    checked = 0
    for row in small["bins"]:
        roots = [root for root in row["roots"] if root["q"] > 0]
        if not roots:
            continue
        actual = fast_bins[row["j"]]
        maximum_q = max(root["q"] for root in roots)
        expected_counts = threshold_counts_from_roots(roots, maximum_q)
        expected_moving = sum(moving_weight(root["q"], row["j"]) for root in roots)
        if expected_counts != actual["threshold_counts"]:
            raise AssertionError(("small/fast threshold mismatch", row["j"]))
        if sum(root["q"] for root in roots) != actual["threshold_token_sum"]:
            raise AssertionError(("small/fast weighted mismatch", row["j"]))
        if expected_moving != actual["moving_sqrt_token_sum"]:
            raise AssertionError(("small/fast moving-weight mismatch", row["j"]))
        checked += 1
    return {
        "limit": small["limit"],
        "hard_sources_match": True,
        "bins_checked": checked,
        "threshold_counts_match": True,
        "weighted_sums_match": True,
        "moving_sqrt_sums_match": True,
    }


def verify_c104_reference(raw: dict, fast: dict) -> dict:
    if raw["limit"] != fast["limit"]:
        raise AssertionError("C104/C108 limit mismatch")
    if raw["totals"]["hard"] != fast["hard_sources"]:
        raise AssertionError("C104/C108 hard-source mismatch")
    if raw["totals"]["maximum_pair_count"] != fast["maximum_pair_count"]:
        raise AssertionError("C104/C108 maximum-d mismatch")
    if raw["digests"]["classification_2_through_limit"] != fast["classification_fnv1a64"]:
        raise AssertionError("C104/C108 classification-digest mismatch")

    endpoint = raw["checkpoints"][-1]
    c104_by_d = {row["D"]: row for row in endpoint["thresholds"] if row["D"] >= 1}
    c108_bins = {row["j"]: row for row in fast["bins"]}
    checked = 0
    for j, c108 in c108_bins.items():
        expected = []
        for d in range(1, c108["maximum_q"] + 1):
            bins = {row["j"]: row["count"] for row in c104_by_d[d]["dyadic_bins"]}
            expected.append(bins.get(j, 0))
        if expected != c108["threshold_counts"]:
            raise AssertionError(("C104/C108 bin mismatch", j))
        checked += 1
    return {
        "limit": raw["limit"],
        "hard_sources_match": True,
        "maximum_pair_count_match": True,
        "classification_digest_match": True,
        "threshold_bins_checked": checked,
        "threshold_counts_match": True,
    }


def verify_large(large: dict) -> dict:
    failure_fields = (
        "first_C104_BIN_failure",
        "first_weighted_token_budget_failure",
        "lower_moving_sqrt_deadline_failure_at_limit",
        "lower_moving_sqrt_deadline_excluding_least_failure_at_limit",
    )
    for field in failure_fields:
        if large[field] is not None:
            raise AssertionError(("reported gate failure", field, large[field]))

    best_half = None
    best_linear = None
    best_moving = None
    best_weighted = None
    checked_thresholds = 0
    for row in large["bins"]:
        j = row["j"]
        capacity = row["capacity"]
        counts = row["threshold_counts"]
        if sum(counts) != row["threshold_token_sum"]:
            raise AssertionError(("layer-cake mismatch", j))
        if counts[0] != row["positive_root_count"]:
            raise AssertionError(("positive-root mismatch", j))
        if row["threshold_token_sum"] > capacity:
            raise AssertionError(("weighted budget failure", j))
        if row["moving_sqrt_token_sum"] > capacity:
            raise AssertionError(("moving-token budget failure", j))

        moving_ratio = Fraction(row["moving_sqrt_token_sum"], capacity)
        weighted_ratio = Fraction(row["threshold_token_sum"], capacity)
        moving_item = (moving_ratio, j)
        weighted_item = (weighted_ratio, j)
        if best_moving is None or moving_item > best_moving:
            best_moving = moving_item
        if best_weighted is None or weighted_item > best_weighted:
            best_weighted = weighted_item

        for d, count in enumerate(counts, 1):
            checked_thresholds += 1
            if d * count > capacity:
                raise AssertionError(("C104-BIN failure", j, d, count))
            linear_item = (Fraction(d * count, capacity), j, d, count, capacity)
            if best_linear is None or linear_item > best_linear:
                best_linear = linear_item
            half_squared = Fraction(d * count * count, capacity * capacity)
            half_item = (half_squared, j, d, count, capacity)
            if best_half is None or half_item > best_half:
                best_half = half_item

    if (best_half is None or best_linear is None or best_moving is None or
        best_weighted is None):
        raise AssertionError("large artifact has no nonempty bins")
    return {
        "limit": large["limit"],
        "hard_sources": large["hard_sources"],
        "maximum_pair_count": large["maximum_pair_count"],
        "classification_fnv1a64": large["classification_fnv1a64"],
        "bins_checked": len(large["bins"]),
        "thresholds_checked": checked_thresholds,
        "all_failure_fields_null": True,
        "layer_cake_identities_hold": True,
        "C104_BIN_holds": True,
        "moving_sqrt_deadline_holds": True,
        "maximum_C104_BIN_ratio": fraction_json(best_linear[0]),
        "maximum_C104_BIN_location": {
            "j": best_linear[1],
            "D": best_linear[2],
            "count": best_linear[3],
            "capacity": best_linear[4],
        },
        "maximum_half_tail_C_squared": fraction_json(best_half[0]),
        "maximum_half_tail_location": {
            "j": best_half[1],
            "D": best_half[2],
            "count": best_half[3],
            "capacity": best_half[4],
        },
        "maximum_moving_token_mass_ratio": fraction_json(best_moving[0]),
        "maximum_moving_token_mass_bin": best_moving[1],
        "maximum_weighted_mass_ratio": fraction_json(best_weighted[0]),
        "maximum_weighted_mass_bin": best_weighted[1],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--small", type=Path, required=True)
    parser.add_argument("--fast-small", type=Path, required=True)
    parser.add_argument("--c104-raw", type=Path, required=True)
    parser.add_argument("--c104-fast", type=Path, required=True)
    parser.add_argument("--large", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    small, small_sha = load(args.small)
    fast_small, fast_small_sha = load(args.fast_small)
    c104_raw, c104_raw_sha = load(args.c104_raw)
    c104_fast, c104_fast_sha = load(args.c104_fast)
    large, large_sha = load(args.large)
    result = {
        "schema": "C108-c104-bin-gate-replay-v1",
        "arithmetic": "exact integers and Fraction only",
        "inputs": {
            args.small.name: small_sha,
            args.fast_small.name: fast_small_sha,
            args.c104_raw.name: c104_raw_sha,
            args.c104_fast.name: c104_fast_sha,
            args.large.name: large_sha,
        },
        "independent_small_replay": verify_independent_small(small, fast_small),
        "C104_reference_replay": verify_c104_reference(c104_raw, c104_fast),
        "large_gate_replay": verify_large(large),
    }
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    args.output.write_bytes(payload.encode("ascii"))
    print(payload, end="")


if __name__ == "__main__":
    main()
