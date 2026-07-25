"""
audit_G7_points.py -- exact (Fraction/int) checks of the individual numeric
claims of G7.md at named points.  Independent of every G7_* script.
"""
import itertools, sys
from fractions import Fraction as F

# ------------------------------------------------------------------ helpers
def cuts(n):
    for S in range(1 << (n - 1)):
        yield S


def mono(edges, S):
    return [(u, v) for (u, v) in edges if ((S >> u) & 1) == ((S >> v) & 1)]


def psi(n, edges, x):
    """min over all cuts of sum of monochromatic x_u x_v (exact)"""
    best = None
    for S in cuts(n):
        s = sum(x[u] * x[v] for (u, v) in edges if ((S >> u) & 1) == ((S >> v) & 1))
        if best is None or s < best:
            best = s; arg = S
    return best, arg


def wdeg(n, edges, x):
    d = [0] * n
    for (u, v) in edges:
        d[u] += x[v]; d[v] += x[u]
    return d


# Gamma_3 in the two labellings actually used in the campaign
G3_ENGINE = (8, [(0, 3), (0, 4), (0, 5), (1, 4), (1, 5), (1, 6),
                 (2, 5), (2, 6), (2, 7), (3, 6), (3, 7), (4, 7)])          # C8({3,4})
G3_C814 = (8, [(j, (j + 1) % 8) for j in range(8)] + [(j, j + 4) for j in range(4)])

print('=== 0. the two Gamma_3 models ===')
# explicit isomorphism  v -> 3v mod 8 maps C8({3,4}) onto C8({1,4})
f = {v: (3 * v) % 8 for v in range(8)}
img = set(frozenset((f[u], f[v])) for u, v in G3_ENGINE[1])
tgt = set(frozenset((u % 8, v % 8)) for u, v in G3_C814[1])
print('  v -> 3v mod 8 maps C8({3,4}) onto C8({1,4}):', img == tgt)

print()
print('=== 1. REFUTED#2: the 4-cut family of G7.md is too small ===')
n, E = G3_C814
FOUR = [[(0, 1), (4, 5)], [(1, 2), (5, 6)], [(2, 3), (6, 7)], [(0, 7), (3, 4)]]
for L in FOUR:
    for e in L:
        assert tuple(sorted(e)) in [tuple(sorted(x)) for x in E], e
# check the claim "exactly 4 cuts leave only 2 monochromatic edges"
cnt = {}
for S in cuts(8):
    L = mono(E, S)
    cnt.setdefault(len(L), []).append(sorted(map(tuple, (tuple(sorted(e)) for e in L))))
print('  #cuts by monochromatic-edge count:',
      {k: len(v) for k, v in sorted(cnt.items())})
print('  the 2-monochromatic cuts:', sorted(map(str, cnt.get(2, []))))
x = [F(1, 6), F(1, 4), F(1, 6), F(1, 4), F(1, 6), 0, 0, 0]
print('  sum x =', sum(x))
vals = [sum(x[u] * x[v] for (u, v) in L) for L in FOUR]
print('  values on the 4-cut family:', vals, ' min =', min(vals),
      ' > 1/25?', min(vals) > F(1, 25))
p, arg = psi(8, E, x)
print('  true psi at that x =', p, ' (report says 1/36) ->', p == F(1, 36))
a = [0, 0, 0, 2, 3, 2, 3, 2]
print('  integer form a=(0,0,0,2,3,2,3,2) q=%d' % sum(a))
vals = [sum(a[u] * a[v] for (u, v) in L) for L in FOUR]
print('   4-family min =', min(vals), ' 25*min/q^2 =', F(25 * min(vals), sum(a) ** 2))
print('   true bip =', psi(8, E, a)[0])

print()
print('=== 2. the 12-cut family (<=3 monochromatic edges) ===')
FAM3 = [mono(E, S) for S in cuts(8) if len(mono(E, S)) <= 3]
print('  #cuts with <=3 mono edges:', len(FAM3))
claimed = [{(3, 4), (3, 7), (6, 7)}, {(1, 2), (2, 6), (6, 7)}, {(1, 2), (1, 5), (4, 5)},
           {(0, 4), (0, 7), (4, 5)}, {(0, 7), (2, 3), (3, 7)}, {(0, 1), (0, 4), (3, 4)},
           {(0, 1), (1, 5), (5, 6)}, {(2, 3), (2, 6), (5, 6)}]
have = [set(map(lambda e: tuple(sorted(e)), L)) for L in FAM3 if len(L) == 3]
print('  the 8 three-edge sets match the report:',
      sorted(map(sorted, have)) == sorted(map(sorted, claimed)))

print()
print('=== 3. G7.md: "at q=40 a second FULL-SUPPORT family of maximisers" ===')
for lab, EE in (('C8({3,4}) [engine labelling]', G3_ENGINE[1]),
                ('C8({1,4}) [report labelling]', G3_C814[1])):
    a = [6, 2, 8, 0, 8, 8, 0, 8]
    print('  %-30s a=%s sum=%d  bip=%s  zeros=%d'
          % (lab, a, sum(a), psi(8, EE, a)[0], a.count(0)))

print()
print('=== 4. degree-restricted feasibility of the induced-C5 point ===')
for lab, EE in (('C8({3,4})', G3_ENGINE[1]), ('C8({1,4})', G3_C814[1])):
    # find every induced C5 and test the uniform-on-C5 point
    for S in itertools.combinations(range(8), 5):
        sub = [(u, v) for (u, v) in EE if u in S and v in S]
        if len(sub) != 5:
            continue
        deg = {v: sum(1 for e in sub if v in e) for v in S}
        if set(deg.values()) != {2}:
            continue
        x = [F(1, 5) if v in S else 0 for v in range(8)]
        d = wdeg(8, EE, x)
        print('  %s induced C5 %s : psi=%s  min weighted degree=%s  feasible(>1/3)=%s'
              % (lab, S, psi(8, EE, x)[0], min(d), min(d) > F(1, 3)))
        break
