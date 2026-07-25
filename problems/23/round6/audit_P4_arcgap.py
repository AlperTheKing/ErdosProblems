"""audit_P4_arcgap - is ARCBOUND ever STRICTLY bigger than psi for a circle measure?
P4 flags 'sup ARCBOUND <= 1/25 is strictly stronger than Erdos 23 on circle graphs'.  That is
formally right (ARCBOUND >= psi), but if the two functionals coincide on circle measures the
strengthening is vacuous.  Random + structured exact test."""
import random
from fractions import Fraction as F
from audit_P4_core import adj_matrix, normalise, arcbound, psi_bruteforce

rng = random.Random(20260725)
gap = 0
n = 0
worst = None
for trial in range(400):
    m = rng.choice([5, 7, 8, 10, 11, 12, 13, 14, 16, 17, 18, 20])
    w = [rng.choice([0, 0, 1, 2, 3, 4, 5]) for _ in range(m)]
    if sum(w) == 0 or sum(1 for t in w if t) > 14:
        continue
    x = normalise(w)
    adj = adj_matrix(m)
    ab = arcbound(x, adj, m)
    ps = psi_bruteforce(x, adj, m)
    n += 1
    if ab != ps:
        gap += 1
        if worst is None or ab - ps > worst[0]:
            worst = (ab - ps, m, w, ab, ps)
print(f"tested {n} exact random circle measures: ARCBOUND != psi in {gap} of them")
if worst:
    print("  largest gap:", worst)
else:
    print("  ARCBOUND == psi in every case (the arc family always contains an optimal cut here)")
