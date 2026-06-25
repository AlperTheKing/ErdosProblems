#!/usr/bin/env python3
"""DECISIVE kill-criterion test: at the EDGE-PINNED optimum x' (K2 localizer on a narrow band, so edge-density
variance ~0), compute the pairwise multiplicativity violations Cov(t(F),t(G))=t(F+G)-t(F)t(G) for F,G with
|F|+|G|<=9, focusing on the ODD cycle C5 vs even/path statistics. C5+C4 (9 vtx), C5+P4 (9), C5+P3 (8) ALL fit
order 9. If at fixed edge density the C5 covariances are SUBSTANTIAL, the odd-vs-even multiplicativity lever
exists -> implement it (kill criterion premature). If ALL near-zero (the edge-pinned residual is multiplicative
in every order-9 pair), the kill criterion is confirmed: order-9 realizability is exhausted, eta stays >0."""
import numpy as np, itertools
from scipy.optimize import linprog
import prove_cert as pc

PATS={
 "P3":(3,[(0,1),(1,2)]),"P4":(4,[(0,1),(1,2),(2,3)]),
 "C4":(4,[(0,1),(1,2),(2,3),(3,0)]),
 "C5":(5,[(0,1),(1,2),(2,3),(3,4),(4,0)]),"P5":(5,[(0,1),(1,2),(2,3),(3,4)]),
}
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

def tF_arr(states,name):
    m,edges=PATS[name]; ns=len(states); a=np.zeros(ns)
    for hi,(n,A) in enumerate(states): a[hi]=hom_inj(edges,m,list(range(n)),A)/falling(n,m)
    return a
def tFG_arr(states,nF,nG):
    mF,eF=PATS[nF]; mG,eG=PATS[nG]; ns=len(states); a=np.zeros(ns)
    for hi,(n,A) in enumerate(states):
        V=list(range(n)); s=0
        for S in itertools.combinations(V,mF):
            Sset=set(S); aS=hom_inj(eF,mF,list(S),A)
            if aS==0: continue
            comp=[v for v in V if v not in Sset]; s+=aS*hom_inj(eG,mG,comp,A)
        a[hi]=s/falling(n,mF+mG)
    return a

def solve(ns,dedge,rows,prov,band,locs=None):
    lo,hi=band; nv=ns+1; c=np.zeros(nv); c[-1]=-1.0; A=[];b=[]
    A.append(np.concatenate([-dedge,[0.0]])); b.append(-lo)
    A.append(np.concatenate([dedge,[0.0]]));  b.append(hi)
    for i,row in enumerate(rows):
        r=np.asarray(row,float)
        if prov[i][0] in ("deficit","deficit_pmap"): A.append(np.concatenate([-r,[1.0]])); b.append(0.0)
        else: A.append(np.concatenate([-r,[0.0]])); b.append(0.0)
    for (L,) in (locs or []): A.append(np.concatenate([-L,[0.0]])); b.append(0.0)
    Aeq=[np.concatenate([np.ones(ns),[0.0]])]; beq=[1.0]; bnd=[(0,None)]*ns+[(None,None)]
    r=linprog(c,A_ub=np.array(A),b_ub=np.array(b),A_eq=np.array(Aeq),b_eq=np.array(beq),bounds=bnd,method="highs-ipm")
    if not r.success: r=linprog(c,A_ub=np.array(A),b_ub=np.array(b),A_eq=np.array(Aeq),b_eq=np.array(beq),bounds=bnd,method="highs")
    x=np.maximum(r.x[:ns],0); return -r.fun,x/x.sum()

def main():
    C=pc.load(9); states=C["states"]; dedgeA=np.asarray(C["dedge"],float)
    st,ns,dedge,t,rows,prov,v=pc.cutting_plane(C,maxit=12,target=-1e-6,mom_maxvecs=8,verbose=False)
    # single-stat arrays
    tA={n:tF_arr(states,n) for n in PATS}
    # K2 interval localizer on narrow band to PIN edge density
    NB=(0.29,0.31); q2=None
    # build t(2K2) for the K2 localizer
    from math import comb
    q2=np.zeros(ns)
    for hi,(n,A) in enumerate(states):
        deg=[bin(A[u]).count("1") for u in range(n)]; E=sum(deg)//2
        M2=comb(E,2)-sum(comb(d,2) for d in deg); q2[hi]=8*M2/(n*(n-1)*(n-2)*(n-3))
    Lk2=(NB[0]+NB[1])*dedgeA - q2 - NB[0]*NB[1]
    etaP,xP=solve(ns,dedge,rows,prov,NB,locs=[(Lk2,)])
    print(f"[edge-pinned x', band{NB}] eta={etaP:+.6e}, edge mean={float(xP@dedgeA):.5f}\n",flush=True)
    pairs=[("C5","C4"),("C5","P4"),("C5","P3"),("C5","K2") if False else ("C4","P4"),("C4","C4"),("P4","P4"),("P3","P4"),("P3","P3")]
    print(f"{'F+G':>10} {'L(F+G)':>10} {'L(F)L(G)':>10} {'Cov':>11}",flush=True)
    maxc=0; maxp=None
    for (nF,nG) in pairs:
        tfg=tFG_arr(states,nF,nG)
        LFG=float(xP@tfg); LF=float(xP@tA[nF]); LG=float(xP@tA[nG]); cv=LFG-LF*LG
        print(f"{nF+'+'+nG:>10} {LFG:10.6f} {LF*LG:10.6f} {cv:+11.3e}",flush=True)
        if abs(cv)>maxc: maxc=abs(cv); maxp=(nF,nG)
    print(f"\n>>> largest |Cov| at FIXED edge density = {maxp}: {maxc:.3e}",flush=True)
    if maxc>5e-4:
        print(f">>> {maxp} multiplicativity (order-9) IS violated at fixed edge density -> lever EXISTS, NOT exhausted.",flush=True)
    else:
        print(">>> ALL order-9 pairwise multiplicativity ~satisfied at fixed edge density, yet eta>0.",flush=True)
        print("    => GPT KILL CRITERION CONFIRMED: order-9 graphon realizability is exhausted; the residual",flush=True)
        print("    fooling is an order-9-multiplicative pseudo-graphon at d_mono=2/25+6.4e-5. Need order>=10 or new ineq.",flush=True)
    print("DONE",flush=True)

if __name__=="__main__": main()
