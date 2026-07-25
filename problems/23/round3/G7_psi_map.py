"""
G7_psi_map.py -- verify the EXPLICIT chain isomorphism used in the collapse
theorem, entry by entry (not via a black-box isomorphism test).

Claim (proved in G7.md):  for m >= 3, put D = {m, 2m, 3m-1} subset of
{1,...,3m-1} = V(Gamma_m)  (note 3m-1 == 0 in Z_{3m-1}, so D = {0,m,2m}).
Then the order preserving relabelling

    psi(j) = j - #{d in D : d < j}

is an isomorphism  Gamma_m - D  ->  Gamma_{m-1}  which maps
   X_m \ {m}      = {1..m-1}      onto  X_{m-1} = {1..m-1},
   Y_m \ {2m}     = {m+1..2m-1}   onto  Y_{m-1} = {m..2m-2},
   Z_m \ {3m-1}   = {2m+1..3m-2}  onto  Z_{m-1} = {2m-1..3m-4}.
Extending psi by the identity on {x,y,a,b,c,u,v,w} gives an isomorphism
   Upsilon_m - D  ->  Upsilon_{m-1}.
In the (i = m-1) labelling of the report this reads
   Upsilon_i = Upsilon_{i+1} - {i+1, 2i+2, 3i+2}.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from G7_patterns import gamma, upsilon

ok = True
for m in range(3, 25):
    D = {m, 2 * m, 3 * m - 1}
    Gm, Gp = gamma(m), gamma(m - 1)
    R = [j for j in range(1, 3 * m) if j not in D]
    psi = {j: j - sum(1 for d in D if d < j) for j in R}
    assert sorted(psi.values()) == list(range(1, 3 * (m - 1))), m
    for a in R:
        for b in R:
            if a >= b:
                continue
            e1 = b in Gm.adj[a]
            e2 = psi[b] in Gp.adj[psi[a]]
            if e1 != e2:
                print('FAIL m=%d edge (%d,%d) -> (%d,%d): %s vs %s'
                      % (m, a, b, psi[a], psi[b], e1, e2)); ok = False
    # tripartition
    X = sorted(psi[j] for j in range(1, m))
    Y = sorted(psi[j] for j in range(m + 1, 2 * m))
    Z = sorted(psi[j] for j in range(2 * m + 1, 3 * m - 1))
    assert X == list(range(1, m)), (m, X)
    assert Y == list(range(m, 2 * m - 1)), (m, Y)
    assert Z == list(range(2 * m - 1, 3 * m - 3)), (m, Z)
    # now the full Vega graph
    Um, _ = upsilon(m, False, False)
    Up, _ = upsilon(m - 1, False, False)
    keep = [v for v in Um.V if not (isinstance(v, int) and v in D)]
    sub = Um.induced(keep)
    phi = {}
    for v in sub.V:
        phi[v] = psi[v] if isinstance(v, int) else v
    assert sorted(map(str, phi.values())) == sorted(map(str, Up.V)), m
    for a in sub.V:
        for b in sub.V:
            if str(a) >= str(b):
                continue
            e1 = b in sub.adj[a]
            e2 = phi[b] in Up.adj[phi[a]]
            if e1 != e2:
                print('FAIL Upsilon m=%d (%s,%s)' % (m, a, b)); ok = False
    print('m=%2d  Gamma_%d - {%d,%d,%d} == Gamma_%d  and  Upsilon_%d - {%d,%d,%d} == Upsilon_%d   [entrywise OK]'
          % (m, m, m, 2 * m, 3 * m - 1, m - 1, m, m, 2 * m, 3 * m - 1, m - 1))
print('ALL ENTRYWISE CHECKS PASSED' if ok else 'FAILURES ABOVE')
