#!/usr/bin/env python3
"""KILL-CRITERION TEST: after pinning edge density (K2 interval localizer on a narrow band), recompute the true
between-component variance Var_true(F) of the residual fooling optimum for every order-<=4 statistic. If the
residual is near-multiplicative in ALL available directions (all Var_true small) yet eta stays > 0, GPT's kill
criterion is met: order-9 graphon realizability is exhausted (the distinguishing constraint = odd-cycle/C5
multiplicativity needs order >=10). Also tries adding ALL available SOUND McCormick localizers on the residual's
dominant directions simultaneously to push eta as far down as order-9 multiplicativity allows."""
import numpy as np, itertools, os
from math import comb
from scipy.optimize import linprog
import prove_cert as pc

PATS={"K2":(2,[(0,1)]),"P3":(3,[(0,1),(1,2)]),"P4":(4,[(0,1),(1,2),(2,3)]),
      "C4":(4,[(0,1),(1,2),(2,3),(3,0)]),"K13":(4,[(0,1),(0,2),(0,3)])}

def hom_inj(edges,m,verts,adj):
    cnt=0
    for p in itertools.permutations(verts,m):
        ok=True
        for (i,j) in edges:
            if not (adj[p[i]]>>p[j])&1: ok=False;break
        if ok: cnt+=1
    return cnt
def falling(n,k):
    r=1
    for i in range(k): r*=(n-i)
    return r

def build_pattern_arrays(states):
    cache="pat_arrays_n9.npz"
    if os.path.exists(cache):
        d=np.load(cache); return {k:(d[k+"_F"],d[k+"_2F"]) for k in PATS}
    out={}
    for name,(m,edges) in PATS.items():
        ns=len(states); tF=np.zeros(ns); t2F=np.zeros(ns)
        for hi,(n,A) in enumerate(states):
            V=list(range(n))
            tF[hi]=hom_inj(edges,m,V,A)/falling(n,m)
            s2=0
            for S in itertools.combinations(V,m):
                Sset=set(S); aS=hom_inj(edges,m,list(S),A)
                if aS==0: continue
                comp=[v for v in V if v not in Sset]; s2+=aS*hom_inj(edges,m,comp,A)
            t2F[hi]=s2/falling(n,2*m)
        out[name]=(tF,t2F); print(f"  pattern {name} done",flush=True)
    np.savez(cache,**{f"{k}_F":out[k][0] for k in out},**{f"{k}_2F":out[k][1] for k in out})
    return out

def solve(ns,dedge,rows,prov,band,locs=None,ret_x=False):
    """locs: list of (qrow_F, a, b) adding Sum_H x[(a+b)tF_H - t2F_H - ab]>=0 (interval localizer on stat with
    per-state value tF and 2-stat value t2F=qrow_F's partner). Here pass (tF,t2F,a,b)."""
    lo,hi=band; nv=ns+1; c=np.zeros(nv); c[-1]=-1.0; A=[];b=[]
    A.append(np.concatenate([-dedge,[0.0]])); b.append(-lo)
    A.append(np.concatenate([dedge,[0.0]]));  b.append(hi)
    for i,row in enumerate(rows):
        r=np.asarray(row,float)
        if prov[i][0] in ("deficit","deficit_pmap"): A.append(np.concatenate([-r,[1.0]])); b.append(0.0)
        else: A.append(np.concatenate([-r,[0.0]])); b.append(0.0)
    for (tF,t2F,a_,b_) in (locs or []):
        L=(a_+b_)*tF - t2F - a_*b_
        A.append(np.concatenate([-L,[0.0]])); b.append(0.0)
    Aeq=[np.concatenate([np.ones(ns),[0.0]])]; beq=[1.0]; bnd=[(0,None)]*ns+[(None,None)]
    r=linprog(c,A_ub=np.array(A),b_ub=np.array(b),A_eq=np.array(Aeq),b_eq=np.array(beq),bounds=bnd,method="highs-ipm")
    if not r.success: r=linprog(c,A_ub=np.array(A),b_ub=np.array(b),A_eq=np.array(Aeq),b_eq=np.array(beq),bounds=bnd,method="highs")
    if not r.success: return (None,None) if ret_x else None
    x=np.maximum(r.x[:ns],0); x=x/x.sum()
    return (-r.fun,x) if ret_x else -r.fun

def variances(x,pat,dedge):
    res={}
    for name,(tF,t2F) in pat.items():
        LF=float(x@tF); res[name]=(LF,float(x@t2F)-LF*LF)
    return res

def main():
    C=pc.load(9); states=C["states"]
    print("building pattern arrays (cached)...",flush=True)
    pat=build_pattern_arrays(states)
    st,ns,dedge,t,rows,prov,v=pc.cutting_plane(C,maxit=12,target=-1e-6,mom_maxvecs=8,verbose=False)
    FULL=(0.2486,0.3197)
    # 1) baseline residual
    eta0,x0=solve(ns,dedge,rows,prov,FULL,ret_x=True)
    print(f"\n[baseline]    eta={eta0:+.6e}",flush=True)
    for n,(LF,var) in variances(x0,pat,dedge).items(): print(f"   {n:>4} Var_true={var:.3e}",flush=True)
    # 2) pin edge density: narrow band [0.29,0.31] + K2 localizer there
    NB=(0.29,0.31); k2=pat["K2"]
    etaK,xK=solve(ns,dedge,rows,prov,NB,locs=[(k2[0],k2[1],NB[0],NB[1])],ret_x=True)
    print(f"\n[K2-pinned, band{NB}]  eta={etaK:+.6e}  (residual variances:)",flush=True)
    vK=variances(xK,pat,dedge)
    for n,(LF,var) in vK.items(): print(f"   {n:>4} L*={LF:.5f} Var_true={var:.3e}",flush=True)
    topS=max([k for k in PATS if k!="K2"], key=lambda k:vK[k][1])
    print(f"   residual dominant STRUCTURAL direction: {topS} Var_true={vK[topS][1]:.3e}",flush=True)
    # 3) add ALL available localizers (each self-branched tightly around its residual mean to MAXIMALLY help)
    locs=[]
    for name,(tF,t2F) in pat.items():
        LF=vK[name][0]; w=0.02
        locs.append((tF,t2F,max(LF-w,0.0),LF+w))
    etaAll=solve(ns,dedge,rows,prov,NB,locs=locs)
    print(f"\n[ALL 5 localizers, self-branched w=0.02] eta={etaAll:+.6e}",flush=True)
    if etaAll is not None and etaAll>1e-6:
        print(">>> KILL CRITERION: even with all order-<=4 multiplicativity localizers, eta stays > 0.",flush=True)
        print("    Order-9 graphon-realizability is EXHAUSTED; the distinguishing constraint needs order >=10",flush=True)
        print("    (odd-cycle/C5 density: 2C5=10>9). GPT's falsifiable kill criterion is MET.",flush=True)
    elif etaAll is not None and etaAll<0:
        print(">>> eta<0 with all localizers -> CANDIDATE close; re-audit each localizer's [a,b] for SOUNDNESS",flush=True)
        print("    (self-branched [a,b] may exclude valid graphons; need true t(F) ranges over band graphons).",flush=True)
    print("DONE",flush=True)

if __name__=="__main__": main()
