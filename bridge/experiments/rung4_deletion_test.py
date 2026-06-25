#!/usr/bin/env python3
"""
RUNG 4 test: the deletion-distance bound (Q13 eq 25 + per-vertex recursion eq 11).
If deleting vertices v1,v2,... (in order) makes G Clebsch-homomorphic, then
  tau_K(G) <= sum_j Q(deg at deletion time)  [eq 11 chained].
We greedily pick the vertex whose deletion most reduces tau_K_ub, delete until tau_K_ub=0, and
sum Q(current degree). If this sum <= RHS=(N^2/5-e)/2, then tau_K(G) <= RHS (CF holds on G).
TEST: is sum_Q <= RHS on the band? (Mycielskians + census extremals.) Where is it tight/loose?
NOTE: sum_Q is an UPPER bound on tau_K via a SPECIFIC (greedy) deletion order, hence >= the true
min-deletion bound >= tau_K. sum_Q<=RHS is SUFFICIENT for CF on G; sum_Q>RHS is inconclusive (greedy loose).
"""
import random
random.seed(17)
labels = [m for m in range(32) if bin(m).count('1') % 2 == 0]
def cost(a, b): return (4 - bin(a ^ b).count('1')) // 2
def Q(d): return 3*(d//4) + (1 if d % 4 in (2, 3) else 0)

def tau_ub(verts, A, restarts=60):
    vs = list(verts); nbr = {v: [w for w in A[v] if w in verts] for v in vs}
    best = None
    for _ in range(restarts):
        lab = {v: random.choice(labels) for v in vs}; imp = True; sw = 0
        while imp and sw < 35:
            imp = False; sw += 1
            for u in vs:
                bc, bl = None, lab[u]
                for L in labels:
                    c = sum(cost(L, lab[w]) for w in nbr[u])
                    if bc is None or c < bc: bc, bl = c, L
                if bl != lab[u]: lab[u] = bl; imp = True
        tot = sum(cost(lab[u], lab[w]) for u in vs for w in nbr[u] if w > u)
        if best is None or tot < best: best = tot
        if best == 0: break
    return best

def greedy_deletion_bound(N, A):
    verts = set(range(N))
    total = 0
    while tau_ub(verts, A, 40) > 0:
        # pick vertex whose deletion most reduces tau_K_ub (tie -> lowest Q)
        best_v, best_key = None, None
        cand = sorted(verts, key=lambda v: -len([w for w in A[v] if w in verts]))
        # evaluate a shortlist (highest current-degree first; they tend to be in the frustrated core)
        for v in cand[:max(6, len(cand)//3)]:
            deg = len([w for w in A[v] if w in verts])
            t2 = tau_ub(verts - {v}, A, 30)
            key = (t2, Q(deg))
            if best_key is None or key < best_key:
                best_key, best_v = key, v
        deg = len([w for w in A[best_v] if w in verts])
        total += Q(deg)
        verts.discard(best_v)
    return total

def adj(N, E):
    A = [set() for _ in range(N)]
    for u, v in E: A[u].add(v); A[v].add(u)
    return A
def C5(): return 5, [(i, (i+1) % 5) for i in range(5)]
def myc(N, E):
    z = 2*N; E2 = list(E)
    for u, v in E: E2.append((u+N, v)); E2.append((u, v+N))
    for v in range(N): E2.append((z, v+N))
    return 2*N+1, E2
def decode_g6(s):
    s = s.strip(); data = [ord(c) - 63 for c in s]; n = data[0]; bits = []
    for d in data[1:]:
        for k in range(5, -1, -1): bits.append((d >> k) & 1)
    A = [set() for _ in range(n)]; idx = 0
    for j in range(1, n):
        for i in range(j):
            if idx < len(bits) and bits[idx]: A[i].add(j); A[j].add(i)
            idx += 1
    return n, A

def report(tag, N, A):
    e = sum(len(A[v]) for v in range(N)) // 2
    rhs = (N*N/5.0 - e) / 2.0
    sq = greedy_deletion_bound(N, A)
    tk = tau_ub(set(range(N)), A, 120)
    ok = sq <= rhs + 1e-9
    print(f"  {tag:22s} N={N:3d} e={e:4d} x={e/(N*N):.4f} tau_K_ub={tk:3d} RHS={rhs:6.1f} "
          f"sum_Q(greedy)={sq:4d}  sum_Q<=RHS={int(ok)}  (sum_Q/RHS={sq/rhs:.2f})", flush=True)
    return ok, sq, rhs

if __name__ == "__main__":
    print("RUNG 4: greedy deletion-distance bound sum_Q vs RHS (sum_Q<=RHS => tau_K<=RHS => CF on G):")
    n, e = C5(); A0 = adj(n, e)
    n2, e2 = myc(n, e); n3, e3 = myc(n2, e2)
    report("M(C5)=Grötzsch", n2, adj(n2, e2))
    report("M(M(C5)) 23v", n3, adj(n3, e3))
    n4, e4 = myc(n3, e3); report("M^3(C5) 47v", n4, adj(n4, e4))
    # census extremals (worst-R small graphs found earlier)
    for tag, g6 in [("N11 worst R", "J?`@F_{Ubo?"), ("N12 worst R", "K?AA@Bw^DsBw")]:
        n, A = decode_g6(g6); report(tag, n, A)
    print("DONE")
