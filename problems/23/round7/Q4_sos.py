"""Q4: multiplier-Positivstellensatz SDP for  max_x psi(H,x) <= 1/c.

Scheme at multiplier degree 2d  (nu_S = c*lambda_S already substituted, so everything is LINEAR):

    nu_S(x) >= 0 on the orthant                            (mode 'coef': nonneg coefficients;
                                                            mode 'sosy': nu_S(y^2) is SOS in y)
    sum_S nu_S = c * L^{2d}                                 L = x_0+...+x_{n-1}
    T(x) := L^{2d+2} - sum_S nu_S q_S   has T(y^2) SOS in y (parity-blocked PSD Gram)

  ==>  max_x psi(H,x) <= 1/c.     Maximise c.  (c = 25 is the target and is a hard ceiling
  whenever H has an induced C5, so the SDP optimum satisfies c* <= 25.)

The SOS condition is imposed after the substitution x_i = y_i^2, i.e. nonnegativity is only
required on the orthant, which is all the scheme needs.  T(y^2) uses only even exponents, so the
Gram matrix splits into blocks indexed by the parity class of the exponent vector.
"""
from itertools import combinations
from math import factorial
import numpy as np
import scipy.sparse as sp
import cvxpy as cp


def monomials(n, deg):
    """All exponent tuples of length n with given total degree, in a fixed order."""
    out = []

    def rec(i, rem, cur):
        if i == n - 1:
            out.append(tuple(cur + [rem]))
            return
        for v in range(rem + 1):
            rec(i + 1, rem - v, cur + [v])
    rec(0, deg, [])
    return out


def multinom(alpha):
    r = factorial(sum(alpha))
    for a in alpha:
        r //= factorial(a)
    return r


def parity_blocks(n, deg):
    """Group degree-`deg` exponent vectors by parity class.  Returns list of lists of exponent tuples."""
    groups = {}
    for b in monomials(n, deg):
        groups.setdefault(tuple(x % 2 for x in b), []).append(b)
    return [groups[k] for k in sorted(groups)]


def build(n, E, cuts, d, c_fixed=None, mode='coef', verbose=True):
    """cuts: list of (mask, frozenset of monochromatic edge indices).  Returns dict with the problem."""
    D = 2 * d              # multiplier degree
    DT = 2 * d + 2         # target degree
    monsD = monomials(n, D)
    idxD = {m: i for i, m in enumerate(monsD)}
    monsT = monomials(n, DT)
    idxT = {m: i for i, m in enumerate(monsT)}
    nC, nD, nT = len(cuts), len(monsD), len(monsT)

    # ---- multiplier variables -------------------------------------------------
    nu_vars = []           # cvxpy variables
    nu_cols = []           # list of (sparse map from var-vector to nu coefficient vector per cut)
    if mode == 'coef':
        NU = cp.Variable((nC, nD), nonneg=True)
        nu_expr = NU                                    # nu_expr[S, m]
        blocks_mult = []
    elif mode == 'sosy':
        # nu_S(y^2) SOS: Gram over y-monomials of degree D, parity-blocked
        pb = parity_blocks(n, D)
        blocks_mult = []
        rows, cols, vals = [], [], []
        exprs = []
        for S in range(nC):
            per_cut = []
            for B in pb:
                k = len(B)
                Q = cp.Variable((k, k), PSD=True) if k > 1 else cp.Variable((1, 1), nonneg=True)
                per_cut.append((Q, B))
            blocks_mult.append(per_cut)
        # nu coefficient of x^m  =  sum over pairs with (beta+gamma)/2 = m
        rows_list = []
        for S in range(nC):
            terms = []
            for Q, B in blocks_mult[S]:
                k = len(B)
                M = np.zeros((nD, k * k))
                for i in range(k):
                    for j in range(k):
                        m = tuple((B[i][t] + B[j][t]) // 2 for t in range(n))
                        M[idxD[m], i * k + j] = 1.0
                terms.append(sp.csr_matrix(M) @ cp.vec(Q, order='C'))
            rows_list.append(sum(terms))
        nu_expr = cp.vstack(rows_list)
    else:
        raise ValueError(mode)

    # ---- target Gram (parity blocks over degree-DT y-monomials) ---------------
    pbT = parity_blocks(n, DT)
    Qblocks = []
    for B in pbT:
        k = len(B)
        Qblocks.append((cp.Variable((k, k), PSD=True) if k > 1 else cp.Variable((1, 1), nonneg=True), B))

    # ---- linear system --------------------------------------------------------
    # (1) normalisation  sum_S nu_S[m] = c * multinom(m)
    c = cp.Variable() if c_fixed is None else c_fixed
    cons = []
    mult_D = np.array([multinom(m) for m in monsD], dtype=float)
    cons.append(cp.sum(nu_expr, axis=0) == c * mult_D)

    # (2) coefficient identity for T
    # A_nu : nT x (nC*nD)   with  sum_S sum_{(u,v) mono(S)} nu_S[alpha - e_u - e_v]
    rows, cols, vals = [], [], []
    for S, (_mask, mono) in enumerate(cuts):
        for k in mono:
            u, v = E[k]
            for a_i, alpha in enumerate(monsT):
                if alpha[u] >= 1 and alpha[v] >= 1:
                    b = list(alpha)
                    b[u] -= 1
                    b[v] -= 1
                    rows.append(a_i)
                    cols.append(S * nD + idxD[tuple(b)])
                    vals.append(1.0)
    A_nu = sp.csr_matrix((vals, (rows, cols)), shape=(nT, nC * nD))

    gram_terms = []
    for Q, B in Qblocks:
        k = len(B)
        rows, cols, vals = [], [], []
        for i in range(k):
            for j in range(k):
                alpha = tuple((B[i][t] + B[j][t]) // 2 for t in range(n))
                rows.append(idxT[alpha])
                cols.append(i * k + j)
                vals.append(1.0)
        M = sp.csr_matrix((vals, (rows, cols)), shape=(nT, k * k))
        gram_terms.append(M @ cp.vec(Q, order='C'))

    b_T = np.array([multinom(a) for a in monsT], dtype=float)
    cons.append(A_nu @ cp.vec(nu_expr, order='C') + sum(gram_terms) == b_T)

    if verbose:
        sizes = [len(B) for _, B in Qblocks]
        from collections import Counter
        print(f"   target Gram blocks: {Counter(sizes)}  (total dim {sum(sizes)})")
        print(f"   cuts={nC}  multiplier monomials={nD}  target monomials={nT}  mode={mode}")
    obj = cp.Maximize(c) if c_fixed is None else cp.Maximize(0)
    return dict(prob=cp.Problem(obj, cons), c=c, nu=nu_expr, Q=Qblocks,
                monsD=monsD, monsT=monsT, A_nu=A_nu, cuts=cuts, n=n, E=E, d=d,
                blocks_mult=blocks_mult, mode=mode)
