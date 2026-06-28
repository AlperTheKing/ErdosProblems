"""Does the bound hold per single geodesic C of f, i.e. sum_{v in C} S(v) <= N?
If yes for a SINGLE geodesic, that's a much stronger/cleaner statement to prove.
If no, by how much does it fail (and does averaging save us)?

Also: study S(v) = sum_g p_g(v). For a FIXED geodesic C of f (a set of ell(f) vertices),
sum_{v in C} S(v) = sum_g sum_{v in C} p_g(v) = sum_g (p_g-mass landing on the vertex-set C).

For each g, sum_{v in C} p_g(v) = expected # of g-geodesic vertices that lie on C.
Triangle-free + shortest: how large can sum_{v in C} p_g(v) be for a single g?
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

def analyze(info):
    n=info['n']; N=n; M=info['M']; ell=info['ell']; cyc=info['cyc']
    pfs={f:pf_vec(info,f) for f in M}
    S={v:sum(pfs[g].get(v,F(0)) for g in M) for v in range(n)}
    worst_single=F(-10); ws=None
    # For each f, each actual geodesic C (vertex set), compute sum_{v in C} S(v).
    for f in M:
        for P in cyc[f]:
            tot=sum(S[v] for v in P)
            if tot-N>worst_single: worst_single=tot-N; ws=(f,P,float(tot),N)
    return worst_single, ws

def run(nmin,nmax,limit=None):
    print(f"=== single-geodesic sum_C S(v) - N  (max over all f, all geodesics) ===")
    worst=F(-10); wg=None
    for nn in range(nmin,nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        if limit: out=out[:limit]
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            w,ws=analyze(info)
            if w>worst: worst=w; wg=(g6,ws)
        print(f"  N<={nn}: max(sum_C S - N)={float(worst):+.4f} @ {wg}",flush=True)

if __name__=="__main__":
    run(7,10, limit=2000)
