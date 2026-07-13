# containers/entropy lens -- exact verification battery for Erdos #23 reformulation
# All decision claims use exact int/Fraction arithmetic. Float appears ONLY in search
# heuristics whose outputs are then re-verified exactly or labeled "indicative".
import itertools, random
from fractions import Fraction as F
random.seed(23)

def maxcut_exact(n, edges):
    best = 0
    for s in range(1 << (n - 1)):
        c = 0
        for (u, v) in edges:
            c += ((s >> u) & 1) ^ ((s >> v) & 1)
        if c > best:
            best = c
    return best

def is_triangle_free(n, edges):
    adj = [0] * n
    for (u, v) in edges:
        adj[u] |= 1 << v; adj[v] |= 1 << u
    return all((adj[u] & adj[v]) == 0 for (u, v) in edges)

def degrees(n, edges):
    d = [0] * n
    for (u, v) in edges: d[u] += 1; d[v] += 1
    return d

def hom_count_to_C5(n, edges, cap=1):
    # count homomorphisms G -> C5 (up to cap); C5: a~b iff (a-b)%5 in {1,4}
    adjl = [[] for _ in range(n)]
    for (u, v) in edges: adjl[u].append(v); adjl[v].append(u)
    order = []
    seen = [False] * n
    for root in range(n):
        if seen[root]: continue
        seen[root] = True; stack = [root]
        while stack:
            x = stack.pop(); order.append(x)
            for y in adjl[x]:
                if not seen[y]: seen[y] = True; stack.append(y)
    pos = {v: i for i, v in enumerate(order)}
    lab = [-1] * n
    cnt = 0
    def bt(i):
        nonlocal cnt
        if cnt >= cap: return
        if i == n: cnt += 1; return
        v = order[i]
        for c in range(5):
            ok = True
            for y in adjl[v]:
                if lab[y] >= 0 and (c - lab[y]) % 5 not in (1, 4):
                    ok = False; break
            if ok:
                lab[v] = c; bt(i + 1); lab[v] = -1
                if cnt >= cap: return
    bt(0)
    return cnt

def report(name, n, edges, incell_check=True):
    m = len(edges)
    assert is_triangle_free(n, edges), name + " NOT triangle-free!"
    mc = maxcut_exact(n, edges)
    beta = m - mc
    dmin = min(degrees(n, edges))
    ok = 25 * beta <= n * n
    hom = hom_count_to_C5(n, edges, cap=1)
    print(f"{name}: N={n} m={m} maxcut={mc} beta={beta}  25*beta={25*beta} vs N^2={n*n}  beta<=N^2/25:{ok}  "
          f"beta/N^2={F(beta,n*n)}  delta={dmin} delta/N={F(dmin,n)}  C5-hom-exists:{bool(hom)}")
    return dict(n=n, m=m, mc=mc, beta=beta, dmin=dmin, hom=bool(hom))

print("=== 1. NAMED GRAPHS (exact brute-force maxcut) ===")
# Petersen
pv = list(itertools.combinations(range(5), 2))
pidx = {p: i for i, p in enumerate(pv)}
pet_edges = [(pidx[a], pidx[b]) for a, b in itertools.combinations(pv, 2) if not (set(a) & set(b))]
rp = report("Petersen", 10, pet_edges)
assert rp["m"] == 15 and rp["mc"] == 12 and rp["beta"] == 3 and rp["hom"] is False

# C5 balanced blowups k=1,2,3
for k in (1, 2, 3):
    n = 5 * k
    edges = [(i * k + a, ((i + 1) % 5) * k + b) for i in range(5) for a in range(k) for b in range(k)]
    r = report(f"C5-blowup(k={k})", n, edges)
    assert r["beta"] == k * k and 25 * r["beta"] == n * n, "C5 blowup must be TIGHT"
print("C5 blowups TIGHT at N^2/25: verified k=1,2,3")

# Grotzsch: outer cycle 0..4, inner 5..9 (u_i=5+i ~ v_{i+-1}), center 10
ge = [(i, (i + 1) % 5) for i in range(5)]
ge += [(5 + i, (i + 1) % 5) for i in range(5)] + [(5 + i, (i - 1) % 5) for i in range(5)]
ge += [(10, 5 + i) for i in range(5)]
rg = report("Grotzsch", 11, ge)

# Andrasfai And_k = circulant Z_{3k-1}, diffs {k..2k-1}; And_2 = C5
and_results = {}
for k in (2, 3, 4, 5, 6):
    n = 3 * k - 1
    edges = sorted(set(tuple(sorted((i, (i + d) % n))) for i in range(n) for d in range(k, 2 * k)))
    r = report(f"And_{k}", n, edges)
    and_results[k] = r
