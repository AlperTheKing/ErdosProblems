import networkx as nx, itertools

# The block-case AM-GM proves: for a SINGLE complete-bipartite block U x V with its 5 disjoint
# geodesic shells (U,A,W,D,V), |M_block| = |U|*|V| <= N_block^2 / 25, where N_block = |U|+|A|+|W|+|D|+|V|.
# The claim under audit: this gives a bound for GENERAL M by aggregating blocks.
# FATAL CONCERN: the 5 shells of DIFFERENT blocks overlap (share vertices). So sum_blocks N_block
# can exceed N, and the per-block bounds do NOT add up to a global N^2/25 bound.
# This script makes the non-additivity explicit and shows the block proof does not compose.

def cd_worst(B,M,N,nodes):
    Bm=list(B.edges()); worst=0
    for r in range(1,N):
        for S in itertools.combinations(nodes,r):
            Ss=set(S)
            eM=sum(1 for (a,b) in M if (a in Ss)!=(b in Ss))
            eB=sum(1 for (a,b) in Bm if (a in Ss)!=(b in Ss))
            if eM-eB>worst: worst=eM-eB
    return worst

# Two blocks sharing the middle shell vertex w (the 'shared-w' instance).
# Block1: u1 -a1- w -b1- v1   (chord u1-v1)
# Block2: u2 -a2- w -b2- v2   (chord u2-v2)
# Shared w. X={w,u1,v1,u2,v2}? Need w on same side as u's? Let's lay sides: X has u1,v1,u2,v2,w; Y has a's,b's.
X={'w','u1','v1','u2','v2'}; Y={'a1','b1','a2','b2'}
B=nx.Graph(); B.add_nodes_from(X|Y)
for e in [('u1','a1'),('a1','w'),('w','b1'),('b1','v1'),
          ('u2','a2'),('a2','w'),('w','b2'),('b2','v2')]: B.add_edge(*e)
M=[('u1','v1'),('u2','v2')]
G=nx.Graph(); G.add_edges_from(B.edges()); G.add_edges_from(M)
N=G.number_of_nodes()
trif=sum(nx.triangles(G).values())==0
sp=dict(nx.all_pairs_shortest_path_length(B))
d4=all(sp[u][v]==4 for u,v in M)
# is X|Y a max cut?
nodes=list(G.nodes())
given=sum(1 for a,b in G.edges() if (a in X)!=(b in X))
best=-1
for mask in range(1<<N):
    S=set(nodes[i] for i in range(N) if mask&(1<<i))
    c=sum(1 for a,b in G.edges() if (a in S)!=(b in S))
    if c>best: best=c
print("shared-w 2-block: N=%d |M|=%d trifree=%s all_d4=%s CDworst=%d maxcut_ok=%s"%(
    N,len(M),trif,d4,cd_worst(B,M,N,nodes),given==best))

# Per-block accounting: each block has U={u_i},A={a_i},W={w},D={b_i},V={v_i}: 5 shells, but w is SHARED.
# Block1 N_block1 = |{u1}|+|{a1}|+|{w}|+|{b1}|+|{v1}| = 5  -> bound |M1| <= 25/25 = 1. OK (|M1|=1).
# Block2 same: N_block2 = 5 -> |M2| <= 1. OK.
# Sum of per-block N_block = 5+5 = 10, but TRUE N = 9 (w shared).
print("Per-block N_block sum = 5+5 = 10, but true N = %d (w shared across both blocks)."%N)
print("=> sum_block N_block^2/25 = 2.0, while N^2/25 = %.3f. The per-block bounds do NOT add to N^2/25;"%(N*N/25))
print("   here it happens to hold only because each block is FAR from its own tightness.")
print()
print("KEY POINT: the block-case AM-GM consumes ALL N vertices to bound ONE block's |M|.")
print("For >=2 blocks it provides NO valid aggregate inequality: the 5-shell partitions of")
print("distinct blocks are different partitions of the SAME vertex set, not a common refinement.")
print("The M-odd-cycle (m5cycle, N=20) has NO global 5-shell layering at all (M non-bipartite),")
print("so the 'five disjoint geodesic shells' object that powers the AM-GM does not even exist globally.")
