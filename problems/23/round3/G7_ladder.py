"""
G7_ladder.py

Exact minimum-degree ladder for the Brandt-Thomasse reduction.

Lemma (regular weightings are optimal).  Let H have a weight vector w* >= 0,
sum w* = 1, with A w* = d* 1 (A = adjacency matrix).  Then for EVERY w >= 0
with sum w = 1 we have min_v (Aw)_v <= d*.
Proof.  Put d = min_v (Aw)_v, so Aw >= d*1 entrywise.  Then
   d* = d* (1^T w) = (A w*)^T w = w*^T (A w) >= d (w*^T 1) = d.        []

Consequently  max_w delta(H,w) = delta_reg(H), which by Brandt-Thomasse
Theorem 3 (Vega) / regularity (Gamma_i) is

   delta_reg(Gamma_i)          = i/(3i-1)
   delta_reg(Upsilon_i)        = (9i-6)/(27i-19)
   delta_reg(Upsilon_i - y)    = (9i-7)/(27i-22)
   delta_reg(Upsilon_i - 2i)   = (9i-7)/(27i-22)
   delta_reg(Upsilon_i-{y,2i}) = (9i-8)/(27i-25).

Observe  (9i-6)/(27i-19) = t/(3t-1) with t = 9i-6, and likewise for the other
three families:  EVERY Vega graph has exactly the regular degree of some
Andrasfai graph.  Hence the set of attainable thresholds is exactly
{t/(3t-1) : t >= 1}, a strictly decreasing sequence with limit 1/3.

This script prints, for each t, the FINITE list L_t of patterns H with
delta_reg(H) > t/(3t-1), i.e. the finite set of graphs whose max_x psi must be
bounded by 1/25 in order to settle the band delta(G) > t N/(3t-1).
"""
from fractions import Fraction
import sys

F = Fraction


def dreg(kind, i):
    if kind == 'Gamma':      return F(i, 3 * i - 1), 3 * i - 1
    if kind == 'Ups':        return F(9 * i - 6, 27 * i - 19), 3 * i + 7
    if kind == 'Ups-y':      return F(9 * i - 7, 27 * i - 22), 3 * i + 6
    if kind == 'Ups-2i':     return F(9 * i - 7, 27 * i - 22), 3 * i + 6
    if kind == 'Ups-y-2i':   return F(9 * i - 8, 27 * i - 25), 3 * i + 5
    raise ValueError(kind)


IMAX = 40
ALL = []
for i in range(1, 3 * IMAX):
    ALL.append(('Gamma_%d' % i,) + dreg('Gamma', i))
for i in range(2, IMAX):
    for k, nm in [('Ups', 'Upsilon_%d'), ('Ups-y', 'Upsilon_%d-y'),
                  ('Ups-2i', 'Upsilon_%d-2i'), ('Ups-y-2i', 'Upsilon_%d-y-2i')]:
        ALL.append((nm % i,) + dreg(k, i))

print('== every Vega regular degree equals an Andrasfai regular degree ==')
for i in range(2, 8):
    for k, nm, t in [('Ups', 'Upsilon_%d', 9 * i - 6), ('Ups-y', 'Upsilon_%d-y', 9 * i - 7),
                     ('Ups-2i', 'Upsilon_%d-2i', 9 * i - 7),
                     ('Ups-y-2i', 'Upsilon_%d-y-2i', 9 * i - 8)]:
        d, n = dreg(k, i)
        assert d == F(t, 3 * t - 1), (k, i)
        print('   %-16s n=%3d  delta_reg = %-10s = delta_reg(Gamma_%d)' % (nm % i, n, d, t))

print()
print('== the ladder:  L_t = {H : delta_reg(H) > t/(3t-1)} ==')
print('   (Erdos #23 holds for every triangle-free G with delta(G) > tN/(3t-1)')
print('    as soon as max_x psi(H,x) <= 1/25 for every H in L_t)')
print()
for t in list(range(1, 17)) + [20, 30]:
    thr = F(t, 3 * t - 1)
    L = sorted([(n, nm, d) for nm, d, n in ALL if d > thr])
    lst = ', '.join('%s(n=%d)' % (nm, n) for n, nm, d in L)
    print('  t=%-3d  delta > %-8s = %.6f   |L_t|=%d   L_t = %s'
          % (t, str(thr), float(thr), len(L), lst if lst else '(empty)'))

print()
print('== sanity: the largest pattern needed for each t and the biggest n ==')
for t in [3, 4, 5, 10, 11, 12, 13, 20, 30, 50, 100]:
    thr = F(t, 3 * t - 1)
    L = [(n, nm) for nm, d, n in ALL if d > thr]
    print('  t=%-4d delta > %-9s  |L_t| = %-3d  max |V(H)| = %d'
          % (t, str(thr), len(L), max(n for n, _ in L) if L else 0))