# balanced-blowup uncut ratio for And_k = (m - maxcut)/n^2 (blowup maxcut = k^2*maxcut by multilinearity)
for k, r in and_results.items():
    print(f"  And_{k} balanced-blowup beta ratio = {F(r['m']-r['mc'], r['n']**2)} = {float(F(r['m']-r['mc'], r['n']**2)):.6f} (1/25=0.04)")

# Clebsch = folded 5-cube: 0..15, i~j iff popcount(i^j) in {1,4}... folded: xor weight 1 or i^j=15
cl_edges = sorted(set(tuple(sorted((i, j))) for i in range(16) for j in range(16)
                      if i != j and (bin(i ^ j).count("1") == 1 or (i ^ j) == 15)))
rc = report("Clebsch", 16, cl_edges)

print()
print("=== 2. LEMMA A (pentagonal): AM-GM  min_i x_i x_{i+1} <= 1/25, tight iff balanced ===")
# exact spot checks + random rational points
def minprod(x):
    return min(x[i] * x[(i + 1) % 5] for i in range(5))
assert minprod([F(1, 5)] * 5) == F(1, 25)
worst = F(0)
for _ in range(20000):
    w = [F(random.randint(0, 50)) for _ in range(5)]
    s = sum(w)
    if s == 0: continue
    x = [wi / s for wi in w]
    mp = minprod(x)
    assert mp <= F(1, 25), ("AM-GM VIOLATED", x)
    worst = max(worst, mp)
print(f"20000 random rational simplex points: max of min_i x_i x_(i+1) found = {worst} <= 1/25  OK (tight only at balanced)")

print()
print("=== 3. beta subgraph-monotonicity spot check (exact) ===")
def rand_tf(n, tries=300):
    edges = []
    adj = [0] * n
    for _ in range(tries):
        u, v = random.sample(range(n), 2)
        if (adj[u] >> v) & 1: continue
        if adj[u] & adj[v]: continue
        adj[u] |= 1 << v; adj[v] |= 1 << u; edges.append((u, v))
    return edges
viol = 0
for t in range(60):
    n = 9
    E = rand_tf(n)
    bG = len(E) - maxcut_exact(n, E)
    E2 = [e for e in E if random.random() < 0.6]
    bH = len(E2) - maxcut_exact(n, E2)
    if bH > bG: viol += 1
print(f"60 random (G, subgraph H) pairs: monotonicity beta(H)<=beta(G) violations = {viol} (expect 0)")

