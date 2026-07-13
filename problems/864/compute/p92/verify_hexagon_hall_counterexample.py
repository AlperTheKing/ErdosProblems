#!/usr/bin/env python3
"""Verify P92's global one-step hexagon-label Hall counterexample."""

from __future__ import annotations


B = (
    10848, 10884, 10983, 11160, 11450, 11504, 11640, 11645, 11729,
    11841, 11842, 12402, 12470, 12669, 12736, 12976, 12982, 13119,
    13176, 13439, 13720, 13824, 13853, 13958, 13981, 14007, 14211,
    14220, 14222, 14387, 14516, 14553, 14572, 14592, 14647, 14932,
    15280, 15396, 15648, 16022, 16055, 16136, 16180, 16253, 16545,
    17000, 17040, 17170, 17221, 17318, 17486, 17718, 17760, 17905,
    18043, 18113, 18497, 18569, 18788, 18812, 18932, 19035, 19047,
    19085, 19264, 19305, 19371, 19406, 19628, 19955, 20014, 20018,
    20192, 20206, 20224, 20302, 20442, 20495, 21009, 21136, 21308,
    21431, 21458, 21647, 21927, 22073, 22155, 22229, 22246, 22557,
    22628, 22649, 22659, 22728, 22883, 23005, 23090, 23259, 23439,
    23527, 23534, 23614, 23928, 23931, 23944, 23992, 24037, 24052,
    24285, 24403, 24567, 24589, 24614, 25235, 25293, 25686, 25714,
    25776, 25928, 25958, 26119, 26184, 26303, 26346, 26429, 26735,
    26874, 26882, 27033, 27182, 27342, 27785, 27862, 27896, 27948,
    27994, 28197, 28409,
)
H, B_SHIFT = 28410, 1

HALL_SHARED = (
    (11504, 12669, 25686),
    (11504, 12736, 24589),
    (11504, 12736, 25686),
    (11504, 13720, 25776),
    (11640, 12669, 24589),
    (11640, 12736, 25686),
    (11640, 12736, 25776),
    (11640, 13720, 25686),
)

EXPECTED_PARAMETERS = (
    (136, 1051, -1097),
    (136, -67, 1187),
    (898, 984, 90),
    (136, -984, -90),
    (-136, 67, 1097),
    (762, -67, -1097),
    (-136, 984, -1187),
    (-136, -1051, 90),
)

EXPECTED_NEIGHBORHOOD = {
    24174, 24241, 24310, 24377, 25139, 25225, 25361,
}


def main() -> None:
    p = len(B)
    sums: dict[int, tuple[int, int]] = {}
    differences: dict[int, tuple[int, int]] = {}
    for i, x in enumerate(B):
        for y in B[i:]:
            assert x + y not in sums
            sums[x + y] = (x, y)
        for y in B[i + 1 :]:
            assert y - x not in differences
            differences[y - x] = (x, y)

    assert B[-1] == H - 1
    assert len(sums) == p * (p + 1) // 2
    assert len(differences) == p * (p - 1) // 2
    assert set(differences).isdisjoint(total + B_SHIFT for total in sums)
    delta = (3 * p * p - p + 2) // 2 - H
    assert delta == 88 > 0

    folds = [
        (a, c, *sums[low + H])
        for low, (a, c) in sorted(sums.items())
        if low + H in sums
    ]
    ac = {(a, c): fold for fold in folds for a, c in [fold[:2]]}
    au = {(a, u): fold for fold in folds for a, _c, u, _v in [fold]}
    cu = {(c, u): fold for fold in folds for _a, c, u, _v in [fold]}
    assert len(ac) == len(au) == len(cu) == len(folds) == 48

    triangles: dict[tuple[int, int, int], tuple[object, ...]] = {}
    for a, c in ac:
        for u in B:
            if (a, u) not in au or (c, u) not in cu:
                continue
            support = (ac[a, c], au[a, u], cu[c, u])
            if len(set(support)) != 3:
                continue
            f0, fz, fx = support
            X = fx[0] - a
            Z = fz[1] - c
            R = f0[2] - u
            triangles[a, c, u] = (support, (X, Z, R))
    assert len(triangles) == 11

    fold_labels = {a + c + B_SHIFT for a, c, _u, _v in folds}
    neighborhood_union: set[int] = set()
    actual_parameters = []
    for shared in HALL_SHARED:
        support, parameters = triangles[shared]
        X, Z, R = parameters
        actual_parameters.append(parameters)
        phase_labels = {
            fold[0] + fold[1] + B_SHIFT for fold in support
        }
        increments = {X, Z, R, R + X, R + Z, Z - X}
        increments |= {-value for value in increments}
        increments.add(0)
        neighborhood = {
            label
            for label in fold_labels
            if any(label - phase in increments for phase in phase_labels)
        }
        neighborhood_union |= neighborhood

    assert tuple(actual_parameters) == EXPECTED_PARAMETERS
    assert neighborhood_union == EXPECTED_NEIGHBORHOOD
    assert len(HALL_SHARED) == 8 > 7 == len(neighborhood_union)

    print(
        {
            "p": p,
            "h": H,
            "b": B_SHIFT,
            "delta": delta,
            "C_S": len(folds),
            "T_F": len(triangles),
            "Hall_left": len(HALL_SHARED),
            "Hall_neighbors": len(neighborhood_union),
        }
    )


if __name__ == "__main__":
    main()
