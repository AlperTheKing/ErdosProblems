#!/usr/bin/env python3
"""Standalone exact counterexample to C84 without the literal-hole premise."""

from __future__ import annotations

import hashlib


B = (
    0, 122, 163, 328, 351, 488, 499, 528, 553, 681, 837, 838, 920, 941,
    1051, 1070, 1117, 1322, 1340, 1414, 1449, 1520, 1608, 1613, 1617,
    1715, 1853, 1866, 1925, 2057, 2074, 2153, 2173, 2240, 2320, 2380,
    2475, 2521, 2564, 2596, 2598, 2654, 2788, 2815, 2839, 2901, 2950,
    2958, 3026, 3070, 3076, 3131, 3170, 3184, 3200, 3212, 3215, 3222,
    3248, 3285,
)
H = 3286


def triangle_count(folds: list[tuple[int, int, int, int]], values: tuple[int, ...]) -> int:
    ac = {(a, c): index for index, (a, c, _u, _v) in enumerate(folds)}
    au = {(a, u): index for index, (a, _c, u, _v) in enumerate(folds)}
    cu = {(c, u): index for index, (_a, c, u, _v) in enumerate(folds)}
    assert len(ac) == len(au) == len(cu) == len(folds)
    return sum(
        None not in ids and len(set(ids)) == 3
        for a, c in ac
        for u in values
        for ids in ((ac.get((a, c)), au.get((a, u)), cu.get((c, u))),)
    )


def main() -> None:
    p = len(B)
    sums = {}
    for i, x in enumerate(B):
        for y in B[i:]:
            total = x + y
            assert total not in sums
            sums[total] = (x, y)
    differences = {}
    for i, x in enumerate(B):
        for y in B[i + 1:]:
            difference = y - x
            assert difference not in differences
            differences[difference] = (x, y)

    folds = []
    for low, (a, c) in sorted(sums.items()):
        if low + H not in sums:
            continue
        u, v = sums[low + H]
        assert a <= c < u <= v
        inner = u - c
        outer = v - a
        assert inner + outer == H
        assert a <= c < u <= v
        folds.append((a, c, u, v))

    triangles = triangle_count(folds, B)

    digest = hashlib.sha256(",".join(map(str, B)).encode("ascii")).hexdigest()
    delta = (3 * p * p - p + 2) // 2 - H
    assert B[-1] == H - 1
    assert len(sums) == p * (p + 1) // 2
    assert len(differences) == p * (p - 1) // 2
    assert len(folds) == 182
    assert triangles == 200 > len(folds)
    assert digest == "9e2345da856430f478d63284d6b62b347498b64b4cec4606f8f85c213db08457"

    c84_failures = []
    first_hole = {1: None, 2: None}
    hole_failures = []
    sum_support = set(sums)
    difference_support = set(differences)
    for gamma in range(delta):
        h = H + gamma
        values = tuple(x + gamma for x in B)
        translated_folds = [
            (a + gamma, c + gamma, u + gamma, v + gamma)
            for low, (a, c) in sorted(sums.items())
            if low + h in sums
            for u, v in (sums[low + h],)
        ]
        translated_triangles = triangle_count(translated_folds, values)
        if translated_triangles > len(translated_folds):
            c84_failures.append((gamma, len(translated_folds), translated_triangles))
        for b in (1, 2):
            hole = difference_support.isdisjoint(
                total + 2 * gamma + b for total in sum_support
            )
            if hole and first_hole[b] is None:
                first_hole[b] = (gamma, len(translated_folds), translated_triangles)
            if hole and translated_triangles > len(translated_folds):
                hole_failures.append((gamma, b))
    assert len(c84_failures) == 75
    assert c84_failures[0] == (0, 182, 200)
    assert c84_failures[-1] == (327, 148, 155)
    assert first_hole == {1: (1169, 54, 14), 2: (1190, 60, 21)}
    assert not hole_failures
    print({
        "p": p,
        "h": H,
        "delta": delta,
        "C_S": len(folds),
        "T_F": triangles,
        "T_F_minus_C_S": triangles - len(folds),
        "positive_defect_translation_failures": len(c84_failures),
        "last_failure": c84_failures[-1],
        "first_hole": first_hole,
        "hole_and_failure_intersection": len(hole_failures),
        "sha256": digest,
    })


if __name__ == "__main__":
    main()
