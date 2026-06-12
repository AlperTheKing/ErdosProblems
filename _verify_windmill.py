import networkx as nx
from itertools import combinations

def all_maximal_matchings_min(G):
    edges=list(G.edges())
    n=len(edges)
    best=None; bestset=None
    # iterate all matchings, check maximal, track min size
    # do it by size ascending
    for r in range(0,n+1):
        if best is not None and r>=best: break
        for S in combinations(edges,r):
            used=set(); ok=True
            for u,v in S:
                if u in used or v in used: ok=False;break
                used.add(u);used.add(v)
            if not ok: continue
            # maximal?
            maximal=True
            for (a,b) in edges:
                if a not in used and b not in used: maximal=False;break
            if maximal:
                best=r;bestset=S
                break
        if best is not None and best==r: break
    return best,bestset

def H(G):
    return sum(2.0/(G.degree(u)+G.degree(v)) for u,v in G.edges())

for k in [4,5]:
    G=nx.windmill_graph(k,3)
    print("windmill(%d,3): n=%d m=%d degseq=%s"%(k,G.number_of_nodes(),G.number_of_edges(),sorted([d for _,d in G.degree()],reverse=True)))
    mm,S=all_maximal_matchings_min(G)
    print("   min maximal matching size =",mm, "example=",S)
    print("   H =",round(H(G),4))
    print("   conj mu*<=H ?", mm<=H(G)+1e-9)
