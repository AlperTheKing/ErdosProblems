# Search small triangle-free graphs (via random generation + maxcut) for instances where
# the all-d4 hypothesis holds, M nonempty, to see how |M| relates to N^2/25 and what the
# certifying flip looks like in NON-block cases. We do NOT assume block structure.
import networkx as nx, itertools, random

def maxcut_bruteforce(G):
    N=G.number_of_nodes(); nodes=list(G.nodes()); best=-1;bestX=None
    # only feasible for small N
    for r in range(N+1):
        for S in itertools.combinations(nodes,r):
            Ss=set(S)
            c=sum(1 for u,v in G.edges() if (u in Ss)!=(v in Ss))
            if c>best: best=c;bestX=Ss
    return best,bestX

def decompose(G,X):
    B=nx.Graph();B.add_nodes_from(G.nodes());M=[]
    for u,v in G.edges():
        if (u in X)==(v in X): M.append((u,v))
        else: B.add_edge(u,v)
    return B,M

def all_d4(B,M):
    spB=dict(nx.all_pairs_shortest_path_length(B))
    if not M: return False
    for (u,v) in M:
        if spB.get(u,{}).get(v,999)!=4: return False
    return True

random.seed(1)
found=[]
for trial in range(4000):
    N=random.randint(8,11)
    p=random.uniform(0.2,0.5)
    G=nx.gnp_random_graph(N,p)
    if sum(nx.triangles(G).values())!=0: continue
    if G.number_of_edges()==0: continue
    mc,X=maxcut_bruteforce(G)
    B,M=decompose(G,X)
    if all_d4(B,M):
        ratio=len(M)/(N*N/25)
        found.append((ratio,N,len(M)))
found.sort(reverse=True)
print("num all-d4 maxcut instances found:",len(found))
for f in found[:10]:
    print("ratio |M|/(N^2/25)=%.3f  N=%d |M|=%d"%f)
