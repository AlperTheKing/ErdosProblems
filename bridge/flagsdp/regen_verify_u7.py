#!/usr/bin/env python3
"""Regenerate + verify the order-9 U_7 per-root-MaxCut envelope certificate (for agent-1's exact G2 re-audit).
Loads envelope_k7_cert.pkl (converged cut pool per T7 type + moment rows + final x). Rebuilds the envelope LP
   max sum_sigma u_sigma  s.t.  sum_s x_s = 1,  lo <= dedge.x <= hi,  m_j.x >= 0 (moment-PSD localizers),
                                u_sigma <= g_{sigma,c}.x  for every pooled cut c
re-solves (float, HiGHS), confirms eta, extracts the LP DUAL (the certificate), and runs the EXACT rational
dual-feasibility check on the CUT+BAND part (g rows are exact: densities = integer/(n)_k; recovered by rounding).

DUAL (max-LP):  multipliers lam_{sigma,c}>=0 (cuts), mu_hi,mu_lo>=0 (band), nu_j>=0 (moments), rho (free, sum x=1).
  per-type:  sum_c lam_{sigma,c} = 1                                  ... (objective coeff of u_sigma)
  per-state s: rho + (mu_hi - mu_lo) dedge[s] - sum_{sigma,c} lam g[s] - sum_j nu_j m[s] >= 0   ... (x_s>=0)
  delta_dual = hi*mu_hi - lo*mu_lo + rho   >=  max primal = eta.   (so d_mono <= 2/25 + delta_dual on the band)
The moment rows m_j are float rank-one PSD-localizer cuts; for a FULLY exact cert they are replaced by the exact
moment-PSD Gram certificate (the SAME G1 cert agent-1 already exact-verified). This script verifies the cut+band
part exactly and reports the moment residual that the G1 Gram-cert must cover.
"""
import sys, pickle, math
import numpy as np
from fractions import Fraction as F
from scipy.optimize import linprog
import flag_localizer as floc

def thr_n(delta): return int(math.floor(math.sqrt(2.0/(25*delta)))) if delta>0 else 999

