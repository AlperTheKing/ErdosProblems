"""Test interval-based sufficient bounds for ROWSUM-O.
For bad edge f, Int(f)=union of layers I_0..I_h (the geodesic interval).
Candidates (exact, want each to IMPLY C(f)<=N AND hold census-wide):
 (A) C(f) <= |Int(f)|  AND |Int(f)| <= N (trivially true, Int subset of V). Is C(f)<=|Int(f)|?
 (B) sum_i bar S_i <= |Int(f)|  (same as A).
 (C) Finer: bar S_i <= |I_i| for each layer? (then C(f)<=|Int| <=N). Test per-layer.
 (D) The mass-balance:  sum_{v in Int(f)} S(v) >= C(f)? i.e. is C(f) <= sum over interval of S?
     C(f)=sum_{v in Int} p_f(v) S(v) and p_f(v)<=1 so C(f) <= sum_{v in Int} S(v). Then need sum_{Int}S<=N? test.
 (E) The REAL question: is sum_{v in Int(f)} S(v) <= N? (interval-total of S). Stronger than C(f)<=N since p_f<=1.
"""
import subprocess
from fractions import Fraction as F
from collections import deque
from _h import dec, GENG, loads

def pf_vec(info, f):
    Ps = info['cyc'][f]; nf = len(Ps); cnt = {}
    for P in Ps:
        for v in P: cnt[v] = cnt.get(v,0)+1
    return {v: F(cnt[v], nf) for v in cnt}

def bdist(info,s):
    adj=info['adj']; side=info['side']
    d={s:0}; q=deque([s])
    while q:
        u=q.popleft()
        for w in adj[u]:
            if side[u]!=side[w] and w not in d: d[w]=d[u]+1; q.append(w)
    return d

def run(nmin,nmax,limit=None):
    print("=== interval bounds ===")
    # (A/D) C(f) <= sum_{Int} S ?  (E) sum_{Int} S <= N ?  (C) bar S_i <= |I_i| ?
    worstE=F(-10); wE=None       # sum_{Int}S - N
    worstC=F(-10); wC=None       # bar S_i - |I_i|
    Aok=0; Afail=0
    for nn in range(nmin,nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        if limit: out=out[:limit]
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            M=info['M']; ell=info['ell']
            pfs={f:pf_vec(info,f) for f in M}
            S={v:sum(pfs[g].get(v,F(0)) for g in M) for v in range(n)}
            for f in M:
                a,b=f; h=ell[f]-1
                da=bdist(info,a)
                Int=set(pfs[f].keys())
                # interval-total of S
                Etot=sum(S[v] for v in Int)
                if Etot-n>worstE: worstE=Etot-n; wE=(g6,f,float(Etot),n)
                # per-layer
                layers=[[] for _ in range(h+1)]
                for v in Int:
                    i=da.get(v,-1)
                    if 0<=i<=h: layers[i].append(v)
                for i in range(h+1):
                    barSi=sum(pfs[f][v]*S[v] for v in layers[i])
                    Li=len(layers[i])
                    if barSi-Li>worstC: worstC=barSi-Li; wC=(g6,f,i,float(barSi),Li)
    print(f"  (E) max(sum_Int S - N) = {float(worstE):+.4f} @ {wE}")
    print(f"  (C) max(bar S_i - |I_i|) = {float(worstC):+.4f} @ {wC}")

if __name__=="__main__":
    run(7,10, limit=None)
