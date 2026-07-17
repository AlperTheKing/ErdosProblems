#!/usr/bin/env python3
"""Exact tests for arithmetic charges proposed for the C114 square block."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path


GENERATED = 1
SPLITLESS = 2
HARD = 3


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def full_spf(limit: int) -> list[int]:
    spf = list(range(limit + 1))
    for p in range(2, math.isqrt(limit) + 1):
        if spf[p] != p:
            continue
        for multiple in range(p * p, limit + 1, p):
            if spf[multiple] == multiple:
                spf[multiple] = p
    return spf


def factorization(n: int, spf: list[int]) -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []
    while n > 1:
        p = spf[n]
        exponent = 0
        while n % p == 0:
            n //= p
            exponent += 1
        result.append((p, exponent))
    return result


def divisors_from_factors(factors: list[tuple[int, int]]) -> list[int]:
    result = [1]
    for p, exponent in factors:
        old = tuple(result)
        power = 1
        for _ in range(exponent):
            power *= p
            result.extend(d * power for d in old)
    return result


def tau_from_factors(factors: list[tuple[int, int]]) -> int:
    result = 1
    for _, exponent in factors:
        result *= exponent + 1
    return result


def tau(n: int, spf: list[int]) -> int:
    return tau_from_factors(factorization(n, spf))


def admissible_pairs(product: int, spf: list[int]) -> list[tuple[int, int]]:
    result = []
    for left in divisors_from_factors(factorization(product, spf)):
        if left < 2 or left * left >= product:
            continue
        right = product // left
        if allowed(left) and allowed(right):
            result.append((left, right))
    return result


def seed_root(endpoint: int) -> int:
    shifted = endpoint - 1
    return 1 + shifted // (shifted & -shifted)


def dyadic_bin(root: int) -> int:
    return (root - 1).bit_length() - 1


def ceil_sqrt(n: int) -> int:
    root = math.isqrt(n)
    return root if root * root == n else root + 1


def frac_json(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def set_failure(store: dict, name: str, condition: bool, row: dict) -> None:
    if not condition and store[name] is None:
        store[name] = row


def scan_prefix(limit: int) -> dict:
    spf = full_spf(limit + 1)
    state = bytearray(limit + 1)
    maximum_d_by_root: dict[int, int] = {}
    q_by_root: dict[int, int] = {}
    certificate_by_root: dict[int, dict] = {}
    co_roots_by_root: dict[int, set[int]] = {}
    hard_sources = 0
    all_upgrades = 0
    positive_q_upgrades = 0
    maximum_d = 0
    first_failures = {
        "endpoint_tau_ge_d": None,
        "cofactor_tau_ge_d": None,
        "both_endpoint_and_cofactor_pay_sqrt_2d": None,
        "chain_exponent_square_ge_q": None,
        "root_shift_tau_square_ge_q": None,
        "all_source_roots_square_ge_q": None,
        "reducible_source_roots_square_ge_q": None,
        "source_smaller_roots_square_ge_q": None,
        "historical_co_roots_square_ge_q": None,
        "historical_smaller_co_roots_square_ge_q": None,
        "individual_left_gap_pays_capped_sqrt_q": None,
        "selected_active_gap_pays_m": None,
        "selected_prefix_pays_m": None,
        "c108_prefix_pays_capped_sqrt_q": None,
    }

    for h in range(2, limit + 1):
        pairs: list[tuple[int, int]] = []
        current = 0
        if h in (2, 3):
            current = GENERATED
        elif allowed(h):
            pairs = admissible_pairs(h + 1, spf)
            if any(state[a] == GENERATED and state[b] == GENERATED for a, b in pairs):
                current = GENERATED
            elif not pairs:
                current = SPLITLESS
            elif h % 2 == 0:
                product = h + 1
                seed_three_easy = (
                    product % 3 == 0
                    and product // 3 != 3
                    and allowed(product // 3)
                )
                if not seed_three_easy:
                    current = HARD
        state[h] = current
        if current != HARD:
            continue

        hard_sources += 1
        d = len(pairs)
        q = d - 1
        maximum_d = max(maximum_d, d)
        all_roots: set[int] = set()
        reducible_endpoints: dict[int, int] = {}
        pair_rows = []
        for left, right in pairs:
            missing_rows = []
            for endpoint in (left, right):
                if state[endpoint] == GENERATED:
                    continue
                root = seed_root(endpoint)
                all_roots.add(root)
                missing_rows.append(
                    {"endpoint": endpoint, "root": root, "root_state": state[root]}
                )
                if state[root] != SPLITLESS:
                    old = reducible_endpoints.get(root)
                    if old is None or endpoint < old:
                        reducible_endpoints[root] = endpoint
            pair_rows.append({"pair": [left, right], "missing": missing_rows})

        source_base = {
            "h": h,
            "d": d,
            "q": q,
            "all_root_count": len(all_roots),
            "reducible_root_count": len(reducible_endpoints),
            "factorization_h_plus_1": factorization(h + 1, spf),
            "pairs": pair_rows,
        }
        set_failure(
            first_failures,
            "all_source_roots_square_ge_q",
            len(all_roots) ** 2 >= q,
            source_base,
        )
        set_failure(
            first_failures,
            "reducible_source_roots_square_ge_q",
            len(reducible_endpoints) ** 2 >= q,
            source_base,
        )

        for root, endpoint in sorted(reducible_endpoints.items()):
            old_d = maximum_d_by_root.get(root, 0)
            if d <= old_d:
                continue
            all_upgrades += 1
            old_q = old_d - 1 if old_d else 0
            maximum_d_by_root[root] = d
            old_co_roots = co_roots_by_root.setdefault(root, set())
            old_co_roots.update(all_roots - {root})
            cofactor = (h + 1) // endpoint
            tau_endpoint = tau(endpoint, spf)
            tau_cofactor = tau(cofactor, spf)
            chain_exponent = (endpoint - 1 & -(endpoint - 1)).bit_length() - 1
            tau_root_shift = tau(root + 1, spf)
            row = {
                **source_base,
                "root": root,
                "j": dyadic_bin(root),
                "old_q": old_q,
                "new_q": q,
                "endpoint": endpoint,
                "chain_exponent": chain_exponent,
                "cofactor": cofactor,
                "tau_endpoint": tau_endpoint,
                "tau_cofactor": tau_cofactor,
                "tau_product": tau_endpoint * tau_cofactor,
                "tau_root_plus_1": tau_root_shift,
                "historical_co_root_count": len(old_co_roots),
                "historical_smaller_co_root_count": sum(
                    co_root < root for co_root in old_co_roots
                ),
                "source_smaller_root_count": sum(
                    source_root < root for source_root in all_roots
                ),
            }
            if tau_endpoint * tau_cofactor < 2 * d:
                raise AssertionError(("divisor submultiplicativity sanity", row))
            set_failure(first_failures, "endpoint_tau_ge_d", tau_endpoint >= d, row)
            set_failure(first_failures, "cofactor_tau_ge_d", tau_cofactor >= d, row)
            set_failure(
                first_failures,
                "both_endpoint_and_cofactor_pay_sqrt_2d",
                min(tau_endpoint, tau_cofactor) ** 2 >= 2 * d,
                row,
            )
            set_failure(
                first_failures,
                "chain_exponent_square_ge_q",
                chain_exponent * chain_exponent >= q,
                row,
            )
            set_failure(
                first_failures,
                "root_shift_tau_square_ge_q",
                tau_root_shift * tau_root_shift >= q,
                row,
            )
            set_failure(
                first_failures,
                "source_smaller_roots_square_ge_q",
                row["source_smaller_root_count"] ** 2 >= q,
                row,
            )
            set_failure(
                first_failures,
                "historical_co_roots_square_ge_q",
                row["historical_co_root_count"] ** 2 >= q,
                row,
            )
            set_failure(
                first_failures,
                "historical_smaller_co_roots_square_ge_q",
                row["historical_smaller_co_root_count"] ** 2 >= q,
                row,
            )
            if q > 0:
                positive_q_upgrades += 1
                q_by_root[root] = q
                certificate_by_root[root] = row

    bins: dict[int, list[tuple[int, int]]] = {}
    for root, q in q_by_root.items():
        bins.setdefault(dyadic_bin(root), []).append((root, q))
    for roots in bins.values():
        roots.sort()

    gap_failures = {
        "individual_left_gap_pays_capped_sqrt_q": None,
        "selected_active_gap_pays_m": None,
        "selected_prefix_pays_m": None,
        "c108_prefix_pays_capped_sqrt_q": None,
    }
    max_q = max(q_by_root.values(), default=0)
    max_m = math.isqrt(max_q)
    for j, roots in sorted(bins.items()):
        prefix = 0
        for index, (root, q) in enumerate(roots):
            weight = min(ceil_sqrt(q), j)
            if index > 0:
                gap = root - roots[index - 1][0]
                if gap_failures["individual_left_gap_pays_capped_sqrt_q"] is None and weight > gap:
                    gap_failures["individual_left_gap_pays_capped_sqrt_q"] = {
                        "limit": limit,
                        "j": j,
                        "previous_root": roots[index - 1][0],
                        "root": root,
                        "q": q,
                        "weight": weight,
                        "gap": gap,
                        "certificate": certificate_by_root[root],
                    }
                prefix += weight
                deadline = root - 1 - (1 << j)
                if gap_failures["c108_prefix_pays_capped_sqrt_q"] is None and prefix > deadline:
                    gap_failures["c108_prefix_pays_capped_sqrt_q"] = {
                        "limit": limit,
                        "j": j,
                        "root": root,
                        "prefix_weight_excluding_least": prefix,
                        "deadline": deadline,
                    }

        for m in range(1, min(max_m, j - 1) + 1):
            active = [(root, q) for root, q in roots if q > m * m]
            selected_prefix = 0
            for index, (root, q) in enumerate(active):
                if index == 0:
                    continue
                gap = root - active[index - 1][0]
                if gap_failures["selected_active_gap_pays_m"] is None and m > gap:
                    gap_failures["selected_active_gap_pays_m"] = {
                        "limit": limit,
                        "j": j,
                        "m": m,
                        "previous_root": active[index - 1][0],
                        "root": root,
                        "q": q,
                        "gap": gap,
                    }
                selected_prefix += m
                deadline = root - 1 - (1 << j)
                if gap_failures["selected_prefix_pays_m"] is None and selected_prefix > deadline:
                    gap_failures["selected_prefix_pays_m"] = {
                        "limit": limit,
                        "j": j,
                        "m": m,
                        "root": root,
                        "prefix_weight_excluding_least": selected_prefix,
                        "deadline": deadline,
                    }

    for name, failure in gap_failures.items():
        first_failures[name] = failure

    square_blocks = []
    for m in range(1, max_m + 1):
        block = Fraction()
        active_roots = 0
        for root, q in q_by_root.items():
            j = dyadic_bin(root)
            height = max(0, min(q, j * j, (m + 1) ** 2) - m * m)
            if height:
                active_roots += 1
                block += Fraction(height, 1 << j)
        square_blocks.append(
            {
                "m": m,
                "active_roots": active_roots,
                "B_m": frac_json(block),
                "B_m_over_m_cubed": frac_json(block / (m**3)),
            }
        )

    return {
        "limit": limit,
        "hard_sources": hard_sources,
        "all_root_upgrade_events": all_upgrades,
        "positive_q_root_upgrade_events": positive_q_upgrades,
        "distinct_reducible_roots": len(q_by_root),
        "maximum_d": maximum_d,
        "first_failures": first_failures,
        "square_blocks": square_blocks,
    }


def synthetic_divisor_rich_bank(j: int) -> dict:
    minus_primes = [5, 11, 17, 23, 29]
    multiplier = math.prod(minus_primes)
    if (1 << j) + 1 <= multiplier:
        raise ValueError("synthetic bin must lie above the multiplier")
    valid_roots = []
    for denominator in range(1 << j, 1 << (j + 1)):
        root = denominator + 1
        if root % 6 != 0:
            continue
        endpoint = 2 * root - 1
        if math.gcd(endpoint, multiplier) != 1:
            continue
        valid_roots.append(root)

    sample_rows = []
    for root in valid_roots[:8]:
        endpoint = 2 * root - 1
        product = endpoint * multiplier
        lower_pairs = []
        for mask in range(1 << len(minus_primes)):
            if mask.bit_count() % 2 == 0:
                continue
            left = 1
            for index, prime in enumerate(minus_primes):
                if mask & (1 << index):
                    left *= prime
            right = product // left
            if not (left < right and allowed(left) and allowed(right) and left * right == product):
                raise AssertionError(("synthetic pair", root, left, right))
            lower_pairs.append([left, right])
        if len(lower_pairs) != 16:
            raise AssertionError(("synthetic pair count", root, len(lower_pairs)))
        sample_rows.append(
            {
                "root": root,
                "endpoint": endpoint,
                "source_plus_1": product,
                "certified_admissible_pairs": lower_pairs,
            }
        )

    return {
        "j": j,
        "bin_capacity": 1 << j,
        "minus_primes": minus_primes,
        "fixed_multiplier": multiplier,
        "certified_pair_lower_bound_per_source": 16,
        "valid_root_count": len(valid_roots),
        "valid_root_density": frac_json(Fraction(len(valid_roots), 1 << j)),
        "sample_rows": sample_rows,
        "scope": "arithmetic superset only; no source is asserted hard or any root missing",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, required=True)
    parser.add_argument("--synthetic-bin", type=int, default=20)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.limit < 2:
        raise ValueError("limit must be at least 2")
    result = {
        "schema": "C118-selected-square-probe-v1",
        "arithmetic": "exact integers and Fraction only",
        "prefix": scan_prefix(args.limit),
        "divisor_rich_multiple_obstruction": synthetic_divisor_rich_bank(
            args.synthetic_bin
        ),
    }
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    args.output.write_bytes(payload.encode("ascii"))
    print(hashlib.sha256(payload.encode("ascii")).hexdigest().upper())


if __name__ == "__main__":
    main()
