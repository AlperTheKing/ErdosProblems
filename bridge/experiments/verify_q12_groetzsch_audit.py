#!/usr/bin/env python3
"""
AUDIT of GPT Q12's answer: COVERAGE (the 4+1-template menu) is FALSE.
GPT's explicit infinite family: weighted blow-up G_k of the 11-vertex Grötzsch graph H,
in-band with tau_K=0 (CF holds) but ALL templates {A7,edge,C5,Petersen,Clebsch} fail.

We verify the load-bearing claims:
(A) GPT's explicit Clebsch embedding of H is a HOMOMORPHISM (every H-edge -> Clebsch edge,
    |symdiff|=4) and is INDUCED (non-edges -> non-Clebsch-edges). => tau_K(H)=0.
(B) Weighted blow-up G_k (u_i,v_i -> class 2k, w -> class k): N=21k, e=70k^2, x=10/63,
    RHS=(N^2/5-e)/2=91/10 k^2, in band [0.1243,0.16]; tau_K(G_k)=0 (homomorphism via embedding,
    cross-checked by local search).
(C) Edge-root certificate FAILS on every edge class (cert_edge > RHS).
(D) C5-root certificate FAILS on every induced C5 (cert_C5 > RHS); also report margin.
(E) H has NO induced Petersen (no H-z is 3-regular) and NO induced Clebsch (|H|=11<16),
    and blow-up classes are false twins => no Petersen/Clebsch root in G_k.
(F) G_k contains induced C5 (so A7 inapplicable).
"""
import itertools, random
random.seed(23)

# Clebsch graph K: even subsets of [5] (bitmask), adjacency |symdiff|=4
labels = [m for m in range(32) if bin(m).count('1') % 2 == 0]
def clebsch_adj(a, b): return bin(a ^ b).count('1') == 4
def cost(a, b): return (4 - bin(a ^ b).count('1')) // 2

# ---- H = Groetzsch, vertices u0..u4 (0..4), v0..v4 (5..9), w (10) ----
def bm(s):
    r = 0
    for x in s: r |= 1 << (x - 1)
    return r
emb = {
    0: bm([]),       1: bm([1,4]),     2: bm([1,3]),     3: bm([1,2]),     4: bm([1,5]),       # u_i
    5: bm([2,3]),    6: bm([1,2,4,5]), 7: bm([3,5]),     8: bm([2,4]),     9: bm([1,3,4,5]),   # v_i
    10: bm([2,3,4,5]),                                                                           # w
}
def H_edges():
    E = []
    for i in range(5):
        E.append((5 + i, 5 + (i + 1) % 5))          # v_i v_{i+1}
        E.append((i, 5 + (i - 1) % 5))              # u_i v_{i-1}
        E.append((i, 5 + (i + 1) % 5))              # u_i v_{i+1}
        E.append((10, i))                           # w u_i
    return sorted(set((min(a,b), max(a,b)) for a,b in E))
HE = H_edges()
Hset = set(HE)

print("=== (A) GPT's Clebsch embedding of H ===")
# all images even-size & distinct
alleven = all(bin(emb[v]).count('1') % 2 == 0 for v in range(11))
distinct = len(set(emb.values())) == 11
# homomorphism: every H-edge -> Clebsch edge
hom = all(clebsch_adj(emb[a], emb[b]) for a, b in HE)
# induced: every H-NONedge -> non-Clebsch-edge (so it's an induced subgraph)
induced = True
for a in range(11):
    for b in range(a+1, 11):
        is_He = (a, b) in Hset
        is_Ke = clebsch_adj(emb[a], emb[b])
        if is_He != is_Ke:
            induced = False
print(f"  |H edges|={len(HE)} (expect 20); images even={alleven} distinct={distinct}")
print(f"  homomorphism (H-edges -> Clebsch edges): {hom}")
print(f"  INDUCED embedding (edges<->edges both ways): {induced}  => tau_K(H)=0: {hom}")

# triangle-free check of H
Hadj = [set() for _ in range(11)]
for a, b in HE: Hadj[a].add(b); Hadj[b].add(a)
trifree = not any((c in Hadj[a] and c in Hadj[b]) for a,b in HE for c in range(11))
print(f"  H triangle-free: {trifree};  H degrees: {[len(Hadj[v]) for v in range(11)]}")

