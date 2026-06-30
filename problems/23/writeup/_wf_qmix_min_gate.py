"""Corrected closing gate: use Q_mix* = MIN over admissible five-shadows phi (phi(x_i)=i)
   of Q_mix(phi).  Unlike the canonical bluedist shadow, Q_mix* VANISHES at the C5[t] extremal
   (the balanced part-shadow achieves 0), so it is admissible as an EQUALITY-cone generator
   (a generator must vanish wherever the target 25*M vanishes).  Still nonneg (each Q_mix>=0),
   still breaks the 3-row-core dual (min = canonical there).

   Targeted battery (must include the C5[2] extremal that forced theta=0 with canonical):
   census N<=9 + C5[1,2] + nonuniform C5 + glued C5|C7.  Exact verify if feasible; else extract dual.
"""
import sys, subprocess, itertools
from collections import deque
from fractions import Fraction as F
import numpy as np
from scipy.optimize import linprog

from _wf_deficit_farkas import build_rows_for_cut, GEN_LABELS, odd_blowup, families
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import Cn, union_disjoint

def qmix_min(n, T, Gamma, P):
    """min over phi:V->Z5, phi(x_i)=i, of  Gamma - 25*min_i n_i w_{i+1}.  Exact Fraction."""
    N = F(n)
    fixed = {P[i]: i for i in range(5)}
    free = [v for v in range(n) if v not in fixed]
    best = None
    for assign in itertools.product(range(5), repeat=len(free)):
        ncnt = [0]*5; wsum = [F(0)]*5
        for i in range(5):
            ncnt[i] += 1; wsum[i] += T[P[i]]
        for v, c in zip(free, assign):
            ncnt[c] += 1; wsum[c] += T[v]
        w = [wsum[i]/N for i in range(5)]
        mn = min(F(ncnt[i])*w[(i+1) % 5] for i in range(5))
        Q = Gamma - 25*mn
        if best is None or Q < best: best = Q
    return best

EXT = GEN_LABELS + ["H.Qmix.min"]
NEXT = len(EXT)

def collect_ext(name, n, E):
    adj, cuts = gmins(n, E)
    rows = []
    for side in cuts:
        base = build_rows_for_cut(n, adj, side, name)
        if not base: continue
        st = struct_for_side(n, adj, side)
        if st is None: continue
        M, ell, T, mu, cyc = st; Gamma = sum(T)
        for r in base:
            Q = qmix_min(n, T, Gamma, r['P'])
            r['g'] = list(r['g']) + [Q if Q is not None else F(0)]
            rows.append(r)
    return rows

def main():
    fams = []
    for nn in range(5, 10):
        outg = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        for g6 in outg:
            n, E = dec(g6); fams.append(("cen%d-%s" % (nn, g6), n, E))
    for sizes in [(1,1,1,1,1),(2,2,2,2,2),(2,1,2,1,2),(2,1,2,1,3)]:
        n, E = odd_blowup(5, list(sizes)); fams.append(("C5%s" % (sizes,), n, E))
    n5, E5 = 5, Cn(5); n7, E7 = 7, Cn(7)
    n, E = union_disjoint((n5, E5), (n7, E7)); E = E + [(0, n5)]
    fams.append(("glue_C5|C7", n, E))

    rows = []
    for (name, n, E) in fams:
        rows += collect_ext(name, n, E)
    print("collected %d rows; gens=%d (45 + Qmix_min)" % (len(rows), NEXT)); sys.stdout.flush()
    R = len(rows)
    A = np.array([[float(rows[r]['g'][c]) for c in range(NEXT)] for r in range(R)], float)
    b = np.array([float(rows[r]['b']) for r in range(R)], float)
    res = linprog(np.zeros(NEXT), A_eq=A, b_eq=b, bounds=[(0, None)]*NEXT, method="highs")
    print("LP:", res.message, "| success:", res.success)
    if not res.success:
        print(">>> INFEASIBLE with Qmix_min too. The Farkas-cone route is dead; pivot to one-sided lemma.")
        return
    lam = [F(res.x[c]).limit_denominator(100000) for c in range(NEXT)]
    bad = [(r, rows[r]['name']) for r in range(R)
           if sum(rows[r]['g'][c]*lam[c] for c in range(NEXT)) != rows[r]['b']]
    sup = [(EXT[c], str(lam[c])) for c in range(NEXT) if lam[c] != 0]
    print("rational support:", sup)
    if not bad:
        print(">>> EXACT CERTIFICATE FOUND on targeted battery. Escalate to full + Mycielskian.")
    else:
        print(">>> float-feasible but %d rows fail exact rationalization (need exact LP)." % len(bad))

if __name__ == "__main__":
    main()
