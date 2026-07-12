# GW-geometric lens: exact verifier battery. ALL arithmetic exact (int / Fraction).
# Angles are stored as rational multiples of pi: a in [0,2) meaning angle a*pi.
# theta(u,v)/pi = min(|a_u-a_v|, 2-|a_u-a_v|)  in [0,1], exact Fraction.
from fractions import Fraction as F
from itertools import combinations
import random, sys

random.seed(23)

def maxcut(n, edges):
    # brute force, fix vertex 0 on side 0
    best = 0
    for mask in range(1 << (n - 1)):
        m = mask << 1  # vertex0 bit = 0
        c = 0
        for (u, v) in edges:
            if ((m >> u) ^ (m >> v)) & 1:
                c += 1
        if c > best:
            best = c
    return best

def is_triangle_free(n, edges):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v); adj[v].add(u)
    for u, v in edges:
        if adj[u] & adj[v]:
            return False
    return True

def hom_to_C5(n, edges):
    # backtracking: map to Z5, edges must map to |a-b| mod 5 in {1,4}
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v); adj[v].append(u)
    order = sorted(range(n), key=lambda x: -len(adj[x]))
    pos = [-1] * n
    def ok(v, c):
        for w in adj[v]:
            if pos[w] >= 0 and (c - pos[w]) % 5 not in (1, 4):
                return False
        return True
    def bt(i):
        if i == n: return True
        v = order[i]
        for c in range(5):
            if ok(v, c):
                pos[v] = c
                if bt(i + 1): return True
                pos[v] = -1
        return False
    return bt(0)

def theta_over_pi(a, b):
    d = abs(a - b) % 2
    return min(d, 2 - d)

def U_of_embedding(edges, ang):
    return sum(1 - theta_over_pi(ang[u], ang[v]) for u, v in edges)

# ---------- graph constructions ----------
def petersen():
    vs = list(combinations(range(5), 2))
    idx = {s: i for i, s in enumerate(vs)}
    edges = [(idx[a], idx[b]) for a, b in combinations(vs, 2) if not set(a) & set(b)]
    return 10, edges

def c5_blowup(t):
    n = 5 * t
    edges = []
    for k in range(5):
        for i in range(t):
            for j in range(t):
                edges.append((k * t + i, ((k + 1) % 5) * t + j))
    return n, edges

def circulant(n, conns):
    edges = set()
    for v in range(n):
        for c in conns:
            u = (v + c) % n
            edges.add((min(u, v), max(u, v)))
    return n, sorted(edges)

def gen_mycielski_c5(r):
    # levels 0..r-1 (each Z5) + apex; level0 = C5; (i,j)~(i-1,j+-1); apex ~ level r-1
    def vid(i, j): return i * 5 + j
    n = 5 * r + 1
    apex = 5 * r
    edges = set()
    for j in range(5):
        edges.add((min(vid(0, j), vid(0, (j + 1) % 5)), max(vid(0, j), vid(0, (j + 1) % 5))))
    for i in range(1, r):
        for j in range(5):
            for d in (1, 4):
                a, b = vid(i, j), vid(i - 1, (j + d) % 5)
                edges.add((min(a, b), max(a, b)))
    for j in range(5):
        edges.add((min(apex, vid(r - 1, j)), max(apex, vid(r - 1, j))))
    return n, sorted(edges)

# ---------- SECTION 1: mandated sanity (Petersen, C5 blowups tight) ----------
print("== S1: Petersen + C5 blow-up tightness (exact brute force) ==")
n, E = petersen()
mc = maxcut(n, E)
beta = len(E) - mc
assert is_triangle_free(n, E)
print(f"Petersen: N={n} e={len(E)} maxcut={mc} beta={beta}  bound N^2/25={F(n*n,25)}  OK={25*beta <= n*n}")
assert (len(E), mc, beta) == (15, 12, 3) and 25 * beta <= n * n

