"""Q4: the DUAL of the multiplier-Positivstellensatz scheme.

Elementary weak duality (proved inline, no duality theory needed).  Let z = (z_alpha) be indexed
by the degree-(2d+2) exponent vectors, and for a cut S and a degree-2d monomial m put
        zhat_S(m) = sum_{(u,v) in mono(S)} z_{m+e_u+e_v} .
Suppose every parity block Z_b = [ z_{(beta+gamma)/2} ]_{beta,gamma in b} is PSD.  Then for ANY
primal-feasible (c, nu, Q):

  sum_alpha muT(alpha) z_alpha  =  sum_S sum_m nu_{S,m} zhat_S(m) + sum_b <Z_b, Q_b>
                                >= sum_m (sum_S nu_{S,m}) * min_S zhat_S(m)
                                 = c * sum_m muD(m) * min_S zhat_S(m).

So    c  <=  num(z)/den(z),   num = sum_alpha muT(alpha) z_alpha,
                              den = sum_m muD(m) min_S zhat_S(m)   (whenever den > 0).

Every z_alpha is a diagonal entry of some Z_b, so PSD forces z >= 0 entrywise; hence dominated
cuts never attain the min and the reduction to inclusion-minimal cuts is exact on both sides.

This module (a) solves the dual SDP directly (cheaper than the primal: 2046 free variables),
(b) turns a numerical z into an EXACT rational certificate  c* <= num/den  by mixing with the
strictly-positive-definite moment vector z_int(alpha) = prod_i alpha_i!  (the moments of
e^{-sum x} dx on the orthant, whose parity blocks are PD), and verifying PSD by exact LDL^T.
"""
from fractions import Fraction
from math import factorial
import numpy as np
import scipy.sparse as sp
import cvxpy as cp
from Q4_sos import monomials, multinom, parity_blocks
from Q4_verify import exact_psd


def dual_problem(n, E, cuts, d):
    D, DT = 2 * d, 2 * d + 2
    monsD, monsT = monomials(n, D), monomials(n, DT)
    idxT = {a: i for i, a in enumerate(monsT)}
    nD, nT = len(monsD), len(monsT)
    z = cp.Variable(nT)
    w = cp.Variable(nD)
    cons = []
    pbT = parity_blocks(n, DT)
    for B in pbT:
        k = len(B)
        rows, cols, vals = [], [], []
        for i in range(k):
            for j in range(k):
                a = tuple((B[i][t] + B[j][t]) // 2 for t in range(n))
                rows.append(i * k + j)
                cols.append(idxT[a])
                vals.append(1.0)
        M = sp.csr_matrix((vals, (rows, cols)), shape=(k * k, nT))
        if k == 1:
            cons.append(M @ z >= 0)
        else:
            cons.append(cp.reshape(M @ z, (k, k), order='C') >> 0)
    # w_m <= zhat_S(m) for every cut S
    for S, (_mask, mono) in enumerate(cuts):
        rows, cols, vals = [], [], []
        for mi, m in enumerate(monsD):
            for k_ in mono:
                u, v = E[k_]
                a = list(m)
                a[u] += 1
                a[v] += 1
                rows.append(mi)
                cols.append(idxT[tuple(a)])
                vals.append(1.0)
        A = sp.csr_matrix((vals, (rows, cols)), shape=(nD, nT))
        cons.append(w <= A @ z)
    muD = np.array([multinom(m) for m in monsD], float)
    muT = np.array([multinom(a) for a in monsT], float)
    cons.append(muD @ w == 1)
    prob = cp.Problem(cp.Minimize(muT @ z), cons)
    return prob, z, w, monsD, monsT


def ratio_exact(n, E, cuts, d, zq):
    """Exact rational num/den for a rational z (dict alpha -> Fraction).  Returns (num, den, ratio)."""
    D, DT = 2 * d, 2 * d + 2
    monsD, monsT = monomials(n, D), monomials(n, DT)
    num = sum(Fraction(multinom(a)) * zq[a] for a in monsT)
    den = Fraction(0)
    for m in monsD:
        best = None
        for _mask, mono in cuts:
            s = Fraction(0)
            for k_ in mono:
                u, v = E[k_]
                a = list(m)
                a[u] += 1
                a[v] += 1
                s += zq[tuple(a)]
            if best is None or s < best:
                best = s
        den += Fraction(multinom(m)) * best
    return num, den, (num / den if den != 0 else None)


def psd_blocks_exact(n, d, zq):
    """Exact PSD check of every parity block of the moment matrix built from rational z."""
    DT = 2 * d + 2
    for B in parity_blocks(n, DT):
        k = len(B)
        M = [[zq[tuple((B[i][t] + B[j][t]) // 2 for t in range(n))] for j in range(k)] for i in range(k)]
        ok, info = exact_psd(M)
        if not ok:
            return False, f"block parity {tuple(x%2 for x in B[0])} size {k}: {info}"
    return True, "all blocks PSD"


def z_interior(n, d):
    """z_int(alpha) = prod alpha_i!  -- moments of exp(-sum x) on the orthant; blocks are PD."""
    return {a: Fraction(int(np.prod([factorial(t) for t in a]))) for a in monomials(n, 2 * d + 2)}


def exact_certificate(n, E, cuts, d, z_num, monsT, denom=10**6, t_list=None, verbose=True):
    """Round a numerical dual z, mix with the interior point until exactly PSD, report num/den."""
    zi = z_interior(n, d)
    scale = max(abs(float(v)) for v in z_num) or 1.0
    zr = {a: Fraction(int(round(z_num[i] / scale * denom)), denom) for i, a in enumerate(monsT)}
    si = max(abs(float(v)) for v in zi.values())
    if t_list is None:
        t_list = [Fraction(0), Fraction(1, 10**6), Fraction(1, 10**5), Fraction(1, 10**4),
                  Fraction(1, 10**3), Fraction(1, 100), Fraction(1, 10), Fraction(1)]
    best = None
    for t in t_list:
        zq = {a: zr[a] + t * zi[a] / si for a in monsT}
        ok, info = psd_blocks_exact(n, d, zq)
        if verbose:
            print(f"   t={t}: PSD={ok} ({info if not ok else ''})", flush=True)
        if not ok:
            continue
        num, den, r = ratio_exact(n, E, cuts, d, zq)
        if verbose:
            print(f"      num/den = {r} = {float(r):.10f}", flush=True)
        if den > 0 and (best is None or r < best[2]):
            best = (num, den, r, t, zq)
        break
    return best
