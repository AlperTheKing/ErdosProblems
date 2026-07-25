"""audit_P3_regression.py -- MANDATORY REGRESSION, run independently of P3_regression.py.

Uses the round-5 witness list (data only) but my own arc family, my own max-cut and my own
Vega construction.  Checks
  R1  ARCBOUND <= 1/25 on all 9 witnesses, and the exact values quoted in P3.md
  R2  ARCBOUND == true bip (exactness) on all 9 witnesses
  R3  the 20 Vega lifts: ARCPLUSmin <= 1/25 and ARCPLUSmin == true bip
"""
import sys
from fractions import Fraction as F
from itertools import combinations
sys.path.insert(0, r'E:\Projects\ErdosProblems\problems\23\round5')
from claude_witness_regression import WITNESSES
from audit_P3_core import vega_family, bip_exact, mono_of, arcs_of, arcplus, famin, SPECIALS

QUOTED = {"W1 half-arc killer": F(1, 49), "W1' same on Gamma_11": F(1, 49),
          "W1'' same on Gamma_16": F(1, 49), "W2 five-atom extremal": F(1, 25),
          "W3 uniform Gamma_18": F(1, 54), "W4 uniform Gamma_20": F(3, 100),
          "W5 three-atom near-path": F(0), "W6 seven-atom": F(1, 49),
          "W7 unequal five-atom": F(1, 100)}


def circle_adj(m):
    adj = {j: set() for j in range(m)}
    for u, v in combinations(range(m), 2):
        if 3 * min((u - v) % m, (v - u) % m) > m:
            adj[u].add(v)
            adj[v].add(u)
    return adj


print('=' * 100)
print('R1/R2  the nine round-5 witnesses, my own arc family and my own exhaustive max-cut')
print('=' * 100)
bad1 = bad2 = badq = 0
for (name, m, w, why) in WITNESSES:
    adj = circle_adj(m)
    order = list(range(m))
    a = {j: w[j] for j in order}
    q = sum(w)
    pos = {j: j + 1 for j in order}
    AR = [set(A) for A in arcs_of(order, pos, m)]
    ab = famin(order, adj, a, AR)
    bp = bip_exact(order, adj, a)
    abF, bpF = F(ab, q * q), F(bp, q * q)
    ok1 = abF <= F(1, 25)
    ok2 = (ab == bp)
    okq = (abF == QUOTED[name])
    bad1 += (not ok1); bad2 += (not ok2); badq += (not okq)
    print('  %-26s m=%3d q=%3d | ARCBOUND=%-8s bip=%-8s | <=1/25:%-5s  EXACT:%-5s  '
          'quoted=%-8s match:%s'
          % (name, m, q, str(abF), str(bpF), ok1, ok2, str(QUOTED[name]), okq))
print('  R1 failures (>1/25): %d   R2 failures (arcbound != bip): %d   quoted-value mismatches: %d'
      % (bad1, bad2, badq))

print()
print('=' * 100)
print('R3  Vega lifts: witness on the circle part of Upsilon_i (m = 3i-1), 0 on the specials')
print('=' * 100)
lifts = 0
bad3 = bad4 = 0
for (name, m, w, why) in WITNESSES:
    if (m + 1) % 3 != 0:
        continue
    i = (m + 1) // 3
    if i < 2 or i > 8:
        continue
    for (gname, adj, order, wreg) in vega_family(i):
        a = {t: 0 for t in order}
        dropped = 0
        for j in range(m):
            v = j + 1
            if v in a:
                a[v] = w[j]
            else:
                dropped += w[j]
        q = sum(a.values())
        if q == 0:
            continue
        L = 3 * i - 1
        pos = {t: (t if isinstance(t, int) else None) for t in order}
        sp = [t for t in order if t in SPECIALS]
        AP = arcplus(order, pos, L, sp)
        apm = famin(order, adj, a, AP)
        bp = bip_exact(order, adj, a)
        ok3 = F(apm, q * q) <= F(1, 25)
        ok4 = (apm == bp)
        lifts += 1
        bad3 += (not ok3); bad4 += (not ok4)
        print('  %-22s <- %-24s i=%d q=%2d dropped=%d | ARCPLUSmin=%-8s bip=%-8s | '
              '<=1/25:%-5s EXACT:%-5s'
              % (gname, name, i, q, dropped, str(F(apm, q * q)), str(F(bp, q * q)), ok3, ok4))
print('  lifts run: %d   R3 failures (>1/25): %d   exactness failures: %d' % (lifts, bad3, bad4))

print()
print('VERDICT: R1 %s | R2 %s | quoted values %s | R3 %s'
      % ('PASS' if bad1 == 0 else 'FAIL', 'PASS' if bad2 == 0 else 'FAIL',
         'MATCH' if badq == 0 else 'MISMATCH', 'PASS' if bad3 == 0 and bad4 == 0 else 'FAIL'))
