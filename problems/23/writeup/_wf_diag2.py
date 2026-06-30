"""Exact Farkas obstruction + does group-G (product-slacks) help vs size-only cone?"""
from _wf_deficit_farkas import families, collect_rows, NGEN, GEN_LABELS
from fractions import Fraction as F
import numpy as np
from scipy.optimize import linprog
import collections

rows = []
for (name, n, E) in families():
    try:
        rows += collect_rows(name, n, E)
    except Exception:
        pass

# dedup
seen = {}; ded = []
for r in rows:
    key = (r['b'], tuple(r['g']))
    if key not in seen:
        seen[key] = 1; ded.append(r)
R = len(ded)
A = np.array([[float(ded[i]['g'][c]) for c in range(NGEN)] for i in range(R)], float)
b = np.array([float(ded[i]['b']) for i in range(R)], float)

def feasible(cols):
    Asub = A[:, cols]
    res = linprog(np.zeros(len(cols)), A_eq=Asub, b_eq=b, bounds=[(0, None)]*len(cols), method="highs")
    return res.success

# group column index sets
def cols_for(prefix):
    return [i for i, lab in enumerate(GEN_LABELS) if lab.startswith(prefix)]
gA = cols_for('A.'); gB = cols_for('B.'); gC = cols_for('C.')
gD = cols_for('D.'); gE = cols_for('E.'); gF = cols_for('F.'); gG = cols_for('G.')
size_only = gA + gB + gC + gD + gE + gF        # everything EXCEPT product-slacks
full = list(range(NGEN))
print('FEASIBLE full (with product-slacks):', feasible(full))
print('FEASIBLE size-only (no product-slacks):', feasible(size_only))
print('FEASIBLE only dGamma (A+B+C):', feasible(gA+gB+gC))
print('FEASIBLE only maxcut (D+E+F):', feasible(gD+gE+gF))
print('FEASIBLE dGamma+prodslack (A+B+C+G):', feasible(gA+gB+gC+gG))
print('FEASIBLE maxcut+prodslack (D+E+F+G):', feasible(gD+gE+gF+gG))

# Exact Farkas direction on FULL via rational LP would be heavy; instead find a SMALL infeasible
# row subset greedily, then exact-verify the dual on that subset.
# Greedy: start from the Farkas-heavy rows.
cc = -b
res2 = linprog(cc, A_ub=A.T, b_ub=np.zeros(NGEN), bounds=[(-1, 1)]*R, method="highs")
y = res2.x
order = sorted(range(R), key=lambda r: -abs(y[r]))
# minimal support of y
supp = [r for r in order if abs(y[r]) > 1e-6]
print('Farkas direction support size:', len(supp), 'obj b^T y =', -res2.fun)
fam = collections.Counter(ded[r]['name'] for r in supp)
print('Farkas-support families:', fam.most_common(12))

# Try to find a SMALL infeasible subset: take top-k Farkas rows + verify infeasible
for k in [2, 3, 5, 8, 12, 20]:
    sub = supp[:k]
    Asub = A[sub, :]; bsub = b[sub]
    r = linprog(np.zeros(NGEN), A_eq=Asub, b_eq=bsub, bounds=[(0, None)]*NGEN, method="highs")
    print('  subset top-%d rows -> feasible? %s' % (k, r.success))
    if not r.success:
        print('     SMALLEST infeasible row block, names+b:')
        for rr in sub:
            print('       %-18s N=%d b=%.4f P=%s' % (ded[rr]['name'], ded[rr]['N'], ded[rr]['b'], ded[rr]['P']))
        break
