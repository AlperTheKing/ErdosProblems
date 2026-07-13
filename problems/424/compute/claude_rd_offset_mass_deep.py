"""Deep (M)-gate points: bool-only D counts (no multiplicities) for larger k.
Same recursion as claude_rd_offset_mass_probe.py but with boolean support arrays
(strided OR), two-layer freeing. Args: va vb vc kmax.
"""
import sys, hashlib
from math import sqrt
import numpy as np

va, vb, vc, kmax = (int(x) for x in sys.argv[1:5])
A, B, C = va * kmax, vb * kmax, vc * kmax
R = {(0, 0, 0): np.array([True])}
layers = {0: [(0, 0, 0)]}
targets = {(va * k, vb * k, vc * k): k for k in range(1, kmax + 1)}
print(f"ray ({va},{vb},{vc}) bool-only, k=1..{kmax}, final M={(2**A)*(3**B)*(5**C)}", flush=True)
for n in range(1, A + B + C + 1):
    layers[n] = []
    for a in range(min(A, n), -1, -1):
        for b in range(min(B, n - a), -1, -1):
            c = n - a - b
            if c < 0 or c > C: continue
            M = (2**a) * (3**b) * (5**c)
            t = np.zeros(M, dtype=bool)
            if a > 0: t[0::2] |= R[(a - 1, b, c)]
            if b > 0: t[1::3] |= R[(a, b - 1, c)]
            if c > 0: t[3::5] |= R[(a, b, c - 1)]
            R[(a, b, c)] = t
            layers[n].append((a, b, c))
            if (a, b, c) in targets:
                k = targets[(a, b, c)]
                D = int(np.count_nonzero(t))
                print(f"  k={k}: M={M}  D={D}  D/M={D/M:.6f}  sqrt(n)*D/M={D/M*sqrt(a+b+c):.4f}", flush=True)
    if n - 1 in layers:
        for key in layers[n - 1]: del R[key]
        del layers[n - 1]
print("script SHA-256:", hashlib.sha256(open(__file__, 'rb').read()).hexdigest())
