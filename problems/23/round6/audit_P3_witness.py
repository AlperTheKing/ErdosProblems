"""audit_P3_witness.py -- verify P3.md's Result 4 / V4 witness and the special-point table.

Claim under audit (P3.md, Result 4 and V4):
  Ups_2, q=15, a = (1,1,1,1,3 || 1,1 || 1,1,1,1,1,1) in order (1,2,3,4,5,x,y,a,b,c,u,v,w)
  - min over ALL 13 neighbourhood cuts N(t) = 10  -> 2/45 > 1/25
  - true bip = 7, psi = 7/225
  - ARCPLUS returns 7 (exact)
Everything recomputed from my own construction.
"""
from fractions import Fraction as F
from audit_P3_core import (vega_family, bip_exact, mono_of, arcs_of, arcplus, famin, SPECIALS)

fam = {name: (adj, order, w) for (name, adj, order, w) in vega_family(2)}
adj, order, wreg = fam['Ups_2']
print('Ups_2 order:', order)

a = dict(zip(order, [1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1]))
q = sum(a.values())
print('q =', q, ' a =', [a[t] for t in order])

# ---- neighbourhood cuts
nb = {}
for t in order:
    S = set(adj[t])
    nb[t] = mono_of(order, adj, a, S)
print('neighbourhood cut values m(t):')
for t in order:
    print('   N(%-2s) = %2d   (independent: %s)'
          % (t, nb[t], all(y not in adj[x] for x in adj[t] for y in adj[t])))
mn = min(nb.values())
print('min over all 13 neighbourhood cuts =', mn, ' -> ', F(mn, q * q), '=', float(F(mn, q*q)))
print('   exceeds 1/25 ?', F(mn, q * q) > F(1, 25))

# ---- true bip
bp = bip_exact(order, adj, a)
print('true bip =', bp, ' psi =', F(bp, q * q), '=', float(F(bp, q * q)),
      ' <= 1/25 ?', F(bp, q * q) <= F(1, 25))

# ---- ARCPLUS
L = 3 * 2 - 1
pos = {t: (t if isinstance(t, int) else None) for t in order}
sp = [t for t in order if t in SPECIALS]
AP = arcplus(order, pos, L, sp)
print('|ARCPLUS| (unreduced) =', len(AP))
apmin = famin(order, adj, a, AP)
print('ARCPLUS min =', apmin, ' equals bip ?', apmin == bp)

# ---- plain arc family (no specials free)
AR = arcs_of(order, pos, L)
armin = famin(order, adj, a, [set(A) for A in AR])
print('ARCFREE min =', armin)

# ---- the four further witnesses quoted in P3.md
print()
print('further quoted witnesses (famMin should be 10, trueBip 7, q=15):')
quoted = [
    ('Ups_2', [0, 2, 2, 0, 1, 1, 1, 1, 2, 1, 1, 2, 1]),
    ('Ups_2-y-2i', [0, 2, 1, 1, 1, 2, 2, 1, 2, 2, 1]),
    ('Ups_3-y-2i', [1, 0, 2, 2, 0, 2, 0, 2, 2, 1, 1, 1, 1, 0]),
    ('Ups_3', [1, 0, 2, 2, 0, 1, 1, 1, 0, 2, 1, 1, 0, 1, 1, 1]),
]
allfam = {}
for i in (2, 3):
    for (nm, ad, od, ww) in vega_family(i):
        allfam[nm] = (ad, od, ww, i)
for nm, vec in quoted:
    ad, od, ww, i = allfam[nm]
    assert len(vec) == len(od), (nm, len(vec), len(od))
    aa = dict(zip(od, vec))
    qq = sum(vec)
    nbv = min(mono_of(od, ad, aa, set(ad[t])) for t in od)
    bp2 = bip_exact(od, ad, aa)
    print('  %-11s q=%d  order=%s' % (nm, qq, ','.join(map(str, od))))
    print('      NBHDmin=%d  trueBip=%d  q^2/25=%.3f  NBHD>1/25 ? %s  bip<=1/25 ? %s'
          % (nbv, bp2, qq * qq / 25.0, F(nbv, qq * qq) > F(1, 25), F(bp2, qq * qq) <= F(1, 25)))

# ---- the regular-weight special point table
print()
print('psi at the paper regular weight function (exact):')
CLOSED = {
    '': lambda i: F(3 * (3 * i - 2) * (5 * i - 3), 2 * (27 * i - 19) ** 2),
    '-y': lambda i: F((3 * i - 2) * (15 * i - 13), 2 * (27 * i - 22) ** 2),
    '-2i': lambda i: F(45 * i * i - 69 * i + 30, 2 * (27 * i - 22) ** 2),
    '-y-2i': lambda i: F(45 * i * i - 81 * i + 40, 2 * (27 * i - 25) ** 2),
}
for i in (2, 3, 4):
    for (nm, ad, od, ww) in vega_family(i):
        qq = sum(ww.values())
        if len(od) > 20:
            continue
        bp2 = bip_exact(od, ad, ww)
        nbv = min(mono_of(od, ad, ww, set(ad[t])) for t in od)
        variant = nm.split('-', 1)[1] if '-' in nm else ''
        variant = '-' + variant if variant else ''
        cf = CLOSED[variant](i)
        print('  %-11s q=%3d  psi=%-14s =%.7f  closedform=%-14s match=%s | NBHDmin/q^2=%.7f '
              'ratio_to_1/25=%.4f  psi/(1/25)=%.4f'
              % (nm, qq, F(bp2, qq * qq), float(F(bp2, qq * qq)), cf,
                 F(bp2, qq * qq) == cf, float(F(nbv, qq * qq)),
                 float(F(nbv, qq * qq) * 25), float(F(bp2, qq * qq) * 25)))
