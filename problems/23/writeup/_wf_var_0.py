"""Explore the FAN-AVERAGING variance inequality n*(n-row_f) >= var_f for NONUNIQUE bad edges f.
Goal: understand the slack structure and test candidate sub-lemmas EXACTLY (Fraction).

Definitions (match _fanavg_var_gate.py):
  M = bad (monochromatic) edges; for g, cyc[g]=B-geodesics, each ell[g] vertices.
  p_g(v) = (#geodesics of g thru v)/|cyc(g)|; sum_v p_g(v)=ell[g].
  S(v) = sum_g p_g(v).  row_f = sum_v p_f(v) S(v).  ell_f = sum_v p_f(v).
  var_f = sum_v p_f(v) S(v)^2 - row_f^2/ell_f.
  Target: n(n-row_f) >= var_f.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint


def build(n, adj, s):
    st = struct_for_side(n, adj, s)
    if st is None:
        return None
    M, ell, T, mu, cyc = st
    S = [F(0)] * n
    pf = {}
    for g in M:
        Ps = cyc[g]; k = len(Ps); d = {}
        for P in Ps:
            for v in P:
                d[v] = d.get(v, F(0)) + F(1, k)
        pf[g] = d
        for v, pv in d.items():
            S[v] += pv
    return M, ell, T, mu, cyc, S, pf


def rowdata(n, M, cyc, S, pf, f):
    d = pf[f]
    ll = sum(d.values())
    row = sum(d[v] * S[v] for v in d)
    mean = row / ll
    var = sum(d[v] * (S[v] - mean) ** 2 for v in d)
    margin = F(n) * (F(n) - row) - var
    # also second-moment form
    sm = sum(d[v] * S[v] ** 2 for v in d)   # = var + row^2/ll
    Smax = max(S[v] for v in d)             # max S on the geodesic support of f
    return dict(ll=ll, row=row, mean=mean, var=var, margin=margin, sm=sm, Smax=Smax,
                d=d, support=set(d))


def iter_battery():
    # census N<=11
    for nn in range(7, 12):
        outg = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        for g6 in outg:
            n, E = dec(g6)
            adj, cuts = gmins(n, E)
            for s in cuts:
                yield (f"cen{nn}:{g6}", n, adj, s)

    def bridge(b1, b2, u, v):
        n, E = union_disjoint(b1, b2); n1 = b1[0]; return n, E + [(u, n1 + v)]

    def blowup(parts):
        m = len(parts); off = [0] * (m + 1)
        for i in range(m):
            off[i + 1] = off[i] + parts[i]
        nn = off[m]; EE = []
        for i in range(m):
            j = (i + 1) % m
            for a in range(off[i], off[i + 1]):
                for b in range(off[j], off[j + 1]):
                    EE.append((min(a, b), max(a, b)))
        return nn, EE

    extra = [("M(C7)",) + mycielski(7, Cn(7)),
             ("M(C9)",) + mycielski(9, Cn(9)),
             ("M(C11)",) + mycielski(11, Cn(11)),
             ("M(Grotzsch)N23",) + mycielski(*mycielski(5, Cn(5))),
             ("C7brgGrot",) + bridge((7, Cn(7)), mycielski(5, Cn(5)), 0, 0),
             ("C9brgC9",) + bridge((9, Cn(9)), (9, Cn(9)), 0, 0),
             ("C5[2]",) + blowup([2, 2, 2, 2, 2]),
             ("C5[3]",) + blowup([3, 3, 3, 3, 3]),
             ("C5unbal",) + blowup([1, 5, 2, 2, 5]),
             ("C7unbal",) + blowup([1, 4, 2, 4, 2, 4, 2]),
             ("C5[1,6,2,2,6]",) + blowup([1, 6, 2, 2, 6])]
    for nm, nn, EE in extra:
        adj, cuts = gmins(nn, EE)
        for s in cuts:
            yield (nm, nn, adj, s)


if __name__ == "__main__":
    print("=== explore fan-averaging var ineq: slack stats over battery (nonunique rows) ===", flush=True)
    nrows = 0
    worst_margin = None; worst_case = None
    # collect distribution of useful quantities
    stat = {'margin_le_0': 0, 'Smax_gt_n': 0, 'row_gt_n': 0}
    examples = []
    for nm, n, adj, s in iter_battery():
        b = build(n, adj, s)
        if b is None:
            continue
        M, ell, T, mu, cyc, S, pf = b
        for f in M:
            if len(cyc[f]) < 2:
                continue
            rd = rowdata(n, M, cyc, S, pf, f)
            nrows += 1
            if rd['margin'] <= 0:
                stat['margin_le_0'] += 1
            if rd['Smax'] > n:
                stat['Smax_gt_n'] += 1
            if rd['row'] > n:
                stat['row_gt_n'] += 1
            if worst_margin is None or rd['margin'] < worst_margin:
                worst_margin = rd['margin']
                worst_case = (nm, f, str(rd['row']), str(rd['ll']), str(rd['var']), str(rd['Smax']), n)
            if len(examples) < 5:
                examples.append((nm, f, str(rd['row']), str(rd['var']), str(rd['margin']), str(rd['Smax']), n))
    print("nonunique rows tested:", nrows)
    print("stats:", stat)
    print("worst margin:", worst_margin)
    print("worst case (nm,f,row,ll,var,Smax,n):", worst_case)
    for e in examples:
        print("  ex:", e)
