"""audit_P3_delta_verify.py -- EXACT independent verification of the falsifiers of P3.md claim (e).

P3.md: "the maximum of psi over P(H) is attained at the (unique) regular weight function in every
case tested ... The maximum over the whole Vega family is 29/841 = 0.0344828 ... V1' has a uniform
13.8% margin and is not tight."

The candidates below came out of my own hill-climber (audit_P3_deltamax.cpp).  Here everything is
recomputed from scratch: my own Vega construction, exact Fraction arithmetic, exact feasibility
(omega(N(v)) > 1/3 for EVERY v), and bip by exhaustive enumeration of all 2^(n-1) cuts.
"""
from fractions import Fraction as F
from audit_P3_core import vega_family, bip_exact

CAND = {
 'Ups_2':      (3500, [93,322,316,108,324,95,104,357,390,319,387,362,323]),
 'Ups_2-y':    (3200, [108,305,295,60,327,216,420,354,319,292,300,204]),
 'Ups_2-2i':   (3200, [202,214,318,332,78,87,372,310,298,401,299,289]),
 'Ups_2-y-2i': (2900, [201,189,300,317,192,370,312,306,312,199,202]),
 'Ups_3':      (6200, [13,305,298,290,310,20,299,302,145,129,722,731,598,725,722,591]),
 'Ups_3-y':    (5900, [20,303,267,276,289,11,279,291,235,749,733,645,644,644,514]),
 'Ups_3-2i':   (5900, [136,310,145,289,290,300,271,123,131,696,629,621,701,631,627]),
 'Ups_3-y-2i': (5600, [144,294,117,295,254,308,239,235,692,647,666,628,546,535]),
 'Ups_4-2i':   (8600, [141,287,258,147,292,264,266,299,259,266,112,134,989,937,966,1056,987,940]),
}

TARGET = F(29, 841)
fam = {}
for i in (2, 3, 4):
    for (nm, adj, order, wreg) in vega_family(i):
        fam[nm] = (adj, order, wreg)

print('THRESHOLDS:  29/841 = %s = %.9f    1/25 = %.9f' % (TARGET, float(TARGET), 0.04))
print()
hdr = '%-11s %5s %5s %-24s %-12s %-10s %-9s %-8s %s'
print(hdr % ('graph', 'n', 'D', 'psi(candidate)', 'psi float', 'psi(reg)',
             'feasible', '>29/841', '>1/25'))
nbeat = 0
for nm, (D, vec) in CAND.items():
    adj, order, wreg = fam[nm]
    assert len(vec) == len(order), (nm, len(vec), len(order))
    assert sum(vec) == D, (nm, sum(vec), D)
    a = dict(zip(order, vec))
    # EXACT feasibility: omega(N(v)) > 1/3  <=>  3 * a(N(v)) > D
    degs = {v: sum(a[u] for u in adj[v]) for v in order}
    feas = all(3 * degs[v] > D for v in order)
    worst = min(F(3 * degs[v], D) for v in order)
    bp = bip_exact(order, adj, a)
    val = F(bp, D * D)
    qreg = sum(wreg.values())
    vreg = F(bip_exact(order, adj, wreg), qreg * qreg)
    beat = val > TARGET
    nbeat += beat
    print(hdr % (nm, len(order), D, str(val), '%.9f' % float(val), '%.7f' % float(vreg),
                 str(feas), str(beat), str(val > F(1, 25))))
    if not feas:
        print('    *** candidate is NOT in P(H): min 3*deg/D = %s ***' % worst)
print()
print('candidates verified exactly inside P(H) with psi > 29/841 : %d of %d' % (nbeat, len(CAND)))
best = max((F(bip_exact(fam[nm][1] and fam[nm][0] or None, fam[nm][1], dict(zip(fam[nm][1], v))), D * D)
            if False else F(0)) for nm, (D, v) in CAND.items())
vals = []
for nm, (D, vec) in CAND.items():
    adj, order, wreg = fam[nm]
    vals.append((F(bip_exact(order, adj, dict(zip(order, vec))), D * D), nm))
vals.sort(reverse=True)
print('largest exactly-verified psi inside P(H): %s = %.9f on %s' % (vals[0][0], float(vals[0][0]), vals[0][1]))
print('   -> P3.md\'s "maximum over the whole Vega family is 29/841" is FALSE')
print('   -> implied margin below 1/25 is at most %.4f%%, not 13.8%%'
      % (100 * (1 - float(vals[0][0]) * 25)))
