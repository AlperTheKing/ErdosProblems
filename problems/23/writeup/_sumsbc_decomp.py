"""Decompose SUM-SBC <=> S := sum_v T(T-N) <= (N^2/25 - m)*Gamma.
Look at the structure: split vertices into O (T>N), under (T<N), exact (T=N).
At C5[t]: all T=N (uniform), so S=0 and RHS=0 (m=N^2/25). Tight.
Print S, RHS, sum_{T>N} T(T-N), sum_{T<N} T(N-T), Gamma, etc. EXACT."""
from fractions import Fraction as F
from _satzmu_conn import struct_for_side
from _h import Bconn, maxcut_all, bdist_restr

def build_two_lane(L):
    nx=L+1
    a=lambda i:(L+1)+i; b=lambda i:(L+1)+(L+1)+i
    n=3*(L+1); E=set()
    for i in range(L): E.add((i,i+1))
    for i in range(L+1):
        E.add((min(i,a(i)),max(i,a(i)))); E.add((min(i,b(i)),max(i,b(i))))
    for i in range(L):
        for u in (a(i),b(i)):
            for v in (a(i+1),b(i+1)): E.add((min(u,v),max(u,v)))
    bad=[(0,L-2),(0,L),(2,L-2),(2,L)]
    for e in bad: E.add((min(e),max(e)))
    side=[0]*n
    for i in range(L+1): side[i]=i%2
    for i in range(L+1): side[a(i)]=1-(i%2); side[b(i)]=1-(i%2)
    return n,sorted(E),side,bad

def gmins(n,E):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    cuts=[s for s in maxcut_all(n,adj) if Bconn(n,adj,s)]
    cand=[]
    for s in cuts:
        Mb=[(u,v) for u in range(n) for v in adj[u] if v>u and s[u]==s[v]]
        if not Mb: continue
        G=0; ok=True
        for (u,v) in Mb:
            d=bdist_restr(adj,s,u,v)
            if d<0: ok=False; break
            G+=(d+1)**2
        if ok: cand.append((s,G))
    if not cand: return adj,[]
    gm=min(g for _,g in cand)
    return adj,[s for s,g in cand if g==gm]

def analyze(name,n,adj,side):
    if not Bconn(n,adj,side): return None
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st
    if not M: return None
    N=n; m=len(M); Gamma=sum(ell[f]**2 for f in M)
    S=sum(T[v]*(T[v]-N) for v in range(n))
    RHS=(F(N*N,25)-m)*Gamma
    over=sum(T[v]*(T[v]-N) for v in range(n) if T[v]>N)
    under=sum(T[v]*(N-T[v]) for v in range(n) if T[v]<N)
    print(f"  {name}: N={N} m={m} Gamma={Gamma} | S={str(S)}={float(S):.1f} RHS={float(RHS):.1f} OK:{S<=RHS} | over={float(over):.1f} under={float(under):.1f} S=over-under:{S==over-under}")
    return S<=RHS

if __name__=="__main__":
    print("--- two-lane ---")
    for L in (8,12,16,20):
        n,E,side,bad=build_two_lane(L)
        adj=[set() for _ in range(n)]
        for a,b in E: adj[a].add(b); adj[b].add(a)
        analyze("twolane%d"%L,n,adj,side)
    print("--- C5[t] extremal (must be S=0=RHS) ---")
    def blowup(parts):
        mm=len(parts); off=[0]*(mm+1)
        for i in range(mm): off[i+1]=off[i]+parts[i]
        nn=off[mm]; EE=[]
        for i in range(mm):
            j=(i+1)%mm
            for a in range(off[i],off[i+1]):
                for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
        return nn,sorted(set(EE))
    for t in range(1,5):
        n,E=blowup([t]*5); adj,cuts=gmins(n,E)
        for s in cuts[:1]: analyze("C5[%d]"%t,n,adj,s)
    print("--- nonuniform fans ---")
    for sizes in [[3,9,1,9,3],[2,10,1,10,2],[1,9,3,9,1]]:
        n,E=blowup(sizes); adj,cuts=gmins(n,E)
        for s in cuts[:1]: analyze("fan%s"%sizes,n,adj,s)
