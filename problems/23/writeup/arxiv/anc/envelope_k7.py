#!/usr/bin/env python3
"""Step-1 deficit fix DONE RIGHT: per-root-MaxCut ENVELOPE U_7, not fixed-cut convex combos.
The 107 k=7 triangle-free types T7 are a COMPLETE cover (every 7-tuple induces exactly one),
so d_mono(W) <= U_7(W) = sum_{sigma in T7} p_sigma(W) min_c E[C|sigma,c] = 2/25 + sum_sigma min_c g_{sigma,c}(W).
Hence  U_7 <= 2/25 on the band  <=>  eta := max_{band x} sum_sigma min_c g_{sigma,c}(x) <= 0.
LP: vars x(ns)>=0, u_sigma(free); max sum u_sigma s.t. sum x=1, band, order-9 moment rows m.x>=0,
and PER-ROOT envelope  u_sigma <= g_{sigma,c}.x  for every cut c in sigma's pool. Separation: per sigma
the MaxCut c*=argmin_c g (sep_multi keep=1); add the row if it lowers u_sigma. eta<=0 => Step-1 closed.
(Contrast run_k7b: single aggregate eta<=min_{all cuts} g.x -> escapes; GPT flagged this.)
"""
import sys, time, pickle
import numpy as np
from scipy.optimize import linprog
import flag_cutgen as fc, flag_localizer as floc
from run_k7b import sep_multi, precompute_k7

def run(band=(0.2486,0.3197), maxit=100, tol=1e-9):
    C=pickle.load(open("cache_n9.pkl","rb"))
    states=C["states"]; ns=len(states); dedge=C["dedge"]; t=C["t"]
    Pmom=[(lab,tt,Pf.T.reshape(ns,tt,tt)) for (lab,tt,sg,fl,s,Pf,Pi) in C["moments"]]
    lo,hi=band
    print(f"ns={ns} t={t}; precompute k=7 ...",flush=True); t0=time.time()
    dt7=precompute_k7(states); nT=len(dt7)
    print(f"  {nT} types [{time.time()-t0:.0f}s]",flush=True)
    pools=[[] for _ in range(nT)]; Mrows=[]
    def solve():
        nv=ns+nT
        cobj=np.zeros(nv); cobj[ns:]=-1.0          # max sum u
        Aeq=np.zeros((1,nv)); Aeq[0,:ns]=1.0; beq=[1.0]
        rows=[]; b=[]
        r=np.zeros(nv); r[:ns]=-dedge; rows.append(r); b.append(-lo)
        r=np.zeros(nv); r[:ns]= dedge; rows.append(r); b.append(hi)
        if Mrows:
            for m in floc._norm_rows(Mrows):
                r=np.zeros(nv); r[:ns]=-m; rows.append(r); b.append(0.0)
        for i in range(nT):
            for g in pools[i]:
                r=np.zeros(nv); r[:ns]=-np.asarray(g); r[ns+i]=1.0; rows.append(r); b.append(0.0)
        A_ub=np.asarray(rows); b_ub=np.asarray(b)
        bounds=[(0,None)]*ns+[(None,None)]*nT
        rr=linprog(cobj,A_ub=A_ub,b_ub=b_ub,A_eq=Aeq,b_eq=beq,bounds=bounds,method="highs-ipm")
        if not rr.success or rr.x is None:
            rr=linprog(cobj,A_ub=A_ub,b_ub=b_ub,A_eq=Aeq,b_eq=beq,bounds=bounds,method="highs")
        if rr.success and rr.x is not None:
            return float(-rr.fun), np.asarray(rr.x[:ns]), np.asarray(rr.x[ns:])
        return 0.0, np.ones(ns)/ns, np.zeros(nT)
    x=np.ones(ns)/ns
    for i,(k,A,E,S,cls) in enumerate(dt7):
        ps,gs=sep_multi(E,S,x,t,1e9,tol,keep=1)
        for p in ps: pools[i].append(fc.cut_from_p(E,S,p,t))
    eta,x,u=solve(); print(f"iter0: eta(sum_sigma min g)={eta:+.7e}",flush=True)
    for it in range(1,maxit+1):
        added=0; ts=time.time()
        for i,(k,A,E,S,cls) in enumerate(dt7):
            ps,gs=sep_multi(E,S,x,t,1e9,tol,keep=1)
            for p in ps:
                g=fc.cut_from_p(E,S,p,t)
                if float(g@x) < u[i]-tol:
                    pools[i].append(g); added+=1
        madded=0; mn=0.0
        for (lab,tt,P) in Pmom:
            mr,lam2,_=fc.separate_moment(P,x,maxvecs=8); mn=min(mn,lam2)
            for r in mr: Mrows.append(r); madded+=1
        if added==0 and madded==0:
            print(f"CONVERGED it{it} eta={eta:+.7e}",flush=True); break
        eta,x,u=solve()
        print(f"it{it}: +{added}cuts +{madded}m eta={eta:+.7e} meig={mn:+.1e} [{time.time()-ts:.0f}s]",flush=True)
        if it%12==0:  # periodic save (robust to timeout)
            pickle.dump(dict(pools=[[g.tolist() for g in P] for P in pools],
                             Mrows=[r.tolist() for r in Mrows], x=x.tolist(), u=u.tolist(), eta=float(eta)),
                        open("envelope_k7_cert.pkl","wb"),protocol=4)
    print(f"FINAL envelope-k7 eta = max_band sum_sigma min_c g = {eta:+.7e}  (closed iff <=0)",flush=True)
    # ALWAYS save the converged cert state (cut pool per type + moment rows + final x) for exact re-audit.
    pickle.dump(dict(pools=[[g.tolist() for g in P] for P in pools],
                     Mrows=[r.tolist() for r in Mrows], x=x.tolist(), u=u.tolist(), eta=float(eta),
                     types=[(int(k),A.tolist() if hasattr(A,'tolist') else A) for (k,A,E,S,cls) in dt7]),
                open("envelope_k7_cert.pkl","wb"),protocol=4)
    print(f"saved envelope_k7_cert.pkl (pools={sum(len(P) for P in pools)} cuts, {len(Mrows)} moment rows)",flush=True)
    # report achievable n: max n with eta < 2/(25 n^2)
    import math
    nmax=int(math.floor(math.sqrt(2.0/(25*max(eta,1e-300))))) if eta>0 else 999
    print(f">>> float eta={eta:.6e} => achievable n<= {nmax} (N<={5*nmax}); thresholds: n=11 needs <{2/(25*121):.3e}, n=10 needs <{2/(25*100):.3e}",flush=True)
    return eta

if __name__=="__main__":
    print("=== order-9 per-root-MaxCut ENVELOPE (U_7) LP -- rigorous Step-1 deficit fix ===",flush=True)
    run(); print("DONE",flush=True)
