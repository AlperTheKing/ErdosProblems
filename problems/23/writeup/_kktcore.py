"""Characterize the KKT core (= worst-case y = maximizer of the CORR deficit g(y)) to feed Codex's exclusion route.
g(y) = sum_f sum_{i<j} sqrt(w_fi w_fj) - 0.5 sum_v (N-S(v)) y_v,  concave, homog deg 1, g<=0 = CORR.
A KKT core = nonzero y with g(y)=0 (the tight boundary; a counterexample would have g>0).
Probe: max g over simplex {y>=0, sum y = N}. Report (1) max g (should be 0 at extremals Gamma=N^2, <0 else =>
NO nonzero core off the extremal family); (2) at extremals, the structure of a tight y (uniform? supported on
one odd cycle?); (3) correlation of the maximizer with (T-N)_+ and with 1."""
import numpy as np, subprocess
from scipy.optimize import minimize
from _h import dec, GENG, loads
from _layerprice import layers_of

def setup(info):
    n=info['n']; M=info['M']; N=n
    L=[(f,)+layers_of(info,f) for f in M]   # (f, lay, pf, h)
    S=np.zeros(n)
    for (f,lay,pf,h) in L:
        for i in lay:
            for v in lay[i]: S[v]+=pf[v]
    return L,S,N,n

def gdef(L,S,N,n,y):
    lhs=0.0
    for (f,lay,pf,h) in L:
        w=[sum(y[v]*pf[v] for v in lay[i]) for i in range(h+1)]
        for i in range(h+1):
            for j in range(i+1,h+1):
                lhs+=np.sqrt(max(w[i],0.)*max(w[j],0.))
    rhs=0.5*sum((N-S[v])*y[v] for v in range(n))
    return lhs-rhs

def maxg(L,S,N,n,restarts=10):
    rng=np.random.default_rng(0); best=-1e9; by=None
    def neg(z):
        y=np.abs(z); s=y.sum()
        if s<=0: return 0.0
        return -gdef(L,S,N,n,y/s*N)
    starts=[np.ones(n)]+[rng.random(n) for _ in range(restarts)]
    for z0 in starts:
        r=minimize(neg,z0,method='Nelder-Mead',options={'maxiter':4000,'xatol':1e-7,'fatol':1e-10})
        y=np.abs(r.x); y=y/y.sum()*N; d=gdef(L,S,N,n,y)
        if d>best: best=d; by=y
    return best,by

def cos(a,b):
    a=np.array(a,float); b=np.array(b,float)
    if np.linalg.norm(a)==0 or np.linalg.norm(b)==0: return 0.0
    return abs(a@b)/(np.linalg.norm(a)*np.linalg.norm(b))

if __name__=="__main__":
    print("=== KKT core (worst-y) structure: max g(y) over simplex ===")
    tests=["FCp`_","H?bB@_W","J?AEB?oE?W?","I?BD@g]Qo","I?ABCc]}?","I?rFf_{N?"]
    for g6 in tests:
        n,E=dec(g6); info=loads(n,E); L,S,N,n=setup(info); G=info['G']; T=[float(t) for t in info['T']]
        mg,by=maxg(L,S,N,n)
        ov=[max(T[v]-N,0.0) for v in range(n)]
        ex = (G==n*n)
        print(f"  {g6:13} N={n} Gamma={G} (extremal:{ex}) | max g(y)={mg:+.4f} | cos(y*,1)={cos(by,[1]*n):.3f} cos(y*,(T-N)+)={cos(by,ov):.3f} | y* (rounded)={[round(v,2) for v in by]}")
    print("--- census: is max g(y) <= 0 with equality ONLY at extremals (Gamma=N^2)? ---")
    for nn in (8,9):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        worst=None; wg=None; tight_nonextremal=0; n_ext_tight=0
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            L,S,N,n=setup(info); mg,by=maxg(L,S,N,n,restarts=4)
            ex=(info['G']==n*n)
            if worst is None or mg>worst: worst=mg; wg=g6
            if mg>1e-4 and not ex: tight_nonextremal+=1
            if mg>-1e-4 and ex: n_ext_tight+=1
        print(f"  N={nn}: max over census of max_y g = {worst:+.4f}@{wg} | nonextremal-with-core(g>0):{tight_nonextremal} | extremals-tight:{n_ext_tight}",flush=True)
