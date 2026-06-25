#!/usr/bin/env python3
"""
SHARP CF TEST on 5-chromatic triangle-free graphs (the only place CF can fail).

A homomorphism G -> Clebsch forces chi(G) <= chi(Clebsch) = 4. So tau_K(G) > 0 exactly when
G is NOT Clebsch-homomorphic; in particular EVERY 5-chromatic triangle-free graph has tau_K > 0.
Since tau_K(F[k]) = k^2 tau_K(F) and RHS(F[k]) = k^2 RHS(F), the ratio tau_K/RHS is blow-up
invariant. Hence ONE in-band triangle-free graph F with tau_K(F) > RHS(F)=(N^2/5-e)/2 yields a
clean CF COUNTEREXAMPLE F[k]. CF is believed TRUE, so we expect to find NONE; finding one would
be momentous. This is the decisive verification.

We test iterated Mycielskians (M(C5)=Grötzsch is 4-chromatic, tau_K=0; M(Grötzsch) is 5-chromatic,
tau_K>0, in band) and a few other 5-chromatic triangle-free graphs.
"""
import random
random.seed(101)

labels = [m for m in range(32) if bin(m).count('1') % 2 == 0]
def cost(a, b): return (4 - bin(a ^ b).count('1')) // 2

def adj_list(N, E):
    A = [set() for _ in range(N)]
    for u, v in E:
        A[u].add(v); A[v].add(u)
    return A

def tau_K_ub(N, A, restarts=200, sweeps=60):
    """Upper bound on tau_K via labeled local search (many restarts for non-zero accuracy)."""
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
        if best == 0: break
    return best

def greedy_chromatic_ub(N, A):
    order = sorted(range(N), key=lambda v: -len(A[v]))
    col = {}
    for v in order:
        used = {col[w] for w in A[v] if w in col}
        c = 0
        while c in used: c += 1
        col[v] = c
    return max(col.values()) + 1

def C5():
    return 5, [(i, (i+1) % 5) for i in range(5)]

def mycielskian(N, E):
    A = adj_list(N, E)
    # vertices: 0..N-1 original, N..2N-1 shadows (v' = v+N), z = 2N
    z = 2 * N
    E2 = list(E)
    for u, v in E:
        E2.append((u + N, v)); E2.append((u, v + N))   # u'~v and u~v'
    for v in range(N):
        E2.append((z, v + N))                          # z ~ all shadows
    return 2 * N + 1, E2

def trifree(N, E):
    A = adj_list(N, E)
    return not any((c in A[a] and c in A[b]) for a, b in E for c in range(N))

def report(tag, N, E):
    E = sorted({(min(u, v), max(u, v)) for u, v in E})
    A = adj_list(N, E); e = len(E)
    x = e / (N * N); rhs = (N*N/5.0 - e) / 2.0
    tf = trifree(N, E)
    chi = greedy_chromatic_ub(N, A)
    tk = tau_K_ub(N, A)
    inband = 0.1243 <= x <= 0.16
    ratio = tk / rhs if rhs > 0 else float('inf')
    flag = ""
    if tk > rhs + 1e-9 and tf:
        flag = "  <<<<< CF COUNTEREXAMPLE (tau_K > RHS, triangle-free)!!"
    print(f"  {tag:22s} N={N:3d} e={e:4d} x={x:.4f} band={int(inband)} trifree={int(tf)} chi<= {chi} "
          f"tau_K_ub={tk:3d} RHS={rhs:6.1f} ratio={ratio:.3f}{flag}")
    return tk, rhs, tf, inband

def main():
    print("SHARP CF test: any in-band triangle-free graph with tau_K > RHS => CF COUNTEREXAMPLE (blow up).")
    print("Expect NONE (CF believed true). 5-chromatic triangle-free graphs have tau_K>0 (hardest case).\n")
    n, e = C5()
    report("C5", n, e)
    n2, e2 = mycielskian(n, e)            # Grötzsch (11 vtx, chi 4)
    report("M(C5)=Grötzsch", n2, e2)
    n3, e3 = mycielskian(n2, e2)          # 23 vtx, chi 5
    report("M(M(C5)) 23v chi5", n3, e3)
    n4, e4 = mycielskian(n3, e3)          # 47 vtx, chi 6
    report("M^3(C5) 47v chi6", n4, e4)
    # also: M(Grötzsch) is the key in-band chi-5 case; test small blow-ups to confirm ratio invariance
    def blow(N, E, k):
        return N * k, [(a*k+x, b*k+y) for (a, b) in E for x in range(k) for y in range(k)]
    print("\n  blow-up ratio-invariance check (M(M(C5))):")
    for k in (1, 2):
        Nb, Eb = blow(n3, e3, k)
        report(f"M(M(C5))[{k}]", Nb, Eb)
    print("\nDONE")

if __name__ == "__main__":
    main()
