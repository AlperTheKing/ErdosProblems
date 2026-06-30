"""Pin minimal infeasible core EXACTLY (Fraction LP via rational nullspace / direct check)."""
from _wf_deficit_farkas import families, collect_rows, NGEN, GEN_LABELS, gmins
from fractions import Fraction as F
import numpy as np
from scipy.optimize import linprog
import itertools

# Rebuild just the small offending families.
import subprocess
from _h import dec, GENG

names = ['DUW', 'ECpo', 'ECxo', 'F?bBo']
rows = []
for g6 in names:
    n, E = dec(g6)
    rows += collect_rows('cen'+g6, n, E)
print('rows from offending block:', len(rows))

# dedup
seen = {}; ded = []
for r in rows:
    key = (r['b'], tuple(r['g']))
    if key not in seen:
        seen[key] = 1; ded.append(r)
R = len(ded)
A = np.array([[float(ded[i]['g'][c]) for c in range(NGEN)] for i in range(R)], float)
b = np.array([float(ded[i]['b']) for i in range(R)], float)
res = linprog(np.zeros(NGEN), A_eq=A, b_eq=b, bounds=[(0, None)]*NGEN, method="highs")
print('block feasible?', res.success)

# Greedy minimal infeasible subset (delete rows while still infeasible)
def infeas(sub):
    Asub = A[sub, :]; bsub = b[sub]
    r = linprog(np.zeros(NGEN), A_eq=Asub, b_eq=bsub, bounds=[(0, None)]*NGEN, method="highs")
    return not r.success

cur = list(range(R))
assert infeas(cur)
changed = True
while changed:
    changed = False
    for r in list(cur):
        trial = [x for x in cur if x != r]
        if trial and infeas(trial):
            cur = trial; changed = True
            break
print('MINIMAL infeasible core size:', len(cur))
for r in cur:
    row = ded[r]
    nz = [(GEN_LABELS[i], row['g'][i]) for i in range(NGEN) if row['g'][i] != 0]
    print('  %-12s N=%d b=%s P=%s' % (row['name'], row['N'], row['b'], row['P']))
    print('     gens:', [(l, (float(v) if v.denominator!=1 else int(v))) for l, v in nz])

# Exact Farkas dual on the minimal core: find rational y, A_core^T y <= 0 entrywise, b_core^T y > 0.
# Solve as a small rational LP by float then rationalize+verify.
core = cur
Ac = np.array([[float(ded[i]['g'][c]) for c in range(NGEN)] for i in core], float)
bc = np.array([float(ded[i]['b']) for i in core], float)
m = len(core)
res2 = linprog(-bc, A_ub=Ac.T, b_ub=np.zeros(NGEN), bounds=[(-1, 1)]*m, method="highs")
yf = res2.x
print('\nFarkas dual on core: obj b^T y =', -res2.fun, 'success', res2.success)
# rationalize y
yr = [F(v).limit_denominator(1000) for v in yf]
# exact check A_core^T y <= 0 and b^T y > 0
Gc = [[ded[i]['g'][c] for c in range(NGEN)] for i in core]
bcF = [ded[i]['b'] for i in core]
colvals = []
for c in range(NGEN):
    s = sum(Gc[i][c]*yr[i] for i in range(m))
    colvals.append(s)
bty = sum(bcF[i]*yr[i] for i in range(m))
print('EXACT check (rationalized y): max col(A^T y) =', max(colvals), '  b^T y =', bty)
print('  all cols <= 0 ?', all(v <= 0 for v in colvals), '   b^T y > 0 ?', bty > 0)
print('  y (rational):', yr)
