import json
from collections import Counter
from pathlib import Path


PATH = Path(__file__).with_name("c84_archived_audit.json")
data = json.loads(PATH.read_text(encoding="ascii"))


def verify(row, expected):
    B = tuple(row["B"])
    p, h, b = row["p"], row["h"], row["b"]
    assert len(B) == len(set(B)) == p
    assert tuple(sorted(B)) == B
    assert B[-1] == h - 1
    sums = {}
    for i, a in enumerate(B):
        for c in B[i:]:
            assert a + c not in sums
            sums[a + c] = (a, c)
    differences = Counter(y - x for i, x in enumerate(B) for y in B[i + 1:])
    assert len(differences) == p * (p - 1) // 2
    assert max(differences.values(), default=0) == 1
    assert set(differences).isdisjoint(s + b for s in sums)
    assert (3 * p * p - p + 2) // 2 - h > 0
    folds = []
    for s, (a, c) in sums.items():
        if s + h in sums:
            u, v = sums[s + h]
            assert a <= c < u <= v
            folds.append((a, c, u, v))
    ac = {(a, c): index for index, (a, c, _u, _v) in enumerate(folds)}
    au = {(a, u): index for index, (a, _c, u, _v) in enumerate(folds)}
    cu = {(c, u): index for index, (_a, c, u, _v) in enumerate(folds)}
    assert len(ac) == len(au) == len(cu) == len(folds)
    triangles = 0
    for a, c in ac:
        for u in B:
            ids = (ac.get((a, c)), au.get((a, u)), cu.get((c, u)))
            if None in ids or ids[0] == ids[1] == ids[2]:
                continue
            assert len(set(ids)) == 3
            triangles += 1
    assert (len(folds), triangles) == expected
    assert row["C_S"] == len(folds) and row["T_F"] == triangles
    return {"p": p, "h": h, "b": b, "C_S": len(folds), "T_F": triangles}


translation = verify(data["translation"]["max_ratio_row"], (142, 116))
insertion = verify(data["insertion"]["max_ratio_row"], (51, 37))
assert data["translation"]["failures"] == 0
assert data["insertion"]["failures"] == 0
print({"translation_max": translation, "insertion_max": insertion})
