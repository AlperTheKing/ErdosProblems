from collections import Counter


B = [
    3, 5, 69, 169, 211, 223, 251, 329, 373, 403, 409,
    501, 505, 519, 631, 639, 689, 715, 775, 863, 883,
    915, 931, 953, 977, 987,
]
p, h, b = len(B), 988, 1


sum_pair = {}
for i, a in enumerate(B):
    for c in B[i:]:
        s = a + c
        assert s not in sum_pair
        sum_pair[s] = (a, c)

diffs = Counter(y - x for i, x in enumerate(B) for y in B[i + 1 :])
assert len(diffs) == p * (p - 1) // 2
assert max(diffs.values()) == 1
assert set(diffs).isdisjoint({s + b for s in sum_pair})

folds = []
for s, (a, c) in sorted(sum_pair.items()):
    if s + h not in sum_pair:
        continue
    u, v = sum_pair[s + h]
    assert a <= c < u <= v
    folds.append((a, c, u, v))

ac = {}
cu = {}
ua = {}
for index, (a, c, u, _v) in enumerate(folds):
    assert (a, c) not in ac
    assert (c, u) not in cu
    assert (u, a) not in ua
    ac[a, c] = index
    cu[c, u] = index
    ua[u, a] = index

canonical = 0
loose = 0
for a in B:
    for c in B:
        i = ac.get((a, c))
        if i is None:
            continue
        for u in B:
            j = cu.get((c, u))
            k = ua.get((u, a))
            if j is None or k is None:
                continue
            support = {i, j, k}
            if len(support) == 1:
                canonical += 1
            else:
                assert len(support) == 3
                loose += 1

delta = (3 * p * p - p + 2) // 2 - h
assert delta == 14
assert len(folds) == 51
assert canonical == 51
assert loose == 25

print({
    "p": p,
    "h": h,
    "b": b,
    "delta": delta,
    "folds": len(folds),
    "canonical_triangles": canonical,
    "loose_triangles": loose,
})
