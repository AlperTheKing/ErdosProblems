"""R-D gate (M) falsifier probe: exact offset-support counts D_{a,b,c} = |D_{a,b,c}|
along supercritical rays, via the exact recursion (48)/(60):
  R_{a,b,c}(d) = R_{a-1,b,c}(d/2)[2|d] + R_{a,b-1,c}((d-1)/3)[d=1 mod 3] + R_{a,b,c-1}((d-3)/5)[d=3 mod 5]
Multiplicity arrays R over [0, 2^a 3^b 5^c) built by strided adds (vectorized, exact int64).
Ray must be SUPERCRITICAL (word entropy > slope rate) for the (M) question to be nontrivial:
  (3,2,1): H=1.0114 > 0.9810 rate; letters n=6k, M_k=360^k.
  (2,1,1): H=1.0397 > 1.0235 rate; letters n=4k, M_k=60^k.
Report: D_k, D_k/M_k, normalized sqrt(n)*D_k/M_k (the (M) invariant), W_k (validated vs
multinomial), E^off, and the CS floor W^2/E^off <= D (sanity).
Falsifier (64): the normalized sequence tending to 0 kills the symmetric mass gate on that ray.
"""
import sys, hashlib
from math import comb, sqrt
import numpy as np

def multinomial(a, b, c):
    return comb(a + b + c, a) * comb(b + c, b)

def run_ray(va, vb, vc, kmax):
    print(f"ray ({va},{vb},{vc}), k = 1..{kmax}")
    A, B, C = va * kmax, vb * kmax, vc * kmax
    R = {(0, 0, 0): np.array([1], dtype=np.int64)}
    layers = {0: [(0, 0, 0)]}
    targets = {(va * k, vb * k, vc * k): k for k in range(1, kmax + 1)}
    results = {}
    maxn = A + B + C
    for n in range(1, maxn + 1):
        layers[n] = []
        for a in range(min(a_ := A, n), -1, -1):
            for b in range(min(B, n - a), -1, -1):
                c = n - a - b
                if c < 0 or c > C: continue
                M = (2**a) * (3**b) * (5**c)
                t = np.zeros(M, dtype=np.int64)
                if a > 0: t[0::2] += R[(a - 1, b, c)]
                if b > 0: t[1::3] += R[(a, b - 1, c)]
                if c > 0: t[3::5] += R[(a, b, c - 1)]
                R[(a, b, c)] = t
                layers[n].append((a, b, c))
                if (a, b, c) in targets:
                    k = targets[(a, b, c)]
                    W = int(t.sum()); D = int(np.count_nonzero(t))
                    Eoff = int((t.astype(np.int64) ** 2).sum())
                    Wchk = multinomial(a, b, c)
                    letters = a + b + c
                    norm = D / M * sqrt(letters)
                    results[k] = (M, W, Wchk, D, Eoff, norm)
                    print(f"  k={k}: M={M}  W={W} (check {Wchk} {'OK' if W==Wchk else 'MISMATCH'})  "
                          f"D={D}  D/M={D/M:.6f}  sqrt(n)*D/M={norm:.4f}  "
                          f"E^off={Eoff}  CSfloor={W*W//Eoff} (<= D: {'OK' if W*W//Eoff <= D else 'VIOLATION'})")
        if n - 1 in layers:
            for key in layers[n - 1]: del R[key]
            del layers[n - 1]
    return results

run_ray(3, 2, 1, int(sys.argv[1]) if len(sys.argv) > 1 else 3)
print()
run_ray(2, 1, 1, int(sys.argv[2]) if len(sys.argv) > 2 else 4)
print("script SHA-256:", hashlib.sha256(open(__file__, 'rb').read()).hexdigest())
