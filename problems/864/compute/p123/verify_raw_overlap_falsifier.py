#!/usr/bin/env python3
"""Independent exact check of GPT-Pro's 44-mark raw-overlap falsifier."""

from __future__ import annotations

import json


Z = (
    0, 12, 155, 187, 196, 234, 315, 329, 553, 574, 614, 684, 704,
    735, 781, 818, 843, 887, 967, 975, 1035, 1120, 1139, 1144, 1235,
    1370, 1400, 1406, 1448, 1482, 1493, 1511, 1546, 1568, 1585, 1595,
    1611, 1618, 1684, 1712, 1834, 1838, 1890, 1892,
)
G = 2003
b = 1


def main() -> None:
    gamma = (G - b) // 2
    h = gamma + max(Z) + 1
    B = tuple(gamma + value for value in Z)
    p = len(B)
    sums = {left + right for index, left in enumerate(B) for right in B[index:]}
    differences = {left - right for left in B for right in B}
    sum_residues = {value % h for value in sums}
    difference_residues = {(-b - value) % h for value in differences}
    overlap = sum_residues & difference_residues
    a = len(sums) - len(sum_residues)
    c = len(differences) - len(difference_residues)
    holes = h - len(sum_residues | difference_residues)

    E = {G + 2 * value for value in Z}
    three_E = {left + middle + right for left in E for middle in E for right in E}
    assert len(sums) == p * (p + 1) // 2
    assert len(differences) == p * (p - 1) + 1
    assert E.isdisjoint(three_E)
    assert (p, h, a, c, len(overlap), holes) == (44, 2894, 13, 44, 614, 682)
    assert max(E) == 5787 and 3 * p * p == 5808
    assert a + c + len(overlap) - holes == -11
    print(json.dumps({
        "arithmetic": "exact Python integers",
        "p": p,
        "h": h,
        "a": a,
        "c": c,
        "overlap": len(overlap),
        "holes": holes,
        "signed_defect": -11,
        "max_E": max(E),
        "three_p_squared": 3 * p * p,
    }, indent=2))


if __name__ == "__main__":
    main()
