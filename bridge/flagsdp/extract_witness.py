#!/usr/bin/env python3
"""Extract the EXACT primal witness: the order-10-lifted pseudo-state (x order-9 densities, q order-10 extension)
achieving d_mono=2/25+~6e-5 under order-9 moments + E10 marginal. Save x,q + basic diagnostics for GPT's path (A)
(diagnose the separating constraint). Reuses cp_cache.pkl + c5lift_cache.npz."""
import numpy as np, pickle
from scipy.optimize import linprog
from scipy.sparse import csr_matrix, hstack, vstack, coo_matrix
import prove_cert as pc
LO,HI=0.2486,0.3197
def main():
    C=pc.load(9); ns,dedge,rows,provtypes,v=pickle.load(open("cp_cache.pkl","rb"))
    d=np.load("c5lift_cache.npz",allow_pickle=True)
    D=csr_matrix((d["Dval"],(d["Drow"],d["Dcol"])),shape=(ns,int(d["nJ"]))); nJ=D.shape[1]
    pC5=d["pC5"]; gam=np.asarray(d["gam"],float); nv=ns+nJ+1
    ub=[]; ub_b=[]
    r=np.zeros(nv); r[:ns]=dedge; ub.append(r.copy()); ub_b.append(HI)
    r=np.zeros(nv); r[:ns]=-dedge; ub.append(r.copy()); ub_b.append(-LO)
    for i,row in enumerate(rows):
        r=np.zeros(nv)
        if provtypes[i] in ("deficit","deficit_pmap"): r[:ns]=-row; r[-1]=1.0
        else: r[:ns]=-row
        ub.append(r); ub_b.append(0.0)
    A_ub=csr_matrix(np.array(ub)); b_ub=np.array(ub_b)
    negI=coo_matrix((-np.ones(ns),(np.arange(ns),np.arange(ns))),shape=(ns,ns))
    E10=hstack([negI,D,csr_matrix((ns,1))],format="csr")
    sumx=np.zeros((1,nv)); sumx[0,:ns]=1.0
    A_eq=vstack([E10,csr_matrix(sumx)],format="csr"); b_eq=np.concatenate([np.zeros(ns),[1.0]])
    cobj=np.zeros(nv); cobj[-1]=-1.0; bounds=[(0,None)]*(ns+nJ)+[(None,None)]
    print("solving order-10 LP for witness...",flush=True)
    res=linprog(cobj,A_ub=A_ub,b_ub=b_ub,A_eq=A_eq,b_eq=b_eq,bounds=bounds,method="highs-ipm")
    eta=-res.fun; x=res.x[:ns]; q=res.x[ns:ns+nJ]
    np.savez("witness.npz", x=x, q=q, eta=eta, dedge=dedge, pC5=pC5)
    print(f"witness saved: eta={eta:+.7e}, d_edge={float(x@dedge):.5f}, t(C5)={float(x@pC5):.5e}",flush=True)
    sx=np.argsort(-x)[:10]; print("top-10 x states (idx:prob):", [(int(i),round(float(x[i]),4)) for i in sx],flush=True)
    sq=np.argsort(-q)[:10]; print("top-10 q states (idx:prob):", [(int(i),round(float(q[i]),4)) for i in sq],flush=True)
    print(f"x support={(x>1e-7).sum()}, q support={(q>1e-7).sum()}",flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
