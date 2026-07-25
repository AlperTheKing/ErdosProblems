"""Decode the known exact extremal graphs and expose their construction."""
import sys, itertools
from h2_lib import *

EXTREMAL = {
 12: ["K?ABBBwerwBw", "K?BD@g]Qvo^?"],
 13: ["L??ED@_~?~^_Fw", "L??EDB_~?~^_Fw", "L??EFB_~FwB{Fw", "L??FFB_~?~^_Fw",
      "L?`DAboU`w@{hS", "L?`DAboUdIF_Bo", "L?`DE`gl@YJODg"],
 14: ["M?AE@bH{AYN_LgBs?"],
}


def twin_classes(n, adj):
    """Vertices u~v iff N(u)==N(v) (false twins => same blow-up part)."""
    seen = {}
    for v in range(n):
        seen.setdefault(adj[v], []).append(v)
    return sorted(seen.values(), key=lambda c: (-len(c), c[0]))


def quotient(n, adj, classes):
    """Quotient graph on twin classes."""
    idx = {}
    for k, c in enumerate(classes):
        for v in c:
            idx[v] = k
    K = len(classes)
    qedges = set()
    for i in range(n):
        for j in range(i + 1, n):
            if (adj[i] >> j) & 1:
                a, b = idx[i], idx[j]
                assert a != b
                qedges.add((min(a, b), max(a, b)))
    return K, sorted(qedges), [len(c) for c in classes]


def indep_number(n, adj):
    best = 0
    # simple branch and bound
    def rec(cand, cur):
        nonlocal best
        if cur + bin(cand).count("1") <= best:
            return
        if cand == 0:
            best = max(best, cur)
            return
        v = (cand & -cand).bit_length() - 1
        # include v
        rec(cand & ~(1 << v) & ~adj[v], cur + 1)
        # exclude v
        rec(cand & ~(1 << v), cur)
    rec((1 << n) - 1, 0)
    return best


def hom_to_C5(n, adj):
    """Backtracking search for homomorphism to C5."""
    col = [-1] * n
    order = sorted(range(n), key=lambda v: -bin(adj[v]).count("1"))
    def ok(v, c):
        for u in range(n):
            if (adj[v] >> u) & 1 and col[u] >= 0:
                if (col[u] - c) % 5 not in (1, 4):
                    return False
        return True
    def rec(k):
        if k == len(order):
            return True
        v = order[k]
        rng = range(5) if k > 0 else [0]
        for c in rng:
            if ok(v, c):
                col[v] = c
                if rec(k + 1):
                    return True
                col[v] = -1
        return False
    return (col[:] if rec(0) else None)


def hom_to_base(n, adj, bn, bedges):
    """Backtracking search for homomorphism G -> base graph."""
    badj = edges_to_adj(bn, bedges)
    col = [-1] * n
    order = sorted(range(n), key=lambda v: -bin(adj[v]).count("1"))
    def ok(v, c):
        for u in range(n):
            if (adj[v] >> u) & 1 and col[u] >= 0:
                if not ((badj[c] >> col[u]) & 1):
                    return False
        return True
    def rec(k):
        if k == len(order):
            return True
        v = order[k]
        for c in range(bn):
            if ok(v, c):
                col[v] = c
                if rec(k + 1):
                    return True
                col[v] = -1
        return False
    return (col[:] if rec(0) else None)


def odd_girth(n, adj):
    from collections import deque
    best = 10 ** 9
    for s in range(n):
        dist = [-1] * n
        dist[s] = 0
        q = deque([s])
        while q:
            v = q.popleft()
            for u in range(n):
                if (adj[v] >> u) & 1:
                    if dist[u] < 0:
                        dist[u] = dist[v] + 1
                        q.append(u)
                    elif (dist[u] - dist[v]) % 2 == 0:
                        best = min(best, dist[u] + dist[v] + 1)
    return best


def maxcut_witness(n, adj):
    """Exact maxcut plus one optimal side set."""
    deg = [bin(adj[i]).count("1") for i in range(n)]
    S = 1
    cut = deg[0]
    best, bestS = cut, S
    for k in range(1, 1 << (n - 1)):
        v = ((k & -k).bit_length() - 1) + 1
        bit = 1 << v
        a = bin(adj[v] & S).count("1")
        if S & bit:
            cut += 2 * a - deg[v]; S &= ~bit
        else:
            cut += deg[v] - 2 * a; S |= bit
        if cut > best:
            best, bestS = cut, S
    return best, bestS


if __name__ == "__main__":
    for N in sorted(EXTREMAL):
        for g in EXTREMAL[N]:
            n, adj = g6_decode(g)
            assert n == N
            m = num_edges(n, adj)
            tf = is_triangle_free(n, adj)
            mc, S = maxcut_witness(n, adj)
            b = m - mc
            cls = twin_classes(n, adj)
            K, qe, sizes = quotient(n, adj, cls)
            print("=" * 78)
            print(f"g6={g}  N={N} m={m} triangle_free={tf} maxcut={mc} bip={b}")
            print(f"  deg seq  = {sorted((bin(adj[i]).count('1') for i in range(n)), reverse=True)}")
            print(f"  alpha    = {indep_number(n, adj)}   odd girth = {odd_girth(n, adj)}")
            print(f"  twin classes ({len(cls)}): sizes {sizes}  -> {cls}")
            print(f"  quotient: {K} vtx, {len(qe)} edges: {qe}")
            h = hom_to_C5(n, adj)
            print(f"  hom->C5: {h}")
            # blow-up-of-quotient check: is G the full blow-up of its twin quotient?
            Nq, aq, offs = blowup(K, qe, sizes)
            print(f"  edges of full blow-up of quotient = {num_edges(Nq, aq)}  (G has {m})")
            print(f"  edge list = {adj_to_edges(n, adj)}")
            print(f"  a maxcut side = {[v for v in range(n) if (S>>v)&1]}")
