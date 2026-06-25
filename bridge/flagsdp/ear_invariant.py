"""Test candidate PER-EAR invariants for the Connected-B Gamma Lemma.

We build the two extremal families plus the theta witness explicitly, then
compute an ear decomposition of the 2-connected bipartite B and track how a
candidate invariant evolves ear by ear.

Candidate invariants tested:
  (I1)  Gamma vs N^2 directly.
  (I2)  A "potential" Phi = sum_v p_v^2 where p_v is a vertex weight summing to N,
        designed so Phi >= Gamma and Phi <= N^2 (Cauchy: sum p_v^2 <= (sum p_v)^2
        only if one nonzero -- so that's wrong; need the RIGHT structure).
  (I3)  The ear-attachment CD inequality: when an ear of internal length p closes
        a new bad edge of length ell, what does CD force on the attachment cut?
"""
from collections import deque
from itertools import combinations

# ---------- graph builders (return adj as dict of sets, plus a 2-coloring side) ----------

def C5_blowup(q):
    """C5[q]: 5 parts of size q, part i fully joined to part i+1 (mod 5).
    Max cut: this is the extremal. Returns (n, adj, side, M, ells)."""
    parts = [[ (i, j) for j in range(q)] for i in range(5)]
    idx = {}; n = 0
    for i in range(5):
        for j in range(q):
            idx[(i, j)] = n; n += 1
    adj = [set() for _ in range(n)]
    for i in range(5):
        for a in range(q):
            for b in range(q):
                u = idx[(i, a)]; v = idx[((i + 1) % 5, b)]
                adj[u].add(v); adj[v].add(u)
    # a maximum cut of C5[q]: 2-coloring. C5 has max cut 4 edges (one mono edge).
    # Standard: color part i by i in {0,1,2,3,4} -> side = ? We just brute the cut on the quotient.
    # For the blowup, the max cut puts one of the 5 cyclic links as 'mono'. Choose link 4-0 mono.
    # side: parts 0,2 -> X ; parts 1,3 -> Y ; part 4 -> X (so 4-0 same side = mono, 3-4 cross, 4-0 mono)
    side = [0] * n
    colorpart = {0: 0, 1: 1, 2: 0, 3: 1, 4: 0}  # 4-0 both 0 => mono
    for i in range(5):
        for j in range(q):
            side[idx[(i, j)]] = colorpart[i]
    return n, adj, side, idx

def odd_cycle(L):
    """C_{2k+1}: a single odd cycle, m=1 bad edge, B = path."""
    n = L
    adj = [set() for _ in range(n)]
    for i in range(n):
        adj[i].add((i + 1) % n); adj[(i + 1) % n].add(i)
    # max cut of odd cycle: one mono edge. side alternates 0,1,...; edge (n-1,0) is mono.
    side = [i % 2 for i in range(n)]
    return n, adj, side

def c5_paths(plen=4):
    """M=C5 on x0..x4; each cyclic edge xi x_{i+1} subdivided into a B-path of length plen
    (internal vertices). The 5 C5 edges are the bad edges M. plen even => path length plen,
    d_B = plen, ell = plen+1. With plen=4 -> ell=5, N=5+5*3=20 (3 internal per edge)."""
    # vertices: x0..x4 (the C5), plus internal of each path
    n = 0
    idx = {}
    for i in range(5):
        idx[('x', i)] = n; n += 1
    adj = [set() for _ in range(50)]
    side = [0] * 50
    # build paths
    for i in range(5):
        prev = idx[('x', i)]
        # plen-1 internal vertices, then connect to x_{i+1}
        chain = []
        for k in range(plen - 1):
            idx[('p', i, k)] = n; chain.append(n); n += 1
        nxt = idx[('x', (i + 1) % 5)]
        seq = [prev] + chain + [nxt]
        for a, b in zip(seq, seq[1:]):
            adj[a].add(b); adj[b].add(a)
    adj = [adj[v] for v in range(n)]
    side = side[:n]
    # 2-color B (the paths) properly; the C5 edges (xi x_{i+1}) are the MONO/bad edges,
    # i.e. they are NOT in B. We need side such that along each path endpoints alternate,
    # and xi, x_{i+1} end up SAME side (so the direct C5 edge would be mono). Since path has
    # even length plen, the two ends have the SAME color in a proper 2-coloring => good.
    # BFS 2-color from x0 over the B-graph (paths only).
    side = [-1] * n
    side[idx[('x', 0)]] = 0
    q = deque([idx[('x', 0)]])
    while q:
        u = q.popleft()
        for w in adj[u]:
            if side[w] < 0:
                side[w] = 1 - side[u]; q.append(w)
    # add the bad edges xi x_{i+1} to adj? They are bad edges (mono), part of G not B.
    # For Gamma we need M as the mono edges of G. Let's add them to G adjacency.
    M = []
    for i in range(5):
        u = idx[('x', i)]; v = idx[('x', (i + 1) % 5)]
        adj[u].add(v); adj[v].add(u)
        M.append((u, v))
    return n, adj, side, M, idx

