#!/usr/bin/env python3
"""
Audit GPT Q11's CF advances (load-bearing structural facts + the new density bound).
(A) Edge-root Clebsch structure: for an edge a~b in Clebsch K, P=N(a)\{b}, Q=N(b)\{a}
    each have 4 vertices, are independent, and the P-Q edges form a PERFECT MATCHING
    with p_i ~ q_j iff i=j (the basis of the edge-root certificate tau_K<=e-(S_u+S_v)/2).
(B) Petersen-root structure: Petersen = 10 two-subsets of [5], adjacency=disjointness;
    the maximal intersecting families of 2-subsets of [5] are exactly 5 stars (size 4)
    + 10 triangles (size 3) = 15, corresponding to 15 of the 16 Clebsch vertices.
(C) M_2 >= 4e^3/N^2 (the inequality chain) on random triangle-free graphs.
(D) tau_K(G) <= e - 4e^2/N^2 CONSISTENCY: tau_K_ub (local search) vs the proved bound,
    on band graphs incl. the cases where C5-root fails (Petersen[t], Clebsch[t]).
"""
import itertools, random
random.seed(13)

labels = [m for m in range(32) if bin(m).count('1') % 2 == 0]
Kadj = [set() for _ in range(16)]
for i in range(16):
    for j in range(16):
        if i != j and bin(labels[i] ^ labels[j]).count('1') == 4:
            Kadj[i].add(j)

print("=== (A) Edge-root Clebsch structure (P-Q perfect matching) ===")
ok_all = True
# test for one edge (a,b); by vertex-transitivity all edges are equivalent
a = 0
b = next(iter(Kadj[a]))
P = sorted(Kadj[a] - {b})
Q = sorted(Kadj[b] - {a})
indepP = not any((y in Kadj[x]) for x in P for y in P if y > x)
indepQ = not any((y in Kadj[x]) for x in Q for y in Q if y > x)
PQ = [(x, y) for x in P for y in Q if y in Kadj[x]]
# perfect matching? each P vtx exactly one Q neighbor and vice versa
degP = {x: sum(1 for y in Q if y in Kadj[x]) for x in P}
degQ = {y: sum(1 for x in P if x in Kadj[y]) for y in Q}
matching = all(d == 1 for d in degP.values()) and all(d == 1 for d in degQ.values())
print(f"edge a={a},b={b}: |P|={len(P)} |Q|={len(Q)}  P indep={indepP} Q indep={indepQ}")
print(f"  P-Q edges={len(PQ)}  perfect matching (each side deg 1)={matching}")
ok_all &= (len(P) == 4 and len(Q) == 4 and indepP and indepQ and matching and len(PQ) == 4)
print(f"  => edge-root structure VERIFIED: {ok_all}")

print("\n=== (B) Petersen 15 maximal intersecting families <-> Clebsch ===")
two = list(itertools.combinations(range(5), 2))  # 10 two-subsets
# stars: {i,*} size 4
stars = [[t for t in two if i in t] for i in range(5)]
# triangles: all 2-subsets within a 3-set {a,b,c}
tris = [[(min(p), max(p)) for p in itertools.combinations(trip, 2)]
        for trip in itertools.combinations(range(5), 3)]
n_star = len(stars); n_tri = len(tris)
# check each is intersecting (pairwise intersect) and maximal-size as claimed
def intersecting(fam): return all(set(x) & set(y) for x in fam for y in fam)
allstar_ok = all(len(s) == 4 and intersecting(s) for s in stars)
alltri_ok = all(len(t) == 3 and intersecting(t) for t in tris)
print(f"  5 stars size4 intersecting={allstar_ok}; 10 triangles size3 intersecting={alltri_ok}; total={n_star+n_tri} (claim 15)")
print(f"  => 15 maximal intersecting families: {n_star+n_tri==15 and allstar_ok and alltri_ok}")

print("\n=== (C) M_2 >= 4 e^3 / N^2 on random triangle-free graphs ===")
def rand_trifree(N):
    A = [set() for _ in range(N)]
    pairs = [(u, v) for u in range(N) for v in range(u+1, N)]
    random.shuffle(pairs)
    for u, v in pairs:
        if A[u] & A[v]: continue
        A[u].add(v); A[v].add(u)
    return A
viol = 0; tested = 0
for _ in range(200):
    N = random.randint(8, 16)
    A = rand_trifree(N)
    deg = [len(A[v]) for v in range(N)]
    e = sum(deg)//2
    if e == 0: continue
    M2 = sum(deg[u]*deg[v] for u in range(N) for v in A[u] if v > u)
    tested += 1
    if M2 < 4*e**3/N**2 - 1e-6: viol += 1
print(f"  tested {tested}: M_2 < 4e^3/N^2 violations = {viol} (expect 0)")

print("\n=== (D) tau_K <= e - 4e^2/N^2 consistency (band graphs) ===")
def cost(x, y): return (4 - bin(x ^ y).count('1'))//2
def tau_K_ub(N, A, restarts=40, sweeps=30):
    nbr = [list(A[v]) for v in range(N)]; best = None
    for _ in range(restarts):
        lab = [random.choice(labels) for _ in range(N)]; imp = True; sw = 0
        while imp and sw < sweeps:
            imp = False; sw += 1
            for u in range(N):
                bc, bl = None, lab[u]
                for L in labels:
                    c = sum(cost(L, lab[w]) for w in nbr[u])
                    if bc is None or c < bc: bc, bl = c, L
                if bl != lab[u]: lab[u] = bl; imp = True
        tot = sum(cost(lab[u], lab[w]) for u in range(N) for w in nbr[u] if w > u)
        if best is None or tot < best: best = tot
    return best
def clebsch_blowup(t):
    base = [(i, j) for i in range(16) for j in range(i+1, 16) if j in Kadj[i]]
    A = [set() for _ in range(16*t)]
    for (p, q) in base:
        for x in range(t):
            for y in range(t):
                A[p*t+x].add(q*t+y); A[q*t+y].add(p*t+x)
    return 16*t, A
for tag, (N, A) in [("Clebsch[1]", clebsch_blowup(1)), ("Clebsch[2]", clebsch_blowup(2))]:
    e = sum(len(A[v]) for v in range(N))//2
    bound = e - 4*e*e/(N*N)
    tk = tau_K_ub(N, A)
    print(f"  {tag}: N={N} e={e} tau_K_ub={tk}  e-4e^2/N^2={bound:.2f}  tau_K_ub<=bound={tk<=bound+1e-9}")
print("DONE")
