#!/usr/bin/env python3
"""
Audit GPT Q10's CF analysis: verify the two explicit graphs.
(A) M_2(C5) = twice-iterated Mycielskian of C5: claim N=23, e=71, triangle-free,
    5-chromatic (=> non-Clebsch-hom since chi(Clebsch)=4 => tau_K>=1), density 0.1342.
    Also check the 13 listed edge-disjoint induced C5's.
(B) C5[m] u. K_{r,r} with 5m=3N/4, 2r=N/4 (N=80: m=12,r=10): claim tau_K=0
    (both components Clebsch-homomorphic), density 0.128125 (in band), tau_5 >= 7/800 N².
Also re-confirm tau_K <= (3/2) beta on small graphs (the proven bound).
"""
import itertools, random
random.seed(3)

LABELS = [m for m in range(32) if bin(m).count('1') % 2 == 0]
def cost(a, b): return (4 - bin(a ^ b).count('1')) // 2

def mycielskian(n, adj):
    # vertices 0..n-1 original, n..2n-1 shadows, 2n apex
    N = 2 * n + 1
    A = [set() for _ in range(N)]
    for u in range(n):
        for v in adj[u]:
            A[u].add(v)
    for u in range(n):
        for v in adj[u]:
            A[u + n].add(v)   # shadow u' ~ neighbors of u
            A[v].add(u + n)
        A[u + n].add(2 * n)   # shadow ~ apex
        A[2 * n].add(u + n)
    return N, A

def adjset_from_edges(N, edges):
    A = [set() for _ in range(N)]
    for u, v in edges:
        A[u].add(v); A[v].add(u)
    return A

def triangle_free(N, A):
    for u in range(N):
        for v in A[u]:
            if v > u and (A[u] & A[v]):
                return False
    return True

def is_k_colorable(N, A, k):
    color = [-1] * N
    order = sorted(range(N), key=lambda x: -len(A[x]))
    def bt(idx):
        if idx == N: return True
        v = order[idx]
        used = {color[w] for w in A[v] if color[w] >= 0}
        for c in range(k):
            if c not in used:
                color[v] = c
                if bt(idx + 1): return True
                color[v] = -1
        return False
    return bt(0)

def maxcut(N, A):
    best = 0
    for mask in range(1 << (N - 1)):
        cut = 0
        for u in range(N):
            for v in A[u]:
                if v > u and (((mask >> u) ^ (mask >> v)) & 1):
                    cut += 1
        if cut > best: best = cut
    return best

def beta_small(N, A):
    e = sum(len(A[u]) for u in range(N)) // 2
    return e - maxcut(N, A)

def tau_K_ub(N, A, restarts=80, sweeps=40):
    nbr = [list(A[u]) for u in range(N)]
    best = None
    for _ in range(restarts):
        lab = [random.choice(LABELS) for _ in range(N)]
        imp = True; sw = 0
        while imp and sw < sweeps:
            imp = False; sw += 1
            for u in range(N):
                bc, bl = None, lab[u]
                for L in LABELS:
                    c = sum(cost(L, lab[w]) for w in nbr[u])
                    if bc is None or c < bc: bc, bl = c, L
                if bl != lab[u]: lab[u] = bl; imp = True
        tot = sum(cost(lab[u], lab[w]) for u in range(N) for w in nbr[u] if w > u)
        if best is None or tot < best: best = tot
    return best

# ---------- (A) M_2(C5) ----------
print("=== (A) M_2(C5) = Mycielskian(Mycielskian(C5)) ===")
C5adj = [set() for _ in range(5)]
for i in range(5):
    C5adj[i].add((i+1) % 5); C5adj[i].add((i-1) % 5)
