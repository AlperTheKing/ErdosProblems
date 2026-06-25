#!/usr/bin/env python3
"""CORRECTION to proto7: cross-multiplicativity t(H+K2)=t(H)*t(K2) for H up to 7 vertices DOES fit order 9
(H+K2 <= 9). GPT's method explicitly includes these. The KEY one is H=C5 (the odd cycle distinguishing the
C5-blowup extremal from bipartite graphs): in a C5-blowup t(C5)>0, in any bipartite graph t(C5)=0, so a mixture
of the two has Cov(t(C5),t(K2)) != 0 -- a violation that the C5+K2 McCormick (an order-9 constraint!) excludes.
Measure Cov(t(H),t(K2)) = t(H+K2) - t(H)*t(K2) at the fooling x* and the edge-pinned x' for H in odd/even cycles
and paths up to 7 vtx. Large Cov => the missing order-9 multiplicativity constraint; proceed to add it & re-solve.
"""
import numpy as np, itertools, os
from scipy.optimize import linprog
import prove_cert as pc

# triangle-free patterns up to 7 vertices (cross with K2 keeps <=9)
PATS={
 "P3":(3,[(0,1),(1,2)]),
 "P4":(4,[(0,1),(1,2),(2,3)]),
 "C4":(4,[(0,1),(1,2),(2,3),(3,0)]),
 "C5":(5,[(0,1),(1,2),(2,3),(3,4),(4,0)]),
 "P5":(5,[(0,1),(1,2),(2,3),(3,4)]),


}
K2=(2,[(0,1)])

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

def arrays_HxK2(states,name):
    """per-state t(H), t(H+K2)."""
    m,edges=PATS[name]; ns=len(states); tH=np.zeros(ns); tHK2=np.zeros(ns)
    for hi,(n,A) in enumerate(states):
        V=list(range(n))
        tH[hi]=hom_inj(edges,m,V,A)/falling(n,m)
        s=0
        for S in itertools.combinations(V,m):
            Sset=set(S); aS=hom_inj(edges,m,list(S),A)
            if aS==0: continue
            comp=[v for v in V if v not in Sset]
            s+=aS*hom_inj(K2[1],2,comp,A)     # place the disjoint edge in the complement
        tHK2[hi]=s/falling(n,m+2)
    return tH,tHK2

def xstar(ns,dedge,rows,prov,band,locs=None):
    lo,hi=band; nv=ns+1; c=np.zeros(nv); c[-1]=-1.0; A=[];b=[]
    A.append(np.concatenate([-dedge,[0.0]])); b.append(-lo)
    A.append(np.concatenate([dedge,[0.0]]));  b.append(hi)
    for i,row in enumerate(rows):
        r=np.asarray(row,float)
        if prov[i][0] in ("deficit","deficit_pmap"): A.append(np.concatenate([-r,[1.0]])); b.append(0.0)
        else: A.append(np.concatenate([-r,[0.0]])); b.append(0.0)
    for (tF,t2F,a_,b_) in (locs or []):
        L=(a_+b_)*tF - t2F - a_*b_; A.append(np.concatenate([-L,[0.0]])); b.append(0.0)
    Aeq=[np.concatenate([np.ones(ns),[0.0]])]; beq=[1.0]; bnd=[(0,None)]*ns+[(None,None)]
    r=linprog(c,A_ub=np.array(A),b_ub=np.array(b),A_eq=np.array(Aeq),b_eq=np.array(beq),bounds=bnd,method="highs-ipm")
    if not r.success: r=linprog(c,A_ub=np.array(A),b_ub=np.array(b),A_eq=np.array(Aeq),b_eq=np.array(beq),bounds=bnd,method="highs")
    x=np.maximum(r.x[:ns],0); return -r.fun,x/x.sum()

def main():
    C=pc.load(9); states=C["states"]; dK2=np.asarray(C["dedge"],float)
    st,ns,dedge,t,rows,prov,v=pc.cutting_plane(C,maxit=12,target=-1e-6,mom_maxvecs=8,verbose=False)
    FULL=(0.2486,0.3197)
    eta0,x0=xstar(ns,dedge,rows,prov,FULL)
    print(f"baseline eta={eta0:+.6e}  pbar={float(x0@dK2):.5f}\n",flush=True)
    print("computing t(H), t(H+K2) per state and Cov(t(H),t(K2)) at fooling x*:",flush=True)
    print(f"{'H':>4} {'L*(H)':>9} {'L*(H+K2)':>10} {'L*(H)*p':>10} {'Cov(H,K2)':>11}",flush=True)
    cov={}
    for name in PATS:
        tH,tHK2=arrays_HxK2(states,name)
        LH=float(x0@tH); LHK2=float(x0@tHK2); p=float(x0@dK2)
        cov[name]=(LH,LHK2,LHK2-LH*p,tH,tHK2)
        print(f"{name:>4} {LH:9.5f} {LHK2:10.6f} {LH*p:10.6f} {cov[name][2]:+11.3e}",flush=True)
    top=max(PATS,key=lambda k:abs(cov[k][2]))
    print(f"\n>>> largest |Cov(t(H),t(K2))| = {top}: {cov[top][2]:+.3e}",flush=True)
    if abs(cov[top][2])>5e-4:
        print(f">>> the {top}+K2 multiplicativity (an ORDER-9 constraint) IS violated at x* -> NOT exhausted;",flush=True)
        print(f"    implement the {top}+K2 McCormick and re-solve. Kill criterion was PREMATURE.",flush=True)
    else:
        print(">>> even C5/C7 cross-multiplicativity with K2 is ~satisfied -> kill criterion stands.",flush=True)
    print("DONE",flush=True)

if __name__=="__main__": main()