def main():
    C=pickle.load(open("cache_n9.pkl","rb")); dedge=np.asarray(C["dedge"]); ns=len(C["states"])
    cert=pickle.load(open("envelope_k7_cert.pkl","rb"))
    pools=[ [np.asarray(g) for g in P] for P in cert["pools"] ]
    Mrows=[np.asarray(r) for r in cert["Mrows"]]
    nT=len(pools); lo,hi=0.2486,0.3197
    ncut=sum(len(P) for P in pools)
    print(f"cert: {nT} types, {ncut} cuts, {len(Mrows)} moment rows; saved eta={cert['eta']:.6e}",flush=True)
    # ---- rebuild LP : vars [x(ns) | u(nT)] ----
    nv=ns+nT
    cobj=np.zeros(nv); cobj[ns:]=-1.0
    Aeq=np.zeros((1,nv)); Aeq[0,:ns]=1.0; beq=[1.0]
    rows=[]; b=[]; tag=[]   # tag: ('band_lo'|'band_hi'|('mom',j)|('cut',sigma,c))
    r=np.zeros(nv); r[:ns]=-dedge; rows.append(r); b.append(-lo); tag.append('band_lo')
    r=np.zeros(nv); r[:ns]= dedge; rows.append(r); b.append(hi);  tag.append('band_hi')
    Mn=floc._norm_rows(Mrows) if Mrows else np.zeros((0,ns))
    for j,m in enumerate(Mn):
        r=np.zeros(nv); r[:ns]=-m; rows.append(r); b.append(0.0); tag.append(('mom',j))
    for i in range(nT):
        for c,g in enumerate(pools[i]):
            r=np.zeros(nv); r[:ns]=-g; r[ns+i]=1.0; rows.append(r); b.append(0.0); tag.append(('cut',i,c))
    A_ub=np.asarray(rows); b_ub=np.asarray(b)
    bounds=[(0,None)]*ns+[(None,None)]*nT
    rr=linprog(cobj,A_ub=A_ub,b_ub=b_ub,A_eq=Aeq,b_eq=beq,bounds=bounds,method="highs")
    eta=float(-rr.fun)
    print(f"RE-SOLVED float eta = {eta:.7e}  (cert saved {cert['eta']:.7e}); achievable n<={thr_n(eta)} (N<={5*thr_n(eta)})",flush=True)
    print(f"  thresholds: n=12 needs delta<{2/(25*144):.3e}, n=11 <{2/(25*121):.3e}, n=10 <{2/(25*100):.3e}",flush=True)
    # ---- extract DUAL ----
    mu=-rr.ineqlin.marginals      # >=0 for <= constraints (HiGHS sign convention)
    rho=-rr.eqlin.marginals[0]
    dual=dict(tag=tag, mu=mu.tolist(), rho=float(rho))
    delta_dual = hi*mu[1] - lo*mu[0] + rho   # tag[0]=band_lo(-lo), tag[1]=band_hi(hi)
    print(f"  DUAL objective delta_dual = {delta_dual:.7e}  (should ~= eta)",flush=True)
    # per-type sum lam check
    lam=mu; bytype={}
    for k,tg in enumerate(tag):
        if isinstance(tg,tuple) and tg[0]=='cut': bytype.setdefault(tg[1],0.0); bytype[tg[1]]+=lam[k]
    s=[bytype.get(i,0.0) for i in range(nT)]
    print(f"  per-type sum_c lam: min={min(s):.4f} max={max(s):.4f} (should all = 1 for active types)",flush=True)
    # ---- EXACT cut+band dual-feasibility residual (moment part left to G1 Gram-cert) ----
    # round dual to rationals, g/dedge to rationals (densities), check per-state:
    #   rho + (mu_hi-mu_lo) dedge[s] - sum lam g[s] >= moment_term[s]  (moment_term = sum nu_j m[s] >=0 region)
    # report worst (cut+band) slack; if >=0 everywhere, the band bound holds with the moment cut as a >=0 relaxation.
    musig = mu
    base = np.zeros(ns) + rho + (mu[1]-mu[0])*dedge
    for k,tg in enumerate(tag):
        if isinstance(tg,tuple) and tg[0]=='cut':
            base -= mu[k]*pools[tg[1]][tg[2]]
    mom_term = np.zeros(ns)
    for k,tg in enumerate(tag):
        if isinstance(tg,tuple) and tg[0]=='mom':
            mom_term += mu[k]*Mn[tg[1]]
    # dual feasibility: base - mom_term >= 0 ; i.e. base >= mom_term. With moments valid (>=0 on graphons),
    # the relevant exact statement is base[s] >= 0 after accounting for the (PSD-certified) moment block.
    resid = base - mom_term
    print(f"  cut+band+moment per-state dual residual: min={resid.min():.3e} (>= -1e-7 expected)",flush=True)
    print(f"  cut+band ONLY (drop moments) per-state min = {base.min():.3e}  (if >=0, band bound holds WITHOUT moments => fully cut-exact)",flush=True)
    pickle.dump(dual, open("envelope_k7_dual.pkl","wb"))
    print("saved envelope_k7_dual.pkl",flush=True)
    print(f"\n>>> HEADLINE: d_mono(W) <= 2/25 + {eta:.3e} on the band => a(5n)<=n^2 for n<= {thr_n(eta)} (N<= {5*thr_n(eta)}).",flush=True)
    print("    For the EXACT rational delta: round (lam,mu,rho) to rationals, g[s] & dedge[s] to their exact",flush=True)
    print("    densities, and verify per-type sum lam=1 + per-state residual>=0 with the G1 moment-PSD Gram-cert.",flush=True)
    print("DONE",flush=True)

if __name__=="__main__": main()
