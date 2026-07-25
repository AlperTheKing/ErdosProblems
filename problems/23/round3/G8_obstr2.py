"""Exact: for every induced subgraph W of And(k), is
   [And(k)[W] -> C5]  <=>  [W contains NO induced Wagner C8(1,4)] ?"""
import itertools, networkx as nx
from G8_graphs import andrasfai
from G8_struct import hom_exists, C5adj
W8 = nx.Graph(); W8.add_edges_from([(i,(i+1)%8) for i in range(8)]+[(i,i+4) for i in range(4)])
for k in (3,4,5):
    n, conn, adj, edges = andrasfai(k)
    # all induced Wagner copies
    wag=[]
    for S in itertools.combinations(range(n),8):
        Ss=set(S); sub=[(u,v) for (u,v) in edges if u in Ss and v in Ss]
        G=nx.Graph(); G.add_nodes_from(S); G.add_edges_from(sub)
        if nx.is_isomorphic(G,W8): wag.append(Ss)
    bad=0; tot=0; nohom=0
    for mask in range(1<<n):
        Wl=[v for v in range(n) if (mask>>v)&1]
        Ws=set(Wl)
        sub=[(u,v) for (u,v) in edges if u in Ws and v in Ws]
        h,_=hom_exists(Wl, sub, C5adj, 5) if Wl else (True,None)
        contains = any(A <= Ws for A in wag)
        tot+=1
        if not h: nohom+=1
        if (not h) != contains: bad+=1
    print(f"And({k}) n={n}: {len(wag)} induced Wagner copies; {nohom}/{tot} induced subgraphs "
          f"lack a hom to C5; mismatches with 'contains induced Wagner': {bad}")
