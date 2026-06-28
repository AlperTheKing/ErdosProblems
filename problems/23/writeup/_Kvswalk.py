"""Test spectral comparison of K with B-graph walk operators, to inject odd-girth>=5.
Candidates (each must have rho<=N and >=K as PSD):
  - A_B (adjacency of B): rho(A_B)<=max B-degree, unrelated to N directly.
  - The point: p_f(v) for f=(a,b) = sigma_a(v) sigma_b(v)/sigma_ab (betweenness), built from B-walks.
Just MEASURE: is there a constant c with K <= c * L_B (B-graph Laplacian)? No (L_B singular, const null,
but K const-eigval=N not 0). Is N*I-K >= 0 implied by N*I - K >= eps * L_B for the RIGHT B-weighting?
Probe: compute, on Myc N=23 and a census graph, the generalized eigenvalues of (K, something) to see
what natural operator K is dominated by. Specifically test K <= diag(T) (FALSE in general, =per-vertex)
and K <= the 'layer-collapsed' all-ones-per-cycle model.
Most useful: just report lambda_min(N*I-K) over a broad exact census to CONFIRM SPEC holds (sanity that
the target is true) and find the tightest non-blowup graph (smallest positive gap), to characterize the
extremal family precisely."""
from fractions import Fraction as F
from _h import dec, loads, blow
from _schur_spec import pf_exact
import numpy as np, subprocess
GENG='E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe'

def buildK(info):
    P,M,ell,n=pf_exact(info)
    K=np.zeros((n,n))
    for d in P:
        for v,pv in d.items():
            for wv,pw in d.items():
                K[v][wv]+=float(pv)*float(pw)
    return K,n

if __name__=="__main__":
    print('=== smallest positive gap N - rho(K) over census (which graphs are near-tight?) ===')
    for nn in [7,8,9,10,11]:
        out=subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split()
        stride=1 if nn<=9 else (6 if nn==10 else 50)
        best=None  # smallest gap among non-tight
        zero_tight=[]
        for g6 in out[::stride]:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            K,n=buildK(info)
            rho=max(np.linalg.eigvalsh(K))
            gap=n-rho
            if gap<1e-6:
                zero_tight.append(g6)
            else:
                if best is None or gap<best[0]: best=(gap,g6,rho,n)
        print('N=%d: #exactly-tight(rho=N)=%d %s | smallest positive gap=%.5f @%s rho=%.4f'%(
            nn,len(zero_tight),zero_tight[:3],best[0],best[1],best[2]))
