"""Empirical check of Lemma A: bip(H[t]) = min_{S} sum_{ij in E uncut by S} t_i t_j.

Brute-force bip of the *explicit* blow-up graph is compared with the
subset formula, over all triangle-free graphs on <= 5 vertices and many
random weight vectors.  Exact integers only.
"""
import random
from itertools import combinations
from f1_bip import bip_bruteforce, blowup_bip, expand, is_triangle_free

random.seed(20260725)


def all_graphs(n):
    pairs = list(combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        yield [pairs[i] for i in range(len(pairs)) if (mask >> i) & 1]


bad = 0
tested = 0
for n in range(2, 6):
    for E in all_graphs(n):
        if not is_triangle_free(n, E):
            continue
        for trial in range(6):
            t = [random.randint(1, 3) for _ in range(n)]
            if sum(t) > 13:
                continue
            N, EE = expand(n, E, t)
            lhs = bip_bruteforce(N, EE)
            rhs = blowup_bip(n, E, t)
            tested += 1
            if lhs != rhs:
                bad += 1
                print("MISMATCH", n, E, t, lhs, rhs)
print("tested", tested, "mismatches", bad)

# specialised check: bip(H[t,...,t]) = t^2 bip(H)
bad2 = 0
for n in range(2, 6):
    for E in all_graphs(n):
        if not is_triangle_free(n, E):
            continue
        b = bip_bruteforce(n, E)
        for t in (2, 3):
            if n * t > 14:
                continue
            N, EE = expand(n, E, [t] * n)
            if bip_bruteforce(N, EE) != t * t * b:
                bad2 += 1
                print("SCALE MISMATCH", n, E, t)
print("scaling mismatches", bad2)

# C5 formula: bip(C5[t]) = min_i t_i t_{i+1}
C5 = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]
bad3 = 0
for trial in range(300):
    t = [random.randint(1, 3) for _ in range(5)]
    f = min(t[i] * t[(i + 1) % 5] for i in range(5))
    if blowup_bip(5, C5, t) != f:
        bad3 += 1
        print("C5 MISMATCH", t)
print("C5 formula mismatches", bad3)
