#!/usr/bin/env python3
"""Theta-graphs and odd-cycle chains sharing PATHS (not just single vertex/edge), plus their
blow-ups, to create bad edges with longer B-geodesics (push Gamma up toward N^2).
Also: C5[q] with an extra C5 chained on (necklace of a blow-up + a bare cycle).
"""
import sys
sys.path.insert(0,'/e/Projects/ErdosProblems/bridge/flagsdp')
from peel_check import check_instance

def report(name, n, adj):
    if n>26:
        print(f"{name}: SKIP N={n}>26"); return None,False
    r=check_instance(n,adj)
    if not r.get("ok"):
        print(f"{name}: N={n} INVALID tf={r.get('triangle_free')} | {r.get('detail')}"); return r,False
    g=r.get("gamma"); n2=r.get("n2"); ratio=(g/n2) if (g and n2) else None
    obstr=r.get("ge_n2") and r.get("m",0)>=2 and r.get("has_safe_peel") is False
    flag="  <<< OBSTRUCTION" if obstr else ""
    nt=f"  [NEAR {ratio:.4f}]" if (ratio and ratio>=0.90 and r.get('m',0)>=2 and r.get('has_safe_peel') is False) else ""
    print(f"{name}: N={n} m={r.get('m')} g={g} n2={n2} ratio={f'{ratio:.4f}' if ratio else None} "
          f"tight={r.get('tight')} sp={r.get('has_safe_peel')} Bconn={r.get('B_connected')} | {r.get('detail')}{flag}{nt}")
    return r,obstr

def from_edges(edges):
    vs=sorted({x for e in edges for x in e}); idx={v:i for i,v in enumerate(vs)}
    n=len(vs); adj=[set() for _ in range(n)]
    for u,v in edges:
        a,b=idx[u],idx[v]
        if a!=b: adj[a].add(b); adj[b].add(a)
    return n,adj

def blowup(n0,adj0,mult):
    parts=[]; s=0
    for v in range(n0): parts.append(list(range(s,s+mult[v]))); s+=mult[v]
    N=s; adj=[set() for _ in range(N)]
    for u in range(n0):
        for v in adj0[u]:
            if v>u:
                for a in parts[u]:
                    for b in parts[v]: adj[a].add(b); adj[b].add(a)
    return N,adj

# theta graph: two vertices joined by 3 internally-disjoint paths of lengths a,b,c (edges).
# triangle-free if no path length 1 paired with length 2 sharing... keep all paths length>=2.
# parity: for the bad-edge structure we want odd cycles. cycle from path i & j has length len_i+len_j.
def theta(a,b,c):
    # endpoints s=0, t=1; path lengths a,b,c (#edges)
    edges=[]; nxt=2
    s,t=0,1
    for L in (a,b,c):
        prev=s
        inter=[]
        for _ in range(L-1):
            inter.append(nxt); nxt+=1
        chain=[s]+inter+[t]
        for i in range(len(chain)-1): edges.append((chain[i],chain[i+1]))
    return from_edges(edges)

if __name__=="__main__":
    print("=== theta graphs (two odd cycles sharing a path) ===")
    # pick (a,b,c) so pairwise sums are odd cycles >=5: need lengths of opposite parity
    for (a,b,c) in [(2,3,3),(2,3,5),(3,4,4),(2,5,5),(3,3,4),(2,3,7),(4,5,5),(3,4,6),(2,5,7),(3,5,6)]:
        n,adj=theta(a,b,c); report(f"theta({a},{b},{c})", n, adj)

    print("=== theta BLOW-UPS (small) ===")
    for (a,b,c) in [(2,3,3),(2,3,5),(3,4,4)]:
        n0,a0=theta(a,b,c)
        report(f"theta({a},{b},{c})[2]", *blowup(n0,a0,[2]*n0))

    print("=== C5[q] with one extra bare C5 chained (necklace: dense blob + sparse cycle) ===")
    # C5[2] on parts 0..9 then attach a C5 via a vertex
    def C5q(q):
        n=5*q; parts=[list(range(i*q,(i+1)*q)) for i in range(5)]
        adj=[set() for _ in range(n)]
        for i in range(5):
            for a in parts[i]:
                for b in parts[(i+1)%5]: adj[a].add(b); adj[b].add(a)
        return n,adj,parts
    for q in (2,3):
        n,adj,parts=C5q(q)
        # attach a fresh C5 sharing vertex 0
        base=n; extra=[0,base,base+1,base+2,base+3]  # 0 is shared
        adj=[set(s) for s in adj]+[set() for _ in range(4)]
        cyc=extra
        for i in range(5):
            u=cyc[i]; v=cyc[(i+1)%5]; adj[u].add(v); adj[v].add(u)
        report(f"C5[{q}]+bareC5", len(adj), adj)
