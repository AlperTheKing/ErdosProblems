#!/usr/bin/env python3
"""STEP 2-4 of the exact cert: rationalize the dual, recompute cut coeffs EXACTLY (k8/Horn=int/90, k7=int/denom
found empirically, dedge=int/45), and check the per-state dual-feasibility residual in EXACT Fractions.
First pass: cut+band+Horn ONLY (no moments) -- if min residual >= 0, the cert is self-contained rational; else
report the per-state deficit the order-9 G1 moment-Gram must cover. delta = HI*mu_hi - LO*mu_lo + rho - 2/25*a8."""
import pickle, numpy as np, time
from fractions import Fraction as Fr
LO,HI=Fr(2486,10000),Fr(3197,10000)
TWO25=Fr(2,25); THR_A30=Fr(1,450)
ns,dedge,rows,provtypes,_=pickle.load(open("cp_cache.pkl","rb"))
d=np.load("c5lift_cache.npz",allow_pickle=True)
from scipy.sparse import csr_matrix
D=csr_matrix((d["Dval"],(d["Drow"],d["Dcol"])),shape=(ns,int(d["nJ"]))); nJ=D.shape[1]; DT=D.T.tocsr()
dedge_q=np.asarray(DT@dedge).ravel()
H=pickle.load(open("horn_dual.pkl","rb")); z=np.asarray(H["z"]); tagS=H["tag"]; m_ub=H["m_ub"]
st=pickle.load(open("horn_cert_state_it16.pkl","rb")); env=st["env"]
ETA=nJ; U7=nJ+1; n7=H.get('n7', None)
# locate named duals by tag string
def tagi(name): return tagS.index(name)
mu_hi=z[tagi('band_hi')]; mu_lo=z[tagi('band_lo')]; a7=z[tagi('k7leg')]; a8=z[tagi('k8leg')]; rho=float(z[m_ub])
# env duals: tags ('env',ei) -> string "('env', 0)"
envdual={}
for k,t in enumerate(tagS):
    if t.startswith("('env'"): envdual[int(t.split(',')[1].rstrip(')'))]=z[k]
print(f"float duals: rho={rho:.6e} mu_hi={mu_hi:.3e} mu_lo={mu_lo:.3e} a7={a7:.4f} a8={a8:.4f}",flush=True)
# ---- classify env cuts correctly: k8 has a col >= U8; k7 has a col in [U7,U8); horn has only q cols ----
U8=nJ+1+ (n7 if n7 else 107)
def classify(idx):
    idxa=np.asarray(idx)
    if (idxa>=U8).any(): return 'k8'
    if ((idxa>=U7)&(idxa<U8)).any(): return 'k7'
    return 'horn'
# ---- exact rational recovery of a cut's q-coefficients ----
def to_frac_q(dat, idx, denom):
    out={}
    for v,j in zip(dat,idx):
        if j>=U7: continue  # leg var coeff (=1.0), not a q coeff
        num=round(v*denom)
        if num!=0: out[int(j)]=Fr(int(num),denom)
    return out
# find k7 denom empirically from one k7 cut
k7denoms=[10*181440, 181440, 90, 45, 3628800, 1814400]
def best_denom(dat,idx,cands):
    best=None;berr=1
    for dd in cands:
        err=max(abs(v*dd-round(v*dd)) for v,j in zip(dat,idx) if j<U7)
        if err<berr: berr=err;best=dd
    return best,berr
# rationalize duals (limit denominator; big margin tolerates coarse rounding)
def rat(x,maxden=10**6):
    return Fr(x).limit_denominator(maxden)
rho_f=rat(rho); mu_hi_f=rat(mu_hi); mu_lo_f=rat(mu_lo); a8_f=rat(a8)
# ---- accumulate exact per-state residual over the 12172 q-states (sparse) ----
t0=time.time()
resid=[Fr(0)]*nJ
for s in range(nJ):
    resid[s]= rho_f + (mu_hi_f-mu_lo_f)*Fr(dedge_q[s]).limit_denominator(45)  # dedge=int/45
# subtract dual*cut over each env cut's nonzeros
cls_count={'k7':0,'k8':0,'horn':0}; denom_seen={}
for ei,(dat,idx) in enumerate(env):
    lam=envdual.get(ei,0.0)
    if abs(lam)<1e-15:
        cls_count[classify(idx)]+=1; continue
    c=classify(idx); cls_count[c]+=1
    if c=='horn' or c=='k8': denom=90
    else:
        denom,err=best_denom(dat,idx,k7denoms); denom_seen[denom]=denom_seen.get(denom,0)+1
    lam_f=rat(lam)
    for v,j in zip(dat,idx):
        if j>=U7: continue
        num=round(v*denom)
        if num: resid[int(j)] -= lam_f*Fr(int(num),denom)
mn=min(resid); mns=int(np.argmin([float(r) for r in resid]))
delta=HI*mu_hi_f - LO*mu_lo_f + rho_f - TWO25*a8_f
print(f"env classes: {cls_count}; k7 denoms: {denom_seen}",flush=True)
print(f"EXACT cut+band+Horn (NO moments) per-state residual: min={float(mn):.6e} at state {mns}  [{time.time()-t0:.0f}s]",flush=True)
print(f"  >=0 everywhere? {mn>=0}  ({'CUT-EXACT, no moment Gram needed' if mn>=0 else 'moment Gram must cover the deficit'})",flush=True)
print(f"delta (exact) = {delta} = {float(delta):.6e}; < 1/450={float(THR_A30):.6e}? {delta<THR_A30}  margin x{float(THR_A30/delta):.1f}",flush=True)
pickle.dump(dict(resid=[ (r.numerator,r.denominator) for r in resid], delta=(delta.numerator,delta.denominator),
                 rho=(rho_f.numerator,rho_f.denominator), mu_hi=(mu_hi_f.numerator,mu_hi_f.denominator),
                 mu_lo=(mu_lo_f.numerator,mu_lo_f.denominator), a8=(a8_f.numerator,a8_f.denominator),
                 min_resid=(mn.numerator,mn.denominator)), open("horn_exact_resid.pkl","wb"))
print("saved horn_exact_resid.pkl",flush=True); print("DONE",flush=True)
