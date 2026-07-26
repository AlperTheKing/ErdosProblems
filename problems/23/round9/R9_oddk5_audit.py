"""R9: adversarial re-checks of the load-bearing claims, each by a route that does NOT
reuse the machinery it is checking.

A1  tau*_w <= 10/3 on Petersen : enumerate ALL cycles, check every odd one carries >= 3
    non-spoke edges, so y = 1/3 on the ten non-spoke edges is feasible.  (No LP code.)
A2  tau_w = 4 on Petersen : independent loop over all 2^10 colourings (not 2^9), and the
    structural argument min_k [C(k,2)+C(5-k,2)] = 4.
A3  Higman-Sims : direct exact check of A^2 = 22I + 6(J-I-A) by set intersections, the
    explicit 750-edge cut re-counted, and the spectral arithmetic done by hand.
A4  Lemma SIM with a genuine gap : K5 with integer costs, brute force on the 25-vertex
    subdivision, compared with the weighted bip / Lambda of K5 itself.
A5  Lambda(K_n) = m/3 : the packing z = 1/(n-2) on all triangles, load re-counted.
"""
from fractions import Fraction as F
from itertools import combinations
from R9_oddk5_lib import *
import R9_oddk5_srg as S
import R9_oddk5_sim as SIM

fails = []
def want(name, cond, info=""):
    print(("PASS " if cond else "FAIL ") + name + ("   " + str(info) if info else ""))
    if not cond:
        fails.append(name)

# ------------------------------------------------------------------ A1 / A2
pet = G(10, [(i, (i + 1) % 5) for i in range(5)] + [(i, i + 5) for i in range(5)] +
       [(5 + i, 5 + (i + 2) % 5) for i in range(5)])
spokes = {(i, i + 5) for i in range(5)}
cyc = all_cycles(pet, only_odd=False)
oddc = [c for c in cyc if len(c) % 2 == 1]
lens = sorted({len(c) for c in cyc})
oddlens = sorted({len(c) for c in oddc})
want("A1 cycle spectrum of Petersen", lens == [5, 6, 8, 9], lens)
want("A1 odd cycle lengths", oddlens == [5, 9], oddlens)
worst = min(sum(1 for e in c if e not in spokes) for c in oddc)
want("A1 every odd cycle has >= 3 non-spoke edges", worst >= 3, f"minimum = {worst}")
want("A1 #odd cycles", len(oddc) == 12 + 20, f"{len(oddc)} (12 pentagons + 20 nonagons)")
cover = F(1, 3) * len([e for e in pet.E if e not in spokes])
want("A1 cover cost", cover == F(10, 3), cover)

best = None
for mask in range(1 << 10):
    tot = 0
    for (a, b) in pet.E:
        if ((mask >> a) & 1) == ((mask >> b) & 1):
            tot += 5 if (a, b) in spokes else 1
    best = tot if best is None else min(best, tot)
want("A2 tau_w = 4 (all 2^10 colourings, weights 1/5)", best == 4, best)
k5mono = min(k * (k - 1) // 2 + (5 - k) * (4 - k) // 2 for k in range(6))
want("A2 structural value min_k [C(k,2)+C(5-k,2)]", k5mono == 4, k5mono)
want("A2 GAP 4 > 10/3", F(4) > F(10, 3))

# ------------------------------------------------------------------ A3
hs = S.higman_sims()
adj = [set(a) for a in hs.adj]
n = hs.n
ok = True
for u in range(n):
    if len(adj[u]) != 22:
        ok = False
for u in range(n):
    for v in range(u + 1, n):
        c = len(adj[u] & adj[v])
        if v in adj[u]:
            if c != 0:
                ok = False
        elif c != 6:
            ok = False
want("A3 Higman-Sims is SRG(100,22,0,6) by direct counting", ok)
want("A3 triangle-free", hs.triangle_free())
want("A3 odd girth 5", odd_girth(hs) == 5)
cut, side = maxcut_local(hs, iters=30, seed=3)
want("A3 explicit cut with >= 750 edges", cut >= 750, cut)
want("A3 re-count of that cut", cut == cut_value(hs, side))
# spectral: lambda_min = -8 from (lam-mu)^2+4(k-mu) = 36+64 = 100
want("A3 lambda_min = -8 from the parameters", ((0 - 6) - 10) // 2 == -8)
lb = F(hs.m, 2) + F(hs.n * (-8), 4)
want("A3 bip >= 350", lb == 350, lb)
want("A3 bip <= 350 from the cut", hs.m - cut == 350, hs.m - cut)
want("A3 Lambda <= 220 (y = 1/5)", F(hs.m, 5) == 220)
want("A3 ratio 35/22", F(350) / F(220) == F(35, 22))
want("A3 psi = 7/200 < 1/25", F(350, 100 * 100) == F(7, 200) and F(7, 200) < F(1, 25))

# ------------------------------------------------------------------ A4
k5 = Kn(5)
for cvec in ([1] * 10, [1, 1, 1, 1, 1, 1, 1, 1, 1, 2], [3, 1, 2, 1, 1, 3, 2, 1, 1, 2]):
    c = {e: F(cvec[i], 3) for i, e in enumerate(k5.E)}
    H, x = SIM.build_sim(k5, c)
    assert H.n == 25 and H.triangle_free()
    lhs = psi(H, x)
    rhs = bip(k5, c)
    lam_H = LambdaX(H, x); verify_Lambda(H, lam_H, prodw(H, x))
    lam_G = Lambda(k5, c); verify_Lambda(k5, lam_G, c)
    want(f"A4 SIM on K5 costs {cvec}", lhs == rhs and lam_H['value'] == lam_G['value'],
         f"psi={lhs} bip_c={rhs} Lam={lam_H['value']}/{lam_G['value']} "
         f"gap={rhs/lam_G['value']}")

# ------------------------------------------------------------------ A5
for nn in (5, 6, 7, 9):
    g = Kn(nn)
    tri = [t for t in combinations(range(nn), 3)]
    load = {e: F(0) for e in g.E}
    for t in tri:
        for e in combinations(sorted(t), 2):
            load[e] += F(1, nn - 2)
    okload = all(load[e] == 1 for e in g.E)
    val = F(len(tri), nn - 2)
    want(f"A5 K{nn}: packing z=1/{nn-2} on {len(tri)} triangles is feasible", okload)
    want(f"A5 K{nn}: packing value = m/3 = {F(g.m,3)}", val == F(g.m, 3), val)
    want(f"A5 K{nn}: bip = {g.m - (nn*nn)//4}", bip(g) == g.m - (nn * nn) // 4)

print()
print("AUDIT:", "ALL PASS" if not fails else f"{len(fails)} FAILURES: {fails}")
