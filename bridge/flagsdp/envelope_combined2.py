#!/usr/bin/env python3
"""COMBINED k7 + k8 per-root-MaxCut envelope LP (the sound formulation that should close).
Both are SOUND eta upper bounds on the SAME graphon (x = D q):
  k7:  eta <= sum_{sigma in T7} u7_sigma,   u7_sigma <= g_{sigma,c}(x)         (order-9, x=Dq; alone gave +6.06e-4)
  k8:  eta <= sum_R u8_R - 2/25,            u8_R <= L_{R,c}(q)                  (order-10 U_8; cuts witness 166x)
=> eta <= min(k7 bound, U_8-2/25). At the k7-worst-case q (eta~6e-4) the U_8 bound is NEGATIVE => eta<=0 => CLOSED.
Vars [q(nJ) | eta | u7(n7>=0) | u8(nR>=0)]; band + SOUND validity rows (deficit EXCLUDED); max eta.
Separation each iter: k7 = sep_multi MaxCut on x=Dq per T7 type; k8 = per-R MaxCut on q. eta<=0 => candidate closure.
"""
import numpy as np, pickle, time
from scipy.optimize import linprog
from scipy.sparse import csr_matrix, vstack
import flag_cutgen as fc
from run_k7b import sep_multi, precompute_k7
from cutting_plane_u8 import maxcut_coloring
LO,HI=0.2486,0.3197

