"""P2 / round 6 - the MINIMAL criterion falsifiers (4 atoms) and the sweep maximum, exact.

A. four atoms, two edges (the graph is 2K_2, bipartite, psi = 0, ARCBOUND = 0) yet CRIT > 1/25.
B. the optimal four-atom weighting: p = sqrt(2) q gives CRIT -> (3 - 2 sqrt 2)/4 = 0.04289322.
C. proof that three atoms can never do it: bound_0 <= 1/27 < 1/25.
D. exact re-verification of the maximum found by the Gamma_m (m <= 30) exhaustive sweep.

Run:  python P2_minimal.py
"""
from fractions import Fraction as F
from itertools import combinations
import P2_verify as V1
import P2_verify2 as V2

TARGET = F(1, 25)


def show(cfg, K=14, psi=True):
    A, W = cfg.A(), cfg.W()
    bs = [cfg.bound(k) for k in range(K + 1)]
    ms = cfg.m()
    crit = min([A] + bs)
    E = [(u, v) for u, v in combinations(range(cfg.n), 2) if cfg.adj[u][v]]
    ab, arc = cfg.arcbound()
    print(f"--- {cfg.name}")
    print(f"    positions {[str(p) for p in cfg.pos]}  weights {[str(x) for x in cfg.x]}")
    print(f"    edges {E}   W = {W} = {float(W):.6f}   T/W = {float(cfg.T()/W):.6f}   "
          f"Var(g) = {cfg.var_g()}")
    print(f"    A = {A} = {float(A):.7f}   bound_0 = {bs[0]} = {float(bs[0]):.7f}   "
          f"bound_{K} = {float(bs[K]):.7f}   min_b m(b) = {min(ms)}")
    print(f"    CRIT = {crit} = {float(crit):.7f}  = {float(crit)*25:.5f} x 1/25   "
          f"{'*** FALSIFIER ***' if crit > TARGET else 'closed'}")
    print(f"    TRUTH: ARCBOUND = {ab} = {float(ab):.7f} (arc {arc})", end="")
    if psi and cfg.n <= 20:
        print(f"   psi = {cfg.psi()[0]} = {float(cfg.psi()[0]):.7f}")
    else:
        print()
    return crit


