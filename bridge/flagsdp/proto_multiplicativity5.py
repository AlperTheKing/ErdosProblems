#!/usr/bin/env python3
"""Diagnostic: at the fooling optimum x*, how much of the edge-density 'variance' is REAL between-component
variance vs within-9-sample artifact? Var_true(K2) = Sum_x* t(2K2,H) - (Sum_x* dedge)^2  [uses the sound 2K2
moment]; Var_biased = Sum_x* dedge^2 - (Sum_x* dedge)^2 (= 9.8e-3, what proto1 measured). If Var_true is large,
edge density IS a genuine fooling direction (McCormick should help with branching); if Var_true~0, the fooling
hides in a STRUCTURAL direction and we need the adaptive Q (covariance eigenvector over higher statistics)."""
import numpy as np
from math import comb
from scipy.optimize import linprog
import prove_cert as pc

def state_q2(states):
    ns=len(states); q2=np.zeros(ns)
    for hi,(n,A) in enumerate(states):
        deg=[bin(A[u]).count("1") for u in range(n)]; E=sum(deg)//2
        M2=comb(E,2)-sum(comb(d,2) for d in deg); n4=n*(n-1)*(n-2)*(n-3)
        q2[hi]=8*M2/n4 if n4 else 0.0
    return q2

def xstar(ns,dedge,rows,prov,band=(0.2486,0.3197)):
    lo,hi=band; nv=ns+1; c=np.zeros(nv); c[-1]=-1.0; A=[];b=[]
    A.append(np.concatenate([-dedge,[0.0]])); b.append(-lo)
    A.append(np.concatenate([dedge,[0.0]]));  b.append(hi)
    for i,row in enumerate(rows):
        r=np.asarray(row,float)
        if prov[i][0] in ("deficit","deficit_pmap"): A.append(np.concatenate([-r,[1.0]])); b.append(0.0)
        else: A.append(np.concatenate([-r,[0.0]])); b.append(0.0)
    Aeq=[np.concatenate([np.ones(ns),[0.0]])]; beq=[1.0]; bnd=[(0,None)]*ns+[(None,None)]
    r=linprog(c,A_ub=np.array(A),b_ub=np.array(b),A_eq=np.array(Aeq),b_eq=np.array(beq),bounds=bnd,method="highs-ipm")
    if not r.success: r=linprog(c,A_ub=np.array(A),b_ub=np.array(b),A_eq=np.array(Aeq),b_eq=np.array(beq),bounds=bnd,method="highs")
    x=np.maximum(r.x[:ns],0); return -r.fun, x/x.sum()

def main():
    C=pc.load(9); states=C["states"]; q2=state_q2(states)
    st,ns,dedge,t,rows,prov,v=pc.cutting_plane(C,maxit=12,target=-1e-6,mom_maxvecs=8,verbose=False)
    eta,x=xstar(ns,dedge,rows,prov)
    pbar=float(x@dedge)
    var_biased=float(x@(dedge*dedge))-pbar**2
    var_true=float(x@q2)-pbar**2
    print(f"eta*={eta:+.6e}  pbar={pbar:.5f}",flush=True)
    print(f"Var_biased(K2) = Sum x* dedge^2 - pbar^2     = {var_biased:.4e}   (within-sample + between)",flush=True)
    print(f"Var_true(K2)   = Sum x* t(2K2) - pbar^2      = {var_true:.4e}   (TRUE between-component)",flush=True)
    print(f"within-sample artifact = biased - true        = {var_biased-var_true:.4e}",flush=True)
    if var_true>1e-3:
        print(">>> edge density IS a genuine fooling direction (large true between-variance) -> McCormick+branching",flush=True)
        print("    on t(K2) should help once we BRANCH (single full-band constraint too weak). Pursue branching.",flush=True)
    else:
        print(">>> edge-density true between-variance is SMALL -> fooling hides in a STRUCTURAL direction; the",flush=True)
        print("    adaptive Q (covariance eigenvector over P3/C4/C5/... ) is REQUIRED, not edge density.",flush=True)
    print("DONE",flush=True)

if __name__=="__main__": main()
