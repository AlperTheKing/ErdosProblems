"""R9: odd-K5 minor decider for signed graphs (G, Sigma) with Sigma = E(G) (all edges odd).

CRITERION (derived, then validated against known answers).
An odd-K5 minor is a family of 5 disjoint vertex sets V_1..V_5, each inducing a CONNECTED
BIPARTITE subgraph, pairwise joined by at least one edge, together with a choice of one
joining edge per pair, such that the contracted signed K5 is switching-equivalent to the
all-odd K5.  With d_i : V_i -> {0,1} the (unique up to flip) proper 2-colouring of G[V_i],
the sign of the minor edge {i,j} realised by the joining edge ab (a in V_i, b in V_j) is
        sigma_ij = 1 + d_i(a) + d_j(b)   (mod 2),
because a cycle of the minor pulls back to a cycle of G whose length is the number of
joining edges plus the parities of the traversed paths inside the branch sets.
A signed K5 is switching-equivalent to the all-odd K5 iff every one of its 10 triangles is
odd, i.e. iff there is eps in GF(2)^5 with sigma_ij = 1 + eps_i + eps_j for all i<j
(the flip of eps_i is exactly the flip of the reference colour of d_i).
So: for each pair let S_ij = { 1 + d_i(a) + d_j(b) : ab a joining edge } subset of {0,1};
an odd-K5 minor exists on this branch family iff some eps in GF(2)^5 has
1 + eps_i + eps_j in S_ij for every pair.
"""
from itertools import combinations
from R9_oddk5_lib import G, g6_decode, Cn
import sys

def connected_bipartite_subsets(g, maxsize=None):
    """all subsets inducing a connected bipartite subgraph, with their 2-colouring."""
    n = g.n
    out = []
    for mask in range(1, 1 << n):
        if maxsize and bin(mask).count('1') > maxsize:
            continue
        vs = [v for v in range(n) if (mask >> v) & 1]
        col = {}
        start = vs[0]
        col[start] = 0
        st = [start]
        ok = True
        while st and ok:
            v = st.pop()
            for u in g.adj[v]:
                if not ((mask >> u) & 1):
                    continue
                if u not in col:
                    col[u] = 1 - col[v]
                    st.append(u)
                elif col[u] == col[v]:
                    ok = False
                    break
        if ok and len(col) == len(vs):
            out.append((mask, col))
    return out

def has_odd_k5_minor(g, want_witness=False, maxbranch=None):
    n = g.n
    cbs = connected_bipartite_subsets(g, maxbranch)
    nbrmask = [0] * n
    for (a, b) in g.E:
        nbrmask[a] |= 1 << b
        nbrmask[b] |= 1 << a
    # neighbourhood mask of a set
    setnbr = {}
    for (mask, col) in cbs:
        nb = 0
        for v in range(n):
            if (mask >> v) & 1:
                nb |= nbrmask[v]
        setnbr[mask] = nb & ~mask
    cbs.sort(key=lambda t: bin(t[0]).count('1'))
    L = len(cbs)
    idx = {cbs[i][0]: i for i in range(L)}

    def pairsig(m1, c1, m2, c2):
        s = set()
        for v in range(n):
            if (m1 >> v) & 1:
                for u in g.adj[v]:
                    if (m2 >> u) & 1:
                        s.add((1 + c1[v] + c2[u]) % 2)
        return s

    res = [None]
    chosen = []

    def rec(start):
        if len(chosen) == 5:
            S = {}
            for a in range(5):
                for b in range(a + 1, 5):
                    ma, ca = cbs[chosen[a]]
                    mb, cb = cbs[chosen[b]]
                    S[(a, b)] = pairsig(ma, ca, mb, cb)
            for eps in range(32):
                good = True
                for a in range(5):
                    for b in range(a + 1, 5):
                        want = (1 + ((eps >> a) & 1) + ((eps >> b) & 1)) % 2
                        if want not in S[(a, b)]:
                            good = False
                            break
                    if not good:
                        break
                if good:
                    res[0] = [cbs[c][0] for c in chosen]
                    return True
            return False
        used = 0
        for c in chosen:
            used |= cbs[c][0]
        for i in range(start, L):
            m, col = cbs[i]
            if m & used:
                continue
            # must be adjacent to every already chosen set
            ok = True
            for c in chosen:
                if not (setnbr[cbs[c][0]] & m):
                    ok = False
                    break
            if not ok:
                continue
            chosen.append(i)
            if rec(i + 1):
                return True
            chosen.pop()
        return False

    found = rec(0)
    if want_witness:
        return found, (res[0] if found else None)
    return found

def bits(mask):
    return [i for i in range(mask.bit_length()) if (mask >> i) & 1]

if __name__ == "__main__":
    pet = G(10, [(i, (i + 1) % 5) for i in range(5)] + [(i, i + 5) for i in range(5)] +
           [(5 + i, 5 + (i + 2) % 5) for i in range(5)])
    v8 = G(8, [(i, (i + 1) % 8) for i in range(8)] + [(i, i + 4) for i in range(4)])
    def circ(m, k):   # Gamma_m : u~v iff k*circdist(u,v) > m   (And(k) = Gamma_{3k-1})
        E = []
        for u in range(m):
            for v in range(u + 1, m):
                d = min(v - u, m - (v - u))
                if k * d > m:
                    E.append((u, v))
        return G(m, E)
    g11 = circ(11, 3)      # And(4)
    def blowup(g, t):
        E = []
        for (a, b) in g.E:
            for i in range(t):
                for j in range(t):
                    E.append((a * t + i, b * t + j))
        return G(g.n * t, E)
    tests = [("C5", Cn(5)), ("Wagner V8 = And(3)", v8), ("C5[2]", blowup(Cn(5), 2)),
             ("Petersen", pet), ("Gamma_11 = And(4)", g11)]
    for nm, g in tests:
        f, w = has_odd_k5_minor(g, want_witness=True)
        print(f"{nm:22s} n={g.n:3d} m={g.m:3d} tf={g.triangle_free()}  odd-K5 minor: "
              f"{'YES' if f else 'NO '}", ("branch sets " + str([bits(x) for x in w])) if f else "")
        sys.stdout.flush()
