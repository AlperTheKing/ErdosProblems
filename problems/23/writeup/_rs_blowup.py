"""Test layer-MAX bound (sum_i max_{I_i} S <= N?) on blow-ups and Mycielskians.
If it holds universally it would PROVE ROWSUM-O (since rowsum_f <= sum_i max_{I_i} S)."""
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
    worst=None
    for fi,f in enumerate(M):
        a,b=f
        d={a:0}; q=deque([a])
        while q:
            u=q.popleft()
            for w in adj[u]:
                if side[u]!=side[w] and w not in d: d[w]=d[u]+1; q.append(w)
        L=ell[f]; pf=P[fi]
        layers={}
        for v in pf: layers.setdefault(d[v],[]).append(v)
        rowsum=sum(pf[v]*S[v] for v in pf)
        maxsum=F(0)
        for i in range(L):
            vs=layers.get(i,[])
            maxsum+=max((S[v] for v in vs),default=F(0))
        if worst is None or maxsum>worst[0]:
            worst=(maxsum,rowsum,L,f)
    return worst,n

def blow_g6(g6,t):
    n,E=dec(g6); EE=[]
    for (a,b) in E:
        for i in range(t):
            for j in range(t): EE.append((a*t+i,b*t+j))
    return n*t,EE

def myciel(n,E):
    # Mycielskian: vertices 0..n-1 (orig), n..2n-1 (shadow u_i), 2n (apex w)
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    NN=2*n+1; EE=list(E)
    for i in range(n):
        for j in adj[i]:
            if j>i:
                EE.append((i, n+j)); EE.append((j, n+i))
    for i in range(n):
        EE.append((n+i, 2*n))
    # dedup
    EE=list(set((min(a,b),max(a,b)) for a,b in EE))
    return NN,EE

if __name__=="__main__":
    print('=== blow-ups of small odd cycles / census graphs ===')
    # C5, C7, C9 blowups
    cases=[('C9bare','H?bB@_W',1),('C9[2]','H?bB@_W',2),('C9[3]','H?bB@_W',3)]
    for name,g6,t in cases:
        nn,EE=blow_g6(g6,t); info=loads(nn,EE)
        if info is None: print(name,'no info'); continue
        worst,n=analyze(info)
        print('%-10s N=%d: maxlayersum=%s (%.4f N) rowsum=%s ell=%d  -> layermax%sN'%(
            name,n,str(worst[0]),float(worst[0])/n,str(worst[1]),worst[2], '<=' if worst[0]<=n else '>'))
    # Mycielskians: C5 -> Grotzsch(11) -> Myc(23)
    n0,E0=dec('Dr?')  # C5? let's build C5 directly
    C5=(5,[(0,1),(1,2),(2,3),(3,4),(4,0)])
    g11=myciel(*C5)
    info=loads(*g11)
    print('Grotzsch N=%d'%g11[0], end=' ')
    if info:
        worst,n=analyze(info); print('maxlayersum=%s (%.4f N) rowsum=%s ell=%d %s'%(str(worst[0]),float(worst[0])/n,str(worst[1]),worst[2],'<=N' if worst[0]<=n else '>N'))
    else: print('no info')
    g23=myciel(*g11)
    info=loads(*g23)
    print('Myc(Grotzsch) N=%d'%g23[0], end=' ')
    if info:
        worst,n=analyze(info); print('maxlayersum=%s (%.4f N) rowsum=%s ell=%d %s'%(str(worst[0]),float(worst[0])/n,str(worst[1]),worst[2],'<=N' if worst[0]<=n else '>N'))
    else: print('no info')
