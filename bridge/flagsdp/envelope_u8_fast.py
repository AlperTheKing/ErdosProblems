#!/usr/bin/env python3
"""Same U_8 per-R envelope LP, but x eliminated via x=Dq (drops 1897 vars + 1897 E10 equalities => much faster).
Vars [q(nJ) | eta | u_R(nR>=0)]. All x-functionals pulled back: f.x = (D^T f).q.
  eq:  (1^T D).q = 1
  band lo <= (D^T dedge).q <= hi
  SOUND validity rows (D^T row).q >= 0    (deficit rows EXCLUDED)
  coupling eta - sum u_R <= -2/25
  per-R u_R <= L_{R,c}(q)
max eta;  eta<=0 => U_8<=2/25 on band => d_mono<=2/25 SOUNDLY.
"""
import numpy as np, pickle, time
from scipy.optimize import linprog
from scipy.sparse import csr_matrix, vstack
from cutting_plane_u8 import maxcut_coloring
LO,HI=0.2486,0.3197

def run(maxit=60, tol=1e-9, method="highs-ds"):
    ns,dedge,rows,provtypes,_=pickle.load(open("cp_cache.pkl","rb"))
    d=np.load("c5lift_cache.npz",allow_pickle=True)
    D=csr_matrix((d["Dval"],(d["Drow"],d["Dcol"])),shape=(ns,int(d["nJ"]))); nJ=D.shape[1]
    DT=D.T.tocsr()
    D9=pickle.load(open("u8_decomp.pkl","rb")); decomp=D9["decomp"]; nR=D9["nR"]
    q0=np.load("witness.npz",allow_pickle=True)["q"]
    val_idx=[i for i in range(len(rows)) if provtypes[i] not in ("deficit","deficit_pmap")]
    print(f"ns={ns} nJ={nJ} nR={nR}; validity rows={len(val_idx)}/{len(rows)}; x eliminated.",flush=True)
    nv=nJ+1+nR; ETA=nJ; UO=nJ+1
    dedge_q=np.asarray(DT@dedge).ravel()
    sum_q=np.asarray(D.sum(axis=0)).ravel()         # 1^T D
    val_q=[np.asarray(DT@np.asarray(rows[i])).ravel() for i in val_idx]
    # static rows (sparse)
    static=[]; sb=[]
    static.append(csr_matrix((dedge_q,(np.zeros(nJ,int),np.arange(nJ))),shape=(1,nv))); sb.append(HI)
    static.append(csr_matrix((-dedge_q,(np.zeros(nJ,int),np.arange(nJ))),shape=(1,nv))); sb.append(-LO)
    for vq in val_q:
        static.append(csr_matrix((-vq,(np.zeros(nJ,int),np.arange(nJ))),shape=(1,nv))); sb.append(0.0)
    cpl=np.zeros(nv); cpl[ETA]=1.0; cpl[UO:UO+nR]=-1.0
    static.append(csr_matrix(cpl)); sb.append(-2.0/25.0)
    Aeq=csr_matrix((sum_q,(np.zeros(nJ,int),np.arange(nJ))),shape=(1,nv)); beq=[1.0]
    cobj=np.zeros(nv); cobj[ETA]=-1.0
    bounds=[(0,None)]*nJ+[(None,None)]+[(0,None)]*nR
    env=[]   # list of csr (1,nv)
    def solve():
        A=vstack(static+env,format="csr"); b=np.concatenate([sb,np.zeros(len(env))])
        rr=linprog(cobj,A_ub=A,b_ub=b,A_eq=Aeq,b_eq=beq,bounds=bounds,method=method)
        if (not rr.success or rr.x is None) and method!="highs":
            rr=linprog(cobj,A_ub=A,b_ub=b,A_eq=Aeq,b_eq=beq,bounds=bounds,method="highs")
        if rr.success and rr.x is not None:
            return float(-rr.fun), np.asarray(rr.x[:nJ]), np.asarray(rr.x[UO:UO+nR])
        return None,None,None
    def maxcut_colorings(q):
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
        return cm
    def add_rows(cm, q, u, force=False):
        acc={rid:{} for rid in cm}
        for jj in range(nJ):
            dl=decomp[jj]
            for (rd,Aset,Bset) in dl:
                if rd in cm and cm[rd].get(Aset,0)==cm[rd].get(Bset,0):
                    a=acc[rd]; a[jj]=a.get(jj,0)+1
        added=0
        for rid,a in acc.items():
            js=np.fromiter(a.keys(),int,len(a)); cs=np.fromiter(a.values(),float,len(a))/90.0
            Lval=float(cs@q[js]) if len(js) else 0.0
            if force or (u is not None and u[rid] > Lval+tol):
                data=np.concatenate([-cs,[1.0]]); cols=np.concatenate([js,[UO+rid]])
                env.append(csr_matrix((data,(np.zeros(len(cols),int),cols)),shape=(1,nv))); added+=1
        return added
    # seed: ALL 410 u_R must be bounded (else eta<=sum u_R-2/25 unbounded). Uniform q hits every R; add witness too.
    quni=np.ones(nJ)/nJ
    add_rows(maxcut_colorings(quni), quni, None, force=True)
    add_rows(maxcut_colorings(q0), q0, None, force=True)
    nseed_R=len(set(int(e.indices[-1]) for e in env))   # distinct R's bounded
    print(f"seeded {len(env)} cuts covering {nseed_R}/{nR} R's; solving...",flush=True)
    eta,q,u=solve(); t0=time.time()
    print(f"iter0: eta={eta:+.7e} [{time.time()-t0:.0f}s]",flush=True)
    if q is None: print("INFEASIBLE at iter0"); return
    for it in range(1,maxit+1):
        ts=time.time(); added=add_rows(maxcut_colorings(q),q,u)
        if added==0: print(f"CONVERGED it{it}: eta={eta:+.7e}",flush=True); break
        eta,q,u=solve()
        if eta is None: print(f"it{it}: INFEASIBLE -> CLOSED(float)",flush=True); break
        print(f"it{it}: +{added} (pool {len(env)}) eta={eta:+.7e} [{time.time()-ts:.0f}s]",flush=True)
        if eta<=tol:
            print(f">>> eta<=0 -> CANDIDATE CLOSURE; saving.",flush=True)
            pickle.dump(dict(env=[(e.data.tolist(),e.indices.tolist()) for e in env],eta=eta),
                        open("envelope_u8_state.pkl","wb"),protocol=4); break
    print(f"FINAL envelope-u8-fast eta={eta:+.7e}  (closed iff <=0)",flush=True)
    return eta

if __name__=="__main__":
    print("=== order-10 per-R U_8 envelope (x-eliminated, fast) ===",flush=True)
    run(); print("DONE",flush=True)
