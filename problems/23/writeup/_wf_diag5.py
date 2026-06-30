"""Self-contained EXACT Farkas witness on the 3-row core. y=(-1,1/2,1/2).
   Verifies: for EVERY generator c, sum_i y_i g_i[c] <= 0, while sum_i y_i b_i > 0.
   => no lambda>=0 with G lambda = b (uniform) => cone INFEASIBLE, exact."""
from _wf_deficit_farkas import collect_rows, NGEN, GEN_LABELS
from fractions import Fraction as F
from _h import dec

core_specs = [('ECxo', (3, 0, 4, 1, 5)), ('F?bBo', (4, 0, 5, 1, 6)), ('F?bBo', (0, 4, 6, 1, 5))]
y = [F(-1), F(1, 2), F(1, 2)]
rowsidx = {}
cache = {}
core = []
for g6, P in core_specs:
    if g6 not in cache:
        n, E = dec(g6)
        cache[g6] = {r['P']: r for r in collect_rows('cen'+g6, n, E)}
    core.append(cache[g6][P])

# A^T y entrywise
colmax = None
worstcol = None
for c in range(NGEN):
    s = sum(y[i]*core[i]['g'][c] for i in range(3))
    if colmax is None or s > colmax:
        colmax = s; worstcol = GEN_LABELS[c]
bty = sum(y[i]*core[i]['b'] for i in range(3))
print('Farkas y = (-1, 1/2, 1/2)')
print('max over generators of (y . column) =', colmax, ' at', worstcol, '  (need <= 0)')
print('y . b =', bty, '=', float(bty), '  (need > 0)')
print('VALID EXACT FARKAS CERT OF INFEASIBILITY:', (colmax <= 0 and bty > 0))
print()
print('Identity read: y0*b0 + y1*b1 + y2*b2 =', '-(%s) + (1/2)(%s) + (1/2)(%s)' %
      (core[0]['b'], core[1]['b'], core[2]['b']), '=', bty)
