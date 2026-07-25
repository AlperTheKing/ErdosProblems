#!/usr/bin/env python3
"""Exact polytope engine for {x in R^6 : N x <= c}, N = the fixed 27 r=5 hive
normals.

Provides
    reduce_rhs(b)          30 rhombus rhs -> 27 normal-indexed rhs
    vertices(c)            exact vertex list (Fractions), integer arithmetic
    facets(V, c)           which normals actually support a facet
    ridges(V, c)           codim-2 faces with their two facet normals
    relvol(V, S)           normalized relative volume of a face (lattice-normalized)
    lambda_vector(c)       the Q^342 ridge-volume vector

Vertex enumeration is exact integer Cramer over the FIXED nonsingular 6-subsets
of the 27 normals; numpy is used only for int64 bookkeeping, never for a
decision that is not an exact integer comparison.
"""
import itertools
import os
import sys
from fractions import Fraction

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from hive5 import A5, NORMALS5, NORMAL_INDEX5, D  # noqa: E402
from exactlin import (rref, rank, prim, det_frac, invert, smith,  # noqa: E402
                      pivots)

NN = len(NORMALS5)          # 27
NARR = np.array(NORMALS5, dtype=np.int64)

# unordered nonparallel pairs of normals = ridge types
def _pair_types():
    out = []
    for i in range(NN):
        for j in range(i + 1, NN):
            if all(NORMALS5[i][t] == -NORMALS5[j][t] for t in range(D)):
                continue
            out.append((i, j))
    return out


PAIR_TYPES = _pair_types()                       # 342
PAIR_INDEX = {p: k for k, p in enumerate(PAIR_TYPES)}


# --------------------------------------------------------------- fixed bases
_CACHE = os.path.join(HERE, '_bases27.npz')


def _adjugate_int(M):
    """Integer adjugate of a 6x6 integer matrix (transpose of cofactors)."""
    n = len(M)
    adj = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            minor = [[M[a][b] for b in range(n) if b != i]
                     for a in range(n) if a != j]
            adj[i][j] = ((-1) ** (i + j)) * _det_small(minor)
    return adj


def _det_small(M):
    n = len(M)
    if n == 1:
        return M[0][0]
    if n == 2:
        return M[0][0] * M[1][1] - M[0][1] * M[1][0]
    tot = 0
    for j in range(n):
        if M[0][j] == 0:
            continue
        minor = [[M[a][b] for b in range(n) if b != j] for a in range(1, n)]
        tot += ((-1) ** j) * M[0][j] * _det_small(minor)
    return tot


def load_bases():
    if os.path.exists(_CACHE):
        z = np.load(_CACHE)
        return z['idx'], z['adj'], z['det']
    idx, adj, det = [], [], []
    for S in itertools.combinations(range(NN), D):
        M = [list(NORMALS5[i]) for i in S]
        dt = _det_small(M)
        if dt == 0:
            continue
        idx.append(S)
        adj.append(_adjugate_int(M))
        det.append(dt)
    idx = np.array(idx, dtype=np.int64)
    adj = np.array(adj, dtype=np.int64)
    det = np.array(det, dtype=np.int64)
    np.savez_compressed(_CACHE, idx=idx, adj=adj, det=det)
    return idx, adj, det


IDX, ADJ, DET = load_bases()
ABSDET = np.abs(DET)
SGN = np.sign(DET)


def reduce_rhs(b30):
    """30 rhombus rhs -> tight rhs indexed by the 27 distinct normals."""
    c = [None] * NN
    for row, rhs in zip(A5, b30):
        k = NORMAL_INDEX5[row]
        c[k] = rhs if c[k] is None else min(c[k], rhs)
    assert all(x is not None for x in c)
    return c


def vertices(c):
    """Exact vertices of {x : NORMALS5 x <= c}.  c: list of 27 integers."""
    cv = np.array(c, dtype=np.int64)
    BS = cv[IDX]                                    # (m,6)
    X = np.einsum('kij,kj->ki', ADJ, BS)            # adj * c_S ; x = X/det
    S = X @ NARR.T                                  # (m,27)
    rhs = cv[None, :] * ABSDET[:, None]
    ok = ((S * SGN[:, None]) <= rhs).all(axis=1)
    out = set()
    for k in np.nonzero(ok)[0]:
        d = int(DET[k])
        out.add(tuple(Fraction(int(X[k, t]), d) for t in range(D)))
    return sorted(out)


def affine_rank(pts):
    if not pts:
        return -1
    p0 = pts[0]
    return rank([[p[t] - p0[t] for t in range(len(p0))] for p in pts[1:]])


