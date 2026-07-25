"""Q4: facial reduction -- find the EXTRA forced kernel beyond the evaluation vectors.

If x in Z, j outside supp(x) and dT/dx_j(x) = 0, then writing x(s) = x + s e_j and y_j = sqrt(s),
    T(x(s)) = s * (w^T Q w) + O(s^{3/2}),   w_beta = x^{(beta - p)/2},  p = parity(beta) containing j,
so w is also forced into the kernel -- same rational shape as an evaluation vector but living in a
block whose parity meets the complement of supp(x).  This module tests, block by block, which of
those candidate vectors the numerical face solution actually annihilates.
"""
import sys, pickle
import numpy as np
from fractions import Fraction as F
from Q4_sos import parity_blocks
from Q4_zeroset import block_kernel

sol = pickle.load(open(sys.argv[1], "rb"))
n, d, Z = sol['n'], sol['d'], sol['Z']
print(f"n={n} d={d} margin t*={sol['t']:.3e}  |Z|={len(Z)}")


def cand_vectors(n, B, x):
    """(x^{(beta-p)/2})_beta -- nonzero even when supp(p) is not inside supp(x)."""
    p = tuple(b % 2 for b in B[0])
    row = []
    for b in B:
        val = F(1)
        for i in range(n):
            e = (b[i] - p[i]) // 2
            if e:
                val *= x[i] ** e
        row.append(val)
    return row, p


tot_extra = 0
for (B, Q), K in zip(sol['Q'], sol['K']):
    k = len(B)
    if k == 1:
        continue
    p = tuple(b % 2 for b in B[0])
    Kf = np.array([[float(v) for v in r] for r in K]) if K else np.zeros((0, k))
    # numerical kernel
    ev, V = np.linalg.eigh(Q)
    nk = int((ev < 1e-8 * max(1.0, ev.max())).sum())
    # candidate extra vectors: evaluation-shape vectors for points x whose support misses part of p
    extra = []
    for x in Z:
        if all(x[i] != 0 for i in range(n) if p[i]):
            continue                                   # already an evaluation vector (in K)
        w, _ = cand_vectors(n, B, x)
        wf = np.array([float(v) for v in w])
        if np.linalg.norm(wf) == 0:
            continue
        r = np.linalg.norm(Q @ wf) / np.linalg.norm(wf)
        if r < 1e-6:
            extra.append((x, r))
    if extra or nk != len(K):
        print(f" block size {k} parity {p}: forced kernel {len(K)}, numerical kernel {nk}, "
              f"annihilated candidates {len(extra)} (min residual "
              f"{min((r for _x, r in extra), default=float('nan')):.2e})")
        tot_extra += len(extra)
print(f"total annihilated extra candidates: {tot_extra}")
