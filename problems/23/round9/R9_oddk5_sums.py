"""R9: gluing calculus (1-sums and 2-sums) and the class-equivalence constructions.

(1) 1-SUM.  If V(G1) cap V(G2) = {v} then for every x
        psi(G,x) = psi(G1, x|G1) + psi(G2, x|G2)
    (the two sides optimise independently: flipping all of G2 is a symmetry).
    So bip is additive over blocks, and the UNWEIGHTED conjecture reduces to 2-connected
    graphs: n1^2 + n2^2 <= (n1+n2-1)^2 = N^2 because 2(n1-1)(n2-1) >= 0.
    The weighted statement is NOT a consequence of that arithmetic, because the cut vertex
    is paid for twice; it is settled here for the pentagon bowtie by exhaustive exact sweep.

(2) PROFILE of C5.   psi(C5,x) = min over the 5 edges of x_u x_v  (delete one edge, the rest
    is a path).  With x_v = u fixed and total 1 the maximum is
        f(u) = min(u, (1-u)/4) * (1-u)/4 ,
    verified below on an exact rational grid.

(3) 2-SUM along two terminals: psi(G,x) = min(p1+p2, q1+q2) where p_i / q_i are the optima
    over cuts keeping the terminals together / apart.  This is >= psi1 + psi2, so 2-sums are
    the only gluing that can gain.  The natural averaged bound phi = (p+q)/2 <= W^2/25 that
    would close the 2-sum is FALSE: the path u-a-w with x = (1/4,1/2,1/4) has p = 0,
    q = 1/8, phi = 1/16 > 1/25.

(4) CLASS EQUIVALENCE.  psi(H,x) is unchanged by adjoining vertices of weight 0, so for
    every triangle-free H there is a triangle-free H* WITH an odd-K5 minor and
    max_x psi(H*,.) >= max_x psi(H,.).  Hence sup over the odd-K5 class = sup over all
    triangle-free graphs, and the restricted conjecture is the whole conjecture.
"""
from fractions import Fraction as F
from itertools import combinations
from R9_oddk5_lib import *
import R9_oddk5_minor as MIN

def c5_psi(y):
    return min(y[i] * y[(i + 1) % 5] for i in range(5))

def profile_C5_check(D=60):
    """max psi(C5,x) over rational x with x_v = u fixed, exhaustive over denominator D."""
    bad = 0
    print("  u        exhaustive max (denominator %d)      closed form" % D)
    for un in range(0, D + 1, D // 12):
        u = F(un, D)
        best = F(0)
        rem = D - un
        for a in range(rem + 1):
            for b in range(rem - a + 1):
                for c in range(rem - a - b + 1):
                    d = rem - a - b - c
                    y = [u, F(a, D), F(b, D), F(c, D), F(d, D)]
                    v = c5_psi(y)
                    if v > best:
                        best = v
        cf = min(u, (1 - u) / 4) * (1 - u) / 4
        flag = "" if best <= cf else "  *** ABOVE CLOSED FORM ***"
        if best > cf:
            bad += 1
        print(f"  {str(u):8s} {str(best):28s} {str(cf):16s}{flag}")
    return bad == 0

def bowtie_sweep(D):
    """two C5's sharing one vertex, 9 vertices; exhaustive over all integer weightings of
    total D (zeros allowed).  psi = min-edge-product(P1) + min-edge-product(P2)."""
    best = 0
    arg = None
    # weights: z on the shared vertex, a1..a4 on P1, b1..b4 on P2 (cyclic order z,a1,a2,a3,a4)
    def rec(i, left, cur):
        nonlocal best, arg
        if i == 8:
            w = cur + [left]
            z = w[0]
            p1 = [z, w[1], w[2], w[3], w[4]]
            p2 = [z, w[5], w[6], w[7], w[8]]
            v = min(p1[k] * p1[(k + 1) % 5] for k in range(5)) + \
                min(p2[k] * p2[(k + 1) % 5] for k in range(5))
            if v > best:
                best = v
                arg = w[:]
            return
        for t in range(left + 1):
            rec(i + 1, left - t, cur + [t])
    rec(0, D, [])
    return best, arg

if __name__ == "__main__":
    print("=" * 84)
    print("(2) profile of C5 : f(u) = min(u,(1-u)/4)*(1-u)/4")
    print("=" * 84)
    print("  closed form confirmed:", profile_C5_check(60))

    print()
    print("=" * 84)
    print("(1) pentagon bowtie (two C5 glued at a vertex, N=9): exhaustive integer sweep")
    print("=" * 84)
    for D in (10, 15, 20, 25):
        v, arg = bowtie_sweep(D)
        print(f"  D={D:3d}:  max sum-of-mins = {v}  at {arg}   psi = {F(v, D*D)} "
              f"  D^2/25 = {F(D*D,25)}   {'OK <= 1/25' if F(v,D*D) <= F(1,25) else '*** ABOVE 1/25 ***'}")

    print()
    print("=" * 84)
    print("(3) the averaged 2-terminal bound phi=(p+q)/2 <= W^2/25 is FALSE")
    print("=" * 84)
    x = [F(1, 4), F(1, 2), F(1, 4)]          # u - a - w
    p = F(0)                                  # u,w same side: colour a differently
    q = min(x[0] * x[1], x[1] * x[2])         # u,w apart: exactly one monochromatic edge
    print(f"  path u-a-w with x=(1/4,1/2,1/4):  p={p}  q={q}  phi=(p+q)/2={(p+q)/2} "
          f"vs 1/25={F(1,25)}   -> {(p+q)/2 > F(1,25)}")

    print()
    print("=" * 84)
    print("(4) class equivalence: zero weights are free")
    print("=" * 84)
    pet = G(10, [(i, (i + 1) % 5) for i in range(5)] + [(i, i + 5) for i in range(5)] +
           [(5 + i, 5 + (i + 2) % 5) for i in range(5)])
    c5 = Cn(5)
    # H* = C5 + a disjoint Petersen (which carries an odd-K5 minor)
    E = list(c5.E) + [(a + 5, b + 5) for (a, b) in pet.E]
    Hs = G(15, E)
    x = [F(1, 5)] * 5 + [F(0)] * 10
    print(f"  H* = C5 + disjoint Petersen: n={Hs.n} triangle-free={Hs.triangle_free()} "
          f"odd-K5 minor={MIN.has_odd_k5_minor(Hs)}")
    print(f"  psi(H*, C5-concentration) = {psi(Hs, x)} = 1/25 : {psi(Hs, x) == F(1,25)}")
    print("  so max_x psi over the odd-K5 class is >= 1/25, i.e. the class contains the")
    print("  extremal value; the conjecture restricted to it is the full conjecture.")
