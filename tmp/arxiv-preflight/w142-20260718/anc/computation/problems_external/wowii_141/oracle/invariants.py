#!/usr/bin/env python3
"""Exact invariants for WOWII / Graffiti.pc conjectures 141, 142, 144, 145, 146,
implemented FAITHFULLY to the formalizations in google-deepmind/formal-conjectures
(local clone formal-conjectures-w143, files read 2026-07-18):

  FormalConjectures/WrittenOnTheWallII/GraphConjecture{141,142,144,145,146}.lean
  FormalConjecturesForMathlib/Combinatorics/SimpleGraph/{Independence,VertexDistance,
    Eccentricity,LargestInducedTree}.lean
  .lake/packages/mathlib/Mathlib/Combinatorics/SimpleGraph/{Diam,Girth}.lean

EXACT Lean statements being tested (all with [Fintype alpha] [DecidableEq alpha]
[Nontrivial alpha]  -- so |V| >= 2 -- and hypothesis h : G.Connected):

C141 (ints; `(G.girth / 2 : Z)` is floor division of the nonneg girth, identical
      to Nat division):
      girth(G)/2 - 1 + max_{v in V} indepNeighborsCard(G,v)  <=  tree(G)

C142 (reals; exact rationals here):
      B := maxEccentricityVertices G = { v | eccent(v) = ediam(G) }   (periphery)
      (2/3) * girth(G) + eccSet(G, B)  <=  tree(G)

C144 (reals; integer-valued):
      girth(G) - 1 + ecc(G, G.center)  <=  tree(G)
      where Mathlib center = { u | eccent(u) = radius(G) } (min-eccentricity set)
      and FC `ecc G S` = max over v NOT IN S of distToSet(v,S), and := 0 if S = univ.

C145 (nats; extra hypothesis hlMin : 0 < localIndependenceMin (complement G)):
      2 * eccSet(G, maxEccentricityVertices G)
        <=  tree(G) * localIndependenceMin(complement G)
      localIndependenceMin H = min_v indepNeighborsCard(H, v).

C146 (nats; extra hypothesis hrad : 0 < graphSquareRadius G, automatic for
      connected |V|>=2):
      2 * eccSet(G, maxEccentricityVertices G)  <=  tree(G) * graphSquareRadius(G)
      graphSquare G: u ~ v iff u != v and dist_G(u,v) <= 2;
      graphSquareRadius = (radius of G^2).toNat.

Definition conventions (verified against the Lean sources):
 * girth : N = egirth.toNat = length of shortest cycle, 0 if acyclic.
 * tree(G) = largestInducedTreeSize G = sSup { n | exists Finset s, |s| = n and
   (G.induce s).IsTree }.  Mathlib IsTree = Connected AND IsAcyclic; Connected
   requires Nonempty, so the EMPTY set does NOT induce a tree but singletons do
   (tree(G) >= 1 always).
 * indepNeighborsCard G v = independence number of induced subgraph on the OPEN
   neighborhood N(v).
 * distToSet G v S = min_{s in S} dist(v,s), 0 if S empty (S nonempty in all uses;
   graphs connected so Mathlib dist is the genuine BFS distance).
 * ecc G S  = max_{v not in S} distToSet(v,S); 0 if S = univ.
 * eccSet G S = max over ALL v of distToSet(v,S)  (members of S contribute 0).
   Note ecc(G,S) == eccSet(G,S) for every S (members contribute 0 to the max and
   both degenerate cases give 0); both are implemented independently anyway.

Graphs are given as (n, adj) where adj is a list of n int bitmasks.
Everything is exact integer / Fraction arithmetic - no floats, no heuristics.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Optional
import sys

sys.setrecursionlimit(100000)


# ----------------------------------------------------------------------------
# basic graph machinery (bitmask representation)
# ----------------------------------------------------------------------------

def nx_to_bitadj(graph) -> tuple[int, list[int]]:
    """Convert a networkx graph (arbitrary hashable nodes) to (n, adj bitmasks)."""
    nodes = sorted(graph.nodes())
    idx = {u: i for i, u in enumerate(nodes)}
    n = len(nodes)
    adj = [0] * n
    for u, v in graph.edges():
        iu, iv = idx[u], idx[v]
        if iu == iv:
            raise ValueError("self-loop encountered; SimpleGraph forbids loops")
        adj[iu] |= 1 << iv
        adj[iv] |= 1 << iu
    return n, adj


def is_connected_mask(adj: list[int], mask: int) -> bool:
    """Is the induced subgraph on `mask` connected (and nonempty)?"""
    if mask == 0:
        return False
    start = mask & -mask
    reached = start
    frontier = start
    while frontier:
        new = 0
        f = frontier
        while f:
            b = f & -f
            f ^= b
            new |= adj[b.bit_length() - 1]
        new &= mask & ~reached
        reached |= new
        frontier = new
    return reached == mask


def edges_in_mask(adj: list[int], mask: int) -> int:
    total = 0
    m = mask
    while m:
        b = m & -m
        m ^= b
        total += (adj[b.bit_length() - 1] & mask).bit_count()
    return total // 2


def graph_connected(n: int, adj: list[int]) -> bool:
    return is_connected_mask(adj, (1 << n) - 1)


def all_pairs_dist(n: int, adj: list[int]) -> list[list[int]]:
    """BFS all-pairs distances; -1 for unreachable (callers assume connected)."""
    dist = [[-1] * n for _ in range(n)]
    for s in range(n):
        row = dist[s]
        row[s] = 0
        frontier = 1 << s
        reached = frontier
        d = 0
        while frontier:
            d += 1
            new = 0
            f = frontier
            while f:
                b = f & -f
                f ^= b
                new |= adj[b.bit_length() - 1]
            new &= ~reached
            reached |= new
            frontier = new
            f = new
            while f:
                b = f & -f
                f ^= b
                row[b.bit_length() - 1] = d
    return dist


# ----------------------------------------------------------------------------
# girth  (Mathlib: egirth.toNat, 0 if acyclic)
# ----------------------------------------------------------------------------

def girth(n: int, adj: list[int]) -> int:
    """Length of shortest cycle; 0 if acyclic.

    Exact edge-deletion method: every shortest cycle uses some edge (u,v); with
    that edge removed, dist(u,v)+1 is that cycle's length, and every dist+1
    found is a genuine cycle length.  Min over all edges = girth."""
    best: Optional[int] = None
    for u in range(n):
        au = adj[u]
        m = au
        while m:
            b = m & -m
            m ^= b
            v = b.bit_length() - 1
            if v <= u:
                continue
            # BFS from u to v in G - uv
            adj_u = adj[u] & ~(1 << v)
            adj_v = adj[v] & ~(1 << u)

            def nbr(w: int) -> int:
                if w == u:
                    return adj_u
                if w == v:
                    return adj_v
                return adj[w]

            frontier = 1 << u
            reached = frontier
            d = 0
            found = -1
            while frontier and found < 0:
                d += 1
                new = 0
                f = frontier
                while f:
                    bb = f & -f
                    f ^= bb
                    new |= nbr(bb.bit_length() - 1)
                new &= ~reached
                if new & (1 << v):
                    found = d
                reached |= new
                frontier = new
            if found > 0:
                c = found + 1
                if best is None or c < best:
                    best = c
    return best if best is not None else 0


# ----------------------------------------------------------------------------
# largest induced tree  (FC largestInducedTreeSize)
# ----------------------------------------------------------------------------

def _greedy_tree_lower_bound(n: int, adj: list[int]) -> int:
    """Cheap induced-tree lower bound: grow sets keeping 'exactly one neighbor
    inside' additions (each addition keeps the induced subgraph a tree)."""
    best = 1
    for start in range(n):
        mask = 1 << start
        changed = True
        while changed:
            changed = False
            for v in range(n):
                bit = 1 << v
                if mask & bit:
                    continue
                if (adj[v] & mask).bit_count() == 1:
                    mask |= bit
                    changed = True
        sz = mask.bit_count()
        if sz > best:
            best = sz
    return best


