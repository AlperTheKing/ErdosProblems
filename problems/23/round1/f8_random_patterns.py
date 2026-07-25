"""
f8_random_patterns.py n count seed
Sample random REDUCED MAXIMAL triangle-free patterns on n vertices (triangle-free
process run to saturation gives a maximal triangle-free graph; we keep the
twin-free ones) and report an upper bound on max_a psi(H,a).
"""
import sys, random
import numpy as np
from f8_core import (g6_encode, is_triangle_free, is_maximal_tf, is_twin_free,
                     mono_sets_any_m, edges_of)
from f8_wopt3 import maxmin

n, count, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
rnd = random.Random(seed)
TARGET = 1.0 / 25.0
best = 0.0
done = 0
tries = 0
while done < count and tries < count * 30:
    tries += 1
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    rnd.shuffle(pairs)
    adj = [0] * n
    for (i, j) in pairs:
        if adj[i] & adj[j]:
            continue
        adj[i] |= 1 << j
        adj[j] |= 1 << i
    if not (is_triangle_free(n, adj) and is_maximal_tf(n, adj) and is_twin_free(n, adj)):
        continue
    done += 1
    E, sets = mono_sets_any_m(n, adj)
    sets = sets[:130]
    T = np.zeros((len(sets), n, n))
    for k, S in enumerate(sets):
        for b in S:
            i, j = E[b]
            T[k, i, j] = T[k, j, i] = 1.0
    t, a = maxmin(n, T, 30)
    best = max(best, t)
    if t > TARGET + 1e-9:
        print(f"EXCEEDS {g6_encode(n,adj)} n={n} psi={t:.10f}", flush=True)
print(f"n={n} seed={seed} sampled={done} maxUB={best:.10f} "
      f"{'OVER' if best > TARGET + 1e-9 else 'ok'}")
