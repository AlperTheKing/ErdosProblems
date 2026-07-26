"""R9: the Petersen graph is NOT weakly bipartite.

The round-brief states that Guenin's theorem "covers C5 and ALL its blow-ups, all planar
triangle-free graphs, the Wagner graph and the Petersen graph".  The last item is false.

Explicit odd-K5 minor: switch at the inner 5-set B = {b_0..b_4}.  Every spoke a_i b_i has
exactly one end in B, so it becomes EVEN; the 5 outer and the 5 inner edges have 0 resp. 2
ends in B, so they stay ODD.  Contracting the 5 (now even) spokes leaves K5 on the classes
{a_i,b_i}, with the outer edges giving the pairs {i,i+1} and the inner edges the pairs
{i,i+2} -- all 10 pairs, all odd.  That is the all-odd K5.

Explicit integrality gap (this is the object Guenin's theorem is about):
w = 1 on the 10 outer/inner edges, w = 5 on the 5 spokes.  Then tau_w = 4 > 10/3 = tau*_w.
Both numbers are computed here exactly, tau by exhaustive enumeration of all 2^9 cuts and
tau* by row generation with a two-sided rational certificate.
"""
from fractions import Fraction as F
from R9_oddk5_lib import *

out = []
A = lambda i: i          # outer C5
B = lambda i: 5 + i      # inner pentagram
E = [(A(i), A((i + 1) % 5)) for i in range(5)] + \
    [(B(i), B((i + 2) % 5)) for i in range(5)] + \
    [(A(i), B(i)) for i in range(5)]
pet = G(10, E)
assert pet.triangle_free() and pet.n == 10 and pet.m == 15

print("Petersen: n=%d m=%d triangle-free=%s odd girth=%d" %
      (pet.n, pet.m, pet.triangle_free(), odd_girth(pet)))
print("graph6:", pet.g6())

# ---- 1. the switching / contraction is checked literally ------------------------
Bset = {B(i) for i in range(5)}
sign = {}
for e in pet.E:
    flips = len(set(e) & Bset) % 2          # switching at Bset flips edges with one end in B
    sign[e] = (1 + flips) % 2               # 1 = odd, all edges start odd
spokes = [(A(i), B(i)) for i in range(5)]
assert all(sign[tuple(sorted(e))] == 0 for e in spokes), "spokes must become even"
others = [e for e in pet.E if tuple(sorted(e)) not in {tuple(sorted(s)) for s in spokes}]
assert all(sign[e] == 1 for e in others), "outer/inner must stay odd"
cls = {}
for i in range(5):
    cls[A(i)] = i
    cls[B(i)] = i
pairs = {}
for e in others:
    p = tuple(sorted((cls[e[0]], cls[e[1]])))
    pairs.setdefault(p, []).append(e)
print("after switching at the inner 5-set: spokes even, other 10 edges odd;")
print("contracting the spokes gives the pairs", sorted(pairs), "= all 10 pairs of K5, all odd")
assert len(pairs) == 10

# ---- 2. explicit weight with an integrality gap ----------------------------------
for M in (4, 5, 6, 10):
    w = {}
    for e in pet.E:
        w[e] = F(M) if tuple(sorted(e)) in {tuple(sorted(s)) for s in spokes} else F(1)
    tau = bip(pet, w)
    r = Lambda(pet, w)
    verify_Lambda(pet, r, w)
    print(f"  M={M:3d}:  tau_w = {tau}   tau*_w = {r['value']}   gap = {F(tau)/r['value']} "
          f"{'  <-- INTEGRALITY GAP' if tau > r['value'] else ''}")

# ---- 3. the same gap as a PRODUCT weight on a triangle-free graph (Lemma SIM) ----
# twice-subdivide Petersen and give the middle vertex of each spoke path weight 5.
import R9_oddk5_sim as SIM
c = {}
sp = {tuple(sorted(s)) for s in spokes}
for e in pet.E:
    c[e] = F(1, 5) if e in sp else F(1, 25)      # scaled into (0,1]; ratio 5 : 1 preserved
H, x = SIM.build_sim(pet, c)
print(f"\nsimulation graph: n={H.n} m={H.m} triangle-free={H.triangle_free()} "
      f"odd girth={odd_girth(H)}")
ps = psi(H, x)
lam = LambdaX(H, x)
verify_Lambda(H, lam, prodw(H, x))
print(f"  psi(H,x) = {ps}   Lambda(H,x) = {lam['value']}   ratio = {ps/lam['value']}")
s = sum(x)
print(f"  normalised: sum x = {s},  psi = {ps/s**2}, Lambda = {lam['value']/s**2}, "
      f"1/25 = {F(1,25)}  (psi below 1/25: {ps/s**2 < F(1,25)})")
