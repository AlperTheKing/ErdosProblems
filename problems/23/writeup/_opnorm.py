"""rho(O)<=N  <=>  ||P||_op^2 <= N  <=>  for all x in R^m: ||P x||_2^2 <= N ||x||_2^2
   where (P x)(v) = sum_f x_f p_f(v).  P is n x m (vertices x bad-edges), P[v,f]=p_f(v) in [0,1].
COLUMN norms: ||column f||^2 = sum_v p_f(v)^2 = O_ff = ||p_f||^2 <= ell(f) (PROVEN).
Operator norm <= N is the statement. Equivalent: sum_v Phi(v)^2 <= N sum_f x_f^2,  Phi(v)=sum_f x_f p_f(v).

This is a RESTRICTED ISOMETRY / frame-bound statement. The family {p_f} of vectors in R^n has upper frame bound N.
Note sum_f ||p_f||^2 = sum_f O_ff = trace(O) = sum_v S... no, = sum_v sum_f p_f(v)^2 (not S).
And rows of P: row v has entries p_f(v), with sum_f p_f(v)=S(v), sum_f p_f(v)^2 <= S(v) (since p_f<=1).
So ||P||_F^2 = sum_v sum_f p_f(v)^2 <= sum_v S(v) = L.  And ||P||_op^2 >= ||P||_F^2/rank...

GERSHGORIN on O won't work (tight). Try: ||Px||^2 = sum_v (sum_f x_f p_f(v))^2.
By Cauchy-Schwarz per vertex: (sum_f x_f p_f(v))^2 <= (sum_f p_f(v)) (sum_f x_f^2 p_f(v)) = S(v) * sum_f x_f^2 p_f(v).
=> ||Px||^2 <= sum_v S(v) sum_f x_f^2 p_f(v) = sum_f x_f^2 (sum_v S(v) p_f(v)) = sum_f x_f^2 C(f).
So ||Px||^2 <= sum_f x_f^2 C(f) <= (max_f C(f)) sum_f x_f^2.  THIS IS EXACTLY ROWSUM-O => op-norm!
(Circular: per-vertex CS recovers rho(O)<=max rowsum, the Perron-Frobenius bound we already have.)

So the per-vertex Cauchy-Schwarz gives back ROWSUM-O. No free lunch. But it shows:
   ||Px||^2 <= sum_f x_f^2 C(f),  equality iff for each v, (x_f) is constant on supp over f through v (proportional to 1).
Let me VERIFY this CS chain exactly and measure the slack, to see where to inject extra structure."""
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
    print("=== op-norm form: verify ||Px||^2<=N||x||^2 directly (random x) + CS-chain slack ===")
    rng=np.random.default_rng(0)
    for nn in range(nmin,nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        if limit: out=out[:limit]
        worst=0.0; wg=None
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            M=info['M']; m=len(M)
            pfs=[pf_vec(info,f) for f in M]
            P=np.zeros((n,m))
            for j,d in enumerate(pfs):
                for v,val in d.items(): P[v,j]=float(val)
            lam=np.linalg.eigvalsh(P.T@P)[-1]
            if lam/nn>worst: worst=lam/nn; wg=g6
        print(f"  N={nn}: max ||P||_op^2/N = {worst:.5f} @ {wg}",flush=True)

if __name__=="__main__":
    run(7,10,limit=None)
