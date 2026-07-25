"""Q4: EXACT rational verification of a multiplier-Positivstellensatz certificate.

Input: rationals c, nu[S][m] >= 0, and rational symmetric Gram blocks Q_b indexed by the
parity classes of degree-(2d+2) exponent vectors.

Checks, all in exact Fraction arithmetic:
  (V1) nu[S][m] >= 0 for all S,m;
  (V2) sum_S nu[S][m] == c * multinom(m)                      for every degree-2d monomial m;
  (V3) multinom(alpha) - sum_S sum_{(u,v) in mono(S)} nu[S][alpha-e_u-e_v]
         == sum_{blocks} sum_{beta+gamma=2 alpha} Q[beta,gamma] for every degree-(2d+2) alpha;
  (V4) every Q_b is positive semidefinite (exact LDL^T with symmetric pivoting).
If all pass then  max_{x>=0} psi(H,x) <= 1/c  is PROVED.
"""
from fractions import Fraction
from Q4_sos import monomials, multinom, parity_blocks


def exact_psd(M):
    """Exact PSD test for a symmetric matrix of Fractions (list of lists). Returns (ok, info)."""
    k = len(M)
    A = [[Fraction(M[i][j]) for j in range(k)] for i in range(k)]
    idx = list(range(k))
    rank = 0
    for step in range(k):
        # pick pivot: largest remaining diagonal entry
        p = max(range(step, k), key=lambda i: A[i][i])
        if A[p][p] < 0:
            return False, f"negative diagonal {A[p][p]} at step {step}"
        if A[p][p] == 0:
            # remaining diagonal all zero => the whole remaining block must be zero
            for i in range(step, k):
                for j in range(step, k):
                    if A[i][j] != 0:
                        return False, f"zero diagonal but nonzero entry ({idx[i]},{idx[j]})={A[i][j]}"
            return True, f"rank {rank}"
        A[step], A[p] = A[p], A[step]
        for r in range(k):
            A[r][step], A[r][p] = A[r][p], A[r][step]
        idx[step], idx[p] = idx[p], idx[step]
        d = A[step][step]
        rank += 1
        for i in range(step + 1, k):
            f = A[i][step] / d
            if f == 0:
                continue
            for j in range(step + 1, k):
                A[i][j] -= f * A[step][j]
            A[i][step] = Fraction(0)
        for j in range(step + 1, k):
            A[step][j] = A[step][j]  # keep upper part (unused)
    return True, f"rank {rank}"


def verify(n, E, cuts, d, c, nu, Qblocks, verbose=True):
    """nu: dict (S_index, monomial tuple) -> Fraction ; Qblocks: list of (basis list, matrix)."""
    D, DT = 2 * d, 2 * d + 2
    monsD = monomials(n, D)
    monsT = monomials(n, DT)
    c = Fraction(c)
    # V1
    for k_, v in nu.items():
        if v < 0:
            return False, f"V1 negative multiplier coefficient {k_} = {v}"
    # V2
    for m in monsD:
        s = sum(nu.get((S, m), Fraction(0)) for S in range(len(cuts)))
        if s != c * multinom(m):
            return False, f"V2 fails at {m}: {s} != {c * multinom(m)}"
    # V3
    lhs = {a: Fraction(multinom(a)) for a in monsT}
    for S, (_mask, mono) in enumerate(cuts):
        for k in mono:
            u, v = E[k]
            for m in monsD:
                val = nu.get((S, m), Fraction(0))
                if val == 0:
                    continue
                a = list(m)
                a[u] += 1
                a[v] += 1
                lhs[tuple(a)] -= val
    rhs = {a: Fraction(0) for a in monsT}
    for B, M in Qblocks:
        k = len(B)
        for i in range(k):
            for j in range(k):
                a = tuple((B[i][t] + B[j][t]) // 2 for t in range(n))
                rhs[a] += Fraction(M[i][j])
    for a in monsT:
        if lhs[a] != rhs[a]:
            return False, f"V3 fails at {a}: target {lhs[a]} != Gram {rhs[a]}"
    # V4
    for bi, (B, M) in enumerate(Qblocks):
        ok, info = exact_psd(M)
        if not ok:
            return False, f"V4 fails on block {bi} (size {len(B)}, parity {tuple(x%2 for x in B[0])}): {info}"
    if verbose:
        print("   EXACT VERIFICATION PASSED: max psi <= 1/%s" % c)
    return True, "ok"
