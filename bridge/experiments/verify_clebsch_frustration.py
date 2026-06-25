#!/usr/bin/env python3
"""
Independent verification of the load-bearing computable claims in GPT Pro's Q9
answer (the Clebsch-frustration reduction).

Checks:
1. Build the Clebsch graph K = 16 even subsets of [5], A~B iff |A xor B|=4.
   Verify: 16 vertices, 5-regular (e=40), triangle-free, beta(K)=8, MaxCut=32.
2. Verify the bound beta(K) <= N^2/25 (= 256/25 = 10.24) and the two ingredients:
   (1) Clebsch-hom => beta <= e/5  (here K->K identity: beta<=40/5=8). Check the 5
       coordinate cuts C_j leave each edge mono in EXACTLY one cut.
   (2) MaxCut >= Q/N = sum d^2 / N  (Q/N=400/16=25; MaxCut=32>=25).
3. Verify MaxCut >= Q/N (eq.2) and MaxCut >= 4e^2/N^2 for many small triangle-free
   graphs (random + structured), 0 violations expected; tight at C5[n].
"""
import itertools, random
random.seed(7)

# ---------- Clebsch graph ----------
even_sets = [frozenset(s) for r in (0, 2, 4) for s in itertools.combinations(range(5), r)]
assert len(even_sets) == 16, len(even_sets)
idx = {s: i for i, s in enumerate(even_sets)}

def sym(a, b):
    return len(a ^ b)

K_edges = []
for i in range(16):
    for j in range(i + 1, 16):
        if sym(even_sets[i], even_sets[j]) == 4:
            K_edges.append((i, j))

def adj_from_edges(N, edges):
    adj = [0] * N
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return adj

Kadj = adj_from_edges(16, K_edges)
deg = [bin(Kadj[i]).count('1') for i in range(16)]
print(f"Clebsch: N=16 e={len(K_edges)} degrees={set(deg)} (expect 5-regular, e=40)")

# triangle-free?
tri = any((Kadj[u] & Kadj[v]) for u, v in K_edges)
print(f"  triangle-free: {not tri}")

def maxcut(N, adj):
    best = 0
    E = sum(bin(a).count('1') for a in adj) // 2
    for mask in range(1 << (N - 1)):
        cut = 0
        for v in range(N):
            if mask & (1 << v):
                cut += bin(adj[v] & ~mask).count('1')
        if cut > best:
            best = cut
    return best, E

mcK, eK = maxcut(16, Kadj)
betaK = eK - mcK
Q = sum(d * d for d in deg)
print(f"  MaxCut={mcK}  beta={betaK}  (expect MaxCut=32, beta=8)")
print(f"  Q=sum d^2={Q}  Q/N={Q/16}  4e^2/N^2={4*eK*eK/256}")
print(f"  beta(K)={betaK} <= N^2/25={256/25:.3f}? {betaK <= 256/25}")
print(f"  MaxCut={mcK} >= Q/N={Q/16}? {mcK >= Q/16}   >= 4e^2/N^2={4*eK*eK/256}? {mcK >= 4*eK*eK/256}")

# coordinate cuts: edge mono in exactly one of the 5?
ok = True
for (u, v) in K_edges:
    a, b = even_sets[u], even_sets[v]
    mono = sum(1 for j in range(5) if (j in a) == (j in b))  # same side of C_j
    if mono != 1:
        ok = False
print(f"  coordinate-cut certificate: every edge mono in exactly 1 of 5 cuts? {ok}  (=> beta<=e/5={eK/5})")

# ---------- MaxCut >= Q/N over triangle-free graphs ----------
def c5_blowup(n):
    parts = [list(range(i * n, i * n + n)) for i in range(5)]
    E = []
    for p in range(5):
        for u in parts[p]:
            for v in parts[(p + 1) % 5]:
                E.append((u, v))
    return 5 * n, E

def rand_trifree(N):
    adj = [0] * N
    pairs = [(u, v) for u in range(N) for v in range(u + 1, N)]
    random.shuffle(pairs)
    E = []
    for (u, v) in pairs:
        if adj[u] & adj[v]:
            continue
        adj[u] |= 1 << v; adj[v] |= 1 << u; E.append((u, v))
    return N, E

viol = 0; tight = 0; tested = 0
cases = []
for n in (1, 2, 3):
    cases.append(c5_blowup(n))
for N in range(5, 11):
    for _ in range(300):
        cases.append(rand_trifree(N))
for (N, E) in cases:
    adj = adj_from_edges(N, E)
    if any(adj[u] & adj[v] for u, v in E):  # safety
        continue
    mc, e = maxcut(N, adj)
    Qg = sum(bin(a).count('1') ** 2 for a in adj)
    tested += 1
    if mc < Qg / N - 1e-9:
        viol += 1
    if abs(mc - Qg / N) < 1e-9:
        tight += 1
print(f"\nMaxCut>=Q/N over {tested} triangle-free graphs (C5[n] + random N<=10): "
      f"violations={viol}, tight(=Q/N)={tight}")
print("DONE")
