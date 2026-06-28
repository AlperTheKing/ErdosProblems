"""Layer-decomposition probe of ROWSUM-O.
rowsum_f = sum_v p_f(v) S(v) = sum_i (weighted avg of S over layer I_i, weight p_f sums to 1).
Compare rowsum_f vs sum_i max_{I_i} S vs N. Find where the layer-max bound overshoots and how
the p_f-weighting recovers <= N (anti-concentration)."""
from fractions import Fraction as F
from _h import dec, loads
from _schur_spec import pf_exact
from collections import deque
import subprocess
GENG='E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe'

def analyze(info):
    P,M,ell,n=pf_exact(info)
    adj=info['adj']; side=info['side']
    S=[sum(P[fi].get(v,F(0)) for fi in range(len(M))) for v in range(n)]
    res=[]
    for fi,f in enumerate(M):
        a,b=f
        d={a:0}; q=deque([a])
        while q:
            u=q.popleft()
            for w in adj[u]:
                if side[u]!=side[w] and w not in d: d[w]=d[u]+1; q.append(w)
        L=ell[f]
        pf=P[fi]
        layers={}
        for v in pf: layers.setdefault(d[v],[]).append(v)
        rowsum=sum(pf[v]*S[v] for v in pf)
        layer_avg=[]; layer_max=[]
        for i in range(L):
            vs=layers.get(i,[])
            wa=sum(pf[v]*S[v] for v in vs)
            mx=max((S[v] for v in vs),default=F(0))
            layer_avg.append(wa); layer_max.append(mx)
        res.append((f,L,rowsum,sum(layer_max),layer_avg,layer_max))
    return res,n

if __name__=="__main__":
    out=subprocess.run([GENG,'-tc','9'],capture_output=True,text=True).stdout.split()
    worst=None; worstmaxsum=None
    for g6 in out:
        n,E=dec(g6); info=loads(n,E)
        if info is None: continue
        P,M,ell,n=pf_exact(info)
        if max(ell.values())<=5: continue
        res,n=analyze(info)
        for (f,L,rs,maxsum,la,lm) in res:
            ratio=F(rs,n)
            if worst is None or ratio>worst[0]:
                worst=(ratio,g6,f,L,rs,n,la,lm)
            mr=F(maxsum,n)
            if worstmaxsum is None or mr>worstmaxsum[0]:
                worstmaxsum=(mr,g6,f,L,maxsum,n)
    print('worst rowsum/N:',float(worst[0]),'g6=',worst[1],'ell=',worst[3],'rowsum=',str(worst[4]),'N=',worst[5])
    print('   layer_avg=',[str(x) for x in worst[6]])
    print('   layer_max=',[str(x) for x in worst[7]])
    print('worst layermaxsum/N:',float(worstmaxsum[0]),'g6=',worstmaxsum[1],'ell=',worstmaxsum[3],'maxsum=',str(worstmaxsum[4]),'N=',worstmaxsum[5])
