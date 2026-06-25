"""REVERSE EAR INDUCTION test for the Connected-B Gamma Lemma.

We need to know whether removing an ear from B (the 2-connected bipartite cut-graph)
admits a clean monotone invariant. CRITICAL SUBTLETY: removing an ear from B may
remove bad edges (if a bad edge's endpoint was an internal ear vertex) AND may
increase ell of surviving bad edges (d_B can only grow when edges leave B). We must
track how Gamma changes.

The clean per-ear question:
   B_t  -> B_{t-1} by removing ear E (p internal vertices, endpoints a,b in B_{t-1}).
   N_t = N_{t-1} + p.
   Gamma_t vs Gamma_{t-1}: bad edges with an endpoint among the p internal vertices
       are DELETED (they involve ear-internal vertices); surviving bad edges may see
       d_B INCREASE (their shortest path used the ear).
We want: Gamma_t <= Gamma_{t-1} + (N_t^2 - N_{t-1}^2) = Gamma_{t-1} + p(2 N_{t-1}+p).
i.e.  Delta Gamma <= p(2 N_{t-1} + p)    [ "the ear pays for its vertices" ].

We TEST this on the extremal families (where it must be tight or fail) and on random
connected-B instances. The induction would need ALSO that removing the ear keeps B
2-connected or terminates at an odd cycle (base case Gamma = N^2). But the cleanest
test is the local inequality itself.
"""
from collections import deque
from itertools import combinations
import flag_engine as fe
import ear_invariant as EI

def bdist(n, adjB, src):
    d = [-1] * n; d[src] = 0; q = deque([src])
    while q:
        u = q.popleft()
        for w in adjB[u]:
            if d[w] < 0:
                d[w] = d[u] + 1; q.append(w)
    return d

def gamma_of(n, adjB, M):
    G = 0; ells = []
    for (u, v) in M:
        d = bdist(n, adjB, u)[v]
        if d < 0:
            ells.append(None)  # disconnected: ell infinite -> invariant breaks
        else:
            ells.append(d + 1); G += (d + 1) ** 2
    return G, ells

def is_2connected(n, adjB):
    # n>=3, connected, no cut vertex
    if n < 3:
        return False
    def conn(skip):
        start = next(x for x in range(n) if x != skip)
        seen = {start}; q = deque([start])
        while q:
            u = q.popleft()
            for w in adjB[u]:
                if w != skip and w not in seen:
                    seen.add(w); q.append(w)
        return len(seen) == n - (1 if skip is not None else 0)
    if not conn(None):
        return False
    for v in range(n):
        if not conn(v):
            return False
    return True

def find_ears_and_test(n, adjB, M, side):
    """Find every 'ear': a maximal path of degree-2 B-vertices, plus single-edge ears
    (chords). Remove it, recompute Gamma, test Delta Gamma <= p(2(N-p)+p)=p(2N-p)
    where here N=n, N_{t-1}=n-p. Return list of (p, dGamma, budget, ok)."""
    deg = [len(adjB[v]) for v in range(n)]
    results = []
    # ear = path of degree-2 vertices (internal), with endpoints of degree>=3
    visited = set()
    for v in range(n):
        if deg[v] == 2 and v not in visited:
            # walk the degree-2 chain
            chain = [v]; visited.add(v)
            # extend both directions through degree-2 vertices
            ends = []
            for start_nb in list(adjB[v]):
                prev = v; cur = start_nb
                path = []
                while deg[cur] == 2 and cur not in chain:
                    path.append(cur);
                    nxts = [w for w in adjB[cur] if w != prev]
                    if not nxts:
                        break
                    prev, cur = cur, nxts[0]
                ends.append((cur, path))
            internal = [v]
            for (endv, path) in ends:
                for x in path:
                    if x not in internal:
                        internal.append(x); visited.add(x)
            a = ends[0][0]; b = ends[1][0] if len(ends) > 1 else ends[0][0]
            p = len(internal)
            # remove internal vertices -> new graph
            keep = [x for x in range(n) if x not in internal]
            remap = {x: i for i, x in enumerate(keep)}
            nn = len(keep)
            nadjB = [set() for _ in range(nn)]
            for x in keep:
                for w in adjB[x]:
                    if w in remap:
                        nadjB[remap[x]].add(remap[w])
            nM = [(remap[u], remap[w]) for (u, w) in M if u in remap and w in remap]
            G_before, _ = gamma_of(n, adjB, M)
            G_after, ells_after = gamma_of(nn, nadjB, nM)
            if any(e is None for e in ells_after):
                results.append((p, 'DISCONNECTED-after-removal', None, None))
                continue
            dGamma = G_before - G_after  # how much Gamma DROPS by removing ear
            # induction direction: G_before(N) <= G_after(N-p) + budget?
            # We want G_before <= N^2 assuming G_after <= (N-p)^2. Need:
            #   G_before - G_after <= N^2 - (N-p)^2 = p(2N - p)
            budget = p * (2 * n - p)
            ok = dGamma <= budget + 1e-9
            results.append((p, dGamma, budget, ok))
    return results

if __name__ == "__main__":
    # Test on extremals first
    print("=== EXTREMALS: per-ear inequality Delta Gamma <= p(2N-p) ? ===")
    # C5[q]
    for q in [2, 3]:
        n, adj, side, idx = EI.C5_blowup(q)
        adjB = [set() for _ in range(n)]
        for u in range(n):
            for v in adj[u]:
                if v > u and side[u] != side[v]:
                    adjB[u].add(v); adjB[v].add(u)
        M = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
        res = find_ears_and_test(n, adjB, M, side)
        print(f" C5[{q}] N={n}: ears tested={len(res)}; sample={res[:4]}")
    # odd cycle
    for L in [7, 9]:
        n, adj, side = EI.odd_cycle(L)
        adjB = [set() for _ in range(n)]
        for u in range(n):
            for v in adj[u]:
                if v > u and side[u] != side[v]:
                    adjB[u].add(v); adjB[v].add(u)
        M = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
        res = find_ears_and_test(n, adjB, M, side)
        print(f" C{L} N={n}: ears={res[:4]}")
    # c5_paths theta
    n, adj, side, M, idx = EI.c5_paths(4)
    adjB = [set() for _ in range(n)]
    for u in range(n):
        for v in adj[u]:
            if v > u and side[u] != side[v]:
                adjB[u].add(v); adjB[v].add(u)
    res = find_ears_and_test(n, adjB, M, side)
    print(f" c5_paths N={n}: ears={res[:6]}")
    print("DONE")
