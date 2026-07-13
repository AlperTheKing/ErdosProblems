#!/usr/bin/env python3
"""Exact checks for the P89 ordered-phase obstruction."""

P75 = (
    3, 5, 69, 169, 211, 223, 251, 329, 373, 403, 409, 501, 505,
    519, 631, 639, 689, 715, 775, 863, 883, 915, 931, 953, 977, 987,
)

P80 = (
    0, 6, 13, 85, 89, 121, 141, 152, 196, 245, 247, 257, 274,
    327, 345, 370, 404, 418, 439, 444, 472, 536, 558, 573, 581,
    582, 620, 623, 639,
)


def sum_pairs(values):
    pairs = {}
    for i, left in enumerate(values):
        for right in values[i:]:
            total = left + right
            assert total not in pairs
            pairs[total] = (left, right)
    return pairs


def folds(values, h):
    pairs = sum_pairs(values)
    return [(*pairs[low], *pairs[low + h]) for low in pairs if low + h in pairs]


def triangles(values, h):
    fs = folds(values, h)
    ac = {(a, c): (r, s) for a, c, r, s in fs}
    au = {(a, r): (c, s) for a, c, r, s in fs}
    cu = {(c, r): (a, s) for a, c, r, s in fs}
    out = []
    for (a, c), (r, s) in ac.items():
        for u in values:
            if u == r or (a, u) not in au or (c, u) not in cu:
                continue
            z, w = au[a, u]
            x, y = cu[c, u]
            out.append((a, c, u, s, x, z, r, y, w))
    return fs, out


def audit_triangle(values, h, b, row):
    a, c, u, s, x, z, r, y, w = row
    x_shift, z_shift, r_shift = x - a, z - c, r - u
    tau = u - a - c - b
    lam = h - b - u
    stencil = (
        tau,
        tau - x_shift,
        tau - z_shift,
        tau + r_shift,
        lam,
        lam - r_shift,
    )
    fold_phases = (
        r - a - c - b,
        s - a - c - b,
        u - a - z - b,
        w - a - z - b,
        u - x - c - b,
        y - x - c - b,
    )
    assert stencil == (
        tau,
        fold_phases[4],
        fold_phases[2],
        fold_phases[0],
        fold_phases[3],
        fold_phases[1],
    )
    assert fold_phases[3] == fold_phases[5] == lam
    assert len(set(stencil[:4])) == 4
    assert all(value not in values for value in stencil)
    return stencil


def main():
    p75_folds, p75_triangles = triangles(P75, 988)
    for row in p75_triangles:
        audit_triangle(P75, 988, 1, row)
    assert (len(p75_folds), len(p75_triangles)) == (51, 25)

    width = P80[-1]
    gamma = width // 2 + 1
    translated = tuple(value + gamma for value in P80)
    h = translated[-1] + 1
    p = len(translated)
    defect = (3 * p * p - p + 2) // 2 - h
    translated_folds, translated_triangles = triangles(translated, h)
    shared = sum(
        1
        for i, a in enumerate(translated)
        for c in translated[i:]
        for u in translated
        if c < u
    )
    assert shared == p * (p - 1) * (p + 1) // 6
    assert defect == 288 > 0
    assert 3 * min(translated) + 1 > max(translated)
    assert all(
        u - a - c - 1 < min(translated)
        for i, a in enumerate(translated)
        for c in translated[i:]
        for u in translated
        if c < u
    )
    stencils = [audit_triangle(translated, h, 1, row) for row in translated_triangles]
    assert all(max(stencil) < min(translated) for stencil in stencils)
    assert (len(translated_folds), len(translated_triangles)) == (14, 2)

    print({
        "P75": {"C_S": 51, "T_F": 25},
        "translated_P80": {
            "p": p,
            "gamma": gamma,
            "h": h,
            "defect": defect,
            "shared_triples": shared,
            "C_S": len(translated_folds),
            "T_F": len(translated_triangles),
            "stencil_max": max(map(max, stencils)),
            "min_B": min(translated),
        },
    })


if __name__ == "__main__":
    main()
