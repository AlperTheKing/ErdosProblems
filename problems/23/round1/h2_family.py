"""H2 (i)+(ii): the explicit parametric family, and its exact values at the target orders.

THE FAMILY.  Let C5 have vertices u_0..u_4 (indices mod 5).  The generalised Mycielskian
tower over C5 is

    level 0 : u_0..u_4                  (the C5 itself)
    level 1 : w_0..w_4  with w_i ~ u_{i-1}, u_{i+1}     (shadows: N(w_i) = N_{C5}(u_i))
    level 2 : z         with z ~ w_0..w_4               (apex)

Level 0+1+2 = the Grotzsch graph M(C5), 11 vertices, 20 edges, maximal triangle-free.

The H2 family is the set of BLOW-UPS of induced subgraphs of this tower (and of its
higher analogues), i.e. the graphs

    F(a_0..a_4; b_0..b_4; c) = M(C5)[a_0..a_4, b_0..b_4, c],

with independent parts of the stated sizes.  It contains
  * every C5 blow-up            (b = 0, c = 0),
  * the exact extremal graph at N = 12,  K?BD@g]Qvo^?  =  F(1,1,1,1,1; 1,1,1,1,1; 2),
  * the exact extremal graph at N = 13,  L??FFB_~?~^_Fw = F(3,3,2,3,2; 0; 0)  (a C5 blow-up).

By the blow-up identity (h2_blowup_theory.py),
    bip(F) = min over the 2^11 cuts S of V(M(C5)) of the monochromatic weight sum,
which this script evaluates exactly in integer arithmetic.
"""
import itertools, sys
from h2_lib import *
from h2_blowup_theory import bip_blowup


def grotzsch():
    E = [(i, (i + 1) % 5) for i in range(5)]
    for i in range(5):
        E += [(5 + i, (i - 1) % 5), (5 + i, (i + 1) % 5), (5 + i, 10)]
    return 11, sorted({(min(a, b), max(a, b)) for a, b in E})


def gen_mycielski_tower(r):
    """r levels of C5 copies plus one apex; r=1 gives C5+apex(deg 5), r=2 gives Grotzsch."""
    n = 5
    E = [(i, (i + 1) % 5) for i in range(5)]
    for lev in range(r - 1):
        for i in range(5):
            E += [(lev * 5 + i, (lev + 1) * 5 + (i - 1) % 5),
                  (lev * 5 + i, (lev + 1) * 5 + (i + 1) % 5)]
    apex = 5 * r
    for i in range(5):
        E.append(((r - 1) * 5 + i, apex))
    return 5 * r + 1, sorted({(min(a, b), max(a, b)) for a, b in E})


def best_over_weights(bn, bedges, N, lo=0):
    """Exhaustive maximisation of bip over integer weight vectors summing to N."""
    best, argb = -1, None
    for w in compositions(N, bn, lo):
        v = bip_blowup(bn, bedges, list(w))
        if v > best:
            best, argb = v, w
    return best, argb


if __name__ == "__main__":
    gn, ge = grotzsch()
    gadj = edges_to_adj(gn, ge)
    print("Grotzsch M(C5):", g6_encode(gn, gadj), "n=", gn, "m=", len(ge),
          "triangle-free:", is_triangle_free(gn, gadj))

    # sanity: the N=12 extremal is F(1^5;1^5;2)
    N12, adj12, _ = blowup(gn, ge, [1] * 10 + [2])
    print("F(1^5;1^5;2): N=", N12, "m=", num_edges(N12, adj12),
          "triangle-free:", is_triangle_free(N12, adj12),
          "bip(exhaustive maxcut)=", bip_exhaustive(N12, adj12),
          "bip(identity)=", bip_blowup(gn, ge, [1] * 10 + [2]))

    print("\n--- exact max of bip over ALL blow-ups of Grotzsch, per order N ---")
    print(" N   bipmax   N^2/25   25bip/N^2   argmax weights (a;b;c)")
    for N in list(range(5, 31)):
        b, w = best_over_weights(gn, ge, N)
        print(f"{N:3d}  {b:5d}   {N*N/25:7.2f}   {25*b/(N*N):.6f}   "
              f"a={w[0:5]} b={w[5:10]} c={w[10]}")

    print("\n--- generalised Mycielskian towers over C5 (r levels + apex) ---")
    for r in (1, 2, 3):
        n, e = gen_mycielski_tower(r)
        adj = edges_to_adj(n, e)
        print(f" r={r}: n={n} m={len(e)} tf={is_triangle_free(n, adj)} g6={g6_encode(n,adj)}"
              f" bip(all weights 1)={bip_blowup(n, e, [1]*n)}")
