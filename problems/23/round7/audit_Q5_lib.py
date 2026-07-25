"""INDEPENDENT audit library for round7/Q5.md.

Written from scratch (own graph6 decoder, own max-cut/bip routine, own odd-cycle
enumeration, own exact tau* with two-sided rational certificates).  Floating point
(scipy) is used ONLY to steer the LP search; every accepted number is re-derived and
re-verified with fractions.Fraction over a COMPLETE enumeration of odd cycles.
"""
from fractions import Fraction as F
from itertools import combinations, product
import sys


# --------------------------------------------------------------- graph6 -----
def g6(s):
    """Own graph6 decoder -> (n, list of adjacency bitmasks)."""
    s = s.strip()
    b = [ord(c) - 63 for c in s]
    if b[0] == 63:
        raise NotImplementedError
    n = b[0]
    # concatenate the 6-bit groups into one big integer, MSB first
    acc = 0
    nb = 0
    for d in b[1:]:
        acc = (acc << 6) | d
        nb += 6
    need = n * (n - 1) // 2
    # the bit stream is padded on the right with zeros
    acc >>= (nb - need) if nb >= need else 0
    A = [0] * n
    k = need - 1
    for j in range(1, n):
        for i in range(j):
            if (acc >> k) & 1:
                A[i] |= 1 << j
                A[j] |= 1 << i
            k -= 1
    return n, A


def g6_encode(n, A):
    bits = []
    for j in range(1, n):
        for i in range(j):
            bits.append(1 if (A[i] >> j) & 1 else 0)
    while len(bits) % 6:
        bits.append(0)
    out = chr(n + 63)
    for i in range(0, len(bits), 6):
        v = 0
        for k in range(6):
            v = (v << 1) | bits[i + k]
        out += chr(v + 63)
    return out


def E_of(n, A):
    return [(i, j) for i in range(n) for j in range(i + 1, n) if (A[i] >> j) & 1]


def tri_free(n, A):
    for i in range(n):
        for j in range(i + 1, n):
            if (A[i] >> j) & 1 and (A[i] & A[j]):
                return False
    return True


def induced(n, A, S):
    S = sorted(S)
    idx = {v: i for i, v in enumerate(S)}
    B = [0] * len(S)
    for u in S:
        for v in S:
            if u != v and (A[u] >> v) & 1:
                B[idx[u]] |= 1 << idx[v]
    return len(S), B


# ------------------------------------------------------- bip (own routine) --
def bip(n, A, w=None):
    """min over cuts of the monochromatic weight.  Own routine: iterate the cut as
    a bitmask, accumulate per-edge, vertex 0 pinned.  w: dict (u,v)->number."""
    E = E_of(n, A)
    if w is None:
        w = {e: 1 for e in E}
    best = None
    bestS = None
    for m in range(1 << (n - 1)):
        S = m << 1                      # vertex 0 on side 0
        t = 0
        for (u, v) in E:
            if ((S >> u) ^ (S >> v)) & 1 == 0:
                t += w[(u, v)]
        if best is None or t < best:
            best, bestS = t, S
    return best, bestS


def psi(n, A, x):
    """psi(G,x) = min over cuts of sum over monochromatic uv of x_u x_v."""
    E = E_of(n, A)
    w = {e: x[e[0]] * x[e[1]] for e in E}
    return bip(n, A, w)[0]


def emass(n, A, x):
    return sum(x[u] * x[v] for (u, v) in E_of(n, A))


# ---------------------------------------------- complete cycle enumeration --
def all_cycles(n, A, only_odd=True, maxlen=None):
    """ALL simple cycles, each once, as sorted tuples of edges.
    Own DFS: smallest vertex of the cycle is the root; second vertex < last vertex."""
    out = []
    for r in range(n):
        # paths starting at r using only vertices > r
        stack = [(r, (r,), 1 << r)]
        while stack:
            u, path, used = stack.pop()
            for v in range(n):
                if not (A[u] >> v) & 1:
                    continue
                if v == r:
                    if len(path) >= 3 and path[1] < path[-1]:
                        if not only_odd or len(path) % 2 == 1:
                            cyc = tuple(sorted(
                                (min(path[i], path[(i + 1) % len(path)]),
                                 max(path[i], path[(i + 1) % len(path)]))
                                for i in range(len(path))))
                            out.append(cyc)
                    continue
                if v <= r or (used >> v) & 1:
                    continue
                if maxlen is not None and len(path) + 1 > maxlen:
                    continue
                stack.append((v, path + (v,), used | (1 << v)))
    return out


