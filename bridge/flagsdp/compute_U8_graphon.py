#!/usr/bin/env python3
"""CORRECTED validation: compute U_8 on the GRAPHON BLOW-UP LAW (i.i.d. 10-sampling, full multinomial over
count-vectors), NOT the finite point mass. Check d_mono(W) <= 45*U_8(W) (GPT's sharpened bound; fresh-fresh cost
is 1/45 of the 45=C(10,2) pairs). If real band graphons satisfy it (U_8 >= d_mono/45) AND the witness gives
45*U_8=0.0217 < 0.08=m*, the witness is genuinely separated. Canonicalization = R alone (canon_label), weight by q_J.
"""
import itertools
from math import comb, factorial
from compute_U8 import canon_label, maxcut, popcount
import flag_engine as fe

def cyc(m):
    A=[0]*m
    for i in range(m): A[i]|=1<<((i+1)%m); A[i]|=1<<((i-1)%m)
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

def U8_graphon(m, Tadj, alpha):
    """U_8 for the blow-up graphon: sum over count-vectors of multinomial weight; aggregate w_R over (J,edge,complement-8)."""
    W={}; total=0.0
    for counts in comps(10,m):
        # weight = multinomial(10;counts) * prod alpha^counts
        w=factorial(10)
        for c in counts: w//=factorial(c)
        wt=w
        for p,c in enumerate(counts): wt*= alpha[p]**c
        if wt==0: continue
        n,A=blowup(counts,Tadj)  # n=10
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
                    key,inv=canon_label(8,Radj)
                    Aset=frozenset(inv[idx[v]] for v in anch if (A[i]>>v)&1)
                    Bset=frozenset(inv[idx[v]] for v in anch if (A[j]>>v)&1)
                    W.setdefault(key,{}); W[key][(Aset,Bset)]=W[key].get((Aset,Bset),0.0)+wt/(10*9)
                    total+=wt/(10*9)
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
    return U8, total

def main():
    from fractions import Fraction as F
    for (name,m) in [("C5",5),("C7",7)]:
        Tadj=cyc(m); alpha=[F(1,m)]*m
        # d_mono via large-ish finite blow-up (distinct-pair convention)
        bt=2 if m==7 else 2
        nB,AB=blowup([bt]*m,Tadj)  # C5[2]=10 or C7[2]=14
        eB=sum(popcount(AB[v]) for v in range(nB))//2; mcB=maxcut_graph(nB,AB)
        dmono=2*(eB-mcB)/(nB*(nB-1))
        U8,tot=U8_graphon(m,Tadj,alpha)
        U8f=float(U8); de=float(sum(alpha[i]*alpha[j] for i in range(m) for j in range(m) if (Tadj[i]>>j)&1))
        print(f"\n{name} graphon: d_edge={de:.4f}, d_mono(~{name}[2])={dmono:.5f}",flush=True)
        print(f"   U_8(blow-up law) = {U8f:.6e}; total weight(~=e={de:.4f})={float(tot):.5f}",flush=True)
        print(f"   45*U_8 = {45*U8f:.6e}   bound d_mono <= 45*U_8 ? {dmono <= 45*U8f + 1e-9}  (d_mono={dmono:.5f})",flush=True)
        print(f"   witness U_8=4.83e-4 -> 45*U_8(witness)=0.02174; vs d_mono;  graphon U_8/witness ratio={U8f/4.83e-4:.2f}",flush=True)
    print("\nDONE",flush=True)

if __name__=="__main__": main()
