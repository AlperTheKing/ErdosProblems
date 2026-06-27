#!/usr/bin/env python3
"""Exact R_cbh[s] = rho + (mu_hi-mu_lo)*dedge[s] + sum_{env cut} lambda * coeff[s]  (cut+band+Horn, NO moments),
in exact Fractions. Cut coeffs + duals recovered via Fraction(x).limit_denominator(1e8) (all exact rationals:
k8/Horn int/90, k7 int/<few-million>, dedge int/45). This is the RHS for the moment-PSD step: find Q>=0 with
sum_t D[t,s]<Q,P^sigma_t> <= R_cbh[s].  delta = HI*mu_hi - LO*mu_lo + rho - 2/25*a8 (exact)."""
import pickle, numpy as np, time
from fractions import Fraction as Fr
LO=Fr(2486,10000); HI=Fr(3197,10000); TWO25=Fr(2,25); MAXDEN=10**8
ns,dedge,rows,provtypes,_=pickle.load(open("cp_cache.pkl","rb"))
from scipy.sparse import csr_matrix
d=np.load("c5lift_cache.npz",allow_pickle=True)
D=csr_matrix((d["Dval"],(d["Drow"],d["Dcol"])),shape=(ns,int(d["nJ"]))); nJ=D.shape[1]; DT=D.T.tocsr()
dedge_q=np.asarray(DT@dedge).ravel()
H=pickle.load(open("horn_dual.pkl","rb")); z=np.asarray(H["z"]); tagS=H["tag"]; m_ub=H["m_ub"]
st=pickle.load(open("horn_cert_state_it16.pkl","rb")); env=st["env"]
U7=nJ+1; U8=nJ+1+107
def tagi(n): return tagS.index(n)
def rat(x): return Fr(float(x)).limit_denominator(MAXDEN)
mu_hi=rat(z[tagi('band_hi')]); mu_lo=rat(z[tagi('band_lo')]); rho=rat(z[m_ub]); a8=rat(z[tagi('k8leg')])
envdual={}
for k,t in enumerate(tagS):
    if t.startswith("('env'"): envdual[int(t.split(',')[1].rstrip(')'))]=z[k]
# exact dedge (int/45)
dedge_f=[Fr(round(v*45),45) for v in dedge_q]
print(f"rationalized duals: rho={float(rho):.6e} mu_hi={float(mu_hi):.2e} mu_lo={float(mu_lo):.2e} a8={float(a8):.4f}",flush=True)
t0=time.time()
resid=[rho + (mu_hi-mu_lo)*dedge_f[s] for s in range(nJ)]
nadd=0
for ei,(dat,idx) in enumerate(env):
    lam=envdual.get(ei,0.0)
    if abs(lam)<1e-15: continue
    lam_f=rat(lam)
    for v,j in zip(dat,idx):
        if j>=U7: continue
        resid[int(j)] += lam_f*Fr(float(v)).limit_denominator(MAXDEN)  # += lam*(stored coeff): R += y*A[row,s]
    nadd+=1
    if nadd%500==0: print(f"  {nadd} cuts [{time.time()-t0:.0f}s]",flush=True)
mn=min(resid); mns=int(np.argmin([float(r) for r in resid])); mx=max(resid)
delta=HI*mu_hi - LO*mu_lo + rho - TWO25*a8
print(f"EXACT R_cbh: min={float(mn):.6e} (state {mns}) max={float(mx):.6e}  [{time.time()-t0:.0f}s, {nadd} cuts]",flush=True)
print(f"  delta(exact)={delta}={float(delta):.6e}  <5e-5? {delta<Fr(5,100000)}  <1/450? {delta<Fr(1,450)}",flush=True)
print(f"  (moment step must find Q>=0 with sum_t D[t,s]<Q,P_t> <= R_cbh[s]; feasible since float Q* exists)",flush=True)
pickle.dump(dict(Rcbh=[(r.numerator,r.denominator) for r in resid],
                 delta=(delta.numerator,delta.denominator),
                 rho=(rho.numerator,rho.denominator),mu_hi=(mu_hi.numerator,mu_hi.denominator),
                 mu_lo=(mu_lo.numerator,mu_lo.denominator),a8=(a8.numerator,a8.denominator)),
            open("horn_Rcbh_exact.pkl","wb"))
print("saved horn_Rcbh_exact.pkl",flush=True); print("DONE",flush=True)
