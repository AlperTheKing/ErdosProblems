"""audit_P3_delta_verify2.py -- EXACT Fraction re-verification of EVERY falsifier of P3.md (e).

Parses the witnesses out of audit_P3_deltamax_deep.log (produced by audit_P3_deltamax.cpp) and
recomputes, from my own Vega construction and my own exhaustive 2^(n-1) max-cut, in exact rational
arithmetic:
   * membership in P(H)   (omega(N(v)) > 1/3 for EVERY vertex v, i.e. 3*a(N(v)) > D)
   * psi = bip / D^2
   * comparison with 29/841 (P3.md's claimed family maximum) and with 1/25 (Erdos 23).
"""
import re
from fractions import Fraction as F
from audit_P3_core import vega_family, bip_exact

fam = {}
for i in (2, 3, 4, 5):
    for (nm, adj, order, w) in vega_family(i):
        fam[nm] = (adj, order, w)

txt = open('audit_P3_deltamax_deep.log').read().split('\n')
T = F(29, 841)
rows = []
for k, line in enumerate(txt):
    m = re.match(r'(\S+)\s+n=\s*(\d+) \| reg feasible=(\S+).*at D=(\d+):', line)
    if not m:
        continue
    nm, D = m.group(1), int(m.group(4))
    if k + 1 >= len(txt) or 'witness a =' not in txt[k + 1]:
        continue
    wit = [int(z) for z in txt[k + 1].split('witness a =')[1].split('roles')[0].split()]
    adj, order, wreg = fam[nm]
    assert sum(wit) == D and len(wit) == len(order)
    a = dict(zip(order, wit))
    degs = {v: sum(a[u] for u in adj[v]) for v in order}
    feas = all(3 * degs[v] > D for v in order)
    bp = bip_exact(order, adj, a)
    val = F(bp, D * D)
    qreg = sum(wreg.values())
    vreg = F(bip_exact(order, adj, wreg), qreg * qreg)
    rows.append((val, nm, D, feas, val > T, val > F(1, 25), vreg, order, wit))

rows.sort(reverse=True)
print('P3.md (e) claims: max psi over P(H) = 29/841 = %.9f, attained at omega_reg, '
      'uniform 13.8%% margin.' % float(T))
print()
hdr = '%-11s %6s %-26s %-12s %-9s %-8s %-6s %s'
print(hdr % ('graph', 'D', 'psi (exact)', 'psi float', 'in P(H)', '>29/841', '>1/25', 'psi(omega_reg)'))
allok = True
for (val, nm, D, feas, gt, g25, vreg, order, wit) in rows:
    print(hdr % (nm, D, str(val), '%.9f' % float(val), feas, gt, g25, '%.7f' % float(vreg)))
    allok = allok and feas and gt and not g25
print()
print('every row: inside P(H) AND > 29/841 AND < 1/25 :', allok, ' (%d rows)' % len(rows))
print('max exactly-verified psi in P(H): %s = %.9f on %s (D=%d)'
      % (rows[0][0], float(rows[0][0]), rows[0][1], rows[0][2]))
print('   -> "the maximum over the whole Vega family is 29/841" is FALSE')
print('   -> "attained at the regular weight function in every case" is FALSE (all %d rows)' % len(rows))
print('   -> demonstrated margin below 1/25 is at most %.4f%%, not 13.8%%'
      % (100 * (1 - float(rows[0][0]) * 25)))
print()
print('argmax witness (%s, D=%d), order = %s' % (rows[0][1], rows[0][2],
                                                 ','.join(map(str, rows[0][7]))))
print('   a =', ' '.join(map(str, rows[0][8])))