# ------------------------------------------------- exact tau* (two-sided) ---
def tau_star_exact(n, A, w=None, verbose=False):
    """EXACT fractional odd-cycle cover value.

    Complete enumeration of odd cycles, scipy(float) to steer, then an exact
    rational primal cover z and dual packing y with w.z == sum y.  Returns
    (value, z, y, cycles) or raises."""
    import numpy as np
    from scipy.optimize import linprog
    E = E_of(n, A)
    ei = {e: i for i, e in enumerate(E)}
    if w is None:
        w = {e: F(1) for e in E}
    w = {e: F(w[e]) for e in E}
    C = all_cycles(n, A, only_odd=True)
    if not C:
        return F(0), {e: F(0) for e in E}, [], []
    M = len(C)
    # primal: min w.z  s.t.  z(C) >= 1, z >= 0
    Aub = np.zeros((M, len(E)))
    for k, cyc in enumerate(C):
        for e in cyc:
            Aub[k, ei[e]] = -1.0
    bub = -np.ones(M)
    cvec = np.array([float(w[e]) for e in E])
    r = linprog(cvec, A_ub=Aub, b_ub=bub, bounds=[(0, None)] * len(E),
                method="highs")
    if not r.success:
        raise RuntimeError("primal LP failed: " + str(r.message))
    zf = r.x
    yf = -r.ineqlin.marginals            # dual multipliers >= 0

    # ---- rationalise and verify EXACTLY
    for D in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 16, 20, 24, 25, 30, 32, 35, 40,
              48, 50, 60, 64, 70, 72, 80, 90, 96, 100, 120, 128, 140, 144, 160, 180,
              200, 210, 240, 280, 300, 360, 420, 480, 504, 560, 600, 720, 840, 1000,
              1260, 1680, 2520, 5040, 10080, 100000):
        z = {E[i]: F(zf[i]).limit_denominator(D) for i in range(len(E))}
        if any(v < 0 for v in z.values()):
            continue
        if any(sum(z[e] for e in cyc) < 1 for cyc in C):
            continue
        val = sum(w[e] * z[e] for e in E)
        y = [F(yf[k]).limit_denominator(D) for k in range(M)]
        if any(v < 0 for v in y):
            continue
        load = {e: F(0) for e in E}
        for k, cyc in enumerate(C):
            if y[k]:
                for e in cyc:
                    load[e] += y[k]
        if any(load[e] > w[e] for e in E):
            continue
        if sum(y) != val:
            continue
        pack = [(C[k], y[k]) for k in range(M) if y[k]]
        if verbose:
            print(f"    tau* certified at denominator {D}: {val}")
        return val, z, pack, C
    # exact fallback: solve the optimal basis exactly
    return _tau_star_exact_basis(n, A, w, C, zf, yf, E, ei)


def _tau_star_exact_basis(n, A, w, C, zf, yf, E, ei):
    """Fallback: take the float support/tight sets, solve the square system with
    Fractions, verify feasibility of both sides exactly."""
    tolz = 1e-9
    supp = [i for i in range(len(E)) if zf[i] > tolz]
    tight = [k for k in range(len(C)) if abs(sum(zf[ei[e]] for e in C[k]) - 1) < 1e-7]
    # solve  sum_{e in supp} z_e = 1 for each tight cycle, z_e = 0 elsewhere
    rows = []
    rhs = []
    for k in tight:
        rows.append([F(1) if E[i] in C[k] else F(0) for i in supp])
        rhs.append(F(1))
    zs = _solve_ls(rows, rhs, len(supp))
    if zs is None:
        raise RuntimeError("exact fallback failed (primal)")
    z = {e: F(0) for e in E}
    for t, i in enumerate(supp):
        z[E[i]] = zs[t]
    if any(v < 0 for v in z.values()):
        raise RuntimeError("exact fallback: negative z")
    if any(sum(z[e] for e in cyc) < 1 for cyc in C):
        raise RuntimeError("exact fallback: infeasible z")
    val = sum(w[e] * z[e] for e in E)
    ysupp = [k for k in range(len(C)) if yf[k] > tolz]
    rows = []
    rhs = []
    for i in supp:
        rows.append([F(1) if E[i] in C[k] else F(0) for k in ysupp])
        rhs.append(w[E[i]])
    rows.append([F(1)] * len(ysupp))
    rhs.append(val)
    ys = _solve_ls(rows, rhs, len(ysupp))
    if ys is None or any(v < 0 for v in ys):
        raise RuntimeError("exact fallback failed (dual)")
    load = {e: F(0) for e in E}
    for t, k in enumerate(ysupp):
        for e in C[k]:
            load[e] += ys[t]
    if any(load[e] > w[e] for e in E):
        raise RuntimeError("exact fallback: packing infeasible")
    if sum(ys) != val:
        raise RuntimeError("exact fallback: no duality match")
    return val, z, [(C[ysupp[t]], ys[t]) for t in range(len(ysupp)) if ys[t]], C


