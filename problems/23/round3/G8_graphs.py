"""G8: Andrasfai graphs And(k) = circulant on Z_{3k-1}, connection set {i : i = 1 mod 3}.

Verify the definition, basic invariants, and exact bip = |E| - maxcut by brute force.
All arithmetic integer/exact.
"""
import itertools, sys
from fractions import Fraction


def andrasfai(k):
    n = 3 * k - 1
    conn = sorted(i for i in range(1, n) if i % 3 == 1)
    adj = [[False] * n for _ in range(n)]
    edges = []
    for v in range(n):
        for c in conn:
            u = (v + c) % n
            if not adj[v][u]:
                adj[v][u] = adj[u][v] = True
    for u in range(n):
        for v in range(u + 1, n):
            if adj[u][v]:
                edges.append((u, v))
    return n, conn, adj, edges


def triangle_free(n, adj):
    for a in range(n):
        for b in range(a + 1, n):
            if not adj[a][b]:
                continue
            for c in range(b + 1, n):
                if adj[a][c] and adj[b][c]:
                    return False, (a, b, c)
    return True, None


def odd_girth(n, adj):
    # BFS-based shortest odd cycle through each vertex
    best = None
    for s in range(n):
        # state (v, parity)
        dist = {(s, 0): 0}
        from collections import deque
        q = deque([(s, 0)])
        while q:
            v, p = q.popleft()
            d = dist[(v, p)]
            for u in range(n):
                if not adj[v][u]:
                    continue
                st = (u, 1 - p)
                if st not in dist:
                    dist[st] = d + 1
                    q.append(st)
        if (s, 1) in dist:
            L = dist[(s, 1)]
            if best is None or L < best:
                best = L
    return best


def independence_number(n, adj):
    best = 0
    bestset = None
    # simple branch and bound
    order = list(range(n))

    def rec(cand, cur):
        nonlocal best, bestset
        if len(cur) + len(cand) <= best:
            return
        if not cand:
            if len(cur) > best:
                best = len(cur)
                bestset = list(cur)
            return
        v = cand[0]
        # include v
        rec([u for u in cand[1:] if not adj[v][u]], cur + [v])
        # exclude v
        rec(cand[1:], cur)

    rec(order, [])
    return best, bestset


def maxcut_bip(n, edges):
    """Exact: returns (maxcut, bip, one optimal cut as frozenset)."""
    m = len(edges)
    best = -1
    bestS = None
    for mask in range(1 << (n - 1)):  # fix vertex 0 on side 0
        cut = 0
        for (u, v) in edges:
            bu = (mask >> (u - 1)) & 1 if u > 0 else 0
            bv = (mask >> (v - 1)) & 1 if v > 0 else 0
            if bu != bv:
                cut += 1
        if cut > best:
            best = cut
            bestS = mask
    S = frozenset([v for v in range(1, n) if (bestS >> (v - 1)) & 1])
    return best, m - best, S


if __name__ == "__main__":
    for k in range(2, 8):
        n, conn, adj, edges = andrasfai(k)
        tf, wit = triangle_free(n, adj)
        og = odd_girth(n, adj)
        alpha, aset = independence_number(n, adj)
        deg = sum(adj[0])
        line = f"And({k}): n={n} conn={conn} deg={deg} |E|={len(edges)} trianglefree={tf} oddgirth={og} alpha={alpha}"
        if n <= 20:
            mc, bp, S = maxcut_bip(n, edges)
            line += f" maxcut={mc} bip={bp} bip/n^2={Fraction(bp, n*n)} vs 1/25={Fraction(1,25)} cut={sorted(S)}"
        print(line)
        sys.stdout.flush()
