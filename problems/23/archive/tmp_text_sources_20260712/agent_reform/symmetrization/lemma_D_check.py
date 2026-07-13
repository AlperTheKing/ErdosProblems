# symmetrization lens -- Lemma D (domination absorption) exhaustive exact check, n<=6
# Lemma D: H triangle-free, u,v nonadjacent, N(v) subseteq N(u) => absorbing v into u
# (delete v, w_u += w_v) never decreases beta. Also: edge-addition monotonicity and
# twin-split invariance spot batteries. All arithmetic is exact (integers).
from itertools import combinations
import random

def beta_w(n, edges, w):
    best = None
    for m in range(1 << (n - 1)):
        c = [0] + [(m >> i) & 1 for i in range(n - 1)]
        mono = 0
        for (u, v) in edges:
            if c[u] == c[v]:
                mono += w[u] * w[v]
        if best is None or mono < best:
            best = mono
    return best

def run(n, weight_sets):
    pairs = list(combinations(range(n), 2))
    ne = len(pairs)
    tested = 0
    violations = 0
    graphs = 0
    for gm in range(1 << ne):
        adj = [0] * n
        edges = []
        ok = True
        for i in range(ne):
            if (gm >> i) & 1:
                u, v = pairs[i]
                if adj[u] & adj[v]:
                    ok = False
                    break
                adj[u] |= 1 << v
                adj[v] |= 1 << u
                edges.append((u, v))
        if not ok:
            continue
        # nontrivial dominated nonadjacent pairs: N(v) nonempty, N(v) subseteq N(u), u!=v, u,v nonadjacent
        doms = [(u, v) for u in range(n) for v in range(n)
                if u != v and not (adj[u] >> v) & 1 and adj[v] and not (adj[v] & ~adj[u])]
        if not doms:
            continue
        graphs += 1
        for w in weight_sets:
            b0 = beta_w(n, edges, w)
            for (u, v) in doms:
                w2 = list(w)
                w2[u] += w2[v]
                w2[v] = 0
                e2 = [e for e in edges if v not in e]
                b1 = beta_w(n, e2, w2)
                tested += 1
                if b1 < b0:
                    violations += 1
                    print("VIOLATION", edges, u, v, w, b0, b1, flush=True)
    print("n=%d: TF-graphs-with-nontrivial-domination=%d, absorption instances=%d, violations=%d"
          % (n, graphs, tested, violations), flush=True)
    return violations

v5 = run(5, [(1, 1, 1, 1, 1), (1, 2, 3, 4, 5), (3, 1, 4, 1, 5), (2, 7, 1, 8, 2)])
v6 = run(6, [(1, 1, 1, 1, 1, 1), (1, 2, 3, 4, 5, 6), (3, 1, 4, 1, 5, 9), (2, 7, 1, 8, 2, 8)])

# --- edge-addition monotonicity + twin-split invariance, random n=6 battery ---
random.seed(5)
pairs = list(combinations(range(6), 2))
add_bad = 0
split_bad = 0
trials = 0
while trials < 400:
    gm = random.randrange(1 << 15)
    edges = [pairs[i] for i in range(15) if (gm >> i) & 1]
    adj = [0] * 6
    tri = False
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    for u, v in edges:
        if adj[u] & adj[v]:
            tri = True
            break
    if tri:
        continue
    trials += 1
    w = tuple(random.randint(1, 9) for _ in range(6))
    b0 = beta_w(6, edges, w)
    for (u, v) in pairs:  # add one TF-safe edge if any
        if not (adj[u] >> v) & 1 and not (adj[u] & adj[v]):
            b1 = beta_w(6, edges + [(u, v)], w)
            if b1 < b0:
                add_bad += 1
            break
    if w[0] >= 2:  # split vertex 0 into twins with weights w0-1 and 1
        e2 = edges + [(6, x) for x in range(6) if (adj[0] >> x) & 1]
        w2 = list(w) + [1]
        w2[0] -= 1
        b2 = beta_w(7, e2, tuple(w2))
        if b2 != b0:
            split_bad += 1
print("edge-add monotonicity violations: %d / %d trials; twin-split invariance violations: %d"
      % (add_bad, trials, split_bad), flush=True)
print("LEMMA-D BATTERY DONE (violations total = %d)" % (v5 + v6 + add_bad + split_bad), flush=True)