def _solve_ls(rows, rhs, nvar):
    """Exact Gaussian elimination; returns any solution or None."""
    M = [list(rows[i]) + [rhs[i]] for i in range(len(rows))]
    piv = []
    r = 0
    for c in range(nvar):
        p = None
        for i in range(r, len(M)):
            if M[i][c] != 0:
                p = i
                break
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        pv = M[r][c]
        M[r] = [x / pv for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [M[i][j] - f * M[r][j] for j in range(nvar + 1)]
        piv.append(c)
        r += 1
        if r == len(M):
            break
    for i in range(r, len(M)):
        if all(M[i][j] == 0 for j in range(nvar)) and M[i][nvar] != 0:
            return None
    x = [F(0)] * nvar
    for i, c in enumerate(piv):
        x[c] = M[i][nvar]
    return x


# ------------------------------------------------------- named graphs -------
def C5n(k):
    """C5[k]."""
    N = 5 * k
    A = [0] * N
    for p in range(5):
        q = (p + 1) % 5
        for a in range(k):
            for b in range(k):
                u, v = p * k + a, q * k + b
                A[u] |= 1 << v
                A[v] |= 1 << u
    return N, A


def circulant(N, diffs):
    A = [0] * N
    for i in range(N):
        for d in diffs:
            j = (i + d) % N
            if j != i:
                A[i] |= 1 << j
                A[j] |= 1 << i
    return N, A


def andrasfai(k):
    """Gamma_{3k-1}: i~j iff circular distance*3 > N."""
    N = 3 * k - 1
    A = [0] * N
    for i in range(N):
        for j in range(i + 1, N):
            d = min((j - i) % N, (i - j) % N)
            if 3 * d > N:
                A[i] |= 1 << j
                A[j] |= 1 << i
    return N, A


def V8():
    return circulant(8, [1, 4])


def petersen():
    A = [0] * 10
    for i in range(5):
        for (u, v) in ((i, (i + 1) % 5), (i, 5 + i), (5 + i, 5 + (i + 2) % 5)):
            A[u] |= 1 << v
            A[v] |= 1 << u
    return 10, A


def grotzsch():
    A = [0] * 11

    def add(a, b):
        A[a] |= 1 << b
        A[b] |= 1 << a
    for i in range(5):
        add(i, (i + 1) % 5)
        add(5 + i, (i + 1) % 5)
        add(5 + i, (i - 1) % 5)
        add(10, 5 + i)
    return 11, A


def Kn(k):
    A = [0] * k
    for i in range(k):
        for j in range(k):
            if i != j:
                A[i] |= 1 << j
    return k, A


def subdiv3(n, A):
    E = E_of(n, A)
    m = n + 2 * len(E)
    B = [0] * m
    nxt = n

    def add(a, b):
        B[a] |= 1 << b
        B[b] |= 1 << a
    for (u, v) in E:
        a, b = nxt, nxt + 1
        nxt += 2
        add(u, a)
        add(a, b)
        add(b, v)
    return m, B


NAMED_G6 = {
    "N12a": "K?ABBBwerwBw",
    "N12b": "K?BD@g]Qvo^?",
    "N13": "L??ED@_~?~^_Fw",
    "N14": "M?AE@bH{AYN_LgBs?",
}
