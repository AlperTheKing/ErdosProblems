"""H2_flat.py -- the exact FLAT SUBSPACE at a rotation-symmetric equality point,
and the second-order quadratic system on it.

At w0 = all-ones on Gamma_m the optimal-arc family is closed under rotation, so
sum over the rotation orbit of L_A(h) = c * sum(h) = 0.  Hence
    L_{A*}(h) >= 0 for all optimal arcs  <=>  L_{A*}(h) = 0 for all optimal arcs.
The admissible perturbations therefore form the linear space

    V = { h : sum h = 0,  L_{A*}(h) = 0 for every optimal arc A* }.

On V the asymptotic criteria become purely quadratic:
    ARC violated for large t   <=>  mono(A*,h) > 0 for every optimal arc A*
    WSQ violated for large t   <=>  S0^2 mono(A*,h) > 2 W0 W(h)  for every optimal A*
"""
import sys
from fractions import Fraction
from H2_core import adj_matrix, edges, total_W, arcbound_fast


def all_arcs(m):
    out = set()
    for s in range(m):
        inA = [False] * m
        for L in range(1, m):
            inA[(s + L - 1) % m] = True
            out.add(tuple(inA))
    return sorted(out)


def setup(m, w0=None):
    if w0 is None:
        w0 = [1] * m
    E = edges(m)
    W0 = total_W(w0, E)
    S0 = sum(w0)
    arcs = all_arcs(m)
    mono0 = {}
    for a in arcs:
        mono0[a] = sum(w0[i] * w0[j] for (i, j) in E if a[i] == a[j])
    AB0 = min(mono0.values())
    opt = [a for a in arcs if mono0[a] == AB0]
    return E, w0, W0, S0, AB0, arcs, mono0, opt


def Lvec(a, E, w0, m):
    """L_a(h) = sum_v h_v * coeff_v."""
    c = [0] * m
    for (i, j) in E:
        if a[i] == a[j]:
            c[j] += w0[i]
            c[i] += w0[j]
    return c


def rref_nullspace(rows, n):
    """Exact nullspace basis (Fractions) of the integer matrix `rows` (list of lists)."""
    M = [[Fraction(x) for x in r] for r in rows]
    piv = []
    r = 0
    for c in range(n):
        p = None
        for i in range(r, len(M)):
            if M[i][c] != 0:
                p = i; break
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        pv = M[r][c]
        M[r] = [x / pv for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        piv.append(c)
        r += 1
        if r == len(M):
            break
    free = [c for c in range(n) if c not in piv]
    basis = []
    for f in free:
        v = [Fraction(0)] * n
        v[f] = Fraction(1)
        for i, c in enumerate(piv):
            v[c] = -M[i][f]
        basis.append(v)
    return basis


def flat_space(m, w0=None):
    E, w0, W0, S0, AB0, arcs, mono0, opt = setup(m, w0)
    rows = [[1] * m]
    for a in opt:
        rows.append(Lvec(a, E, w0, m))
    B = rref_nullspace(rows, m)
    return dict(m=m, E=E, w0=w0, W0=W0, S0=S0, AB0=AB0, arcs=arcs,
                mono0=mono0, opt=opt, basis=B)


if __name__ == "__main__":
    ms = [int(x) for x in sys.argv[1:]] or list(range(5, 42))
    for m in ms:
        d = flat_space(m)
        E, W0, S0, AB0 = d['E'], d['W0'], d['S0'], d['AB0']
        eqW = AB0 * S0 * S0 == W0 * W0
        eqA = 25 * AB0 == S0 * S0
        print(f"m={m:3d} deg={2*len(E)//m:3d} AB0={AB0:4d} W0={W0:5d} "
              f"#optarcs={len(d['opt']):4d} dim(V)={len(d['basis']):3d} "
              f"WSQ-eq={int(eqW)} ARC-eq={int(eqA)}")
