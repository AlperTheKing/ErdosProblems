"""Q4: rationalise a numerical subspace (the minimal-face kernel of a Gram block).

The kernel of the maximum-rank solution is a rational subspace (the minimal face of a rationally
defined spectrahedron), so its reduced row echelon form has rational entries.  We recover them by
RREF + limit_denominator, and then CHECK the result: (i) it contains the proved evaluation kernel,
(ii) it is invariant under the automorphism group.  Nothing here has to be trusted -- the kernel is
only used to STEER the search; the final certificate is verified from scratch by Q4_verify.
"""
from fractions import Fraction as F
import numpy as np


def rref_rational(rows, tol=1e-7, maxden=10**6):
    """Numerical RREF, then rationalise. rows: 2-d numpy array."""
    A = np.array(rows, dtype=float).copy()
    nr, nc = A.shape
    piv, r = [], 0
    for c in range(nc):
        if r >= nr:
            break
        i = int(np.argmax(np.abs(A[r:, c]))) + r
        if abs(A[i, c]) < tol:
            continue
        A[[r, i]] = A[[i, r]]
        A[r] = A[r] / A[r, c]
        for k in range(nr):
            if k != r:
                A[k] = A[k] - A[k, c] * A[r]
        piv.append(c)
        r += 1
    A = A[:r]
    out, err = [], 0.0
    for row in A:
        rr = []
        for v in row:
            f = F(float(v)).limit_denominator(maxden)
            err = max(err, abs(float(f) - v))
            rr.append(f)
        out.append(rr)
    return out, piv, err


def check_contains(basis, vectors, tol=None):
    """Exact test: is every vector in `vectors` in the rational row space of `basis`?"""
    B = [list(r) for r in basis]
    piv = []
    for r in B:
        nz = [i for i, v in enumerate(r) if v != 0]
        piv.append(nz[0] if nz else None)
    for v in vectors:
        w = list(v)
        for r, p in zip(B, piv):
            if p is not None and w[p] != 0:
                f = w[p] / r[p]
                w = [wi - f * ri for wi, ri in zip(w, r)]
        if any(x != 0 for x in w):
            return False
    return True
