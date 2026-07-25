#!/usr/bin/env python3
"""LEMMA S test.

Derivation (exact, verified below).  Let rho_d be the Irwin-Hall reference
measure: the law of u = V_1 + ... + V_{d+1} with V_i iid Uniform[-1,1].
Its "Ehrhart transform" is the pure monomial:  E_rho[ Q_d(t - u/2) ] = t^d,
where Q_d(t) = prod_{m=1}^{d} (t + m - (d+1)/2)  (so d!*C(t+d-j,d) =
Q_d(t - u_j/2) with u_j = 2j-(d+1)).

Hence, writing the normalised h*-measure p as p = rho_d * nu (deconvolution
at the level of the first d+1 moments -- always possible and unique),

        a_k  =  (M/d!) * C(d,k) * beta_{d-k},     beta_m := E_nu[(-v)^m],

so KTT positivity for Q  <=>  beta_m >= 0 for m = 0..d, and

  LEMMA S :  (beta_0, ..., beta_d) is a truncated STIELTJES moment sequence,
             i.e. there is a probability measure on [0, infinity) with these
             moments.  Equivalently P(t) = (M/d!) * E[(t + w/2)^d], w >= 0.

Lemma S implies KTT.  It is dilation-invariant (beta_m -> beta_m / t^m).
It is exactly decidable: Hankel matrices H0 = (beta_{i+j}) and
H1 = (beta_{i+j+1}) must both be positive semidefinite.
"""
from fractions import Fraction as F
from math import comb, factorial
from crit import coeffs_from_hstar


def betas(h):
    """beta_m for m = 0..d, exact."""
    d = len(h) - 1
    a = coeffs_from_hstar(list(h))
    M = sum(h)
    return [F(factorial(d), 1) * a[d - m] / (M * comb(d, m)) for m in range(d + 1)]


def psd(mat):
    """Exact PSD test for a symmetric rational matrix (LDL with pivoting on
    zero rows).  Returns True iff PSD."""
    n = len(mat)
    A = [row[:] for row in mat]
    idx = list(range(n))
    for i in range(n):
        if A[i][i] < 0:
            return False
        if A[i][i] == 0:
            # whole row/col must vanish
            if any(A[i][j] != 0 for j in range(n)):
                return False
            continue
        for j in range(i + 1, n):
            if A[j][i] == 0:
                continue
            f = A[j][i] / A[i][i]
            for k in range(i, n):
                A[j][k] -= f * A[i][k]
            for k in range(i, n):
                A[k][j] = A[j][k] if k >= j else A[k][j]
        # resymmetrise the trailing block
        for j in range(i + 1, n):
            for k in range(i + 1, n):
                pass
    # simpler & safe: check all leading principal minors of all symmetric
    # permutations is expensive; use eigen-free Cholesky-with-tolerance on
    # the ORIGINAL matrix via sympy
    import sympy as sp
    Msym = sp.Matrix(len(mat), len(mat), lambda i, j: sp.Rational(mat[i][j]))
    return all(x >= 0 for x in Msym.eigenvals(multiple=True))


def stieltjes_ok(b):
    d = len(b) - 1
    n0 = d // 2
    H0 = [[b[i + j] for j in range(n0 + 1)] for i in range(n0 + 1)]
    n1 = (d - 1) // 2
    H1 = [[b[i + j + 1] for j in range(n1 + 1)] for i in range(n1 + 1)]
    return psd(H0), psd(H1)


if __name__ == "__main__":
    import csv, collections, sys
    # ---- verification of the reference identity E_rho[Q_d(t-u/2)] = t^d ----
    import sympy as sp
    t, z = sp.symbols('t z')
    for d in range(1, 9):
        Q = sp.prod([t + m - sp.Rational(d + 1, 2) for m in range(1, d + 1)])
        # E_rho[Q(t-u/2)] = S(D) Q(t) with S(z) = (2 sinh(z/2)/z)^{d+1}
        S = sp.series((2 * sp.sinh(z / 2) / z) ** (d + 1), z, 0, d + 2).removeO()
        acc = 0
        Qe = sp.expand(Q)
        for m in range(d + 1):
            acc += S.coeff(z, m) * sp.diff(Qe, t, m)
        assert sp.expand(acc - t ** d) == 0, (d, sp.expand(acc))
    print("reference identity  E_rho[Q_d(t-u/2)] = t^d  VERIFIED for d<=8")

    # ---- sanity: beta for the unimodular simplex and for Reeve ----
    print("simplex d=3  h*=(1,0,0,0)  beta =", betas([1, 0, 0, 0]),
          " stieltjes:", stieltjes_ok(betas([1, 0, 0, 0])))
    for q in (6, 10, 13):
        b = betas([1, 0, q - 1, 0])
        print("Reeve q=%2d  beta = %s  stieltjes: %s" % (q, b, stieltjes_ok(b)))

    rows = []
    for r in csv.DictReader(open('hstar_atlas2.tsv'), delimiter='\t'):
        h = tuple(int(x) for x in r['hstar'].split(','))
        rows.append((int(r['d']), int(r['M']), h, r['lam'], r['mu'], r['nu']))
    okc = collections.Counter()
    fails = []
    for d, M, h, lam, mu, nu in rows:
        b = betas(list(h))
        s0, s1 = stieltjes_ok(b)
        okc[(s0, s1)] += 1
        if not (s0 and s1):
            fails.append((d, h, s0, s1, lam, mu, nu))
    print("Hankel verdicts (H0 psd, H1 psd):", dict(okc), "of", len(rows))
    for f in fails[:10]:
        print("   FAIL d=%d h*=%s H0=%s H1=%s (%s|%s|%s)" % f)
