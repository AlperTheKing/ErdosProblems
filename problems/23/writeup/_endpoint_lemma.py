"""Anti-concentration mechanism: where p_f=1 (endpoints a,b and any forced-cut vertex), S is small.
Structural sub-lemmas to test EXACTLY (census + blowups):
 (EP) For a bad-edge endpoint a (so p_f(a)=1 for f incident to a): S(a) <= ?
      S(a)=sum_g p_g(a). Conjecture forms:
        (EP1) S(a) <= deg_B(a)  (B-degree)?
        (EP2) S(a) <= (# bad edges incident to a) + (# bad edges with a STRICTLY interior on geodesic)?
 (KEY) Test the GLOBAL weighted bound that would give ROWSUM-O:
        sum_v p_f(v) S(v) <= sum_v p_f(v) * h(v)  where h(v) is a SIMPLE per-vertex quantity with
        sum_v p_f(v) h(v) <= N provable. Candidates h(v): 1+? , deg_B(v), ...
 (CONV) Power-mean: since sum_{I_i}p_f=1 per layer, by convexity sum_{I_i}p_f S >= (sum p_f S?) ...
        Actually we want UPPER bound. Test Jensen the other way won't help.
 (PFSQ) Test:  sum_v p_f(v) S(v) <= sum_v p_f(v) + sum_v p_f(v)(S(v)-1)_+ ...
 Direct useful test: is S(v) <= 1 + (number of OTHER bad edges strictly-interior-passing v)?
   i.e. decompose S(v) = [p_f(v) for f with v endpoint] + [interior].
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
    print("=== endpoint & per-vertex structural sub-lemmas ===")
    # (EP1) S(a) <= deg_B(a) for endpoints a
    ep1_fail=0; ep1_worst=F(-10); ep1w=None
    # S(v) <= deg_B(v) for ALL v?
    allv_fail=0; allv_worst=F(-10); allvw=None
    for nn in range(nmin,nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        if limit: out=out[:limit]
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            M=info['M']; side=info['side']; adj=info['adj']
            pfs={f:pf_vec(info,f) for f in M}
            S={v:sum(pfs[g].get(v,F(0)) for g in M) for v in range(n)}
            degB=[sum(1 for w in adj[v] if side[w]!=side[v]) for v in range(n)]
            endpoints=set()
            for (a,b) in M: endpoints.add(a); endpoints.add(b)
            for v in range(n):
                r=S[v]-degB[v]
                if v in endpoints:
                    if r>0: ep1_fail+=1
                    if r>ep1_worst: ep1_worst=r; ep1w=(g6,v,float(S[v]),degB[v])
                if r>0: allv_fail+=1
                if r>allv_worst: allv_worst=r; allvw=(g6,v,float(S[v]),degB[v])
        print(f"  N<={nn}: (EP1)S(a)>deg_B(a) endpoint-fails={ep1_fail} worst={float(ep1_worst):+.3f}@{ep1w} | (ALL)S(v)>deg_B(v) fails={allv_fail} worst={float(allv_worst):+.3f}@{allvw}",flush=True)

if __name__=="__main__":
    run(7,10,limit=None)
