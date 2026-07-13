from collections import Counter


B = [
    3, 5, 69, 169, 211, 223, 251, 329, 373, 403, 409,
    501, 505, 519, 631, 639, 689, 715, 775, 863, 883,
    915, 931, 953, 977, 987,
]
h, b = 988, 1

pairs = {q + r: (q, r) for i, q in enumerate(B) for r in B[i:]}
assert len(pairs) == len(B) * (len(B) + 1) // 2
assert not any(q + r + t + b == v for q in B for r in B for t in B for v in B)
folds = []
for t, (a, c) in pairs.items():
    if t + h in pairs:
        folds.append((a, c, *pairs[t + h]))
AC = {(a, c): (r, s) for a, c, r, s in folds}
AU = {(a, u): (z, w) for a, z, u, w in folds}
CU = {(c, u): (x, y) for x, c, u, y in folds}
assert len(AC) == len(AU) == len(CU) == len(folds)

chambers = Counter()
triangles = 0
for (a, c), (r, s) in AC.items():
    for u in B:
        if (a, u) not in AU or (c, u) not in CU or u == r:
            continue
        z, w = AU[a, u]
        x, y = CU[c, u]
        K = a + c + h - u
        X, Z, R = x - a, z - c, r - u
        tau, lam = h - b - K, h - b - u
        assert (x, z, r, y, w, s) == (a + X, c + Z, u + R, K + X, K + Z, K - R)
        assert X != 0 and Z != 0 and R != 0
        assert K > c and K not in B
        assert all(q not in B for q in (tau, tau - X, tau - Z, tau + R, lam, lam - R))
        chamber = "".join("+" if q > 0 else "-" for q in (X, Z, R))
        chambers[chamber] += 1
        triangles += 1
expected = {"+++": 2, "++-": 11, "+--": 4, "-+-": 2, "--+": 5, "---": 1}
assert len(folds) == 51
assert triangles == 25
assert dict(sorted(chambers.items())) == expected
print({"folds": len(folds), "triangles": triangles, "chambers": expected})
