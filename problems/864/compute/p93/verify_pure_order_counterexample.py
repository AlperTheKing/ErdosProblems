from collections import Counter


B = (
    0, 122, 163, 328, 351, 488, 499, 528, 553, 681, 837, 838, 920,
    941, 1051, 1070, 1117, 1322, 1340, 1414, 1449, 1520, 1608, 1613,
    1617, 1715, 1853, 1866, 1925, 2057, 2074, 2153, 2173, 2240, 2320,
    2380, 2475, 2521, 2564, 2596, 2598, 2654, 2788, 2815, 2839, 2901,
    2950, 2958, 3026, 3070, 3076, 3131, 3170, 3184, 3200, 3212, 3215,
    3222, 3248, 3285,
)
h = 3286

sums = {}
for i, a in enumerate(B):
    for c in B[i:]:
        assert a + c not in sums
        sums[a + c] = (a, c)

differences = Counter(
    right - left
    for i, left in enumerate(B)
    for right in B[i + 1 :]
)
assert max(differences.values()) == 1

folds = sorted(
    (a, c, *sums[low + h])
    for low, (a, c) in sums.items()
    if low + h in sums
)
for a, c, u, v in folds:
    assert a <= c < u <= v
    assert (v - a) + (u - c) == h

ac = {(a, c): i for i, (a, c, _u, _v) in enumerate(folds)}
au = {(a, u): i for i, (a, _c, u, _v) in enumerate(folds)}
cu = {(c, u): i for i, (_a, c, u, _v) in enumerate(folds)}
triangles = []
for a, c in ac:
    for u in B:
        ids = (ac.get((a, c)), au.get((a, u)), cu.get((c, u)))
        if None not in ids and len(set(ids)) == 3:
            triangles.append(ids)

incident = [set() for _ in folds]
for triangle_id, ids in enumerate(triangles):
    for fold_id in ids:
        incident[fold_id].add(triangle_id)
seen = set()
components = []
for start in range(len(folds)):
    if start in seen:
        continue
    vertices = {start}
    edges = set()
    stack = [start]
    seen.add(start)
    while stack:
        fold_id = stack.pop()
        for triangle_id in incident[fold_id]:
            edges.add(triangle_id)
            for neighbor in triangles[triangle_id]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    vertices.add(neighbor)
                    stack.append(neighbor)
    components.append((len(vertices), len(edges)))

delta = (3 * len(B) ** 2 - len(B) + 2) // 2 - h
hole = {
    b: differences.keys().isdisjoint(total + b for total in sums)
    for b in (1, 2)
}
assert len(folds) == 182
assert len(triangles) == 200
assert max(components, key=lambda row: row[1] - row[0]) == (165, 200)
assert delta == 2085
assert hole == {1: False, 2: False}
print(
    {
        "p": len(B), "h": h, "delta": delta,
        "C_S": len(folds), "T_F": len(triangles),
        "max_component": (165, 200), "literal_holes": hole,
    }
)
