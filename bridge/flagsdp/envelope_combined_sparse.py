#!/usr/bin/env python3
"""COMBINED k7+k8 envelope, x EXPLICIT (k7 cut rows stay sparse over x(1897); k8 over q; E10 couples x=Dq).
Avoids the dense D^T pullback (which bloated the x-eliminated version to 4GB). Vars [x|q|eta|u7|u8].
Same math: eta <= min(sum u7, sum u8 - 2/25); u7_s <= g_{s,c}(x); u8_R <= L_{R,c}(q). max eta; eta<=0 => closed.
"""
import numpy as np, pickle, time
from scipy.optimize import linprog
from scipy.sparse import csr_matrix, coo_matrix, hstack, vstack
import flag_cutgen as fc
from run_k7b import sep_multi, precompute_k7
from cutting_plane_u8 import maxcut_coloring
LO,HI=0.2486,0.3197

def run(maxit=120, tol=1e-9, method="highs"):
    ns,dedge,rows,provtypes,_=pickle.load(open("cp_cache.pkl","rb"))
    C=pickle.load(open("cache_n9.pkl","rb")); states=C["states"]; t=C["t"]; assert len(states)==ns
    d=np.load("c5lift_cache.npz",allow_pickle=True)
    D=csr_matrix((d["Dval"],(d["Drow"],d["Dcol"])),shape=(ns,int(d["nJ"]))); nJ=D.shape[1]
    D9=pickle.load(open("u8_decomp.pkl","rb")); decomp=D9["decomp"]; nR=D9["nR"]
    q0=np.load("witness.npz",allow_pickle=True)["q"]
    dt7=precompute_k7(states); n7=len(dt7)
    val_idx=[i for i in range(len(rows)) if provtypes[i] not in ("deficit","deficit_pmap")]
    print(f"ns={ns} nJ={nJ} n7={n7} nR={nR}; validity={len(val_idx)}; x EXPLICIT.",flush=True)
    X=0; Q=ns; ETA=ns+nJ; U7=ns+nJ+1; U8=ns+nJ+1+n7; nv=ns+nJ+1+n7+nR
    # equalities E10 (x - Dq = 0) and sum x = 1
    negI=coo_matrix((-np.ones(ns),(np.arange(ns),np.arange(ns))),shape=(ns,ns))
    E10=hstack([negI,D,csr_matrix((ns,1+n7+nR))],format="csr")
    sx=np.zeros((1,nv)); sx[0,:ns]=1.0
    Aeq=vstack([E10,csr_matrix(sx)],format="csr"); beq=np.concatenate([np.zeros(ns),[1.0]])
    def sprow(dd):
        cols=np.fromiter(dd.keys(),int,len(dd)); data=np.fromiter(dd.values(),float,len(dd))
        return csr_matrix((data,(np.zeros(len(cols),int),cols)),shape=(1,nv))
    static=[]; sb=[]
    static.append(sprow({X+i:dedge[i] for i in range(ns) if dedge[i]})); sb.append(HI)
    static.append(sprow({X+i:-dedge[i] for i in range(ns) if dedge[i]})); sb.append(-LO)
    for i in val_idx:
        r=np.asarray(rows[i]); static.append(sprow({X+j:-r[j] for j in range(ns) if r[j]})); sb.append(0.0)
    static.append(sprow({ETA:1.0,**{U7+i:-1.0 for i in range(n7)}})); sb.append(0.0)
    static.append(sprow({ETA:1.0,**{U8+i:-1.0 for i in range(nR)}})); sb.append(-2.0/25.0)
    cobj=np.zeros(nv); cobj[ETA]=-1.0
    bounds=[(0,None)]*ns+[(0,None)]*nJ+[(None,None)]+[(0,None)]*(n7+nR)
    env=[]
    def solve():
        A=vstack(static+env,format="csr"); b=np.concatenate([sb,np.zeros(len(env))])
        rr=linprog(cobj,A_ub=A,b_ub=b,A_eq=Aeq,b_eq=beq,bounds=bounds,method=method)
        if rr.success and rr.x is not None:
            x=np.asarray(rr.x[:ns]); q=np.asarray(rr.x[Q:Q+nJ])
            return float(-rr.fun),x,q,np.asarray(rr.x[U7:U7+n7]),np.asarray(rr.x[U8:U8+nR])
        return None,None,None,None,None
    def sep_k7(x,q,u7,force=False):
        added=0
        for i,(k,A,E,S,cls) in enumerate(dt7):
            ps,gs=sep_multi(E,S,x,t,1e9,tol,keep=1)
            for p in ps:
                g=np.asarray(fc.cut_from_p(E,S,p,t)); Lx=float(g@x)
                if force or (u7 is not None and u7[i]>Lx+tol):
                    env.append(sprow({U7+i:1.0,**{X+j:-float(g[j]) for j in np.nonzero(g)[0]}})); added+=1
        return added
    def sep_k8(q,u8,force=False):
        W=[dict() for _ in range(nR)]; sup=np.where(q>1e-12)[0]
        for jj in sup:
            qj=float(q[jj])
            for (rid,Aset,Bset) in decomp[jj]:
                key=(Aset,Bset) if (len(Aset),Aset)<=(len(Bset),Bset) else (Bset,Aset)
                W[rid][key]=W[rid].get(key,0.0)+qj/90.0
        cm={}
        for rid in range(nR):
            if not W[rid]: continue
            profs=set(); off={}
            for (a,b),w in W[rid].items():
                profs.add(a); profs.add(b)
                if a!=b: off[(a,b)]=off.get((a,b),0.0)+w
            cm[rid]=maxcut_coloring(list(profs),off)
        acc={rid:{} for rid in cm}
        for jj in range(nJ):
            for (rd,Aset,Bset) in decomp[jj]:
                if rd in cm and cm[rd].get(Aset,0)==cm[rd].get(Bset,0):
                    a=acc[rd]; a[jj]=a.get(jj,0)+1
        added=0
        for rid,a in acc.items():
            js=list(a.keys()); cs=np.array([a[j] for j in js])/90.0
            Lval=float(cs@q[js]) if js else 0.0
            if force or (u8 is not None and u8[rid]>Lval+tol):
                env.append(sprow({U8+rid:1.0,**{Q+jj:-float(c) for jj,c in zip(js,cs)}})); added+=1
        return added
    quni=np.ones(nJ)/nJ; xuni=np.asarray(D@quni).ravel()
    sep_k7(xuni,quni,None,force=True); sep_k8(quni,None,force=True); sep_k8(q0,None,force=True)
    print(f"seeded {len(env)} cuts; solving (method={method})...",flush=True)
    eta,x,q,u7,u8=solve(); print(f"iter0: eta={eta:+.7e}",flush=True)
    if x is None: print("INFEASIBLE iter0"); return
    for it in range(1,maxit+1):
        ts=time.time(); a7=sep_k7(x,q,u7); a8=sep_k8(q,u8); added=a7+a8
        if added==0: print(f"CONVERGED it{it}: eta={eta:+.7e}",flush=True); break
        eta,x,q,u7,u8=solve()
        if eta is None: print(f"it{it}: INFEASIBLE -> CLOSED(float)",flush=True); break
        print(f"it{it}: +{a7}k7 +{a8}k8 (pool {len(env)}) eta={eta:+.7e} [{time.time()-ts:.0f}s]",flush=True)
        if eta<=tol:
            print(f">>> eta<=0 -> CANDIDATE CLOSURE; saving.",flush=True)
            pickle.dump(dict(env=[(e.data.tolist(),e.indices.tolist()) for e in env],eta=eta),
                        open("envelope_combined_sparse_state.pkl","wb"),protocol=4); break
    print(f"FINAL combined-sparse eta={eta:+.7e}  (closed iff <=0)",flush=True)
    return eta

if __name__=="__main__":
    print("=== COMBINED k7+k8 envelope (x explicit, sparse) ===",flush=True)
    run(); print("DONE",flush=True)
