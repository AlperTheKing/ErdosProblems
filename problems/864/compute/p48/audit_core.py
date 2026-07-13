"""Exact core checks for P48 recursive constructions."""

from __future__ import annotations

import itertools
import math
from fractions import Fraction
from typing import Iterable, Sequence


def primes_through(limit: int) -> list[int]:
    return [
        n
        for n in range(2, limit + 1)
        if all(n % d for d in range(2, math.isqrt(n) + 1))
    ]


def prime_factors(n: int) -> tuple[int, ...]:
    factors: list[int] = []
    d = 2
    while d * d <= n:
        if n % d == 0:
            factors.append(d)
            while n % d == 0:
                n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return tuple(factors)


def primitive_root(p: int) -> int:
    factors = prime_factors(p - 1)
    for g in range(2, p):
        if all(pow(g, (p - 1) // r, p) != 1 for r in factors):
            return g
    raise AssertionError(f"no primitive root modulo {p}")


def normalize(values: Iterable[int]) -> tuple[int, ...]:
    out = tuple(sorted(values))
    if len(out) != len(set(out)):
        raise ValueError("marks are not distinct")
    base = out[0]
    return tuple(x - base for x in out)


def pair_sum_collision(values: Sequence[int]) -> dict[str, object] | None:
    seen: dict[int, tuple[int, int]] = {}
    for i, a in enumerate(values):
        for j in range(i, len(values)):
            total = a + values[j]
            if total in seen:
                old = seen[total]
                return {
                    "sum": total,
                    "first_indices": old,
                    "second_indices": (i, j),
                    "first_pair": (values[old[0]], values[old[1]]),
                    "second_pair": (a, values[j]),
                    "uses_diagonal": old[0] == old[1] or i == j,
                }
            seen[total] = (i, j)
    return None


def is_sidon(values: Sequence[int]) -> bool:
    return pair_sum_collision(values) is None


def unordered_sums(values: Sequence[int]) -> set[int]:
    return {
        values[i] + values[j]
        for i in range(len(values))
        for j in range(i, len(values))
    }


def positive_differences(values: Sequence[int]) -> set[int]:
    return {
        values[j] - values[i]
        for i in range(len(values))
        for j in range(i + 1, len(values))
    }


def unordered_triples(values: Sequence[int]) -> set[int]:
    return {
        values[i] + values[j] + values[k]
        for i in range(len(values))
        for j in range(i, len(values))
        for k in range(j, len(values))
    }


def three_sum_witness(values: Sequence[int]) -> dict[str, object] | None:
    value_set = set(values)
    for i in range(len(values)):
        for j in range(i, len(values)):
            for k in range(j, len(values)):
                total = values[i] + values[j] + values[k]
                if total in value_set:
                    return {
                        "target": total,
                        "summands": (values[i], values[j], values[k]),
                        "repeated_summand": i == j or j == k,
                    }
    return None


def valid_same_parity_set(values: Sequence[int]) -> bool:
    return (
        bool(values)
        and min(values) > 0
        and len({x % 2 for x in values}) == 1
        and is_sidon(values)
        and three_sum_witness(values) is None
    )


def first_signed_gap(ruler: Sequence[int]) -> int:
    sums = unordered_sums(ruler)
    differences = positive_differences(ruler)
    forbidden = {d - s for d in differences for s in sums if d > s}
    gap = 1
    while gap in forbidden:
        gap += 1
    return gap


def signed_set(ruler: Sequence[int], gap: int) -> tuple[int, ...]:
    return tuple(gap + 2 * z for z in ruler)


def ratio_record(numerator: int, denominator: int) -> dict[str, object]:
    value = Fraction(numerator, denominator)
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "decimal": float(value),
    }


def best_lift_record(ruler: Sequence[int]) -> dict[str, object]:
    ruler = normalize(ruler)
    assert is_sidon(ruler)
    gap = first_signed_gap(ruler)
    values = signed_set(ruler, gap)
    assert valid_same_parity_set(values)
    return {
        "G": gap,
        "W": ruler[-1],
        "M": values[-1],
        "ratio": ratio_record(values[-1], len(ruler) ** 2),
        "ruler": ruler,
    }


def tensor_audit() -> dict[str, object]:
    full_products = 0
    sample: dict[str, object] | None = None
    subsets = [
        tuple(c)
        for size in range(2, 4)
        for c in itertools.combinations(range(5), size)
    ]
    for x_values in subsets:
        for y_values in subsets:
            radix = 2 * max(x_values) + 3
            product = tuple(sorted(x + radix * y for x in x_values for y in y_values))
            collision = pair_sum_collision(product)
            assert collision is not None
            full_products += 1
            if sample is None:
                sample = {
                    "X": x_values,
                    "Y": y_values,
                    "radix": radix,
                    "product": product,
                    "collision": collision,
                }

    separable_carries = 0
    x_values = (0, 2, 7)
    y_values = (0, 3)
    radix = 11
    carry_weight = 101
    for alpha in itertools.product(range(-1, 2), repeat=len(x_values)):
        for beta in itertools.product(range(-1, 2), repeat=len(y_values)):
            u = tuple(x + carry_weight * a for x, a in zip(x_values, alpha))
            v = tuple(radix * y + carry_weight * b for y, b in zip(y_values, beta))
            product = tuple(u_i + v_j for u_i in u for v_j in v)
            if len(set(product)) == len(product):
                assert pair_sum_collision(tuple(sorted(product))) is not None
            separable_carries += 1

    return {
        "full_cartesian_products": full_products,
        "separable_carry_assignments": separable_carries,
        "sample": sample,
    }


def is_costas(permutation: Sequence[int]) -> bool:
    seen: set[tuple[int, int]] = set()
    for i in range(len(permutation)):
        for j in range(i + 1, len(permutation)):
            displacement = (j - i, permutation[j] - permutation[i])
            if displacement in seen:
                return False
            seen.add(displacement)
    return True


def costas_composition_audit() -> dict[str, object]:
    costas = {
        n: [p for p in itertools.permutations(range(n)) if is_costas(p)]
        for n in range(2, 5)
    }
    checked = 0
    sample: dict[str, object] | None = None
    for m in range(2, 5):
        for n in range(2, 5):
            for pi in costas[m]:
                for tau in costas[n]:
                    rho = tuple(n * pi[i] + tau[j] for i in range(m) for j in range(n))
                    assert not is_costas(rho)
                    flattened = tuple(i + (m * n + 1) * rho[i] for i in range(m * n))
                    collision = pair_sum_collision(tuple(sorted(flattened)))
                    assert collision is not None
                    checked += 1
                    if sample is None:
                        sample = {"pi": pi, "tau": tau, "rho": rho, "collision": collision}
    return {
        "costas_counts": {str(n): len(perms) for n, perms in costas.items()},
        "compositions_checked": checked,
        "sample": sample,
    }


def normalized_rulers(max_span: int) -> list[tuple[int, ...]]:
    rulers: list[tuple[int, ...]] = []
    for span in range(1, max_span + 1):
        interior = range(1, span)
        for mask in range(1 << (span - 1)):
            values = (0,) + tuple(x for x in interior if mask & (1 << (x - 1))) + (span,)
            if is_sidon(values):
                rulers.append(values)
    return rulers


def lag_differences(values: Sequence[int], lag: int) -> list[int]:
    return [
        values[i + r] - values[i]
        for r in range(1, lag + 1)
        for i in range(len(values) - r)
    ]


def check_joint_lag_bound(x_values: Sequence[int], y_values: Sequence[int]) -> int:
    checks = 0
    u = x_values[-1]
    v = y_values[-1]
    for h_x in range(len(x_values)):
        for h_y in range(len(y_values)):
            if h_x == h_y == 0:
                continue
            selected = lag_differences(x_values, h_x) + lag_differences(y_values, h_y)
            assert len(selected) == len(set(selected))
            count = len(selected)
            bound_twice = h_x * (h_x + 1) * u + h_y * (h_y + 1) * v
            assert count * (count + 1) <= bound_twice
            assert 2 * sum(selected) <= bound_twice
            checks += 1
    return checks


def guarded_union(
    x_values: Sequence[int], y_values: Sequence[int]
) -> tuple[tuple[int, ...], int, int, tuple[int, ...]]:
    u = x_values[-1]
    v = y_values[-1]
    gap = max(u, v) + 1
    shift = gap + 3 * u + 1
    ruler = tuple(x_values) + tuple(shift + y for y in y_values)
    values = signed_set(ruler, gap)
    return ruler, gap, shift, values


def separated_union_audit(max_span: int) -> dict[str, object]:
    rulers = normalized_rulers(max_span)
    pairs = 0
    lag_checks = 0
    best: tuple[Fraction, dict[str, object]] | None = None
    for x_values in rulers:
        d_x = positive_differences(x_values)
        for y_values in rulers:
            if not d_x.isdisjoint(positive_differences(y_values)):
                continue
            ruler, gap, shift, values = guarded_union(x_values, y_values)
            assert len(ruler) == len(x_values) + len(y_values)
            assert is_sidon(ruler)
            assert valid_same_parity_set(values)
            assert len(unordered_sums(values)) == len(values) * (len(values) + 1) // 2
            assert set(values).isdisjoint(unordered_triples(values))
            lag_checks += check_joint_lag_bound(x_values, y_values)
            pairs += 1
            ratio = Fraction(max(values), len(values) ** 2)
            record = {
                "X": x_values,
                "Y": y_values,
                "G": gap,
                "T": shift,
                "Z": ruler,
                "E": values,
                "ratio": ratio_record(max(values), len(values) ** 2),
            }
            if best is None or ratio < best[0]:
                best = (ratio, record)

    falsifiers = []
    cases = [
        ((0, 2), (0, 1), 2, 9, "G=max(X)"),
        ((0, 1), (0, 2), 2, 6, "G=max(Y)"),
        ((0, 1), (0, 2), 3, 6, "T=G+3max(X)"),
    ]
    for x_values, y_values, gap, shift, label in cases:
        ruler = tuple(x_values) + tuple(shift + y for y in y_values)
        values = signed_set(ruler, gap)
        assert is_sidon(ruler)
        witness = three_sum_witness(values)
        assert witness is not None and witness["repeated_summand"]
        falsifiers.append({"label": label, "Z": ruler, "E": values, "witness": witness})

    return {
        "max_span": max_span,
        "normalized_sidon_rulers": len(rulers),
        "difference_disjoint_pairs": pairs,
        "joint_lag_inequalities": lag_checks,
        "best_finite_guarded_union": None if best is None else best[1],
        "strict_guard_falsifiers": falsifiers,
    }
