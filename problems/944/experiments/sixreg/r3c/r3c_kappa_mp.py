#!/usr/bin/env python3
# Parallel exact minimal-shore-axiom check (same reduction as r3c_kappa.py):
# min over ordered disjoint K-edge pairs (e1 in X, e2 in X^c) of
# maxflow_{K+}(e1 -> e2 ∪ {s}), early-exit at 8.  Violating X must have an
# edge on both sides (independent-side cases >= 12/14 by the stub bound,
# valid since every b(v) <= 1 in these instances).
import sys, json
from collections import deque
from multiprocessing import Pool

FN = None
DATA = None

def init(fn):
    global DATA
    with open(fn) as f:
        out = json.load(f)
    inst = out['inst']
    n, edges = inst['n'], [tuple(e) for e in inst['edges']]
    deg = [0] * n
    for a, b in edges:
        deg[a] += 1; deg[b] += 1
    defic = [(v, 6 - deg[v]) for v in range(n) if deg[v] < 6]
    assert all(bb == 1 for _, bb in defic), "stub bound needs b(v)<=1"
    DATA = (n, edges, defic)

def maxflow_pair(args):
    i = args
    n, edges, defic = DATA
    S_NODE, T_SUPER, SRC = n, n + 1, n + 2
    NN = n + 3
    a1, b1 = edges[i]
    best = 10 ** 9
    for j, (a2, b2) in enumerate(edges):
        if i == j or len({a1, b1, a2, b2}) < 4:
            continue
        # Dinic, early exit at 8
        g = [[] for _ in range(NN)]
        def add(a, b, cap, cap2=0):
            g[a].append([b, cap, len(g[b])])
            g[b].append([a, cap2, len(g[a]) - 1])
        for (a, b) in edges:
            add(a, b, 1, 1)
        for v, bb in defic:
            add(v, S_NODE, bb, bb)
        BIG = 1 << 20
        add(SRC, a1, BIG); add(SRC, b1, BIG)
        add(a2, T_SUPER, BIG); add(b2, T_SUPER, BIG)
        add(S_NODE, T_SUPER, BIG)
        flow = 0
        while flow < 8:
            lev = [-1] * NN; lev[SRC] = 0; dq = deque([SRC])
            while dq:
                x = dq.popleft()
                for e in g[x]:
                    if e[1] > 0 and lev[e[0]] < 0:
                        lev[e[0]] = lev[x] + 1; dq.append(e[0])
            if lev[T_SUPER] < 0:
                break
            it = [0] * NN
            stack = [(SRC, 1 << 30, False)]
            # iterative DFS augmentation, one path at a time
            def dfs(x, f):
                if x == T_SUPER:
                    return f
                while it[x] < len(g[x]):
                    e = g[x][it[x]]
                    if e[1] > 0 and lev[e[0]] == lev[x] + 1:
                        d = dfs(e[0], min(f, e[1]))
                        if d > 0:
                            e[1] -= d
                            g[e[0]][e[2]][1] += d
                            return d
                    it[x] += 1
                return 0
            while flow < 8:
                f = dfs(SRC, 1 << 30)
                if f == 0:
                    break
                flow += f
        if flow < best:
            best = flow
            if best < 8:
                return (best, edges[i], edges[j])
    return (best, edges[i], None)

def main():
    fn = sys.argv[1]
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    init(fn)
    n, edges, defic = DATA
    m = len(edges)
    print(f"n={n} m={m}: {m} tasks x ~{m} flows, {workers} workers", flush=True)
    best = 10 ** 9; argbest = None
    with Pool(workers, initializer=init, initargs=(fn,)) as pool:
        done = 0
        for res in pool.imap_unordered(maxflow_pair, range(m), chunksize=4):
            done += 1
            if res[0] < best:
                best, argbest = res[0], res[1:]
            if done % 100 == 0:
                print(f"  {done}/{m} tasks, min so far {best}", flush=True)
    print(f"DONE: min kappa (edge-both-sides cuts, capped at 8) = {best} {argbest}")
    print(f"==> minimal-shore axiom kappa(X)>=8: {'HOLDS (EXACT)' if best >= 8 else 'FAILS'}")

if __name__ == "__main__":
    main()
