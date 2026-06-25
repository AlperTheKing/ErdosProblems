"""TEST the factored bound:  (max_ell) * (sum_ell) <= N^2  over all connected-B instances.

If TRUE, it implies Gamma = sum ell^2 <= max_ell * sum_ell <= N^2 (since ell<=max_ell),
and it is tight on BOTH extremals (odd cycle: max=sum=N; C5[q]: max=5, sum=N^2/5).
This is a STRICTLY STRONGER, but possibly cleaner, inequality. Falsify it numerically.
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

def connectedB_ells(N):
    states = fe.enumerate_graphs(N, triangle_free=True)
    out = []
    for (n, A) in states:
        adj = adjset(n, A)
        E = [(u, v) for u in range(n) for v in adj[u] if v > u]
        if not E:
            continue
        mc, cuts = all_maxcuts(n, adj)
        # choose the max cut MINIMIZING Gamma (lemma uses 'some max cut')
        best = None
        for side in cuts:
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
            ok = True; ells = []
            for (u, v) in M:
                d = bdist(n, adjB, u)[v]
                if d < 4 or d % 2:
                    ok = False; break
                ells.append(d + 1)
            if not ok:
                continue
            G = sum(e * e for e in ells)
            if best is None or G < best[0]:
                best = (G, ells)
        if best is not None:
            out.append((n, best[1]))
    return out

if __name__ == "__main__":
    for N in [7, 8, 9, 10, 11]:
        inst = connectedB_ells(N)
        viol = 0; worst = 0.0; worstdat = None
        for (n, ells) in inst:
            mx = max(ells); S = sum(ells)
            ratio = mx * S / (n * n)
            if ratio > 1 + 1e-9:
                viol += 1
            if ratio > worst:
                worst = ratio; worstdat = (n, sorted(ells), mx, S)
        print(f"N={N}: connectedB inst={len(inst)} | max (max_ell*sum_ell)/N^2 = {worst:.4f} "
              f"| VIOLATIONS(>1): {viol} | worst={worstdat}")
    print("DONE")
