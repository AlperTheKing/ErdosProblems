"""H5 (round 4), part (b): QUADRATIC-MULTIPLIER CERTIFICATE (QMC) for max_x psi(H,x) <= 1/25.

CERTIFICATE SCHEME  (mine; designed so that the whole thing is one small SDP whose solution
can be rounded to rationals and verified with exact arithmetic).

Let H be a graph on n vertices, let S range over a family of cuts of H and let
q_S(z) = sum_{uv monochromatic in S} z_u z_v.   Suppose we can produce quadratic forms
lambda_S(z) and a quartic form Q(z) with

    (K2)  lambda_S(y^2)  is SOS in y                       (equivalently lambda_S >= 0 on z >= 0)
    (SUM) sum_S lambda_S(z) = (sum_j z_j)^2               (exact identity of quadratic forms)
    (K4)  Q(z) := (sum_j z_j)^4 - 25 * sum_S lambda_S(z) q_S(z)   has  Q(y^2) SOS in y.

Then max_x psi(H,x) <= 1/25.
PROOF.  Let x be in the simplex and t = psi(H,x) = min_S q_S(x) >= 0.  Put y_j = sqrt(x_j).
(K4) gives Q(x) >= 0, i.e. 1 = (sum x)^4 >= 25 sum_S lambda_S(x) q_S(x).  By (K2) every
lambda_S(x) >= 0 and q_S(x) >= t, so sum_S lambda_S(x) q_S(x) >= t sum_S lambda_S(x) = t (sum x)^2 = t
by (SUM).  Hence 1 >= 25 t.  []

Note this is exactly a certificate that READS THE WEIGHTS (accepted fact R3-C7): lambda_S(x)/1 is a
probability distribution on the cuts that depends on x.  With lambda_S CONSTANT the scheme collapses
to the averaging bound and can only reach 1/20 -- so the quadratic case is the first live one.

Membership in the two cones is exactly a block-diagonal SDP because everything is even in y:
  * quadratic in z, SOS in y  <=>  z^T M z + sum_{j<k} c_jk z_j z_k with M PSD (nxn) and c >= 0;
  * quartic  in z, SOS in y   <=>  Gram matrix on the C(n+3,4) degree-4 y-monomials, block diagonal
    by parity class alpha mod 2:  one block on {y^{2beta} : |beta| = 2} of size C(n+1,2), one block
    of size n for every pair {j,k} on {y_j y_k y_l^2 : l}, and one 1x1 block for every 4-subset.

Usage: python H5_cert.py [graph] [--cuts all|rot] [--nosym]
"""
import sys
import itertools
import numpy as np
import cvxpy as cp


# ------------------------------------------------------------------ monomial helpers
def mons_deg(n, d):
    """exponent tuples in n variables of total degree exactly d, sorted"""
    out = []
    for c in itertools.combinations_with_replacement(range(n), d):
        a = [0] * n
        for i in c:
            a[i] += 1
        out.append(tuple(a))
    return sorted(set(out))


def eadd(*aa):
    n = len(aa[0])
    return tuple(sum(a[i] for a in aa) for i in range(n))


def unit(n, j, k=None):
    a = [0] * n
    a[j] += 1
    if k is not None:
        a[k] += 1
    return tuple(a)


# ------------------------------------------------------------------ graphs / cuts
def graph(name):
    if name == 'C5':
        return 5, [(i, (i + 1) % 5) for i in range(5)]
    if name == 'C7':
        return 7, [(i, (i + 1) % 7) for i in range(7)]
    if name == 'wagner':
        E = set()
        for v in range(8):
            for w in ((v + 1) % 8, (v + 4) % 8):
                E.add((min(v, w), max(v, w)))
        return 8, sorted(E)
    raise SystemExit('unknown graph ' + name)


def cuts_of(n, E, mode):
    if mode == 'rot':
        assert n == 5
        return [((( (i + 3) % 5, (i + 4) % 5) if (i + 3) % 5 < (i + 4) % 5
                  else ((i + 4) % 5, (i + 3) % 5)),) for i in range(5)]
    out = set()
    for m in range(1 << (n - 1)):
        side = [0] + [(m >> i) & 1 for i in range(n - 1)]
        out.add(tuple((u, v) for (u, v) in E if side[u] == side[v]))
    return sorted(out)


# ------------------------------------------------------------------ K4 cone bookkeeping
def k4_blocks(n):
    """Return (blocks, contrib) describing the cone {quartic Q(z) : Q(y^2) SOS in y}.

    blocks : list of (label, size, rowlabels)
    contrib: list of (blockindex, i, j, z-monomial) meaning G_b[i,j] adds to that z-monomial.
    """
    blocks, contrib = [], []
    # parity class 0 : monomials y^{2beta}, |beta| = 2
    B0 = mons_deg(n, 2)
    blocks.append(('even', len(B0), B0))
    for i, b in enumerate(B0):
        for j, b2 in enumerate(B0):
            contrib.append((0, i, j, eadd(b, b2)))
    # parity class {j,k}: monomials y_j y_k y_l^2, l = 0..n-1
    for (j, k) in itertools.combinations(range(n), 2):
        bi = len(blocks)
        blocks.append((('pair', j, k), n, list(range(n))))
        for l in range(n):
            for l2 in range(n):
                contrib.append((bi, l, l2, eadd(unit(n, j, k), unit(n, l, l2))))
    # parity class {j,k,l,m}: single monomial y_j y_k y_l y_m
    for q in itertools.combinations(range(n), 4):
        bi = len(blocks)
        blocks.append((('quad',) + q, 1, [0]))
        mu = [0] * n
        for v in q:
            mu[v] += 1
        contrib.append((bi, 0, 0, tuple(mu)))
    return blocks, contrib