n1, A1 = mycielskian(5, C5adj)          # Grotzsch, 11 vtx
n2, A2 = mycielskian(n1, A1)            # M_2(C5), 23 vtx
e2 = sum(len(A2[u]) for u in range(n2)) // 2
print(f"N={n2} e={e2} density={2*e2/(n2*(n2-1)):.4f} (claim N=23,e=71,dens~0.1342 i.e. e/N^2={e2/(n2*n2):.4f})")
print(f"triangle-free: {triangle_free(n2, A2)}")
print(f"4-colorable: {is_k_colorable(n2, A2, 4)}  (False => chi>=5 => NOT Clebsch-hom => tau_K>=1)")
# verify the 13 listed edge-disjoint induced C5's
cycles = [(0,1,16,10,20),(0,4,3,2,6),(11,9,0,17,22),(18,1,5,21,22),(6,13,1,7,21),
          (2,12,7,10,17),(15,8,2,19,22),(3,15,5,10,18),(14,7,3,20,22),(3,9,10,8,13),
          (12,5,4,16,22),(4,11,6,10,19),(8,4,14,9,21)]
used_edges = set(); ok_cycles = 0; edge_disjoint = True; all_C5 = True
for cyc in cycles:
    ce = []
    good = True
    for i in range(5):
        u, v = cyc[i], cyc[(i+1)%5]
        if v not in A2[u]: good = False
        ce.append((min(u,v), max(u,v)))
    # induced C5: also the 5 non-cycle pairs are non-edges
    if good:
        for i in range(5):
            for j in range(i+1,5):
                if (j-i) % 5 not in (1,4):  # non-consecutive
                    if cyc[j] in A2[cyc[i]]: good=False
    if good: ok_cycles += 1
    else: all_C5 = False
    for ed in ce:
        if ed in used_edges: edge_disjoint = False
        used_edges.add(ed)
print(f"13 cycles: all induced C5={all_C5} ({ok_cycles}/13), edge-disjoint={edge_disjoint}, tau5>=13 vs 7/800*23^2={7/800*23*23:.2f}")

# ---------- (B) C5[m] disjoint K_{r,r} ----------
print("\n=== (B) C5[12] u. K_{10,10} (N=80) ===")
m, r = 12, 10
N = 5*m + 2*r
A = [set() for _ in range(N)]
# C5[m] on 0..5m-1
parts = [list(range(i*m,(i+1)*m)) for i in range(5)]
for p in range(5):
    for u in parts[p]:
        for v in parts[(p+1)%5]:
            A[u].add(v); A[v].add(u)
# K_{r,r} on 5m..5m+2r-1
L = list(range(5*m, 5*m+r)); R = list(range(5*m+r, 5*m+2*r))
for u in L:
    for v in R:
        A[u].add(v); A[v].add(u)
e = sum(len(A[u]) for u in range(N)) // 2
print(f"N={N} e={e} e/N^2={e/(N*N):.6f} (claim 0.128125, band 0.1243..0.16) triangle-free={triangle_free(N,A)}")
tk = tau_K_ub(N, A, restarts=40, sweeps=30)
print(f"tau_K upper bound (local search) = {tk}  (claim 0; C5[m] & K_rr both Clebsch-hom)")
print(f"tau5(C5[m])=m^2={m*m}; (tau5/N^2={m*m/(N*N):.4f} > 7/800={7/800:.5f})")

# ---------- (C) spot-check tau_K <= 3/2 beta on small triangle-free graphs ----------
print("\n=== (C) tau_K <= (3/2) beta spot-check (small tri-free graphs) ===")
def rand_trifree(n):
    A = [set() for _ in range(n)]
    pairs = [(u,v) for u in range(n) for v in range(u+1,n)]
    random.shuffle(pairs)
    for u,v in pairs:
        if A[u]&A[v]: continue
        A[u].add(v); A[v].add(u)
    return A
viol = 0; tested = 0
for _ in range(40):
    n = random.randint(6,9)
    A = rand_trifree(n)
    b = beta_small(n, A)
    if b == 0: continue
    tk = tau_K_ub(n, A, restarts=60, sweeps=30)
    tested += 1
    if tk > 1.5*b + 1e-9: viol += 1
print(f"tested {tested} graphs: tau_K_ub <= 1.5*beta violations = {viol} (expect 0; ub<=true so 0 confirms bound)")
print("DONE")
