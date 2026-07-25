#!/usr/bin/env python3
"""Exact Ehrhart engine for general 3xN transportation polytopes.

T(r,c) = { 3xN nonneg integer matrices with row sums r, column sums c }.
L_T(n) = # of 3xN nonneg integer matrices with row sums n*r, column sums n*c.

Two independent counters:
  count_naive : per-column (a,b) enumeration DP (obviously correct, slow)
  count_fast  : O(states) per column via prefix/anti-diagonal region sums

Ehrhart polynomial via exact Fraction Newton interpolation from n=0..d,
verified at held-out dilations d+1, d+2.  Also h*-vector and codegree.
"""
from __future__ import annotations
from fractions import Fraction
from functools import lru_cache
import itertools, sys


# ---------------------------------------------------------------------------
# Naive counter (validation reference)
# ---------------------------------------------------------------------------
def count_naive(rowsums, colsums):
    """# of 3 x len(colsums) nonneg integer matrices with given margins."""
    rowsums = tuple(rowsums); colsums = tuple(colsums)
    if len(rowsums) != 3:
        raise ValueError("naive counter is for exactly 3 rows")
    if min(rowsums, default=0) < 0 or min(colsums, default=0) < 0:
        return 0
    if sum(rowsums) != sum(colsums):
        return 0
    R1, R2, R3 = rowsums
    cols = colsums
    m = len(cols)
    csuf = [0]*(m+1)
    for j in range(m):
        csuf[j+1] = csuf[j] + cols[j]

    @lru_cache(maxsize=None)
    def dp(j, u0, u1):
        if j == m:
            return 1 if (u0 == R1 and u1 == R2) else 0
        v = cols[j]
        total = 0
        # choose entry a in row0, b in row1, c=v-a-b in row2
        amax = min(v, R1 - u0)
        for a in range(amax + 1):
            bmax = min(v - a, R2 - u1)
            for b in range(bmax + 1):
                c = v - a - b
                u2 = csuf[j] - u0 - u1  # row2 used before this column
                if u2 + c <= R3:
                    total += dp(j+1, u0 + a, u1 + b)
        return total
    res = dp(0, 0, 0)
    dp.cache_clear()
    return res


# ---------------------------------------------------------------------------
# Fast counter: O(states) per column region-sum convolution
# ---------------------------------------------------------------------------
def count_fast(rowsums, colsums):
    rowsums = tuple(rowsums); colsums = tuple(colsums)
    if len(rowsums) != 3:
        raise ValueError("fast counter is for exactly 3 rows")
    if min(rowsums, default=0) < 0 or min(colsums, default=0) < 0:
        return 0
    if sum(rowsums) != sum(colsums):
        return 0
    R1, R2, R3 = rowsums
    N = sum(colsums)
    # dp[s1][s2] = number of partial fillings of processed columns with
    # row0 partial sum s1, row1 partial sum s2 (row2 partial determined).
    dp = [[0]*(R2+1) for _ in range(R1+1)]
    dp[0][0] = 1
    processed = 0
    for v in colsums:
        processed_next = processed + v
        # new[s1][s2] = sum_{a+b<=v, a<=s1, b<=s2} dp[s1-a][s2-b]
        # then apply row-2 upper bound: s3 = processed_next - s1 - s2 <= R3
        # i.e. s1 + s2 >= processed_next - R3
        new = _region_convolve(dp, v, R1, R2)
        lowbound = processed_next - R3
        for s1 in range(R1+1):
            row = new[s1]
            for s2 in range(R2+1):
                if s1 + s2 < lowbound:
                    row[s2] = 0
        dp = new
        processed = processed_next
    return dp[R1][R2]


def _region_convolve(dp, v, R1, R2):
    """Return new[s1][s2] = sum_{a>=0,b>=0,a+b<=v, a<=s1, b<=s2} dp[s1-a][s2-b]."""
    # Row prefix RP[p][q] = sum_{q'<=q} dp[p][q']
    RP = [[0]*(R2+1) for _ in range(R1+1)]
    for p in range(R1+1):
        dprow = dp[p]; rprow = RP[p]
        acc = 0
        for q in range(R2+1):
            acc += dprow[q]
            rprow[q] = acc
    # 2D prefix P2[s1][s2] = sum_{p<=s1} RP[p][s2]
    P2 = [[0]*(R2+1) for _ in range(R1+1)]
    for s2 in range(R2+1):
        acc = 0
        for s1 in range(R1+1):
            acc += RP[s1][s2]
            P2[s1][s2] = acc

    def RPval(p, q):
        if p < 0 or p > R1:
            return 0
        if q < 0:
            return 0
        if q > R2:
            q = R2
        return RP[p][q]

    def P2val(s1, s2):
        if s1 < 0 or s2 < 0:
            return 0
        return P2[s1][s2]

    # Anti-diagonal prefix sums of RP by M = p + q.
    # S_M is a dict: for diagonal M, cumulative sum over p ascending of RP[p][M-p].
    # We'll store SdiagCum[M] as list indexed by p (0..R1) giving cumulative
    # sum_{p'<=p} RP[p'][M-p'] (only where 0<=M-p'<=R2 contributes; else 0).
    maxM = R1 + R2
    SdiagCum = [None]*(maxM+1)
    for M in range(maxM+1):
        cum = [0]*(R1+1)
        run = 0
        for p in range(R1+1):
            q = M - p
            if 0 <= q <= R2:
                run += RP[p][q]
            cum[p] = run
        SdiagCum[M] = cum

    def Sval(M, p):
        # cumulative sum over p'<=p on diagonal M
        if M < 0 or M > maxM:
            return 0
        if p < 0:
            return 0
        if p > R1:
            p = R1
        return SdiagCum[M][p]

    new = [[0]*(R2+1) for _ in range(R1+1)]
    for s1 in range(R1+1):
        for s2 in range(R2+1):
            first = P2val(s1, s2) - P2val(s1 - v - 1, s2)
            M = s1 + s2 - v - 1
            if M < 0:
                second = 0
            else:
                second = Sval(M, s1) - Sval(M, s1 - v - 1)
            new[s1][s2] = first - second
    return new