def largest_induced_tree(n: int, adj: list[int]) -> tuple[int, int]:
    """Return (size, witness_mask) of a maximum induced tree.

    Exhaustive over all 2^n - 1 nonempty vertex subsets: induced subgraph is a
    tree iff connected and #edges = |S| - 1.  Greedy seed only raises the skip
    bar; exhaustiveness is unaffected (only subsets with size <= current best
    are skipped, and a valid tree of the greedy size is already in hand)."""
    best = _greedy_tree_lower_bound(n, adj)
    # recover a witness for the greedy bound
    witness = None
    for start in range(n):
        mask = 1 << start
        changed = True
        while changed:
            changed = False
            for v in range(n):
                bit = 1 << v
                if not (mask & bit) and (adj[v] & mask).bit_count() == 1:
                    mask |= bit
                    changed = True
        if mask.bit_count() == best:
            witness = mask
            break
    if witness is None:  # pragma: no cover - greedy always yields its own witness
        witness = 1
        best = 1
    for mask in range(1, 1 << n):
        if mask.bit_count() <= best:
            continue
        if not is_connected_mask(adj, mask):
            continue
        k = mask.bit_count()
        if edges_in_mask(adj, mask) == k - 1:
            best = k
            witness = mask
    return best, witness


# ----------------------------------------------------------------------------
# independence number on a vertex mask (exact branch & bound)
# ----------------------------------------------------------------------------

