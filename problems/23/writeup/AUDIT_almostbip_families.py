#!/usr/bin/env python3
"""Almost-bipartite family generators for the T_uniform GPI test.
Idea: bipartite base B0 (even cycle, grid, tree) + a FEW added edges that close LONG odd cycles
=> few bad edges, large ell (ell^2 dominates Gamma), few shortest cycles (uniform-split concentrates load)."""
import random

def even_cycle(L):
    """Even cycle C_{2L}: vertices 0..2L-1."""
    n = 2 * L
    E = [(i, (i + 1) % n) for i in range(n)]
    return n, E

def even_cycle_plus_chord(L, a, b):
    """C_{2L} + chord (a,b). Chord parity even=>still bipartite-ish; odd=>creates an odd cycle.
    For a long odd cycle we want a,b with even index difference (the two arcs split into even/odd)."""
    n, E = even_cycle(L)
    E = list(E) + [(a % n, b % n)]
    return n, E

def two_even_cycles_bridge(L1, L2):
    """Two even cycles sharing... actually build a theta-like graph: even cycle + a long path chord."""
    n = 2 * L1
    E = [(i, (i + 1) % n) for i in range(n)]
    return n, list(E)

def long_odd_cycle(L):
    """A single odd cycle C_{2L+1}: itself is the bad structure (1 bad edge, ell=2L+1)."""
    n = 2 * L + 1
    E = [(i, (i + 1) % n) for i in range(n)]
    return n, E

def grid(r, c):
    """r x c grid graph (bipartite)."""
    def vid(i, j): return i * c + j
    n = r * c
    E = []
    for i in range(r):
        for j in range(c):
            if j + 1 < c: E.append((vid(i, j), vid(i, j + 1)))
            if i + 1 < r: E.append((vid(i, j), vid(i + 1, j)))
    return n, E

def grid_plus_edge(r, c, e):
    n, E = grid(r, c)
    return n, list(E) + [e]

def subdivide(n, E, edge_idx_to_sub, times):
    """Subdivide chosen edges 'times' times each (each subdivision adds one vertex, raising path length)."""
    E = [tuple(x) for x in E]
    nxt = n
    out = []
    for idx, (u, v) in enumerate(E):
        if idx in edge_idx_to_sub:
            chain = [u]
            for _ in range(times):
                chain.append(nxt); nxt += 1
            chain.append(v)
            for k in range(len(chain) - 1):
                out.append((chain[k], chain[k + 1]))
        else:
            out.append((u, v))
    return nxt, out

def theta_graph(a, b, c):
    """Theta graph: two endpoints joined by 3 internally-disjoint paths of lengths a,b,c (edges).
    Bipartite iff all path-lengths same parity. Pick parities to make exactly one/few odd cycles, long."""
    # endpoints 0 and 1
    n = 2
    E = []
    def add_path(length):
        nonlocal n
        prev = 0
        for _ in range(length - 1):
            cur = n; n += 1
            E.append((prev, cur)); prev = cur
        E.append((prev, 1))
    add_path(a); add_path(b); add_path(c)
    return n, E

def prism_subdivided(L):
    """Two cycles connected (Mobius-Kantor-ish). Build a long even cycle, add one long chord making big odd cycle."""
    n, E = even_cycle(L)
    # add chord between 0 and L (diametric). 0..L is a path of length L; the cycle 0-...-L-0 has length L+1.
    E = list(E) + [(0, L % n)]
    return n, E
