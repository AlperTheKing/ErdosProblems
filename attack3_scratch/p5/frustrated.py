## Build a "frustrated" cycle of chords: vertices m0,m1,m2 in X, bad edges m0m1, m1m2, m2m0?
## But a bad edge needs d_B=4; a triangle of bad edges among 3 vertices would need pairwise d_B=4.
## Orientation frustration: if we want a path-layering phi:V->{0..4} with each bad edge spanning
## {0,4}, then each bad edge forces its two endpoints to opposite ends. For an ODD cycle of bad
## edges m0-m1-m2-m0 (in the "bad" graph M), the {0,4} 2-coloring is impossible (odd cycle not
## bipartite in M). So if M contains an ODD CYCLE, NO global path-layering exists. Does CD+all-d4
## ALLOW M to contain an odd cycle? Test by constructing one and checking CD + triangle-free.
import networkx as nx, itertools

def cd_worst(B,M,N,nodes):
    Bm=list(B.edges()); worst=(0,None)
    for r in range(1,N):
        for S in itertools.combinations(nodes,r):
            Ss=set(S)
            eM=sum(1 for (a,b) in M if (a in Ss)!=(b in Ss))
            eB=sum(1 for (a,b) in Bm if (a in Ss)!=(b in Ss))
            if eM-eB>worst[0]: worst=(eM-eB,S)
    return worst

# Three X-vertices m0,m1,m2, pairwise bad edges (triangle in M). Each pair needs a B-geodesic of
# length 4 through Y,X,Y. Give each pair its own 3 intermediate vertices (a_ij in Y, w_ij in X, b_ij in Y).
import itertools as it
def build_triangle_M():
    B=nx.Graph(); M=[]
    Xset=set(['m0','m1','m2']); Yset=set()
    pairs=[('m0','m1'),('m1','m2'),('m2','m0')]
    for (u,v) in pairs:
        a=f"a_{u}{v}"; w=f"w_{u}{v}"; b=f"b_{u}{v}"
        Yset|={a,b}; Xset|={w}
        for e in [(u,a),(a,w),(w,b),(b,v)]: B.add_edge(*e)
        M.append((u,v))
    B.add_nodes_from(Xset|Yset)
    return B,M,Xset,Yset
B,M,X,Y=build_triangle_M()
N=B.number_of_nodes(); nodes=list(B.nodes())
G=nx.Graph(); G.add_edges_from(B.edges()); G.add_edges_from(M)
trif=sum(nx.triangles(G).values())==0
spB=dict(nx.all_pairs_shortest_path_length(B))
d4=all(spB.get(u,{}).get(v,999)==4 for u,v in M)
bip=all((a in X)!=(b in X) for a,b in B.edges())
mono=all((a in X)==(b in X) for a,b in M)
w=cd_worst(B,M,N,nodes)
print("M-triangle instance: N",N,"|M|",len(M),"trifree",trif,"alld4",d4,"Bbip",bip,"Mmono",mono)
print("CD worst (>0 means NOT cut-valid):",w[0],"certifying S=",w[1])
print("N^2/25=",round(N*N/25,3),"|M|=",len(M))
# Check: is M (odd triangle) layerable? No (odd cycle). So if CD-valid, it'd be a genuine
# non-layerable CD instance. If CDworst>0, CD FORBIDS it -> CD kills frustration.
PYEOF=0
