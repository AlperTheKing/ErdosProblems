import sys
sys.path.insert(0, '.')
exec(open('ref_sublemma_check.py').read().split('if __name__')[0])
import verify_bridge_QFC25 as vb

N, A = vb.gpt_k23()
adj = adjset(N, A)
E = [(u, v) for u in range(N) for v in adj[u] if v > u]
mc, _ = maxcut(N, adj)
print("K23-N13: max cut value =", mc, " total edges =", len(E), " tau =", len(E) - mc)

best_maxratio = 99.0
n_maxcuts = 0
example = None
for mask in range(1 << (N - 1)):
    side = [(mask >> u) & 1 for u in range(N)]
    c = sum(1 for (u, v) in E if side[u] != side[v])
    if c != mc:
        continue
    n_maxcuts += 1
    M = [(u, v) for (u, v) in E if side[u] == side[v]]
    adjB = [set() for _ in range(N)]
    for (u, v) in E:
        if side[u] != side[v]:
            adjB[u].add(v)
            adjB[v].add(u)
    lam = [0.0] * N
    ok = True
    for (u, v) in M:
        du = blayers(N, adjB, u)
        d = du[v]
        t = geoflow(N, adjB, u, v, d)
        if t is None:
            ok = False
            break
        for x in range(N):
            lam[x] += t[x]
    if not ok:
        continue
    deg = [len(adj[u]) for u in range(N)]
    mr = max((2 * lam[v] / deg[v] if deg[v] > 0 else 0) for v in range(N))
    if mr < best_maxratio:
        best_maxratio = mr
        example = (list(side), [round(2 * lam[v] / deg[v], 3) for v in range(N)])

print(f"#maximum cuts = {n_maxcuts}; BEST (min over all max-cuts) max(2lam/deg) = {best_maxratio:.4f}")
print("=> if > 1, sub-lemma 2lam<=deg FAILS for the uniform geodesic flow under EVERY maximum cut")
print("best-cut side + per-vertex ratios:", example)
