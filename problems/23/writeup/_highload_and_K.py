"""TASK 3 + structural probe.
(A) Highest-load bound: is (O ell)_f <= sum of the ell(f) HIGHEST values of T(v)?  And is that <= N*ell(f)?
    [N*ell would need each of top-ell loads <= N, FALSE since max T can exceed N. Test both.]
(B) Crofton/coarea identity for the load along f's geodesic.
    T(v) = sum_w K_{vw}, K=P P^T. Along gate G_i, sum_{v in G_i} T(v) = sum_{v in G_i,w} K_{vw}.
    Test the coarea law:  sum_{i=0}^{h} L_i = (O ell)_f, and try to express via 'profile' of the load
    crossing gates. Define the layer-cumulative S_i = sum_{j<=i} L_j. Probe whether
    L_i is bounded by a quantity tied to delta_B(G_{i-1}) or delta_B(G_i).
(C) The KEY test: weighted-CD. The load that p_f sees in layer i is concentrated on layer-i vertices.
    Test:  L_i <= (mass_i=1) * max_{v in I_i} T(v), trivial; instead test the AVERAGED form
    sum_i L_i <= sum_i (avg over the 'gate annulus' of T) and whether annulus-averaged T <= N
    via CD applied to the annulus A_i = G_i \ G_{i-1}."""
import subprocess
from fractions import Fraction as F
from collections import deque
from _h import dec, GENG, loads, blow

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

def analyze(info):
    n=info['n']; T=info['T']; N=n; res=[]
    Tsorted=sorted(T,reverse=True)
    for f in info['M']:
        pf=pf_vec(info,f); ell=info['ell'][f]
        Of=sum(pf[v]*T[v] for v in pf)
        # (A) top-ell loads
        topell=sum(Tsorted[:ell])
        res.append(dict(f=f,ell=ell,N=N,Of=Of,topell=topell,
                        A_topell=(Of<=topell),
                        A_topellN=(topell<=F(N)*ell)))
    return res

def run(nmin,nmax,limit=None):
    print(f"=== top-ell load census N={nmin}..{nmax} ===")
    a1=0; a2=0; nf=0
    worst_a1=None
    for nn in range(nmin,nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        if limit: out=out[:limit]
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            for r in analyze(info):
                nf+=1
                if not r['A_topell']:
                    a1+=1
                    if worst_a1 is None: worst_a1=(g6,r['f'],float(r['Of']),float(r['topell']))
                if not r['A_topellN']: a2+=1
    print(f"bad_edges={nf} | (Of<=sum top-ell T) fails:{a1} | (sum top-ell T<=N*ell) fails:{a2}")
    if worst_a1: print(f"  example A1 fail: {worst_a1}")

if __name__=="__main__":
    run(7,10)
    print("\n=== blowups ===")
    for t in range(1,5):
        n,E=blow(t); info=loads(n,E)
        if info is None: continue
        rs=analyze(info)
        print(f"  C5[{t}] N={n}: A1fail={sum(not r['A_topell'] for r in rs)} A2fail={sum(not r['A_topellN'] for r in rs)}")
