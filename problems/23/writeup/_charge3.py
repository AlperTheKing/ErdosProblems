"""For a FIXED geodesic C of f (vertex set, ell(f) vertices), study sum_g mu_g(C), mu_g(C)=sum_{v in C} p_g(v).
We want sum_g mu_g(C) <= N. Decompose:
  - mu_f(C) = sum_{v in C} p_f(v).  (the self term; >= 1 since C itself is a geodesic giving p_f mass)
  - For g != f: mu_g(C) = p_g-mass landing on C.
Questions:
  (1) max single mu_g(C) over g (incl g=f). Triangle-free+shortest should cap how much one g overlaps a geodesic.
  (2) The 'charge per vertex' view: sum_g mu_g(C) = sum_{v in C} S(v). We charge S(v) at each of the ell(f)
      vertices of C. Is there a clean per-vertex/per-layer cap?
  (3) Crucially: is sum_g mu_g(C) = sum_{v in C} S(v), and can we bound S(v) for v in C by something layer-local?
"""
import subprocess
from fractions import Fraction as F
from collections import deque
from _h import dec, GENG, loads, blow

def pf_vec(info, f):
    Ps = info['cyc'][f]; nf = len(Ps); cnt = {}
    for P in Ps:
        for v in P: cnt[v] = cnt.get(v,0)+1
    return {v: F(cnt[v], nf) for v in cnt}

def analyze(info, report_max_mu=True):
    n=info['n']; N=n; M=info['M']; cyc=info['cyc']; ell=info['ell']
    pfs={f:pf_vec(info,f) for f in M}
    S={v:sum(pfs[g].get(v,F(0)) for g in M) for v in range(n)}
    max_mu=F(0); mm=None
    worst_tot=F(-10); wt=None
    for f in M:
        for P in cyc[f]:
            Cset=set(P)
            tot=sum(S[v] for v in P)
            if tot-N>worst_tot: worst_tot=tot-N; wt=(f,P,float(tot))
            for g in M:
                mu=sum(pfs[g].get(v,F(0)) for v in Cset)
                if mu>max_mu: max_mu=mu; mm=(f,g,float(mu),ell[g])
    return max_mu,mm,worst_tot,wt

def run(nmin,nmax,limit=None):
    print(f"=== max mu_g(C) (overlap of one g's geodesic-measure with a single f-geodesic C) ===")
    gmax=F(0); gg=None; gw=F(-10)
    for nn in range(nmin,nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        if limit: out=out[:limit]
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            mm_,mm,wt_,wt=analyze(info)
            if mm_>gmax: gmax=mm_; gg=(g6,mm)
            if wt_>gw: gw=wt_
        print(f"  N<={nn}: max mu_g(C)={float(gmax):.4f} @ {gg} | worst sum_C S - N={float(gw):+.4f}",flush=True)

if __name__=="__main__":
    run(7,10, limit=1500)
