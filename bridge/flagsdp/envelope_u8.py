#!/usr/bin/env python3
"""GPT's u_R closure: per-R 8-anchor ENVELOPE LP at order-10 (the SOUND replacement for the deficit cert).
Vars [x(ns) | q(nJ) | eta | u_R(nR>=0)].  Equalities: E10 (x = D q), sum x = 1.
Inequalities:
  band  lo <= dedge.x <= hi
  SOUND order-9 validity/moment rows only (row.x >= 0)  -- the unsound 'deficit' rows are EXCLUDED (agent-1 gap)
  envelope coupling  eta <= sum_R u_R - 2/25      (d_mono <= sum_R u_R = U_8)
  per-R cuts  u_R <= L_{R,c}(q)  for separated colorings c (=> u_R <= min_c = per-R MaxCut)
Maximize eta. eta<=0  =>  U_8 <= 2/25 on the band  =>  d_mono <= 2/25 SOUNDLY (validated: U_8(C5)=0.08 tight,
U_8(witness)=4.83e-4 violates). Separation: per R the MaxCut sigma*_R from current q (build_sigma_star).
"""
import numpy as np, pickle, time, sys
from scipy.optimize import linprog
from scipy.sparse import csr_matrix, coo_matrix, hstack, vstack
import flag_engine as fe
from cutting_plane_u8 import maxcut_coloring
LO,HI=0.2486,0.3197

