#!/usr/bin/env python3
"""GPT path (A): SOUND envelope = moment-only validity + k8 U_8 envelope + (8,9) conditional-profile Gram PSD cuts.
Drops the 12 invalid localizer rows (moment-only). The (8,9) cuts enforce P_R(q) >= 0 (PSD) for every 8-root R,
which a real graphon satisfies (cond. i.i.d. profile draws) but the pseudo-state violates (witness min lambdahat=-0.5).
Vars [q(nJ) | eta | u8(nR)]. eta <= sum_R u8_R - 2/25 (d_mono <= U_8); u8_R <= L_{R,c}(q) (per-R MaxCut, edge decomp);
Gram cut: for neg eigvec c of P_R(q), add c^T P_R(q) c = sum_J (sum_{A,B} c_A c_B cnt_{J,R,A,B})/90 * q_J >= 0.
max eta; eta<=0 => U_8 <= 2/25 on the (8,9)-tightened band => sound closure. K7 optional (--k7) for the extra eta bound.
"""
import numpy as np, pickle, time, sys
from scipy.optimize import linprog
from scipy.sparse import csr_matrix, vstack
from cutting_plane_u8 import maxcut_coloring
LO,HI=0.2486,0.3197

def run(maxit=60, tol=1e-9, gram_tol=1e-7, modes=2, method="highs-ds"):
    ns,dedge,rows,provtypes,_=pickle.load(open("cp_cache.pkl","rb"))
    d=np.load("c5lift_cache.npz",allow_pickle=True)
    D=csr_matrix((d["Dval"],(d["Drow"],d["Dcol"])),shape=(ns,int(d["nJ"]))); nJ=D.shape[1]; DT=D.T.tocsr()
    De=pickle.load(open("u8_decomp.pkl","rb"));    dec_e=De["decomp"]; nR=De["nR"]          # edge (k8 U_8)
    Da=pickle.load(open("u8_decomp_all.pkl","rb")); dec_a=Da["decomp"]; Rprof=Da["Rprofiles"]; assert Da["nR"]==nR
    q0=np.load("witness.npz",allow_pickle=True)["q"]
    mom_idx=[i for i in range(len(rows)) if (provtypes[i][0] if isinstance(provtypes[i],(list,tuple)) else provtypes[i])=='moment']
    print(f"ns={ns} nJ={nJ} nR={nR}; MOMENT-only validity={len(mom_idx)} (localizers DROPPED); x=Dq.",flush=True)
    nv=nJ+1+nR; ETA=nJ; U8=nJ+1
    dedge_q=np.asarray(DT@dedge).ravel(); sum_q=np.asarray(D.sum(axis=0)).ravel()
    mom_q=[np.asarray(DT@np.asarray(rows[i])).ravel() for i in mom_idx]
    def sprow(dd):
        cols=np.fromiter(dd.keys(),int,len(dd)); data=np.fromiter(dd.values(),float,len(dd))
        return csr_matrix((data,(np.zeros(len(cols),int),cols)),shape=(1,nv))
    static=[]; sb=[]
    static.append(sprow({j:dedge_q[j] for j in range(nJ) if dedge_q[j]})); sb.append(HI)
    static.append(sprow({j:-dedge_q[j] for j in range(nJ) if dedge_q[j]})); sb.append(-LO)
    for vq in mom_q:
        static.append(sprow({j:-vq[j] for j in range(nJ) if vq[j]})); sb.append(0.0)
    static.append(sprow({ETA:1.0,**{U8+i:-1.0 for i in range(nR)}})); sb.append(-2.0/25.0)
    Aeq=sprow({j:sum_q[j] for j in range(nJ) if sum_q[j]}); beq=[1.0]
    cobj=np.zeros(nv); cobj[ETA]=-1.0
    bounds=[(0,None)]*nJ+[(None,None)]+[(0,None)]*nR
    env=[]; envb=[]
    def solve():
        A=vstack(static+env,format="csr"); b=np.concatenate([sb,np.asarray(envb)])
        rr=linprog(cobj,A_ub=A,b_ub=b,A_eq=Aeq,b_eq=beq,bounds=bounds,method=method)
        if (not rr.success or rr.x is None) and method!="highs":
            rr=linprog(cobj,A_ub=A,b_ub=b,A_eq=Aeq,b_eq=beq,bounds=bounds,method="highs")
        if rr.success and rr.x is not None: return float(-rr.fun), np.asarray(rr.x[:nJ]), np.asarray(rr.x[U8:U8+nR])
        return None,None,None
    # ---- k8 U_8 per-R MaxCut envelope (edge decomp) ----
    def sep_k8(q,u8,force=False):
        W=[dict() for _ in range(nR)]; sup=np.where(q>1e-12)[0]
        for jj in sup:
            qj=float(q[jj])
            for (rid,A,B) in dec_e[jj]:
                key=(A,B) if (len(A),A)<=(len(B),B) else (B,A); W[rid][key]=W[rid].get(key,0.0)+qj/90.0
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
            for (rd,A,B) in dec_e[jj]:
                if rd in cm and cm[rd].get(A,0)==cm[rd].get(B,0): a=acc[rd]; a[jj]=a.get(jj,0)+1
        added=0
        for rid,a in acc.items():
            js=np.fromiter(a.keys(),int,len(a)); cs=np.fromiter(a.values(),float,len(a))/90.0
            L=float(cs@q[js]) if len(js) else 0.0
            if force or (u8 is not None and u8[rid]>L+tol):
                env.append(sprow({U8+rid:1.0,**{int(jj):-float(c) for jj,c in zip(js,cs)}})); envb.append(0.0); added+=1
        return added
    # ---- (8,9) Gram PSD cuts (all-pairs decomp) ----
    def sep_gram(q):
        acc=[dict() for _ in range(nR)]; sup=np.where(q>1e-13)[0]
        for jj in sup:
            qj=float(q[jj])
            for (rid,A,B) in dec_a[jj]: acc[rid][(A,B)]=acc[rid].get((A,B),0.0)+qj/90.0
        cuts=[]  # list of (rid, {profile:coef})
        for rid in range(nR):
            if not acc[rid]: continue
            profs=sorted(set(tuple(p) for p in Rprof[rid])|set(a for (a,b) in acc[rid])|set(b for (a,b) in acc[rid]))
            idx={p:i for i,p in enumerate(profs)}; m=len(profs)
            P=np.zeros((m,m))
            for (A,B),w in acc[rid].items(): P[idx[A],idx[B]]+=w
            P=0.5*(P+P.T)
            ev,V=np.linalg.eigh(P)
            for k in range(min(modes,m)):
                if ev[k] < -gram_tol:
                    c=V[:,k]; cuts.append((rid,{profs[i]:float(c[i]) for i in range(m) if abs(c[i])>1e-12}))
                else: break
        if not cuts: return 0
        # one pass over all-pairs decomp to build per-cut coeff over q
        rid_to_cuts={}
        for ci,(rid,cd) in enumerate(cuts): rid_to_cuts.setdefault(rid,[]).append((ci,cd))
        coeffs=[dict() for _ in cuts]
        for jj in range(nJ):
            dl=dec_a[jj]
            for (rd,A,B) in dl:
                cl=rid_to_cuts.get(rd)
                if cl:
                    for (ci,cd) in cl:
                        ca=cd.get(A); cb=cd.get(B)
                        if ca is not None and cb is not None:
                            coeffs[ci][jj]=coeffs[ci].get(jj,0.0)+ca*cb
        added=0
        for ci,co in enumerate(coeffs):
            if not co: continue
            # cut: sum_J coeff_J/90 * q_J >= 0  => -(coeff/90).q <= 0
            env.append(sprow({int(jj):-v/90.0 for jj,v in co.items()})); envb.append(0.0); added+=1
        return added
    # seed k8 (bound all u8): uniform q + witness
    quni=np.ones(nJ)/nJ; sep_k8(quni,None,force=True); sep_k8(q0,None,force=True)
    print(f"seeded {len(env)} k8 cuts; solving...",flush=True)
    eta,q,u8=solve(); print(f"iter0: eta={eta:+.7e}",flush=True)
    if q is None: print("INFEASIBLE iter0"); return
    for it in range(1,maxit+1):
        ts=time.time(); a8=sep_k8(q,u8); ag=sep_gram(q); added=a8+ag
        if added==0: print(f"CONVERGED it{it}: eta={eta:+.7e}",flush=True); break
        eta,q,u8=solve()
        if eta is None: print(f"it{it}: INFEASIBLE -> CLOSED(float)",flush=True); break
        print(f"it{it}: +{a8}k8 +{ag}gram (pool {len(env)}) eta={eta:+.7e} [{time.time()-ts:.0f}s]",flush=True)
        if eta<=tol:
            print(f">>> eta<=0 -> CANDIDATE CLOSURE (k8+gram89); saving.",flush=True)
            pickle.dump(dict(eta=eta),open("envelope_gram89_state.pkl","wb")); break
    print(f"FINAL envelope-gram89 eta={eta:+.7e}  (closed iff <=0; N<=180 iff <6.17e-5)",flush=True)
    return eta

if __name__=="__main__":
    print("=== moment-only k8 U_8 + (8,9) Gram PSD envelope (GPT path A) ===",flush=True)
    run(); print("DONE",flush=True)
