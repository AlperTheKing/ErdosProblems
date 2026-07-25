"""H5 round 4, part (b): EXACT RATIONAL certificate that max_x psi(C5,x) <= 1/25.

Certificate scheme (QMC, see H5_cert.py):
    lambda_e(z) for e in E(C5), quadratic forms with NONNEGATIVE coefficients,
    sum_e lambda_e(z) = (sum_j z_j)^2,
    Q(z) := (sum_j z_j)^4 - 25 * sum_{e=(u,v)} lambda_e(z) z_u z_v  is SOS after z = y^2.

Everything below is exact (fractions.Fraction).  The only floating point is the search for a
starting Gram matrix; the accepted object is corrected onto the affine constraints exactly and
its positive semidefiniteness is verified by a rational LDL^T (and independently by sympy).

Usage: python H5_exact.py [--den D]
"""
import sys
import itertools
from fractions import Fraction as F
import numpy as np
import cvxpy as cp

N = 5
EDGES = [(i, (i + 1) % N) for i in range(N)]

# ---- reflection-invariant 9 parameters of lambda_{(i,i+1)}; roles a=i b=i+1 p=i+2 q=i+3 r=i+4
#      constraints: 2c1+2c2+c3 = 1,  c4+2c7+2c8 = 2,  2c5+2c6+c9 = 2
PARAMS = dict(c1=F(1, 10), c2=F(1, 5), c3=F(2, 5),
              c4=F(1, 4), c7=F(1, 4), c8=F(5, 8),
              c5=F(7, 20), c6=F(1, 2), c9=F(3, 10))


def check_params(c):
    assert 2 * c['c1'] + 2 * c['c2'] + c['c3'] == 1, "diagonal constraint"
    assert c['c4'] + 2 * c['c7'] + 2 * c['c8'] == 2, "distance-1 constraint"
    assert 2 * c['c5'] + 2 * c['c6'] + c['c9'] == 2, "distance-2 constraint"
    assert all(v >= 0 for v in c.values()), "nonnegative coefficients"


def lam_matrices(c):
    """L[i] = symmetric rational matrix with lambda_{(i,i+1)}(z) = z^T L[i] z."""
    out = []
    for i in range(N):
        a, b, p, q, r = [(i + k) % N for k in range(5)]
        Lm = [[F(0)] * N for _ in range(N)]

        def put(u, v, val):
            Lm[u][v] += val
            if u != v:
                Lm[v][u] += val
        put(a, a, c['c1']); put(b, b, c['c1'])
        put(p, p, c['c2']); put(r, r, c['c2'])
        put(q, q, c['c3'])
        put(a, b, c['c4'] / 2)
        put(a, p, c['c5'] / 2); put(b, r, c['c5'] / 2)
        put(a, q, c['c6'] / 2); put(b, q, c['c6'] / 2)
        put(a, r, c['c7'] / 2); put(b, p, c['c7'] / 2)
        put(p, q, c['c8'] / 2); put(q, r, c['c8'] / 2)
        put(p, r, c['c9'] / 2)
        out.append(Lm)
    return out


# ---------------------------------------------------------------- polynomial bookkeeping
def mons_deg(n, d):
    out = set()
    for cmb in itertools.combinations_with_replacement(range(n), d):
        a = [0] * n
        for i in cmb:
            a[i] += 1
        out.add(tuple(a))
    return sorted(out)


def eadd(*aa):
    return tuple(sum(a[i] for a in aa) for i in range(len(aa[0])))


def unit(n, j, k=None):
    a = [0] * n
    a[j] += 1
    if k is not None:
        a[k] += 1
    return tuple(a)


D2 = mons_deg(N, 2)
D4 = mons_deg(N, 4)
I4 = {m: i for i, m in enumerate(D4)}


def multinom(mu):
    from math import factorial
    r = factorial(sum(mu))
    for e in mu:
        r //= factorial(e)
    return r


