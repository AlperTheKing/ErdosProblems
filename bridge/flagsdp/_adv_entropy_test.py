"""Adversarial verification of the counting-entropy sub-lemma.
 a_{e,v} = (#shortest B-geodesics of e through v)/g_e ; sum_v a_{e,v}=h_e.
 L(v)=sum_e h_e a_{e,v}.  Claim: sum_v L(v)^2 <= N*Gamma.
 Per-edge: W_e = sum_v a_{e,v} L(v) <= N*h_e."""
from mycielskian_check import mycielskian, edges_of, gamma_min_cut, all_shortest_geos

def analyze(name,N,adj,side,G,M,verbose=True):
    he=[]; a=[]
    for (u,v) in M:
        geos=all_shortest_geos(N,adj,side,u,v)
        g=len(geos); h=len(geos[0]); he.append(h)
        cnt={}
        for P in geos:
            for w in P: cnt[w]=cnt.get(w,0)+1
        a.append({w:c/g for w,c in cnt.items()})
    L=[0.0]*N
    for ei in range(len(M)):
        for w,frac in a[ei].items():
            L[w]+=he[ei]*frac
    sumL=sum(L); sumL2=sum(x*x for x in L)
    rhs=N*G
    ratio=sumL2/rhs if rhs>0 else 0.0
    worstWe=-1.0
    for ei,(u,v) in enumerate(M):
        We=sum(frac*L[w] for w,frac in a[ei].items())
        r=We/(N*he[ei])
        if r>worstWe: worstWe=r
    ok=sumL2<=rhs+1e-9
    if verbose:
        tag='OK' if ok else 'VIOLATION'
        print("%s: N=%d beta=%d Gamma=%d | sumL=%.3f(=G?%s) sumL2=%.3f N*G=%d ratio=%.6f %s | maxWe/(Nh)=%.6f"%(
            name,N,len(M),G,sumL,abs(sumL-G)<1e-6,sumL2,rhs,ratio,tag,worstWe))
    return ok, ratio, worstWe

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

def decode_g6(s):
    data=[ord(c)-63 for c in s]; n=data[0]; bits=[]
    for d in data[1:]:
        for k in range(5,-1,-1): bits.append((d>>k)&1)
    adj=[set() for _ in range(n)]; idx=0
    for j in range(1,n):
        for i in range(j):
            if idx<len(bits) and bits[idx]: adj[i].add(j); adj[j].add(i)
            idx+=1
    return n,adj

if __name__=="__main__":
    print("=== WITNESSES ===")
    for q in (2,3,4,5):
        n,adj,side,G,M=C5q(q); analyze("C5[%d]"%q,n,adj,side,G,M)
    n,adj=decode_g6("G?`F`w"); E=edges_of([set(x) for x in adj])
    res,mc=gamma_min_cut(n,[set(x) for x in adj],E)
    side,G,M=res; analyze("n8 band-max",n,[set(x) for x in adj],side,G,M)
    C5e=[(0,1),(1,2),(2,3),(3,4),(4,0)]
    Nm,adjm=mycielskian(5,C5e)
    Em=edges_of(adjm); res,mc=gamma_min_cut(Nm,adjm,Em,cap=20000)
    if res: side,G,M=res; analyze("M(C5)=Grotzsch N=11",Nm,adjm,side,G,M)
    Pet=[(0,1),(1,2),(2,3),(3,4),(4,0),(5,7),(7,9),(9,6),(6,8),(8,5),(0,5),(1,6),(2,7),(3,8),(4,9)]
    Np,adjp=mycielskian(10,Pet)
    Ep=edges_of(adjp); res,mc=gamma_min_cut(Np,adjp,Ep,cap=300000)
    if res: side,G,M=res; analyze("M(Petersen) N=21",Np,adjp,side,G,M)
    else: print("M(Petersen): no min-cut found within cap")
