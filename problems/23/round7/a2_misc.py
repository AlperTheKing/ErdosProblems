"""AUDIT pass 2 -- everything except R1/E3:  C5[n] spectrum, entropy rows, Q1-B, Q1-C,
pentagon counting (R2), Petersen / Mycielski calibration, the census total, and the
smallest failure of the single-neighbourhood sub-family.  Exact unless marked diagnostic."""
import math
from fractions import Fraction as F
from itertools import combinations, product
from a2_core import (g6_decode, adj_masks, is_triangle_free, bip, bip2, blowup_value,
                     expand_blowup, nbhd_union_sets, family_value, count_C5_subgraphs,
                     cycle, compositions)

C = math.comb
print('===== 1. C5[n] cut spectrum (exact, own profile enumeration) =====')
spec = {}
for n in range(1, 9):
    hist = {}
    tot = 0
    for s in product(range(n + 1), repeat=5):
        m = sum(s[i] * s[(i + 1) % 5] + (n - s[i]) * (n - s[(i + 1) % 5]) for i in range(5))
        mult = 1
        for si in s:
            mult *= C(n, si)
        hist[m] = hist.get(m, 0) + mult
        tot += mult
    mn = min(hist)
    assert tot == 2 ** (5 * n), (n, tot)
    spec[n] = hist
    print(f'  n={n} N={5*n}: total cuts {tot}=2^{5*n}  min={mn} (=n^2? {mn==n*n})  '
          f'#minimisers={hist[mn]}  10(2^n-1)={10*(2**n-1)}  match={hist[mn]==10*(2**n-1)}')

print('\n===== 2. entropy budget rows (diagnostic floats over an EXACT spectrum) =====')
n = 8
N = 40
hist = spec[n]
items = sorted(hist.items())


def maxent(M):
    """min_{beta>=0} [beta*M + log Z(beta)] by ternary search (convex in beta)."""
    def f(b):
        mmin = items[0][0]
        s = sum(c * math.exp(-b * (m - mmin)) for m, c in items)
        return b * M + (-b * mmin + math.log(s))
    lo, hi = 0.0, 50.0
    for _ in range(400):
        a1 = lo + (hi - lo) / 3
        a2 = hi - (hi - lo) / 3
        if f(a1) < f(a2):
            hi = a2
        else:
            lo = a1
    return f((lo + hi) / 2)


full = N * math.log(2)
print(f'  full entropy N log2 = {full:.4f}')
for eps, rep in [(F(0), 7.8438), (F(1, 1000), 9.1580), (F(1, 200), 11.9322),
                 (F(1, 100), 14.4715), (F(1, 50), 18.4715)]:
    M = float((F(1, 25) + eps) * N * N)
    v = math.log(hist[64]) if eps == 0 else maxent(M)
    print(f'  eps={str(eps):>6s}  M={M:8.2f}  my max-entropy={v:9.4f}  Q1.md={rep:9.4f}  '
          f'diff={100*(rep-v)/v:+.2f}%  frac={v/full:.4f}')

print('\n===== 3. Q1-B arithmetic (exact/symbolic) =====')
import sympy as sp
e = sp.Rational
x = sp.symbols('x')
poly = sp.expand((1 + 25 * x) * (1 - 6 * x) ** 2 - 1)
print('  (1+25e)(1-6e)^2-1 =', poly)
r = sp.solve(sp.Eq(sp.expand(poly / x), 0), x)
print('  roots of 900x^2-264x+13 :', [sp.nsimplify(t) for t in r], [float(t) for t in r])
print('  eps <= 1/16-1/25 =', sp.Rational(1, 16) - sp.Rational(1, 25), '=', float(sp.Rational(9, 400)))
print('  smallest positive root > 9/400 ?', min(float(t) for t in r) > 9 / 400)
print('  max of m - 4m^2/N^2 over m  (N=1):', sp.maximum(x - 4 * x ** 2, x, sp.Interval(0, 1)))

print('\n===== 4. Q1-C : bip <= floor((N-Delta-1)^2/4) =====')
bad = 0
tot = 0
for nn in range(5, 11):
    for line in open(f'a2_tf{nn}.g6'):
        line = line.strip()
        if not line:
            continue
        m, E = g6_decode(line)
        A = adj_masks(m, E)
        D = max(bin(A[v]).count('1') for v in range(m))
        b = bip(m, E)
        tot += 1
        if b > ((m - D - 1) ** 2) // 4:
            bad += 1
            if bad < 4:
                print('   VIOLATION', line, m, D, b)
print(f'  checked {tot} connected triangle-free graphs n=5..10, violations = {bad}')
Nn, Dd = sp.symbols('N Delta', positive=True)
print('  at Delta = 3N/5 - 1 :  (N-Delta-1)^2/4 =',
      sp.simplify(((Nn - (3 * Nn / 5 - 1) - 1) ** 2) / 4), ' (target N^2/25 =', Nn ** 2 / 25, ')')
