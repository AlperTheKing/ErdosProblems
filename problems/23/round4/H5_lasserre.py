"""H5 (round 4), part (a): INDEPENDENT Lasserre / moment relaxation of

        max_x psi(H,x) = max { t : q_S(x) >= t for every cut S,  x >= 0,  sum x = 1,  0 <= t <= 1/4 }

written from scratch: own monomial ordering, own moment/localizing assembly (sparse
selection matrices + one reshape, no cp.bmat), own cut enumeration, own equality handling.

Deliberately different from round3/claude_lasserre_epi.py in every implementation detail so
that agreement of the optimal values is evidence and not a shared bug.

Usage:  python H5_lasserre.py <graph> <level> [--solver both|scs|clarabel] [--cuts all|rot]
"""
import sys
import time
import numpy as np
import scipy.sparse as sp
import cvxpy as cp


# ---------------------------------------------------------------- monomials
def mons_upto(nvar, dmax):
    """All exponent tuples in nvar variables of total degree <= dmax,
    ordered by (total degree, colexicographic)."""
    out = []
    cur = [0] * nvar

    def rec(pos, rem):
        if pos == nvar - 1:
            for e in range(rem + 1):
                cur[pos] = e
                out.append(tuple(cur))
            cur[pos] = 0
            return
        for e in range(rem + 1):
            cur[pos] = e
            rec(pos + 1, rem - e)
        cur[pos] = 0

    rec(0, dmax)
    out.sort(key=lambda a: (sum(a), a[::-1]))
    return out


def add(a, b):
    return tuple(ai + bi for ai, bi in zip(a, b))


# ---------------------------------------------------------------- graphs
def graph(name):
    if name == 'C5':
        return 5, [(i, (i + 1) % 5) for i in range(5)]
    if name == 'C7':
        return 7, [(i, (i + 1) % 7) for i in range(7)]
    if name == 'wagner':            # And(3) = Moebius-Kantor V8 = C8 + 4 main diagonals
        E = set()
        for v in range(8):
            for w in ((v + 1) % 8, (v + 4) % 8):
                E.add((min(v, w), max(v, w)))
        return 8, sorted(E)
    if name == 'and4':              # Andrasfai(4) = circulant C11(1,2)? -- Gamma_11, 3*d>11 <=> d in {4,5}
        n = 11
        E = set()
        for v in range(n):
            for d in (4, 5):
                w = (v + d) % n
                E.add((min(v, w), max(v, w)))
        return n, sorted(E)
    if name == 'P5':                # path on 5 vertices (sanity: bipartite, psi = 0)
        return 5, [(i, i + 1) for i in range(4)]
    raise SystemExit('unknown graph ' + name)


def all_cuts(n, E):
    """Monochromatic edge sets q_S, one per cut (S and complement identified by fixing vertex 0)."""
    out = []
    for m in range(1 << (n - 1)):
        side = [(m >> i) & 1 for i in range(n - 1)]
        side = [0] + side
        out.append(tuple((u, v) for (u, v) in E if side[u] == side[v]))
    return out


def rotation_cuts_C5():
    """The five single-edge cuts of C5: S = {i, i+2} leaves only edge (i+3, i+4) monochromatic."""
    out = []
    for i in range(5):
        u, v = (i + 3) % 5, (i + 4) % 5
        out.append(((min(u, v), max(u, v)),))
    return out


# ---------------------------------------------------------------- SDP assembly
def selector(rows_basis, shifts, index, nmom):
    """Sparse S with (S @ y).reshape(k,k) = the matrix  M[a][b] = sum_c coeff_c * y[a+b+shift_c]."""
    k = len(rows_basis)
    data, ri, ci = [], [], []
    for i, a in enumerate(rows_basis):
        for j, b in enumerate(rows_basis):
            ab = add(a, b)
            for (co, sh) in shifts:
                data.append(co)
                ri.append(i * k + j)
                ci.append(index[add(ab, sh)])
    return sp.csr_matrix((data, (ri, ci)), shape=(k * k, nmom)), k


