"""audit_P4_structure — what P4's item-7 falsifiers actually ARE.

Finding: after collapsing twins, P4's witness W9 is the UNIFORM measure on the Wagner graph
Gamma_8 = And(3), re-embedded into Gamma_20 so that the mean adjacent distance T drops.
All CUT invariants (W, g, m(b), bound_k, psi, ARCBOUND) are preserved by the re-embedding;
A = W - 2T is NOT (it is embedding-dependent).  On its own circle Gamma_8 the uniform measure has
A = 1/32 <= 1/25, so hypothesis 1 of item 7 fails there and only the Gamma_20 re-embedding refutes
item 7.  This also gives a closed-form family of hierarchy failures:

    uniform measure on a k-regular triangle-free graph on N vertices:
        W = k/(2N),  g = k/N,  m(b) = k(N-2k)/(2N^2)  for every b,  so every bound_k equals it.
    For And(k) = Gamma_{3k-1}:  m = k(k-1)/(2(3k-1)^2)  ->  1/25 at k=2 (C5) and > 1/25 for k>=3.
"""
from fractions import Fraction as F
from itertools import combinations
from audit_P4_core import (adj_matrix, normalise, W_of, T_of, A_of, g_of, m_of, bound_k,
                           arcbound, psi_bruteforce, triangle_free)

ONE25 = F(1, 25)

WIT = {
    "W8":  (20, [0, 3, 4, 0, 1, 0, 0, 2, 4, 4, 0, 0, 0, 0, 4, 4, 3, 1, 0, 0]),
    "W9":  (20, [0, 0, 5, 5, 5, 0, 0, 0, 0, 5, 5, 2, 0, 0, 0, 3, 5, 5, 0, 0]),
    "W10": (20, [0, 5, 5, 0, 0, 0, 0, 6, 4, 5, 0, 0, 0, 0, 5, 4, 6, 0, 0, 0]),
}


def twin_collapse(M, w):
    adj = adj_matrix(M)
    supp = [i for i in range(M) if w[i]]
    nbr = {u: frozenset(v for v in supp if v != u and adj[u][v]) for u in supp}
    cls = {}
    for u in supp:
        cls.setdefault(nbr[u], []).append(u)
    keys = list(cls)
    reps = [cls[k][0] for k in keys]
    wt = [sum(w[u] for u in cls[k]) for k in keys]
    A = [[adj[reps[a]][reps[b]] if a != b else False for b in range(len(keys))]
         for a in range(len(keys))]
    return [cls[k] for k in keys], wt, A


def iso_to_gamma(A, wt):
    """is the collapsed graph isomorphic to some Gamma_m (m = #vertices)?  brute force"""
    n = len(A)
    G = adj_matrix(n)
    from itertools import permutations
    if n > 9:
        return None
    for p in permutations(range(n)):
        if all(A[u][v] == G[p[u]][p[v]] for u in range(n) for v in range(n)):
            return p
    return None


def uniform_profile(M):
    adj = adj_matrix(M)
    x = [F(1, M)] * M
    W = W_of(x, adj)
    A = A_of(x, adj, M)
    g = g_of(x, adj)[0]
    mb = m_of(0, x, adj, M)
    ps = psi_bruteforce(x, adj, M) if M <= 22 else None
    return W, A, g, mb, ps


if __name__ == "__main__":
    print("=== what the falsifiers are ===")
    for name, (M, w) in WIT.items():
        cls, wt, A = twin_collapse(M, w)
        n = len(cls)
        p = iso_to_gamma(A, wt)
        deg = [sum(r) for r in A]
        print(f"{name}: support {sum(1 for t in w if t)} atoms -> {n} twin classes, "
              f"class weights {wt} (of {sum(w)}), degrees {deg}, triangle-free={triangle_free(A)}")
        print(f"      classes: {cls}")
        print(f"      isomorphic to Gamma_{n}?  {'YES via ' + str(p) if p else 'no'}"
              + ("   [Gamma_8 = Wagner = And(3)]" if n == 8 and p else ""))

    print("\n=== the same graph on its OWN circle: A is embedding-dependent, m(b) is not ===")
    print(f"{'M':>4s} {'W':>10s} {'A':>12s} {'g':>8s} {'m(b)':>12s} {'psi':>10s}  A>1/25  m>1/25")
    for M in (5, 8, 11, 14, 17, 20):
        W, A, g, mb, ps = uniform_profile(M)
        print(f"{M:4d} {str(W):>10s} {str(A):>12s} {str(g):>8s} {str(mb):>12s} {str(ps):>10s}"
              f"   {str(A > ONE25):>5s}  {str(mb > ONE25):>5s}")
    print("  (rows are the uniform measures on Gamma_5=C5, Gamma_8=Wagner=And(3), Gamma_11=And(4),")
    print("   Gamma_14=And(5), Gamma_17=And(6), Gamma_20=And(7).)")
    print("  m(b) = k(k-1)/(2(3k-1)^2) exactly:",
          [f"k={k}: {F(k*(k-1), 2*(3*k-1)**2)}" for k in range(2, 8)])
    print("  so EVERY uniform Andrasfai measure with k>=3 already defeats the whole bound_k")
    print("  hierarchy; what P4's search had to add was an embedding making A > 1/25 as well.")

    print("\n=== W9 = uniform Wagner re-embedded : invariants vs non-invariants ===")
    M, w = WIT["W9"]
    adj20 = adj_matrix(M)
    x20 = normalise(w)
    adj8 = adj_matrix(8)
    x8 = [F(1, 8)] * 8
    for label, (a, x, mm) in {"W9 on Gamma_20": (adj20, x20, 20),
                              "uniform Gamma_8": (adj8, x8, 8)}.items():
        supp = [i for i in range(mm) if x[i]]
        print(f"  {label:16s} W={str(W_of(x,a)):>8s} T/W={float(T_of(x,a,mm)/W_of(x,a)):.6f} "
              f"A={str(A_of(x,a,mm)):>8s} g={str(g_of(x,a)[supp[0]]):>6s} "
              f"m(b)={str(m_of(supp[0],x,a,mm)):>8s} bound_0={str(bound_k(0,x,a,mm)):>8s} "
              f"psi={str(psi_bruteforce(x,a,mm)):>8s} ARCBOUND={str(arcbound(x,a,mm)):>8s}")
    print("  => identical W, g, m(b), bound_0, psi, ARCBOUND;  A differs (3/64 vs 1/32) because")
    print("     A depends on the DISTANCES, not on the graph.  Hypothesis 1 of item 7 (A > 1/25)")
    print("     therefore holds only for the Gamma_20 embedding.")
