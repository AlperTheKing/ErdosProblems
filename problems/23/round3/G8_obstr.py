"""Are the minimal non-C5-colourable induced subgraphs of And(k) all == Wagner?"""
import itertools, networkx as nx
from G8_graphs import andrasfai
from G8_struct import hom_exists, C5adj
W = nx.Graph(); W.add_edges_from([(i,(i+1)%8) for i in range(8)]+[(i,i+4) for i in range(4)])
for k in (4,5):
    n, conn, adj, edges = andrasfai(k)
    cnt=0; iso=0
    for S in itertools.combinations(range(n), 8):
        Ss=set(S); sub=[(u,v) for (u,v) in edges if u in Ss and v in Ss]
        h,_=hom_exists(S, sub, C5adj, 5)
        if h: continue
        cnt+=1
        G=nx.Graph(); G.add_nodes_from(S); G.add_edges_from(sub)
        if nx.is_isomorphic(G,W): iso+=1
    print(f"And({k}): {cnt} induced 8-vertex subgraphs with no hom to C5; {iso} of them are isomorphic to the Wagner graph C8(1,4)")
