#!/usr/bin/env python3
"""Step-1 deficit-fix: re-derive the cert with GPT's TYPE-BALANCE constraint (graphon-sound).
Need lambda>=0 with (3) sum_{r in type sigma} lambda_{k,sigma,r} = alpha_k for EVERY sigma in T_k, (4) sum_k alpha_k=1,
then d_mono(W)-2/25 <= sum lambda g(W) RIGOROUSLY. We: (a) run the k=7 (107 types)+k<=5 cut separation to build a cut
pool (tracking each cut's root-size k and TYPE index), + moments; (b) solve the DUAL LP
   min delta s.t. for all H: sum lambda g(H) + sum gam m(H) + mu(e-lo)+nu(hi-e) <= delta ;
   lambda,gam,mu,nu>=0 ; BALANCE: for each (k,sigma_idx) sum_r lambda = alpha_{k,sigma}; and for each k all sigma share
   the SAME alpha_k => sum_r lambda_{k,sigma,r} equal across sigma of size k ; sum_k alpha_k = 1.
Report the balanced delta'. If delta' < 2/(25*36^2)=6.17e-5 => N<=180 recovered with rigorous graphon transfer.
"""
import sys, time, pickle
import numpy as np
from scipy.optimize import linprog
import flag_engine as fe, flag_cutgen as fc, flag_localizer as floc, cpp_precompute as cpp

