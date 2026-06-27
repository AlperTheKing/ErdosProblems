"""The flagged untested regime: MULTIPLE odd cycles of DIFFERENT lengths sharing
vertices, so a single hub vertex accrues E(w) (many bad-edge endpoints) AND I(w)
(interior betweenness) simultaneously. 'Book of odd cycles' + random odd-cycle gluings.
Check uniform-routing T<=K over ALL max cuts."""
import numpy as np, random
from mycielskian_check import all_shortest_geos, gamma_of, Bconnected, edges_of, maxcut_value

def load_uniform(N, adj, side, M):
    T = np.zeros(N)
    for (u, v) in M:
        geos = all_shortest_geos(N, adj, side, u, v)
        if not geos:
            return None
        w = 1.0 / len(geos); h = len(geos[0])
        for P in geos:
            for x in P:
                T[x] += h * w
    return T

def all_cuts(n, adj, cap=50000):
    E = edges_of(adj); mc = maxcut_value(n, E); out = []; cnt = 0
    for mask in range(1 << (n - 1)):
        c = sum(1 for (u, v) in E if ((mask >> u) & 1) != ((mask >> v) & 1))
        if c != mc:
            continue
        side = [(mask >> u) & 1 for u in range(n)]
        if not Bconnected(n, adj, side):
            continue
        G, M = gamma_of(n, adj, side)
        if G is None or not M:
            continue
        out.append((side, G, M)); cnt += 1
        if cnt >= cap:
            break
    return out

def is_trifree(n, adj):
    for u in range(n):
        for v in adj[u]:
            if v > u and (adj[u] & adj[v]):
                return False
    return True

def check(n, adj, name):
    if not is_trifree(n, adj):
        return None
    worst = -1e9; wc = None
    for side, G, M in all_cuts(n, adj):
        T = load_uniform(n, adj, side, M)
        if T is None:
            continue
        K = n + (n * n - G); gap = T.max() - K
        if gap > worst:
            worst = gap; wc = (G, K, T.max())
    if wc is None:
        return None
    if worst > 1e-9:
        print("  *** %s N=%d VIOLATION gap=%.4f %s" % (name, n, worst, wc))
    return worst

def book(lengths):
    adj = [set(), set()]
    adj[0].add(1); adj[1].add(0)
    for L in lengths:
        prev = 0
        for _ in range(L - 1):
            adj.append(set()); cur = len(adj) - 1
            adj[prev].add(cur); adj[cur].add(prev); prev = cur
        adj[prev].add(1); adj[1].add(prev)
    return len(adj), adj

print("=== book of odd cycles sharing one edge ===")
for lengths in [[5, 5], [5, 7], [5, 5, 5], [5, 7, 9], [7, 7], [5, 5, 7], [7, 9]]:
    n, adj = book(lengths)
    if n > 16:
        print("  book%s N=%d: too big, skip" % (lengths, n)); continue
    w = check(n, adj, "book%s" % lengths)
    print("  book%s N=%d worst gap=%s" % (lengths, n, w))

print("=== random odd-cycle gluings ===")
random.seed(7)
worst_overall = -1e9; nfail = 0; ntested = 0
for trial in range(4000):
    k = random.randint(2, 3)
    L0 = random.choice([5, 7, 9])
    adj = [set() for _ in range(L0)]
    for i in range(L0):
        adj[i].add((i + 1) % L0); adj[(i + 1) % L0].add(i)
    for _ in range(k - 1):
        L = random.choice([5, 7, 9])
        base = len(adj); share = random.randrange(len(adj))
        new = [share] + [base + i for i in range(L - 1)]
        for i in range(L - 1):
            adj.append(set())
        for i in range(L):
            a = new[i]; b = new[(i + 1) % L]; adj[a].add(b); adj[b].add(a)
    n = len(adj)
    if n > 15:
        continue
    if not is_trifree(n, adj):
        continue
    w = check(n, adj, "rand%d" % trial)
    if w is None:
        continue
    ntested += 1
    if w > worst_overall:
        worst_overall = w
    if w > 1e-9:
        nfail += 1
print("random gluings: tested=%d worst gap=%.6f violations=%d" % (ntested, worst_overall, nfail))