def build(name, level, cutmode='all', verbose=True):
    n, E = graph(name)
    if cutmode == 'rot':
        assert name == 'C5'
        cuts = rotation_cuts_C5()
    else:
        cuts = all_cuts(n, E)
    # dedupe identical monochromatic edge-sets (different S can give the same q_S)
    cuts = sorted(set(cuts))
    N = n + 1                       # variables x_0..x_{n-1}, and t at index n
    ZERO = tuple([0] * N)
    ET = tuple([0] * n + [1])

    B = mons_upto(N, level)                 # moment-matrix basis
    Bl = mons_upto(N, level - 1)            # localizing basis (all our g have degree <= 2)
    allmon = mons_upto(N, 2 * level)
    index = {a: i for i, a in enumerate(allmon)}
    nmom = len(allmon)
    if verbose:
        print(f"[H5] {name}: n={n} |E|={len(E)} distinct-cuts={len(cuts)} level={level} "
              f"moments={nmom} M={len(B)}x{len(B)} L={len(Bl)}x{len(Bl)}")

    y = cp.Variable(nmom)
    cons = [y[index[ZERO]] == 1]

    Smom, k = selector(B, [(1.0, ZERO)], index, nmom)
    cons.append(cp.reshape(Smom @ y, (k, k), order='C') >> 0)

    def gshift(edges, with_t):
        sh = []
        for (u, v) in edges:
            e = [0] * N
            e[u] += 1
            e[v] += 1
            sh.append((1.0, tuple(e)))
        if with_t:
            sh.append((-1.0, ET))
        return sh

    for mono in cuts:                                   # q_S(x) - t >= 0
        S, k2 = selector(Bl, gshift(mono, True), index, nmom)
        cons.append(cp.reshape(S @ y, (k2, k2), order='C') >> 0)
    for i in range(n):                                  # x_i >= 0
        e = [0] * N
        e[i] = 1
        S, k2 = selector(Bl, [(1.0, tuple(e))], index, nmom)
        cons.append(cp.reshape(S @ y, (k2, k2), order='C') >> 0)
    S, k2 = selector(Bl, [(1.0, ET)], index, nmom)      # t >= 0
    cons.append(cp.reshape(S @ y, (k2, k2), order='C') >> 0)
    S, k2 = selector(Bl, [(0.25, ZERO), (-1.0, ET)], index, nmom)   # 1/4 - t >= 0
    cons.append(cp.reshape(S @ y, (k2, k2), order='C') >> 0)

    # equality  (sum_i x_i - 1) * x^a = 0  for every monomial a of degree <= 2*level-1
    rows, cols, vals = [], [], []
    r = 0
    for a in mons_upto(N, 2 * level - 1):
        for i in range(n):
            e = [0] * N
            e[i] = 1
            rows.append(r); cols.append(index[add(a, tuple(e))]); vals.append(1.0)
        rows.append(r); cols.append(index[a]); vals.append(-1.0)
        r += 1
    Aeq = sp.csr_matrix((vals, (rows, cols)), shape=(r, nmom))
    cons.append(Aeq @ y == 0)

    prob = cp.Problem(cp.Maximize(y[index[ET]]), cons)
    return prob, y, index, ET


def run(name, level, which='both', cutmode='all'):
    prob, y, index, ET = build(name, level, cutmode)
    res = {}
    solvers = {'scs': cp.SCS, 'clarabel': cp.CLARABEL}
    todo = list(solvers) if which == 'both' else [which]
    for s in todo:
        t0 = time.time()
        try:
            kw = {'max_iters': 400000, 'eps': 1e-10} if s == 'scs' else {'max_iter': 400}
            prob.solve(solver=solvers[s], verbose=False, **kw)
            dt = time.time() - t0
            print(f"    {s:9s} status={prob.status:20s} value={prob.value!r}  ({dt:.1f}s)")
            res[s] = (prob.status, prob.value, dt)
        except Exception as ex:
            print(f"    {s:9s} FAILED after {time.time()-t0:.1f}s: {ex}")
            res[s] = ('failed', None, time.time() - t0)
    return res


if __name__ == '__main__':
    name = sys.argv[1] if len(sys.argv) > 1 else 'C5'
    lev = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    which = 'both'
    cutmode = 'all'
    for i, a in enumerate(sys.argv):
        if a == '--solver':
            which = sys.argv[i + 1]
        if a == '--cuts':
            cutmode = sys.argv[i + 1]
    run(name, lev, which, cutmode)
