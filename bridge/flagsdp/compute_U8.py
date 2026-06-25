#!/usr/bin/env python3
"""GPT path (A): the ORDER-10 EIGHT-ANCHOR profile-cut gap U_8(q) on the witness.
For each order-10 graph J (q_J>0) and each ordered edge (i,j): anchors = the other 8 vertices, R = J[anchors]
(canonically relabeled), A=profile of i, B=profile of j (in canonical anchor coords). Accumulate
w_R(A,B) += q_J/(10*9). Per canonical R: MaxCut on the profile graph (nodes=profiles, edge {A,B} weight w_R(A,B),
self-loops A=B always monochromatic) => min monochromatic_R = total_R - MaxCut_R. U_8 = sum_R min_monochromatic_R
(edge-density units). Compare U_8 to m*=2/25+6.0e-5 (witness d_mono) and to 2/25. Float first (is U_8 < m* / <=2/25?);
exact rational + cut-validity audit only if it closes.
"""
import numpy as np, itertools, sys
from fractions import Fraction as F
import flag_engine as fe

def popcount(x): return bin(x).count("1")

def perm_colors(n, adj):
    """per-vertex refined color (WL + walk counts), returned as small ints (ties = same color)."""
    col=[popcount(adj[v]) for v in range(n)]
    for _ in range(5):
        newc=[(col[v], tuple(sorted(col[u] for u in range(n) if (adj[v]>>u)&1))) for v in range(n)]
        u={c:i for i,c in enumerate(sorted(set(newc)))}; col=[u[c] for c in newc]
    # walk counts A2,A3,A4 row sums + diagonals
    M=[[1 if (adj[i]>>j)&1 else 0 for j in range(n)] for i in range(n)]
    def mm(X,Y): return [[sum(X[i][k]*Y[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
    A2=mm(M,M); A3=mm(A2,M); A4=mm(A3,M)
    sig=[(col[v],sum(A2[v]),sum(A3[v]),sum(A4[v]),A2[v][v],A3[v][v],A4[v][v]) for v in range(n)]
    u={c:i for i,c in enumerate(sorted(set(sig)))}; return [u[s] for s in sig]

def canon_label(n, adj):
    """return (canonical adjacency tuple, inv) where inv[old_vertex]=canonical_position (minimizing adj string)."""
    col=perm_colors(n,adj)
    order0=sorted(range(n),key=lambda v:col[v])
    # group by color
    groups=[]; i=0
    while i<n:
        j=i
        while j<n and col[order0[j]]==col[order0[i]]: j+=1
        groups.append(order0[i:j]); i=j
    best=None; bestperm=None
    def gen(idx, cur):
        nonlocal best,bestperm
        if idx==len(groups):
            # cur = full ordering; build adjacency string
            pos={cur[p]:p for p in range(n)}
            key=tuple( 1 if (adj[cur[a]]>>cur[b])&1 else 0 for a in range(n) for b in range(a+1,n) )
            if best is None or key<best: best=key; bestperm=list(cur)
            return
        for pr in itertools.permutations(groups[idx]):
            gen(idx+1, cur+list(pr))
    gen(0,[])
    inv={bestperm[p]:p for p in range(n)}
    return best, inv

def maxcut(nodes, edges):
    """edges: dict {(a,b):w} a<b (off-diagonal), nodes:list. return MaxCut weight (max over 2-colorings)."""
    nn=len(nodes); idx={v:i for i,v in enumerate(nodes)}
    el=[(idx[a],idx[b],w) for (a,b),w in edges.items()]
    if nn<=20:
        best=0.0
        for mask in range(1<<(nn-1)):
            c=0.0
            for a,b,w in el:
                if ((mask>>a)&1)!=((mask>>b)&1): c+=w
            if c>best: best=c
        return best
    # heuristic: local search + restarts (rng-free: vary init by index)
    import random
    best=0.0
    for r in range(40):
        s=[(r>>0 ^ i)&1 for i in range(nn)]  # deterministic-ish init
        s=[ (i*r+ r)%2 for i in range(nn)]
        improved=True
        while improved:
            improved=False
            for v in range(nn):
                d=0.0
                for a,b,w in el:
                    if a==v or b==v:
                        o=b if a==v else a
                        d+= w if s[v]==s[o] else -w
                if d>1e-15: s[v]^=1; improved=True
        c=sum(w for a,b,w in el if s[a]!=s[b]); best=max(best,c)
    return best

def main():
    d=np.load("witness.npz",allow_pickle=True); q=d["q"]
    g10=fe.enumerate_graphs(10,triangle_free=True)
    assert len(g10)==len(q), f"{len(g10)} vs {len(q)}"
    mstar=2.0/25.0+6.02e-5
    sup=[j for j in range(len(q)) if q[j]>1e-9]
    print(f"witness q support={len(sup)}; building w_R(A,B)...",flush=True)
    # w[Rkey] = dict {(A,B): weight}, A,B = frozenset of canonical anchor positions
    W={}
    norm=10*9
    total=0.0
    for jj in sup:
        n,A=g10[jj]; qj=float(q[jj])
        for i in range(10):
            for je in range(10):
                if i!=je and (A[i]>>je)&1:
                    anchors=[v for v in range(10) if v!=i and v!=je]
                    # induced R on anchors
                    m,Radj=fe.induced(A,anchors)  # 8-vertex
                    key,inv=canon_label(8,Radj)
                    # profiles: which anchors i,je connect to, in canonical coords
                    Aset=frozenset(inv[anchors.index(v)] for v in range(10) if v!=i and v!=je and (A[i]>>v)&1)
                    Bset=frozenset(inv[anchors.index(v)] for v in range(10) if v!=i and v!=je and (A[je]>>v)&1)
                    W.setdefault(key,{}); W[key][(Aset,Bset)]=W[key].get((Aset,Bset),0.0)+qj/norm
                    total+=qj/norm
    print(f"total weight (should ~= t(K2,q)~0.297) = {total:.5f}; #distinct R = {len(W)}",flush=True)
    U8=0.0; selfloop_tot=0.0
    for key,ed in W.items():
        profiles=set()
        offdiag={}; sloop=0.0
        for (Aset,Bset),w in ed.items():
            profiles.add(Aset); profiles.add(Bset)
            if Aset==Bset: sloop+=w
            else:
                a,b=tuple(sorted([Aset,Bset],key=lambda s:(len(s),sorted(s))))
                offdiag[(a,b)]=offdiag.get((a,b),0.0)+w
        nodes=list(profiles); tot_off=sum(offdiag.values())
        mc=maxcut(nodes,offdiag) if offdiag else 0.0
        min_mono = sloop + (tot_off - mc)
        U8+=min_mono; selfloop_tot+=sloop
    print(f"\n>>> U_8(q) = {U8:.6e}   (m* = {mstar:.6e}, 2/25 = {2/25:.6e})",flush=True)
    print(f"    Delta_8 = m* - U_8 = {mstar-U8:+.6e}",flush=True)
    print(f"    self-loop (always-mono) total = {selfloop_tot:.6e}",flush=True)
    if U8<=2/25: print("    >>> U_8 <= 2/25 : the 8-anchor cut KILLS the witness at threshold => candidate CLOSURE (needs exact rational + cut-validity audit).",flush=True)
    elif U8<mstar-1e-9: print(f"    >>> U_8 < m* : 8-anchor cut TIGHTENS (gap {mstar-U8:.2e}); add cut, re-solve, iterate.",flush=True)
    else: print("    >>> U_8 ~ m* : 8-anchor cut does not help (Delta_8<=0); go to 9 anchors.",flush=True)
    print("DONE",flush=True)

if __name__=="__main__": main()
