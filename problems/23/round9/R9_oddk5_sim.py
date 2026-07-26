"""R9: the SIMULATION construction.

Lemma S  (odd subdivision).  If H is obtained from G by replacing every edge with a
path of odd length, then bip(H) = bip(G) and Lambda(H) = Lambda(G).

Lemma SIM (weighted simulation).  For every graph G and every cost vector
c: E(G) -> (0,1] cap Q there is a TRIANGLE-FREE graph H (the twice subdivision of G)
and a rational weight x >= 0 on V(H) with
        psi(H,x)      = bip_c(G)   * s^-2 ,
        Lambda(H,x)   = Lambda_c(G)* s^-2 ,   s = sum x,
so the ratio psi/Lambda of a triangle-free graph under PRODUCT weights realises the
integrality gap of an ARBITRARY weighted instance.
Construction: keep V(G) at weight 1; replace edge e=uv by u - a_e - b_e - v with
x[a_e] = 1, x[b_e] = c_e.  Then min(x_u x_a, x_a x_b, x_b x_v) = c_e.

This file verifies both lemmas by brute force in exact arithmetic.
"""
from fractions import Fraction as F
from R9_oddk5_lib import *
import itertools, random

def wbip(g, c):
    return bip(g, c)

def build_sim(g, c):
    """twice subdivision with the weights described above; returns (H, x, mapping)"""
    n = g.n
    edges = []
    x = [F(1)] * n
    nxt = n
    for e in g.E:
        a, b = e
        ia, ib = nxt, nxt + 1
        nxt += 2
        edges += [(a, ia), (ia, ib), (ib, b)]
        x += [F(1), F(c[e])]
    return G(nxt, edges), x

def run():
    print("=" * 78)
    print("TEST A : Lemma S  (odd subdivision preserves bip and Lambda)")
    print("=" * 78)
    pet = G(10, [(i, (i + 1) % 5) for i in range(5)] + [(i, i + 5) for i in range(5)] +
           [(5 + i, 5 + (i + 2) % 5) for i in range(5)])
    k33 = G(6, [(i, 3 + j) for i in range(3) for j in range(3)])
    cases = [("C5", Cn(5)), ("K4", Kn(4)), ("K5", Kn(5)), ("Petersen", pet), ("K33", k33),
             ("K33+e", G(6, k33.E + [(0, 1)]))]
    for nm, g in cases:
        b0 = bip(g)
        r0 = Lambda(g); verify_Lambda(g, r0)
        row = [f"{nm:9s} n={g.n:2d} m={g.m:2d} bip={b0} Lam={r0['value']}"]
        for k in (2, 4):        # path length k+1 = 3, 5  (odd)
            if g.m * k + g.n > 25:
                row.append(f"  [k={k} skipped: {g.n + g.m * k} vertices]")
                continue
            H, _ = subdivide(g, k)
            b1 = bip(H)
            r1 = Lambda(H); verify_Lambda(H, r1)
            tag = "OK " if (b1 == b0 and r1['value'] == r0['value']) else "*** MISMATCH ***"
            row.append(f"  odd-sub k={k}: n={H.n} tf={H.triangle_free()} og={odd_girth(H)} "
                       f"bip={b1} Lam={r1['value']} {tag}")
        # control: even subdivision (path length 2) must NOT preserve parity
        H, _ = subdivide(g, 1)
        if H.n <= 20:
            b2 = bip(H)
            r2 = Lambda(H)
            row.append(f"  EVEN-sub k=1 (control): bip={b2} Lam={r2['value']} "
                       f"{'(changed, as expected)' if b2 != b0 else '(unchanged)'}")
        print("\n".join(row))

    print()
    print("=" * 78)
    print("TEST B : Lemma SIM  (arbitrary weighted instance -> triangle-free + product weights)")
    print("=" * 78)
    rnd = random.Random(20260726)
    tests = [("K4", Kn(4)), ("C5", Cn(5)), ("K33+e", G(6, k33.E + [(0, 1)]))]
    allok = True
    for nm, g in tests:
        for trial in range(4):
            if trial == 0:
                c = {e: F(1) for e in g.E}
            else:
                c = {e: F(rnd.randint(1, 12), 12) for e in g.E}
            H, x = build_sim(g, c)
            assert H.triangle_free(), "simulation graph must be triangle-free"
            lhs_psi = psi(H, x)
            rhs_psi = wbip(g, c)
            rH = LambdaX(H, x); verify_Lambda(H, rH, prodw(H, x))
            rG = Lambda(g, c);  verify_Lambda(g, rG, c)
            good = (lhs_psi == rhs_psi and rH['value'] == rG['value'])
            allok &= good
            print(f"{nm:6s} trial{trial}  N(H)={H.n:3d}  psi(H,x)={lhs_psi}  bip_c(G)={rhs_psi}  "
                  f"Lam(H,x)={rH['value']}  Lam_c(G)={rG['value']}  "
                  f"gap={rhs_psi/rG['value'] if rG['value'] else 'inf'}  "
                  + ("OK" if good else "*** MISMATCH ***"))
    print("TEST B:", "ALL OK" if allok else "FAILURES")

    print()
    print("=" * 78)
    print("TEST C : the subdivided-K_n family (exact)")
    print("=" * 78)
    print(f"{'n':>3} {'N=n^2':>6} {'|E|':>5} {'bip':>5} {'Lambda':>8} {'ratio':>9} {'psi':>16} {'Lam(x)':>16}")
    for n in range(4, 12):
        g = Kn(n)
        b = n * (n - 1) // 2 - (n * n) // 4
        lam = F(n * (n - 1), 6)
        N = n * n
        if n <= 5:                    # verify the closed forms by brute force where feasible
            H, _ = subdivide(g, 2)
            assert bip(H) == b and Lambda(H)['value'] == lam, "closed form failed"
        print(f"{n:>3} {N:>6} {3*g.m:>5} {b:>5} {str(lam):>8} {str(F(b)/lam):>9} "
              f"{str(F(b, N*N)):>16} {str(lam/(N*N)):>16}")

if __name__ == "__main__":
    run()
