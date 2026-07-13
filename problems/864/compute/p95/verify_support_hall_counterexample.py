import json
from pathlib import Path


source = Path(__file__).parents[1] / "p94" / "c84_archived_audit.json"
row = json.loads(source.read_text(encoding="ascii"))["translation"]["max_ratio_row"]
B, h = tuple(row["B"]), row["h"]

sums = {}
for i, a in enumerate(B):
    for c in B[i:]:
        assert a + c not in sums
        sums[a + c] = (a, c)
folds = []
for s, (a, c) in sums.items():
    if s + h in sums:
        folds.append((a, c, *sums[s + h]))
ac = {(a, c): i for i, (a, c, _u, _v) in enumerate(folds)}
au = {(a, u): i for i, (a, _c, u, _v) in enumerate(folds)}
cu = {(c, u): i for i, (_a, c, u, _v) in enumerate(folds)}
triangles = []
for a, c in ac:
    for u in B:
        ids = (ac.get((a, c)), au.get((a, u)), cu.get((c, u)))
        if None in ids or ids[0] == ids[1] == ids[2]:
            continue
        assert len(set(ids)) == 3
        triangles.append(ids)

right_match = [-1] * len(folds)
left_match = [-1] * len(triangles)

def augment(left, seen):
    for right in triangles[left]:
        if right in seen:
            continue
        seen.add(right)
        if right_match[right] < 0 or augment(right_match[right], seen):
            right_match[right] = left
            left_match[left] = right
            return True
    return False

for left in range(len(triangles)):
    augment(left, set())

unmatched = [left for left, right in enumerate(left_match) if right < 0]
reachable_left = set(unmatched)
reachable_right = set()
stack = list(unmatched)
while stack:
    left = stack.pop()
    for right in triangles[left]:
        if left_match[left] == right:
            continue
        if right in reachable_right:
            continue
        reachable_right.add(right)
        matched_left = right_match[right]
        if matched_left >= 0 and matched_left not in reachable_left:
            reachable_left.add(matched_left)
            stack.append(matched_left)
neighbors = {right for left in reachable_left for right in triangles[left]}

assert (len(folds), len(triangles)) == (142, 116)
assert sum(right >= 0 for right in left_match) == 105
assert len(unmatched) == 11
assert neighbors == reachable_right
assert (len(reachable_left), len(reachable_right)) == (72, 61)

extended = []
fourth_cells = 0
for ids in triangles:
    a, c = folds[ids[0]][:2]
    x = folds[ids[2]][0]
    z = folds[ids[1]][1]
    neighborhood = set(ids)
    fourth = ac.get(tuple(sorted((x, z))))
    if fourth is not None:
        neighborhood.add(fourth)
        fourth_cells += 1
    extended.append(tuple(neighborhood))

right_match_2 = [-1] * len(folds)
def augment_2(left, seen):
    for right in extended[left]:
        if right in seen:
            continue
        seen.add(right)
        if right_match_2[right] < 0 or augment_2(right_match_2[right], seen):
            right_match_2[right] = left
            return True
    return False

extended_matching = sum(augment_2(left, set()) for left in range(len(extended)))
assert fourth_cells == 36
assert extended_matching == 105
print({
    "folds": len(folds),
    "triangles": len(triangles),
    "maximum_matching": 105,
    "Hall_left": len(reachable_left),
    "Hall_neighbors": len(reachable_right),
    "deficiency": len(reachable_left) - len(reachable_right),
    "triangles_with_fourth_fold": fourth_cells,
    "support_plus_fourth_matching": extended_matching,
})
