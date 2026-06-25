#!/usr/bin/env python3
"""Faster order-10 + C5-diagonal: cache cutting_plane; compute c-range once; branch + envelope; max eta."""
import numpy as np, os, pickle
from scipy.optimize import linprog
from scipy.sparse import csr_matrix, hstack, vstack, coo_matrix
import prove_cert as pc
LO,HI=0.2486,0.3197

def get_cp(C):
    if os.path.exists("cp_cache.pkl"): return pickle.load(open("cp_cache.pkl","rb"))
    st,ns,dedge,t,rows,prov,v=pc.cutting_plane(C,maxit=12,target=-1e-6,mom_maxvecs=8,verbose=False)
    out=(ns,np.asarray(dedge,float),[np.asarray(r,float) for r in rows],[p[0] for p in prov],v)
    pickle.dump(out,open("cp_cache.pkl","wb")); return out

def main():
    C=pc.load(9); ns,dedge,rows,provtypes,v=get_cp(C)
    d=np.load("c5lift_cache.npz",allow_pickle=True)
    D=csr_matrix((d["Dval"],(d["Drow"],d["Dcol"])),shape=(ns,int(d["nJ"]))); nJ=D.shape[1]
    pC5=d["pC5"]; gam=np.asarray(d["gam"],float); nv=ns+nJ+1
    # base ub
    ub=[]; ub_b=[]
    r=np.zeros(nv); r[:ns]=dedge; ub.append(r.copy()); ub_b.append(HI)
    r=np.zeros(nv); r[:ns]=-dedge; ub.append(r.copy()); ub_b.append(-LO)
    for i,row in enumerate(rows):
        r=np.zeros(nv)
        if provtypes[i] in ("deficit","deficit_pmap"): r[:ns]=-row; r[-1]=1.0
        else: r[:ns]=-row
        ub.append(r); ub_b.append(0.0)
    A_ub0=np.array(ub); b_ub0=np.array(ub_b)
    negI=coo_matrix((-np.ones(ns),(np.arange(ns),np.arange(ns))),shape=(ns,ns))
    E10=hstack([negI,D,csr_matrix((ns,1))],format="csr")
    sumx=np.zeros((1,nv)); sumx[0,:ns]=1.0
    A_eq=vstack([E10,csr_matrix(sumx)],format="csr"); b_eq=np.concatenate([np.zeros(ns),[1.0]])
    bounds=[(0,None)]*(ns+nJ)+[(None,None)]
    cobj=np.zeros(nv); cobj[-1]=-1.0
    def lp(extra_ub=None,extra_b=None,obj=cobj):
        Aub=A_ub0 if extra_ub is None else np.vstack([A_ub0,extra_ub])
        bub=b_ub0 if extra_b is None else np.concatenate([b_ub0,extra_b])
        return linprog(obj,A_ub=csr_matrix(Aub),b_ub=bub,A_eq=A_eq,b_eq=b_eq,bounds=bounds,method="highs")
    # c range
    cc=np.zeros(nv); cc[:ns]=pC5
    cmax=float(pC5@lp(obj=-cc).x[:ns]); cmin=float(pC5@lp(obj=cc).x[:ns])
    print(f"E10 eta={-lp().fun:+.7e}; c=pC5.x range [{cmin:.4e},{cmax:.4e}]",flush=True)
    K=4; edges=np.linspace(max(cmin,0.0),cmax*1.0001+1e-9,K+1); worst=-9e9; worstbr=None
    for bi in range(K):
        a,b=edges[bi],edges[bi+1]; eu=[]; eb=[]
        r=np.zeros(nv); r[ns:ns+nJ]=gam; r[:ns]-=(a+b)*pC5; eu.append(r.copy()); eb.append(-a*b)   # z<=(a+b)c-ab
        r=np.zeros(nv); r[ns:ns+nJ]=-gam; r[:ns]+=2*a*pC5; eu.append(r.copy()); eb.append(a*a)
        r=np.zeros(nv); r[ns:ns+nJ]=-gam; r[:ns]+=2*b*pC5; eu.append(r.copy()); eb.append(b*b)
        r=np.zeros(nv); r[:ns]=pC5; eu.append(r.copy()); eb.append(b)
        r=np.zeros(nv); r[:ns]=-pC5; eu.append(r.copy()); eb.append(-a)
        res=lp(np.array(eu),np.array(eb)); e=-res.fun if res.success else None
        if e is not None and e>worst: worst=e; worstbr=(a,b)
        print(f"  c in [{a:.4e},{b:.4e}]: eta={'INFEAS' if e is None else f'{e:+.6e}'}",flush=True)
    print(f"\n>>> ORDER-10 + C5-diagonal max eta = {worst:+.7e} at {worstbr}  (E10 {-lp().fun:+.6e}, order-9 {v:+.6e})",flush=True)
    if worst<0: print("    >>> eta<0 ALL branches => band CLOSED (float) -> build EXACT cert.",flush=True)
    elif worst<v-1e-7: print("    helps further but not closing.",flush=True)
    print("DONE",flush=True)

if __name__=="__main__": main()