print('  base-5 already gives  delta > (4N-2)/25 = 0.16N, so Delta >= delta > 0.16N;'
      '  Q1.md quotes the weaker Delta > N/10.')

print('\n===== 5. R2 pentagon counting =====')
n7, E7 = cycle(7)
print(f'  C7: |E|={len(E7)} bip={bip(n7,E7)}/{bip2(n7,E7)}  #C5={count_C5_subgraphs(n7,E7)}'
      f'  -> bip^(5/2) <= c5 FALSE: {bip(n7,E7)**5 > 0}')
n5, E5 = cycle(5)
print(f'  C5: bip={bip(n5,E5)} #C5={count_C5_subgraphs(n5,E5)}')
# C5[2] and C5[3] : bip = n^2, #C5 = n^5
for t in (2, 3):
    NN, EE = expand_blowup(5, E5, [t] * 5)
    print(f'  C5[{t}]: N={NN} bip={bip(NN,EE)} (=t^2? {bip(NN,EE)==t*t})  '
          f'#C5={count_C5_subgraphs(NN,EE)} (=t^5? {count_C5_subgraphs(NN,EE)==t**5})')
PET = 'IheA@GUAo'   # Petersen graph in graph6
pn, pE = g6_decode(PET)
pb = bip(pn, pE)
pc5 = count_C5_subgraphs(pn, pE)
print(f'  Petersen {PET}: n={pn} |E|={len(pE)} trianglefree={is_triangle_free(pn,pE)} '
      f'bip={pb} #C5={pc5}  bip^5/c5^2={F(pb**5,pc5**2)}')
psets = nbhd_union_sets(pn, pE)
print(f'  Petersen family value (uniform) = {family_value(pn,pE,[1]*pn,psets)}  (= bip? '
      f'{family_value(pn,pE,[1]*pn,psets)==pb})')
K = F(pb ** 5, pc5 ** 2)          # = (bip^{5/2}/c5)^2
c = float(K) ** sp.Rational(1, 5)
print(f'  Q1.md: "(27/16)^(2/5) N^2/25 = N^2/22.56".  Correct constant is K^(1/5) with '
      f'K=27/16:  (27/16)^(1/5) = {float(sp.Rational(27,16)**sp.Rational(1,5)):.6f} '
      f'-> N^2/{25/float(sp.Rational(27,16)**sp.Rational(1,5)):.4f}')
print(f'  the literal expression (27/16)^(2/5) = {float(sp.Rational(27,16)**sp.Rational(2,5)):.6f}'
      f' -> N^2/{25/float(sp.Rational(27,16)**sp.Rational(2,5)):.4f}   (NOT 22.56)')

print('\n===== 6. Mycielski calibration M(C7), M(C9) =====')


def mycielski(nn, EE):
    m = 2 * nn + 1
    F_ = []
    for (u, v) in EE:
        F_ += [(nn + u, nn + v), (u, nn + v), (v, nn + u)]
    F_ += [(i, 2 * nn) for i in range(nn)]
    return m, sorted(tuple(sorted(x)) for x in F_)


for k in (5, 7, 9):
    kn, kE = cycle(k)
    mn, mE = mycielski(kn, kE)
    b = bip(mn, mE)
    fv = family_value(mn, mE, [1] * mn)
    print(f'  M(C{k}): n={mn} |E|={len(mE)} tf={is_triangle_free(mn,mE)} bip={b} fam={fv} '
          f'25*fam={25*fv} vs n^2={mn*mn}  fails={25*fv>mn*mn}')

print('\n===== 7. smallest failure of the SINGLE-neighbourhood sub-family (base-5 bound) =====')
found = []
for nn in range(3, 9):
    for line in open(f'a2_tf{nn}.g6'):
        line = line.strip()
        if not line:
            continue
        m, E = g6_decode(line)
        A = adj_masks(m, E)
        single = min(sum(1 for (u, v) in E if ((A[w] >> u) & 1) == ((A[w] >> v) & 1))
                     for w in range(m))
        if 25 * single > m * m:
            found.append((m, line, single, bip(m, E)))
    if found:
        break
print(f'  smallest n with 25*min_v e(G-N(v)) > n^2 : n={found[0][0]}, '
      f'{len(found)} graph(s): {found[:3]}')

print('\n===== 8. census total arithmetic =====')
cens = [6, 19, 59, 267, 1380, 9832, 90842, 1144061]
print(f'  6+19+59+267+1380+9832+90842+1144061 = {sum(cens)}   Q1.md says 1236380 -> '
      f'{"MATCH" if sum(cens)==1236380 else "MISMATCH, off by " + str(sum(cens)-1236380)}')