print("=" * 100)
print("A. FOUR ATOMS - the minimum possible.  Positions 0, 3e, 1/3+2e, 2/3+e  (uniform weights 1/4)")
print("   graph = two disjoint edges (2K_2): bipartite, so the TRUTH is psi = 0 and ARCBOUND = 0")
print("=" * 100)
for den in (600, 1200, 6000, 60000):
    e = F(1, den)
    cfg = V1.Config([F(0), 3 * e, F(1, 3) + 2 * e, F(2, 3) + e], [1, 1, 1, 1],
                    f"4 atoms, eps = 1/{den}")
    c1 = show(cfg)
    # independent implementation #2 on the same configuration
    M = 3 * den
    c2 = V2.IConfig(M, [0, 9, M // 3 + 6, 2 * M // 3 + 3], [1, 1, 1, 1], "impl2")
    print(f"    [independent impl #2, integer positions over M={M}: A = {c2.A()}, "
          f"bound_0 = {c2.bounds(0)[0][0]}, ARCBOUND = {c2.arcbound()[0]}]  match = "
          f"{c2.A() == cfg.A() and c2.bounds(0)[0][0] == cfg.bound(0) and c2.arcbound()[0] == cfg.arcbound()[0]}")
    assert c2.A() == cfg.A() and c2.bounds(0)[0][0] == cfg.bound(0)
    print()

print("=" * 100)
print("B. the OPTIMAL four-atom weighting.  With x = (q,p,q,p) on the same four positions:")
print("   every bound_k lies between bound_0 and bound_inf = W - p^2 = q^2, and A -> (p^2+q^2)/3;")
print("   the two meet at p = sqrt(2) q, i.e. q = (sqrt2 - 1)/2, giving CRIT -> (3-2 sqrt2)/4.")
print("=" * 100)
import math
print(f"    (3 - 2*sqrt(2))/4 = {(3 - 2 * math.sqrt(2)) / 4:.9f} = "
      f"{(3 - 2 * math.sqrt(2)) / 4 * 25:.6f} x 1/25")
for (a, b), den in ((( 12, 17), 60000), ((29, 41), 60000), ((70, 99), 200000), ((169, 239), 600000)):
    e = F(1, den)
    cfg = V1.Config([F(0), 3 * e, F(1, 3) + 2 * e, F(2, 3) + e], [a, b, a, b],
                    f"4 atoms, weights ({a},{b},{a},{b})/{2*(a+b)}, eps = 1/{den}")
    show(cfg, K=60)
    print()

print("=" * 100)
print("C. THREE atoms can never falsify the criterion (so four is the exact minimum)")
print("=" * 100)
print("   a 3-atom circle graph is triangle-free, so it has 0, 1 or 2 edges.")
print("   * 2 edges (path a-b-c):  int g^2 = x_b^2(x_a+x_c) + x_b(x_a+x_c)^2 = W (x_a+x_b+x_c) = W,")
print("     hence bound_0 = W - int g^2 = 0.")
print("   * 1 edge (a,b) plus isolated c:  int g^2 = x_a x_b (x_a + x_b), so bound_0 = x_a x_b x_c")
print("     <= 1/27 < 1/25  (AM-GM).")
print("   * 0 edges: W = 0, A = 0.")
print("   verification by direct search over exact rational 3-atom measures:")
best = F(0)
N = 60
for i in range(1, N):
    for j in range(1, N - i):
        k = N - i - j
        for shift in (F(1, 7), F(1, 5), F(3, 11)):
            for pos in ([F(0), F(1, 3) + shift, F(2, 3) + shift / 2],
                        [F(0), F(1, 3) + shift, F(2, 3) - shift],
                        [F(0), F(2, 5), F(4, 5)]):
                cfg = V1.Config(pos, [i, j, k])
                v = min([cfg.A()] + [cfg.bound(t) for t in range(5)])
                best = max(best, v)
print(f"   max CRIT over that 3-atom family = {best} = {float(best):.7f} "
      f"{'< 1/25 as proved' if best < TARGET else '*** UNEXPECTED ***'}")
assert best < TARGET

print()
print("=" * 100)
print("D. the maximum of CRIT over the exhaustive Gamma_m sweep (m <= 30): Gamma_29, q = 8")
print("=" * 100)
w29 = [1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1]
pos = [F(i, 29) for i in range(29) if w29[i]]
cfg = V1.Config(pos, [1] * 8, "Gamma_29 support {0,8,9,17,18,19,27,28}, uniform")
show(cfg, K=14)
P = [i for i in range(29) if w29[i]]
c2 = V2.IConfig(29, P, [1] * 8, "impl2")
b2, g2, m2 = c2.bounds(14)
print(f"    [impl #2] A = {c2.A()}  bound_0 = {b2[0]}  min m = {min(m2)}  ARCBOUND = {c2.arcbound()[0]}"
      f"   match = {c2.A() == cfg.A() and b2[0] == cfg.bound(0) and c2.arcbound()[0] == cfg.arcbound()[0]}")
assert c2.A() == cfg.A() and b2 == [cfg.bound(k) for k in range(15)]
print()
print("    the same 8-vertex graph (the WAGNER graph V8 = C8(1,4)) also embeds in Gamma_14, 20, 23, 26:")
for m, w in ((14, [1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1]),
             (20, [1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1]),
             (23, [1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1])):
    pos = [F(i, m) for i in range(m) if w[i]]
    c = V1.Config(pos, [1] * sum(w), f"Gamma_{m}")
    A = c.A()
    bs = [c.bound(k) for k in range(9)]
    cr = min([A] + bs)
    print(f"      Gamma_{m}: W={c.W()} A={A}={float(A):.7f} bound_k={bs[0]} "
          f"CRIT={cr}={float(cr):.7f} {'FALSIFIER' if cr > TARGET else 'closed'} "
          f"ARCBOUND={c.arcbound()[0]} psi={c.psi()[0]}")