# ---------------------------------------------------------------------------
# Ehrhart machinery
# ---------------------------------------------------------------------------
def ehrhart_values(r, c, upto, counter=count_fast):
    return [counter([n*x for x in r], [n*x for x in c]) for n in range(upto+1)]


def newton_interpolate(values):
    """values[n] for n=0..d define degree<=d polynomial; return coeff list
    (low degree first) as Fractions in the monomial basis."""
    d = len(values) - 1
    # finite differences
    xs = list(range(d+1))
    ys = [Fraction(v) for v in values]
    # divided differences (integer nodes -> use forward differences)
    diffs = [ys[:]]
    for k in range(1, d+1):
        prev = diffs[-1]
        diffs.append([prev[i+1]-prev[i] for i in range(len(prev)-1)])
    # Newton forward: P(x) = sum_k C(x,k) * Delta^k y[0]
    # Convert binomial C(x,k) to monomial coeffs.
    coeffs = [Fraction(0)]*(d+1)
    # precompute monomial expansion of falling factorial x(x-1)...(x-k+1)/k!
    for k in range(d+1):
        dk = diffs[k][0]
        if dk == 0:
            continue
        # binom(x,k) = (1/k!) * prod_{i=0}^{k-1}(x-i)
        poly = [Fraction(1)]
        for i in range(k):
            # multiply by (x - i)
            newp = [Fraction(0)]*(len(poly)+1)
            for e, ce in enumerate(poly):
                newp[e]   += ce * (-i)
                newp[e+1] += ce
            poly = newp
        fact = 1
        for i in range(1, k+1):
            fact *= i
        for e, ce in enumerate(poly):
            coeffs[e] += dk * ce / fact
    return coeffs


def poly_eval(coeffs, n):
    return sum(c * (n**k) for k, c in enumerate(coeffs))


def hstar_vector(coeffs, dim):
    """h*-vector from Ehrhart coeffs: sum h*_i z^i = (1-z)^{d+1} sum_{n>=0} L(n) z^n.
    Compute via L(0..dim) and the standard transform."""
    # h*_j = sum_{i=0}^{j} (-1)^i C(d+1,i) L(j-i)
    from math import comb
    L = [poly_eval(coeffs, n) for n in range(dim+1)]
    h = []
    for j in range(dim+1):
        s = Fraction(0)
        for i in range(j+1):
            s += (-1)**i * comb(dim+1, i) * L[j-i]
        h.append(s)
    return h


def analyze(r, c, verbose=False, counter=count_fast):
    # Ehrhart polynomial is invariant under permuting rows.  Put the LARGEST
    # row margin last (it becomes the "determined" row in the DP), so the DP
    # state (nR1+1)x(nR2+1) uses the two SMALLEST margins -> small & fast.
    r = tuple(sorted(int(x) for x in r)); c = tuple(c)
    dim = (3-1)*(len(c)-1)  # full dim for all-positive margins
    # need dim+1 points to interpolate + 2 held out
    vals = ehrhart_values(r, c, dim+2, counter=counter)
    coeffs = newton_interpolate(vals[:dim+1])
    # verify held-out
    ok = all(poly_eval(coeffs, n) == vals[n] for n in (dim+1, dim+2))
    if not ok:
        return None
    if poly_eval(coeffs, 0) != 1:
        return None
    h = hstar_vector(coeffs, dim)
    return {
        "r": r, "c": c, "dim": dim,
        "coeffs": coeffs,
        "L1": vals[1],
        "hstar": h,
        "min_coeff": min(coeffs),
        "linear_coeff": coeffs[1],
        "any_negative": any(x < 0 for x in coeffs),
        "vals": vals,
    }


if __name__ == "__main__":
    # quick self-test
    print("naive vs fast small checks:")
    tests = [
        ((3,3,3),(2,1,1,1,1,1,1,1)),
        ((3,4,5),(3,2,2,1,1,1,1,1)),
        ((4,4,4),(2,2,2,2,1,1,1,1)),
    ]
    for r,c in tests:
        for n in range(0,4):
            rn=[n*x for x in r]; cn=[n*x for x in c]
            a=count_naive(rn,cn); b=count_fast(rn,cn)
            assert a==b, (r,c,n,a,b)
        print("  ok", r, c, "L1=", count_fast(r,c))
    print("PASS self-test")
