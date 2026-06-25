## Test whether a GLOBAL analogue of the four chain inequalities holds.
## In the block case the proof used N >= p+q+a+w+d with 5 DISJOINT layers.
## General-case substitute idea: define for the WHOLE graph a single optimal
## fractional "potential" via the LP dual of CD. Concretely: does there exist
## an assignment of each vertex to a "level" in [0,4] (real) such that
##   (a) every bad edge has level-drop = 4 (its endpoints at levels differing by 4),
##   (b) every B-edge has |level-drop| <= 1,
## ? If yes, the coarea identity sum_M|drop| <= sum_B|drop| <= |B| gives 4|M|<=|B|,
## still only LINEAR. So even a perfect potential does NOT reach N^2/25 by itself.
##
## CONCLUSION TO TEST: the quadratic N^2 bound CANNOT come from a single 1-Lipschitz
## potential (that only ever gives a |B|-type linear bound). It must come from a
## TWO-DIMENSIONAL embedding (C5 sits in the plane / circle). Test: does CD+all-d4
## force a homomorphism-like map to the 5-cycle metric on a CIRCLE giving area ~ N^2?
##
## Direct experiment: take random all-d4 CD instances and check the SHARP quadratic
## inequality  25|M| <= N^2  AND  whether the certifying improving flip (when 25|M|>N^2,
## which never happens for CD-valid) would be a ball. Since CD-valid never violates,
## instead measure SLACK N^2 - 25|M| and see if it correlates with non-block structure.
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

# Try to find an all-d4 instance whose M is NOT a single complete-bipartite block
# (i.e. genuinely tests incompatibility) and check the bound.
random.seed(7)
nonblock=[]
for trial in range(8000):
    N=random.randint(9,12); p=random.uniform(0.25,0.5)
    G=nx.gnp_random_graph(N,p)
    if sum(nx.triangles(G).values())!=0 or G.number_of_edges()==0: continue
    if N>11: continue
    mc,X=maxcut_bruteforce(G)
    B,M=decompose(G,X)
    if not all_d4(B,M): continue
    # is M a single complete bipartite block within one side?
    Mg=nx.Graph(); Mg.add_edges_from(M)
    comps=list(nx.connected_components(Mg))
    is_block = (len(comps)==1)
    if len(M)>=3:
        nonblock.append((len(M),N,N*N/25 - len(M), is_block, len(comps)))
nonblock.sort()
print("all-d4 instances with |M|>=3:",len(nonblock))
for x in nonblock[:15]:
    print("|M|=%d N=%d slack(N^2/25 - |M|)=%.2f single_M_comp=%s #Mcomps=%d"%x)
