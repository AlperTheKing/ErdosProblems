#!/usr/bin/env python3
"""Exact eventwise probe for the C114 integrated Carleson gate."""

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


def failure_certificate(
    *,
    h: int,
    d: int,
    pairs: list[dict],
    all_roots: set[int],
    reducible_roots: set[int],
    upgrades: list[dict],
    lhs: int,
    rhs: int,
) -> dict:
    return {
        "h": h,
        "d": d,
        "lhs": lhs,
        "rhs": rhs,
        "all_roots": sorted(all_roots),
        "reducible_roots": sorted(reducible_roots),
        "upgrades": upgrades,
        "pairs": pairs,
    }


def analyze(limit: int) -> dict:
    spf = full_spf(limit + 1)
    state = bytearray(limit + 1)
    maximum_d: dict[int, int] = {}
    co_roots: dict[int, set[int]] = {}
    q_by_bin: dict[int, dict[int, int]] = {}
    first_failures: dict[str, dict | None] = {
        "source_mixed_A_times_M_ge_q": None,
        "source_with_reducible_has_A_ge_d": None,
        "source_with_reducible_has_A_ge_q": None,
        "source_A_times_M_pays_total_q_increment": None,
        "source_A_pays_total_sqrt_increment": None,
        "source_incidence_mass_pays_weighted_sqrt_increment": None,
        "source_root_mass_pays_weighted_sqrt_increment": None,
        "root_distinct_co_roots_ge_q": None,
        "new_co_roots_pay_q_increment": None,
        "integrated_C_equals_1": None,
    }
    hard_sources = 0
    upgrade_sources = 0
    root_upgrade_events = 0
    gate_tests = 0
    maximum_d_seen = 0
    best_gate: tuple[Fraction, dict] | None = None

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
        if current != HARD:
            continue

        hard_sources += 1
        d = len(pairs)
        maximum_d_seen = max(maximum_d_seen, d)
        pair_rows = []
        all_roots: set[int] = set()
        reducible_roots: set[int] = set()
        pair_root_sets: list[set[int]] = []
        for left, right in pairs:
            missing = []
            roots_here: set[int] = set()
            for endpoint in (left, right):
                if state[endpoint] == GENERATED:
                    continue
                root = seed_root(endpoint)
                if state[root] == GENERATED:
                    raise AssertionError(("generated witness root", n, endpoint, root))
                roots_here.add(root)
                all_roots.add(root)
                if state[root] != SPLITLESS:
                    reducible_roots.add(root)
                missing.append(
                    {"endpoint": endpoint, "root": root, "root_state": state[root]}
                )
            if not missing:
                raise AssertionError(("unblocked hard pair", n, left, right))
            pair_root_sets.append(roots_here)
            pair_rows.append({"pair": [left, right], "missing": missing})

        q = d - 1
        if reducible_roots and len(all_roots) < q:
            if first_failures["source_with_reducible_has_A_ge_q"] is None:
                first_failures["source_with_reducible_has_A_ge_q"] = failure_certificate(
                    h=n,
                    d=d,
                    pairs=pair_rows,
                    all_roots=all_roots,
                    reducible_roots=reducible_roots,
                    upgrades=[],
                    lhs=len(all_roots),
                    rhs=q,
                )
        if reducible_roots and len(all_roots) < d:
            if first_failures["source_with_reducible_has_A_ge_d"] is None:
                first_failures["source_with_reducible_has_A_ge_d"] = failure_certificate(
                    h=n,
                    d=d,
                    pairs=pair_rows,
                    all_roots=all_roots,
                    reducible_roots=reducible_roots,
                    upgrades=[],
                    lhs=len(all_roots),
                    rhs=d,
                )
        if reducible_roots and len(all_roots) * len(reducible_roots) < q:
            if first_failures["source_mixed_A_times_M_ge_q"] is None:
                first_failures["source_mixed_A_times_M_ge_q"] = failure_certificate(
                    h=n,
                    d=d,
                    pairs=pair_rows,
                    all_roots=all_roots,
                    reducible_roots=reducible_roots,
                    upgrades=[],
                    lhs=len(all_roots) * len(reducible_roots),
                    rhs=q,
                )

        upgrades = []
        total_q_increment = 0
        total_sqrt_increment = 0
        weighted_sqrt_increment = Fraction()
        for root in sorted(reducible_roots):
            old_co_roots = co_roots.setdefault(root, set())
            additions = (all_roots - {root}) - old_co_roots
            old_co_roots.update(all_roots - {root})
            old_d = maximum_d.get(root, 0)
            if d <= old_d:
                continue
            old_q = old_d - 1 if old_d else 0
            new_q = q
            old_sqrt = ceil_sqrt(old_q) if old_q else 0
            new_sqrt = ceil_sqrt(new_q) if new_q else 0
            q_increment = new_q - old_q
            sqrt_increment = new_sqrt - old_sqrt
            j = dyadic_bin(root)
            upgrades.append(
                {
                    "root": root,
                    "j": j,
                    "old_q": old_q,
                    "new_q": new_q,
                    "q_increment": q_increment,
                    "sqrt_increment": sqrt_increment,
                }
            )
            total_q_increment += q_increment
            total_sqrt_increment += sqrt_increment
            weighted_sqrt_increment += Fraction(sqrt_increment, 1 << j)
            maximum_d[root] = d
            q_by_bin.setdefault(j, {})[root] = new_q
            root_upgrade_events += 1

            root_candidates = (
                ("root_distinct_co_roots_ge_q", len(old_co_roots), new_q),
                ("new_co_roots_pay_q_increment", len(additions), q_increment),
            )
            for name, lhs, rhs in root_candidates:
                if lhs < rhs and first_failures[name] is None:
                    first_failures[name] = failure_certificate(
                        h=n,
                        d=d,
                        pairs=pair_rows,
                        all_roots=all_roots,
                        reducible_roots=reducible_roots,
                        upgrades=[upgrades[-1]],
                        lhs=lhs,
                        rhs=rhs,
                    )

        if not upgrades:
            continue
        upgrade_sources += 1

        source_root_mass = sum((Fraction(1, 1 << dyadic_bin(r)) for r in all_roots), Fraction())
        source_incidence_mass = sum(
            (
                sum((Fraction(1, 1 << dyadic_bin(r)) for r in roots), Fraction())
                for roots in pair_root_sets
            ),
            Fraction(),
        )
        candidates = (
            (
                "source_A_times_M_pays_total_q_increment",
                len(all_roots) * len(reducible_roots),
                total_q_increment,
            ),
            (
                "source_A_pays_total_sqrt_increment",
                len(all_roots),
                total_sqrt_increment,
            ),
        )
        for name, lhs, rhs in candidates:
            if lhs < rhs and first_failures[name] is None:
                first_failures[name] = failure_certificate(
                    h=n,
                    d=d,
                    pairs=pair_rows,
                    all_roots=all_roots,
                    reducible_roots=reducible_roots,
                    upgrades=upgrades,
                    lhs=lhs,
                    rhs=rhs,
                )

        mass_candidates = (
            (
                "source_incidence_mass_pays_weighted_sqrt_increment",
                source_incidence_mass,
            ),
            ("source_root_mass_pays_weighted_sqrt_increment", source_root_mass),
        )
        for name, budget in mass_candidates:
            if budget < weighted_sqrt_increment and first_failures[name] is None:
                certificate = failure_certificate(
                    h=n,
                    d=d,
                    pairs=pair_rows,
                    all_roots=all_roots,
                    reducible_roots=reducible_roots,
                    upgrades=upgrades,
                    lhs=weighted_sqrt_increment.numerator * budget.denominator,
                    rhs=budget.numerator * weighted_sqrt_increment.denominator,
                )
                certificate["weighted_sqrt_increment"] = frac_json(weighted_sqrt_increment)
                certificate["budget"] = frac_json(budget)
                first_failures[name] = certificate

        lx = 1 + n.bit_length() - 1
        max_q = max((value for roots in q_by_bin.values() for value in roots.values()), default=0)
        for threshold in range(1, max_q + 1):
            cutoff = ceil_sqrt(threshold)
            tail = sum(
                (
                    Fraction(sum(value >= threshold for value in roots.values()), 1 << j)
                    for j, roots in q_by_bin.items()
                    if j >= cutoff
                ),
                Fraction(),
            )
            ratio_squared = Fraction(threshold * tail * tail, lx * lx)
            gate_tests += 1
            location = {
                "X": n,
                "D": threshold,
                "J": cutoff,
                "L_X": lx,
                "tail": frac_json(tail),
                "C_squared": frac_json(ratio_squared),
            }
            if best_gate is None or ratio_squared > best_gate[0]:
                best_gate = (ratio_squared, location)
            if ratio_squared > 1 and first_failures["integrated_C_equals_1"] is None:
                first_failures["integrated_C_equals_1"] = location

    endpoint_lx = 1 + limit.bit_length() - 1
    endpoint_rows = []
    endpoint_layer_sum = Fraction()
    endpoint_capped_energy = Fraction()
    max_q = max((value for roots in q_by_bin.values() for value in roots.values()), default=0)
    for threshold in range(1, max_q + 1):
        cutoff = ceil_sqrt(threshold)
        tail = sum(
            (
                Fraction(sum(value >= threshold for value in roots.values()), 1 << j)
                for j, roots in q_by_bin.items()
                if j >= cutoff
            ),
            Fraction(),
        )
        endpoint_layer_sum += tail
        endpoint_rows.append(
            {"D": threshold, "J": cutoff, "tail": frac_json(tail)}
        )
    for j, roots in q_by_bin.items():
        endpoint_capped_energy += Fraction(
            sum(min(value, j * j) for value in roots.values()), 1 << j
        )
    if endpoint_layer_sum != endpoint_capped_energy:
        raise AssertionError(("square-layer cake mismatch", endpoint_layer_sum, endpoint_capped_energy))
    if best_gate is None:
        best_gate = (Fraction(), {})

    return {
        "schema": "C114-integrated-carleson-probe-v1",
        "limit": limit,
        "arithmetic": "exact integers and Fraction only",
        "totals": {
            "hard_sources": hard_sources,
            "upgrade_sources": upgrade_sources,
            "root_upgrade_events": root_upgrade_events,
            "distinct_reducible_roots_with_positive_q": sum(len(v) for v in q_by_bin.values()),
            "maximum_d": maximum_d_seen,
            "eventwise_gate_tests": gate_tests,
        },
        "first_failures": first_failures,
        "maximum_eventwise_integrated_ratio": best_gate[1],
        "endpoint": {
            "L_X": endpoint_lx,
            "square_layer_cake_identity": True,
            "sum_of_threshold_tails": frac_json(endpoint_layer_sum),
            "capped_upgrade_energy": frac_json(endpoint_capped_energy),
            "threshold_tails": endpoint_rows,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.limit < 2:
        raise ValueError("limit must be at least 2")
    result = analyze(args.limit)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    args.output.write_bytes(payload.encode("ascii"))
    print(hashlib.sha256(payload.encode("ascii")).hexdigest().upper())


if __name__ == "__main__":
    main()
