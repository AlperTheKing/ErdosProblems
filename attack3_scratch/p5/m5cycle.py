## M contains an ODD 5-CYCLE m0-m1-m2-m3-m4-m0 (bad edges), each with its own length-4 B-geodesic.
## M as a graph is C5 (odd, not bipartite) => no {0,4} path-layering => geodesics globally
## incompatible. Triangle-free in G? bad edges only adjacent (share m_i); a B-geodesic per bad
## edge with fresh internal vertices avoids triangles. Test triangle-free + all-d4 + CD.
import networkx as nx, itertools

def cd_worst(B,M,N,nodes,cap=None):
    Bm=list(B.edges()); worst=(0,None); cnt=0
    for r in range(1,N):
        for S in itertools.combinations(nodes,r):
            Ss=set(S)
            eM=sum(1 for (a,b) in M if (a in Ss)!=(b in Ss))
            eB=sum(1 for (a,b) in Bm if (a in Ss)!=(b in Ss))
            if eM-eB>worst[0]: worst=(eM-eB,S)
            cnt+=1
            if cap and cnt>cap: return worst
    return worst

def build_M5():
    B=nx.Graph(); M=[]; Xset=set(); Yset=set()
    ms=[f"m{i}" for i in range(5)]; Xset|=set(ms)
    edges=[(ms[i],ms[(i+1)%5]) for i in range(5)]
    for (u,v) in edges:
        a=f"a_{u}_{v}"; w=f"w_{u}_{v}"; b=f"b_{u}_{v}"
        Yset|={a,b}; Xset|={w}
        for e in [(u,a),(a,w),(w,b),(b,v)]: B.add_edge(*e)
        M.append((u,v))
    B.add_nodes_from(Xset|Yset)
    return B,M,Xset,Yset
B,M,X,Y=build_M5()
N=B.number_of_nodes(); nodes=list(B.nodes())
G=nx.Graph(); G.add_edges_from(B.edges()); G.add_edges_from(M)
trif=sum(nx.triangles(G).values())==0
spB=dict(nx.all_pairs_shortest_path_length(B))
d4=all(spB.get(u,{}).get(v,999)==4 for u,v in M)
bip=all((a in X)!=(b in X) for a,b in B.edges())
print("M5-cycle: N",N,"|M|",len(M),"trifree",trif,"alld4",d4,"Bbip",bip)
# M as graph is C5: is it bipartite? no.
Mg=nx.Graph(); Mg.add_edges_from(M)
print("M bipartite?",nx.is_bipartite(Mg)," (False => no global {0,4} layering)")
w=cd_worst(B,M,N,nodes,cap=4_000_000)
print("CD worst:",w[0]," (>0 => CD forbids this frustrated instance)")
print(" certifying improving flip S=",sorted(w[1]) if w[1] else None)
print("N^2/25=",round(N*N/25,3),"|M|=",len(M))
