#!/usr/bin/env python3
"""
Max-cut SWITCHING constraints as colored-density functionals (Phase C, the global content).
Each returns a vector g over states with the valid constraint  sum_H x_H g(H) <= 0  for any
max-cut-colored graphon.

0-root family (2-vertex densities), p_v = a if col0 else b:
   (2a-2a^2) d_mono00 + (2b-2b^2) d_mono11 <= (a+b-2ab) d_cut.
   At (a,b)=(1/2,1/2): d_mono <= d_cut.

1-root SW1 (3-vertex densities), the GPT-verified switch S=P∪T at a color-c root v:
   e(P,R) + e(Q,T) <= e(R,T)   [the cubic survivor of |P|+e(P,R)+e(Q,T) <= e(R,T)]
   P=col-c nbrs of v, Q=other-col nbrs, R=col-c non-nbrs(≠v), T=other-col non-nbrs.
All terms are consistent-order colored-subgraph counts, so the weighted sum is a graphon density.
"""
import numpy as np


def _edges_between(A, X, Y):
    c = 0
    for u in X:
        Au = A[u]
        for w in Y:
            if (Au >> w) & 1:
                c += 1
    return c

def sw1_counts(states, root_color):
    g = []
    other = 1 - root_color
    for (n, A, col) in states:
        tot = 0
        for v in range(n):
            if col[v] != root_color:
                continue
            nbr = [(A[v] >> u) & 1 for u in range(n)]
            P = [u for u in range(n) if u != v and col[u] == root_color and nbr[u]]
            Q = [u for u in range(n) if u != v and col[u] == other and nbr[u]]
            R = [u for u in range(n) if u != v and col[u] == root_color and not nbr[u]]
            T = [u for u in range(n) if u != v and col[u] == other and not nbr[u]]
            tot += _edges_between(A, P, R) + _edges_between(A, Q, T) - _edges_between(A, R, T)
        g.append(float(tot))
    return np.array(g)

def sw0_counts(states, a, b):
    """(2a-2a^2) mono00 + (2b-2b^2) mono11 - (a+b-2ab) cut, as raw edge counts."""
    ca = 2*a - 2*a*a; cb = 2*b - 2*b*b; cc = a + b - 2*a*b
    g = []
    for (n, A, col) in states:
        m00 = m11 = cut = 0
        for u in range(n):
            for w in range(u+1, n):
                if (A[u] >> w) & 1:
                    if col[u] == 0 and col[w] == 0: m00 += 1
                    elif col[u] == 1 and col[w] == 1: m11 += 1
                    else: cut += 1
        g.append(ca*m00 + cb*m11 - cc*cut)
    return np.array(g)

def _adj_bits(A, w, R):
    return tuple(1 if (A[w] >> r) & 1 else 0 for r in R)

def rooted_switch_counts(states, sigma, pfunc):
    """General rooted-switch limit functional (density-consistent, <=0 for max cuts):
       g(H) = sum over ordered k-tuples R inducing sigma, sum over edges uv (u,v not in R) with
              exactly one of u,v in S_R, of chi(uv) [+1 mono, -1 cut],
       S_R = { non-root w : pfunc(col[w], adj(w,R)) == 1 }.
    sigma=(k,Asig,colsig); pfunc(color, adjbits-tuple)->0/1."""
    import itertools
    k, Asig, colsig = sigma
    g = []
    for (n, A, col) in states:
        tot = 0
        for R in itertools.permutations(range(n), k):
            ok = all(col[R[a]] == colsig[a] for a in range(k))
            if ok:
                for a in range(k):
                    for b in range(a+1, k):
                        e = (A[R[a]] >> R[b]) & 1
                        s = (Asig[a] >> b) & 1
                        if e != s: ok = False; break
                    if not ok: break
            if not ok:
                continue
            Rset = set(R)
            pval = [0.0]*n
            for w in range(n):
                if w in Rset: continue
                pval[w] = float(pfunc(col[w], _adj_bits(A, w, R)))
            for u in range(n):
                if u in Rset: continue
                Au = A[u]; pu = pval[u]
                for v in range(u+1, n):
                    if v in Rset: continue
                    if not ((Au >> v) & 1): continue
                    pv = pval[v]
                    w_uv = pu + pv - 2*pu*pv     # P[exactly one of u,v in random S]
                    if w_uv != 0.0:
                        tot += w_uv if col[u] == col[v] else -w_uv
        g.append(float(tot))
    return np.array(g)

