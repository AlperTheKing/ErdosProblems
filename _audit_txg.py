import networkx as nx
from itertools import combinations

def independent_domination_number(G):
    n = G.number_of_nodes()
    nodes = list(G.nodes())
    best = n+1
    for r in range(1, n+1):
        if r >= best: break
        found = False
        for S in combinations(nodes, r):
            ok = True
            for u,v in combinations(S,2):
                if G.has_edge(u,v): ok=False; break
            if not ok: continue
            dominated = set(S)
            for s in S: dominated |= set(G.neighbors(s))
            if len(dominated)==n:
                best=r; found=True; break
        if found: break
    return best

def min_maximal_matching(G):
    edges = list(G.edges())
    m = len(edges)
    best = m+1
    for r in range(1, m+1):
        if r>=best: break
        found=False
        for S in combinations(edges, r):
            used=set(); ok=True
            for u,v in S:
                if u in used or v in used: ok=False;break
                used.add(u); used.add(v)
            if not ok: continue
            maximal=True
            for (a,b) in edges:
                if a not in used and b not in used:
                    maximal=False;break
            if maximal:
                best=r;found=True;break
        if found:break
    return best

def harmonic_index(G):
    s=0.0
    for u,v in G.edges():
        s += 2.0/(G.degree(u)+G.degree(v))
    return s

from networkx.generators.atlas import graph_atlas_g
G_atlas = graph_atlas_g()

print("=== Conjecture 3: i(G) <= mu*(G) for r-regular r>=3 ===")
tested=0; tight=0; viol=0
for G in G_atlas:
    if G.number_of_nodes()<4: continue
    if not nx.is_connected(G): continue
    degs = [d for _,d in G.degree()]
    if len(set(degs))!=1: continue
    r=degs[0]
    if r<3: continue
    i_=independent_domination_number(G)
    mm=min_maximal_matching(G)
    tested+=1
    if i_>mm: viol+=1; print("VIOLATION C3 n=%d r=%d i=%d mm=%d"%(G.number_of_nodes(),r,i_,mm))
    if i_==mm: tight+=1
print("C3 tested=%d tight(equality)=%d violations=%d"%(tested,tight,viol))

print("=== Conjecture 4: mu*(G) <= H(G) for connected graphs ===")
tested=0; tightish=0; viol=0; minmargin=99; worstG=None
for G in G_atlas:
    if G.number_of_nodes()<2: continue
    if not nx.is_connected(G): continue
    mm=min_maximal_matching(G)
    H=harmonic_index(G)
    tested+=1
    margin=H-mm
    if margin< minmargin: minmargin=margin; worstG=(G.number_of_nodes(),mm,round(H,4))
    if mm>H+1e-9: viol+=1; print("VIOLATION C4 n=%d mm=%d H=%.4f"%(G.number_of_nodes(),mm,H))
    if abs(margin)<1e-9: tightish+=1
print("C4 tested=%d exact-equality=%d violations=%d minmargin=%.4f worst=%s"%(tested,tightish,viol,minmargin,worstG))
