# Test the LOAD-BEARING inequality candidate via a quadratic averaging over BFS balls.
# For each ordered pair (r, t) with r in V, t in {0,1,2,3}, define S_{r,t} = ball_B(r,t).
# CD: e_M(S_{r,t}) <= e_B(S_{r,t}).  Sum over r in V and t in {0,1,2,3}:
#    sum_{r,t} e_M(S_{r,t})  <=  sum_{r,t} e_B(S_{r,t}).
# LHS = sum_{r} sum_{mn in M} #{t in 0..3 : exactly one of m,n in ball(r,t)}
#     = sum_{mn in M} sum_r |#{t<=3: d(r,m)<=t} - #{t<=3: d(r,n)<=t}|   (monotone in t)
#     = sum_{mn in M} sum_r |clip(4-d(r,m)) - clip(4-d(r,n))|  where clip(x)=min(max(x,0),4)
# Let me just compute LHS and RHS directly on C5[2] and block models and look at the ratio,
# to see whether this quadratic-in-N family yields 25|M| <= N^2 with the right constant.
import networkx as nx, itertools
def block_model(sizes):
    L=[];idx=0
    for s in sizes: L.append(list(range(idx,idx+s)));idx+=s
    N=idx;B=nx.Graph();B.add_nodes_from(range(N))
    for i in range(4):
        for u in L[i]:
            for v in L[i+1]:B.add_edge(u,v)
    M=[(u,v) for u in L[0] for v in L[4]]
    return B,M,N

def lhs_rhs(B,M,N,T=3):
    sp=dict(nx.all_pairs_shortest_path_length(B))
    INF=999
    def inball(r,x,t): return sp[r].get(x,INF)<=t
    LHS=0;RHS=0
    for r in range(N):
        for t in range(T+1):
            ball=set(x for x in range(N) if inball(r,x,t))
            LHS+=sum(1 for (a,b) in M if (a in ball)!=(b in ball))
            RHS+=sum(1 for (a,b) in B.edges() if (a in ball)!=(b in ball))
    return LHS,RHS

for sizes in [[2,2,2,2,2],[3,3,3,3,3],[4,4,4,4,4],[2,2,2,2,3],[3,2,2,2,3]]:
    B,M,N=block_model(sizes)
    L,R=lhs_rhs(B,M,N)
    # we want some normalization giving 25|M|<=N^2. Print L, R, and L per |M|, N, etc.
    print(sizes,"N",N,"|M|",len(M),"LHS",L,"RHS",R,"LHS/|M|=%.2f"%(L/len(M)),"holds(L<=R)",L<=R)
