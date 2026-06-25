"""Test a VERTEX-DELETION induction for Connected-B Gamma Lemma (the honest replacement
for ear induction). For each connected-B instance, ask: does there exist a vertex x whose
removal (a) keeps the cut a MAXIMUM cut of G-x with B still the cut-graph, and (b) satisfies
   Gamma(G) <= Gamma(G-x) + (2N-1)   ?
Equivalently the per-vertex drop Gamma(G)-Gamma(G-x) >= -(2N-1)... we need a vertex with
   Gamma(G) - Gamma(G-x) <= 2N-1.
We do NOT require G-x to stay connected-B; we just measure the BEST vertex's drop to see if
the inductive step is plausible, and CRUCIALLY whether removing the min-drop vertex can
INCREASE Gamma (drop<0), which would break monotone induction.

The decisive question for the strategy: across all connected-B instances, what is
   min_x [ Gamma(G) - Gamma(G-x) ]   and is it <= 2N-1 always?
If yes for a vertex that also preserves the inductive hypotheses, a clean induction exists.
We also flag the WORST case (the instance where even the best vertex has the largest drop).
"""
from collections import deque
import flag_engine as fe

def adjset(n, A):
    return [set(v for v in range(n) if (A[u] >> v) & 1) for u in range(n)]

def all_maxcuts(n, adj):
    best = -1; cuts = []
    for mask in range(1 << (n - 1)):
        side = [(mask >> u) & 1 for u in range(n)]
        c = sum(1 for u in range(n) for v in adj[u] if v > u and side[u] != side[v])
        if c > best:
            best = c; cuts = [side]
        elif c == best:
            cuts.append(side)
    return best, cuts

def bdist(n, adjB, src):
    d = [-1] * n; d[src] = 0; q = deque([src])
    while q:
        u = q.popleft()
        for w in adjB[u]:
            if d[w] < 0:
                d[w] = d[u] + 1; q.append(w)
    return d

def gamma_with_side(n, adj, side):
    """Gamma using the GIVEN side as the cut. Returns (Gamma, ok) where ok=False if some
    bad edge has d_B<4 or odd (struct fail) or disconnected."""
    adjB = [set() for _ in range(n)]
    for u in range(n):
        for v in adj[u]:
            if v > u and side[u] != side[v]:
                adjB[u].add(v); adjB[v].add(u)
    M = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
    G = 0
    for (u, v) in M:
        d = bdist(n, adjB, u)[v]
        if d < 0:
            return None, False
        G += (d + 1) ** 2
    return G, True

def maxcut_gamma(n, adj):
    """Min Gamma over all max cuts (the value the lemma bounds)."""
    mc, cuts = all_maxcuts(n, adj)
    best = None
    for side in cuts:
        G, ok = gamma_with_side(n, adj, side)
        if G is not None and (best is None or G < best):
            best = G
    return best, mc

def connectedB_instances(N):
    states = fe.enumerate_graphs(N, triangle_free=True)
    out = []
    for (n, A) in states:
        adj = adjset(n, A)
        E = [(u, v) for u in range(n) for v in adj[u] if v > u]
        if not E:
            continue
        mc, cuts = all_maxcuts(n, adj)
        for side in cuts[:1]:
            adjB = [set() for _ in range(n)]
            for (u, v) in E:
                if side[u] != side[v]:
                    adjB[u].add(v); adjB[v].add(u)
            seen = set([0]); q = deque([0])
            while q:
                u = q.popleft()
                for w in adjB[u]:
                    if w not in seen:
                        seen.add(w); q.append(w)
            if len(seen) != n:
                continue
            M = [(u, v) for (u, v) in E if side[u] == side[v]]
            if not M:
                continue
            ok = True
            for (u, v) in M:
                d = bdist(n, adjB, u)[v]
                if d < 4 or d % 2:
                    ok = False; break
            if not ok:
                continue
            out.append((n, adj, side))
    return out

def remove_vertex_adj(n, adj, x):
    keep = [v for v in range(n) if v != x]
    remap = {v: i for i, v in enumerate(keep)}
    nn = len(keep)
    nadj = [set() for _ in range(nn)]
    for v in keep:
        for w in adj[v]:
            if w != x:
                nadj[remap[v]].add(remap[w])
    return nn, nadj, remap

if __name__ == "__main__":
    for N in [7, 8, 9]:
        inst = connectedB_instances(N)
        worst_bestdrop = -10**9; worst_case = None
        n_negdrop = 0  # cases where best vertex still INCREASES Gamma (drop<0) -> bad for induction
        for (n, adj, side) in inst:
            G0, ok = gamma_with_side(n, adj, side)
            if not ok:
                continue
            # for each vertex, drop using the RECOMPUTED max-cut Gamma of G-x
            best_drop = None
            for x in range(n):
                nn, nadj, remap = remove_vertex_adj(n, adj, x)
                G1, mc1 = maxcut_gamma(nn, nadj)
                if G1 is None:
                    continue
                drop = G0 - G1   # we want this <= 2N-1 for induction Gamma(N)<=Gamma(N-1)+(2N-1)
                if best_drop is None or drop < best_drop:
                    best_drop = drop
            if best_drop is None:
                continue
            if best_drop < 0:
                n_negdrop += 1
            if best_drop > worst_bestdrop:
                worst_bestdrop = best_drop; worst_case = (n, G0)
        budget = 2 * N - 1
        print(f"N={N}: instances={len(inst)} | max over instances of (best-vertex drop) = {worst_bestdrop} "
              f"| budget 2N-1 = {budget} | induction-step holds for ALL: {worst_bestdrop <= budget} "
              f"| #instances where best vertex still raises Gamma: {n_negdrop}")
    print("DONE")
