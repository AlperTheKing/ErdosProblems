#!/usr/bin/env python3
"""VALIDATE GPT's 8-anchor cut: d_mono(W) <= U_8(W) MUST hold for REAL graphs (else construction/canonicalization
is buggy). Compute U_8 directly on real triangle-free graphs G (aggregate w_R over (ordered edge (i,j), 8-subset
anchors of V\\{i,j})), compare to d_mono(G)=e-MaxCut (brute). Expect U_8 >= d_mono >= 0 for every real G; the
witness gave U_8~0 (pseudo). Reuses canon_label/perm_colors/maxcut from compute_U8."""
import itertools
from math import comb
from compute_U8 import canon_label, maxcut, popcount
import flag_engine as fe

def cyc_blowup(m, t):
    """C_m blown up by t: m*t vertices, parts of size t, part i ~ part i+-1 mod m."""
    n=m*t; A=[0]*n
    for u in range(n):
        for w in range(u+1,n):
            pu,pw=u//t,w//t
            if pu!=pw and (pw==(pu+1)%m or pw==(pu-1)%m): A[u]|=1<<w; A[w]|=1<<u
    return n,A

def maxcut_graph(n,A):
    best=0
    for mask in range(1<<(n-1)):
        c=0
        for u in range(n):
            au=A[u]
            for w in range(u+1,n):
                if (au>>w)&1 and ((mask>>u)&1)!=((mask>>w)&1): c+=1
        if c>best: best=c
    return best

def U8_of_graph(n, A):
    """aggregate w_R(A,B) over (ordered edge (i,j), 8-subset anchors), then per-R MaxCut -> U_8 (edge-density units)."""
    V=list(range(n))
    W={}; total=0.0
    edges=[(i,j) for i in range(n) for j in range(n) if i!=j and (A[i]>>j)&1]
    denom = n*(n-1)*comb(n-2,8)   # ordered pair x 8-subset anchors -> normalizes total to edge density e
    for (i,j) in edges:
        rest=[v for v in V if v!=i and v!=j]
        for anch in itertools.combinations(rest,8):
            # induced R on anch
            idx={v:p for p,v in enumerate(anch)}
            Radj=[0]*8
            for p in range(8):
                for qd in range(p+1,8):
                    if (A[anch[p]]>>anch[qd])&1: Radj[p]|=1<<qd; Radj[qd]|=1<<p
            key,inv=canon_label(8,Radj)
            Aset=frozenset(inv[idx[v]] for v in anch if (A[i]>>v)&1)
            Bset=frozenset(inv[idx[v]] for v in anch if (A[j]>>v)&1)
            W.setdefault(key,{}); W[key][(Aset,Bset)]=W[key].get((Aset,Bset),0.0)+1.0/denom
            total+=1.0/denom
    U8=0.0; sloop=0.0
    for key,ed in W.items():
        offdiag={}; sl=0.0; profiles=set()
        for (Aset,Bset),w in ed.items():
            profiles.add(Aset); profiles.add(Bset)
            if Aset==Bset: sl+=w
            else:
                a,b=tuple(sorted([Aset,Bset],key=lambda s:(len(s),sorted(s))))
                offdiag[(a,b)]=offdiag.get((a,b),0.0)+w
        mc=maxcut(list(profiles),offdiag) if offdiag else 0.0
        U8 += sl + (sum(offdiag.values())-mc); sloop+=sl
    return U8, total, sloop

def main():
    for (name,m,t) in [("C5[2]",5,2),("C7[2]",7,2),("C5[2]+pad? skip","_",0)][:2]:
        n,A=cyc_blowup(m,t)
        if n<8+2:
            print(f"{name}: n={n} too small for 8 anchors+2"); continue
        e=sum(popcount(A[v]) for v in range(n))//2
        mc=maxcut_graph(n,A)
        dmono=2*(e-mc)/(n*(n-1))   # distinct-pair normalization, matching U_8
        U8,tot,sloop=U8_of_graph(n,A)
        de=2*e/(n*(n-1))
        print(f"\n{name}: n={n}, d_edge={de:.4f}, d_mono={dmono:.5f}",flush=True)
        print(f"   total weight (~=e={de:.4f}? )= {tot:.5f}; U_8 = {U8:.5f}; self-loops={sloop:.5f}",flush=True)
        ok = U8 >= dmono - 1e-9
        print(f"   U_8 >= d_mono ? {ok}   (U_8={U8:.5f} vs d_mono={dmono:.5f}) {'VALID' if ok else '*** VIOLATION: construction BUGGY ***'}",flush=True)
    print("\nDONE",flush=True)

if __name__=="__main__": main()
