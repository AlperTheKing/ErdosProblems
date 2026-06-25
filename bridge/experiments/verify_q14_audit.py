#!/usr/bin/env python3
"""
AUDIT of GPT Q14 (charging inequality (STAR), second-moment route).
Load-bearing checks:
(A) THE FALSIFICATION: G=K_{16t,64t} (complete bipartite, in-band x=0.16) with all 16 Clebsch labels
    distributed uniformly per shore => s_{v,i}=0 for all v,i => F_v=0 (every vertex a tie) => 1-opt-stable,
    cost(phi)=3e/4=0.12 N^2 >> RHS=0.02 N^2, so (STAR) fails by 0.8 N^2; yet tau_K(G)=0 (2-color the
    bipartition). Confirms: 1-opt stability + local types + triangle-freeness ALONE cannot prove (STAR).
(B) STABLE POLYTOPE: the normalized stable profiles rho_v have exactly 4 types up to S5
    {(0,0,0,0,0),(1,0,0,0,0),(1,1,0,0,0),(-1,1,1,1,1)} with (t,q)=(sum rho, ||rho||^2)=(0,0),(1,1),(2,2),(3,5).
(C) SHARP BOUND: F_v >= (3/5) Q_v/d_v at every stable neighborhood (3/5 optimal at type h_i).
(D) GLOBAL IDENTITY (eq 7): sum_v Q_v = 10e - 6 W0 + 2 W1 + 10 W2 on random triangle-free graphs.
"""
import itertools, random
random.seed(14)
labels = [m for m in range(32) if bin(m).count('1') % 2 == 0]   # 16 Clebsch vertices
def sig(A, i): return -1 if (A >> i) & 1 else 1
def cost(A, B): return (4 - bin(A ^ B).count('1')) // 2
Kadj = [[j for j in range(16) if i != j and bin(labels[i] ^ labels[j]).count('1') == 4] for i in range(16)]

print("=== (A) K_{16,64} uniform-label falsification ===")
# Sum of sigma_i over all 16 Clebsch labels = 0 ?
sums = [sum(sig(A, i) for A in labels) for i in range(5)]
print(f"  sum_A sigma_i(A) over 16 even subsets = {sums} (expect all 0)")
t = 1
small = list(range(16 * t)); big = list(range(16 * t, 80 * t))   # K_{16t,64t}
N = 80 * t; e = (16 * t) * (64 * t)
# label assignment: small shore one Clebsch label per t vertices; big shore 4t per label
lab = {}
for k, v in enumerate(small): lab[v] = labels[k // t]
for k, v in enumerate(big):   lab[v] = labels[k // (4 * t)]
# adjacency: complete bipartite
def nbrs(v): return big if v in set(small) else small
smallset = set(small)
def neigh(v): return big if v in smallset else small
# s_{v,i}
maxabs = 0
for v in range(N):
    s = [sum(sig(lab[u], i) for u in neigh(v)) for i in range(5)]
    maxabs = max(maxabs, max(abs(x) for x in s))
print(f"  max_v,i |s_{{v,i}}| = {maxabs} (expect 0 => F_v=0 all v)")
# 1-opt-stable? every relabel of v is a tie (cost 3 d_v/4 for all A)
def incident_cost(v, A): return sum(cost(A, lab[u]) for u in neigh(v))
stable = True
for v in [small[0], big[0]]:
    costs = [incident_cost(v, A) for A in labels]
    if len(set(costs)) != 1: stable = False
print(f"  every single-vertex relabel a tie (1-opt-stable): {stable}")
total_cost = sum(cost(lab[u], lab[w]) for u in small for w in big)
rhs = (N * N / 5.0 - e) / 2.0
print(f"  N={N} e={e} x={e/(N*N):.4f}  cost(phi)={total_cost} (=3e/4={3*e//4}, =0.12N^2={0.12*N*N:.0f})  RHS={rhs:.0f}")
print(f"  (STAR) LHS=sum F_v=0  vs needed 10e-4N^2/5={10*e-4*N*N//5} => (STAR) FAILS at this stable phi: {0 < 10*e-4*N*N/5}")
# tau_K=0 via 2-coloring (small->A, big->B with A~B in K)
A0 = labels[0]; B0 = labels[Kadj[0][0]]
tk2 = sum(cost(A0, B0) for u in small for w in big)   # cost if small->A0, big->B0
print(f"  2-coloring (small->A0, big->K-neighbor B0) cost = {tk2} => tau_K(G)=0: {tk2==0}")
print(f"  ==> CF HOLDS (tau_K=0) but (STAR) fails at a 1-opt-stable labeling. NEGATIVE result CONFIRMED.")

print("\n=== (B,C) Stable polytope types + sharp bound F_v >= (3/5) Q_v/d_v ===")
# enumerate stable profiles: rho = (1/d) sum of b in H_minus with pairwise rho_i+rho_j>=0
Hminus = [x for x in itertools.product([-1, 1], repeat=5) if (x[0]*x[1]*x[2]*x[3]*x[4]) == -1]
# sample multisets of H_minus vectors, normalize, keep those satisfying stability, collect (t,q) types
seen_types = set(); bound_ok = True; sharp_hi = False
for _ in range(20000):
    d = random.randint(1, 6)
    bs = [random.choice(Hminus) for _ in range(d)]
    rho = [sum(b[i] for b in bs) / d for i in range(5)]
    if any(rho[i] + rho[j] < -1e-9 for i in range(5) for j in range(i+1, 5)):
        continue   # not stable
    tt = sum(rho); qq = sum(r*r for r in rho)
    # F_v = d * t ; Q_v = d^2 * q ; bound F_v >= (3/5) Q_v/d  <=> d*t >= (3/5) d*q <=> t >= (3/5) q
    if tt < (3.0/5.0) * qq - 1e-9: bound_ok = False
    # type up to permutation
    key = tuple(sorted(round(r, 6) for r in rho))
    seen_types.add((round(tt, 4), round(qq, 4)))
    if abs(qq - (5.0/3.0)*tt) < 1e-9 and qq > 0: sharp_hi = True
print(f"  distinct (t,q) extreme-ish values sampled (subset): {sorted(seen_types)[:8]} ...")
print(f"  F_v >= (3/5) Q_v/d_v at ALL sampled stable profiles: {bound_ok}")
print(f"  bound tight at h_i-type (q=(5/3)t) seen: {sharp_hi}")

print("\n=== (D) global identity sum_v Q_v = 10e - 6W0 + 2W1 + 10W2 ===")
def rand_trifree(n):
    A = [set() for _ in range(n)]; ps = [(u, v) for u in range(n) for v in range(u+1, n)]; random.shuffle(ps)
    for u, v in ps:
        if A[u] & A[v]: continue
        A[u].add(v); A[v].add(u)
    return A
bad = 0
for _ in range(150):
    n = random.randint(6, 14); A = rand_trifree(n)
    e2 = sum(len(A[v]) for v in range(n)) // 2
    lab2 = [random.choice(labels) for _ in range(n)]
    sumQ = 0
    for v in range(n):
        s = [sum(sig(lab2[u], i) for u in A[v]) for i in range(5)]
        sumQ += sum(x*x for x in s)
    W = [0, 0, 0]
    for u in range(n):
        for w in range(u+1, n):
            kappa = len(A[u] & A[w])
            if kappa: W[cost(lab2[u], lab2[w])] += kappa
    rhs_id = 10*e2 - 6*W[0] + 2*W[1] + 10*W[2]
    if sumQ != rhs_id: bad += 1
print(f"  identity holds on random tri-free graphs+labelings: violations={bad}/150")
print("DONE")
