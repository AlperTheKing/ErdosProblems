#!/usr/bin/env python3
"""Standalone exact verifier for the P105 corrected-C84 witness."""

from collections import Counter
from hashlib import sha256


B = (
    1, 245, 327, 703, 977, 999, 1057, 1107, 1363, 1675, 1677, 1841,
    1883, 2103, 2141, 2235, 2681, 2829, 2899, 3041, 3217, 3227, 3235,
    3431, 3707, 3733, 3851, 4115, 4149, 4307, 4347, 4481, 4641, 4761,
    4951, 5043, 5129, 5193, 5197, 5309, 5577, 5679, 5803, 5901, 5917,
    6053, 6141, 6153, 6263, 6341, 6369, 6401, 6425, 6431, 6445, 6497,
    6571,
)
H = 6572
OFFSET = 1


sum_count = Counter(
    B[i] + B[j] for i in range(len(B)) for j in range(i, len(B))
)
pair_at_sum = {
    B[i] + B[j]: (B[i], B[j])
    for i in range(len(B)) for j in range(i, len(B))
}
diff_count = Counter(
    B[j] - B[i] for i in range(len(B)) for j in range(i + 1, len(B))
)
differences = set(diff_count)

folds = []
for low in sorted(pair_at_sum):
    if low + H not in pair_at_sum:
        continue
    a, c = pair_at_sum[low]
    u, v = pair_at_sum[low + H]
    assert a <= c < u <= v
    folds.append((a, c, u, v))

ac = {(a, c): i for i, (a, c, _u, _v) in enumerate(folds)}
au = {(a, u): i for i, (a, _c, u, _v) in enumerate(folds)}
cu = {(c, u): i for i, (_a, c, u, _v) in enumerate(folds)}
triangles = []
for a, c in ac:
    for aa, u in au:
        if aa != a or (c, u) not in cu:
            continue
        ids = (ac[a, c], au[a, u], cu[c, u])
        if ids[0] == ids[1] == ids[2]:
            continue
        assert len(set(ids)) == 3
        triangles.append(ids)

collisions = [fold for fold in folds if fold[0] + fold[1] + OFFSET in differences]
literal_hole = differences.isdisjoint(total + OFFSET for total in sum_count)
digest = sha256(",".join(map(str, B)).encode("ascii")).hexdigest()
delta = (3 * len(B) * len(B) - len(B) + 2) // 2 - H

assert B[-1] == H - 1
assert len(sum_count) == len(B) * (len(B) + 1) // 2
assert max(sum_count.values()) == 1
assert len(diff_count) == len(B) * (len(B) - 1) // 2
assert max(diff_count.values()) == 1
assert literal_hole
assert len(folds) == 159
assert len(triangles) == 160
assert len(collisions) == 0
assert len(triangles) > len(folds) + len(collisions)
assert digest == "760cd38d911ce0790ab6e1ce71b5e7e6bb888d3d2a8f3ce150d9abdbc3fdce99"

print({
    "p": len(B), "h": H, "b": OFFSET, "delta": delta,
    "C_S": len(folds), "T_F": len(triangles), "V_b": len(collisions),
    "excess": len(triangles) - len(folds) - len(collisions),
    "literal_hole": literal_hole, "sha256": digest,
})
