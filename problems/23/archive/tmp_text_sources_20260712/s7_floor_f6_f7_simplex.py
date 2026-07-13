from __future__ import annotations
import math
import sympy as sp


def bernstein_controls(poly, var, upper):
    P = sp.Poly(sp.expand(poly), var)
    n = P.degree()
    coeff = {i: P.nth(i) for i in range(n + 1)}
    out = []
    for k in range(n + 1):
        s = 0
        for i in range(k + 1):
            if coeff[i] != 0:
                s += coeff[i] * sp.Rational(math.comb(k, i), math.comb(n, i)) * upper**i
        out.append(sp.expand(s))
    return out


def stats(poly, vars_):
    P = sp.Poly(sp.expand(poly), *vars_)
    coeffs = P.coeffs()
    neg = [(m,c) for m,c in zip(P.monoms(), coeffs) if c < 0]
    return len(coeffs), P.total_degree(), min(coeffs) if coeffs else 0, len(neg), neg[:3]


def f6_base():
    C,E,U,d,L,W,X = sp.symbols('C E U d L W X')
    c = 1 + C
    e = c + E
    u = 1 + U
    x = 1 + X
    y = 1 + W - X
    P = x + y
    q = u + e
    M = e * P + u * x
    D = q + d
    R = D + L
    T = R + 1 + sp.Rational(1,1)*(M - c) / D
    N = T + D + P + q
    Phi = 2*N**2 + 4*u*N*x/e - 50*M - 75*M/e + 75*D + 75*T*L/(M+L) - 15
    target = sp.together(e * D**2 * (M+L) * Phi).as_numer_denom()[0]
    M0 = C + E + U + d + L
    return target, (C,E,U,d,L), W, X, M0


def f7_base():
    E,C,U,d,L,W,X = sp.symbols('E C U d L W X')
    e = 1 + E
    c = e + C
    u = 1 + U
    x = 1 + X
    y = 1 + W - X
    P = x + y
    q = u + e
    M = e * P + u * x
    D = q + d
    R = D + L
    gap = C + L
    T = R + 1 + (M - e) / D
    N = T + D + P + q
    Phi = 2*N**2 + 4*u*N*x/e - 50*M - 75*M/e + 75*D + 75*T*gap/(M+gap) - 15
    target = sp.together(e * D**2 * (M+gap) * Phi).as_numer_denom()[0]
    M0 = E + U + d + L
    # P<=R gives W<=1+E+U+d+L, independent of C.
    return target, (E,C,U,d,L), W, X, M0


def run(name, builder):
    target, base_vars, W, X, M0 = builder()
    bx = bernstein_controls(target, X, W)
    print(name, 'X degree controls', len(bx))
    all_stats = []
    bad = []
    for idx, ctrl in enumerate(bx):
        bw = bernstein_controls(ctrl, W, M0)
        for j, c in enumerate(bw):
            st = stats(c, base_vars)
            all_stats.append(st)
            if st[3]:
                bad.append((idx,j,st))
                print(name, 'BAD', idx, j, st)
                return False
    print(name, 'PASS controls', len(all_stats), 'max_terms', max(s[0] for s in all_stats), 'max_degree', max(s[1] for s in all_stats), 'min_coeff', min(s[2] for s in all_stats))
    return True

if __name__ == '__main__':
    print('F6 ok?', run('F6', f6_base))
    print('F7 ok?', run('F7', f7_base))