def mis_size(adj: list[int], mask: int) -> int:
    """Exact maximum independent set size of the induced subgraph on `mask`."""
    if mask == 0:
        return 0
    # pick a vertex of maximum degree within mask
    vbest, dbest = -1, -1
    m = mask
    while m:
        b = m & -m
        m ^= b
        v = b.bit_length() - 1
        d = (adj[v] & mask).bit_count()
        if d > dbest:
            dbest = d
            vbest = v
    if dbest == 0:
        return mask.bit_count()
    bit = 1 << vbest
    # include vbest
    inc = 1 + mis_size(adj, mask & ~bit & ~adj[vbest])
    # exclude vbest
    exc = mis_size(adj, mask & ~bit)
    return inc if inc >= exc else exc


def indep_neighbors_card(n: int, adj: list[int], v: int) -> int:
    """FC indepNeighborsCard: independence number of G[N(v)]."""
    return mis_size(adj, adj[v])


def complement_adj(n: int, adj: list[int]) -> list[int]:
    full = (1 << n) - 1
    return [(~adj[v]) & full & ~(1 << v) for v in range(n)]


def local_independence_min(n: int, adj: list[int]) -> int:
    """FC localIndependenceMin: min over v of indepNeighborsCard."""
    return min(indep_neighbors_card(n, adj, v) for v in range(n))


# ----------------------------------------------------------------------------
# eccentricities, center, periphery, set-distances (FC/Mathlib conventions)
# ----------------------------------------------------------------------------

def eccentricities(n: int, dist: list[list[int]]) -> list[int]:
    return [max(dist[v]) for v in range(n)]


def dist_to_set(dist: list[list[int]], v: int, s_mask: int) -> int:
    """FC distToSet: min over s in S of dist(v,s); 0 if S empty."""
    if s_mask == 0:
        return 0
    best = None
    m = s_mask
    while m:
        b = m & -m
        m ^= b
        d = dist[v][b.bit_length() - 1]
        if best is None or d < best:
            best = d
    return best


def ecc_of_set(n: int, dist: list[list[int]], s_mask: int) -> int:
    """FC `ecc`: max over v NOT in S of distToSet(v,S); 0 if S = univ."""
    comp = ((1 << n) - 1) & ~s_mask
    if comp == 0:
        return 0
    best = 0
    m = comp
    while m:
        b = m & -m
        m ^= b
        d = dist_to_set(dist, b.bit_length() - 1, s_mask)
        if d > best:
            best = d
    return best


def ecc_set(n: int, dist: list[list[int]], s_mask: int) -> int:
    """FC `eccSet`: max over ALL v of distToSet(v,S)."""
    best = 0
    for v in range(n):
        d = dist_to_set(dist, v, s_mask)
        if d > best:
            best = d
    return best


def graph_square_adj(n: int, dist: list[list[int]]) -> list[int]:
    """FC graphSquare: u ~ v iff u != v and dist(u,v) <= 2 (G connected here)."""
    adj2 = [0] * n
    for u in range(n):
        for v in range(u + 1, n):
            if 0 <= dist[u][v] <= 2:
                adj2[u] |= 1 << v
                adj2[v] |= 1 << u
    return adj2


