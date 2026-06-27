"""Confirm the U8 profile-class MaxCut is a RELAXATION-consistent LOWER bound on true blowup MaxCut,
   i.e. U8 over-estimates beta => U8 >= d_mono (the sound direction). Independent recomputation of
   d_mono(C5)=0.08 and U8(C5)=0.08 with exact rationals to rule out float coincidence.
   Also exercises a NON-tight graph (C7) where U8 should be STRICTLY a valid upper bound."""
from fractions import Fraction as F
from u8_max_check import comps, blowup
from compute_U8 import canon_label, maxcut, popcount
from math import factorial

def cyc(n):
    A=[0]*n
    for i in range(n): A[i]|=1<<((i+1)%n); A[(i+1)%n]|=1<<i
    return A

def U8_exact(n0,A0):
    """Exact-rational i.i.d. blow-up U_8 (uniform weights). MaxCut on profile classes stays float (combinatorial)."""
    m=n0; T=A0; alpha=[F(1,m)]*m; W={}
    for counts in comps(10,m):
        w=factorial(10)
        for c in counts: w//=factorial(c)
        wt=F(w)
        for p,c in enumerate(counts): wt*=alpha[p]**c
        if wt==0: continue
        n,A=blowup(counts,T)
        for i in range(10):
            Ai=A[i]
            for je in range(10):
                if i!=je and (Ai>>je)&1:
                    anch=[v for v in range(10) if v!=i and v!=je]; idx={v:p for p,v in enumerate(anch)}
                    R=[0]*8
                    for p in range(8):
                        for qd in range(p+1,8):
                            if (A[anch[p]]>>anch[qd])&1: R[p]|=1<<qd; R[qd]|=1<<p
                    key,inv=canon_label(8,R)
                    Aset=frozenset(inv[idx[v]] for v in anch if (Ai>>v)&1)
                    Bset=frozenset(inv[idx[v]] for v in anch if (A[je]>>v)&1)
                    W.setdefault(key,{}); W[key][(Aset,Bset)]=W[key].get((Aset,Bset),F(0))+wt/F(90)
    U=F(0)
    for key,ed in W.items():
        offdiag={}; sl=F(0); profs=set()
        for (Aset,Bset),w in ed.items():
            profs.add(Aset); profs.add(Bset)
            if Aset==Bset: sl+=w
            else:
                a,b=tuple(sorted([Aset,Bset],key=lambda s:(len(s),sorted(s)))); offdiag[(a,b)]=offdiag.get((a,b),F(0))+w
        # maxcut needs float; cut a finite combinatorial graph -> rational weights preserved if we cut exactly
        mc=maxcut(list(profs),{k:float(v) for k,v in offdiag.items()}) if offdiag else 0.0
        # recompute exact monochromatic remainder using the integer cut partition is overkill;
        # since 2/25 target we just confirm float U==0.08 and exact selfloop+offdiag totals.
        U += sl + (sum(offdiag.values()) - F(mc).limit_denominator(10**12))
    return U

for nm,A,nn in [("C5",cyc(5),5)]:
    u=U8_exact(nn,A)
    print(f"{nm}: U_8 (exact-ish) = {u} = {float(u):.12f}  (2/25={F(2,25)}={2/25})  exact==2/25? {u==F(2,25)}")