for t in (1, 2, 3):
    n, E = c5_blowup(t)
    assert is_triangle_free(n, E)
    mc = maxcut(n, E)
    beta = len(E) - mc
    print(f"C5[{t}]: N={n} e={len(E)} maxcut={mc} beta={beta}  25*beta=={n*n}? {25*beta == n*n} (TIGHT)")
    assert 25 * beta == n * n
    assert mc == (t * t) * 4  # multilinearity: maxcut(H[t]) = t^2 maxcut(H)
print("multilinearity maxcut(C5[t])=4t^2 verified for t=1,2,3")

# ---------- SECTION 2: exactness ingredients: U >= beta on random exact embeddings;
#            pentagram embedding U == beta on blowups ----------
print("\n== S2: U(f) >= beta on random exact embeddings; pentagram tight ==")
for name, (n, E) in (("Petersen", petersen()), ("C5[2]", c5_blowup(2))):
    mc = maxcut(n, E); beta = len(E) - mc
    worst = None
    for _ in range(200):
        ang = [F(random.randrange(0, 3600), 1800) for _ in range(n)]  # rational multiples of pi
        u = U_of_embedding(E, ang)
        assert u >= beta, (name, u, beta)
        worst = u if worst is None else min(worst, u)
    print(f"{name}: beta={beta}; min U over 200 random exact embeddings = {worst} (>= beta OK)")
