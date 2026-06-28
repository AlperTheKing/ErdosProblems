"""SPEC route: rho(O) = lambda_max(O) <= N, where O_{fg}=<p_f,p_g>, O=P^T P, P[v,f]=p_f(v).
O and K=P P^T share nonzero spectrum. rho(O)=rho(K)=||P||_2^2.
Row sums of K = T(v). Row sums of O = (O 1)_f = sum_g <p_f,p_g> = <p_f, sum_g p_g>.

Test candidate spectral certificates for rho<=N:
 (S1) rho(O) <= max row-sum of O  (Perron/Gershgorin upper bd, O>=0 entrywise so rho<=max rowsum).
      Is max_f (O 1)_f <= N?  [if yes, DONE: rho<=maxrowsum<=N]
 (S2) rho(K) <= max row-sum of K = max_v T(v). FALSE generally (max T>N possible). Confirm.
 (S3) The Perron eigenvector of O is ell (claimed in setup). Check O ell ~ rho ell? Actually claim
      was tightness ell=Perron. Test ell^T O ell / ell^T ell <= N (Rayleigh at ell) -- that's exactly
      (Cycle-SM summed) / ||ell||^2... Actually sum_f ell_f (O ell)_f = ell^T O ell <= N ||ell||^2?
 (S4) rho(O) <= N via O <= N * Pi for some projection? Test O <= (something).
Compute rho(O) exactly-ish (float fine for eigenvalue), and the row-sum bounds exactly."""
import subprocess
import numpy as np
from fractions import Fraction as F
from collections import deque
from _h import dec, GENG, loads, blow

def pf_vec(info, f):
    Ps = info['cyc'][f]; nf = len(Ps); cnt = {}
    for P in Ps:
        for v in P: cnt[v] = cnt.get(v,0)+1
    return {v: F(cnt[v], nf) for v in cnt}

def build_O(info):
    M=info['M']; m=len(M); pfs=[pf_vec(info,f) for f in M]
    O=[[F(0)]*m for _ in range(m)]
    for i in range(m):
        for j in range(m):
            pi,pj=pfs[i],pfs[j]
            O[i][j]=sum(pi[v]*pj.get(v,F(0)) for v in pi)
    return O,M,pfs

def analyze(info):
    n=info['n']; N=n; O,M,pfs=build_O(info); m=len(M)
    ell=[info['ell'][f] for f in M]
    # row sums of O
    rowsum=[sum(O[i]) for i in range(m)]
    maxrow=max(rowsum) if rowsum else F(0)
    # rho via float
    Of=np.array([[float(O[i][j]) for j in range(m)] for i in range(m)])
    rho=float(np.linalg.eigvalsh(Of)[-1]) if m>0 else 0.0
    # Rayleigh at ell
    ellv=np.array([float(e) for e in ell])
    rayl = float(ellv@Of@ellv/(ellv@ellv)) if m>0 else 0.0
    return dict(N=N,m=m,maxrow=maxrow,rho=rho,rayl=rayl,
                S1=(maxrow<=F(N)), rho_le_N=(rho<=N+1e-9))

def run(nmin,nmax,limit=None):
    print(f"=== SPEC census N={nmin}..{nmax} ===")
    s1fail=0; rhofail=0; ng=0; worst_rho=0; worst_g=None; worst_maxrow=F(0); worst_mr_g=None
    for nn in range(nmin,nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        if limit: out=out[:limit]
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            ng+=1
            r=analyze(info)
            if not r['S1']:
                s1fail+=1
                if r['maxrow']/F(r['N'])>worst_maxrow:
                    worst_maxrow=r['maxrow']/F(r['N']); worst_mr_g=(g6,str(r['maxrow']),r['N'])
            if not r['rho_le_N']:
                rhofail+=1
            if r['rho']/r['N']>worst_rho: worst_rho=r['rho']/r['N']; worst_g=(g6,r['rho'],r['N'])
    print(f"graphs={ng} | (S1) maxrowsum(O)<=N fails:{s1fail} | rho(O)<=N fails:{rhofail}")
    print(f"  worst rho/N = {worst_rho:.4f} @ {worst_g}")
    print(f"  worst maxrowsum(O)/N = {float(worst_maxrow):.4f} @ {worst_mr_g}")

if __name__=="__main__":
    run(7,10)
    print("\n=== blowups ===")
    for t in range(1,6):
        n,E=blow(t); info=loads(n,E)
        if info is None: continue
        r=analyze(info)
        print(f"  C5[{t}] N={n}: rho={r['rho']:.4f} rho/N={r['rho']/r['N']:.4f} maxrow(O)={float(r['maxrow']):.3f} S1={r['S1']} rayl={r['rayl']:.4f}")