print("\n=== (E) no induced Petersen / Clebsch in H ===")
# any 10-vtx induced subgraph = H - z; Petersen is 3-regular
no_pet = True
for z in range(11):
    keep = [v for v in range(11) if v != z]
    degs = [len(Hadj[v] - {z}) for v in keep]
    if all(d == 3 for d in degs):   # would-be 3-regular (necessary for Petersen)
        no_pet = False
print(f"  no H-z is 3-regular (=> no induced Petersen): {no_pet}")
print(f"  no induced Clebsch (|H|=11 < 16): True")

print("\n=== (B)-(D),(F) Weighted blow-up G_k ===")
def build_Gk(k):
    # classes: u_i (2k), v_i (2k) for i in 0..4, w (k). order them; record class label per vtx.
    sizes = [2*k]*10 + [k]   # H-vertex index -> class size
    start = [0]*12
    for i in range(11): start[i+1] = start[i] + sizes[i]
    N = start[11]
    cls = [None]*N
    for i in range(11):
        for j in range(start[i], start[i+1]): cls[j] = i
    A = [set() for _ in range(N)]
    for (a, b) in HE:
        for x in range(start[a], start[a+1]):
            for y in range(start[b], start[b+1]):
                A[x].add(y); A[y].add(x)
    return N, A, cls
def edges_of(N, A): return [(u, v) for u in range(N) for v in A[u] if v > u]

def tau_via_embedding(N, A, cls):
    lab = [emb[cls[v]] for v in range(N)]
    return sum(cost(lab[u], lab[v]) for u in range(N) for v in A[u] if v > u)

def tau_K_ub(N, A, restarts=20, sweeps=25):
    nbr = [list(A[v]) for v in range(N)]; best = None
    for _ in range(restarts):
        lab = [random.choice(labels) for _ in range(N)]; imp=True; sw=0
        while imp and sw < sweeps:
            imp=False; sw+=1
            for u in range(N):
                bc, bl = None, lab[u]
                for L in labels:
                    c = sum(cost(L, lab[w]) for w in nbr[u])
                    if bc is None or c < bc: bc, bl = c, L
                if bl != lab[u]: lab[u]=bl; imp=True
        tot = sum(cost(lab[u], lab[w]) for u in range(N) for w in nbr[u] if w>u)
        if best is None or tot < best: best=tot
    return best

def edge_root_fail(N, A, e, rhs):
    deg = [len(A[v]) for v in range(N)]
    S = [sum(deg[z] for z in A[v]) for v in range(N)]
    # best (smallest) edge-root bound over all edges
    best = min(e - (S[u] + S[v]) / 2.0 for u in range(N) for v in A[u] if v > u)
    return best, best > rhs + 1e-9   # fails (no edge certifies) iff best > RHS

# C5-root via the 10 explicit maps (reuse verify_4branch_coverage's min_FC if importable)
from verify_4branch_coverage import min_FC

for k in (1, 2):
    N, A, cls = build_Gk(k)
    E = edges_of(N, A); e = len(E)
    x = e / (N*N); rhs = (N*N/5.0 - e)/2.0
    tau_emb = tau_via_embedding(N, A, cls)
    inband = 0.1243 <= x <= 0.16
    er_best, er_fail = edge_root_fail(N, A, e, rhs)
    fc = min_FC(N, A, E)
    fc_fail = (fc is not None) and (fc > rhs + 1e-9)
    has_c5 = fc is not None
    print(f"  k={k}: N={N} (exp {21*k}) e={e} (exp {70*k*k}) x={x:.6f} (exp {10/63:.6f}) inband={inband}")
    print(f"        RHS={rhs:.1f} (exp {91/10*k*k:.1f})  tau_emb={tau_emb} (exp 0)  tau_K_ub={tau_K_ub(N,A)}")
    print(f"        edge-root best={er_best:.1f} > RHS (fails)={er_fail}")
    print(f"        C5-root min F_C={fc} > RHS (fails)={fc_fail}  has_induced_C5={has_c5} (A7 inapplicable)")
    allfail = er_fail and fc_fail and tau_emb == 0 and inband and has_c5
    print(f"        => COVERAGE GAP confirmed (in-band, tau_K=0, edge+C5 fail, no P/K root): {allfail}")
print("\nAUDIT DONE")