def build_Q(L):
    """Q = (sum z)^4 - 25 sum_e lambda_e(z) z_u z_v, exactly."""
    Q = {mu: F(multinom(mu)) for mu in D4}
    for i, (u, v) in enumerate(EDGES):
        for j in range(N):
            for k in range(N):
                if L[i][j][k] == 0:
                    continue
                mu = eadd(unit(N, j, k), unit(N, u, v))
                Q[mu] -= 25 * L[i][j][k]
    return Q


# ---------------------------------------------------------------- the K4 (SOS-in-y) blocks
def k4_blocks(n):
    blocks = []
    B0 = mons_deg(n, 2)
    blocks.append(('even', B0))
    for (j, k) in itertools.combinations(range(n), 2):
        blocks.append((('pair', j, k), list(range(n))))
    for q in itertools.combinations(range(n), 4):
        blocks.append((('quad',) + q, [0]))
    return blocks


def block_monomial(lab, rows, i, j, n):
    """z-monomial receiving G_block[i,j]"""
    if lab == 'even':
        return eadd(rows[i], rows[j])
    if lab[0] == 'pair':
        _, a, b = lab
        return eadd(unit(n, a, b), unit(n, rows[i], rows[j]))
    q = lab[1:]
    mu = [0] * n
    for v in q:
        mu[v] += 1
    return tuple(mu)


BLOCKS = k4_blocks(N)
# facial reduction: Q(1,...,1)=0 forces G*1 = 0 in every block; the 1x1 'quad' blocks vanish.
ACTIVE = [(bi, lab, rows) for bi, (lab, rows) in enumerate(BLOCKS)
          if not (isinstance(lab, tuple) and lab[0] == 'quad')]


def Ubasis(sz):
    """integer basis of 1^perp:  columns e_i - e_last"""
    U = np.zeros((sz, sz - 1))
    for i in range(sz - 1):
        U[i, i] = 1.0
        U[sz - 1, i] = -1.0
    return U


def numeric_gram(Q, verbose=False):
    """maximise the smallest eigenvalue of the reduced Gram blocks subject to matching Q"""
    Hs, cons, expr = [], [], {mu: 0.0 for mu in D4}
    mu_marg = cp.Variable()
    for (bi, lab, rows) in ACTIVE:
        sz = len(rows)
        U = Ubasis(sz)
        r = U.shape[1]
        Hv = cp.Variable((r, r), symmetric=True)
        cons.append(Hv - mu_marg * np.eye(r) >> 0)
        Hs.append((bi, lab, rows, U, Hv))
        G = U @ Hv @ U.T
        for i in range(sz):
            for j in range(sz):
                expr[block_monomial(lab, rows, i, j, N)] = \
                    expr[block_monomial(lab, rows, i, j, N)] + G[i, j]
    for mu in D4:
        cons.append(expr[mu] == float(Q[mu]))
    cons.append(mu_marg <= 10)              # CLARABEL chokes without an explicit cap
    prob = cp.Problem(cp.Maximize(mu_marg), cons)
    for s in (cp.SCS, cp.CLARABEL):
        try:
            prob.solve(solver=s, verbose=verbose,
                       **({'max_iters': 200000, 'eps': 1e-11} if s is cp.SCS else {}))
            if prob.status in ('optimal', 'optimal_inaccurate'):
                print(f"    [gram] solver {s} margin {mu_marg.value}")
                break
        except Exception as ex:
            print(f"    [gram] solver {s} failed: {ex}")
    return prob, Hs, mu_marg.value


# ---------------------------------------------------------------- exact linear algebra
def rat_ldl(M):
    """exact LDL^T of a symmetric rational matrix without pivoting.
    returns (ok, pivots).  ok = True iff every pivot is > 0 (i.e. M is positive definite)."""
    n = len(M)
    A = [row[:] for row in M]
    piv = []
    for k in range(n):
        d = A[k][k]
        piv.append(d)
        if d <= 0:
            return False, piv
        for i in range(k + 1, n):
            f = A[i][k] / d
            if f == 0:
                continue
            for j in range(k, n):
                A[i][j] -= f * A[k][j]
            for j in range(k, n):
                A[j][i] = A[i][j]
    return True, piv


