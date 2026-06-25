#!/usr/bin/env python3
"""PROTOTYPE step 3 (SOUNDNESS-CORRECTED): re-test GPT's interval localizer with the CORRECT t(2K2) moment.
BUG in proto2: used q_H = dedge_H^2 => Sum_H x_H dedge_H^2 = p^2 + Var(D) (within-9-sample edge-density variance),
which over-constrains single graphons (spurious Var(D) term) -> FALSE eta<0. FIX: q_H = t(2K2,H) = the injective
4-point hom density = 8*M2(H)/(n)_4, M2 = #vertex-disjoint edge pairs = C(|E|,2) - sum_v C(deg_v,2). This is an
UNBIASED estimator of t(2K2,W) (U-statistic), so Sum_H x_H q_H = t(2K2,W) = p^2 EXACTLY for a single graphon,
and the localizer (a+b)p - q - ab = (p-a)(b-p) >= 0 holds for p in [a,b]. SOUND. For a mixture it forces
Var(p_i) <= (p-a)(b-p), excluding the wide fooling mixture. Re-run; eta<0 with CORRECT q_H => genuine candidate.
"""
import numpy as np
from math import comb
from scipy.optimize import linprog
import prove_cert as pc

def state_moments(states):
    """Return (my_dedge, q2) per state: induced edge density and t(2K2) injective-hom density."""
    ns = len(states); my_dedge = np.zeros(ns); q2 = np.zeros(ns)
    for hi,(n,A) in enumerate(states):
        deg = [bin(A[u]).count("1") for u in range(n)]
        E = sum(deg)//2
        Cn2 = comb(n,2)
        my_dedge[hi] = E / Cn2 if Cn2 else 0.0
        # M2 = #vertex-disjoint edge pairs = C(E,2) - sum_v C(deg_v,2)
        M2 = comb(E,2) - sum(comb(d,2) for d in deg)
        n4 = n*(n-1)*(n-2)*(n-3)
        q2[hi] = 8*M2/n4 if n4 else 0.0
    return my_dedge, q2

def solve(ns, dedge, rows, prov, band, loc=None):
    """loc = (a,b,qrow) adds Sum_H x_H[(a+b)dedge_H - qrow_H - ab] >= 0."""
    lo,hi = band; nv=ns+1; c=np.zeros(nv); c[-1]=-1.0; A=[];b=[]
    A.append(np.concatenate([-dedge,[0.0]])); b.append(-lo)
    A.append(np.concatenate([dedge,[0.0]]));  b.append(hi)
    for i,row in enumerate(rows):
        r=np.asarray(row,float)
        if prov[i][0] in ("deficit","deficit_pmap"): A.append(np.concatenate([-r,[1.0]])); b.append(0.0)
        else: A.append(np.concatenate([-r,[0.0]])); b.append(0.0)
    if loc is not None:
        a_,b_,qrow = loc
        L = (a_+b_)*dedge - qrow - a_*b_
        A.append(np.concatenate([-L,[0.0]])); b.append(0.0)
    Aeq=[np.concatenate([np.ones(ns),[0.0]])]; beq=[1.0]; bnd=[(0,None)]*ns+[(None,None)]
    r=linprog(c,A_ub=np.array(A),b_ub=np.array(b),A_eq=np.array(Aeq),b_eq=np.array(beq),bounds=bnd,method="highs-ipm")
    if not r.success: r=linprog(c,A_ub=np.array(A),b_ub=np.array(b),A_eq=np.array(Aeq),b_eq=np.array(beq),bounds=bnd,method="highs")
    return (-r.fun if r.success else None)

def main():
    C=pc.load(9); states=C["states"]
    print("computing state moments (dedge, t(2K2))...",flush=True)
    my_dedge,q2 = state_moments(states)
    eng_dedge = np.asarray(C["dedge"],float)
    print(f"convention check: max|my_dedge - engine dedge| = {np.abs(my_dedge-eng_dedge).max():.2e}",flush=True)
    print("cutting_plane (maxit=12)...",flush=True)
    st,ns,dedge,t,rows,prov,v = pc.cutting_plane(C,maxit=12,target=-1e-6,mom_maxvecs=8,verbose=False)
    print(f"cuts={len(rows)}, baseline eta(full band)={v:+.7e}",flush=True)
    FULL=(0.2486,0.3197)
    print(f"[no loc]            full band eta = {solve(ns,dedge,rows,prov,FULL):+.7e}",flush=True)
    # WRONG (proto2) version: q=dedge^2  -- confirm it spuriously closes
    wrong = solve(ns,dedge,rows,prov,FULL,loc=(FULL[0],FULL[1],dedge*dedge))
    print(f"[WRONG q=dedge^2]   full band eta = {wrong:+.7e}   (the buggy proto2 result)",flush=True)
    # CORRECT version: q = t(2K2)
    corr = solve(ns,dedge,rows,prov,FULL,loc=(FULL[0],FULL[1],q2))
    print(f"[CORRECT q=t(2K2)]  full band eta = {corr:+.7e}   <<< THE SOUND TEST",flush=True)
    print("--- narrow sub-bands, CORRECT q=t(2K2) ---",flush=True)
    for (a,b) in [(0.2486,0.27),(0.27,0.29),(0.29,0.31),(0.31,0.3197),(0.28,0.31),(0.26,0.30),(0.2486,0.3197)]:
        e0=solve(ns,dedge,rows,prov,(a,b))
        e =solve(ns,dedge,rows,prov,(a,b),loc=(a,b,q2))
        tag="  <<< eta<0!" if (e is not None and e<0) else ""
        e0s=f"{e0:+.3e}" if e0 is not None else "None"; es=f"{e:+.3e}" if e is not None else "None"
        print(f"  [{a:.4f},{b:.4f}] w={b-a:.3f}: no-loc={e0s}  +corr-loc={es}{tag}",flush=True)
    print("DONE",flush=True)

if __name__=="__main__": main()
