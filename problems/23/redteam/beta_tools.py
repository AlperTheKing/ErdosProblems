import itertools, sys

def is_triangle_free(N, edges):
    adj=[set() for _ in range(N)]
    for u,v in edges:
        adj[u].add(v); adj[v].add(u)
    for u,v in edges:
        if adj[u] & adj[v]:
            return False, (u,v,next(iter(adj[u]&adj[v])))
    return True, None

def maxcut_bruteforce(N, edges):
    # exact maxcut via meet-in-the-middle bitmask not needed for N<=25; do plain 2^(N-1)
    # build adjacency bitmask
    nbr=[0]*N
    for u,v in edges:
        nbr[u]|=(1<<v); nbr[v]|=(1<<u)
    best=0
    # fix vertex 0 in set A to halve
    full=1<<N
    # iterate subsets where bit0=0 (vertex0 in A)
    # cut = number of edges crossing
    # We'll iterate over all 2^(N-1) assignments of vertices 1..N-1, vertex0 in side0
    m=N-1
    for s in range(1<<m):
        side = s<<1  # bit i set => vertex i on side1; vertex0 side0
        cut=0
        for u,v in edges:
            if ((side>>u)&1)!=((side>>v)&1):
                cut+=1
        if cut>best:
            best=cut
    return best

def maxcut_fast(N, edges):
    # faster: incremental over gray-ish? Use per-vertex contribution dynamic.
    # We'll do DP: but simplest robust fast = iterate subsets with popcount of crossing via precomputed.
    nbr=[0]*N
    for u,v in edges:
        nbr[u]|=(1<<v); nbr[v]|=(1<<u)
    best=0
    m=N-1
    # contribution: for assignment 'side' (bitmask over all N, bit0=0),
    # cut = sum over v of (#neighbors of v on opposite side)/2
    # We'll compute cut incrementally by flipping one vertex at a time using Gray code.
    side=0
    # initial cut for side=0 is 0 (all same side)
    cut=0
    # gray code over bits 1..N-1
    total=1<<m
    g_prev=0
    for i in range(1,total):
        g=i^(i>>1)
        diff=g^g_prev
        # which bit changed (in 0..m-1 -> vertex bit+1)
        b=diff.bit_length()-1
        vbit=b+1
        # flipping vertex vbit: change in cut = (#neighbors on same side now becoming opposite) 
        # delta = (neighbors_on_opposite_before - neighbors_on_same_before) when moving
        # current side bitmask:
        opp = bin(nbr[vbit] & side).count("1")  # neighbors on side1
        same = bin(nbr[vbit] & ~side & ((1<<N)-1)).count("1")  # neighbors on side0
        # vertex currently on side = (side>>vbit)&1
        if (side>>vbit)&1:
            # moving from side1 to side0: edges to side0 neighbors become cut(+same... ) 
            # before: cut-edges from vbit = neighbors on side0 = same
            # after: neighbors on side1 = opp
            delta = opp - same
        else:
            delta = same - opp
        side^=(1<<vbit)
        cut+=delta
        if cut>best: best=cut
        g_prev=g
    return best

def beta(N, edges):
    e=len(edges)
    mc=maxcut_fast(N, edges)
    return e-mc, e, mc

if __name__=="__main__":
    # sanity: C5 N=5
    e5=[(0,1),(1,2),(2,3),(3,4),(4,0)]
    tf,_=is_triangle_free(5,e5)
    b,e,mc=beta(5,e5)
    print("C5 trianglefree",tf,"beta",b,"e",e,"maxcut",mc)  # maxcut=4, beta=1
