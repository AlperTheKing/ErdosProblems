"""Exact switching-loss library for Erdos #23 (family F2).

Conventions.  G = simple graph, cut = subset V0 of V (side 0); side 1 = V \ V0.
  B = crossing edges, M = monochromatic edges,  bip-value of the cut = |M|.
  For S subset V:  sigma(S) = #{B-edges with exactly one end in S}
                            - #{M-edges with exactly one end in S}
                = (decrease of the cut size when S is switched).
  The cut is maximum  <=>  sigma(S) >= 0 for every S.
All arithmetic is integer.
"""
from itertools import combinations


def edges_of(adj):
    n = len(adj)
    return [(u, v) for u in range(n) for v in adj[u] if u < v]


def cut_status(E, side):
    """Return (B, M) lists of edges for the 0/1 vector `side`."""
    B = [e for e in E if side[e[0]] != side[e[1]]]
    M = [e for e in E if side[e[0]] == side[e[1]]]
    return B, M


def sigma(S, B, M):
    """Exact switching loss of the vertex set S (a frozenset/set of ints)."""
    s = 0
    for (u, v) in B:
        if (u in S) != (v in S):
            s += 1
    for (u, v) in M:
        if (u in S) != (v in S):
            s -= 1
    return s


def max_cut_brute(n, E):
    """Exact max cut by brute force over 2^(n-1) bipartitions.  Returns (maxcut, list of side-vectors)."""
    best = -1
    argbest = []
    for mask in range(1 << (n - 1)):          # fix vertex 0 on side 0
        side = [(mask >> i) & 1 for i in range(n - 1)]
        side = [0] + side
        c = sum(1 for (u, v) in E if side[u] != side[v])
        if c > best:
            best, argbest = c, [side]
        elif c == best:
            argbest.append(side)
    return best, argbest


def blowup(H_edges, h, n_parts):
    """Blow-up of H (h vertices, edge list) with part sizes n_parts.
    Returns (N, E, part_of) where part_of[v] = index of the part of v."""
    start = []
    tot = 0
    for i in range(h):
        start.append(tot)
        tot += n_parts[i]
    part_of = []
    for i in range(h):
        part_of += [i] * n_parts[i]
    E = []
    for (a, b) in H_edges:
        for x in range(start[a], start[a] + n_parts[a]):
            for y in range(start[b], start[b] + n_parts[b]):
                E.append((x, y) if x < y else (y, x))
    return tot, E, part_of


def all_subsets_sigma(N, B, M):
    """Iterate over all 2^N subsets, yielding (mask, sigma).  Only for tiny N."""
    for mask in range(1 << N):
        S = {i for i in range(N) if (mask >> i) & 1}
        yield mask, sigma(S, B, M)


def min_negative_set(N, B, M):
    """Smallest |S| with sigma(S) < 0 (None if the cut is maximum).  Brute force."""
    verts = list(range(N))
    for k in range(1, N + 1):
        for S in combinations(verts, k):
            if sigma(set(S), B, M) < 0:
                return k, S
    return None, None
