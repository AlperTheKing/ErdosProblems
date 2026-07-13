#!/usr/bin/env python3
"""Independent exact certificates for the P38 reflected-core obstruction."""

from __future__ import annotations

import json
from collections import Counter
from itertools import combinations_with_replacement
from pathlib import Path


OUTPUT = Path("problems/864/compute/p38/certificate_verification.json")


def unordered_sum_counts(points: tuple[int, ...]) -> Counter[int]:
    return Counter(x + y for x, y in combinations_with_replacement(points, 2))


def repeated_sums(points: tuple[int, ...]) -> dict[int, int]:
    return {
        label: multiplicity
        for label, multiplicity in sorted(unordered_sum_counts(points).items())
        if multiplicity >= 2
    }


def assert_admissible(points: tuple[int, ...]) -> None:
    assert len(repeated_sums(points)) <= 1


def core_and_residual(
    points: tuple[int, ...], sigma: int
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    point_set = set(points)
    core = tuple(x for x in points if sigma - x in point_set)
    residual = tuple(x for x in points if sigma - x not in point_set)
    return core, residual


def finite_falsifier_certificate() -> dict[str, object]:
    points = (0, 5, 9, 13, 15, 16)
    sigma = 18
    assert repeated_sums(points) == {sigma: 2}
    core, residual = core_and_residual(points, sigma)
    assert core == (5, 9, 13)
    assert residual == (0, 15, 16)

    n = points[-1] - points[0] + 1
    k = len(points)
    c = len(core)
    span = n - 1
    core_span = core[-1] - core[0]
    # k^2/N > 4/3 + 1/2 = 11/6.
    assert 6 * k * k > 11 * n
    # Failure of L-L_P >= 3/4(k^2-c^2), cleared by four.
    transfer_margin4 = 3 * (k * k - c * c) - 4 * (span - core_span)
    assert transfer_margin4 == 49

    completion = tuple(sorted(set(points) | {sigma - x for x in residual}))
    completion_repetitions = repeated_sums(completion)
    assert tuple(completion_repetitions) == (5, 15, 16, 18, 20, 21, 31)

    return {
        "A": points,
        "sigma": sigma,
        "core": core,
        "residual": residual,
        "density_gate": {"left": 6 * k * k, "right": 11 * n},
        "span_transfer_margin4": transfer_margin4,
        "completion": completion,
        "completion_repeated_sums": completion_repetitions,
    }


def deletion_certificate() -> dict[str, object]:
    host = (0, 1, 3, 8, 12, 18, 22, 27, 29, 30)
    sigma = 30
    assert repeated_sums(host) == {sigma: 5}
    assert set(host) == {sigma - x for x in host}

    lower_points = tuple(x for x in host if 2 * x < sigma)
    checked = 0
    formula_checked = 0
    for mask in range(1 << len(lower_points)):
        broken = tuple(
            x for index, x in enumerate(lower_points) if mask & (1 << index)
        )
        descendant = tuple(sorted(set(host) - {sigma - x for x in broken}))
        assert_admissible(descendant)
        checked += 1
        t = len(broken)
        if len(lower_points) - t < 2:
            continue
        assert repeated_sums(descendant) == {sigma: len(lower_points) - t}
        core, residual = core_and_residual(descendant, sigma)
        assert len(descendant) == len(host) - t
        assert len(core) == len(host) - 2 * t
        assert len(residual) == t
        formula_checked += 1

    descendant = (0, 1, 3, 8, 12, 29, 30)
    assert repeated_sums(descendant) == {sigma: 2}
    core, residual = core_and_residual(descendant, sigma)
    assert core == (0, 1, 29, 30)
    assert residual == (3, 8, 12)
    assert core[-1] - core[0] == descendant[-1] - descendant[0] == 30
    assert 3 * len(descendant) ** 2 > 4 * 31

    return {
        "host": host,
        "sigma": sigma,
        "all_descendants_checked": checked,
        "core_formula_descendants_checked": formula_checked,
        "span_preserving_descendant": descendant,
        "core": core,
        "residual": residual,
        "density_gate": {
            "left": 3 * len(descendant) ** 2,
            "right": 4 * 31,
        },
    }


def midpoint_certificate() -> dict[str, object]:
    host = (1, 2, 4, 6, 7)
    sigma = 8
    assert repeated_sums(host) == {sigma: 3}
    assert set(host) == {sigma - x for x in host}

    descendant = (1, 2, 4, 7)
    assert repeated_sums(descendant) == {sigma: 2}
    core, residual = core_and_residual(descendant, sigma)
    assert core == (1, 4, 7)
    assert residual == (2,)
    assert core[-1] - core[0] == descendant[-1] - descendant[0]
    return {
        "host": host,
        "descendant": descendant,
        "sigma": sigma,
        "core": core,
        "residual": residual,
    }


def arbitrary_size_span_obstruction() -> dict[str, object]:
    rows: list[dict[str, int]] = []
    for pair_count in range(3, 13):
        base = tuple(1 << index for index in range(pair_count))
        ruler_max = base[-1]
        sigma = 3 * ruler_max + 1
        host = tuple(sorted(set(base) | {sigma - x for x in base}))
        assert len(host) == 2 * pair_count
        assert set(host) == {sigma - x for x in host}
        assert repeated_sums(host) == {sigma: pair_count}

        broken_count = pair_count // 2
        broken = base[1 : broken_count + 1]  # Protect the endpoint pair at 1.
        descendant = tuple(sorted(set(host) - {sigma - x for x in broken}))
        assert repeated_sums(descendant) == {sigma: pair_count - broken_count}
        core, residual = core_and_residual(descendant, sigma)
        assert len(residual) == broken_count
        assert core[0] == descendant[0] == 1
        assert core[-1] == descendant[-1] == sigma - 1

        k = len(descendant)
        c = len(core)
        transfer_rhs4 = 3 * (k * k - c * c)
        assert transfer_rhs4 > 0
        rows.append(
            {
                "pair_count": pair_count,
                "broken_count": broken_count,
                "k": k,
                "c": c,
                "u": len(residual),
                "span_difference": 0,
                "transfer_rhs_times_4": transfer_rhs4,
            }
        )
    return {"families_checked": len(rows), "rows": rows}


def algebra_certificate() -> dict[str, int]:
    checked = 0
    for delta in (0, 1):
        for p in range(2, 65):
            k_host = 2 * p + delta
            for t in range(p + 1):
                k = k_host - t
                c = k_host - 2 * t
                u = t
                assert k == c + u
                assert k * k - c * c == 2 * k_host * t - 3 * t * t
                assert k_host * k_host == (k + u) * (k + u)
                checked += 1
    return {"integer_parameter_rows_checked": checked}


def main() -> None:
    result = {
        "arithmetic": "integer only",
        "finite_falsifier": finite_falsifier_certificate(),
        "deletion": deletion_certificate(),
        "midpoint": midpoint_certificate(),
        "arbitrary_size_span_obstruction": arbitrary_size_span_obstruction(),
        "algebra": algebra_certificate(),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