# ----------------------------------------------------------------------------
# full invariant bundle + the five conjecture checks
# ----------------------------------------------------------------------------

def compute_all(n: int, adj: list[int]) -> dict:
    """All invariants needed by conjectures 141/142/144/145/146.
    Requires G connected and n >= 2 (the Lean hypotheses)."""
    assert n >= 2, "Nontrivial alpha requires n >= 2"
    assert graph_connected(n, adj), "conjectures assume G.Connected"
    dist = all_pairs_dist(n, adj)
    ecc_v = eccentricities(n, dist)
    ediam = max(ecc_v)
    radius = min(ecc_v)
    center_mask = 0
    periph_mask = 0
    for v in range(n):
        if ecc_v[v] == radius:
            center_mask |= 1 << v
        if ecc_v[v] == ediam:
            periph_mask |= 1 << v
    g = girth(n, adj)
    tree_sz, tree_witness = largest_induced_tree(n, adj)
    l_vals = [indep_neighbors_card(n, adj, v) for v in range(n)]
    cadj = complement_adj(n, adj)
    lmin_comp = min(mis_size(cadj, cadj[v]) for v in range(n))
    adj2 = graph_square_adj(n, dist)
    dist2 = all_pairs_dist(n, adj2)
    ecc2 = eccentricities(n, dist2)
    rad_square = min(ecc2)  # finite: G connected => G^2 connected
    return {
        "n": n,
        "m": sum(a.bit_count() for a in adj) // 2,
        "girth": g,
        "tree": tree_sz,
        "tree_witness_mask": tree_witness,
        "l_values": l_vals,
        "max_l": max(l_vals),
        "radius": radius,
        "ediam": ediam,
        "center_mask": center_mask,
        "periphery_mask": periph_mask,
        "ecc_center": ecc_of_set(n, dist, center_mask),
        "eccSet_periphery": ecc_set(n, dist, periph_mask),
        "lmin_complement": lmin_comp,
        "graphSquareRadius": rad_square,
    }


def check_conjectures(inv: dict) -> dict:
    """Evaluate the five FC statements exactly.  Each entry:
    {holds, lhs, rhs, slack} with slack = rhs - lhs (Fraction for 142)."""
    g = inv["girth"]
    tree = inv["tree"]
    out = {}

    # C141: girth/2 - 1 + max_l <= tree   (integer floor division)
    lhs141 = g // 2 - 1 + inv["max_l"]
    out["c141"] = {"holds": lhs141 <= tree, "lhs": lhs141, "rhs": tree,
                   "slack": tree - lhs141}

    # C142: (2/3)*girth + eccSet(periphery) <= tree   (exact rationals)
    lhs142 = Fraction(2, 3) * g + inv["eccSet_periphery"]
    out["c142"] = {"holds": lhs142 <= tree, "lhs": str(lhs142), "rhs": tree,
                   "slack": str(Fraction(tree) - lhs142)}

    # C144: girth - 1 + ecc(center) <= tree
    lhs144 = g - 1 + inv["ecc_center"]
    out["c144"] = {"holds": lhs144 <= tree, "lhs": lhs144, "rhs": tree,
                   "slack": tree - lhs144}

    # C145: (0 < lMin(G^c))  ->  2*eccSet(periphery) <= tree * lMin(G^c)
    lmin = inv["lmin_complement"]
    hyp145 = lmin > 0
    lhs145 = 2 * inv["eccSet_periphery"]
    rhs145 = tree * lmin
    out["c145"] = {"hypothesis": hyp145,
                   "holds": (not hyp145) or lhs145 <= rhs145,
                   "lhs": lhs145, "rhs": rhs145, "slack": rhs145 - lhs145}

    # C146: (0 < rad(G^2))  ->  2*eccSet(periphery) <= tree * rad(G^2)
    rad2 = inv["graphSquareRadius"]
    hyp146 = rad2 > 0
    lhs146 = 2 * inv["eccSet_periphery"]
    rhs146 = tree * rad2
    out["c146"] = {"hypothesis": hyp146,
                   "holds": (not hyp146) or lhs146 <= rhs146,
                   "lhs": lhs146, "rhs": rhs146, "slack": rhs146 - lhs146}
    return out
