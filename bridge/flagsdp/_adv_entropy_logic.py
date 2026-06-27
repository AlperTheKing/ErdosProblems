"""Logic audit: relate the entropy sub-lemma to the GPI / vertex-load theorem.
L(v) = T_x(v) for the UNIFORM (max-entropy) routing x_{e,P}=1/g_e.
The vertex-load theorem says EXISTS x with max_v T_x(v) <= N+(N^2-Gamma)=K.
The entropy sub-lemma uses the FIXED uniform routing and only controls the L2 norm.
Question A: does uniform routing satisfy max_v L(v) <= K?  (If yes, GPI proven directly by uniform x -- too good.)
Question B: is sum_v L^2 <= N*Gamma equivalent to 'uniform routing has L2-load <= N*Gamma'?
Report max_v L(v) vs K=N+N^2-Gamma, and vs N, on witnesses + census worst."""
from mycielskian_check import mycielskian, edges_of, gamma_min_cut, all_shortest_geos, gamma_of, maxcut_value, Bconnected
from flag_engine import enumerate_graphs

def loads(N,adj,side,M):
    he=[]; a=[]
    for (u,v) in M:
        geos=all_shortest_geos(N,adj,side,u,v)
        if not geos: return None
        g=len(geos); h=len(geos[0]); he.append(h)
        cnt={}
        for P in geos:
            for w in P: cnt[w]=cnt.get(w,0)+1
        a.append({w:c/g for w,c in cnt.items()})
    L=[0.0]*N
    for ei in range(len(M)):
        for w,frac in a[ei].items(): L[w]+=he[ei]*frac
    return L

def C5q(q):
    n=5*q; vid=lambda i,j:i*q+j; side=[0]*n; adj=[set() for _ in range(n)]
    for i in range(5):
        for j in range(q): side[vid(i,j)]=(0 if i in (0,2,4) else 1)
    for i in range(5):
        for x in range(q):
            for y in range(q):
                u=vid(i,x); v=vid((i+1)%5,y); adj[u].add(v); adj[v].add(u)
    M=[(vid(4,x),vid(0,y)) for x in range(q) for y in range(q)]; G=25*len(M)
    return n,adj,side,G,M

print("WITNESSES: maxL_uniform vs N vs K=N+N^2-Gamma")
for q in (2,3,4,5):
    n,adj,side,G,M=C5q(q); L=loads(n,adj,side,M)
    K=n+(n*n-G)
    print("C5[%d]: N=%d maxL=%.3f minL=%.3f  N=%d  K=%d  maxL<=N? %s  maxL<=K? %s"%(
        q,n,max(L),min(L),n,K,max(L)<=n+1e-6,max(L)<=K+1e-6))

# census: does uniform routing ever exceed K (l_inf), even though l2 always ok?
worst_inf=0.0; n_exceed_N=0; n_exceed_K=0; tot=0
for N in range(5,11):
    for (n,A) in enumerate_graphs(N,triangle_free=True):
        adj=[set() for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if (A[i]>>j)&1: adj[i].add(j)
        E=edges_of(adj)
        if not E: continue
        res,mc=gamma_min_cut(n,adj,E)
        if res is None: continue
        side,G,M=res
        if not M: continue
        L=loads(n,adj,side,M)
        if L is None: continue
        K=n+(n*n-G); mx=max(L); tot+=1
        if mx>worst_inf*1: worst_inf=max(worst_inf,mx/N)
        if mx>N+1e-7: n_exceed_N+=1
        if mx>K+1e-7: n_exceed_K+=1
print("\nCENSUS N<=10 (gamma-min cut): instances=%d"%tot)
print("  uniform routing maxL>N (l_inf fails the tight N)? count=%d  worst maxL/N=%.4f"%(n_exceed_N,worst_inf))
print("  uniform routing maxL>K (l_inf exceeds K)? count=%d"%n_exceed_K)
