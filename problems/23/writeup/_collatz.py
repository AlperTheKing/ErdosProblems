"""Collatz-Wielandt for rho(O)<=N: it SUFFICES to find ANY positive vector x (per bad edge weighting)
with (O x)_f <= N x_f for all f. Then rho(O)=lambda_max(O)<=N (Perron-Frobenius, O>=0 entrywise).
We've tested x=1 (ROWSUM-O) and x=ell (Cycle-SM). Both hold census but both tight at extremals.
Question: is there an EASIER x (e.g. x_f = ||p_f||, or x_f = O_ff, or x_f=ell(f)^2) that has STRICT slack
even at extremals (=> more robust to prove), OR that decouples nicely?

Also compute lambda_max(O) directly (float) vs N to see the true spectral margin, and the Perron eigenvector
of O — maybe IT has a clean combinatorial meaning that suggests the proof.
"""
import subprocess
import numpy as np
from fractions import Fraction as F
from _h import dec, GENG, loads

def pf_vec(info, f):
    Ps = info['cyc'][f]; nf = len(Ps); cnt = {}
    for P in Ps:
        for v in P: cnt[v] = cnt.get(v,0)+1
    return {v: F(cnt[v], nf) for v in cnt}

def build_O(info):
    M=info['M']; m=len(M); n=info['n']
    pfs=[pf_vec(info,f) for f in M]
    P=np.zeros((n,m))
    for j,d in enumerate(pfs):
        for v,val in d.items(): P[v,j]=float(val)
    O=P.T@P
    ell=np.array([info['ell'][f] for f in M],dtype=float)
    return O,ell,M,pfs

def run(nmin,nmax,limit=None):
    print("=== Collatz-Wielandt: lambda_max(O)/N and candidate certificate vectors ===")
    for nn in range(nmin,nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        if limit: out=out[:limit]
        worst_lam=0.0; wg=None
        # test x candidates: 1, ell, diag(O), ell^2, sqrt-diag
        cwfail={'one':0,'ell':0,'diag':0,'ell2':0}
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            O,ell,M,pfs=build_O(info)
            m=len(M)
            lam=np.linalg.eigvalsh(O)[-1]
            if lam/n>worst_lam: worst_lam=lam/n; wg=g6
            diag=np.diag(O)
            for name,x in [('one',np.ones(m)),('ell',ell),('diag',diag),('ell2',ell**2)]:
                Ox=O@x
                # check Ox <= N x + tiny
                if np.any(Ox > n*x + 1e-9): cwfail[name]+=1
        print(f"  N={nn}: max lambda_max(O)/N = {worst_lam:.5f} @ {wg} | CW-fails: {cwfail}",flush=True)

if __name__=="__main__":
    run(7,10, limit=None)
