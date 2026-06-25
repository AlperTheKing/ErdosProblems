## CRITICAL TEST: when M has multiple components / is non-block, can we still get the bound
## by summing per-block bounds, given the layers OVERLAP?  The danger: N is shared but layer
## sums are added => over-counting => sum of (N_block^2/25) could EXCEED N^2/25.
##
## Test: take the two-chords-shared-w instance. Treat each chord as a "micro-block" with
## p=q=a=w=d=1, so each gives 1 <= N_local^2/25 with N_local=5. Two blocks share w.
## sum |M_block| = 2. N=9. 2 <= 81/25=3.24 OK. The shared w SAVES vertices (N=9 not 10),
## yet bound still holds because each block is far from tight.
##
## The real question: can overlap make sum|M| approach N^2/25 from ABOVE? i.e. is there a
## CD+all-d4 instance with 25|M| > N^2 ? The project claims NO (0 violations N<=11, Gamma<=N^2).
## Let me do an EXHAUSTIVE-ish randomized stress test maximizing |M| for given N under CD+all-d4,
## using a local search that adds bad edges + B structure while preserving constraints.
import networkx as nx, itertools, random

def maxcut_bruteforce(G):
    N=G.number_of_nodes(); nodes=list(G.nodes()); best=-1;bestX=None
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
    return all(spB.get(u,{}).get(v,999)==4 for (u,v) in M)

# Exhaustive over all triangle-free graphs up to N=8 using nauty would be ideal but we just
# randomize heavily and track max ratio 25|M|/N^2.
random.seed(123)
best_ratio=0; best_info=None
for trial in range(60000):
    N=random.randint(5,10)
    # bias toward C5-blowup-like: build from 5 groups with C5 adjacency + noise
    if random.random()<0.5:
        G=nx.gnp_random_graph(N,random.uniform(0.2,0.55))
    else:
        # blow-up-ish
        sizes=[random.randint(1,2) for _ in range(5)]
        L=[];idx=0
        for s in sizes: L.append(list(range(idx,idx+s)));idx+=s
        Nn=idx; G=nx.Graph(); G.add_nodes_from(range(Nn))
        for i in range(5):
            for u in L[i]:
                for v in L[(i+1)%5]:
                    if random.random()<0.9: G.add_edge(u,v)
        N=Nn
    if sum(nx.triangles(G).values())!=0 or G.number_of_edges()==0: continue
    mc,X=maxcut_bruteforce(G)
    B,M=decompose(G,X)
    if not all_d4(B,M): continue
    ratio=25*len(M)/(N*N)
    if ratio>best_ratio:
        best_ratio=ratio; best_info=(N,len(M))
print("max 25|M|/N^2 over all CD-valid all-d4 instances found:",round(best_ratio,4),"at",best_info)
print("(<=1 means bound holds; =1 means tight = C5[n] only)")
