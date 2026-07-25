"""H2_core.py -- exact arc-cut evaluator for the circle graph Gamma.

Gamma: circle R/Z, x ~ y iff circular distance d(x,y) > 1/3.
Gamma_m: m equally spaced points i/m; i ~ j iff 3*min(|i-j|, m-|i-j|) > m.

For an integer (or Fraction) weight vector w on Gamma_m:
  W(w)         = sum over edges uv of w_u w_v            (total adjacent mass)
  mono(A,w)    = sum over edges uv with u,v on the same side of A
  ARCBOUND(w)  = min over CYCLIC INTERVALS A of mono(A,w)
  S(w)         = sum w

Conjectures under attack:
  ARC   :  25 * ARCBOUND(w)          <= S(w)^2
  WSQ   :  ARCBOUND(w) * S(w)^2      <= W(w)^2

All arithmetic here is exact (python ints / Fractions).
"""
from fractions import Fraction
from itertools import product


def adj_matrix(m):
    """Adjacency list of Gamma_m as list of sets."""
    A = [set() for _ in range(m)]
    for i in range(m):
        for j in range(i + 1, m):
            d = min(j - i, m - (j - i))
            if 3 * d > m:
                A[i].add(j)
                A[j].add(i)
    return A


def edges(m):
    A = adj_matrix(m)
    return [(i, j) for i in range(m) for j in A[i] if i < j]


def adj_general(pos):
    """Adjacency for arbitrary positions on the circle given as Fractions in [0,1).
    Returns list of sets. i ~ j iff circular distance > 1/3 (strict)."""
    k = len(pos)
    A = [set() for _ in range(k)]
    for i in range(k):
        for j in range(i + 1, k):
            d = abs(pos[i] - pos[j])
            d = min(d, 1 - d)
            if 3 * d > 1:
                A[i].add(j)
                A[j].add(i)
    return A


def total_W(w, E):
    return sum(w[i] * w[j] for (i, j) in E)


def mono_of_arc(w, E, inA):
    """mono for the indicator list inA (bool per vertex)."""
    return sum(w[i] * w[j] for (i, j) in E if inA[i] == inA[j])


def arcbound(w, E, k=None, return_arc=False):
    """min over cyclic intervals [s, s+L) of mono.  O(k^2 * |E|) -- reference impl."""
    if k is None:
        k = len(w)
    best = None
    besta = None
    for s in range(k):
        inA = [False] * k
        for L in range(0, k + 1):
            if L > 0:
                inA[(s + L - 1) % k] = True
            v = mono_of_arc(w, E, inA)
            if best is None or v < best:
                best = v
                besta = (s, L)
            if L == k:
                break
    if return_arc:
        return best, besta
    return best


def arcbound_fast(w, E, k, return_arc=False):
    """Incremental O(k^2 + k*|E|) evaluation via mono(A) = W - cut(A)."""
    nbr = [[] for _ in range(k)]
    for (i, j) in E:
        nbr[i].append(j)
        nbr[j].append(i)
    W = total_W(w, E)
    best = W          # empty arc
    besta = (0, 0)
    for s in range(k):
        dA = [0] * k          # dA[v] = weighted adjacency of v into current A
        cut = 0
        for L in range(1, k + 1):
            j = (s + L - 1) % k
            Dj = sum(w[t] for t in nbr[j])
            cut += w[j] * (Dj - 2 * dA[j])
            for t in nbr[j]:
                dA[t] += w[j]
            v = W - cut
            if v < best:
                best = v
                besta = (s, L)
    if return_arc:
        return best, besta
    return best


def psi_full(w, E, k):
    """min over ALL cuts (2^(k-1)) of mono -- only for small k."""
    best = None
    for mask in range(1 << (k - 1)):
        inA = [bool((mask >> i) & 1) for i in range(k - 1)] + [False]
        v = mono_of_arc(w, E, inA)
        if best is None or v < best:
            best = v
    return best


def report(w, m=None, E=None, name=""):
    k = len(w)
    if E is None:
        E = edges(m if m is not None else k)
    W = total_W(w, E)
    S = sum(w)
    ab, arc = arcbound_fast(w, E, k, return_arc=True)
    ab2 = arcbound(w, E, k)
    assert ab == ab2, (ab, ab2)
    arc_ok = 25 * ab <= S * S
    wsq_ok = ab * S * S <= W * W
    return dict(name=name, k=k, w=list(w), S=S, W=W, ARCBOUND=ab, arc=arc,
                arc_ratio=Fraction(25 * ab, S * S) if S else None,
                wsq_ratio=(Fraction(ab * S * S, W * W) if W else None),
                ARC_ok=arc_ok, WSQ_ok=wsq_ok)


if __name__ == "__main__":
    for m in [5, 7, 8, 9, 10, 11, 13, 14, 16, 17, 19, 20, 22, 23, 25, 26, 28, 29, 31]:
        r = report([1] * m, m=m, name=f"uniform Gamma_{m}")
        print(f"m={m:3d} deg={2*len(edges(m))//m if m else 0:2d} W={r['W']:5d} "
              f"AB={r['ARCBOUND']:5d} S^2={r['S']**2:5d} "
              f"25AB/S^2={float(r['arc_ratio']):.6f} AB*S^2/W^2={float(r['wsq_ratio']):.6f} "
              f"ARC={'ok' if r['ARC_ok'] else 'VIOLATED'} WSQ={'ok' if r['WSQ_ok'] else 'VIOLATED'}")
