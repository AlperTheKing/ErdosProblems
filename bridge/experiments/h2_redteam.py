import itertools, sys

def neighbors(n, edges):
    adj = [0]*n
    for (u,v) in edges:
        adj[u] |= (1<<v)
        adj[v] |= (1<<u)
    return adj

def is_triangle_free(n, edges):
    adj = neighbors(n, edges)
    for (u,v) in edges:
        if adj[u] & adj[v]:
            return False
    return True

def has_triangle_subset(adj, verts):
    # verts: list of vertex indices; check triangle among them using adj bitmask
    vmask = 0
    for w in verts:
        vmask |= (1<<w)
    for i in range(len(verts)):
        u = verts[i]
        nu = adj[u] & vmask
        for j in range(i+1, len(verts)):
            v = verts[j]
            if (nu>>v)&1:
                if adj[u] & adj[v] & vmask:
                    return True
    return False

def maxcut_full(n, adj_list_edges):
    # adj_list_edges: list of (u,v). brute force over 2^n colorings of vertices present.
    # vertices assumed labeled 0..n-1 but some may be isolated; that's fine.
    m = len(adj_list_edges)
    best = 0
    # represent each edge as pair
    E = adj_list_edges
    for assign in range(1<<n):
        cut = 0
        for (u,v) in E:
            if ((assign>>u)^(assign>>v)) & 1:
                cut += 1
        if cut > best:
            best = cut
    return best

def beta(n, edges):
    m = len(edges)
    return m - maxcut_full(n, edges)

# faster maxcut using vertex-order incremental? For n<=15 brute is fine but for repeated
# subgraph (10 vtx) we relabel.

def maxcut_relabel(verts, edges_set):
    # verts: set of remaining vertices; edges_set: set of frozenset/tuple among full graph
    vl = sorted(verts)
    idx = {v:i for i,v in enumerate(vl)}
    k = len(vl)
    E = []
    for (u,v) in edges_set:
        if u in idx and v in idx:
            E.append((idx[u], idx[v]))
    best = 0
    for assign in range(1<<k):
        cut = 0
        for (u,v) in E:
            if ((assign>>u)^(assign>>v)) & 1:
                cut += 1
        if cut > best:
            best = cut
    return best, len(E)

def beta_sub(verts, edges_set):
    mc, m = maxcut_relabel(verts, edges_set)
    return m - mc

def min5drop(n, edges):
    # returns (min_drop, argmin set, beta_G)
    edges_set = [tuple(sorted(e)) for e in edges]
    bG = beta_sub(set(range(n)), edges_set)
    allv = set(range(n))
    best = None
    bestS = None
    for S in itertools.combinations(range(n), 5):
        rem = allv - set(S)
        bGS = beta_sub(rem, edges_set)
        drop = bG - bGS
        if best is None or drop < best:
            best = drop
            bestS = S
    return best, bestS, bG

def report(name, n, edges):
    edges = [tuple(sorted(e)) for e in set(tuple(sorted(e)) for e in edges)]
    tf = is_triangle_free(n, edges)
    if not tf:
        print(f"{name}: NOT triangle-free (m={len(edges)})")
        return None
    md, S, bG = min5drop(n, edges)
    # H2 at n=3 requires min5drop <= 2n-1 = 5. Break if min5drop >= 6.
    nn = n//5
    thr = 2*nn - 1
    status = "BREAKS H2" if md > thr else "satisfies H2"
    print(f"{name}: n={n} m={len(edges)} TF=True beta={bG} min5drop={md} thr(2n-1)={thr} -> {status} (argmin {S})")
    return (bG, md, thr, md>thr)

if __name__ == "__main__":
    # quick self-test: C5 blow-up C5[3] should have beta=9, min5drop=5
    def c5_blowup(t):
        # parts 0..4 each size t; part i = vertices [i*t, (i+1)*t)
        edges = []
        for i in range(5):
            j = (i+1)%5
            for a in range(t):
                for b in range(t):
                    edges.append((i*t+a, j*t+b))
        return 5*t, edges
    n,e = c5_blowup(3)
    report("C5[3] (sanity)", n, e)
