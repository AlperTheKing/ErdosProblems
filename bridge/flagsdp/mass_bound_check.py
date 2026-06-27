#!/usr/bin/env python3
"""Answer Step-1's [15:02:00Z] question: is the mass bound L <= 2|C|N-|C|^2 (cond (iii)) TIGHT or strictly
SLACK at the beta=e/5 non-extremal graphs Petersen and the n8 band-maximizer (g6=G?`F`w)?
If strictly slack there, my peel route already pins d_edge=2/5 and is AHEAD of the graphon (Q) inequality.
Report, per bad edge's shortest geodesic C: L=Gamma-Gamma', mass(M_C)=sum_{bad edges incident to C}(d_B+1)^2,
and the bound 2|C|N-|C|^2; flag equality vs slack."""
from collections import deque
from peel_check import maxcut_all, bdistB, Bconnected, gamma_of, shortest_path_B, check_instance

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

def petersen():
    # outer 5-cycle 0..4, inner pentagram 5..9, spokes i~i+5
    adj=[set() for _ in range(10)]
    def e(a,b): adj[a].add(b); adj[b].add(a)
    for i in range(5):
        e(i,(i+1)%5); e(5+i,5+(i+2)%5); e(i,5+i)
    return 10,adj

def all_shortest_geos(n,adj,side,s,t):
    dist={s:0}; pred={s:[]}; layer=[s]
    while layer:
        nxt=[]
        for u in layer:
            for v in adj[u]:
                if side[u]!=side[v]:
                    if v not in dist: dist[v]=dist[u]+1; pred[v]=[u]; nxt.append(v)
                    elif dist[v]==dist[u]+1: pred[v].append(u)
        layer=nxt
    if t not in dist: return []
    out=[]
    def rec(v,acc):
        if v==s: out.append([s]+acc[::-1]); return
        for p in pred[v]: rec(p,acc+[v])
    rec(t,[]); return out

def analyze(name, n, adj):
    adj=[set(a) for a in adj]
    r=check_instance(n,adj)
    if not r.get("ok"):
        print(f"{name}: NOT ok ({r.get('detail')})"); return
    side=r["side"]; G=r["gamma"]; NN=n
    M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
    Mset=set((min(a,b),max(a,b)) for (a,b) in M)
    d_edge_num=2*sum(len(adj[u]) for u in range(n))//2  # 2e
    e=sum(len(adj[u]) for u in range(n))//2
    print(f"\n=== {name}: N={n} e={e} beta={r['m']} Gamma={G} N^2={n*n} deficit={n*n-G} d_edge=2e/N^2={2*e/(n*n):.4f} has_safe_peel={r.get('has_safe_peel')} ===")
    print(f"    (beta=e/5? {r['m']}=={e/5}: {abs(r['m']-e/5)<1e-9}; d_edge=2/5? {2*e/(n*n):.4f} vs 0.4)")
    best_L_minus_bound=None
    for (u,v) in M:
        geos=all_shortest_geos(n,adj,side,u,v)
        for C in geos:
            Cset=set(C); s=len(C); keep=set(x for x in range(n) if x not in Cset)
            # Gamma' over surviving bad edges
            Mp=[(a,b) for (a,b) in M if a in keep and b in keep]
            Gp=0; ok=True
            for (a,b) in Mp:
                d=bdistB(n,adj,side,a,banned=Cset).get(b,-1)
                if d<0: ok=False; break
                Gp+=(d+1)**2
            bound=2*s*NN-s*s
            # mass(M_C) = bad edges incident to C
            massC=0
            for (a,b) in M:
                if a in Cset or b in Cset:
                    d=bdistB(n,adj,side,a,set()).get(b,-1); massC+=(d+1)**2 if d>=0 else 0
            if not ok:
                tag="(ii)-DISCONNECT"; L="inf"
                print(f"   bad({u},{v}) C={C} |C|={s}: {tag}; mass(M_C)={massC} vs bound={bound} ({'<=' if massC<=bound else '>'}); peel INVALID")
                continue
            L=G-Gp
            slack=bound-L
            if best_L_minus_bound is None or L-bound>best_L_minus_bound: best_L_minus_bound=L-bound
            print(f"   bad({u},{v}) C={C} |C|={s}: L={L} bound=2|C|N-|C|^2={bound} slack={slack} {'TIGHT(=)' if slack==0 else 'SLACK' if slack>0 else 'VIOLATION'} | mass(M_C)={massC}")
    print(f"    >>> max(L - bound) over all shortest peels = {best_L_minus_bound}  => mass/cond-(iii) bound is {'TIGHT somewhere' if best_L_minus_bound==0 else 'STRICTLY SLACK everywhere (L<bound)' if (best_L_minus_bound is not None and best_L_minus_bound<0) else 'n/a'}")

if __name__=="__main__":
    n,adj=decode_g6("G?`F`w"); analyze("n8 band-maximizer (g6=G?`F`w)", n, adj)
    n,adj=petersen(); analyze("Petersen GP(5,2)", n, adj)
    # C5[2] tight anchor for contrast
    def C5q(q):
        n=5*q; vid=lambda i,j:i*q+j; adj=[set() for _ in range(n)]
        for i in range(5):
            for a in range(q):
                for b in range(q):
                    u=vid(i,a); v=vid((i+1)%5,b); adj[u].add(v); adj[v].add(u)
        return n,adj
    n,adj=C5q(2); analyze("C5[2] (tight anchor)", n, adj)
    print("\nDONE")
