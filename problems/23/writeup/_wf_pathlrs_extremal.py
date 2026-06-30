"""Probe the PATH-LRS / ROW-LRS extremal structure on C5[t] (uniform blow-up), where LRS is tight.
Goal: confirm Sum_v T = Gamma exactly, and report the EXACT slack of each sub-lemma at the extremal,
to see which inequality is tight (zero residual) at C5[t] (the conjectured extremal a(5n)=n^2).
"""
from fractions import Fraction as F
from _satzmu_conn import struct_for_side
from _stark1 import gmins

def blowup(parts):
    mm = len(parts); off = [0]*(mm+1)
    for i in range(mm): off[i+1] = off[i]+parts[i]
    nn = off[mm]; EE = []
    for i in range(mm):
        j = (i+1) % mm
        for a in range(off[i], off[i+1]):
            for b in range(off[j], off[j+1]): EE.append((min(a, b), max(a, b)))
    return nn, sorted(set(EE))

for t in (1, 2, 3, 4, 5):
    n, E = blowup([t]*5)
    adj, cuts = gmins(n, E)
    if not cuts:
        print("C5[%d] N=%d: no gmin cut" % (t, n)); continue
    side = cuts[0]
    st = struct_for_side(n, adj, side)
    if st is None:
        print("C5[%d]: struct None" % t); continue
    M, ell, T, mu, cyc = st
    N = F(n); m = len(M); Gamma = sum(ell[f]**2 for f in M)
    sumT = sum(T); sumT2 = sum(t2*t2 for t2 in T)
    slack = N*N/F(25) - m
    # LRS slack
    lrs_slack = Gamma*(N + slack) - sumT2
    # ROW-LRS worst
    rowmin = None
    for f in M:
        Oell_f = sum(T[v] for v in cyc[f][0])  # not needed; compute A_f directly
    # A_f
    Pf = {}
    rows = []
    for f in M:
        k = len(cyc[f]); pf = {}
        for P in cyc[f]:
            for v in P: pf[v] = pf.get(v, F(0)) + F(1, k)
        Af = sum(pf[v]*T[v] for v in pf)/ell[f]
        rows.append((f, ell[f], Af, (N+slack)-Af))
    rowmin = min(r[3] for r in rows)
    print("C5[%d] N=%d m=%d Gamma=%d N^2=%d sumT=%s(=Gamma:%s) sumT2=%s slack(N^2/25-m)=%s"
          % (t, n, m, Gamma, n*n, sumT, sumT == Gamma, sumT2, slack), flush=True)
    print("   LRS slack=%s  ROW-LRS worst-margin=%s  Tset=%s"
          % (lrs_slack, rowmin, sorted(set(str(x) for x in T))), flush=True)
