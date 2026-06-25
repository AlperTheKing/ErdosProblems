"""Ear-decomposition probe for the Connected-B Gamma Lemma (Strategy B).
Characterize the worst connected-B instances and test candidate per-vertex weight
schemes that AM-GM to N^2 globally.
"""
import sys
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
            ells = []
            ok = True
            for (u, v) in M:
                d = bdist(n, adjB, u)[v]
                if d < 4 or d % 2:
                    ok = False; break
                ells.append(d + 1)
            if not ok:
                continue
            out.append((n, adjB, M, ells, side, adj))
    return out

if __name__ == "__main__":
    Ns = [int(x) for x in sys.argv[1:]]
    if not Ns:
        Ns = [8, 9, 10]
    for N in Ns:
        inst = connectedB_instances(N)
        ratios = sorted((sum(e * e for e in x[3]) / (N * N), x) for x in inst)
        worst = ratios[-1][0] if ratios else 0
        print(f"N={N}: connected-B instances={len(inst)}, worst Gamma/N^2={worst:.4f}")
        for r, (n, adjB, M, ells, side, adj) in ratios[-6:]:
            degB = sorted(len(adjB[v]) for v in range(n))
            print(f"   Gamma/N^2={r:.4f} m={len(M)} ells={sorted(ells)} degB={degB}")
    print("DONE")
