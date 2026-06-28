"""STRESS-TEST candidate LAYER-MAX:  sum_i max_{v in I_i(f)} S(v) <= N  for every bad edge f.
If true it proves ROWSUM-O (rowsum_f <= sum_i max_{I_i} S <= N).
Test on: full census N<=11 (done elsewhere, 0 overshoot), random triangle-free N up to ~16,
and Mycielskians (with a custom max-cut that is not brute force)."""
from fractions import Fraction as F
from _h import dec, geos, bdist_restr, Bconn
from collections import deque
import random, itertools

def maxcut_local(n, adj, restarts=40, seed=0):
    """Greedy + local search max cut (not exact, but a valid cut to test against)."""
    rnd=random.Random(seed)
    edges=[(u,v) for u in range(n) for v in adj[u] if v>u]
    best=None; bestc=-1
    for _ in range(restarts):
        side=[rnd.randint(0,1) for _ in range(n)]
        improved=True
        while improved:
            improved=False
            for u in range(n):
                same=sum(1 for v in adj[u] if side[v]==side[u])
                diff=sum(1 for v in adj[u] if side[v]!=side[u])
                if same>diff:
                    side[u]^=1; improved=True
        c=sum(1 for u,v in edges if side[u]!=side[v])
        if c>bestc: bestc=c; best=side[:]
    return best,bestc

def loads_fixedcut(n,E,side):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    if not Bconn(n,adj,side): return None
    M=[(min(u,v),max(u,v)) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
    if not M: return None
    ell={}; P=[]
    for f in M:
        a,b=f
        d=bdist_restr(adj,side,a,b)
        if d<0: return None
        ell[f]=d+1
        Ps=geos(adj,side,a,b); nf=len(Ps)
        if nf==0: return None
        cnt={}
        for p in Ps:
            for v in p: cnt[v]=cnt.get(v,0)+1
        P.append({v:F(cnt[v],nf) for v in cnt})
    S=[sum(P[fi].get(v,F(0)) for fi in range(len(M))) for v in range(n)]
    # layer-max per bad edge
    worst=None
    for fi,f in enumerate(M):
        a,b=f
        dd={a:0}; q=deque([a])
        while q:
            u=q.popleft()
            for w in adj[u]:
                if side[u]!=side[w] and w not in dd: dd[w]=dd[u]+1; q.append(w)
        L=ell[f]; pf=P[fi]
        layers={}
        for v in pf: layers.setdefault(dd[v],[]).append(v)
        maxsum=F(0); rowsum=sum(pf[v]*S[v] for v in pf)
        for i in range(L):
            vs=layers.get(i,[])
            maxsum+=max((S[v] for v in vs),default=F(0))
        if worst is None or maxsum>worst[0]:
            worst=(maxsum,rowsum,L,f)
    return worst,n

def rand_trianglefree(n,p,seed):
    rnd=random.Random(seed)
    E=[]; adj=[set() for _ in range(n)]
    pairs=[(i,j) for i in range(n) for j in range(i+1,n)]
    rnd.shuffle(pairs)
    for i,j in pairs:
        if rnd.random()<p:
            # triangle-free: no common neighbor
            if adj[i] & adj[j]: continue
            E.append((i,j)); adj[i].add(j); adj[j].add(i)
    return n,E

def myciel(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    NN=2*n+1; EE=list(E)
    for i in range(n):
        for j in adj[i]:
            if j>i:
                EE.append((i, n+j)); EE.append((j, n+i))
    for i in range(n):
        EE.append((n+i, 2*n))
    EE=list(set((min(a,b),max(a,b)) for a,b in EE))
    return NN,EE

if __name__=="__main__":
    print('=== random triangle-free, layer-max vs N (using local-search max cut) ===')
    worst_ratio=None
    for n in range(7,17):
        for seed in range(30):
            p=random.Random(seed*7+n).uniform(0.2,0.5)
            nn,E=rand_trianglefree(n,p,seed)
            adj=[set() for _ in range(nn)]
            for a,b in E: adj[a].add(b); adj[b].add(a)
            side,c=maxcut_local(nn,adj,restarts=25,seed=seed)
            r=loads_fixedcut(nn,E,side)
            if r is None: continue
            worst,N=r
            ratio=F(worst[0],N)
            if worst_ratio is None or ratio>worst_ratio[0]:
                worst_ratio=(ratio,n,worst,N)
            if worst[0]>N:
                print('  OVERSHOOT n=%d seed=%d: layermax=%s > N=%d rowsum=%s ell=%d'%(n,seed,str(worst[0]),N,str(worst[1]),worst[2]))
    print('worst layermax/N over random:',float(worst_ratio[0]),'at n=%d ell=%d'%(worst_ratio[1],worst_ratio[2][2]))

    print('=== Mycielskians (local-search cut; may not be gamma-min) ===')
    C5=(5,[(0,1),(1,2),(2,3),(3,4),(4,0)])
    g=C5
    for depth in range(1,4):
        g=myciel(*g)
        nn,E=g
        adj=[set() for _ in range(nn)]
        for a,b in E: adj[a].add(b); adj[b].add(a)
        side,c=maxcut_local(nn,adj,restarts=60,seed=depth)
        r=loads_fixedcut(nn,E,side)
        if r is None: print('  Myc depth %d N=%d: no valid loads (cut not connected-B / no bad?)'%(depth,nn)); continue
        worst,N=r
        print('  Myc depth %d N=%d: layermax=%s (%.4f N) rowsum=%s ell=%d %s'%(
            depth,nn,str(worst[0]),float(worst[0])/N,str(worst[1]),worst[2],'<=N' if worst[0]<=N else 'OVERSHOOT>N'))
