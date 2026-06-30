"""Confirm (UNIF-LOAD) max_v T_uni(v) <= N + (N^2 - Gamma) on C5[t] (tight) and two-lane (killer),
exact Fraction. T_uni = sum_f ell_f * (#f-geos thru v)/n_f."""
from fractions import Fraction as F
from _satzmu_conn import struct_for_side
from _h import gmin, maxcut_all, blow

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

def check(name,n,E,side):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    M,ell,T,mu,cyc=struct_for_side(n,adj,side)
    # T from struct_for_side IS already T_uni (uniform split over geodesics)
    N=n; Gamma=sum(ell[f]**2 for f in M)
    K=N + (N*N - Gamma)
    maxT=max(T); sumT=sum(T)
    ok = maxT <= K
    print(f"[{name}] N={N} Gamma={Gamma} sum_T={sumT}(=Gamma?{sumT==Gamma}) K=N+(N^2-G)={K} "
          f"maxT_uni={float(maxT):.4f} maxT<=K: {ok} slack={float(K-maxT):.3f}")

print("=== C5[t] (expect tight: maxT=N, K=N) ===")
for t in (1,2,3,4):
    n,E=blow(t)
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    side,G,M,ell=gmin(n,adj,maxcut_all(n,adj))
    check(f"C5[{t}]",n,E,side)
print("=== two-lane killer (SM/SPEC FALSE here; UNIF-LOAD must HOLD) ===")
for L in (8,12,16,20,24):
    n,E,side=two_lane(L); check(f"two-lane L={L}",n,E,side)