def theta_witness():
    """A single bad edge uv whose B-endpoints u,v are joined by TWO B-paths of
    DIFFERENT even lengths 4 and 6 (the minimal 'theta' that breaks single-source layering).
    d_B(u,v)=4 (shortest), ell=5. m=1. This is a sub-case but shows the theta regime."""
    n = 0; idx = {}
    idx['u'] = n; n += 1
    idx['v'] = n; n += 1
    # path A length 4: u-a1-a2-a3-v
    for k in range(3):
        idx[('a', k)] = n; n += 1
    # path B length 6: u-b1-b2-b3-b4-b5-v
    for k in range(5):
        idx[('b', k)] = n; n += 1
    adj = [set() for _ in range(n)]
    def link(x, y): adj[x].add(y); adj[y].add(x)
    pa = [idx['u'], idx[('a', 0)], idx[('a', 1)], idx[('a', 2)], idx['v']]
    for x, y in zip(pa, pa[1:]): link(x, y)
    pb = [idx['u'], idx[('b', 0)], idx[('b', 1)], idx[('b', 2)], idx[('b', 3)], idx[('b', 4)], idx['v']]
    for x, y in zip(pb, pb[1:]): link(x, y)
    side = [-1] * n; side[idx['u']] = 0; q = deque([idx['u']])
    while q:
        x = q.popleft()
        for w in adj[x]:
            if side[w] < 0:
                side[w] = 1 - side[x]; q.append(w)
    # both paths even length => u,v same side => uv is mono(bad)
    link(idx['u'], idx['v'])
    M = [(idx['u'], idx['v'])]
    return n, adj, side, M, idx

# ---------- generic Gamma evaluation ----------

def bdist_graph(n, adjB, src):
    d = [-1] * n; d[src] = 0; q = deque([src])
    while q:
        u = q.popleft()
        for w in adjB[u]:
            if d[w] < 0:
                d[w] = d[u] + 1; q.append(w)
    return d

def evaluate(n, adj, side, M):
    # B = cross edges
    adjB = [set() for _ in range(n)]
    for u in range(n):
        for v in adj[u]:
            if v > u and side[u] != side[v]:
                adjB[u].add(v); adjB[v].add(u)
    ells = []
    for (u, v) in M:
        d = bdist_graph(n, adjB, u)[v]
        ells.append(d + 1 if d >= 0 else None)
    Gamma = sum(e * e for e in ells if e)
    return n, Gamma, ells, adjB

if __name__ == "__main__":
    print("=== C5[q] family (extremal, Gamma should = N^2) ===")
    for q in [1, 2, 3]:
        n, adj, side, idx = C5_blowup(q)
        M = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
        nn, G, ells, adjB = evaluate(n, adj, side, M)
        print(f"  q={q}: N={nn} m={len(M)} ells={sorted([e for e in ells if e])} Gamma={G} N^2={nn*nn} ratio={G/(nn*nn):.4f}")

    print("=== odd cycles (extremal) ===")
    for L in [5, 7, 9, 11]:
        n, adj, side = odd_cycle(L)
        M = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
        nn, G, ells, adjB = evaluate(n, adj, side, M)
        print(f"  L={L}: N={nn} m={len(M)} ells={ells} Gamma={G} N^2={nn*nn} ratio={G/(nn*nn):.4f}")

    print("=== c5_paths theta-regime (M=C5, paths length 4) ===")
    n, adj, side, M, idx = c5_paths(4)
    nn, G, ells, adjB = evaluate(n, adj, side, M)
    print(f"  N={nn} m={len(M)} ells={ells} Gamma={G} N^2={nn*nn} ratio={G/(nn*nn):.4f}")

    print("=== single theta witness (paths 4 & 6 for one bad edge) ===")
    n, adj, side, M, idx = theta_witness()
    nn, G, ells, adjB = evaluate(n, adj, side, M)
    print(f"  N={nn} m={len(M)} ells={ells} Gamma={G} N^2={nn*nn} ratio={G/(nn*nn):.4f}")
    print("DONE")
