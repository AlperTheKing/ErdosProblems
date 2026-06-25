import networkx as nx, itertools

def make_graph(B,M):
    G=nx.Graph(); G.add_edges_from(B.edges()); G.add_edges_from(M); return G
def is_triangle_free(B,M):
    return sum(nx.triangles(make_graph(B,M)).values())==0
def all_d4(B,M):
    spB=dict(nx.all_pairs_shortest_path_length(B))
    return all(spB.get(u,{}).get(v,999)==4 for (u,v) in M)
def cd_worst(B,M,N):
    Bm=list(B.edges()); Mm=list(M); worst=(0,None)
    for r in range(1,N):
        for S in itertools.combinations(range(N),r):
            Ss=set(S)
            eM=sum(1 for (a,b) in Mm if (a in Ss)!=(b in Ss))
            eB=sum(1 for (a,b) in Bm if (a in Ss)!=(b in Ss))
            if eM-eB>worst[0]: worst=(eM-eB,S)
    return worst
def C5_blowup_BM(n):
    L=[list(range(i*n,(i+1)*n)) for i in range(5)]
    N=5*n; Bfull=nx.Graph(); Bfull.add_nodes_from(range(N))
    for i in range(5):
        for u in L[i]:
            for v in L[(i+1)%5]: Bfull.add_edge(u,v)
    X=set(L[0])|set(L[2])|set(L[4])
    M=set(); B2=nx.Graph(); B2.add_nodes_from(range(N))
    for (a,b) in Bfull.edges():
        if (a in X)==(b in X): M.add((a,b))
        else: B2.add_edge(a,b)
    return B2,M,N,X
B,M,N,X=C5_blowup_BM(2)
print("C5[2]: N",N,"|M|",len(M),"|B|",B.number_of_edges(),
      "trifree",is_triangle_free(B,M),"alld4",all_d4(B,M),"N^2/25",N*N/25)
print("CD worst",cd_worst(B,M,N)[0])
