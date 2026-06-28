"""Anti-concentration probe for ROWSUM-O: C(f)=sum_v p_f(v)S(v)<=N.
Idea: At extremal, S(v)=N/ell(f) on the interval and C(f)=ell*(N/ell)=N.
Define excess e(v)=S(v)-? . We need sum_v p_f(v) S(v) <= N = sum_v p_f(v) * (N/ell(f)) * ... no, sum p_f=ell.

REWRITE: C(f) <= N  <=>  sum_v p_f(v) S(v) <= N  <=>  sum_v p_f(v) (S(v) - N/ell(f)*?).
Since sum_v p_f(v)=ell(f), if S(v) were constant = N/ell(f) we'd get C(f)=N. So:
   C(f)-N = sum_v p_f(v)(S(v)) - N = sum_v p_f(v) S(v) - (N/ell)*sum_v p_f(v) = sum_v p_f(v)(S(v)-N/ell).
   => C(f)<=N  <=>  sum_v p_f(v)(S(v) - N/ell(f)) <= 0   <=>  <p_f, S - (N/ell)1> <= 0.
So the centered statement:  the p_f-weighted average of (S - N/ell) over the interval is <= 0.
i.e. on f's geodesic interval, S is on average (weighted by p_f) at most N/ell(f).

Test: covariance/correlation between p_f and S. Where p_f BIG (bottleneck vertices, few geodesics),
is S small? Compute Cov_{p_f}(p_f, S) ... actually we want <p_f, S> <= N.

Probe the centered quantity directly + look at the SIGN structure of (S(v)-N/ell) weighted by p_f.
Also test a candidate: sum_v p_f(v)^2 * something. And test  sum_v p_f(v) S(v) <= sum_v p_f(v) * T(v)/5
(true since S<=T/5) then need sum_v p_f(v) T(v) <= 5N? That's Cycle-SM with ell replaced by 5. Test it.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads

def pf_vec(info, f):
    Ps = info['cyc'][f]; nf = len(Ps); cnt = {}
    for P in Ps:
        for v in P: cnt[v] = cnt.get(v,0)+1
    return {v: F(cnt[v], nf) for v in cnt}

def run(nmin,nmax,limit=None):
    print("=== anti-concentration probes ===")
    # (1) Cycle-SM-with-5: sum_v p_f(v) T(v) <= 5N ?  (since S<=T/5, C(f)=<p_f,S> <= <p_f,T>/5 <= N iff this)
    w1=F(-10); g1=None
    # (2) the actual Cycle-SM: sum_v p_f(v)T(v) <= N*ell(f) ?  (proven-equivalent route, should hold)
    w2=F(-10); g2=None
    # (3) does <p_f,S> <= <p_f,T>/5 give slack? i.e. is the S<=T/5 bound tight on p_f-support?
    for nn in range(nmin,nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        if limit: out=out[:limit]
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            M=info['M']; ell=info['ell']; T=info['T']
            pfs={f:pf_vec(info,f) for f in M}
            for f in M:
                pfT=sum(pfs[f][v]*T[v] for v in pfs[f])
                # (1) pfT <= 5N
                r1=pfT-5*n
                if r1>w1: w1=r1; g1=(g6,f,float(pfT),n)
                # (2) pfT <= N*ell
                r2=pfT-n*ell[f]
                if r2>w2: w2=r2; g2=(g6,f,float(pfT),n,ell[f])
    print(f"  (1) max(<p_f,T> - 5N) = {float(w1):+.4f} @ {g1}   [<=0 would give ROWSUM-O via S<=T/5]")
    print(f"  (2) max(<p_f,T> - N*ell(f)) = {float(w2):+.4f} @ {g2}  [Cycle-SM, expected <=0]")

if __name__=="__main__":
    run(7,10, limit=None)
