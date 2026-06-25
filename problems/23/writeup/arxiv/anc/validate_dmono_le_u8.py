#!/usr/bin/env python3
"""SOUNDNESS GATE: directly test  d_mono(W_G) <= U_8(W_G)  for many small triangle-free graphs G.
U_8 in MY LP's normalization (/90 = ordered pairs, edge-density units; same as compute_U8/cutting_plane_u8).
d_mono(W_G) = 2(e - maxcut(G))/n^2  (graphon maxcut = integer maxcut since the cut functional is multilinear
=> max at a corner). If U_8 >= d_mono for ALL G (tight at C5), the envelope bound d_mono<=U_8 is validated.
Memoized canon_label for speed.
"""
import itertools, time
from math import factorial
from compute_U8 import canon_label, maxcut, popcount
import flag_engine as fe

def cyc(m):
    A=[0]*m
    for i in range(m): A[i]|=1<<((i+1)%m); A[i]|=1<<((i-1)%m)
    return A

def petersen():
    # outer 5-cycle 0..4, inner pentagram 5..9, spokes i-(i+5)
    A=[0]*10
    def e(u,v): A[u]|=1<<v; A[v]|=1<<u
    for i in range(5):
        e(i,(i+1)%5); e(5+i,5+((i+2)%5)); e(i,5+i)
    return A

def blowup(counts, Tadj):
    parts=[]
    for p,c in enumerate(counts): parts+=[p]*c
    n=len(parts); A=[0]*n
    for u in range(n):
        for w in range(u+1,n):
            if parts[u]!=parts[w] and (Tadj[parts[u]]>>parts[w])&1: A[u]|=1<<w; A[w]|=1<<u
    return n,A

def comps(total, parts):
    if parts==1: yield (total,); return
    for f in range(total+1):
        for rest in comps(total-f,parts-1): yield (f,)+rest

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

_memo={}
def canon_memo(Radj):
    rk=tuple(Radj); v=_memo.get(rk)
    if v is None: v=canon_label(8,Radj); _memo[rk]=v
    return v

def U8_graphon(m, Tadj, alpha):
    W={}
    for counts in comps(10,m):
        w=factorial(10)
        for c in counts: w//=factorial(c)
        wt=w
        for p,c in enumerate(counts): wt*=alpha[p]**c
        if wt==0: continue
        n,A=blowup(counts,Tadj)
        for i in range(10):
            Ai=A[i]
            for j in range(10):
                if i!=j and (Ai>>j)&1:
                    anch=[v for v in range(10) if v!=i and v!=j]
                    idx={v:p for p,v in enumerate(anch)}
                    Radj=[0]*8
                    for p in range(8):
                        for qd in range(p+1,8):
                            if (A[anch[p]]>>anch[qd])&1: Radj[p]|=1<<qd; Radj[qd]|=1<<p
                    key,inv=canon_memo(Radj)
                    Aset=frozenset(inv[idx[v]] for v in anch if (A[i]>>v)&1)
                    Bset=frozenset(inv[idx[v]] for v in anch if (A[j]>>v)&1)
                    W.setdefault(key,{}); W[key][(Aset,Bset)]=W[key].get((Aset,Bset),0.0)+wt/90.0
    U8=0.0
    for key,ed in W.items():
        offdiag={}; sl=0.0; profiles=set()
        for (Aset,Bset),w in ed.items():
            profiles.add(Aset); profiles.add(Bset)
            if Aset==Bset: sl+=w
            else:
                a,b=tuple(sorted([Aset,Bset],key=lambda s:(len(s),sorted(s))))
                offdiag[(a,b)]=offdiag.get((a,b),0.0)+w
        mc=maxcut(list(profiles),offdiag) if offdiag else 0.0
        U8 += sl + (sum(offdiag.values())-mc)
    return U8

def dmono(n,A):
    e=sum(popcount(A[v]) for v in range(n))//2; mc=maxcut_graph(n,A)
    return 2*(e-mc)/(n*n)

def tri_free(n,A):
    for u in range(n):
        for v in range(u+1,n):
            if (A[u]>>v)&1 and (A[u]&A[v]): return False
    return True

def main():
    from fractions import Fraction as F
    graphs=[("C5",5,cyc(5)),("C7",7,cyc(7)),("C9",9,cyc(9)),
            ("C5+C5",10,None),("Petersen",10,petersen()),
            ("path P5",5,[2,1|4 if False else 1,0,0,0])]
    # fix some templates explicitly
    P5=[0]*5
    for i in range(4): P5[i]|=1<<(i+1); P5[i+1]|=1<<i
    C5C5=[0]*10
    for i in range(5):
        C5C5[i]|=1<<((i+1)%5); C5C5[(i+1)%5]|=1<<i
        C5C5[5+i]|=1<<(5+(i+1)%5); C5C5[5+(i+1)%5]|=1<<(5+i)
    tests=[("C5",5,cyc(5)),("C7",7,cyc(7)),("C9",9,cyc(9)),("P5",5,P5),
           ("C5uC5",10,C5C5),("Petersen",10,petersen())]
    print(f"{'graph':10s} {'n':>2s} {'triFree':>7s} {'d_mono':>10s} {'U_8':>12s} {'U_8>=d_mono':>11s} {'ratio':>8s}",flush=True)
    worst=1e9
    for (name,n,A) in tests:
        if not tri_free(n,A): print(f"{name}: NOT triangle-free, skip"); continue
        dm=dmono(n,A); t0=time.time()
        U8=float(U8_graphon(n,A,[F(1,n)]*n))
        ok=U8>=dm-1e-12; ratio=U8/dm if dm>0 else float('inf')
        worst=min(worst, U8-dm)
        print(f"{name:10s} {n:2d} {str(tri_free(n,A)):>7s} {dm:10.6f} {U8:12.6e} {str(ok):>11s} {ratio:8.3f}  [{time.time()-t0:.0f}s]",flush=True)
    print(f"\nWORST U_8 - d_mono = {worst:+.3e}  => d_mono<=U_8 holds for ALL tested ? {worst>=-1e-9}",flush=True)
    print("DONE",flush=True)

if __name__=="__main__": main()
