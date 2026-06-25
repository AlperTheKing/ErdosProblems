#!/usr/bin/env python3
"""Adaptive-Q diagnostic: at the fooling x*, compute the TRUE between-component variance Var_true(F)=
Sum_x* t(2F,H) - (Sum_x* t(F,H))^2 for every order-<=4 connected triangle-free statistic F (K2,P3,P4,C4,K13).
These are the ONLY branchable directions at order 9 (2F must fit in <=8 vertices; the key odd-cycle C5 needs
2C5=10 > 9 -- a structural limit). Whichever F has the largest Var_true is GPT's dominant adaptive Q to branch
on. If ALL are tiny, the fooling is invisible to <=4-vertex even statistics (C5-blowup vs bipartite hides in
odd cycles) => order-9 kill criterion likely. t(F,H), t(2F,H) via exact subset decomposition (sound, unbiased).
"""
import numpy as np, itertools
from math import comb
from scipy.optimize import linprog
import prove_cert as pc

# patterns: (num vertices, edge list)
PATS = {
 "K2":  (2, [(0,1)]),
 "P3":  (3, [(0,1),(1,2)]),
 "P4":  (4, [(0,1),(1,2),(2,3)]),
 "C4":  (4, [(0,1),(1,2),(2,3),(3,0)]),
 "K13": (4, [(0,1),(0,2),(0,3)]),
}

def hom_inj(edges, m, verts, adj):
    """# injective edge-preserving maps from pattern(m verts, edges) into induced subgraph on `verts`."""
    cnt = 0
    for p in itertools.permutations(verts, m):
        ok = True
        for (i,j) in edges:
            if not (adj[p[i]] >> p[j]) & 1:
                ok = False; break
        if ok: cnt += 1
    return cnt

def falling(n,k):
    r=1
    for i in range(k): r*=(n-i)
    return r

def state_tF_t2F(states, name):
    m, edges = PATS[name]
    ns=len(states); tF=np.zeros(ns); t2F=np.zeros(ns)
    for hi,(n,A) in enumerate(states):
        adj=A
        V=list(range(n))
        # t(F): hom_inj over all of H / (n)_m
        hF_total = hom_inj(edges, m, V, adj)
        tF[hi] = hF_total/falling(n,m)
        # t(2F): sum over m-subsets S of hom_inj(F,S)*hom_inj(F, complement) / (n)_{2m}
        s2=0
        for S in itertools.combinations(V, m):
            Sset=set(S); comp=[v for v in V if v not in Sset]
            aS=hom_inj(edges,m,list(S),adj)
            if aS==0: continue
            bC=hom_inj(edges,m,comp,adj)
            s2 += aS*bC
        t2F[hi]=s2/falling(n,2*m)
    return tF,t2F

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
    C=pc.load(9); states=C["states"]
    # sanity: on a single dense state, t(2F) ~ t(F)^2
    st,ns,dedge,t,rows,prov,v=pc.cutting_plane(C,maxit=12,target=-1e-6,mom_maxvecs=8,verbose=False)
    eta,x=xstar(ns,dedge,rows,prov)
    print(f"eta*={eta:+.6e}  pbar={float(x@dedge):.5f}",flush=True)
    print(f"{'F':>5} {'L*(F)':>10} {'L*(2F)':>10} {'L*(F)^2':>10} {'Var_true':>11} {'std':>8}",flush=True)
    results={}
    for name in PATS:
        tF,t2F=state_tF_t2F(states,name)
        LF=float(x@tF); L2F=float(x@t2F); var=L2F-LF*LF
        results[name]=(LF,L2F,var)
        print(f"{name:>5} {LF:10.5f} {L2F:10.5f} {LF*LF:10.5f} {var:11.4e} {max(var,0)**0.5:8.4f}",flush=True)
    top=max(results,key=lambda k: results[k][2])
    print(f">>> dominant adaptive Q (largest true between-variance) = {top}  Var_true={results[top][2]:.4e}",flush=True)
    big=[k for k in results if results[k][2]>5e-4]
    if big:
        print(f">>> branchable structural directions (Var_true>5e-4): {big} -> implement McCormick branching on these",flush=True)
    else:
        print(">>> ALL <=4-vertex statistics have tiny true variance -> fooling hides in odd-cycle (C5) direction",flush=True)
        print("    invisible at order 9 (2C5=10) => GPT kill criterion LIKELY; order-9 realizability exhausted.",flush=True)
    print("DONE",flush=True)

if __name__=="__main__": main()
