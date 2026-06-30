"""Probe first-moment (linear) handles on two-lane vs C5[t]:
 - edge load mu(e) max, sum
 - Sigma_f ell_f, |B|, identity check Sum mu = Gamma - Sigma ell
 - candidate linear bound: Gamma - Sigma ell = Sum_B mu(e); is max mu(e) bounded? is Sum mu <= |B|*c?
Goal: see if a clean LINEAR inequality (not quadratic, not spectral) separates extremal from killer."""
from fractions import Fraction as F
from _satzmu_conn import struct_for_side
from _h import gmin, maxcut_all, blow

def edgeload(n,adj,side,M,ell,cyc):
    mu={}
    for u in range(n):
        for v in adj[u]:
            if side[u]!=side[v] and u<v: mu[(u,v)]=F(0)
    for f in M:
        Ps=cyc[f]; w=F(ell[f],len(Ps))
        for P in Ps:
            for i in range(len(P)-1):
                a,b=P[i],P[i+1]; e=(min(a,b),max(a,b))
                if e in mu: mu[e]+=w
    return mu

def two_lane(L):
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

def report(name,n,E,side):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    st=struct_for_side(n,adj,side)
    M,ell,T,mu0,cyc=st
    N=n; Gamma=sum(ell[f]**2 for f in M); sumell=sum(ell[f] for f in M)
    mu=edgeload(n,adj,side,M,ell,cyc)
    B=len(mu); summu=sum(mu.values()); maxmu=max(mu.values()) if mu else 0
    print(f"[{name}] N={N} Gamma={Gamma} Sumell={sumell} |B|={B} Summu={summu} (=Gamma-Sumell? {summu==Gamma-sumell}) "
          f"maxmu={float(maxmu):.3f} Summu/|B|={float(F(summu,B)):.3f} m=|M|={len(M)}")

print("=== C5[t] extremal ===")
for t in (1,2,3,4):
    n,E=blow(t)
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    side,G,M,ell=gmin(n,adj,maxcut_all(n,adj))
    report(f"C5[{t}]",n,E,side)
print("=== two-lane killer ===")
for L in (8,12,16,20):
    n,E,side=two_lane(L); report(f"two-lane L={L}",n,E,side)
