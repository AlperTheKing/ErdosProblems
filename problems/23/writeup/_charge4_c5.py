"""C5-ANCHORED case: ALL bad edges have ell=5 (minimal odd cycle C5). Prove SINGLE-GEO here first.
For ell=5: each bad edge f=(a,b) (a,b same side, dist_B(a,b)=4). Geodesic interval layers I_0={a},I_1,I_2,I_3,I_4={b}.
A geodesic C = a - x1 - x2 - x3 - b with x1 in I_1, x2 in I_2, x3 in I_3.
Since ell=5 means the odd cycle through a,b plus the bad edge is a C5: a-b is the bad edge, and a..b path of length 4.
So the 5-cycle is a,b,x3,x2,x1? No: bad edge (a,b), B-geodesic a-x1-x2-x3-b length 4 -> 5-cycle a-x1-x2-x3-b-a. Yes C5.

Want: for a single such geodesic C={a,x1,x2,x3,b}, sum_{v in C} S(v) <= N.
S(v)=sum_g p_g(v). Decompose by where v sits.
Collect data: which graphs are C5-anchored, verify SINGLE-GEO, and inspect S-values on the 5 vertices.
Look for a per-vertex charge: e.g. S(a)+S(b) <= ? and S(x1)+S(x2)+S(x3) <= ?
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

def is_c5anchored(info):
    return all(v==5 for v in info['ell'].values())

def analyze(info):
    n=info['n']; N=n; M=info['M']; cyc=info['cyc']; ell=info['ell']
    pfs={f:pf_vec(info,f) for f in M}
    S={v:sum(pfs[g].get(v,F(0)) for g in M) for v in range(n)}
    data=[]
    for f in M:
        a,b=f
        for P in cyc[f]:
            # P = [a, x1, x2, x3, b]
            tot=sum(S[v] for v in P)
            data.append((f,P,[S[v] for v in P], tot, N))
    return data,S

def run(nmin,nmax,limit=None):
    print("=== C5-anchored SINGLE-GEO + per-vertex S structure ===")
    cnt_c5=0; worst=F(-10); wd=None
    # candidate sub-bounds:
    end_max=F(0)   # max S(a)+S(b) over endpoints / N
    mid_max=F(0)   # max S(x1)+S(x2)+S(x3) / N
    for nn in range(nmin,nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        if limit: out=out[:limit]
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            if not is_c5anchored(info): continue
            cnt_c5+=1
            data,S=analyze(info)
            for (f,P,Svals,tot,N) in data:
                if tot-N>worst: worst=tot-N; wd=(g6,f,P,[str(x) for x in Svals])
                end=Svals[0]+Svals[-1]
                mid=sum(Svals[1:-1])
                if end>end_max: end_max=end
                if mid>mid_max: mid_max=mid
        print(f"  N<={nn}: c5-anchored graphs={cnt_c5} | worst sum_C S - N={float(worst):+.4f} | max(S(a)+S(b))={float(end_max):.3f} max(S mid)={float(mid_max):.3f}",flush=True)
    print(f"  worst case detail: {wd}")

if __name__=="__main__":
    run(7,11, limit=None)
