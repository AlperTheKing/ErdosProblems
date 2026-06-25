## Deliberately construct two C5-chords sharing structure, to probe geodesic incompatibility.
## Chord 1: u1-a1-w-b1-v1 (bad edge u1v1, both in X).
## Chord 2: u2-a2-w-b2-v2 sharing middle w but otherwise distinct.
## We must keep B bipartite (X,Y), M monochromatic, triangle-free, and check CD + all-d4 + bound.
import networkx as nx, itertools

def analyze(B, M, X, Y, label):
    N = B.number_of_nodes()
    G = nx.Graph(); G.add_edges_from(B.edges()); G.add_edges_from(M)
    trif = sum(nx.triangles(G).values())==0
    # bipartite check on B
    bip = all((a in X)!=(b in X) for a,b in B.edges())
    mono = all((a in X)==(b in X) for a,b in M)
    spB=dict(nx.all_pairs_shortest_path_length(B))
    d4 = all(spB.get(u,{}).get(v,999)==4 for u,v in M)
    # CD worst
    Bm=list(B.edges()); Mm=list(M); worst=(0,None)
    nodes=list(range(N))
    for r in range(1,N):
        for S in itertools.combinations(nodes,r):
            Ss=set(S)
            eM=sum(1 for (a,b) in Mm if (a in Ss)!=(b in Ss))
            eB=sum(1 for (a,b) in Bm if (a in Ss)!=(b in Ss))
            if eM-eB>worst[0]: worst=(eM-eB,S)
    print(label, "N",N,"|M|",len(M),"trifree",trif,"Bbip",bip,"Mmono",mono,
          "alld4",d4,"CDworst",worst[0],"N^2/25",round(N*N/25,2),"|M|<=N^2/25", len(M)<=N*N/25)
    return worst

# Build: shared middle w. Vertices: w(X), u1,v1,u2,v2 (X), a1,b1,a2,b2 (Y).
# B edges: u1-a1-w-b1-v1 ; u2-a2-w-b2-v2.  M: u1v1, u2v2.
X={'w','u1','v1','u2','v2'}; Y={'a1','b1','a2','b2'}
B=nx.Graph(); B.add_nodes_from(X|Y)
for e in [('u1','a1'),('a1','w'),('w','b1'),('b1','v1'),
          ('u2','a2'),('a2','w'),('w','b2'),('b2','v2')]:
    B.add_edge(*e)
M=[('u1','v1'),('u2','v2')]
analyze(B,M,X,Y,"two-chords-shared-w:")

# Now FORCE a cross-incompatibility: make u2 = v1 (one chord's source is another's sink).
# Relabel v1 and u2 to same vertex 'm'. Chords: u1-a1-w-b1-m and m-a2-w'-b2-v2.
X2={'w','wp','u1','m','v2'}; Y2={'a1','b1','a2','b2'}
B2=nx.Graph(); B2.add_nodes_from(X2|Y2)
for e in [('u1','a1'),('a1','w'),('w','b1'),('b1','m'),
          ('m','a2'),('a2','wp'),('wp','b2'),('b2','v2')]:
    B2.add_edge(*e)
M2=[('u1','m'),('m','v2')]
analyze(B2,M2,X2,Y2,"chained-chords (m is sink of 1, source of 2):")
