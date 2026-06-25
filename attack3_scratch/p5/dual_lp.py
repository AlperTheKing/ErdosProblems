## The cleanest rigorous route: FRACTIONAL BLOCK DECOMPOSITION via a weighted flip LP.
##
## Load-bearing inequality (candidate): For ANY probability weights lambda_S >= 0 over flips S
## with sum lambda_S = 1, CD gives  sum_S lambda_S e_M(S) <= sum_S lambda_S e_B(S).
## Choose lambda supported on a 1-parameter family so that:
##   LHS = sum_{mn in M} Pr[S cuts mn]   and   RHS = sum_{ab in B} Pr[S cuts ab].
## We want a distribution making Pr[cut mn] (for d_B=4 edges) LARGE relative to the total
## B-capacity, with the quadratic N^2 emerging from a SECOND averaging over a base point.
##
## Test the 2-point "interval on a circle" distribution that is EXACTLY tight on C5[n]:
## Embed the 5 C5-classes at angles 0,72,144,216,288 deg. Random arc S = points whose angle
## in [theta, theta+180). For C5[n] this is the maxcut family and should be tight.
##
## For a GENERAL graph we do NOT have angles. So instead test: is there a distribution over
## flips, depending only on B (not on a homomorphism), that certifies 25|M|<=N^2 ?
## Use the RANDOM BFS half-ball: pick root r, threshold the potential phi_r = d_B(r,.) at the
## MEDIAN, combined with random root. Measure constant.
import networkx as nx, itertools, math

def block_model(sizes):
    L=[];idx=0
    for s in sizes: L.append(list(range(idx,idx+s)));idx+=s
    N=idx;B=nx.Graph();B.add_nodes_from(range(N))
    for i in range(4):
        for u in L[i]:
            for v in L[i+1]:B.add_edge(u,v)
    M=[(u,v) for u in L[0] for v in L[4]]
    return B,M,N

# Distribution: S = {x : d_B(r,x) in selected residue mod 5 windows}?
# The TRUE tight family for C5[n] maxcut: S = union of 2 or 3 consecutive classes.
# In B-distance terms from a vertex in class 0: classes at distance 0,1,2,2,1 (C5 metric!).
# So B-distance does NOT separate the 5 classes (class 3 and 4 both at dist 2). That is the
# core reason a single BFS potential is insufficient: the C5 metric is not a path metric.
#
# Demonstrate: from a class-0 vertex in C5[n], print B-distance to each class.
import numpy as np
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
    return B2,M,N,L,X
B,M,N,L,X=C5_blowup_BM(3)
sp=dict(nx.all_pairs_shortest_path_length(B))
r=L[0][0]
print("From class-0 vertex, B-distance to a representative of each class:")
for i in range(5):
    print(" class",i,"->",sp[r].get(L[i][0],"inf"))
print("M edges live within X = classes 0,2,4. |M|=",len(M),"N=",N)
print("So B (the cut graph) is NOT the C5 cycle; it is the bipartite double-cover-ish graph.")
