from collections import Counter


BASE = (
    0, 122, 163, 328, 351, 488, 499, 528, 553, 681, 837, 838, 920, 941,
    1051, 1070, 1117, 1322, 1340, 1414, 1449, 1520, 1608, 1613, 1617,
    1715, 1853, 1866, 1925, 2057, 2074, 2153, 2173, 2240, 2320, 2380,
    2475, 2521, 2564, 2596, 2598, 2654, 2788, 2815, 2839, 2901, 2950,
    2958, 3026, 3070, 3076, 3131, 3170, 3184, 3200, 3212, 3215, 3222,
    3248, 3285,
)

B = tuple(2 * value + 1 for value in BASE)
h = 6572
b = 1


def canonical_folds(values, shift):
    pair_by_sum = {
        left + right: (left, right)
        for i, left in enumerate(values)
        for right in values[i:]
    }
    folds = []
    for low_sum, (a, c) in pair_by_sum.items():
        high = pair_by_sum.get(low_sum + shift)
        if high is None:
            continue
        u, v = high
        assert a <= c < u <= v
        folds.append((a, c, u, v))
    return folds


def loose_triangles(values, folds):
    ac = {(a, c): i for i, (a, c, _u, _v) in enumerate(folds)}
    au = {(a, u): i for i, (a, _c, u, _v) in enumerate(folds)}
    cu = {(c, u): i for i, (_a, c, u, _v) in enumerate(folds)}
    triangles = []
    for a, c in ac:
        for u in values:
            ids = (ac.get((a, c)), au.get((a, u)), cu.get((c, u)))
            if None in ids or ids[0] == ids[1] == ids[2]:
                continue
            assert len(set(ids)) == 3
            triangles.append(ids)
    return triangles


sum_count = Counter(
    left + right for i, left in enumerate(B) for right in B[i:]
)
difference_count = Counter(
    right - left for i, left in enumerate(B) for right in B[i + 1:]
)
folds = canonical_folds(B, h)
triangles = loose_triangles(B, folds)
collisions = sum(a + c + b in difference_count for a, c, _u, _v in folds)
literal_hole = set(difference_count).isdisjoint(
    {pair_sum + b for pair_sum in sum_count}
)
p = len(B)
delta = (3 * p * p - p + 2) // 2 - h

assert max(B) == h - 1
assert len(sum_count) == p * (p + 1) // 2
assert max(sum_count.values()) == 1
assert len(difference_count) == p * (p - 1) // 2
assert max(difference_count.values()) == 1
assert literal_hole
assert len(folds) == 182
assert len(triangles) == 200
assert collisions == 0
assert delta == -1201
assert len(triangles) > len(folds) + collisions

print({
    "p": p,
    "h": h,
    "b": b,
    "delta": delta,
    "C_S": len(folds),
    "T_F": len(triangles),
    "V_b": collisions,
    "residual": len(triangles) - len(folds) - collisions,
    "literal_hole": literal_hole,
})