print()
print("=== 4. PEEL ARITHMETIC (exact): if d(v) <= D(N) then floor(d/2) <= (2N-1)/25, and (N-1)^2 + (2N-1) = N^2 ===")
def D(N):  # max degree peelable at size N
    d = 0
    while 25 * ((d + 1) // 2) <= 2 * N - 1: d += 1
    return d
bad = 0
for N in range(2, 20001):
    assert (N - 1) ** 2 + (2 * N - 1) == N * N
    d = D(N)
    if not (25 * (d // 2) <= 2 * N - 1 and 25 * ((d + 1) // 2) > 2 * N - 1): bad += 1
    if 25 * d < 4 * N - 52: bad += 1  # D(N) >= (4N-52)/25 sanity
print(f"N=2..20000: identity + D(N) window checks, failures = {bad}; samples D(100)={D(100)} D(200)={D(200)} D(1000)={D(1000)}  (~4N/25={4*1000//25} at N=1000)")

print()
print("=== 5. nu(H) = max_x min_cuts uncut(x): float search + EXACT rational witnesses ===")
try:
    import numpy as np
    HAVE_NP = True
except Exception:
    HAVE_NP = False
print("numpy:", HAVE_NP)

def build_cut_matrix(n, edges):
    import numpy as np
    S = 1 << (n - 1)
    E = len(edges)
    M = np.zeros((S, E), dtype=np.float64)
    for ei, (u, v) in enumerate(edges):
        for s in range(S):
            if ((s >> u) & 1) == ((s >> v) & 1): M[s, ei] = 1.0
    return M

def nu_search(name, n, edges, iters=4):
    import numpy as np
    M = build_cut_matrix(n, edges)
    us = np.array([e[0] for e in edges]); vs = np.array([e[1] for e in edges])
    best_val, best_x = -1.0, None
    for it in range(iters):
        for supsz in (5, n):
            B = 4000
            X = np.zeros((B, n))
            for b in range(B):
                sup = random.sample(range(n), supsz)
                w = np.random.dirichlet(np.ones(supsz))
                X[b, sup] = w
            W = X[:, us] * X[:, vs]
            f = (M @ W.T).min(axis=0)
            i = int(f.argmax())
            if f[i] > best_val: best_val, best_x = float(f[i]), X[i].copy()
    # local refinement
    x = best_x.copy()
    step = 0.05
    for _ in range(4000):
        y = np.maximum(x + step * (np.random.rand(n) - 0.5), 0); y /= y.sum()
        w = y[us] * y[vs]
        fv = float((M @ w).min())
        if fv > best_val: best_val, x = fv, y
        step *= 0.9995
    # exact verification of rounded witness
    Dq = 2520
    xr = [F(int(round(xi * Dq)), Dq) for xi in x]
    diff = 1 - sum(xr); xr[int(np.argmax(x))] += diff
    if min(xr) < 0: xr = [max(q, F(0)) for q in xr]; s = sum(xr); xr = [q / s for q in xr]
    exact = None
    if all(q >= 0 for q in xr) and sum(xr) == 1:
        exact = min(sum(xr[u] * xr[v] for (u, v) in edges if ((s >> u) & 1) == ((s >> v) & 1))
                    for s in range(1 << (n - 1)))
    print(f"nu({name}): float-search max = {best_val:.6f} (1/25 = 0.04); exact value at rounded witness = {exact} = {float(exact):.6f}")
    return best_val, exact

def find_induced_C5(n, edges):
    eset = set(map(tuple, map(sorted, edges)))
    for sub in itertools.combinations(range(n), 5):
        ie = [tuple(sorted((a, b))) for a, b in itertools.combinations(sub, 2) if tuple(sorted((a, b))) in eset]
        if len(ie) != 5: continue
        dd = {}
        for a, b in ie: dd[a] = dd.get(a, 0) + 1; dd[b] = dd.get(b, 0) + 1
        if all(dd.get(v, 0) == 2 for v in sub):
            # connected 2-regular on 5 vertices = C5
            return sub, ie
    return None, None

for name, n, edges in [("And_3", 8, None), ("And_4", 11, None), ("Petersen", 10, pet_edges), ("Clebsch", 16, cl_edges)]:
    if edges is None:
        k = int(name.split("_")[1]); n = 3 * k - 1
        edges = sorted(set(tuple(sorted((i, (i + d) % n))) for i in range(n) for d in range(k, 2 * k)))
    sub, ie = find_induced_C5(n, edges)
    if sub:
        xs = [F(0)] * n
        for v in sub: xs[v] = F(1, 5)
        val = min(sum(xs[u] * xs[v] for (u, v) in edges if ((s >> u) & 1) == ((s >> v) & 1))
                  for s in range(1 << (n - 1)))
        print(f"{name}: induced C5 at {sub}; EXACT nu lower bound at balanced-C5 support = {val} (=1/25? {val == F(1,25)})")
    if HAVE_NP and n <= 16:
        nu_search(name, n, edges)

print()
print("=== 6. In-cell pentagonal sup: max min_i x_i x_(i+1) s.t. min_i(x_(i-1)+x_(i+1)) <= tau ===")
def cell_search(tau_f, tau_q):
    best, bx = -1.0, None
    for _ in range(200000):
        w = [random.random() for _ in range(5)]
        s = sum(w); x = [wi / s for wi in w]
        if min(x[(i - 1) % 5] + x[(i + 1) % 5] for i in range(5)) > tau_f + 1e-12: continue
        v = min(x[i] * x[(i + 1) % 5] for i in range(5))
        if v > best: best, bx = v, x
    # refine
    for _ in range(200000):
        y = [max(xi + 0.01 * (random.random() - 0.5), 0) for xi in bx]
        s = sum(y); y = [yi / s for yi in y]
        if min(y[(i - 1) % 5] + y[(i + 1) % 5] for i in range(5)) > tau_f + 1e-12: continue
        v = min(y[i] * y[(i + 1) % 5] for i in range(5))
        if v > best: best, bx = v, y
    # exact rational witness
    Dq = 10000
    xr = [F(int(round(xi * Dq)), Dq) for xi in bx]
    xr[0] += 1 - sum(xr)
    okc = min(xr[(i - 1) % 5] + xr[(i + 1) % 5] for i in range(5)) <= tau_q and all(q >= 0 for q in xr)
    ev = min(xr[i] * xr[(i + 1) % 5] for i in range(5)) if okc else None
    evs = f"{ev} ({float(ev):.6f})" if ev is not None else "rounding infeasible (float value stands as indicative only)"
    print(f"tau={tau_q}: float sup ~= {best:.6f}; exact feasible witness value = {evs}  vs 1/25=0.04")
cell_search(1 / 3, F(1, 3))
cell_search(3 / 8, F(3, 8))

print()
print("=== 7. Cell membership of named graphs (delta/N in (4/25,1/3], m<N^2/5) ===")
for nm, r in [("Petersen", rp), ("Clebsch", rc), ("Grotzsch", rg)] + [(f"And_{k}", v) for k, v in and_results.items()]:
    n, m, dmin = r["n"], r["m"], r["dmin"]
    incell = (25 * dmin > 4 * n) and (3 * dmin <= n) and (5 * m < n * n)
    print(f"{nm}: delta/N={F(dmin,n)} m/N^2={F(m,n*n)} -> in open cell (as balanced blowup family): {incell}; beta/N^2={F(r['beta'],n*n)}")
print("DONE")
