# EXHAUSTIVE check of Lemma W' for n = 5, 6, 7 over ALL labeled graphs
# (no isolated vertices; triangle-free; non-bipartite):
#   min over S in im(A) u im(A+I) of uncut(S)  <=  floor(n^2/25)
# plus a random sample at n = 8.  All integer arithmetic.
import sys, random
from itertools import combinations
from lib import edges_to_adj, is_bipartite, _span_reduce

def run_exhaustive(n, bound):
    pairs = list(combinations(range(n), 2))
    P = len(pairs)
    tri_masks = []
    pidx = {p: i for i, p in enumerate(pairs)}
    for a, b, c in combinations(range(n), 3):
        m = (1 << pidx[(a, b)]) | (1 << pidx[(b, c)]) | (1 << pidx[(a, c)])
        tri_masks.append(m)
    total = tested = fails = 0
    worst = -1
    for mask in range(1, 1 << P):
        ok_tf = True
        for t in tri_masks:
            if mask & t == t:
                ok_tf = False
                break
        if not ok_tf:
            continue
        edges = [pairs[i] for i in range(P) if (mask >> i) & 1]
        deg = [0] * n
        for u, v in edges:
            deg[u] += 1; deg[v] += 1
        if min(deg) == 0:
            continue  # covered at smaller n
        total += 1
        if is_bipartite(n, edges):
            continue
        tested += 1
        adj = edges_to_adj(n, edges)
        closed = [adj[u] ^ (1 << u) for u in range(n)]
        found = False
        # early candidates: single open/closed neighborhoods
        for S in adj + closed:
            if sum(1 for u, v in edges if ((S >> u) & 1) == ((S >> v) & 1)) <= bound:
                found = True
                break
        if not found:
            for cols in (adj, closed):
                bs = _span_reduce(cols)
                span = [0]
                for b in bs:
                    span += [x ^ b for x in span]
                for S in span:
                    if sum(1 for u, v in edges if ((S >> u) & 1) == ((S >> v) & 1)) <= bound:
                        found = True
                        break
                if found:
                    break
        if not found:
            fails += 1
            print(f"  FAIL n={n}: edges={edges}")
    print(f"n={n}: no-isolated triangle-free graphs={total}, non-bipartite tested={tested}, "
          f"bound=floor(n^2/25)={bound}, FAILURES={fails}")
    sys.stdout.flush()
    return fails

def run_sample8(count, seed=0):
    n = 8
    bound = 64 // 25
    pairs = list(combinations(range(n), 2))
    P = len(pairs)
    pidx = {p: i for i, p in enumerate(pairs)}
    tri_masks = []
    for a, b, c in combinations(range(n), 3):
        tri_masks.append((1 << pidx[(a, b)]) | (1 << pidx[(b, c)]) | (1 << pidx[(a, c)]))
    rng = random.Random(seed)
    tested = fails = 0
    it = 0
    while tested < count and it < count * 400:
        it += 1
        mask = rng.getrandbits(P)
        skip = False
        for t in tri_masks:
            if mask & t == t:
                skip = True
                break
        if skip:
            continue
        edges = [pairs[i] for i in range(P) if (mask >> i) & 1]
        deg = [0] * n
        for u, v in edges:
            deg[u] += 1; deg[v] += 1
        if min(deg) == 0 or is_bipartite(n, edges):
            continue
        tested += 1
        adj = edges_to_adj(n, edges)
        closed = [adj[u] ^ (1 << u) for u in range(n)]
        found = False
        for cols in (adj, closed):
            bs = _span_reduce(cols)
            span = [0]
            for b in bs:
                span += [x ^ b for x in span]
            for S in span:
                if sum(1 for u, v in edges if ((S >> u) & 1) == ((S >> v) & 1)) <= bound:
                    found = True
                    break
            if found:
                break
        if not found:
            fails += 1
            print(f"  FAIL n=8: edges={edges}")
    print(f"n=8 random sample: tested {tested} non-bipartite triangle-free graphs, bound={bound}, FAILURES={fails}")
    return fails

if __name__ == "__main__":
    F = 0
    F += run_exhaustive(5, 25 // 25)
    F += run_exhaustive(6, 36 // 25)
    F += run_exhaustive(7, 49 // 25)
    F += run_sample8(20000, seed=42)
    print("TOTAL FAILURES:", F)
