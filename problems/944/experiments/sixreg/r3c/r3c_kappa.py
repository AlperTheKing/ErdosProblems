#!/usr/bin/env python3
# EXACT minimal-shore-axiom check for an r3c instance:
#   for every X with 2 <= |X| <= n-2:  kappa(X) := 6|X| - 2 e(K[X]) >= 8
#   (equivalently e(K[X]) <= 3|X| - 4).
# Reduction (proved in the writeup):
#   kappa(X) = cut_{K+}(X) where K+ adds a stub-vertex s joined to each
#   deficient v with multiplicity b(v) = 6 - deg(v), and s is placed in X^c.
#   If X is independent, kappa(X) = 6|X| >= 12.  If X^c (within K) is
#   independent, kappa(X) = 6|X^c| + 6 - 2*stubs(X^c) >= 6*2 + 6 - 12 = 6...
#   sharper: stubs(X^c) <= |X^c| here (b(v)<=1), so kappa(X) >= 6*2+6-2*2 = 14.
#   Hence any violating X (kappa<8) has a K-edge inside X AND inside X^c.
#   Therefore  min kappa over the range  =  min over ordered disjoint edge
#   pairs (e1, e2) of maxflow_{K+}(source=e1, sink=e2 ∪ {s}), all caps 1
#   (stub edges cap b(v)).  We early-exit each flow at value 8.
import sys, json
from collections import deque

def load(fn):
    with open(fn) as f:
        return json.load(f)

class Dinic:
    def __init__(self, n):
        self.n = n; self.g = [[] for _ in range(n)]
    def add(self, a, b, cap, cap2=0):
        self.g[a].append([b, cap, len(self.g[b])])
        self.g[b].append([a, cap2, len(self.g[a]) - 1])
    def maxflow(self, s, t, limit):
        flow = 0
        while flow < limit:
            # BFS level graph
            lev = [-1] * self.n; lev[s] = 0; dq = deque([s])
            while dq:
                x = dq.popleft()
                for e in self.g[x]:
                    if e[1] > 0 and lev[e[0]] < 0:
                        lev[e[0]] = lev[x] + 1; dq.append(e[0])
            if lev[t] < 0:
                return flow
            it = [0] * self.n
            def dfs(x, f):
                if x == t:
                    return f
                while it[x] < len(self.g[x]):
                    e = self.g[x][it[x]]
                    if e[1] > 0 and lev[e[0]] == lev[x] + 1:
                        d = dfs(e[0], min(f, e[1]))
                        if d > 0:
                            e[1] -= d
                            self.g[e[0]][e[2]][1] += d
                            return d
                    it[x] += 1
                return 0
            while flow < limit:
                f = dfs(s, 1 << 30)
                if f == 0:
                    break
                flow += f
        return flow

def main(fn, target=8):
    out = load(fn)
    inst = out['inst']
    n, edges = inst['n'], [tuple(e) for e in inst['edges']]
    deg = [0] * n
    for a, b in edges:
        deg[a] += 1; deg[b] += 1
    defic = [(v, 6 - deg[v]) for v in range(n) if deg[v] < 6]
    S_NODE, T_SUPER, SRC = n, n + 1, n + 2   # s, super-sink, super-source
    NN = n + 3
    best = 10 ** 9; arg = None
    m = len(edges)
    print(f"n={n} edges={m} -> ordered disjoint edge pairs ...")
    cnt = 0
    for i, (a1, b1) in enumerate(edges):
        for j, (a2, b2) in enumerate(edges):
            if i == j or len({a1, b1, a2, b2}) < 4:
                continue
            D = Dinic(NN)
            for (a, b) in edges:
                D.add(a, b, 1, 1)
            for v, bb in defic:
                D.add(v, S_NODE, bb, bb)
            BIG = 1 << 20
            D.add(SRC, a1, BIG); D.add(SRC, b1, BIG)
            D.add(a2, T_SUPER, BIG); D.add(b2, T_SUPER, BIG)
            D.add(S_NODE, T_SUPER, BIG)
            f = D.maxflow(SRC, T_SUPER, target)
            cnt += 1
            if f < best:
                best = f; arg = ((a1, b1), (a2, b2))
                print(f"  new min flow {f} at e1={arg[0]} e2={arg[1]}")
            if f < target:
                pass
        if (i + 1) % 20 == 0:
            print(f"  ... e1 {i+1}/{m}, flows={cnt}, min so far={best}", flush=True)
    print(f"DONE: min kappa over all X with an edge on both sides "
          f"(capped at {target}) = {best}")
    print(f"Independent-side cases are >= 12 (X) / >= 14 (X^c) by the stub bound.")
    print(f"==> minimal-shore axiom kappa(X) >= 8 for 2<=|X|<=n-2: "
          f"{'HOLDS (EXACT)' if best >= target else 'FAILS at ' + str(arg)}")

if __name__ == "__main__":
    main(sys.argv[1])
