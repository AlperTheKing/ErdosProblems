"""FAST large-N ROWSUM-O stress using block-level cut search (2^L over the L=2k+1 blocks) instead of
full 2^(n-1) maxcut, for odd-cycle blowups C_{2k+1}[t]. Plus Mycielskians (small N). EXACT Fraction.
ROWSUM-O: for each bad edge f, sum_v p_f(v) S(v) <= N, S(v)=sum_g p_g(v)."""
from fractions import Fraction as F
from _h import loads
from _stress_rowsumO import mycielski, rowsumO_exact

def odd_blow_adj(k,t):
    L=2*k+1; n=L*t; adj=[set() for _ in range(n)]
    for i in range(L):
        for a in range(t):
            for b in range(t):
                u=i*t+a; w=((i+1)%L)*t+b
                adj[u].add(w); adj[w].add(u)
    return n,adj,L

def rowsumO_blocklevel(k,t):
    n,adj,L=odd_blow_adj(k,t)
    edges=[(u,w) for u in range(n) for w in adj[u] if w>u]
    best=None
    for mask in range(1<<L):
        side=[0]*n
        for i in range(L):
            c=(mask>>i)&1
            for a in range(t): side[i*t+a]=c
        cut=sum(1 for u,w in edges if side[u]!=side[w])
        if best is None or cut>best[0]: best=(cut,side[:])
    cut,side=best
    M=[(u,w) for u,w in edges if side[u]==side[w]]
    if not M: return None,n
    def geos(s,tt):
        dist={s:0};pred={s:[]};layer=[s]
        while layer:
            nxt=[]
            for u in layer:
                for v in adj[u]:
                    if side[u]!=side[v]:
                        if v not in dist:dist[v]=dist[u]+1;pred[v]=[u];nxt.append(v)
                        elif dist[v]==dist[u]+1:pred[v].append(u)
            layer=nxt
        if tt not in dist:return []
        P=[]
        def rec(v,acc):
            if v==s:P.append([s]+acc[::-1]);return
            for p in pred[v]:rec(p,acc+[v])
        rec(tt,[]);return P
    pf={}
    for f in M:
        Ps=geos(f[0],f[1]); nf=len(Ps)
        if nf==0: return ('disconnected',n)
        cnt={}
        for P in Ps:
            for v in P: cnt[v]=cnt.get(v,0)+1
        pf[f]={v:F(cnt[v],nf) for v in cnt}
    S=[sum(pf[g].get(v,F(0)) for g in M) for v in range(n)]
    worst=F(-10**9)
    for f in M:
        Cf=sum(pf[f][v]*S[v] for v in pf[f])
        if Cf-F(n)>worst: worst=Cf-F(n)
    return worst,n

if __name__=="__main__":
    print("=== ROWSUM-O on odd-cycle blowups C_{2k+1}[t] (block-level cut, EXACT) ===")
    for k in [2,3,4]:
        for t in range(1,9):
            n=(2*k+1)*t
            if n>50: break
            r,nn=rowsumO_blocklevel(k,t)
            tag='VIOLATION' if (isinstance(r,F) and r>0) else 'ok'
            print(f"  C{2*k+1}[{t}] N={nn}: max(ROWSUM-O - N)={r if isinstance(r,F) else r} ({float(r) if isinstance(r,F) else r:+}) {tag}")
    print("\n=== Mycielskians (iterated, raises chromatic number) EXACT ===")
    C5=[(i,(i+1)%5) for i in range(5)]
    NN,EE=mycielski(5,C5)   # Grotzsch N=11
    info=loads(NN,EE)
    print(f"  Grotzsch M(C5) N={NN}: max(ROWSUM-O - N)={rowsumO_exact(info)} ({float(rowsumO_exact(info)):+.4f})")
    NN2,EE2=mycielski(NN,EE) # N=23
    info2=loads(NN2,EE2)
    print(f"  M(M(C5)) N={NN2}: max(ROWSUM-O - N)={rowsumO_exact(info2)} ({float(rowsumO_exact(info2)):+.4f})")