def solve_exact(Amat, rhs, pivots):
    """solve Amat[:, pivots] * d = rhs exactly (Amat rational, len(pivots) == len(rhs))."""
    m = len(rhs)
    A = [[Amat[i][p] for p in pivots] + [rhs[i]] for i in range(m)]
    row = 0
    where = []
    for col in range(m):
        sel = None
        for i in range(row, m):
            if A[i][col] != 0:
                sel = i
                break
        if sel is None:
            raise RuntimeError('singular pivot set at column %d' % col)
        A[row], A[sel] = A[sel], A[row]
        inv = A[row][col]
        A[row] = [x / inv for x in A[row]]
        for i in range(m):
            if i != row and A[i][col] != 0:
                f = A[i][col]
                A[i] = [a - f * b for a, b in zip(A[i], A[row])]
        where.append(col)
        row += 1
    return [A[i][m] for i in range(m)]


def main():
    den = 10 ** 7
    for i, a in enumerate(sys.argv):
        if a == '--den':
            den = int(sys.argv[i + 1])
    c = PARAMS
    check_params(c)
    L = lam_matrices(c)

    # (SUM) sum_e lambda_e = (sum z)^2  <=>  sum_e L_e = all-ones
    tot = [[sum(L[e][i][j] for e in range(N)) for j in range(N)] for i in range(N)]
    assert all(tot[i][j] == 1 for i in range(N) for j in range(N)), tot
    assert all(L[e][i][j] >= 0 for e in range(N) for i in range(N) for j in range(N)), \
        "lambda has a negative coefficient -> K2 membership not automatic"
    print("[exact] lambda family OK: sum = (sum z)^2, all coefficients >= 0")
    print("        lambda_{(0,1)} matrix rows:")
    for row in L[0]:
        print("          ", [str(x) for x in row])

    Q = build_Q(L)
    print(f"[exact] Q has {sum(1 for v in Q.values() if v != 0)} nonzero coefficients "
          f"out of {len(D4)};  Q(1,...,1) = {sum(Q.values())}")
    assert sum(Q.values()) == 0, "Q(1,..,1) must vanish"

    prob, Hs, marg = numeric_gram(Q)
    print(f"[numeric] SOS feasibility for this fixed lambda: status={prob.status} "
          f"margin(min eig of reduced blocks)={marg}")
    if prob.status not in ('optimal', 'optimal_inaccurate') or marg is None or marg <= 0:
        print("FAILED: no strictly feasible reduced Gram for these lambda parameters")
        return

    # ---- round the reduced Gram blocks to rationals
    Hrat = []
    for (bi, lab, rows, U, Hv) in Hs:
        V = np.array(Hv.value)
        V = (V + V.T) / 2
        r = V.shape[0]
        Hrat.append([[F(int(round(V[i][j] * den)), den) for j in range(r)] for i in range(r)])

    # ---- coefficient map in reduced coordinates:  coeff[mu] = sum_b <A_b[mu], H_b>
    varlist = []          # (blockpos, i, j) with i<=j  -> coefficient vector over D4
    Acols = []
    for bpos, (bi, lab, rows, U, Hv) in enumerate(Hs):
        sz = len(rows)
        r = U.shape[1]
        for i in range(r):
            for j in range(i, r):
                vec = {}
                for a in range(sz):
                    for b in range(sz):
                        w = U[a][i] * U[b][j] + (U[a][j] * U[b][i] if i != j else 0.0)
                        if w == 0:
                            continue
                        mu = block_monomial(lab, rows, a, b, N)
                        vec[mu] = vec.get(mu, 0) + int(round(w))
                varlist.append((bpos, i, j))
                Acols.append(vec)

    def coeffs_of(H):
        out = {mu: F(0) for mu in D4}
        for (bpos, i, j), vec in zip(varlist, Acols):
            val = H[bpos][i][j]
            if val == 0:
                continue
            for mu, w in vec.items():
                out[mu] += F(w) * val
        return out

    cur = coeffs_of(Hrat)
    resid = [Q[mu] - cur[mu] for mu in D4]
    print(f"[exact] residual after rounding (max |.|): "
          f"{max(abs(float(x)) for x in resid):.3e}")

    # ---- exact RREF of the augmented system  A * d = resid  (A may be rank deficient)
    m = len(D4)
    nv = len(varlist)
    work = [[F(Acols[k].get(mu, 0)) for k in range(nv)] + [resid[i]]
            for i, mu in enumerate(D4)]
    pivots = []
    r = 0
    for col in range(nv):
        if r == m:
            break
        sel = None
        for i in range(r, m):
            if work[i][col] != 0:
                sel = i
                break
        if sel is None:
            continue
        work[r], work[sel] = work[sel], work[r]
        inv = work[r][col]
        work[r] = [x / inv for x in work[r]]
        for i in range(m):
            if i != r and work[i][col] != 0:
                f = work[i][col]
                work[i] = [a - f * b for a, b in zip(work[i], work[r])]
        pivots.append(col)
        r += 1
    print(f"[exact] coefficient map rank = {r} of {m} equations, {nv} unknowns")
    incons = [i for i in range(r, m) if work[i][nv] != 0]
    if incons:
        print(f"FAILED: {len(incons)} inconsistent rows -> Q is NOT in the span of the "
              f"facially-reduced Gram cone.  Largest violation "
              f"{max(abs(float(work[i][nv])) for i in incons)}")
        return
    print("[exact] system consistent (Q lies exactly in the reduced Gram span)")
    delta = [work[k][nv] for k in range(r)]      # values of the pivot variables

    for k, col in enumerate(pivots):
        bpos, i, j = varlist[col]
        Hrat[bpos][i][j] += delta[k]
        if i != j:
            Hrat[bpos][j][i] += delta[k]
    print(f"[exact] correction max |delta| = {max(abs(float(d)) for d in delta):.3e}")
    chk = coeffs_of(Hrat)
    bad = [mu for mu in D4 if chk[mu] != Q[mu]]
    print(f"[exact] after correction: coefficient mismatches = {len(bad)}")
    assert not bad

    # ---- exact positive definiteness of every reduced block
    allok = True
    for bpos, (bi, lab, rows, U, Hv) in enumerate(Hs):
        ok, piv = rat_ldl(Hrat[bpos])
        mn = min(piv) if piv else None
        print(f"    block {str(lab):18s} size {len(Hrat[bpos])}  LDL pivots > 0 : {ok}   "
              f"min pivot = {float(mn):.6g}")
        allok = allok and ok
    print(f"[exact] ALL BLOCKS POSITIVE DEFINITE : {allok}")

    if allok:
        # --- export a SELF-CONTAINED certificate: lambda matrices + explicit Gram blocks
        #     indexed by explicit degree-4 y-monomials, so a verifier needs none of this code.
        import json
        out = {"graph": "C5", "n": N, "edges": [list(e) for e in EDGES],
               "claim": "max_x psi(C5,x) <= 1/25",
               "lambda": [[[str(x) for x in row] for row in Le] for Le in L],
               "gram": []}
        for bpos, (bi, lab, rows, U, Hv) in enumerate(Hs):
            sz = len(rows)
            if lab == 'even':
                ymons = [tuple(2 * e for e in b) for b in rows]
            else:
                _, a, b = lab
                ymons = [eadd(unit(N, a, b), unit(N, l, l)) for l in rows]
            Ui = U.astype(int)
            G = [[sum(F(int(Ui[i][p])) * Hrat[bpos][p][q] * F(int(Ui[j][q]))
                      for p in range(U.shape[1]) for q in range(U.shape[1]))
                  for j in range(sz)] for i in range(sz)]
            out["gram"].append({"label": str(lab),
                                "ymonomials": [list(mm) for mm in ymons],
                                "G": [[str(x) for x in row] for row in G]})
        with open('H5_certificate_C5.json', 'w') as f:
            json.dump(out, f, indent=1)
        print("[exact] self-contained certificate written to H5_certificate_C5.json")
        dens = set()
        for Le in L:
            for row in Le:
                for x in row:
                    dens.add(x.denominator)
        gd = set()
        for blk in out["gram"]:
            for row in blk["G"]:
                for x in row:
                    gd.add(F(x).denominator)
        print(f"[exact] lambda denominators {sorted(dens)};  max Gram denominator {max(gd)}")


if __name__ == '__main__':
    main()
