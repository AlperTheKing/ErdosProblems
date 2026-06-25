import networkx as nx
def C5_blowup_BM(n):
    L=[list(range(i*n,(i+1)*n)) for i in range(5)]
    N=5*n; Bfull=nx.Graph(); Bfull.add_nodes_from(range(N))
    for i in range(5):
        for u in L[i]:
            for v in L[(i+1)%5]: Bfull.add_edge(u,v)
    X=set(L[0])|set(L[2])|set(L[4])
    M=[]; B2=nx.Graph(); B2.add_nodes_from(range(N))
    for (a,b) in Bfull.edges():
        if (a in X)==(b in X): M.append((a,b))
        else: B2.add_edge(a,b)
    classof={}
    for i in range(5):
        for x in L[i]: classof[x]=i
    return B2,M,N,L,X,classof
B,M,N,L,X,classof=C5_blowup_BM(3)
from collections import Counter
pairs=Counter(tuple(sorted((classof[a],classof[b]))) for a,b in M)
print("bad-edge class-pairs:",dict(pairs))
# So the bad edges connect class 4 and class 0? both in X. In C5, 4-0 ARE adjacent (cycle edge).
# That cycle edge 4-0 is the ODD edge of the maxcut (the one mono edge). |class4|*|class0| of them.
print("So M = complete bipartite between class 4 and class 0 (the single odd C5-edge), size",
      len(L[0])*len(L[4]))
# This is ONE block U=class0, V=class4. The geodesic u in c0 to v in c4 in B:
sp=dict(nx.all_pairs_shortest_path_length(B))
u=L[0][0]; v=L[4][0]
print("d_B(u,v) for u in c0,v in c4:",sp[u][v])
# path: c0 - c1 - c2 - c3 - c4 (length 4) since the direct 0-4 edge is in M not B.
print("So C5[n] IS the single-block case U=class0(p=n), V=class4(q=n), A=c1,W=c2,D=c3, all size n.")
print("Block proof is EXACTLY tight here: p=q=a=w=d=n, N=5n, pq=n^2=N^2/25.")
