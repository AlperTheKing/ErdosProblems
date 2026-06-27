#!/usr/bin/env python3
"""Adversarial angle: GENERALIZED THETA graphs and their balanced blow-ups.

Two hubs joined by k>=3 internally-disjoint paths of odd lengths (=> triangle-free, bipartite-friendly).
A theta with two terminals joined by paths is bipartite iff all path lengths have the SAME parity.
If all path lengths are even (number of edges even), hubs land on same side -> the two hubs being
non-adjacent is fine. If all odd, hubs on opposite sides. To get BAD (monochromatic) edges we need a
non-bipartite structure, OR we rely on blow-ups producing monochromatic edges under the max cut.

Strategy: theta_k(L) = two hubs s,t with k internally disjoint paths each of edge-length in list Ls.
For triangle-free we need each path length >=2 (so no chord makes a triangle) and no two length-1 paths.
We MIX odd lengths (3,5,7). The graph is bipartite iff all Ls share parity. To force monochromatic
(bad) edges we make a NON-bipartite theta: lengths of DIFFERENT parity create an odd closed walk.

We then take balanced blow-ups: replace each *internal* vertex of every path by an independent set of
size q with complete bipartite links along consecutive path positions; hubs blown up too (size q).
Vary k in {3,4,5}, length multisets, q in {1,2,3,4}.
"""
import itertools, sys
from peel_check import check_instance, maxcut_all, Bconnected, gamma_of

def theta_graph(Ls):
    """Theta: hubs 0=s, 1=t, then k internally-disjoint paths with edge-lengths in Ls.
    Each path of edge-length L has L-1 internal vertices. Returns (n, adj)."""
    adj=[];
    def newv():
        adj.append(set()); return len(adj)-1
    s=newv(); t=newv()
    for L in Ls:
        prev=s
        for i in range(L-1):
            v=newv(); adj[prev].add(v); adj[v].add(prev); prev=v
        # connect last internal (or s if L==1) to t
        adj[prev].add(t); adj[t].add(prev)
    return len(adj), adj

def blowup(n, adj, q, blow_set=None):
    """Replace each vertex in blow_set (default ALL) by an independent set of size q;
    edges become complete bipartite. Vertices not in blow_set stay size 1."""
    if blow_set is None: blow_set=set(range(n))
    # assign block sizes
    size=[q if v in blow_set else 1 for v in range(n)]
    start=[0]*n; c=0
    for v in range(n):
        start[v]=c; c+=size[v]
    N=c
    A=[set() for _ in range(N)]
    for u in range(n):
        for v in adj[u]:
            if v>u:
                for a in range(size[u]):
                    for b in range(size[v]):
                        x=start[u]+a; y=start[v]+b
                        A[x].add(y); A[y].add(x)
    return N, A

def summarize(label, n, adj):
    r=check_instance(n, adj)
    obstruction = (r.get("ok") and r.get("triangle_free") and r.get("B_connected")
                   and r.get("ge_n2") and (r.get("m") or 0)>=2 and r.get("has_safe_peel")==False)
    print(f"{label}: N={r.get('N')} tf={r.get('triangle_free')} Bconn={r.get('B_connected')} "
          f"m={r.get('m')} gamma={r.get('gamma')} n2={r.get('n2')} "
          f"ratio={ (r.get('gamma')/r.get('n2')) if r.get('gamma') and r.get('n2') else None} "
          f"tight={r.get('tight')} safe_peel={r.get('has_safe_peel')} OBSTR={obstruction} | {r.get('detail')}")
    sys.stdout.flush()
    return r, obstruction

if __name__=="__main__":
    results=[]
    # length multisets: mixes of 3,5,7 with k in 3..5
    length_sets=[]
    for k in (3,4,5):
        # all same odd length (bipartite) - blow-up may still give bad edges
        for Lval in (3,5,7):
            length_sets.append([Lval]*k)
        # mixed parity to force non-bipartite
        for combo in set(itertools.combinations_with_replacement((3,5,7,2,4), k)):
            length_sets.append(list(combo))
    # dedup
    seen=set(); uniq=[]
    for ls in length_sets:
        key=tuple(sorted(ls))
        if key not in seen: seen.add(key); uniq.append(list(ls))
    print(f"Testing {len(uniq)} length-multisets, q in 1..3")
    best_ratio=(-1,None)
    obstr_count=0
    for ls in uniq:
        for q in (1,2,3):
            n0,adj0=theta_graph(ls)
            N,A=blowup(n0,adj0,q)
            if N>18:  # keep maxcut brute force fast (2^17) and keep<=22
                continue
            label=f"theta{ls}_q{q}"
            try:
                r,ob=summarize(label,N,A)
            except Exception as e:
                print(f"{label}: ERROR {e}"); continue
            if r.get("gamma") and r.get("n2"):
                ratio=r["gamma"]/r["n2"]
                if ratio>best_ratio[0]: best_ratio=(ratio,label)
            if ob: obstr_count+=1
    print(f"\nBEST ratio gamma/n2 = {best_ratio}")
    print(f"OBSTRUCTIONS FOUND = {obstr_count}")
