"""
f8_named_patterns.py -- check which named triangle-free graphs are REDUCED
MAXIMAL triangle-free patterns, and run max_a psi on the ones with n <= 21.
"""
import sys, itertools
import numpy as np
from f8_core import (g6_decode, g6_encode, edges_of, is_triangle_free,
                     is_maximal_tf, is_twin_free, mono_sets)
from f8_families import (andrasfai, kneser, clebsch, cayley_Z, circular,
                         hoffman_singleton, higman_sims, grotzsch, mk)
from f8_wopt3 import tensors, psi_np, maxmin

CAND = []
for k in range(2, 9):
    CAND.append((f"Andrasfai({k}) [n={3*k-1}]", andrasfai(k)))
CAND.append(("Petersen", kneser(5, 2)))
CAND.append(("Clebsch", clebsch()))
CAND.append(("Grotzsch", grotzsch()))
CAND.append(("C13(1,5)", cayley_Z(13, [1, 5])))
CAND.append(("C16(1,2,7)", cayley_Z(16, [1, 2, 7])))
CAND.append(("C17(1,2,4,8)", cayley_Z(17, [1, 2, 4, 8])))
CAND.append(("HoffmanSingleton", hoffman_singleton()))
CAND.append(("HigmanSims", higman_sims()))
for n in [13, 16, 17, 18, 19, 20, 21, 22, 23]:
    CAND.append((f"Circular({n})", circular(n, 2 * n / 5.0, 3 * n / 5.0)))
    CAND.append((f"CircularThird({n})", circular(n, n / 3.0, 2 * n / 3.0)))

NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 20
print(f"{'graph':26s} {'n':>4} {'m':>5}  TF  maxTF twinfree   bip/N^2      max_a psi")
for name, (n, adj) in CAND:
    tf = is_triangle_free(n, adj)
    mt = is_maximal_tf(n, adj)
    tw = is_twin_free(n, adj)
    m = len(edges_of(n, adj))
    if not tf:
        print(f"{name:26s} {n:>4} {m:>5}  NO")
        continue
    if n <= NMAX:
        from f8_core import mono_sets_any_m
        E, sets = mono_sets_any_m(n, adj)
        sets = sets[:150]
        T = np.zeros((len(sets), n, n))
        for k, S in enumerate(sets):
            for b_ in S:
                i, j = E[b_]
                T[k, i, j] = T[k, j, i] = 1.0
        t, a = maxmin(n, T, 60)
        b = min(len(S) for S in sets)
        print(f"{name:26s} {n:>4} {m:>5}  yes {str(mt):5s} {str(tw):8s} "
              f"{b}/{n*n}={b/n**2:.6f}  UB={t:.10f} {'*** > 1/25 ***' if t>0.04+1e-9 else ''}")
    else:
        print(f"{name:26s} {n:>4} {m:>5}  yes {str(mt):5s} {str(tw):8s}   (n too large for full enumeration)")
