"""Validation:
(1) class-respecting lemma: bip(H[w]) computed over class-respecting cuts only equals the
    true bip over ALL 2^(N-1) bipartitions of the explicit blow-up;
(2) bip(C5[n]) = n^2 = N^2/25;
(3) sanity of the exhaustive vs hill-climbing maximiser.
"""
import random, itertools
from beta import Template, explicit_blowup, bip_bruteforce, maximize, maximize_exhaustive

C5 = (5, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)])
PET = (10, [(0,1),(1,2),(2,3),(3,4),(4,0),(0,5),(1,6),(2,7),(3,8),(4,9),
            (5,7),(7,9),(9,6),(6,8),(8,5)])
C7 = (7, [(i, (i + 1) % 7) for i in range(7)])
K33 = (6, [(i, 3 + j) for i in range(3) for j in range(3)])

print("--- (1) class-respecting lemma, random small blow-ups ---")
rng = random.Random(7)
bad = 0
for (n, E) in [C5, C7, K33, (4, [(0,1),(1,2),(2,3),(3,0)])]:
    t = Template(n, E)
    for trial in range(12):
        while True:
            w = [rng.randint(0, 3) for _ in range(n)]
            N = sum(w)
            if 1 <= N <= 16:
                break
        cw, _ = t.bip(w)
        N, EE = explicit_blowup(n, E, w)
        tr = bip_bruteforce(N, EE) if N >= 1 else 0
        if cw != tr:
            bad += 1
            print("  MISMATCH n=%d w=%s classwise=%d true=%d" % (n, w, cw, tr))
print("  mismatches:", bad)

print("--- (2) bip(C5[n]) ---")
t5 = Template(*C5)
for n in range(1, 9):
    v, cut = t5.bip([n] * 5)
    print("   n=%d  N=%2d  bip=%3d  N^2/25=%6.2f  25*bip-N^2=%d" % (n, 5 * n, v, (5 * n) ** 2 / 25, 25 * v - (5 * n) ** 2))

print("--- (3) maximiser: exhaustive vs hill-climb, D=15 ---")
for name, (n, E) in [("C5", C5), ("C7", C7), ("K33", K33), ("Petersen", PET)]:
    t = Template(n, E)
    D = 15
    if n <= 7:
        be, we = maximize_exhaustive(t, D)
    else:
        be, we = (None, None)
    bh, wh = maximize(t, D, restarts=40, seed=1)
    print("   %-9s exhaustive=%s hill=%s  w=%s   25*bip/D^2=%.6f" %
          (name, be, bh, wh, 25 * bh / D ** 2))
