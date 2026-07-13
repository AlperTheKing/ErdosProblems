#!/usr/bin/env python3
"""Exact audits for P83's loose-fold phase parametrization."""

from __future__ import annotations

from dataclasses import dataclass
from math import comb
from typing import Sequence


Fold = tuple[int, int, int, int]


@dataclass(frozen=True)
class LooseTriangle:
    shared: tuple[int, int, int]
    folds: tuple[Fold, Fold, Fold]
    parameters: tuple[int, int, int, int]
    phase_labels: tuple[int, int, int]


def sum_map(values: Sequence[int]) -> dict[int, tuple[int, int]]:
    result: dict[int, tuple[int, int]] = {}
    for i, x in enumerate(values):
        for y in values[i:]:
            total = x + y
            assert total not in result
            result[total] = (x, y)
    return result


def positive_difference_map(
    values: Sequence[int],
) -> dict[int, tuple[int, int]]:
    result: dict[int, tuple[int, int]] = {}
    for i, x in enumerate(values):
        for y in values[i + 1 :]:
            difference = y - x
            assert difference not in result
            result[difference] = (x, y)
    return result


def fold_list(values: Sequence[int], h: int) -> list[Fold]:
    sums = sum_map(values)
    result: list[Fold] = []
    for low, (a, c) in sorted(sums.items()):
        if low + h not in sums:
            continue
        u, v = sums[low + h]
        assert a <= c < u <= v
        result.append((a, c, u, v))
    return result


def loose_triangles(values: Sequence[int], h: int, b: int) -> list[LooseTriangle]:
    folds = fold_list(values, h)
    ac = {(a, c): i for i, (a, c, _u, _v) in enumerate(folds)}
    cu = {(c, u): i for i, (_a, c, u, _v) in enumerate(folds)}
    ua = {(u, a): i for i, (a, _c, u, _v) in enumerate(folds)}
    result: list[LooseTriangle] = []

    for (a, c), i0 in ac.items():
        for u in values:
            iz = ua.get((u, a))
            ix = cu.get((c, u))
            if iz is None or ix is None or len({i0, iz, ix}) != 3:
                continue

            f0 = folds[i0]
            fz = folds[iz]
            fx = folds[ix]
            _, _, r, s = f0
            _, z, _, w = fz
            x, _, _, y = fx
            X, Z, R = x - a, z - c, r - u

            assert X != 0 and Z != 0 and R != 0
            assert (x, z, r, w, y) == (
                a + X,
                c + Z,
                u + R,
                s + R + Z,
                s + R + X,
            )
            assert a + c + h == u + R + s
            assert a <= c < u + R <= s
            assert a <= c + Z < u <= s + R + Z
            assert a + X <= c < u <= s + R + X

            d = a + c + b
            result.append(
                LooseTriangle(
                    shared=(a, c, u),
                    folds=(f0, fz, fx),
                    parameters=(X, Z, R, s),
                    phase_labels=(d, d + Z, d + X),
                )
            )
    return result


def audit(values: Sequence[int], h: int, b: int) -> dict[str, int]:
    values = tuple(values)
    p = len(values)
    H = h - 1
    assert max(values) == H
    sums = sum_map(values)
    positive_differences = positive_difference_map(values)
    signed_differences = {y - x for x in values for y in values}
    assert set(positive_differences).isdisjoint({total + b for total in sums})

    triangles = loose_triangles(values, h, b)
    shared_keys: set[tuple[int, int, int]] = set()
    phase_keys: set[tuple[int, int, int]] = set()
    endpoint_targets_in_range = 0

    for triangle in triangles:
        a, c, u = triangle.shared
        X, Z, R, s = triangle.parameters
        d, dZ, dX = triangle.phase_labels
        f0, fz, fx = triangle.folds
        _, _, r, _ = f0
        _, z, _, w = fz
        x, _, _, y = fx

        assert triangle.shared not in shared_keys
        assert triangle.phase_labels not in phase_keys
        shared_keys.add(triangle.shared)
        phase_keys.add(triangle.phase_labels)

        assert d > 0 and dZ > 0 and dX > 0
        assert d not in positive_differences
        assert dZ not in positive_differences
        assert dX not in positive_differences
        assert d != dZ and d != dX and dZ != dX

        represented_increments = (X, Z, R, R + X, R + Z, Z - X)
        assert all(increment in signed_differences for increment in represented_increments)
        assert (x - a, z - c, r - u, y - s, w - s, w - y) == represented_increments

        phase = H - d
        assert phase == (H - r) + (H - s) + 1 - b
        assert phase - Z == (H - u) + (H - w) + 1 - b
        assert phase - X == (H - u) + (H - y) + 1 - b

        endpoint_targets_in_range += a + c + u + b <= H

    assert len(triangles) <= comb(p + 1, 3)
    return {
        "p": p,
        "h": h,
        "b": b,
        "delta": (3 * p * p - p + 2) // 2 - h,
        "C_S": len(fold_list(values, h)),
        "T_F": len(triangles),
        "shared_injection_keys": len(shared_keys),
        "phase_injection_keys": len(phase_keys),
        "shared_endpoint_targets_in_range": endpoint_targets_in_range,
        "universal_bound": comb(p + 1, 3),
    }


def main() -> None:
    p75 = (
        3, 5, 69, 169, 211, 223, 251, 329, 373, 403, 409, 501, 505,
        519, 631, 639, 689, 715, 775, 863, 883, 915, 931, 953, 977, 987,
    )
    p75_report = audit(p75, h=988, b=1)
    assert p75_report == {
        "p": 26,
        "h": 988,
        "b": 1,
        "delta": 14,
        "C_S": 51,
        "T_F": 25,
        "shared_injection_keys": 25,
        "phase_injection_keys": 25,
        "shared_endpoint_targets_in_range": 3,
        "universal_bound": 2925,
    }

    falsifier = (5, 7, 18, 24, 25, 28, 33)
    falsifier_report = audit(falsifier, h=34, b=2)
    triangles = loose_triangles(falsifier, h=34, b=2)
    assert falsifier_report["delta"] == 37
    assert falsifier_report["C_S"] == 4
    assert falsifier_report["T_F"] == 1
    assert len(triangles) == 1
    triangle = triangles[0]
    assert triangle.shared == (5, 7, 24)
    assert triangle.parameters == (2, 11, -6, 28)
    assert triangle.phase_labels == (14, 25, 16)
    d = triangle.phase_labels[0]
    R = triangle.parameters[2]
    assert d - R == 20
    assert positive_difference_map(falsifier)[d - R] == (5, 25)

    print({"P75": p75_report, "d_minus_R_falsifier": falsifier_report})


if __name__ == "__main__":
    main()