def _vertex_classes(k):
    import itertools
    return [(c,) + ab for c in (0, 1) for ab in itertools.product((0, 1), repeat=k)]

def gen_rooted_switches(states, sigma, pvals=(0.0, 0.5, 1.0)):
    """All distinct switches (p in pvals^classes) for a colored type sigma, minus constant maps."""
    import itertools
    k = sigma[0]
    classes = _vertex_classes(k)
    cons = []
    for assign in itertools.product(pvals, repeat=len(classes)):
        if all(a == 0.0 for a in assign) or all(a == 1.0 for a in assign):
            continue  # S=empty or S=all are trivial; constant p=1/2 is KEPT (gives d_mono<=d_cut)
        amap = {cl: a for cl, a in zip(classes, assign)}
        def pfunc(color, adjbits, amap=amap):
            return amap[(color,) + tuple(adjbits)]
        cons.append(rooted_switch_counts(states, sigma, pfunc))
    return cons

def gen_switches(states, kmax=1):
    """Full rooted-switch families for k=0..kmax over all colored types. Dedup identical vectors."""
    import flag_engine_col as fc
    cons = []
    seen = set()
    def add(vecs):
        for v in vecs:
            key = tuple(np.round(v, 6))
            if key not in seen and any(abs(x) > 1e-9 for x in v):
                seen.add(key); cons.append(v)
    for k in range(0, kmax+1):
        for (kk, A, col) in fc.enumerate_colored(k, triangle_free=True):
            add(gen_rooted_switches(states, (k, A, tuple(col))))
    return cons


def all_switching(states, include_sw1=True, ab_grid=None):
    cons = []
    if ab_grid is None:
        ab_grid = [(0.5, 0.5), (1.0, 0.5), (0.5, 1.0), (0.75, 0.25), (0.25, 0.75), (1.0, 0.0), (0.0, 1.0)]
    for (a, b) in ab_grid:
        cons.append(sw0_counts(states, a, b))
    if include_sw1:
        cons.append(sw1_counts(states, 0))
        cons.append(sw1_counts(states, 1))
    return cons


if __name__ == "__main__":
    # sanity: SW1-limit functional should be <= 0 on max-cut-colored graphs.
    # (we test on enumerated colored states using their GIVEN coloring; the per-graph value can be
    #  positive for a non-max-cut induced coloring, but for genuine max cuts it must be <=0.)
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    import flag_engine as fe
    # build a few graphs + an EXACT max cut coloring via the audit helper
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "experiments"))
    from verify_q15_audit import maxcut, adj, C5n, myc, kbip
    bad = 0; tested = 0
    for tag, (N, A) in [("C5[3]", C5n(3)), ("M(M(C5))", myc(*myc(*C5n(2)))), ("K8,32", kbip(8,32))]:
        beta, colc = maxcut(N, A)
        # SW1-limit value at this max cut
        for rc in (0, 1):
            tot = 0
            for v in range(N):
                if colc[v] != rc: continue
                nb = [1 if w in A[v] else 0 for w in range(N)]
                P = [u for u in range(N) if u!=v and colc[u]==rc and nb[u]]
                Q = [u for u in range(N) if u!=v and colc[u]!=rc and nb[u]]
                R = [u for u in range(N) if u!=v and colc[u]==rc and not nb[u]]
                T = [u for u in range(N) if u!=v and colc[u]!=rc and not nb[u]]
                Ab = [0]*N
                for uu in range(N):
                    for ww in A[uu]: Ab[uu] |= 1<<ww
                tot += _edges_between(Ab, P, R) + _edges_between(Ab, Q, T) - _edges_between(Ab, R, T)
            tested += 1
            if tot > 1e-9: bad += 1
            print(f"  {tag} root_color={rc}: SW1-limit value = {tot}  ({'OK <=0' if tot<=1e-9 else 'VIOLATION'})")
    print(f"SW1-limit valid on max cuts: {tested-bad}/{tested}")
    print("DONE")
