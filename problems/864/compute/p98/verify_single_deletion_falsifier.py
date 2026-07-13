#!/usr/bin/env python3
"""Standalone exact verifier for P98's one-deletion component falsifier."""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
source = ROOT / "problems/864/compute/p98/tight_mutations.json"
payload = json.loads(source.read_text(encoding="ascii"))
seed = tuple(payload["seed"]["B"])
B = tuple(value for value in seed if value != 4740)
h, b = 14484, 1
p = len(B)

sums = {}
sum_count = Counter()
for i, a in enumerate(B):
    for c in B[i:]:
        sum_count[a + c] += 1
        sums[a + c] = (a, c)
differences = Counter(
    right - left
    for j, right in enumerate(B)
    for left in B[:j]
)
assert max(B) == h - 1
assert len(sum_count) == p * (p + 1) // 2
assert max(sum_count.values()) == 1
assert len(differences) == p * (p - 1) // 2
assert max(differences.values()) == 1
assert set(differences).isdisjoint(total + b for total in sums)
delta = (3 * p * p - p + 2) // 2 - h
assert delta == 1379 > 0

folds = []
for low in sorted(sums):
    if low + h in sums:
        folds.append((*sums[low], *sums[low + h]))
assert all(a <= c < u <= v for a, c, u, v in folds)
ac = {(a, c): i for i, (a, c, _u, _v) in enumerate(folds)}
au = {(a, u): i for i, (a, _c, u, _v) in enumerate(folds)}
cu = {(c, u): i for i, (_a, c, u, _v) in enumerate(folds)}
triangles = []
for a, c in ac:
    for u in B:
        ids = (ac.get((a, c)), au.get((a, u)), cu.get((c, u)))
        if None not in ids and len(set(ids)) == 3:
            triangles.append(ids)

parent = list(range(len(folds)))
def find(item):
    while parent[item] != item:
        parent[item] = parent[parent[item]]
        item = parent[item]
    return item
for triangle in triangles:
    root = find(triangle[0])
    for item in triangle[1:]:
        other = find(item)
        if root != other:
            parent[other] = root
fold_counts = Counter(find(item) for item in range(len(folds)))
triangle_counts = Counter(find(triangle[0]) for triangle in triangles)
components = sorted(
    ((triangle_counts[root], count) for root, count in fold_counts.items()),
    reverse=True,
)

V_b = sum(a + c + b in differences for a, c, _u, _v in folds)
assert (len(folds), len(triangles)) == (132, 110)
assert components[0] == (110, 109)
assert V_b == 0
assert len(triangles) <= len(folds) + V_b
print({
    "p": p, "h": h, "b": b, "delta": delta,
    "C_S": len(folds), "T_F": len(triangles), "V_b": V_b,
    "max_component_folds": components[0][1],
    "max_component_triangles": components[0][0],
})
