#!/usr/bin/env python3
"""GPT §9 EXCHANGE incidence traces (the data GPT said it needs to attempt the exchange-master proof of OVD).
For the GLOBAL min-overshoot shortest cycle C (ov(C)=min over all bad-edge shortest geodesics of L-bound),
list F(C)={incident bad edges != peeled} with ell(f) and ov(C_f) (min-overshoot cycle of f), and probe the
§9 inequalities:
  minimality:        ov(C_f) >= ov(C)  for all f in F(C)   (auto, C is global min)
  exchange-sum:      sum_f ell(f)(ov(C)-ov(C_f)) <= N^2-Gamma   (GPT: trivially <=0, too weak)
  exchange-master:   exists lambda_f>=0 with ov(C) + sum_f lambda_f(ov(C_f)-ov(C)) <= N^2-Gamma  (<=> OVD at lam=0)
Report the raw traces so the algebraic cancellation can be attempted by hand."""
import sys
from mycielskian_check import mycielskian, edges_of, gamma_min_cut, all_shortest_geos, bdistB

def ov_of(N,adj,side,M,C,ellG):
    Cset=set(C); h=len(C); mu=0; Delta=0; conn=True
    for f in M:
        key=(min(f),max(f))
        if f[0] in Cset or f[1] in Cset: mu+=ellG[key]**2
        else:
            nd=bdistB(N,adj,side,f[0],banned=Cset).get(f[1],-1)
            if nd<0: conn=False; break
            Delta+=(nd+1)**2-ellG[key]**2
    if not conn: return None
    L=mu-Delta; return L-(2*h*N-h*h)

def trace(name,N,adj):
    adj=[set(a) for a in adj]; E=edges_of(adj)
    res,mc=gamma_min_cut(N,adj,E)
    if res is None: print(f"{name}: no connected-B max cut"); return
    side,G,M=res
    ellG={(min(x,y),max(x,y)): bdistB(N,adj,side,x,set())[y]+1 for (x,y) in M}
    # min-overshoot over ALL shortest cycles; also per-bad-edge min ov
    best=None; peredge={}
    for (u,v) in M:
        be=None
        for C in all_shortest_geos(N,adj,side,u,v):
            ov=ov_of(N,adj,side,M,C,ellG)
            if ov is None: continue
            if be is None or ov<be[0]: be=(ov,C)
            if best is None or ov<best[0]: best=(ov,C,(u,v))
        if be is not None: peredge[(u,v)]=be
    if best is None: print(f"{name}: no connected peel"); return
    ovC,C,peeled=best; Cset=set(C); h=len(C); deficit=N*N-G
    F=[f for f in M if (f[0] in Cset or f[1] in Cset) and (min(f),max(f))!=peeled]
    print(f"\n=== {name}: N={N} beta={len(M)} Gamma={G} N^2-Gamma={deficit} | min-overshoot C={C} (peeled {peeled}) ov(C)={ovC} ===")
    print(f"    OVD: ov(C)={ovC} <= N^2-Gamma={deficit}? {ovC<=deficit}")
    print(f"    F(C) incident edges ({len(F)}): " + ", ".join(f"f={f} ell={ellG[(min(f),max(f))]} ov(C_f)={peredge[f][0] if f in peredge else 'NA'} (delta={peredge[f][0]-ovC if f in peredge else 'NA'})" for f in F[:12]))
    # exchange-sum
    xs=sum(ellG[(min(f),max(f))]*(ovC-peredge[f][0]) for f in F if f in peredge)
    print(f"    exchange-sum sum_f ell(f)(ov(C)-ov(C_f)) = {xs}  <= N^2-Gamma={deficit}? {xs<=deficit}  (GPT: trivially <=0)")
    # the informative gap: how the deficit relates to the spread of ov(C_f)
    if F:
        ovfs=[peredge[f][0] for f in F if f in peredge]
        print(f"    ov(C_f) over F(C): min={min(ovfs)} max={max(ovfs)} ; ov(C)={ovC} ; (ov-spread vs deficit {deficit})")

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
        n,adj=C5q(2); trace("C5[2]",n,adj)
        n,adj=decode_g6("G?`F`w"); trace("n8 band-max",n,adj)
    if w in ("grot","all"):
        C5e=[(i,(i+1)%5) for i in range(5)]; gN,gadj=mycielskian(5,C5e)
        N,adj=mycielskian(11,edges_of(gadj)); trace("M(Grotzsch)",N,adj)
    print("\nDONE")
