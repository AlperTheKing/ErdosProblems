"""AUDIT pass 2 -- final checks: cross-implementation check of the new maximisers,
the pentagon ratio table, the cheap single-neighbourhood falsifier, M(C11)."""
from fractions import Fraction as F
from a2_core import (g6_decode, adj_masks, bip, bip2, blowup_value, expand_blowup,
                     nbhd_union_sets, family_value, count_C5_subgraphs, cycle,
                     is_triangle_free)

G6 = 'J?BD@g]Qvo?'
n, E = g6_decode(G6)
print('== 1. cross-check the new maximisers found by a2_blowup.exe (Python, exact) ==')
for a in [[0, 0, 0, 0, 0, 5, 5, 5, 5, 5, 0],
          [0, 0, 0, 0, 1, 5, 4, 5, 5, 5, 0],
          [0, 0, 0, 1, 3, 4, 2, 5, 5, 5, 0],
          [5, 5, 0, 0, 0, 5, 5, 0, 0, 5, 0]]:
    q = blowup_value(n, E, a)
    W = sum(a)
    NN, EE = expand_blowup(n, E, a)
    qq = bip(NN, EE) if NN <= 25 else None
    print(f'   a={a}  W={W}  bip={q}  25bip/W^2={F(25*q,W*W)}  explicit {NN}-vertex bip={qq}'
          f'  agree={q==qq}  support size={sum(1 for v in a if v)}')

print('\n== 2. pentagon ratio  max bip^5 / c5^2  over connected triangle-free graphs ==')
for nn in range(5, 11):
    best = None
    zero = 0
    for line in open(f'a2_tf{nn}.g6'):
        line = line.strip()
        if not line:
            continue
        m, EE = g6_decode(line)
        b = bip(m, EE)
        c = count_C5_subgraphs(m, EE)
        if c == 0:
            if b > 0:
                zero += 1
            continue
        r = F(b ** 5, c ** 2)
        if best is None or r > best[0]:
            best = (r, line, b, c)
    print(f'   n={nn}: max bip^5/c5^2 = {best[0]} (={float(best[0]):.4f}) at {best[1]} '
          f'bip={best[2]} c5={best[3]};  #graphs with c5=0 but bip>0 = {zero}')

print('\n== 3. the cheap falsifier of the single-neighbourhood (base-5) certificate ==')
m, EE = g6_decode('EEh_')
A = adj_masks(m, EE)
vals = [sum(1 for (u, v) in EE if ((A[w] >> u) & 1) == ((A[w] >> v) & 1)) for w in range(m)]
print(f'   EEh_ : n={m} |E|={len(EE)} edges={EE} tf={is_triangle_free(m,EE)}')
print(f'   bip={bip(m,EE)}/{bip2(m,EE)} (bipartite: {bip(m,EE)==0})   e(G-N(v)) by v: {vals}  '
      f'min={min(vals)}   25*min={25*min(vals)} > n^2={m*m}: {25*min(vals) > m*m}')
sets = nbhd_union_sets(m, EE)
print(f'   union family = {family_value(m,EE,[1]*m,sets)}  (repairs it: '
      f'{25*family_value(m,EE,[1]*m,sets) <= m*m})')

print('\n== 4. M(C11) family value ==')


def mycielski(nn, EEc):
    mm = 2 * nn + 1
    F_ = []
    for (u, v) in EEc:
        F_ += [(nn + u, nn + v), (u, nn + v), (v, nn + u)]
    F_ += [(i, 2 * nn) for i in range(nn)]
    return mm, sorted(tuple(sorted(x)) for x in F_)


kn, kE = cycle(11)
mn, mE = mycielski(kn, kE)
nb = adj_masks(mn, mE)
cur = {0}
for v in range(mn):
    cur |= {S | nb[v] for S in cur}
fv = min(sum(1 for (u, v) in mE if ((S >> u) & 1) == ((S >> v) & 1)) for S in cur)
print(f'   M(C11): n={mn} |E|={len(mE)} #union-cuts={len(cur)}  fam={fv}  '
      f'n^2/25={F(mn*mn,25)}={float(F(mn*mn,25)):.2f}  Q1.md says 7 -> {fv==7}')