# ------------------------------------------------------------------ main SDP
def build_and_solve(name='C5', cutmode='rot', facial=True, solver=cp.CLARABEL, verbose=False):
    n, E = graph(name)
    cuts = cuts_of(n, E, cutmode)
    nc = len(cuts)
    D2 = mons_deg(n, 2)
    D4 = mons_deg(n, 4)
    i4 = {m: i for i, m in enumerate(D4)}
    print(f"[H5-cert] {name}: n={n} |E|={len(E)} cuts={nc} "
          f"deg2 z-monomials={len(D2)} deg4 z-monomials={len(D4)}")

    # --- lambda_S = z^T M_S z + sum_{j<k} c^S_{jk} z_j z_k
    M = [cp.Variable((n, n), symmetric=True) for _ in range(nc)]
    C = [cp.Variable((n, n), symmetric=True) for _ in range(nc)]
    cons = [Ms >> 0 for Ms in M]
    for Cs in C:
        cons += [Cs >= 0, cp.diag(Cs) == 0]

    def lam_coeff(s, mu):
        """coefficient of the degree-2 z-monomial mu in lambda_s"""
        supp = [j for j in range(n) if mu[j] > 0]
        if len(supp) == 1:
            j = supp[0]
            return M[s][j, j]
        j, k = supp
        return 2 * M[s][j, k] + C[s][j, k]

    # --- (SUM) sum_S lambda_S = (sum z)^2
    for mu in D2:
        tgt = 1.0 if max(mu) == 2 else 2.0
        cons.append(sum(lam_coeff(s, mu) for s in range(nc)) == tgt)

    # --- Q = (sum z)^4 - 25 sum_S lambda_S q_S      (coefficients as affine expressions)
    def multinom(mu):
        from math import factorial
        r = factorial(sum(mu))
        for e in mu:
            r //= factorial(e)
        return r

    Qc = [None] * len(D4)
    for i, mu in enumerate(D4):
        Qc[i] = float(multinom(mu))                       # coefficient in (sum z)^4
    for s, mono in enumerate(cuts):
        for mu2 in D2:
            for (u, v) in mono:
                mu = eadd(mu2, unit(n, u, v))
                Qc[i4[mu]] = Qc[i4[mu]] - 25 * lam_coeff(s, mu2)

    # --- (K4) Gram blocks
    blocks, contrib = k4_blocks(n)
    G = []
    Hred = []
    mu_marg = cp.Variable()
    for (lab, sz, _) in blocks:
        if facial and lab != 'even' and isinstance(lab, tuple) and lab[0] == 'quad':
            G.append(None)                                # forced zero
            continue
        if facial:
            # kernel: all-ones vector of that block (evaluation of Q(y^2) at y = (1,...,1))
            U = null_basis_ones(sz)
            r = U.shape[1]
            Hv = cp.Variable((r, r), symmetric=True)
            Hred.append((Hv, r))
            cons.append(Hv - mu_marg * np.eye(r) >> 0)
            G.append(U @ Hv @ U.T)
        else:
            Gv = cp.Variable((sz, sz), symmetric=True)
            cons.append(Gv >> 0)
            G.append(Gv)

    expr = [0.0] * len(D4)
    for (bi, i, j, mu) in contrib:
        if G[bi] is None:
            continue
        expr[i4[mu]] = expr[i4[mu]] + G[bi][i, j]
    for i in range(len(D4)):
        cons.append(expr[i] == Qc[i])

    prob = cp.Problem(cp.Maximize(mu_marg if facial else cp.Constant(0)), cons)
    prob.solve(solver=solver, verbose=verbose)
    print(f"    status={prob.status}  margin={prob.value}")
    return dict(prob=prob, n=n, cuts=cuts, M=M, C=C, G=G, blocks=blocks, D2=D2, D4=D4,
                margin=(mu_marg.value if facial else None))


def null_basis_ones(sz):
    """orthonormal-ish integer basis of the orthogonal complement of the all-ones vector"""
    if sz == 1:
        return np.zeros((1, 0))
    U = np.zeros((sz, sz - 1))
    for i in range(sz - 1):
        U[i, i] = 1.0
        U[sz - 1, i] = -1.0
    return U


if __name__ == '__main__':
    name = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-') else 'C5'
    cutmode = 'rot'
    for i, a in enumerate(sys.argv):
        if a == '--cuts':
            cutmode = sys.argv[i + 1]
    out = build_and_solve(name, cutmode)
    if out['prob'].status in ('optimal', 'optimal_inaccurate'):
        n = out['n']
        np.set_printoptions(precision=5, suppress=True, linewidth=200)
        for s in range(len(out['cuts'])):
            print(f"  cut {s} mono-edges {out['cuts'][s]}")
            print("   M =", out['M'][s].value.round(5).tolist())
            print("   C =", out['C'][s].value.round(5).tolist())
