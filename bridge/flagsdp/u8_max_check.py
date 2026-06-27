#!/usr/bin/env python3
"""KEY proof test: is U_8(W) <= 2/25 for ALL triangle-free W (tight at C5)?  If yes, the conjecture d_mono<=2/25
REDUCES to the explicit functional bound U_8<=2/25 (the order-10 LP target). If some graph has U_8>2/25, the
U_8 envelope is too weak there (can't prove via U_8 alone -> need (6,8) or the band-only structure).
Enumerate ALL triangle-free graphs on n=6,7,8 (and the zoo), compute U_8, report MAX U_8 and any with U_8 > 2/25.
"""
import time
from math import factorial
from fractions import Fraction as F
from compute_U8 import canon_label, maxcut, popcount
import flag_engine as fe

TWO25=2.0/25.0
def comps(total,parts):
    if parts==1: yield (total,); return
    for f in range(total+1):
        for rest in comps(total-f,parts-1): yield (f,)+rest
def blowup(counts,T):
    parts=[]
    for p,c in enumerate(counts): parts+=[p]*c
    n=len(parts); A=[0]*n
    for u in range(n):
        for w in range(u+1,n):
            if parts[u]!=parts[w] and (T[parts[u]]>>parts[w])&1: A[u]|=1<<w; A[w]|=1<<u
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
def dmono(n,A):
    e=sum(popcount(A[v]) for v in range(n))//2; return 2*(e-maxcut_graph(n,A))/(n*n)
_memo={}
def canon8(R):
    rk=tuple(R); v=_memo.get(rk)
    if v is None: v=canon_label(8,R); _memo[rk]=v
    return v
def U8(n0,A0,alpha=None):
    """U_8 of the i.i.d. blow-up of the n0-vertex graph A0 with weights alpha (uniform if None)."""
    m=n0; T=A0; alpha=alpha or [F(1,m)]*m
    W={}
    for counts in comps(10,m):
        w=factorial(10)
        for c in counts: w//=factorial(c)
        wt=w
        for p,c in enumerate(counts): wt*=float(alpha[p])**c
        if wt==0: continue
        n,A=blowup(counts,T)
        for i in range(10):
            Ai=A[i]
            for je in range(10):
                if i!=je and (Ai>>je)&1:
                    anch=[v for v in range(10) if v!=i and v!=je]
                    idx={v:p for p,v in enumerate(anch)}
                    R=[0]*8
                    for p in range(8):
                        for qd in range(p+1,8):
                            if (A[anch[p]]>>anch[qd])&1: R[p]|=1<<qd; R[qd]|=1<<p
                    key,inv=canon8(R)
                    Aset=frozenset(inv[idx[v]] for v in anch if (Ai>>v)&1)
                    Bset=frozenset(inv[idx[v]] for v in anch if (A[je]>>v)&1)
                    W.setdefault(key,{}); W[key][(Aset,Bset)]=W[key].get((Aset,Bset),0.0)+wt/90.0
    U=0.0
    for key,ed in W.items():
        offdiag={}; sl=0.0; profs=set()
        for (Aset,Bset),w in ed.items():
            profs.add(Aset); profs.add(Bset)
            if Aset==Bset: sl+=w
            else:
                a,b=tuple(sorted([Aset,Bset],key=lambda s:(len(s),sorted(s)))); offdiag[(a,b)]=offdiag.get((a,b),0.0)+w
        mc=maxcut(list(profs),offdiag) if offdiag else 0.0
        U += sl + (sum(offdiag.values())-mc)
    return U
def tri_free(n,A):
    for u in range(n):
        for v in range(u+1,n):
            if (A[u]>>v)&1 and (A[u]&A[v]): return False
    return True

def main():
    maxU=0.0; argmax=None; viol=[]
    for nn in [6,7,8]:
        gs=fe.enumerate_graphs(nn,triangle_free=True); t0=time.time(); mx=0.0; mxA=None
        for (k,A) in gs:
            u=float(U8(nn,A))
            if u>mx: mx=u; mxA=A
            if u>maxU: maxU=u; argmax=(nn,A)
            if u>TWO25+1e-9: viol.append((nn,A,u))
        print(f"n={nn}: {len(gs)} tri-free graphs, max U_8={mx:.6f} (2/25={TWO25:.6f}), {'>2/25!' if mx>TWO25+1e-9 else 'all <=2/25'} [{time.time()-t0:.0f}s]",flush=True)
    print(f"\nGLOBAL max U_8 over n<=8 tri-free = {maxU:.6f}  (2/25 = {TWO25:.6f})",flush=True)
    print(f"  U_8 <= 2/25 for ALL tested ? {maxU<=TWO25+1e-9}  ; #violations = {len(viol)}",flush=True)
    if viol:
        for (nn,A,u) in viol[:5]: print(f"  VIOLATION n={nn} U_8={u:.6f} A={A}",flush=True)
    print("DONE",flush=True)

if __name__=="__main__": main()