def main(band=(0.2486,0.3197), sep_iters=4, tol=1e-7):
    C=pickle.load(open("cache_n9.pkl","rb"))
    states=C["states"]; ns=len(states); dedge=C["dedge"]; t=C["t"]; deftypes=C["deftypes"]
    Pmom=[(lab,tt,Pf.T.reshape(ns,tt,tt)) for (lab,tt,sg,fl,s,Pf,Pi) in C["moments"]]
    lo,hi=band
    cpp.compile_cpp()
    types7=fe.enumerate_graphs(7,triangle_free=True)
    print(f"k=7: {len(types7)} types; precomputing...",flush=True); t0=time.time()
    dt7=[(7,A,*cpp.precompute_type_cpp(states,7,A,nthreads=32)) for (k,A) in types7]
    print(f"  [{time.time()-t0:.0f}s]",flush=True)
    # alltypes with a stable type-id: (k, type_index). deftypes are k<=5 base.
    alltypes=[]
    for ti,(k,A,E,S,cls) in enumerate(list(deftypes)):
        alltypes.append((k,('base',ti),E,S,cls))
    for ti,(k,A,E,S,cls) in enumerate(dt7):
        alltypes.append((7,('k7',ti),E,S,cls))
    # ---- cutting-plane to build the cut pool (track type per cut) ----
    Gdef=[]; Gtype=[]; Mrows=[]
    def solve_primal():
        c=np.zeros(ns+1); c[-1]=-1.0; Aeq=np.zeros((1,ns+1)); Aeq[0,:ns]=1.0
        ub=[np.concatenate([-dedge,[0.0]]),np.concatenate([dedge,[0.0]])]; ubb=[-lo,hi]
        parts=[np.array(ub)]
        if Gdef:
            Gd=np.asarray(Gdef); parts.append(np.concatenate([-Gd,np.ones((Gd.shape[0],1))],axis=1))
        if Mrows:
            Mn=floc._norm_rows(Mrows); parts.append(np.concatenate([-Mn,np.zeros((Mn.shape[0],1))],axis=1))
        A_ub=np.vstack(parts); b_ub=np.array(ubb+[0.0]*(A_ub.shape[0]-2))
        r=linprog(c,A_ub=A_ub,b_ub=b_ub,A_eq=Aeq,b_eq=[1.0],bounds=[(0,None)]*ns+[(None,None)],method="highs-ipm")
        if not r.success: r=linprog(c,A_ub=A_ub,b_ub=b_ub,A_eq=Aeq,b_eq=[1.0],bounds=[(0,None)]*ns+[(None,None)],method="highs")
        return (-float(r.fun),np.asarray(r.x[:ns])) if r.success else (0.0,np.ones(ns)/ns)
    v,x=solve_primal()
    from run_k7b import sep_multi
    seen=set()
    for it in range(1,sep_iters+1):
        added=0
        for (k,tid,E,S,cls) in alltypes:
            # BEST cut per type each round (v=1e9 => returns best even if non-violated) => guarantees coverage
            ps,gs=sep_multi(E,S,x,t,1e9,tol,keep=1)
            for p in ps:
                key=(tid,tuple(p))
                if key in seen: continue
                seen.add(key); Gdef.append(fc.cut_from_p(E,S,p,t)); Gtype.append((k,tid)); added+=1
        for (lab,tt,P) in Pmom:
            mr,_,_=fc.separate_moment(P,x,maxvecs=4)
            for r in mr: Mrows.append(r)
        v,x=solve_primal()
        print(f"sep it{it}: pool={len(Gdef)} cuts ({len(set(Gtype))} types) eta={v:+.7e}",flush=True)
        if added==0: break
    print(f"unbalanced primal eta={v:+.7e}, pool {len(Gdef)} cuts over {len(set(Gtype))} types",flush=True)
    # ---- BALANCED DUAL LP ----
    # vars: lambda[i] (per cut), gam[j] (per moment row), mu, nu, alpha[(k)] (per root size), delta
    nC=len(Gdef); nM=len(Mrows)
    types_present=sorted(set(Gtype)); ks=sorted(set(k for (k,_) in types_present))
    # map: cut i -> (k, tid); per (k,tid) the list of cut indices
    from collections import defaultdict
    by_type=defaultdict(list)
    for i,(k,tid) in enumerate(Gtype): by_type[(k,tid)].append(i)
    # variable layout: [lam(nC) | gam(nM) | mu | nu | alpha(len ks) | delta]
    nv=nC+nM+2+len(ks)+1
    kidx={k:i for i,k in enumerate(ks)}
    G=np.asarray(Gdef); Mn=floc._norm_rows(Mrows) if Mrows else np.zeros((0,ns))
    # per-state: sum lam G(H) + sum gam Mn(H) + mu(e-lo)+nu(hi-e) - delta <= 0
    A_ub=np.zeros((ns,nv))
    A_ub[:,:nC]=G.T
    if nM: A_ub[:,nC:nC+nM]=Mn.T
    A_ub[:,nC+nM]=dedge-lo; A_ub[:,nC+nM+1]=hi-dedge; A_ub[:,-1]=-1.0
    b_ub=np.zeros(ns)
    # balance equalities: for each (k,tid): sum_{i in type} lam[i] - alpha[k] = 0
    Aeq=[]; beq=[]
    for (k,tid),idxs in by_type.items():
        row=np.zeros(nv)
        for i in idxs: row[i]=1.0
        row[nC+nM+2+kidx[k]]=-1.0
        Aeq.append(row); beq.append(0.0)
    # sum_k alpha_k = 1
    row=np.zeros(nv)
    for k in ks: row[nC+nM+2+kidx[k]]=1.0
    Aeq.append(row); beq.append(1.0)
    c=np.zeros(nv); c[-1]=1.0
    bounds=[(0,None)]*(nC+nM+2)+[(0,None)]*len(ks)+[(None,None)]
    r=linprog(c,A_ub=A_ub,b_ub=b_ub,A_eq=np.array(Aeq),b_eq=np.array(beq),bounds=bounds,method="highs-ipm")
    if not r.success: r=linprog(c,A_ub=A_ub,b_ub=b_ub,A_eq=np.array(Aeq),b_eq=np.array(beq),bounds=bounds,method="highs")
    if r.success:
        dprime=r.x[-1]; thr=2.0/(25*36*36)
        print(f"\n>>> BALANCED full-coverage delta' = {dprime:+.7e}",flush=True)
        print(f"    threshold for N<=36 (2/(25*36^2)) = {thr:.6e}",flush=True)
        print(f"    delta' < threshold ? {dprime < thr}  => N<=180 {'RECOVERED (rigorous graphon transfer)' if dprime<thr else 'NOT recovered at full coverage'}",flush=True)
        alphas={k:float(r.x[nC+nM+2+kidx[k]]) for k in ks}
        print(f"    alpha_k = {alphas} (sum={sum(alphas.values()):.4f})",flush=True)
        pickle.dump(dict(lam=r.x[:nC].tolist(),Gtype=Gtype,delta=float(dprime),alphas=alphas), open("balanced_cert.pkl","wb"))
    else:
        print(f"balanced dual LP status {r.status}: {r.message}",flush=True)
    print("DONE",flush=True)

if __name__=="__main__": main()
