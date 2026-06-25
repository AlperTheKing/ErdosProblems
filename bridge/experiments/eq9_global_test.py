#!/usr/bin/env python3
"""
RUNG 6 probe: does GPT Q14's wedge subtarget (eq 9) hold AT THE GLOBAL tau_K-MINIMIZER?
  (eq 9)  6 H_1 + 12 H_2  >=  17 e - N^2 - 6 n_+
where (at a labeling phi) H_j = sum over unordered pairs {u,w}, u!=w, with c(phi(u),phi(w))=j of
  h(u,w) = sum_{v in N(u)∩N(w)} 1/d_v,  and n_+ = #nonisolated vertices.
GPT proved: if (eq 9) holds at a 1-opt-stable phi then (STAR) holds there => tau_K<=RHS. The bad uniform
1-opt labeling of K_{16,64} VIOLATES eq 9 (and STAR). QUESTION: at the GLOBAL minimizer phi* (cost=tau_K),
does eq 9 hold? If yes everywhere in-band => the 2nd-moment route works AT the global min (sharp next step).
Also verifies the global identity R = 8 n_+ - 6e + 8 H_1 + 16 H_2 (eq 8) and Sum F_v >= (3/5) R.
"""
import itertools, random
random.seed(6)
labels = [m for m in range(32) if bin(m).count('1') % 2 == 0]
def sig(A, i): return -1 if (A >> i) & 1 else 1
def cost(A, B): return (4 - bin(A ^ B).count('1')) // 2
Kadj = [[j for j in range(16) if i != j and bin(labels[i] ^ labels[j]).count('1') == 4] for i in range(16)]

def best_label(N, A, restarts=120):
    nbr = [list(A[v]) for v in range(N)]; best = None; blab = None
    for _ in range(restarts):
        lab = [random.choice(labels) for _ in range(N)]; imp = True; sw = 0
        while imp and sw < 50:
            imp = False; sw += 1
            for u in range(N):
                bc, bl = None, lab[u]
                for L in labels:
                    c = sum(cost(L, lab[w]) for w in nbr[u])
                    if bc is None or c < bc: bc, bl = c, L
                if bl != lab[u]: lab[u] = bl; imp = True
        tot = sum(cost(lab[u], lab[w]) for u in range(N) for w in nbr[u] if w > u)
        if best is None or tot < best: best = tot; blab = lab[:]
        if best == 0: break
    return blab, best

def Hj_and_F(N, A, lab):
    deg = [len(A[v]) for v in range(N)]
    n_plus = sum(1 for v in range(N) if deg[v] > 0)
    # H_j via common neighbors: for each v, each unordered pair u,w in N(v) gets 1/d_v into bucket c(phi u,phi w)
    H = [0.0, 0.0, 0.0]
    for v in range(N):
        if deg[v] == 0: continue
        nb = list(A[v]); inv = 1.0 / deg[v]
        for a in range(len(nb)):
            for b in range(a+1, len(nb)):
                u, w = nb[a], nb[b]
                H[cost(lab[u], lab[w])] += inv
    # F_v
    F = 0
    for v in range(N):
        s = [sum(sig(lab[u], i) for u in A[v]) for i in range(5)]
        if all(x != 0 for x in s):
            prod = 1
            for x in s: prod *= -(1 if x > 0 else -1)
            eps = 1 if prod == -1 else 0
        else: eps = 0
        m = min(abs(x) for x in s) if s else 0
        F += sum(abs(x) for x in s) - 2*eps*m
    R = sum((sum(sum(sig(lab[u], i) for u in A[v])**2 for i in range(5)) / deg[v]) for v in range(N) if deg[v] > 0)
    return H, n_plus, F, R

def report(tag, N, A):
    e = sum(len(A[v]) for v in range(N)) // 2
    lab, tk = best_label(N, A)
    H, n_plus, F, R = Hj_and_F(N, A, lab)
    rhs9 = 17*e - N*N - 6*n_plus
    lhs9 = 6*H[1] + 12*H[2]
    rhs_star = 10*e - 0.8*N*N
    Rid = 8*n_plus - 6*e + 8*H[1] + 16*H[2]   # eq 8 identity check
    print(f"  {tag:16s} N={N:3d} e={e:4d} x={e/(N*N):.4f} tau_K={tk:4d} | "
          f"eq9 LHS={lhs9:9.1f} RHS={rhs9:7d} HOLDS={int(lhs9>=rhs9-1e-6)} | "
          f"R={R:.1f}=id{Rid:.1f}({int(abs(R-Rid)<1e-6)}) F={F} F>=3R/5={int(F>=0.6*R-1e-6)} "
          f"STAR(F>=10e-.8N²={rhs_star:.0f})={int(F>=rhs_star-1e-6)}")
    return lhs9 >= rhs9 - 1e-6

def adj(N, E):
    Aa = [set() for _ in range(N)]
    for u, v in E: Aa[u].add(v); Aa[v].add(u)
    return Aa
def C5(): return 5, [(i, (i+1) % 5) for i in range(5)]
def myc(N, E):
    z = 2*N; E2 = list(E)
    for u, v in E: E2.append((u+N, v)); E2.append((u, v+N))
    for v in range(N): E2.append((z, v+N))
    return 2*N+1, E2
def kbip(a, b):
    E = [(u, a+w) for u in range(a) for w in range(b)]
    return a+b, E
def rand_band(N, lo, hi):
    for _ in range(300):
        Aa = [set() for _ in range(N)]; ps = [(u, v) for u in range(N) for v in range(u+1, N)]
        random.shuffle(ps); cnt = 0; E = []
        tgt = random.randint(lo, hi)
        for u, v in ps:
            if cnt >= tgt: break
            if Aa[u] & Aa[v]: continue
            Aa[u].add(v); Aa[v].add(u); E.append((u, v)); cnt += 1
        if lo <= cnt <= hi: return N, E
    return None

if __name__ == "__main__":
    print("RUNG 6: does eq 9 (=> STAR => CF) hold AT THE GLOBAL tau_K-minimizer? (it FAILS at bad 1-opt K_16,64)")
    n, e = C5(); n2, e2 = myc(n, e); n3, e3 = myc(n2, e2); n4, e4 = myc(n3, e3)
    allok = True
    allok &= report("M(M(C5))", n3, adj(n3, e3))
    allok &= report("M^3(C5)", n4, adj(n4, e4))
    allok &= report("K_16,64", *[ (lambda NE: (NE[0], adj(*NE)))(kbip(16,64)) ][0])
    allok &= report("K_8,32", *[ (lambda NE: (NE[0], adj(*NE)))(kbip(8,32)) ][0])
    print("  -- random in-band graphs --")
    for N in (15, 18, 20):
        lo, hi = int(0.1243*N*N)+1, int(0.16*N*N)
        for _ in range(3):
            r = rand_band(N, lo, hi)
            if r: allok &= report(f"rand{N}", r[0], adj(*r))
    print(f"\n  eq 9 holds at global minimizer on ALL tested: {allok}")
    print("  (if True: the 2nd-moment route WORKS at the global min where it fails at bad 1-opt labelings)")
    print("DONE")
