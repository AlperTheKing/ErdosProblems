#!/usr/bin/env python3
"""Independent finite audit for the C99 all-prime hard-hole sieve."""

from __future__ import annotations

import argparse
import json
import math


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def smallest_prime_factors(limit: int) -> list[int]:
    spf = list(range(limit + 1))
    for p in range(2, math.isqrt(limit) + 1):
        if spf[p] != p:
            continue
        for n in range(p * p, limit + 1, p):
            if spf[n] == n:
                spf[n] = p
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


def divisors_from_factorization(factors: list[tuple[int, int]]) -> list[int]:
    divisors = [1]
    for p, exponent in factors:
        old = tuple(divisors)
        power = 1
        for _ in range(exponent):
            power *= p
            divisors.extend(d * power for d in old)
    return divisors


def admissible_pairs(n: int, spf: list[int]) -> list[tuple[int, int]]:
    successor = n + 1
    pairs: list[tuple[int, int]] = []
    for a in divisors_from_factorization(factorization(successor, spf)):
        if a < 2 or a * a >= successor:
            continue
        b = successor // a
        if allowed(a) and allowed(b):
            pairs.append((a, b))
    pairs.sort()
    return pairs


def seed_root(n: int) -> int:
    while n % 2 == 1:
        n = (n + 1) // 2
    return n


