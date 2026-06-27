"""Probe the CLAIMED CRUX of the entropy strategy:
 sum_v L^2 = sum_{e,f} h_e h_f I(e,f), I(e,f)=<a_e,a_f> (expected geo overlap).
 Surrogate S1 = sum_{e,f} h_e h_f min(h_e,h_f) (overlap bounded by per-edge max) -> claim S1/N^3 in {2,3,4} on C5[q].
 Verify: (1) S1 overshoots, (2) the diagonal alone sum_e h_e^2 * I(e,e) and whether I(e,e)<h_e (geos NOT all through same verts),
 (3) is there ANY local/Cauchy-Schwarz bound on I that gives <=N? Test diagonal-only surrogate sum_e h_e^2*<a_e,a_e>."""
from mycielskian_check import mycielskian, edges_of, gamma_min_cut, all_shortest_geos

def build(N,adj,side,M):
    he=[]; a=[]
    for (u,v) in M:
        geos=all_shortest_geos(N,adj,side,u,v)
        g=len(geos); h=len(geos[0]); he.append(h)
        cnt={}
        for P in geos:
            for w in P: cnt[w]=cnt.get(w,0)+1
        a.append({w:c/g for w,c in cnt.items()})
    return he,a

def overlap(ae,af):
    s=0.0
    for w,x in ae.items():
        if w in af: s+=x*af[w]
    return s

def analyze(name,N,adj,side,G,M):
    he,a=build(N,adj,side,M)
    beta=len(M)
    # true quadratic form
    Q=0.0; diag=0.0; offdiag=0.0
    S1=0.0
    selfI=[]
    for e in range(beta):
        Iee=overlap(a[e],a[e]); selfI.append(Iee)
        for f in range(beta):
            I=overlap(a[e],a[f]); term=he[e]*he[f]*I
            Q+=term
            if e==f: diag+=term
            else: offdiag+=term
            S1+=he[e]*he[f]*min(he[e],he[f])
    rhs=N*G
    # diagonal-only surrogate: replace I(e,f) by min(h_e,h_f) only off-diag? report ratio of pieces
    print("%s: N=%d beta=%d G=%d | Q=sumL2=%.3f rhs=N*G=%d ratio=%.4f"%(name,N,beta,G,Q,rhs,Q/rhs))
    print("    diag(sum h_e^2 I_ee)=%.3f  offdiag=%.3f  | S1(min-surrogate)=%.1f  S1/rhs=%.3f  S1/N^3=%.3f"%(
        diag,offdiag,S1,S1/rhs,S1/(N**3)))
    avgIee=sum(selfI)/beta
    print("    avg I_ee=%.4f (=h_e iff all geos identical-vertex-set; h_e=%d) -> geos %s"%(
        avgIee, he[0], "SPREAD" if avgIee<he[0]-1e-6 else "concentrated"))

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

if __name__=="__main__":
    for q in (2,3,4):
        n,adj,side,G,M=C5q(q); analyze("C5[%d]"%q,n,adj,side,G,M)
    Pet=[(0,1),(1,2),(2,3),(3,4),(4,0),(5,7),(7,9),(9,6),(6,8),(8,5),(0,5),(1,6),(2,7),(3,8),(4,9)]
    Np,adjp=mycielskian(10,Pet)
    Ep=edges_of(adjp); res,mc=gamma_min_cut(Np,adjp,Ep,cap=300000)
    if res: side,G,M=res; analyze("M(Petersen) N=21",Np,adjp,side,G,M)
