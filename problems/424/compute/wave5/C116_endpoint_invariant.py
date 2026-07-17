#!/usr/bin/env python3
"""Exact prefix test for the C116 structural canonical-blocker invariants."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


OTHER = 0
GENERATED = 1
SPLITLESS = 2
HARD = 3
FNV_OFFSET = 14695981039346656037
FNV_PRIME = 1099511628211
MASK64 = (1 << 64) - 1


def require(condition: bool, message: object) -> None:
    if not condition:
        raise RuntimeError(message)


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def smallest_prime_factors(limit: int) -> list[int]:
    spf = list(range(limit + 1))
    for p in range(2, math.isqrt(limit - 1) + 1):
        if spf[p] != p:
            continue
        for multiple in range(p * p, limit, p):
            if spf[multiple] == multiple:
                spf[multiple] = p
    return spf


def divisors(n: int, spf: list[int]) -> list[int]:
    values = [1]
    while n > 1:
        prime = spf[n]
        old = tuple(values)
        power = 1
        while n % prime == 0:
            n //= prime
            power *= prime
            values.extend(value * power for value in old)
    return values


def admissible_pairs(n: int, spf: list[int]) -> list[tuple[int, int]]:
    product = n + 1
    pairs = []
    for left in divisors(product, spf):
        if left < 2 or left * left >= product:
            continue
        right = product // left
        if allowed(left) and allowed(right):
            pairs.append((left, right))
    return sorted(pairs)


def seed_root(endpoint: int) -> int:
    require(endpoint > 1 and endpoint % 2 == 1, ("odd endpoint", endpoint))
    shifted = endpoint - 1
    return 1 + shifted // (shifted & -shifted)


def fnv_byte(digest: int, value: int) -> int:
    return ((digest ^ value) * FNV_PRIME) & MASK64


def fnv_u64(digest: int, value: int) -> int:
    for shift in range(0, 64, 8):
        digest = fnv_byte(digest, (value >> shift) & 0xFF)
    return digest


def state_name(value: int) -> str:
    return ("other_hole", "generated", "structural_splitless", "hard")[value]


def certificate(
    h: int,
    pairs: list[tuple[int, int]],
    state: bytearray,
    spf: list[int],
    d: int,
    s: int,
    t: int,
    e0: set[int],
    e1: set[int],
) -> dict[str, object]:
    rows = []
    prefix_t = 0
    minimum_prefix_slack = None
    for index, (left, right) in enumerate(pairs, start=1):
        endpoints = []
        counted = False
        for endpoint in (left, right):
            present = state[endpoint] == GENERATED
            root = None if present else seed_root(endpoint)
            structural = False if present else not admissible_pairs(root, spf)
            counted = counted or structural
            endpoints.append(
                {
                    "value": endpoint,
                    "state": state_name(state[endpoint]),
                    "root": root,
                    "root_state": None if root is None else state_name(state[root]),
                    "root_pair_count": None if root is None else len(admissible_pairs(root, spf)),
                }
            )
        canonical = left if state[left] != GENERATED else right
        canonical_root = seed_root(canonical)
        canonical_structural = not admissible_pairs(canonical_root, spf)
        prefix_t += int(canonical_structural)
        prefix_slack = 2 * prefix_t - index + 8
        if minimum_prefix_slack is None or prefix_slack < minimum_prefix_slack:
            minimum_prefix_slack = prefix_slack
        rows.append(
            {
                "prefix_index": index,
                "prefix_t": prefix_t,
                "prefix_slack": prefix_slack,
                "pair": [left, right],
                "counted_in_s": counted,
                "canonical_blocker": canonical,
                "canonical_root": canonical_root,
                "counted_in_t": canonical_structural,
                "endpoints": endpoints,
            }
        )
    return {
        "h": h,
        "product": h + 1,
        "d": d,
        "s": s,
        "t": t,
        "E0_count": len(e0),
        "E1_count": len(e1),
        "endpoint_imbalance_slack": len(e0) + 8 - len(e1),
        "power_bridge_slack": 3 * s - d + 8,
        "canonical_power_slack": 2 * t - d + 8,
        "minimum_canonical_prefix_slack": minimum_prefix_slack,
        "E0": sorted(e0),
        "E1": sorted(e1),
        "pairs": rows,
    }


def scan(limit: int) -> dict[str, object]:
    require(limit >= 534, ("limit", limit))
    spf = smallest_prime_factors(limit + 2)
    state = bytearray(limit + 1)
    root_is_structural: dict[int, bool] = {}
    classification_digest = FNV_OFFSET
    metric_digest = FNV_OFFSET
    hard_count = 0
    maximum_d = 0
    first_failures: dict[str, dict[str, object] | None] = {
        "nonstructural_pairs_le_E1": None,
        "E0_le_twice_s": None,
        "endpoint_imbalance": None,
        "power_bridge": None,
        "canonical_t_le_s": None,
        "canonical_power": None,
        "canonical_prefix_balance": None,
    }
    minimum_endpoint_slack: tuple[int, dict[str, object]] | None = None
    minimum_power_slack: tuple[int, dict[str, object]] | None = None
    minimum_canonical_slack: tuple[int, dict[str, object]] | None = None
    minimum_canonical_prefix_slack: tuple[int, dict[str, object]] | None = None

    for n in range(2, limit + 1):
        pairs: list[tuple[int, int]] = []
        current = OTHER
        if n in (2, 3):
            current = GENERATED
        elif allowed(n):
            pairs = admissible_pairs(n, spf)
            if any(state[left] == GENERATED and state[right] == GENERATED for left, right in pairs):
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
        classification_digest = fnv_byte(classification_digest, current)
        if current != HARD:
            continue

        hard_count += 1
        d = len(pairs)
        maximum_d = max(maximum_d, d)
        e0: set[int] = set()
        e1: set[int] = set()
        s = 0
        t = 0
        prefix_t = 0
        hole_minimum_prefix_slack = None
        for index, (left, right) in enumerate(pairs, start=1):
            missing = 0
            structural_pair = False
            for endpoint in (left, right):
                if state[endpoint] == GENERATED:
                    continue
                missing += 1
                root = seed_root(endpoint)
                require(root < endpoint and root % 2 == 0 and allowed(root), (n, endpoint, root))
                require(state[root] != GENERATED, ("generated root", n, endpoint, root))
                if root not in root_is_structural:
                    root_is_structural[root] = not admissible_pairs(root, spf)
                structural = root_is_structural[root]
                require(structural == (state[root] == SPLITLESS), ("root state", n, endpoint, root))
                if structural:
                    e0.add(endpoint)
                    structural_pair = True
                else:
                    e1.add(endpoint)
            require(missing >= 1, ("unblocked hard pair", n, left, right))
            s += int(structural_pair)
            canonical = left if state[left] != GENERATED else right
            canonical_root = seed_root(canonical)
            canonical_structural = int(root_is_structural[canonical_root])
            t += canonical_structural
            prefix_t += canonical_structural
            prefix_slack = 2 * prefix_t - index + 8
            if (
                hole_minimum_prefix_slack is None
                or prefix_slack < hole_minimum_prefix_slack
            ):
                hole_minimum_prefix_slack = prefix_slack

        require(len(e0 & e1) == 0, ("endpoint partition", n))
        require(len(e0) + len(e1) >= d, ("missing endpoint count", n))
        metric_digest = fnv_u64(metric_digest, n)
        metric_digest = fnv_u64(metric_digest, d)
        metric_digest = fnv_u64(metric_digest, s)
        values = {
            "nonstructural_pairs_le_E1": (d - s, len(e1)),
            "E0_le_twice_s": (len(e0), 2 * s),
            "endpoint_imbalance": (len(e1), len(e0) + 8),
            "power_bridge": (d - 8, 3 * s),
            "canonical_t_le_s": (t, s),
            "canonical_power": (d - 8, 2 * t),
        }
        failed = [name for name, (lhs, rhs) in values.items() if lhs > rhs]
        require(hole_minimum_prefix_slack is not None, ("empty hard pair set", n))
        if hole_minimum_prefix_slack < 0:
            failed.append("canonical_prefix_balance")
        endpoint_slack = len(e0) + 8 - len(e1)
        power_slack = 3 * s - d + 8
        canonical_slack = 2 * t - d + 8
        need_row = (
            failed
            or minimum_endpoint_slack is None
            or endpoint_slack < minimum_endpoint_slack[0]
            or minimum_power_slack is None
            or power_slack < minimum_power_slack[0]
            or minimum_canonical_slack is None
            or canonical_slack < minimum_canonical_slack[0]
            or minimum_canonical_prefix_slack is None
            or hole_minimum_prefix_slack < minimum_canonical_prefix_slack[0]
        )
        row = certificate(n, pairs, state, spf, d, s, t, e0, e1) if need_row else {}
        for name in failed:
            if first_failures[name] is None:
                first_failures[name] = row
        if minimum_endpoint_slack is None or endpoint_slack < minimum_endpoint_slack[0]:
            minimum_endpoint_slack = (endpoint_slack, row)
        if minimum_power_slack is None or power_slack < minimum_power_slack[0]:
            minimum_power_slack = (power_slack, row)
        if minimum_canonical_slack is None or canonical_slack < minimum_canonical_slack[0]:
            minimum_canonical_slack = (canonical_slack, row)
        if (
            minimum_canonical_prefix_slack is None
            or hole_minimum_prefix_slack < minimum_canonical_prefix_slack[0]
        ):
            minimum_canonical_prefix_slack = (hole_minimum_prefix_slack, row)

    require(
        minimum_endpoint_slack is not None
        and minimum_power_slack is not None
        and minimum_canonical_slack is not None
        and minimum_canonical_prefix_slack is not None,
        "no hard holes",
    )
    return {
        "schema": "C116-endpoint-invariant-v2",
        "limit": limit,
        "exactness": {
            "arithmetic": "integers only",
            "closure": "independent ascending least-fixed-point reconstruction",
            "factor_pairs": "full SPF divisor enumeration",
            "structural_test": "literal empty admissible-pair set, cross-checked against state",
            "floating_point_acceptance": False,
        },
        "totals": {"hard_holes": hard_count, "maximum_d": maximum_d},
        "first_failures": first_failures,
        "minimum_endpoint_imbalance_slack": minimum_endpoint_slack[1],
        "minimum_power_bridge_slack": minimum_power_slack[1],
        "minimum_canonical_power_slack": minimum_canonical_slack[1],
        "minimum_canonical_prefix_slack": minimum_canonical_prefix_slack[1],
        "digests": {
            "algorithm": "FNV-1a-64 little-endian",
            "classification_2_through_limit": f"{classification_digest:016x}",
            "hard_h_d_s": f"{metric_digest:016x}",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = scan(args.limit)
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    args.output.write_bytes(encoded.encode("ascii"))
    print(hashlib.sha256(encoded.encode("ascii")).hexdigest().upper())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
