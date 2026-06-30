"""Exact gate for Codex's ALL-ODD-L endpoint-curvature lemma (block 363, coefficient 1):

   B_L(P) >= DG(x_0) + DG(x_{L-1})       [strongest; implies the 26/27 form]

   B_L(P) = L*(N^2-Gamma) - 25*sum_{i=0}^{L-1}(T[x_i]-N) - C_L(P)  = 25*M(P)  (unified atom)
     h_i = T[x_i]/N, S = sum_i h_i, q = min_i h_i*h_{(i+1) mod L}, C_L = S^2 - L^2*q.
   DG(endpoint) = Gamma(flip singleton endpoint) - Gamma  if the flip is max-cut-neutral
     (delta_B==delta_M) AND switched-B connected AND struct valid; else 0.
   gamma-min => DG(endpoints) >= 0 => B_L >= 0 => unified atom => conjecture.

   ONE-SIDED per-row inequality (not an equality cone) -> escapes the exact Farkas dual.
   ALL arithmetic exact Fraction.  Reports first violating row + min slack per length.
"""
import sys, subprocess
from fractions import Fraction as F
from _wf_deficit_farkas import gamma_of, deltas, flip
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

def odd_blowup(m, sizes):
    nn = sum(sizes); start = [0]*m
    for i in range(1, m): start[i] = start[i-1] + sizes[i-1]
    E = []
    for i in range(m):
        j = (i+1) % m
        for a in range(sizes[i]):
            for b in range(sizes[j]):
                E.append((start[i]+a, start[j]+b))
    return nn, E

def endpoint_dg(n, adj, side, v, Gamma):
    s2 = flip(side, [v])
    if not Bconn(n, adj, s2): return F(0)
    dB, dM = deltas(n, adj, side, {v})
    if dB != dM: return F(0)
    g1 = gamma_of(n, adj, s2)
    if g1 is None: return F(0)
    return g1 - Gamma

def rows_for_cut(n, adj, side):
    st = struct_for_side(n, adj, side)
    if st is None: return []
    M, ell, T, mu, cyc = st
    N = F(n); Gamma = sum(T)
    out = []
    for f in M:
        L = ell[f]
        if L % 2 == 0: continue          # odd cycles only
        for P in cyc[f]:
            if len(P) != L: continue
            x = P
            h = [T[x[i]]/N for i in range(L)]
            S = sum(h)
            q = min(h[i]*h[(i+1) % L] for i in range(L))
            C_L = S*S - (L*L)*q
            B_L = L*(N*N - Gamma) - 25*sum(T[x[i]] - N for i in range(L)) - C_L
            DG0 = endpoint_dg(n, adj, side, x[0], Gamma)
            DGL = endpoint_dg(n, adj, side, x[-1], Gamma)
            slack = B_L - (DG0 + DGL)
            out.append((L, slack, B_L, DG0, DGL, Gamma, x, [T[xi] for xi in x]))
    return out

def gate_family(name, n, E):
    adj, cuts = gmins(n, E)
    viols = []; nrows = 0
    minslack = {}   # L -> (slack, row)
    for side in cuts:
        for (L, slack, B_L, DG0, DGL, Gamma, x, Tp) in rows_for_cut(n, adj, side):
            nrows += 1
            if slack < 0:
                viols.append((name, n, L, x, str(B_L), str(DG0), str(DGL), str(Gamma)))
            if L not in minslack or slack < minslack[L][0]:
                minslack[L] = (slack, (name, n, x, str(B_L), str(DG0), str(DGL)))
    return nrows, viols, minslack

def main():
    fams = []
    # census N<=11 triangle-free connected (exhaustive gamma-min cuts)
    for nn in range(5, 12):
        outg = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        for g6 in outg:
            n, E = dec(g6); fams.append(("cen%d-%s" % (nn, g6), n, E))
    # theta witnesses
    for g6 in ["G?Fw", "G?bFw", "G?rFw", "H?AFBo]"]:
        try:
            n, E = dec(g6); fams.append(("thw-%s" % g6, n, E))
        except Exception: pass
    # C5[t] uniform + nonuniform + stress
    for sizes in [(1,1,1,1,1),(2,2,2,2,2),(2,1,2,1,2),(3,2,3,2,3),(2,1,2,1,3),
                  (3,1,1,1,1),(2,1,1,1,1),(1,2,1,2,1)]:
        if sum(sizes) <= 12:
            n, E = odd_blowup(5, list(sizes)); fams.append(("C5%s" % (sizes,), n, E))
    # C7[t] (test longer odd girth)
    for sizes in [(1,1,1,1,1,1,1),(2,1,1,1,1,1,1)]:
        if sum(sizes) <= 12:
            n, E = odd_blowup(7, list(sizes)); fams.append(("C7%s" % (sizes,), n, E))
    # glued islands (the Farkas killers)
    n5, E5 = 5, Cn(5); n7, E7 = 7, Cn(7)
    n, E = union_disjoint((n5, E5), (n7, E7)); E = E + [(0, n5)]
    fams.append(("glue_C5|C7", n, E))
    n, E = union_disjoint((n5, E5), (n7, E7)); E = E + [(0, n5),(2, n5+3)]
    fams.append(("glue2_C5|C7", n, E))

    total = 0; allviol = []; agg = {}
    for (name, n, E) in fams:
        nr, viols, ms = gate_family(name, n, E)
        total += nr
        if viols:
            allviol += viols
            print("VIOLATION %s: %d" % (name, len(viols)))
            for v in viols[:3]: print("   ", v);
            sys.stdout.flush()
        for L,(s,row) in ms.items():
            if L not in agg or s < agg[L][0]: agg[L] = (s, row)
    print("="*60)
    print("TOTAL ODD-L ROWS:", total)
    print("VIOLATIONS:", len(allviol))
    for L in sorted(agg):
        print("  L=%d  min slack = %s   at %s" % (L, str(agg[L][0]), agg[L][1][:3]))
    if allviol:
        print("FIRST VIOLATION:", allviol[0])
    else:
        print("ALL-L COEFFICIENT-1 ENDPOINT-CURVATURE LEMMA HOLDS (exact Fraction).")

if __name__ == "__main__":
    main()
