#!/usr/bin/env python3
"""AUDIT GPT's marginal-loss reduction of condition (iii). For the MIN-OVERSHOOT shortest-geodesic peel C:
 (A')  A(C)=sum_{f in F(C)} ell(f)               <= 2(N-h)      [anchored length]
 (LEP) H(C)=sum_{f in F(C)} (ell(f)^2 - h ell(f))_+ <= Delta(C) [long-edge payment]
=>  (iii)  L(C)=mu(C)-Delta(C) <= 2hN-h^2.   F(C)=incident bad edges != peeled; h=|C|;
mu(C)=sum_{f cap C != empty} ell_G(f)^2; Delta(C)=sum_{f cap C = empty}(ell_{G-C}(f)^2 - ell_G(f)^2)>=0.
Both tight on C5[q]. Check on C5[q], n8, M(Petersen), M(Grotzsch)."""
import sys
from mycielskian_check import mycielskian, edges_of, gamma_min_cut, all_shortest_geos, bdistB

def ell_G(N,adj,side,x,y,banned=None):
    d=bdistB(N,adj,side,x,banned=banned).get(y,-1)
    return None if d<0 else d+1

def analyze(name,N,adj):
    adj=[set(a) for a in adj]; E=edges_of(adj)
    res,mc=gamma_min_cut(N,adj,E)
    if res is None: print(f"{name}: no connected-B max cut"); return
    side,G,M=res
    Mset=set((min(a,b),max(a,b)) for (a,b) in M)
    ellG={}
    for (x,y) in M: ellG[(min(x,y),max(x,y))]=ell_G(N,adj,side,x,y)
    # enumerate peels (one per bad edge per shortest geodesic), keep connected ones, pick min overshoot
    best=None  # (ov, C, peeled_edge, L, mu, Delta, h)
    for (u,v) in M:
        peeled=(min(u,v),max(u,v))
        for C in all_shortest_geos(N,adj,side,u,v):
            Cset=set(C); h=len(C)
            # survivors disjoint from C: Gamma' + Delta
            Delta=0; mu=0; conn=True
            for f in M:
                key=(min(f),max(f))
                if f[0] in Cset or f[1] in Cset:
                    mu+=ellG[key]**2
                else:
                    new=ell_G(N,adj,side,f[0],f[1],banned=Cset)
                    if new is None: conn=False; break
                    Delta+=new**2-ellG[key]**2
            if not conn: continue
            L=mu-Delta; bound=2*h*N-h*h; ov=L-bound
            if best is None or ov<best[0]: best=(ov,C,peeled,L,mu,Delta,h)
    if best is None: print(f"{name}: no connected peel"); return
    ov,C,peeled,L,mu,Delta,h=best
    Cset=set(C)
    # F(C) = incident bad edges != peeled
    F=[f for f in M if (f[0] in Cset or f[1] in Cset) and (min(f),max(f))!=peeled]
    A=sum(ellG[(min(f),max(f))] for f in F)
    H=sum(max(0, ellG[(min(f),max(f))]**2 - h*ellG[(min(f),max(f))]) for f in F)
    bound=2*h*N-h*h
    print(f"\n=== {name}: N={N} beta={len(M)} Gamma={G} N^2={N*N} | MIN-OVERSHOOT peel C={C} h={h} peeled={peeled} ===")
    print(f"    mu(C)={mu} Delta(C)={Delta} L=mu-Delta={L}  bound=2hN-h^2={bound}  ov={ov}  (iii) L<=bound? {L<=bound}")
    print(f"    F(C)={len(F)} incident bad edges (ell's: {sorted(ellG[(min(f),max(f))] for f in F)})")
    print(f"    (A')  A(C)={A} <= 2(N-h)={2*(N-h)} ? {A<=2*(N-h)}")
    print(f"    (LEP) H(C)={H} <= Delta(C)={Delta} ? {H<=Delta}")
    print(f"    decomposition mu<=h^2+h*A+H = {h*h}+{h*A}+{H}={h*h+h*A+H} >= mu={mu}? {h*h+h*A+H>=mu} ; and gives L<=bound? {h*h+h*A+H-Delta<=bound}")

if __name__=="__main__":
    def C5q(q):
        n=5*q; vid=lambda i,j:i*q+j; adj=[set() for _ in range(n)]
        for i in range(5):
            for a in range(q):
                for b in range(q):
                    u=vid(i,a); v=vid((i+1)%5,b); adj[u].add(v); adj[v].add(u)
        return n,adj
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
    w=sys.argv[1] if len(sys.argv)>1 else "small"
    if w in ("small","all"):
        for q in (2,3): n,adj=C5q(q); analyze(f"C5[{q}]",n,adj)
        n,adj=decode_g6("G?`F`w"); analyze("n8 band-max",n,adj)
    if w in ("pet","all"):
        pet=[set() for _ in range(10)]
        for i in range(5):
            for (a,b) in [(i,(i+1)%5),(5+i,5+(i+2)%5),(i,5+i)]: pet[a].add(b); pet[b].add(a)
        N,adj=mycielskian(10,edges_of(pet)); analyze("M(Petersen)",N,adj)
    if w in ("grot","all"):
        C5e=[(i,(i+1)%5) for i in range(5)]; gN,gadj=mycielskian(5,C5e)
        N,adj=mycielskian(11,edges_of(gadj)); analyze("M(Grotzsch)",N,adj)
    print("\nDONE")
