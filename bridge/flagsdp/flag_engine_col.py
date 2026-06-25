#!/usr/bin/env python3
"""
2-vertex-colored flag-algebra engine (Phase C), built on flag_engine.
Colored graph = (n, A, col) with col a tuple in {0,1}^n (the two max-cut sides).
Colored iso = adjacency- AND color-preserving bijection.  Canonical form = lex-min of the
(color-tuple, upper-edge-tuple) signature over relabelings fixing the first `roots` vertices.
Triangle-freeness ignores color.  Edges are MONO (both endpoints same color, count toward beta)
or CUT (endpoints differ).
"""
import itertools
import flag_engine as fe


def relabel_col(n, A, col, perm):
    B = fe.relabel(n, A, perm)
    cp = [0]*n
    for i in range(n):
        cp[perm[i]] = col[i]
    return B, tuple(cp)

def sig_col(n, A, col):
    return (tuple(col), fe._bits_upper(n, A))

def canonical_col(n, A, col, roots=0):
    """Lex-min (col, edges) signature over relabelings fixing first `roots` vertices."""
    best = None
    free = list(range(roots, n))
    for p in itertools.permutations(free):
        perm = list(range(roots)) + list(p)
        B, cp = relabel_col(n, A, col, perm)
        key = sig_col(n, B, cp)
        if best is None or key < best:
            best = key
    return best

def from_key_col(n, key):
    col, ebits = key
    A = fe.graph_from_key(n, ebits)
    return (n, A, list(col))

def induced_col(A, col, verts):
    k, B = fe.induced(A, verts)
    cc = tuple(col[v] for v in verts)
    return k, B, cc

def _aut_group(n, A):
    """Automorphism group of (n,A) as a list of permutations (perm[i] = image of i). Brute, small n."""
    auts = []
    for perm in itertools.permutations(range(n)):
        if fe.relabel(n, A, list(perm)) == A:
            auts.append(perm)
    return auts

def enumerate_colored(n, triangle_free=True):
    """All 2-colored triangle-free graphs on n vertices up to colored iso. Returns [(n,A,col)].
    Fast: for each uncolored graph G, enumerate colorings up to Aut(G) (orbit reps)."""
    out = []
    for (_, A) in fe.enumerate_graphs(n, triangle_free=triangle_free):
        auts = _aut_group(n, A)
        seen_col = set()
        for cbits in itertools.product((0, 1), repeat=n):
            # canonical coloring under Aut(G): min over auts of (relabeled coloring)
            best = None
            for perm in auts:
                cprime = [0]*n
                for i in range(n):
                    cprime[perm[i]] = cbits[i]
                t = tuple(cprime)
                if best is None or t < best:
                    best = t
            if best not in seen_col:
                seen_col.add(best)
                out.append((n, list(A), list(best)))
    return out

def induced_density_col(small, big):
    """p(small; big) for colored graphs. small=(k,As,cs) canonicalized; big=(n,Ab,cb)."""
    k, As, cs = small; n, Ab, cb = big
    if k > n: return 0.0
    target = canonical_col(k, As, cs)
    cnt = 0; tot = 0
    for verts in itertools.combinations(range(n), k):
        kk, B, cc = induced_col(Ab, cb, list(verts))
        tot += 1
        if canonical_col(kk, B, cc) == target:
            cnt += 1
    return cnt / tot if tot else 0.0


# convenience colored small graphs
def mono_edge():   # both endpoints color 0 (a monochromatic edge; by symmetry color 1 same class only if swap allowed)
    return (2, fe.adj_from_edges(2, [(0,1)]), (0,0))
def mono_edge_11():
    return (2, fe.adj_from_edges(2, [(0,1)]), (1,1))
def cut_edge():
    return (2, fe.adj_from_edges(2, [(0,1)]), (0,1))


if __name__ == "__main__":
    print("=== colored engine self-test ===")
    # number of 2-colored triangle-free graphs up to colored iso (sanity: grows from uncolored counts)
    for n in range(1, 6):
        c = len(enumerate_colored(n, True))
        print(f"  n={n}: 2-colored triangle-free up to iso = {c}")
    # density check: a properly 2-colored C5 is impossible (C5 not bipartite); test a bipartite C6
    C6 = (6, fe.adj_from_edges(6, [(i,(i+1)%6) for i in range(6)]))
    col_bip = (0,1,0,1,0,1)  # proper 2-coloring -> all edges CUT, 0 mono
    big = (6, C6[1], col_bip)
    dm0 = induced_density_col(mono_edge(), big)
    dm1 = induced_density_col(mono_edge_11(), big)
    dc = induced_density_col(cut_edge(), big)
    print(f"  bipartite C6 (proper 2-col): mono00={dm0} mono11={dm1} cut={dc}  (expect mono=0, cut=6/15=0.4)")
    # all edges mono: color C6 all one color
    big2 = (6, C6[1], (0,0,0,0,0,0))
    print(f"  C6 all color-0: mono00={induced_density_col(mono_edge(), big2)} cut={induced_density_col(cut_edge(), big2)} (expect mono=0.4, cut=0)")
    # beta density consistency: mono00+mono11+cut total edge density = edge density
    tot = dm0+dm1+dc
    print(f"  C6 bip: mono00+mono11+cut = {tot}  (= edge density 0.4)  {'OK' if abs(tot-0.4)<1e-9 else 'BAD'}")
    print("DONE")