def run(maxit=80, tol=1e-9, method="highs-ds"):
    ns,dedge,rows,provtypes,_=pickle.load(open("cp_cache.pkl","rb"))
    C=pickle.load(open("cache_n9.pkl","rb")); states=C["states"]; t=C["t"]; assert len(states)==ns
    d=np.load("c5lift_cache.npz",allow_pickle=True)
    D=csr_matrix((d["Dval"],(d["Drow"],d["Dcol"])),shape=(ns,int(d["nJ"]))); nJ=D.shape[1]; DT=D.T.tocsr()
    D9=pickle.load(open("u8_decomp.pkl","rb")); decomp=D9["decomp"]; nR=D9["nR"]
    gam=np.asarray(d["gam"]).ravel(); pC5=np.asarray(d["pC5"]).ravel()
    pC5q=np.asarray(DT@pC5).ravel()    # c(q)=pC5.x=(D^T pC5).q ; z(q)=gam.q ; valid: z>=c^2 (z=c^2 real)
    q0=np.load("witness.npz",allow_pickle=True)["q"]
    dt7=precompute_k7(states); n7=len(dt7)
    val_idx=[i for i in range(len(rows)) if provtypes[i] not in ("deficit","deficit_pmap")]
    print(f"ns={ns} nJ={nJ} n7={n7} nR={nR}; validity={len(val_idx)}; x=Dq eliminated.",flush=True)
    nv=nJ+1+n7+nR; ETA=nJ; U7=nJ+1; U8=nJ+1+n7
    dedge_q=np.asarray(DT@dedge).ravel(); sum_q=np.asarray(D.sum(axis=0)).ravel()
    val_q=[np.asarray(DT@np.asarray(rows[i])).ravel() for i in val_idx]
    def sprow(vec_cols, b=None):  # build (1,nv) csr from {col:val}
        cols=np.fromiter(vec_cols.keys(),int,len(vec_cols)); data=np.fromiter(vec_cols.values(),float,len(vec_cols))
        return csr_matrix((data,(np.zeros(len(cols),int),cols)),shape=(1,nv))
    static=[]; sb=[]
    static.append(sprow({j:dedge_q[j] for j in range(nJ) if dedge_q[j]})); sb.append(HI)
    static.append(sprow({j:-dedge_q[j] for j in range(nJ) if dedge_q[j]})); sb.append(-LO)
    for vq in val_q:
        static.append(sprow({j:-vq[j] for j in range(nJ) if vq[j]})); sb.append(0.0)
    static.append(sprow({ETA:1.0, **{U7+i:-1.0 for i in range(n7)}})); sb.append(0.0)        # eta<=sum u7
    static.append(sprow({ETA:1.0, **{U8+i:-1.0 for i in range(nR)}})); sb.append(-2.0/25.0)   # eta<=sum u8-2/25
    Aeq=sprow({j:sum_q[j] for j in range(nJ) if sum_q[j]}); beq=[1.0]
    cobj=np.zeros(nv); cobj[ETA]=-1.0
    bounds=[(0,None)]*nJ+[(None,None)]+[(0,None)]*(n7+nR)
    env=[]; env_b=[]
    def solve():
        A=vstack(static+env,format="csr"); b=np.concatenate([sb,np.asarray(env_b)])
        rr=linprog(cobj,A_ub=A,b_ub=b,A_eq=Aeq,b_eq=beq,bounds=bounds,method=method)
        if (not rr.success or rr.x is None) and method!="highs":
            rr=linprog(cobj,A_ub=A,b_ub=b,A_eq=Aeq,b_eq=beq,bounds=bounds,method="highs")
        if rr.success and rr.x is not None:
            return float(-rr.fun), np.asarray(rr.x[:nJ]), np.asarray(rr.x[U7:U7+n7]), np.asarray(rr.x[U8:U8+nR])
        return None,None,None,None
    # ---- k7 separation on x=Dq: u7_i <= g_{sigma,c}(x) = (D^T g).q ----
    def sep_k7(x, q, u7, force=False):
        added=0
        for i,(k,A,E,S,cls) in enumerate(dt7):
            ps,gs=sep_multi(E,S,x,t,1e9,tol,keep=1)
            for p in ps:
                g=fc.cut_from_p(E,S,p,t); gq=np.asarray(DT@np.asarray(g)).ravel()
                Lval=float(gq@q)
                if force or (u7 is not None and u7[i] > Lval+tol):
                    row={U7+i:1.0}
                    for j in np.nonzero(gq)[0]: row[int(j)]=row.get(int(j),0.0)-float(gq[j])
                    env.append(sprow(row)); env_b.append(0.0); added+=1
        return added
    # ---- k8 separation: per-R MaxCut on q, batched row build ----
    def sep_k8(q, u8, force=False):
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
            js=np.fromiter(a.keys(),int,len(a)); cs=np.fromiter(a.values(),float,len(a))/90.0
            Lval=float(cs@q[js]) if len(js) else 0.0
            if force or (u8 is not None and u8[rid] > Lval+tol):
                row={U8+rid:1.0}
                for jj,c in zip(js,cs): row[int(jj)]=row.get(int(jj),0.0)-float(c)
                env.append(sprow(row)); env_b.append(0.0); added+=1
        return added
    def sep_c5diag(q):
        """C5-diagonal tangent cut: z=gam.q >= c^2, c=pC5q.q (z=c^2 for real graphons). Tangent at c0:
        gam.q >= 2 c0 (pC5q.q) - c0^2  => -(gam-2c0 pC5q).q <= c0^2. Add if violated."""
        c0=float(pC5q@q); z=float(gam@q); coef=gam-2.0*c0*pC5q
        if z < c0*c0 - tol:   # current q violates the convex constraint z>=c^2 at its own tangent
            row={int(j):-float(coef[j]) for j in np.nonzero(coef)[0]}
            env.append(sprow(row)); env_b.append(c0*c0); return 1
        return 0
    # seed (bound all u7,u8): uniform x for k7; uniform q + witness for k8
    quni=np.ones(nJ)/nJ; xuni=np.asarray(D@quni).ravel()
    sep_k7(xuni, quni, None, force=True)
    sep_k8(quni, None, force=True); sep_k8(q0, None, force=True)
    print(f"seeded {len(env)} cuts; solving...",flush=True)
    eta,q,u7,u8=solve()
    print(f"iter0: eta={eta:+.7e}",flush=True)
    if q is None: print("INFEASIBLE iter0"); return
    for it in range(1,maxit+1):
        ts=time.time(); x=np.asarray(D@q).ravel()
        a7=sep_k7(x,q,u7); a8=sep_k8(q,u8); ac=sep_c5diag(q); added=a7+a8+ac
        if added==0: print(f"CONVERGED it{it}: eta={eta:+.7e}",flush=True); break
        eta,q,u7,u8=solve()
        if eta is None: print(f"it{it}: INFEASIBLE -> CLOSED(float)",flush=True); break
        print(f"it{it}: +{a7}k7 +{a8}k8 +{ac}c5 (pool {len(env)}) eta={eta:+.7e} c={float(pC5q@q):.4f} [{time.time()-ts:.0f}s]",flush=True)
        if eta<=tol:
            print(f">>> eta<=0 -> CANDIDATE CLOSURE (k7+k8); saving.",flush=True)
            pickle.dump(dict(env=[(e.data.tolist(),e.indices.tolist()) for e in env],eta=eta,nv=nv,
                             U7=U7,U8=U8,n7=n7,nR=nR),open("envelope_combined_state.pkl","wb"),protocol=4); break
    print(f"FINAL envelope-combined eta={eta:+.7e}  (closed iff <=0)",flush=True)
    return eta

if __name__=="__main__":
    print("=== COMBINED k7+k8 envelope + C5-diagonal tangent cuts (tightened) ===",flush=True)
    run(); print("DONE",flush=True)
