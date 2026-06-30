"""Check rho(K) vs A=N+N^2/25-m on two-lane and blowups.  K=sum_f p_f p_f^T.
SUM-SBC <= [rho(K)<=A].  If rho(K)<=A holds everywhere, the ONLY rigorous superset of SUM-SBC
(spectral) is itself provable-shaped; if rho(K)>A somewhere, even the spectral relaxation of SUM-SBC fails
and SUM-SBC must use vector-specific (cone) slack. Decisive for whether a quadratic certificate can exist."""
from fractions import Fraction as F
import numpy as np
from _satzmu_conn import struct_for_side
from _h import Bconn, maxcut_all, bdist_restr

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

def Kmat(n,adj,side):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st
    if not M: return None
    K=[[F(0)]*n for _ in range(n)]
    for f in M:
        Ps=cyc[f]; k=len(Ps); pf={}
        for P in Ps:
            for v in P: pf[v]=pf.get(v,F(0))+F(1,k)
        it=list(pf.items())
        for a in range(len(it)):
            va,pa=it[a]
            for b in range(len(it)):
                vb,pb=it[b]; K[va][vb]+=pa*pb
    return K,M,ell,T

def analyze(name,n,adj,side):
    if not Bconn(n,adj,side): return
    r=Kmat(n,adj,side)
    if r is None: return
    K,M,ell,T=r; N=n; m=len(M); A=N+N*N/25.0-m
    Kf=np.array([[float(x) for x in row] for row in K])
    rho=max(np.linalg.eigvalsh(Kf))
    sumT2=sum(float(T[v])**2 for v in range(n)); Gamma=sum(float(T[v]) for v in range(n))
    print(f"  {name}: N={n} m={m} rho(K)={rho:.4f} A={A:.3f} rho<=A:{rho<=A+1e-9} | sumT2/Gamma={sumT2/Gamma:.4f} (Rayleigh@1) <=A:{sumT2/Gamma<=A+1e-9}")

def build_two_lane(L):
    a=lambda i:(L+1)+i; b=lambda i:(L+1)+(L+1)+i
    n=3*(L+1); E=set()
    for i in range(L): E.add((i,i+1))
    for i in range(L+1):
        E.add((min(i,a(i)),max(i,a(i)))); E.add((min(i,b(i)),max(i,b(i))))
    for i in range(L):
        for u in (a(i),b(i)):
            for v in (a(i+1),b(i+1)): E.add((min(u,v),max(u,v)))
    for e in [(0,L-2),(0,L),(2,L-2),(2,L)]: E.add((min(e),max(e)))
    side=[0]*n
    for i in range(L+1): side[i]=i%2
    for i in range(L+1): side[a(i)]=1-(i%2); side[b(i)]=1-(i%2)
    return n,sorted(E),side
def blowup(parts):
    mm=len(parts); off=[0]*(mm+1)
    for i in range(mm): off[i+1]=off[i]+parts[i]
    nn=off[mm]; EE=[]
    for i in range(mm):
        j=(i+1)%mm
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,sorted(set(EE))

if __name__=="__main__":
    for L in (8,12,16,20):
        n,E,side=build_two_lane(L)
        adj=[set() for _ in range(n)]
        for a,b in E: adj[a].add(b); adj[b].add(a)
        analyze("twolane%d"%L,n,adj,side)
    for t in range(1,5):
        n,E=blowup([t]*5); adj,cuts=gmins(n,E)
        for s in cuts[:1]: analyze("C5[%d]"%t,n,adj,s)
    for sizes in [[3,9,1,9,3],[1,9,3,9,1],[2,1,2,1,2]]:
        n,E=blowup(sizes); adj,cuts=gmins(n,E)
        for s in cuts[:1]: analyze("fan%s"%sizes,n,adj,s)