def hard_shape(n: int, pairs: list[tuple[int, int]]) -> bool:
    if n % 2 or not pairs:
        return False
    successor = n + 1
    seed_three_easy = (
        successor % 3 == 0
        and successor // 3 != 3
        and allowed(successor // 3)
    )
    return not seed_three_easy


def exact_residue_two_divisors(
    r_factors: list[tuple[int, int]],
) -> tuple[int, int, int, bool]:
    tau_plus = 1
    tau_minus = 1
    omega = 0
    all_minus_exponents_even = True
    for p, exponent in r_factors:
        if p == 3:
            raise AssertionError("R must be coprime to 3")
        omega += 1
        if p % 3 == 1:
            tau_plus *= exponent + 1
        else:
            tau_minus *= exponent + 1
            if exponent % 2:
                all_minus_exponents_even = False
    delta = int(all_minus_exponents_even)
    residue_two_count = tau_plus * (tau_minus - delta) // 2
    return residue_two_count, tau_plus, tau_minus, bool(delta)


def audit(limit: int, exponent: float) -> dict[str, object]:
    if limit < 534:
        raise ValueError("limit must be at least 534 to audit the trap failure")

    spf = smallest_prime_factors(limit + 1)
    generated = bytearray(limit + 1)
    generated[2] = 1
    generated[3] = 1
    structural_even = bytearray(limit + 1)
    hard_holes: list[int] = []
    hard_data: dict[int, tuple[list[tuple[int, int]], set[int]]] = {}

    formula_failures: list[dict[str, object]] = []
    lower_bound_failures: list[dict[str, object]] = []
    first_direct_trap_failure: dict[str, object] | None = None
    first_trap_failure_by_min_pairs: dict[int, dict[str, object]] = {}
    nontrapped_hard_count = 0
    nontrapped_above_log_power = 0
    maximum_nontrapped_pairs = 0
    minus_parity_cases = {"all_even": 0, "some_odd": 0}
    d0_count = 0
    log_power_count = 0
    max_omega = 0
    max_pairs = 0

    loglog = math.log(math.log(limit))
    d0 = loglog * loglog
    log_power_threshold = math.log(limit) ** exponent

    for n in range(2, limit + 1):
        if not allowed(n):
            continue
        pairs = admissible_pairs(n, spf)
        if n not in (2, 3):
            generated[n] = any(generated[a] and generated[b] for a, b in pairs)

        if n not in (2, 3) and n % 2 == 0 and not pairs:
            structural_even[n] = 1

        if generated[n] or not hard_shape(n, pairs):
            continue

        successor = n + 1
        epsilon = int(successor % 3 == 0)
        r = successor // (3 if epsilon else 1)
        if r % 3 != 1:
            raise AssertionError(f"bad C55 normalization at h={n}")
        r_factors = factorization(r, spf)
        residue_two_count, tau_plus, tau_minus, all_even = (
            exact_residue_two_divisors(r_factors)
        )
        minus_parity_cases["all_even" if all_even else "some_odd"] += 1
        expected_pairs = residue_two_count if epsilon else residue_two_count // 2
        if len(pairs) != expected_pairs:
            formula_failures.append(
                {
                    "h": n,
                    "actual": len(pairs),
                    "expected": expected_pairs,
                    "epsilon": epsilon,
                    "R": r,
                }
            )

        omega = len(r_factors)
        if 4 * len(pairs) < 2**omega:
            lower_bound_failures.append(
                {"h": n, "pairs": len(pairs), "omega": omega, "R": r}
            )

        roots: set[int] = set()
        for a, b in pairs:
            for endpoint in (a, b):
                if not generated[endpoint]:
                    root = seed_root(endpoint)
                    if generated[root]:
                        raise AssertionError(
                            f"missing endpoint {endpoint} has generated root {root}"
                        )
                    roots.add(root)

        outside = sorted(root for root in roots if not structural_even[root])
        if outside:
            failure = {
                "h": n,
                "pairs": pairs,
                "pair_count": len(pairs),
                "witness_roots": sorted(roots),
                "non_splitless_roots": outside,
            }
            if first_direct_trap_failure is None:
                first_direct_trap_failure = {
                    "h": n,
                    "pairs": pairs,
                    "pair_count": len(pairs),
                    "witness_roots": sorted(roots),
                    "non_splitless_roots": outside,
                }
            for minimum in range(1, len(pairs) + 1):
                first_trap_failure_by_min_pairs.setdefault(minimum, failure)
            nontrapped_hard_count += 1
            nontrapped_above_log_power += len(pairs) > log_power_threshold
            maximum_nontrapped_pairs = max(maximum_nontrapped_pairs, len(pairs))

        hard_holes.append(n)
        hard_data[n] = (pairs, roots)
        max_omega = max(max_omega, omega)
        max_pairs = max(max_pairs, len(pairs))
        d0_count += len(pairs) <= d0
        log_power_count += len(pairs) <= log_power_threshold

    structural_mass = math.fsum(
        1.0 / (n - 1) for n in range(4, limit + 1, 2) if structural_even[n]
    )
    all_even_hole_root_mass = math.fsum(
        1.0 / (n - 1)
        for n in range(4, limit + 1, 2)
        if allowed(n) and not generated[n]
    )
    neighborhood_union = set().union(*(roots for _, roots in hard_data.values()))
    neighborhood_mass = math.fsum(1.0 / (r - 1) for r in neighborhood_union)

    trap_534 = hard_data.get(534)
    if trap_534 is None:
        raise AssertionError("534 was not reconstructed as a hard hole")

    result = {
        "limit": limit,
        "hard_holes": len(hard_holes),
        "generated_allowed": sum(generated),
        "structural_even_roots": sum(structural_even),
        "all_prime_formula_failures": formula_failures,
        "all_prime_lower_bound_failures": lower_bound_failures,
        "maximum_omega_R": max_omega,
        "maximum_admissible_pairs": max_pairs,
        "minus_exponent_parity_cases": minus_parity_cases,
        "thresholds": {
            "D0_loglog_squared": d0,
            "D0_hard_count": d0_count,
            "log_power_exponent": exponent,
            "log_power_threshold": log_power_threshold,
            "log_power_hard_count": log_power_count,
        },
        "reciprocal_masses": {
            "structural_even": structural_mass,
            "structural_over_sqrt_log": structural_mass / math.sqrt(math.log(limit)),
            "all_even_hole_roots": all_even_hole_root_mass,
            "hard_witness_root_union": neighborhood_mass,
            "hard_witness_root_union_size": len(neighborhood_union),
        },
        "first_direct_splitless_trap_failure": first_direct_trap_failure,
        "direct_splitless_trap_audit": {
            "nontrapped_hard_count": nontrapped_hard_count,
            "nontrapped_above_log_power_threshold": nontrapped_above_log_power,
            "maximum_nontrapped_pair_count": maximum_nontrapped_pairs,
            "first_failure_by_minimum_pair_count": first_trap_failure_by_min_pairs,
        },
        "h_534_audit": {
            "pairs": trap_534[0],
            "witness_roots": sorted(trap_534[1]),
            "root_54_pairs": admissible_pairs(54, spf),
            "child_107_pairs": admissible_pairs(107, spf),
            "root_54_is_structural_splitless": bool(structural_even[54]),
        },
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=1_000_000)
    parser.add_argument("--exponent", type=float, default=0.6)
    args = parser.parse_args()
    print(json.dumps(audit(args.limit, args.exponent), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
