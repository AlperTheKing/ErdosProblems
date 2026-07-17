#!/usr/bin/env python3
"""Exact C120 scan of canonical-blocker roots and deterministic leaves."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from array import array
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

import sympy


OTHER = 0
GENERATED = 1
SPLITLESS = 2
HARD = 3
STATE_NAMES = {
    OTHER: "other_hole",
    GENERATED: "generated",
    SPLITLESS: "structural_splitless",
    HARD: "hard",
}
RECIPROCAL_SCALE_BITS = 64
RECIPROCAL_SCALE = 1 << RECIPROCAL_SCALE_BITS


def require(condition: bool, message: object) -> None:
    if not condition:
        raise RuntimeError(message)


def allowed(value: int) -> bool:
    return value >= 2 and value % 3 != 1


def hard_shape(product: int) -> str | None:
    if product % 3 == 1:
        return "R"
    if product % 9 == 3 and (product // 3) % 3 == 1:
        return "3R"
    return None


def seed_root(endpoint: int) -> int:
    require(endpoint >= 3 and endpoint % 2 == 1, ("odd endpoint", endpoint))
    shifted = endpoint - 1
    return 1 + shifted // (shifted & -shifted)


def smallest_prime_factors(limit: int) -> array:
    spf = array("I", range(limit + 1))
    for prime in range(2, math.isqrt(limit) + 1):
        if spf[prime] != prime:
            continue
        start = prime * prime
        for multiple in range(start, limit + 1, prime):
            if spf[multiple] == multiple:
                spf[multiple] = prime
    return spf


def divisors_spf(value: int, spf: array) -> list[int]:
    result = [1]
    while value > 1:
        prime = int(spf[value])
        base = tuple(result)
        power = 1
        while value % prime == 0:
            value //= prime
            power *= prime
            result.extend(item * power for item in base)
    return result


def pairs_spf(value: int, spf: array) -> tuple[tuple[int, int], ...]:
    product = value + 1
    return tuple(sorted(
        (left, product // left)
        for left in divisors_spf(product, spf)
        if 2 <= left < product // left
        and allowed(left)
        and allowed(product // left)
    ))


def classify_prefix(limit: int, spf: array) -> bytearray:
    state = bytearray(limit + 1)
    for value in range(2, limit + 1):
        if value in (2, 3):
            state[value] = GENERATED
            continue
        if not allowed(value):
            continue
        pairs = pairs_spf(value, spf)
        if any(
            state[left] == GENERATED and state[right] == GENERATED
            for left, right in pairs
        ):
            state[value] = GENERATED
        elif not pairs:
            state[value] = SPLITLESS
        elif value % 2 == 0 and hard_shape(value + 1) is not None:
            state[value] = HARD
    return state


def prefix_leaf_function(state: bytearray, spf: array):
    memo: dict[int, tuple[int, int]] = {}
    next_root_map: dict[int, int] = {}

    def leaf_from_root(start: int) -> tuple[int, int]:
        cached = memo.get(start)
        if cached is not None:
            return cached
        path: list[int] = []
        root = start
        while root not in memo and state[root] != SPLITLESS:
            require(state[root] != GENERATED, ("generated descent root", start, root))
            pairs = pairs_spf(root, spf)
            require(bool(pairs), ("nonstructural root without pair", start, root))
            left, right = pairs[0]
            blocker = left if state[left] != GENERATED else right
            require(state[blocker] != GENERATED, ("unblocked descent pair", root, left, right))
            next_root = seed_root(blocker)
            require(next_root < root, ("nondecreasing descent", root, blocker, next_root))
            next_root_map[root] = next_root
            path.append(root)
            root = next_root
        if root in memo:
            leaf, depth = memo[root]
        else:
            require(state[root] == SPLITLESS, ("terminal not structural", start, root))
            leaf, depth = root, 0
            memo[root] = (leaf, depth)
        for node in reversed(path):
            depth += 1
            memo[node] = (leaf, depth)
        return memo[start]

    return leaf_from_root, memo, next_root_map


def source_metrics_prefix(
    source: int,
    pairs: tuple[tuple[int, int], ...],
    state: bytearray,
    leaf_from_root,
    detailed: bool = False,
) -> dict[str, object]:
    blockers: list[int] = []
    roots: list[int] = []
    leaves: list[int] = []
    depths: list[int] = []
    rows: list[dict[str, object]] = []
    for left, right in pairs:
        blocker = left if state[left] != GENERATED else right
        require(state[blocker] != GENERATED, ("unblocked hard pair", source, left, right))
        root = seed_root(blocker)
        require(state[root] != GENERATED, ("generated seed root", source, blocker, root))
        leaf, depth = leaf_from_root(root)
        blockers.append(blocker)
        roots.append(root)
        leaves.append(leaf)
        depths.append(depth)
        if detailed:
            rows.append({
                "pair": [left, right],
                "canonical_blocker": blocker,
                "seed_root": root,
                "root_state": STATE_NAMES[state[root]],
                "structural_leaf": leaf,
                "descent_depth": depth,
            })
    root_counts = Counter(roots)
    leaf_counts = Counter(leaves)
    result: dict[str, object] = {
        "h": source,
        "d": len(pairs),
        "distinct_seed_roots": len(root_counts),
        "maximum_same_seed_root": max(root_counts.values(), default=0),
        "distinct_structural_leaves": len(leaf_counts),
        "maximum_same_structural_leaf": max(leaf_counts.values(), default=0),
        "maximum_descent_depth": max(depths, default=0),
        "leaf_power_3_4_B8": {
            "lhs": (len(leaf_counts) + 8) ** 4,
            "rhs": len(pairs) ** 3,
            "falsifier": (len(leaf_counts) + 8) ** 4 < len(pairs) ** 3,
        },
    }
    if detailed:
        result["seed_root_multiplicities"] = [
            [root, count] for root, count in sorted(root_counts.items())
        ]
        result["structural_leaf_multiplicities"] = [
            [leaf, count] for leaf, count in sorted(leaf_counts.items())
        ]
        result["pairs"] = rows
    return result


def better_extreme(candidate: dict[str, object], current: dict[str, object] | None, key: str) -> bool:
    if current is None:
        return True
    candidate_key = (int(candidate[key]), int(candidate["d"]), -int(candidate["h"]))
    current_key = (int(current[key]), int(current["d"]), -int(current["h"]))
    return candidate_key > current_key


def reciprocal_capacity_rows(
    root_domain: set[int],
    leaf_memo: dict[int, tuple[int, int]],
    next_root_map: dict[int, int],
) -> tuple[list[dict[str, int]], list[dict[str, int]]]:
    basin_upper_numerators: Counter[int] = Counter()
    basin_lower_numerators: Counter[int] = Counter()
    basin_counts: Counter[int] = Counter()
    for root in root_domain:
        leaf, _ = leaf_memo[root]
        shifted = root - 1
        basin_lower_numerators[leaf] += RECIPROCAL_SCALE // shifted
        basin_upper_numerators[leaf] += (RECIPROCAL_SCALE + shifted - 1) // shifted
        basin_counts[leaf] += 1
    basin_rows = []
    for leaf, upper_numerator in basin_upper_numerators.items():
        lower_numerator = basin_lower_numerators[leaf]
        upper_ratio = Fraction((leaf - 1) * upper_numerator, RECIPROCAL_SCALE)
        lower_ratio = Fraction((leaf - 1) * lower_numerator, RECIPROCAL_SCALE)
        basin_rows.append({
            "leaf": leaf,
            "root_count": basin_counts[leaf],
            "fixed64_lower_ratio_numerator": lower_ratio.numerator,
            "fixed64_lower_ratio_denominator": lower_ratio.denominator,
            "fixed64_upper_ratio_numerator": upper_ratio.numerator,
            "fixed64_upper_ratio_denominator": upper_ratio.denominator,
        })
    basin_rows.sort(
        key=lambda row: Fraction(
            row["fixed64_upper_ratio_numerator"],
            row["fixed64_upper_ratio_denominator"],
        ),
        reverse=True,
    )
    incoming_upper_numerators: Counter[int] = Counter()
    incoming_lower_numerators: Counter[int] = Counter()
    incoming_counts: Counter[int] = Counter()
    for parent in root_domain:
        child = next_root_map.get(parent)
        if child is None:
            continue
        shifted = parent - 1
        incoming_lower_numerators[child] += RECIPROCAL_SCALE // shifted
        incoming_upper_numerators[child] += (RECIPROCAL_SCALE + shifted - 1) // shifted
        incoming_counts[child] += 1
    incoming_rows = []
    for child, upper_numerator in incoming_upper_numerators.items():
        lower_numerator = incoming_lower_numerators[child]
        upper_ratio = Fraction((child - 1) * upper_numerator, RECIPROCAL_SCALE)
        lower_ratio = Fraction((child - 1) * lower_numerator, RECIPROCAL_SCALE)
        incoming_rows.append({
            "child_root": child,
            "parent_count": incoming_counts[child],
            "fixed64_lower_ratio_numerator": lower_ratio.numerator,
            "fixed64_lower_ratio_denominator": lower_ratio.denominator,
            "fixed64_upper_ratio_numerator": upper_ratio.numerator,
            "fixed64_upper_ratio_denominator": upper_ratio.denominator,
        })
    incoming_rows.sort(
        key=lambda row: Fraction(
            row["fixed64_upper_ratio_numerator"],
            row["fixed64_upper_ratio_denominator"],
        ),
        reverse=True,
    )
    return basin_rows, incoming_rows


def scan_prefix(limit: int) -> dict[str, object]:
    require(limit >= 534, ("limit", limit))
    spf = smallest_prime_factors(limit + 1)
    state = classify_prefix(limit, spf)
    leaf_from_root, leaf_memo, next_root_map = prefix_leaf_function(state, spf)
    hard_count = 0
    maximum_d = 0
    leaf_power_falsifiers = 0
    source_counts_by_leaf: Counter[int] = Counter()
    extremes: dict[str, dict[str, object] | None] = {
        "maximum_same_seed_root": None,
        "maximum_same_structural_leaf": None,
        "maximum_descent_depth": None,
        "maximum_d_minus_distinct_leaves": None,
    }
    min_leaves_by_d: dict[int, tuple[int, int]] = {}
    for source in range(2, limit + 1):
        if state[source] != HARD:
            continue
        hard_count += 1
        pairs = pairs_spf(source, spf)
        metrics = source_metrics_prefix(source, pairs, state, leaf_from_root)
        d_value = int(metrics["d"])
        leaf_count = int(metrics["distinct_structural_leaves"])
        maximum_d = max(maximum_d, d_value)
        leaf_power_falsifiers += int(bool(metrics["leaf_power_3_4_B8"]["falsifier"]))  # type: ignore[index]
        current_min = min_leaves_by_d.get(d_value)
        if current_min is None or (leaf_count, source) < current_min:
            min_leaves_by_d[d_value] = (leaf_count, source)
        detailed_leaves: set[int] = set()
        for left, right in pairs:
            blocker = left if state[left] != GENERATED else right
            root = seed_root(blocker)
            leaf, _ = leaf_from_root(root)
            detailed_leaves.add(leaf)
        for leaf in detailed_leaves:
            source_counts_by_leaf[leaf] += 1
        candidate_values = {
            "maximum_same_seed_root": int(metrics["maximum_same_seed_root"]),
            "maximum_same_structural_leaf": int(metrics["maximum_same_structural_leaf"]),
            "maximum_descent_depth": int(metrics["maximum_descent_depth"]),
            "maximum_d_minus_distinct_leaves": d_value - leaf_count,
        }
        for key, value in candidate_values.items():
            row = dict(metrics)
            row[key] = value
            if better_extreme(row, extremes[key], key):
                extremes[key] = row
    require(hard_count > 0, "no hard source")
    detailed_extremes: dict[str, object] = {}
    for key, row in extremes.items():
        require(row is not None, ("missing extreme", key))
        source = int(row["h"])
        detailed_extremes[key] = source_metrics_prefix(
            source, pairs_spf(source, spf), state, leaf_from_root, detailed=True
        )
    capacity_rows = [
        {
            "leaf": leaf,
            "source_count": count,
            "capacity_numerator": count * (leaf - 1),
            "capacity_denominator": limit + 1,
        }
        for leaf, count in source_counts_by_leaf.items()
    ]
    capacity_rows.sort(
        key=lambda row: (int(row["capacity_numerator"]), int(row["leaf"])),
        reverse=True,
    )
    observed_root_domain = set(leaf_memo)
    observed_basin_rows, observed_incoming_rows = reciprocal_capacity_rows(
        observed_root_domain, leaf_memo, next_root_map
    )
    all_root_starts = 0
    for root in range(2, limit + 1, 2):
        if allowed(root) and state[root] != GENERATED:
            leaf_from_root(root)
            all_root_starts += 1
    all_root_domain = set(leaf_memo)
    all_basin_rows, all_incoming_rows = reciprocal_capacity_rows(
        all_root_domain, leaf_memo, next_root_map
    )
    return {
        "schema": "C120-same-root-capacity-v1",
        "mode": "prefix",
        "limit": limit,
        "definitions": {
            "canonical_blocker": "left endpoint if missing, otherwise right endpoint",
            "seed_root": "1+(p-1)/2^v2(p-1)",
            "deterministic_descent": "at each nonstructural root use the admissible pair with smallest lower endpoint and its canonical blocker",
            "source_leaf_incidence": "one incidence per distinct terminal leaf per source",
            "basin_ratio_bounds": "sum floor(2^64/(q-1))/2^64 and ceil(2^64/(q-1))/2^64",
        },
        "exactness": {
            "arithmetic": "integers only",
            "closure": "ascending least-fixed-point reconstruction",
            "factor_pairs": "full SPF divisor enumeration",
            "floating_point_acceptance": False,
        },
        "totals": {
            "hard_sources": hard_count,
            "maximum_d": maximum_d,
            "leaf_power_3_4_B8_falsifiers": leaf_power_falsifiers,
            "distinct_terminal_leaves": len(source_counts_by_leaf),
            "descent_memo_entries": len(leaf_memo),
            "all_nongenerated_even_root_starts": all_root_starts,
        },
        "minimum_distinct_leaves_by_d": [
            {"d": d_value, "minimum_leaves": value[0], "first_h": value[1]}
            for d_value, value in sorted(min_leaves_by_d.items())
        ],
        "extremes": detailed_extremes,
        "largest_normalized_leaf_capacities": capacity_rows[:32],
        "largest_observed_leaf_basin_ratios": observed_basin_rows[:32],
        "largest_observed_one_step_incoming_ratios": observed_incoming_rows[:32],
        "largest_all_root_leaf_basin_ratios": all_basin_rows[:32],
        "largest_all_root_one_step_incoming_ratios": all_incoming_rows[:32],
    }


@lru_cache(maxsize=None)
def sparse_pairs(value: int) -> tuple[tuple[int, int], ...]:
    product = value + 1
    return tuple(
        (int(left), int(product // left))
        for left_value in sympy.divisors(product)
        for left in (int(left_value),)
        if 2 <= left < product // left
        and allowed(left)
        and allowed(product // left)
    )


@lru_cache(maxsize=None)
def sparse_state(value: int) -> int:
    if value in (2, 3):
        return GENERATED
    if not allowed(value):
        return OTHER
    pairs = sparse_pairs(value)
    if any(
        sparse_state(left) == GENERATED and sparse_state(right) == GENERATED
        for left, right in pairs
    ):
        return GENERATED
    if not pairs:
        return SPLITLESS
    if value % 2 == 0 and hard_shape(value + 1) is not None:
        return HARD
    return OTHER


@lru_cache(maxsize=None)
def sparse_leaf_from_root(root: int) -> tuple[int, int]:
    require(sparse_state(root) != GENERATED, ("generated sparse root", root))
    if sparse_state(root) == SPLITLESS:
        return root, 0
    pairs = sparse_pairs(root)
    require(bool(pairs), ("sparse nonstructural root without pair", root))
    left, right = pairs[0]
    blocker = left if sparse_state(left) != GENERATED else right
    require(sparse_state(blocker) != GENERATED, ("sparse unblocked pair", root, left, right))
    next_root = seed_root(blocker)
    require(next_root < root, ("sparse nondecreasing descent", root, blocker, next_root))
    leaf, depth = sparse_leaf_from_root(next_root)
    return leaf, depth + 1


def sparse_source_metrics(source: int) -> dict[str, object]:
    require(sparse_state(source) == HARD, ("sparse source not hard", source))
    pairs = sparse_pairs(source)
    rows = []
    roots = []
    leaves = []
    depths = []
    for left, right in pairs:
        blocker = left if sparse_state(left) != GENERATED else right
        require(sparse_state(blocker) != GENERATED, ("sparse unblocked source pair", source, left, right))
        root = seed_root(blocker)
        leaf, depth = sparse_leaf_from_root(root)
        roots.append(root)
        leaves.append(leaf)
        depths.append(depth)
        rows.append({
            "pair": [left, right],
            "canonical_blocker": blocker,
            "seed_root": root,
            "root_state": STATE_NAMES[sparse_state(root)],
            "structural_leaf": leaf,
            "descent_depth": depth,
        })
    root_counts = Counter(roots)
    leaf_counts = Counter(leaves)
    return {
        "h": source,
        "N": source + 1,
        "d": len(pairs),
        "distinct_seed_roots": len(root_counts),
        "maximum_same_seed_root": max(root_counts.values(), default=0),
        "distinct_structural_leaves": len(leaf_counts),
        "maximum_same_structural_leaf": max(leaf_counts.values(), default=0),
        "maximum_descent_depth": max(depths, default=0),
        "leaf_power_3_4_B8": {
            "lhs": (len(leaf_counts) + 8) ** 4,
            "rhs": len(pairs) ** 3,
            "falsifier": (len(leaf_counts) + 8) ** 4 < len(pairs) ** 3,
        },
        "seed_root_multiplicities": [
            [root, count] for root, count in sorted(root_counts.items())
        ],
        "structural_leaf_multiplicities": [
            [leaf, count] for leaf, count in sorted(leaf_counts.items())
        ],
        "pairs": rows,
    }


def scan_sparse(claim_path: Path) -> dict[str, object]:
    claim = json.loads(claim_path.read_text(encoding="ascii"))
    records = claim.get("verification_records")
    require(isinstance(records, list), ("missing verification records", claim_path))
    rows = [sparse_source_metrics(int(record["h"])) for record in records]
    return {
        "schema": "C120-same-root-capacity-v1",
        "mode": "sparse-C117",
        "claim": str(claim_path).replace("\\", "/"),
        "records": rows,
        "totals": {
            "records": len(rows),
            "maximum_d": max((int(row["d"]) for row in rows), default=0),
            "maximum_same_seed_root": max((int(row["maximum_same_seed_root"]) for row in rows), default=0),
            "maximum_same_structural_leaf": max((int(row["maximum_same_structural_leaf"]) for row in rows), default=0),
            "maximum_descent_depth": max((int(row["maximum_descent_depth"]) for row in rows), default=0),
            "leaf_power_3_4_B8_falsifiers": sum(
                int(bool(row["leaf_power_3_4_B8"]["falsifier"])) for row in rows  # type: ignore[index]
            ),
        },
        "cache": {
            "states": sparse_state.cache_info().currsize,
            "pairs": sparse_pairs.cache_info().currsize,
            "leaves": sparse_leaf_from_root.cache_info().currsize,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="mode", required=True)
    prefix = subparsers.add_parser("prefix")
    prefix.add_argument("--limit", type=int, required=True)
    sparse = subparsers.add_parser("sparse")
    sparse.add_argument("--claim", type=Path, required=True)
    for child in (prefix, sparse):
        child.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.mode == "prefix":
        result = scan_prefix(args.limit)
    else:
        result = scan_sparse(args.claim)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    args.output.write_bytes(payload.encode("ascii"))
    print(hashlib.sha256(payload.encode("ascii")).hexdigest().upper())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
