"""Q4: value of the degree-2d scheme on Gamma_m as a function of the CUT FAMILY.
Shows that the recorded 'degree-2 infeasible for And(3)' is a property of the restricted
(arc) cut family, not of the multiplier degree.
Usage: python Q4_arcs.py <m> <d> <family>   family in {all, nd, arcs, ndarcs, k}
"""
import sys
import numpy as np
from Q4_graphs import gamma_graph, all_cuts, nondominated_cuts
import Q4_sos as Q

m = int(sys.argv[1]); d = int(sys.argv[2]); fam = sys.argv[3]
n, E = gamma_graph(m)
cuts = all_cuts(n, E)


def as_set(mask):
    return frozenset(v for v in range(n) if v and (mask >> (v - 1)) & 1)


def is_arc(Sset):
    for T in (Sset, frozenset(range(n)) - Sset):
        if not T:
            return True
        k = len(T)
        for s in range(n):
            if T == frozenset((s + i) % n for i in range(k)):
                return True
    return False


if fam == 'all':
    sel = cuts
elif fam == 'nd':
    sel = nondominated_cuts(cuts)
elif fam == 'arcs':
    sel = [c for c in cuts if is_arc(as_set(c[0]))]
elif fam == 'ndarcs':
    sel = [c for c in nondominated_cuts(cuts) if is_arc(as_set(c[0]))]
else:
    raise SystemExit("bad family")
print(f"Gamma_{m} d={d} family={fam}: {len(sel)} cuts")
P = Q.build(n, E, sel, d, mode='coef')
P['prob'].solve(solver='CLARABEL')
print(f"RESULT Gamma_{m} d={d} family={fam} ({len(sel)} cuts): status={P['prob'].status} "
      f"c* = {P['c'].value}")
