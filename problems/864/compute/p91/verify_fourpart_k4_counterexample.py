B = [
    3, 5, 69, 169, 211, 223, 251, 329, 373, 403, 409,
    501, 505, 519, 631, 639, 689, 715, 775, 863, 883,
    915, 931, 953, 977, 987,
]
h = 988
H = h - 1

sum_pair = {}
for i, a in enumerate(B):
    for c in B[i:]:
        assert a + c not in sum_pair
        sum_pair[a + c] = (a, c)

folds = []
for s, (a, c) in sum_pair.items():
    if s + h in sum_pair:
        u, v = sum_pair[s + h]
        folds.append((a, c, H - v, H - u))

pair_support = {(i, j): set() for i in range(4) for j in range(i + 1, 4)}
for fold in folds:
    for i, j in pair_support:
        key = (fold[i], fold[j])
        assert key not in pair_support[i, j]
        pair_support[i, j].add(key)

values = [sorted({fold[i] for fold in folds}) for i in range(4)]
canonical = set(folds)
cliques = []
for a in values[0]:
    for c in values[1]:
        if (a, c) not in pair_support[0, 1]:
            continue
        for alpha in values[2]:
            if (a, alpha) not in pair_support[0, 2]:
                continue
            if (c, alpha) not in pair_support[1, 2]:
                continue
            for beta in values[3]:
                vertex = (a, c, alpha, beta)
                if all(
                    (vertex[i], vertex[j]) in pair_support[i, j]
                    for i, j in pair_support
                ):
                    cliques.append(vertex)

noncanonical = sorted(set(cliques) - canonical)
assert len(folds) == 51
assert len(cliques) == 106
assert len(noncanonical) == 55
assert (3, 329, 10, 356) in noncanonical

print({
    "folds": len(folds),
    "shadow_K4": len(cliques),
    "canonical": len(canonical),
    "noncanonical": len(noncanonical),
})