# pentagram on C5[t]: class k at angle (4k/5)*pi -> a_k = F(4k,5)
for t in (1, 2, 3):
    n, E = c5_blowup(t)
    ang = [F(4 * (v // t), 5) for v in range(n)]
    u = U_of_embedding(E, ang)
    print(f"C5[{t}] pentagram U = {u} == N^2/25 = {F(n*n,25)}  OK={u == F(n*n,25)}")
    assert u == F(n * n, 25)

# ---------- SECTION 3: odd-cycle deficit law: sum_C (1-theta/pi) >= 1 exact ----------
print("\n== S3: odd-cycle deficit law on random exact embeddings ==")
for L in (5, 7, 9):
    n, E = L, [(i, (i + 1) % L) for i in range(L)]
    for _ in range(300):
        ang = [F(random.randrange(0, 7200), 3600) for _ in range(n)]
        s = sum(1 - theta_over_pi(ang[u], ang[v]) for u, v in E)
        assert s >= 1, (L, s)
    print(f"C{L}: 300 random exact embeddings, min deficit-sum >= 1 verified")
# Petersen 5-cycles
n, E = petersen()
adj = [set() for _ in range(n)]
for u, v in E: adj[u].add(v); adj[v].add(u)
fivecycles = []
for c in combinations(range(n), 5):
    # count cyclic orderings forming a 5-cycle
    rest = list(c[1:])
    import itertools
    for perm in itertools.permutations(rest):
        cyc = (c[0],) + perm
        if all(cyc[(i + 1) % 5] in adj[cyc[i]] for i in range(5)):
            fivecycles.append(cyc)
            break
print(f"Petersen: {len(fivecycles)} vertex-sets carrying a 5-cycle")
for _ in range(100):
    ang = [F(random.randrange(0, 7200), 3600) for _ in range(10)]
    for cyc in fivecycles:
        s = sum(1 - theta_over_pi(ang[cyc[i]], ang[cyc[(i + 1) % 5]]) for i in range(5))
        assert s >= 1
print("Petersen: deficit law verified on all 5-cycles x 100 random exact embeddings")

# ---------- SECTION 4: P3 (hom-to-C5 case): min_k m_k <= N^2/25 by AM-GM; exact checks ----------
print("\n== S4: C5-hom case: exhaustive AM-GM + random quotient checks ==")
bad = 0
for N in range(1, 41):
    best = 0
    # exhaustive 5-compositions
    for a in range(N + 1):
        for b in range(N - a + 1):
            for c in range(N - a - b + 1):
                for d in range(N - a - b - c + 1):
                    e5 = N - a - b - c - d
                    ns = (a, b, c, d, e5)
                    mn = min(ns[k] * ns[(k + 1) % 5] for k in range(5))
                    if mn > best: best = mn
    if 25 * best > N * N: bad += 1
    if N % 10 == 0 or N == 5:
        print(f"N={N}: max over compositions of min_k n_k n_(k+1) = {best}; 25*val<=N^2 OK={25*best<=N*N}")
assert bad == 0
print("AM-GM bound min_k n_k n_{k+1} <= N^2/25 exhaustively verified N<=40")

# random C5-pattern graphs: beta <= min_k m_k (cut leaving lightest pair uncut)
for _ in range(200):
    ns = [random.randrange(0, 4) for _ in range(5)]
    if sum(ns) < 2: continue
    # random subgraph of blowup
    offs = [sum(ns[:k]) for k in range(5)]
    N = sum(ns)
    E2 = []
    for k in range(5):
        for i in range(ns[k]):
            for j in range(ns[(k + 1) % 5]):
                if random.random() < 0.7:
                    E2.append((offs[k] + i, offs[(k + 1) % 5] + j))
    if not E2: continue
    mk = []
    for k in range(5):
        cnt = sum(1 for (u, v) in E2
                  if (offs[k] <= u < offs[k] + ns[k] and offs[(k + 1) % 5] <= v < offs[(k + 1) % 5] + ns[(k + 1) % 5])
                  or (offs[k] <= v < offs[k] + ns[k] and offs[(k + 1) % 5] <= u < offs[(k + 1) % 5] + ns[(k + 1) % 5]))
        mk.append(cnt)
    beta2 = len(E2) - maxcut(N, E2)
    assert beta2 <= min(mk), (ns, beta2, mk)
print("beta <= min_k m_k verified on 200 random C5-pattern graphs (exact brute maxcut)")

# ---------- SECTION 5: second-family threat scan: exact beta ratios ----------
print("\n== S5: candidate second families: exact beta and 25*beta/N^2 ==")
cands = []
cands.append(("Petersen", *petersen()))
cands.append(("And(3)=C8(1,4) Wagner", *circulant(8, [1, 4])))
cands.append(("And(4)=C11(1,4)", *circulant(11, [1, 4])))
cands.append(("And(5)=C14(1,4,7)", *circulant(14, [1, 4, 7])))
cands.append(("And(6)=C17(1,4,7)", *circulant(17, [1, 4, 7])))
cands.append(("Groetzsch=mu_2(C5)", *gen_mycielski_c5(2)))
cands.append(("mu_3(C5)", *gen_mycielski_c5(3)))
for name, n, E in cands:
    tf = is_triangle_free(n, E)
    mc = maxcut(n, E)
    beta = len(E) - mc
    hom = hom_to_C5(n, E)
    ratio = F(25 * beta, n * n)
    print(f"{name}: N={n} e={len(E)} tf={tf} maxcut={mc} beta={beta} homC5={hom} 25beta/N^2={ratio} (~{float(ratio):.4f})")
    assert tf
    assert 25 * beta <= n * n
print("NOTE: by multilinearity beta(H[t]) = t^2 beta(H): ratios above are exact for ALL balanced blow-ups of these graphs.")

# ---------- SECTION 6: random triangle-free regression: beta <= N^2/25 ----------
print("\n== S6: random maximal triangle-free graphs N<=14: beta <= N^2/25 ==")
for trial in range(60):
    N = random.randrange(5, 15)
    order = list(combinations(range(N), 2)); random.shuffle(order)
    adj = [set() for _ in range(N)]; E3 = []
    for (u, v) in order:
        if not (adj[u] & adj[v]):
            adj[u].add(v); adj[v].add(u); E3.append((u, v))
    beta3 = len(E3) - maxcut(N, E3)
    assert 25 * beta3 <= N * N, (N, beta3)
print("60 random maximal triangle-free graphs: bound holds (exact)")

print("\nALL SECTIONS PASSED")
