"""Gate Codex's endpoint-DG dichotomy (367): for each odd-L row, is DG(endpoint) in {0, L^2-1}?
   Can both endpoints be positive simultaneously?  Report distinct nonzero DG values per L,
   #rows with DG0>0, DGL>0, both>0, and the fraction of rows with DGsum=0 (vacuity measure).
"""
import subprocess
from fractions import Fraction as F
from _wf_deficit_farkas import gamma_of, deltas, flip, odd_blowup
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import Cn, union_disjoint, mycielski

def edg(n, adj, side, v, G):
    s2 = flip(side, [v])
    if not Bconn(n, adj, s2): return F(0)
    dB, dM = deltas(n, adj, side, {v})
    if dB != dM: return F(0)
    g1 = gamma_of(n, adj, s2)
    return F(0) if g1 is None else g1 - G

def scan(name, n, E, agg):
    adj, cuts = gmins(n, E)
    for side in cuts:
        st = struct_for_side(n, adj, side)
        if st is None: continue
        M, ell, T, mu, cyc = st; G = sum(T)
        for f in M:
            L = ell[f]
            if L % 2 == 0: continue
            for P in cyc[f]:
                if len(P) != L: continue
                d0 = edg(n, adj, side, P[0], G); dL = edg(n, adj, side, P[-1], G)
                a = agg.setdefault(L, dict(rows=0, dg0pos=0, dgLpos=0, both=0, vals=set(), bad=[]))
                a['rows'] += 1
                if d0 > 0: a['dg0pos'] += 1
                if dL > 0: a['dgLpos'] += 1
                if d0 > 0 and dL > 0: a['both'] += 1
                for d in (d0, dL):
                    if d != 0:
                        a['vals'].add(d)
                        if d != F(L*L-1) and len(a['bad']) < 3:
                            a['bad'].append((name, n, L, tuple(P), str(d)))

def main():
    agg = {}
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); scan("cen%d" % nn, n, E, agg)
    for g6 in ["H?AFBo]"]:
        n, E = dec(g6); scan("thw", n, E, agg)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(2,2,2,2,2)]:
        n, E = odd_blowup(5, list(sizes)); scan("C5", n, E, agg)
    for sizes in [(1,)*7,(2,1,1,1,1,1,1)]:
        if sum(sizes) <= 11:
            n, E = odd_blowup(7, list(sizes)); scan("C7", n, E, agg)
    for L in sorted(agg):
        a = agg[L]
        print("L=%d: rows=%d  DG0>0:%d  DGL>0:%d  both>0:%d  vacuous(DG=0)=%.4f  nonzero-vals=%s  L^2-1=%d"
              % (L, a['rows'], a['dg0pos'], a['dgLpos'], a['both'],
                 1 - (a['dg0pos']+a['dgLpos']-a['both'])/a['rows'],
                 sorted(str(v) for v in a['vals']), L*L-1))
        if a['bad']:
            print("   OFF-DICHOTOMY (DG not in {0,L^2-1}):", a['bad'])

if __name__ == "__main__":
    main()