def run(maxit=40, tol=1e-9):
    ns,dedge,rows,provtypes,_=pickle.load(open("cp_cache.pkl","rb"))
    d=np.load("c5lift_cache.npz",allow_pickle=True)
    D=csr_matrix((d["Dval"],(d["Drow"],d["Dcol"])),shape=(ns,int(d["nJ"]))); nJ=D.shape[1]
    D9=pickle.load(open("u8_decomp.pkl","rb")); decomp=D9["decomp"]; nR=D9["nR"]
    Rprof=D9["Rprofiles"]
    assert D9["nJ"]==nJ, f"{D9['nJ']} vs {nJ}"
    wit=np.load("witness.npz",allow_pickle=True); q0=wit["q"]
    print(f"ns={ns} nJ={nJ} nR={nR}; building base LP...",flush=True)
    # ---- sound validity rows only (exclude deficit) ----
    val_rows=[rows[i] for i in range(len(rows)) if provtypes[i] not in ("deficit","deficit_pmap")]
    print(f"  validity rows kept={len(val_rows)} / {len(rows)} (deficit rows excluded)",flush=True)
    nv=ns+nJ+1+nR
    QO=ns; ETA=ns+nJ; UO=ns+nJ+1
    # equalities: E10 (x - Dq = 0), sum x = 1
    negI=coo_matrix((-np.ones(ns),(np.arange(ns),np.arange(ns))),shape=(ns,ns))
    E10=hstack([negI,D,csr_matrix((ns,1+nR))],format="csr")
    sumx=np.zeros((1,nv)); sumx[0,:ns]=1.0
    A_eq=vstack([E10,csr_matrix(sumx)],format="csr"); b_eq=np.concatenate([np.zeros(ns),[1.0]])
    # static inequalities
    base_rows=[]; base_b=[]
    r=np.zeros(nv); r[:ns]=dedge; base_rows.append(r); base_b.append(HI)
    r=np.zeros(nv); r[:ns]=-dedge; base_rows.append(r); base_b.append(-LO)
    for row in val_rows:
        r=np.zeros(nv); r[:ns]=-np.asarray(row); base_rows.append(r); base_b.append(0.0)
    # envelope coupling: eta - sum u_R <= -2/25
    r=np.zeros(nv); r[ETA]=1.0; r[UO:UO+nR]=-1.0; base_rows.append(r); base_b.append(-2.0/25.0)
    base_A=np.asarray(base_rows); base_b=np.asarray(base_b)
    cobj=np.zeros(nv); cobj[ETA]=-1.0
    bounds=[(0,None)]*(ns+nJ)+[(None,None)]+[(0,None)]*nR
    env_rows=[]   # accumulated per-R envelope rows (sparse coo data)
    def solve():
        if env_rows:
            extra=vstack([csr_matrix((er,(np.zeros(len(er),dtype=int),ec)),shape=(1,nv)) for (er,ec) in env_rows]+
                         [csr_matrix(base_A)],format="csr")
            bb=np.concatenate([np.zeros(len(env_rows)),base_b])
        else:
            extra=csr_matrix(base_A); bb=base_b
        rr=linprog(cobj,A_ub=extra,b_ub=bb,A_eq=A_eq,b_eq=b_eq,bounds=bounds,method="highs")
        if rr.success and rr.x is not None:
            return float(-rr.fun), np.asarray(rr.x[QO:QO+nJ]), np.asarray(rr.x[UO:UO+nR])
        return None,None,None
    def separate(q):
        """per-R MaxCut sigma* from q; return list of (rid, c*dict, rowcoef dict J->coeff)."""
        W=[dict() for _ in range(nR)]
        sup=np.where(q>1e-12)[0]
        for jj in sup:
            qj=float(q[jj])
            for (rid,Aset,Bset) in decomp[jj]:
                key=(Aset,Bset) if (len(Aset),Aset)<=(len(Bset),Bset) else (Bset,Aset)
                W[rid][key]=W[rid].get(key,0.0)+qj/90.0
        out=[]
        for rid in range(nR):
            if not W[rid]: continue
            profs=set(); off={}
            for (a,b),w in W[rid].items():
                profs.add(a); profs.add(b)
                if a!=b: off[(a,b)]=off.get((a,b),0.0)+w
            col=maxcut_coloring(list(profs),off)
            out.append((rid,col))
        return out
    def build_row(rid,col):
        """coeff_J = (1/90) sum_{(i,j)->rid in J} 1{col(Aset)==col(Bset)}; return (data,cols) over q-vars."""
        acc={}
        for jj in range(nJ):
            dl=decomp[jj]; c=0
            for (rd,Aset,Bset) in dl:
                if rd==rid and col.get(Aset,0)==col.get(Bset,0): c+=1
            if c: acc[QO+jj]=c/90.0
        return acc
    # SEED: u_R must be bounded above before solving (else eta<=sum u_R-2/25 is unbounded).
    # Add one envelope cut per R from the witness q (the per-R MaxCut of the witness).
    seps0=separate(q0); colmap={rid:col for (rid,col) in seps0}
    acc={rid:{} for rid in colmap}
    for jj in range(nJ):
        for (rd,Aset,Bset) in decomp[jj]:
            if rd in colmap and colmap[rd].get(Aset,0)==colmap[rd].get(Bset,0):
                a=acc[rd]; a[jj]=a.get(jj,0)+1
    for rid,col in seps0:
        data=[-c/90.0 for c in acc[rid].values()]+[1.0]
        cols=[QO+jj for jj in acc[rid].keys()]+[UO+rid]
        env_rows.append((np.asarray(data),np.asarray(cols,dtype=int)))
    print(f"  seeded {len(env_rows)} per-R cuts from witness; first solve...",flush=True)
    # iterate
    eta,q,u=solve()
    print(f"iter0 (seeded): eta={eta:+.7e}",flush=True)
    if q is None: print("base LP infeasible?!"); return
    for it in range(1,maxit+1):
        ts=time.time()
        seps=separate(q); added=0
        # build rows for all separated rids in ONE pass over decomp (faster than per-rid)
        colmap={rid:col for (rid,col) in seps}
        acc={rid:{} for rid in colmap}
        for jj in range(nJ):
            for (rd,Aset,Bset) in decomp[jj]:
                if rd in colmap and colmap[rd].get(Aset,0)==colmap[rd].get(Bset,0):
                    a=acc[rd]; a[jj]=a.get(jj,0)+1
        for rid,col in seps:
            data=[]; cols=[]
            for jj,c in acc[rid].items():
                data.append(-c/90.0); cols.append(QO+jj)   # u_R - L <=0  => +u_R, -L coeffs
            data.append(1.0); cols.append(UO+rid)
            # violation check: u_rid > L(q)+tol ?
            Lval=sum((-dd)*q[cc-QO] for dd,cc in zip(data[:-1],cols[:-1]))
            if u[rid] > Lval + tol:
                env_rows.append((np.asarray(data),np.asarray(cols,dtype=int))); added+=1
        if added==0:
            print(f"CONVERGED it{it}: eta={eta:+.7e}",flush=True); break
        eta,q,u=solve()
        if eta is None: print(f"it{it}: INFEASIBLE -> no order-10 pseudo-graphon survives => CLOSED(float)",flush=True); break
        print(f"it{it}: +{added} R-cuts (pool {len(env_rows)}) eta={eta:+.7e} [{time.time()-ts:.0f}s]",flush=True)
        if eta<=tol:
            print(f">>> eta={eta:+.3e} <= 0 -> U_8<=2/25 on band -> CANDIDATE CLOSURE (float). saving state.",flush=True)
            pickle.dump(dict(env_rows=[(er.tolist(),ec.tolist()) for er,ec in env_rows],eta=eta),
                        open("envelope_u8_state.pkl","wb"),protocol=4)
            break
    print(f"FINAL envelope-u8 eta={eta:+.7e}  (closed iff <=0)",flush=True)
    return eta

if __name__=="__main__":
    print("=== order-10 per-R 8-anchor ENVELOPE LP (U_8) -- sound deficit fix + Step-2 closure ===",flush=True)
    run(); print("DONE",flush=True)
