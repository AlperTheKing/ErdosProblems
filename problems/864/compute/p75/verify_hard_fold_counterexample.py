from collections import Counter


B = [
    3, 5, 69, 169, 211, 223, 251, 329, 373, 403, 409,
    501, 505, 519, 631, 639, 689, 715, 775, 863, 883,
    915, 931, 953, 977, 987,
]
p, h, b = len(B), 988, 1

sums = Counter(x + y for i, x in enumerate(B) for y in B[i:])
diffs = Counter(y - x for i, x in enumerate(B) for y in B[i + 1 :])
folds = sorted(s for s in sums if s + h in sums)

support_hole = set(diffs).isdisjoint({s + b for s in sums})
literal_hole = not any(
    x + y + z + b == w
    for x in B
    for y in B
    for z in B
    for w in B
)
delta = (3 * p * p - p + 2) // 2 - h

assert max(B) == h - 1
assert len(sums) == p * (p + 1) // 2
assert max(sums.values()) == 1
assert len(diffs) == p * (p - 1) // 2
assert max(diffs.values()) == 1
assert support_hole and literal_hole
assert delta == 14 > 0
assert len(folds) == 51 > 2 * p - 3

print(
    {
        "p": p,
        "h": h,
        "b": b,
        "delta": delta,
        "sums": len(sums),
        "differences": len(diffs),
        "C_S": len(folds),
        "bound": 2 * p - 3,
    }
)
