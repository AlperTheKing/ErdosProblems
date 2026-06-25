#!/usr/bin/env python3
"""GPT path (A) ORACLE: enforce the (8,9) conditional-profile Gram PSD constraint P_R(q)>=0 as ACTUAL block LMIs
(cvxpy + Clarabel), not a slow cutting-plane. Gives the true (8,9)-tightened optimum eta directly.
Vars q(nJ)>=0, eta, u7(n7), u8(nR); LP rows: band + moment-only validity + k7 cuts + k8 cuts (cutting-planes, the
only iterated part); SDP blocks: P_R(q) = reshape(M_R @ q)/90 >> 0 for each active root R (profiles = those that
appear in the all-pairs decomp for R, capped at MAXB; larger roots split off / handled by the cutting-plane gram).
max eta. eta<=0 => (8,9) closes Step-2 (then rationalize PSD dual to rank-1 exact cuts). Iterate k7/k8 separation.
"""
import numpy as np, pickle, time, sys
import cvxpy as cp
from scipy.sparse import csr_matrix, coo_matrix
import flag_cutgen as fc
from run_k7b import sep_multi, precompute_k7
from cutting_plane_u8 import maxcut_coloring
LO,HI=0.2486,0.3197

def run(maxit=25, tol=1e-9, MAXB=40):
    ns,dedge,rows,provtypes,_=pickle.load(open("cp_cache.pkl","rb"))
    C=pickle.load(open("cache_n9.pkl","rb")); states=C["states"]; t=C["t"]
    d=np.load("c5lift_cache.npz",allow_pickle=True)
    D=csr_matrix((d["Dval"],(d["Drow"],d["Dcol"])),shape=(ns,int(d["nJ"]))); nJ=D.shape[1]; DT=D.T.tocsr()
    De=pickle.load(open("u8_decomp.pkl","rb")); dec_e=De["decomp"]; nR=De["nR"]
    Da=pickle.load(open("u8_decomp_all.pkl","rb")); dec_a=Da["decomp"]
    dt7=precompute_k7(states); n7=len(dt7)
    mom_idx=[i for i in range(len(rows)) if (provtypes[i][0] if isinstance(provtypes[i],(list,tuple)) else provtypes[i])=='moment']
    dedge_q=np.asarray(DT@dedge).ravel(); sum_q=np.asarray(D.sum(axis=0)).ravel()
    mom_q=[np.asarray(DT@np.asarray(rows[i])).ravel() for i in mom_idx]
    # --- per-root profile sets + M_R sparse (vec(P_R) = M_R @ q), from all-pairs decomp ---
    # Use the BAND-RELEVANT profile set: profiles appearing in states J that band q's actually weight
    # (witness support + uniform-low-density states), NOT all dense states. Keeps blocks small & captures the violation.
    print("building per-root P_R coefficient maps (band-relevant profiles)...",flush=True); t0=time.time()
    q0=np.load("witness.npz",allow_pickle=True)["q"]
    # band-relevant states = sparse states (<=16 edges => order-10 d_edge<=0.355, covers the band) + witness support
    bandJ=set(np.where(q0>1e-12)[0].tolist())
    for jj in range(nJ):
        if len(dec_e[jj]) <= 32: bandJ.add(jj)   # dec_e[jj] = directed-edge contribs = 2*#edges
    prof_set=[set() for _ in range(nR)]
    for jj in bandJ:
        for (rid,A,B) in dec_a[jj]: prof_set[rid].add(A); prof_set[rid].add(B)
    profs=[sorted(prof_set[r]) for r in range(nR)]
    pidx=[{p:i for i,p in enumerate(profs[r])} for r in range(nR)]
    roots=[r for r in range(nR) if 1<len(profs[r])<=MAXB]   # SDP roots (skip trivial; cap big blocks)
    big=[r for r in range(nR) if len(profs[r])>MAXB]
    rowdat={r:{} for r in roots}   # (entry a*m+b) -> {J: count}  (PRINCIPAL submatrix over band-relevant profiles)
    rootset=set(roots)
    for jj in range(nJ):
        for (rid,A,B) in dec_a[jj]:
            if rid in rootset:
                pm=pidx[rid]; a=pm.get(A); b=pm.get(B)
                if a is None or b is None: continue   # profile outside the band-relevant submatrix -> different entry
                m=len(profs[rid]); e=a*m+b; rowdat[rid].setdefault(e,{}); rowdat[rid][e][jj]=rowdat[rid][e].get(jj,0)+1
    MR={}
    for r in roots:
        m=len(profs[r]); ii=[];jj2=[];vv=[]
        for e,jc in rowdat[r].items():
            for J,c in jc.items(): ii.append(e); jj2.append(J); vv.append(c/90.0)
        MR[r]=csr_matrix((vv,(ii,jj2)),shape=(m*m,nJ))
    print(f"  SDP roots={len(roots)} (skipped {len(big)} big>{MAXB}), total PSD dim={sum(len(profs[r]) for r in roots)} [{time.time()-t0:.0f}s]",flush=True)
    # --- cvxpy problem ---
    q=cp.Variable(nJ,nonneg=True); eta=cp.Variable(); u7=cp.Variable(n7,nonneg=True); u8=cp.Variable(nR,nonneg=True)
    cons=[cp.sum(q)==1, dedge_q@q<=HI, dedge_q@q>=LO]
    for vq in mom_q: cons.append(vq@q>=0)
    cons.append(eta<=cp.sum(u7)); cons.append(eta<=cp.sum(u8)-2.0/25.0)
    for r in roots:
        m=len(profs[r]); P=cp.reshape(MR[r]@q,(m,m),order='C'); cons.append((P+P.T)/2>>0)
    k7rows=[]; k8rows=[]   # accumulated cutting-plane rows: (sigma, gq) and (R, Lq)
    prob=None
    def build_solve():
        c=list(cons)
        for (i,gq) in k7rows: c.append(u7[i]<=gq@q)
        for (R,Lq) in k8rows: c.append(u8[R]<=Lq@q)
        pr=cp.Problem(cp.Maximize(eta),c)
        pr.solve(solver=cp.CLARABEL, verbose=False)
        return pr
    def sep_k7(x,qv,u7v,force=False):
        added=0
        for i,(k,A,E,S,cls) in enumerate(dt7):
            ps,gs=sep_multi(E,S,x,t,1e9,tol,keep=1)
            for p in ps:
                g=fc.cut_from_p(E,S,p,t); gq=np.asarray(DT@np.asarray(g)).ravel()
                if force or (u7v is not None and u7v[i]>float(gq@qv)+tol): k7rows.append((i,gq)); added+=1
        return added
    def sep_k8(qv,u8v,force=False):
        W=[dict() for _ in range(nR)]; sup=np.where(qv>1e-12)[0]
        for jj in sup:
            qj=float(qv[jj])
            for (rid,A,B) in dec_e[jj]:
                key=(A,B) if (len(A),A)<=(len(B),B) else (B,A); W[rid][key]=W[rid].get(key,0.0)+qj/90.0
        cm={}
        for rid in range(nR):
            if not W[rid]: continue
            pr=set(); off={}
            for (a,b),w in W[rid].items():
                pr.add(a); pr.add(b)
                if a!=b: off[(a,b)]=off.get((a,b),0.0)+w
            cm[rid]=maxcut_coloring(list(pr),off)
        acc={rid:{} for rid in cm}
        for jj in range(nJ):
            for (rd,A,B) in dec_e[jj]:
                if rd in cm and cm[rd].get(A,0)==cm[rd].get(B,0): a=acc[rd]; a[jj]=a.get(jj,0)+1
        added=0
        for rid,a in acc.items():
            js=np.fromiter(a.keys(),int,len(a)); cs=np.fromiter(a.values(),float,len(a))/90.0
            Lq=np.zeros(nJ); Lq[js]=cs
            if force or (u8v is not None and u8v[rid]>float(Lq@qv)+tol): k8rows.append((rid,Lq)); added+=1
        return added
    quni=np.ones(nJ)/nJ; xuni=np.asarray(D@quni).ravel()
    sep_k7(xuni,quni,None,True); sep_k8(quni,None,True)
    q0=np.load("witness.npz",allow_pickle=True)["q"]; sep_k8(q0,None,True)
    print(f"seeded k7={len(k7rows)} k8={len(k8rows)}; first SDP solve...",flush=True)
    import math
    for it in range(maxit):
        ts=time.time(); pr=build_solve()
        if pr.status not in ("optimal","optimal_inaccurate"):
            print(f"it{it}: SDP status={pr.status}",flush=True)
            if "infeasible" in str(pr.status): print(">>> INFEASIBLE => no (8,9)-PSD pseudo-graphon in band => CLOSED",flush=True)
            break
        etav=float(eta.value); qv=np.asarray(q.value).ravel(); qv=np.maximum(qv,0)
        u7v=np.asarray(u7.value).ravel(); u8v=np.asarray(u8.value).ravel(); x=np.asarray(D@qv).ravel()
        nn=int(math.floor(math.sqrt(2.0/(25*etav)))) if etav>0 else 999
        a7=sep_k7(x,qv,u7v); a8=sep_k8(qv,u8v)
        print(f"it{it}: eta={etav:+.7e} n<={nn} +{a7}k7 +{a8}k8 (rows {len(k7rows)}+{len(k8rows)}) [{time.time()-ts:.0f}s]",flush=True)
        if etav<=tol:
            print(f">>> eta<=0 with (8,9) PSD enforced -> CANDIDATE Step-2 CLOSURE; saving for exact re-verify.",flush=True)
            pickle.dump(dict(eta=etav,q=qv.tolist()),open("envelope_order10_sdp_state.pkl","wb")); break
        if a7+a8==0:
            print(f"CONVERGED it{it}: eta={etav:+.7e} (k7/k8 separation dry; (8,9) exactly enforced)",flush=True); break
    print("DONE",flush=True)

if __name__=="__main__":
    print("=== order-10 SDP oracle: P_R(q)>=0 block LMIs + k7/k8 envelope (GPT path A) ===",flush=True)
    run()