def tight_sets(V, c):
    """For each normal index, the frozenset of vertex indices where it is tight."""
    T = []
    for i in range(NN):
        n = NORMALS5[i]
        T.append(frozenset(t for t, v in enumerate(V)
                           if sum(n[k] * v[k] for k in range(D)) == c[i]))
    return T


def facets(V, c, T=None):
    if T is None:
        T = tight_sets(V, c)
    return [i for i in range(NN)
            if len(T[i]) >= D and affine_rank([V[t] for t in T[i]]) == D - 1]


def ridges(V, c, T=None, F=None):
    """dict: (i,j) facet-normal pair -> frozenset of vertex indices (dim d-2)."""
    if T is None:
        T = tight_sets(V, c)
    if F is None:
        F = facets(V, c, T)
    out = {}
    for a in range(len(F)):
        for bq in range(a + 1, len(F)):
            i, j = F[a], F[bq]
            S = T[i] & T[j]
            if len(S) < D - 1:
                continue
            if affine_rank([V[t] for t in S]) != D - 2:
                continue
            out[(i, j)] = S
    return out


# ------------------------------------------------- lattice coords & volumes
def lattice_coords(pts):
    """Coordinates of pts in a basis of the direction lattice Z^6 cap lin(pts-p0)."""
    p0 = pts[0]
    dirs = [[p[i] - p0[i] for i in range(D)] for p in pts[1:]]
    R = rref(dirs)
    k = len(R)
    if k == 0:
        return [tuple()] * len(pts), 0
    piv = pivots(R, D)
    L0 = _saturated_basis(R, piv, k)
    Minv = invert(L0, k)
    coords = []
    for p in pts:
        v = [Fraction(p[c]) - Fraction(p0[c]) for c in piv]
        coords.append(tuple(sum(Minv[i][j] * v[j] for j in range(k))
                            for i in range(k)))
    return coords, k


def _saturated_basis(R, piv, k):
    """Basis (in piv coordinates) of Z^6 cap span(R), R the rational rref."""
    from math import gcd
    M = [[R[i][c] for i in range(k)] for c in range(D)]
    den = 1
    for row in M:
        for x in row:
            den = den * x.denominator // gcd(den, x.denominator)
    Mi = [[int(x * den) for x in row] for row in M]
    Sm, _U, Vv = smith(Mi, D, k)
    basis = []
    for i in range(k):
        s = Sm[i][i] if i < len(Sm) else 0
        m = 1 if s == 0 else den // gcd(den, abs(s))
        e = [0] * k
        e[i] = m
        basis.append([sum(Vv[a][bq] * e[bq] for bq in range(k)) for a in range(k)])
    return [[Fraction(x) for x in row] for row in basis]


def relvol(V, S, T):
    """Normalized relative volume of the face with vertex-index set S."""
    idx = sorted(S)
    pts = [V[i] for i in idx]
    coords, k = lattice_coords(pts)
    if k == 0:
        return Fraction(1)
    cmap = {idx[t]: coords[t] for t in range(len(idx))}

    def tri(vset, dim):
        if dim == 0:
            return [(next(iter(vset)),)]
        v0 = min(vset)
        out = []
        seen = set()
        for i in range(NN):
            Fc = frozenset(vset) & T[i]
            if len(Fc) < dim or Fc in seen or Fc == frozenset(vset):
                continue
            if affine_rank([V[t] for t in Fc]) != dim - 1:
                continue
            seen.add(Fc)
            if v0 in Fc:
                continue
            for s in tri(Fc, dim - 1):
                out.append((v0,) + s)
        return out

    total = Fraction(0)
    for simp in tri(frozenset(idx), k):
        p0 = cmap[simp[0]]
        Mtx = [[cmap[simp[t + 1]][j] - p0[j] for j in range(k)] for t in range(k)]
        total += abs(det_frac(Mtx))
    return total


def lambda_vector(c, V=None):
    """Q^342 vector of ridge normalized volumes, indexed by PAIR_TYPES."""
    if V is None:
        V = vertices(c)
    T = tight_sets(V, c)
    F = facets(V, c, T)
    Rg = ridges(V, c, T, F)
    lam = [Fraction(0)] * len(PAIR_TYPES)
    for (i, j), S in Rg.items():
        key = (i, j) if i < j else (j, i)
        if key not in PAIR_INDEX:
            raise RuntimeError('ridge with antiparallel normals %s' % (key,))
        lam[PAIR_INDEX[key]] += relvol(V, S, T)
    return lam, V, T, F, Rg
