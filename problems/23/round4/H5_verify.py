"""H5 round 4: INDEPENDENT exact verifier for a QMC certificate stored in JSON.

Reads only the JSON (lambda matrices + explicit Gram blocks indexed by explicit y-monomials).
Shares no code with the constructor: uses sympy symbolic expansion for the identity and
characteristic-polynomial sign tests for positive semidefiniteness (the constructor used a
hand-written rational LDL^T).

What is checked, all exactly:
  1. sum_e lambda_e(z) == (sum_j z_j)^2   as an identity of quadratic forms
  2. every lambda_e has nonnegative coefficients  (=> lambda_e(y^2) is SOS in y, so lambda_e >= 0
     on the nonnegative orthant)
  3. every Gram block G_b is symmetric and positive semidefinite (exact charpoly test)
  4. the SOS identity, fully expanded in the y variables:
        (sum_j y_j^2)^4 - 25 * sum_{e=(u,v)} lambda_e(y^2) y_u^2 y_v^2
              ==  sum_b sum_{i,j} G_b[i,j] * y^{m_i} * y^{m_j}
  5. a brute-force independent evaluation that x = (1/n,...,1/n) attains psi = 1/25 on C5,
     so the bound proved is sharp.

Usage: python H5_verify.py H5_certificate_C5.json
"""
import sys
import json
import itertools
import sympy as sp


def psd_exact(M):
    """exact PSD test for a symmetric rational sympy Matrix via the characteristic polynomial:
    a real symmetric matrix is PSD iff every elementary symmetric function of its eigenvalues is
    >= 0, i.e. iff the charpoly coefficients alternate in sign."""
    n = M.rows
    lam = sp.symbols('lam')
    p = sp.Poly(M.charpoly(lam).as_expr(), lam)
    coeffs = [p.coeff_monomial(lam ** k) for k in range(n + 1)]
    # det(lam I - M) = lam^n + sum_{k<n} c_k lam^k with c_k = (-1)^{n-k} e_{n-k}(eig)
    for k in range(n):
        e = (-1) ** (n - k) * coeffs[k]
        if e < 0:
            return False, (k, e)
    return True, None


def main(path):
    d = json.load(open(path))
    n = d['n']
    edges = [tuple(e) for e in d['edges']]
    R = sp.Rational
    y = sp.symbols('y0:%d' % n)
    z = [y[j] ** 2 for j in range(n)]

    # ---- 1 & 2 : the multiplier family
    L = [sp.Matrix(n, n, lambda i, j: R(d['lambda'][e][i][j])) for e in range(len(edges))]
    for e, Le in enumerate(L):
        assert Le == Le.T, f"lambda_{e} not symmetric"
    tot = sp.zeros(n, n)
    for Le in L:
        tot += Le
    ok_sum = (tot == sp.ones(n, n))
    ok_nonneg = all(Le[i, j] >= 0 for Le in L for i in range(n) for j in range(n))
    print(f"[verify] (1) sum_e lambda_e == (sum z)^2 : {ok_sum}")
    print(f"[verify] (2) all lambda coefficients >= 0 : {ok_nonneg}")
    assert ok_sum and ok_nonneg

    # ---- 3 : Gram blocks PSD
    blocks = []
    for blk in d['gram']:
        G = sp.Matrix(len(blk['G']), len(blk['G']),
                      lambda i, j: R(blk['G'][i][j]))
        assert G == G.T, f"block {blk['label']} not symmetric"
        ok, why = psd_exact(G)
        rk = G.rank()
        print(f"[verify] (3) block {blk['label']:18s} size {G.rows:2d} PSD={ok} rank={rk}"
              + ("" if ok else f"  VIOLATION at e_{G.rows-why[0]} = {why[1]}"))
        assert ok
        blocks.append((G, [tuple(m) for m in blk['ymonomials']]))

    # ---- 4 : the identity
    lhs = sum(z) ** 4
    for e, (u, v) in enumerate(edges):
        lam = sum(L[e][i, j] * z[i] * z[j] for i in range(n) for j in range(n))
        lhs -= 25 * lam * z[u] * z[v]
    rhs = 0
    for (G, ms) in blocks:
        for i in range(G.rows):
            mi = sp.prod([y[t] ** ms[i][t] for t in range(n)])
            for j in range(G.rows):
                if G[i, j] == 0:
                    continue
                mj = sp.prod([y[t] ** ms[j][t] for t in range(n)])
                rhs += G[i, j] * mi * mj
    diff = sp.expand(lhs - rhs)
    print(f"[verify] (4) SOS identity residual (expanded) : {diff}")
    assert diff == 0

    # ---- 5 : sharpness, computed from scratch
    E = edges if d['graph'] != 'C5' else [(i, (i + 1) % n) for i in range(n)]
    Eall = [(i, (i + 1) % n) for i in range(n)] if d['graph'] == 'C5' else E
    x = [R(1, n)] * n
    best = None
    for m in range(1 << (n - 1)):
        side = [0] + [(m >> i) & 1 for i in range(n - 1)]
        q = sum(x[u] * x[v] for (u, v) in Eall if side[u] == side[v])
        best = q if best is None else min(best, q)
    print(f"[verify] (5) psi(C5, uniform) = {best}  (= 1/25 : {best == R(1,25)})")

    print()
    print("[verify] CONCLUSION.  For every x in the simplex put t = psi(C5,x) = min_S q_S(x) >= 0.")
    print("         Item (4) with y_j = sqrt(x_j) gives  1 - 25*sum_e lambda_e(x) x_u x_v >= 0,")
    print("         items (1),(2) give sum_e lambda_e(x) = 1 and lambda_e(x) >= 0, and every")
    print("         q_e(x) = x_u x_v is a cut value so q_e(x) >= t.  Hence 1 >= 25 t, i.e.")
    print("         max_x psi(C5,x) <= 1/25, and by (5) equality holds.  QED")


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'H5_certificate_C5.json')
