"""Search for a PROVABLE PSD upper bound K <= X with rho(X)<=N, X built from B (cut graph) structure.
K_{vw}=sum_f p_f(v)p_f(w), rho(K)<=N is the target.
Candidates X (test K <= X i.e. X-K PSD, exact eig via numpy float first):
  (a) X = diag(deg_B)            [since S(v)~<=deg_B; row sums of K are T(v) not S]
  (b) X = N * (something normalized)
  (c) X = D_B - A_B = L_B (graph Laplacian of cut graph)? rho(L_B)<=2 max deg <=2N.
  (d) X = adjacency-power: p_f lives on geodesic interval; K_{vw}>0 needs v,w co-on-a-geodesic.
Also directly: is rho(K) <= max_v deg_B(v)? (would give rho<=N-1<N if max deg<N, but star-ish graphs?)
Test max_v deg_B(v) vs rho(K)."""
import subprocess
import numpy as np
from fractions import Fraction as F
from _h import dec, GENG, loads

def pf_vec(info, f):
    Ps = info['cyc'][f]; nf = len(Ps); cnt = {}
    for P in Ps:
        for v in P: cnt[v] = cnt.get(v,0)+1
    return {v: F(cnt[v], nf) for v in cnt}

def run(nmin,nmax,limit=None):
    print("=== PSD/spectral comparison candidates ===")
    for nn in range(nmin,nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        if limit: out=out[:limit]
        # (1) rho(K) vs max deg_B  (does rho(K)<=maxdegB?)
        worst_rk_md=-1e9; w1=None
        # (2) diag(deg_B)-K PSD?
        psd_db_fail=0; w2=None
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            M=info['M']; m=len(M); side=info['side']; adj=info['adj']
            pfs=[pf_vec(info,f) for f in M]
            P=np.zeros((n,m))
            for j,d in enumerate(pfs):
                for v,val in d.items(): P[v,j]=float(val)
            K=P@P.T
            rk=np.linalg.eigvalsh(K)[-1]
            degB=np.array([sum(1 for w in adj[v] if side[w]!=side[v]) for v in range(n)],dtype=float)
            md=degB.max()
            if rk-md>worst_rk_md: worst_rk_md=rk-md; w1=(g6,rk,md)
            # diag(deg_B)-K
            eigmin=np.linalg.eigvalsh(np.diag(degB)-K)[0]
            if eigmin<-1e-9: psd_db_fail+=1;
            if w2 is None or eigmin<w2[1]: w2=(g6,eigmin)
        print(f"  N={nn}: max(rho(K)-maxdegB)={worst_rk_md:+.4f}@{w1} | diag(degB)-K not-PSD fails={psd_db_fail} mineig@{w2}",flush=True)

if __name__=="__main__":
    run(7,10,limit=None)
