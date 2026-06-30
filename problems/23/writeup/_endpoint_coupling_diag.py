"""DIAGNOSTIC for the DIRECT ENDPOINT-CURVATURE coupling angle on crux lemma (A).

Per odd-L gamma-min connected-B max-cut row P=(x_0..x_{L-1}), compute exactly:
  N, Gamma, L
  T_i = T[x_i], h_i=T_i/N, S=sum h_i, q=min cyclic h_i h_{i+1}
  delta = (S/L)^2 - q  (>=0),   delL2 = L^2*delta = S^2 - L^2 q
  E0 = DG(x_0)+DG(x_{L-1})  (renormalized endpoint curvature; 0 if a flip not neutral/connected)
  RHS = (L/5)*(N^2-Gamma)
  The crux atom (A):  E0 + delL2 <= 25 * RHS / 25 ?? -- use the SOLVED form B_L>=E0:
     B_L = L*(N^2-Gamma) - 25*sum(T_i-N) - delL2   ;  lemma (A) :  B_L >= E0.
  ENDPOINT LOAD GAP candidates:
     gap_end = |T_0 - N| + |T_{L-1} - N|   (deviation of endpoint loads from N)
     gend    = (T_0 - N) + (T_{L-1} - N)   (signed)
     gmid    = sum_{i=1}^{L-2}(T_i - N)     (interior signed deviation)
  Also the per-vertex sum  D = sum_i (T_i - N).

We DUMP, per row, these exact rationals and several CANDIDATE coupled inequalities, reporting
min slack (as float for ranking) + exact at the binding row, to FIND a direct two-sided law:
   (C1)  E0 <= -c * gend_pos  +  k * something    (negative curvature absorbs dispersion)
   (C2)  delL2 <= kappa * (N^2-Gamma) - mu*(-E0)  (dispersion paid by curvature credit)
Output guides the StructuredOutput claim.  ALL exact Fraction.
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
    if not Bconn(n, adj, s2): return None
    dB, dM = deltas(n, adj, side, {v})
    if dB != dM: return None
    g1 = gamma_of(n, adj, s2)
    if g1 is None: return None
    return g1 - Gamma

def rows_for_cut(n, adj, side):
    st = struct_for_side(n, adj, side)
    if st is None: return []
    M, ell, T, mu, cyc = st
    N = F(n); Gamma = sum(T)
    out = []
    for f in M:
        L = ell[f]
        if L % 2 == 0: continue
        for P in cyc[f]:
            if len(P) != L: continue
            x = P
            Ti = [T[x[i]] for i in range(L)]
            h = [Ti[i]/N for i in range(L)]
            S = sum(h)
            q = min(h[i]*h[(i+1) % L] for i in range(L))
            delL2 = S*S - (L*L)*q          # = L^2 * delta
            D = sum(Ti[i] - N for i in range(L))
            B_L = L*(N*N - Gamma) - 25*D - delL2
            dg0 = endpoint_dg(n, adj, side, x[0], Gamma)
            dgL = endpoint_dg(n, adj, side, x[-1], Gamma)
            # E0 only defined when BOTH endpoint flips are admissible; else mark None
            if dg0 is None or dgL is None:
                E0 = None
            else:
                E0 = dg0 + dgL
            gend = (Ti[0]-N) + (Ti[-1]-N)
            gend_abs = abs(Ti[0]-N) + abs(Ti[-1]-N)
            out.append(dict(N=N, L=L, Gamma=Gamma, Ti=Ti, S=S, q=q,
                            delL2=delL2, D=D, B_L=B_L, E0=E0,
                            gend=gend, gend_abs=gend_abs,
                            RHSfull=(N*N-Gamma)))
    return out

def families():
    fams = []
    for nn in range(5, 12):
        outg = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        for g6 in outg:
            n, E = dec(g6); fams.append(("cen%d-%s" % (nn, g6), n, E))
    for sizes in [(1,1,1,1,1),(2,2,2,2,2),(2,1,2,1,2),(3,2,3,2,3),(2,1,2,1,3),
                  (3,1,1,1,1),(2,1,1,1,1),(1,2,1,2,1),(3,3,2,2,2)]:
        if sum(sizes) <= 14:
            n, E = odd_blowup(5, list(sizes)); fams.append(("C5%s" % (sizes,), n, E))
    for sizes in [(1,1,1,1,1,1,1),(2,1,1,1,1,1,1),(2,2,1,1,1,1,1)]:
        if sum(sizes) <= 14:
            n, E = odd_blowup(7, list(sizes)); fams.append(("C7%s" % (sizes,), n, E))
    # Mycielskians
    for base, lbl in [(Cn(5),'C5'),(Cn(7),'C7')]:
        try:
            n, E = mycielski(*base) if isinstance(base, tuple) else (None,None)
        except Exception:
            n, E = (None, None)
    return fams

def main():
    fams = families()
    rows = []
    for (name, n, E) in fams:
        adj, cuts = gmins(n, E)
        for side in cuts:
            for r in rows_for_cut(n, adj, side):
                r['name'] = name
                rows.append(r)
    # Filter to rows with defined E0 (both endpoints admissible)
    defrows = [r for r in rows if r['E0'] is not None]
    print("TOTAL odd-L rows:", len(rows), " with E0 defined:", len(defrows))

    # --- Statistic 1: confirm crux atom B_L >= E0 (lemma A) on defrows ---
    bad = [r for r in defrows if r['B_L'] < r['E0']]
    print("Lemma(A) B_L>=E0 violations:", len(bad))

    # --- Statistic 2: sign of E0 vs dispersion delL2.  Hypothesis: E0<0 when delL2 large. ---
    # bucket by E0 sign
    neg = [r for r in defrows if r['E0'] < 0]
    pos = [r for r in defrows if r['E0'] > 0]
    zer = [r for r in defrows if r['E0'] == 0]
    def avg(rs, key):
        if not rs: return None
        return float(sum(r[key] for r in rs))/len(rs)
    print("E0<0: %d rows, avg delL2=%s, avg gend=%s" % (len(neg), avg(neg,'delL2'), avg(neg,'gend')))
    print("E0=0: %d rows, avg delL2=%s, avg gend=%s" % (len(zer), avg(zer,'delL2'), avg(zer,'gend')))
    print("E0>0: %d rows, avg delL2=%s, avg gend=%s" % (len(pos), avg(pos,'delL2'), avg(pos,'gend')))

    # --- CANDIDATE COUPLED LAW under test ---
    # (CL):  delL2 + E0  <=  (L/5)*(N^2 - Gamma)   [the DECOUPLED-FALSE delL2 alone, but with +E0 credit]
    # equivalently:  E0 <= (L/5)(N^2-Gamma) - delL2.  We KNOW B_L>=E0 i.e.
    #   E0 <= L(N^2-Gamma) - 25 D - delL2. Compare (L/5) coefficient.
    # Test the SHARP per-row claim:  delL2 <= (L/5)*(N^2-Gamma) + max(0,-E0)   (curvature credit fills the gap)
    viol_CL = []
    minslackCL = None
    for r in defrows:
        L = r['L']
        credit = -r['E0'] if r['E0'] < 0 else F(0)
        lhs = r['delL2']
        rhs = F(L,5)*r['RHSfull'] + credit
        slack = rhs - lhs
        if slack < 0: viol_CL.append(r)
        if minslackCL is None or slack < minslackCL[0]:
            minslackCL = (slack, r)
    print("\n(CL) delL2 <= (L/5)(N^2-G) + max(0,-E0):  viols=%d  min slack=%s"
          % (len(viol_CL), str(minslackCL[0]) if minslackCL else None))
    if minslackCL:
        r = minslackCL[1]
        print("   binding row %s L=%d N=%s G=%s delL2=%s E0=%s" %
              (r['name'], r['L'], r['N'], r['Gamma'], r['delL2'], r['E0']))

    # --- Test the STRONGER decoupled-with-credit at coefficient 1/5 exactly tight on C5[t] ---
    # On C5[t]: T==N so delL2=0, E0=0, both sides 0. Tightness check:
    c5 = [r for r in defrows if r['name'].startswith('C5(1, 1, 1, 1, 1)') or
          (r['delL2']==0 and r['E0']==0)]
    print("\nrows with delL2==0 and E0==0 (C5-like tight):", len(c5))

    # --- Test the two-sided endpoint-gap couplings ---
    # (G1)  -E0 >= delL2 - (L/5)(N^2-G)     <=> (CL)   [already]
    # (G2)  -E0 <= 2*gend_abs * N           (curvature bounded by endpoint load deviation)?
    viol_G2 = 0; minG2 = None
    for r in defrows:
        lhs = -r['E0']
        rhs = 2*r['gend_abs']*r['N']
        slack = rhs - lhs
        if slack < 0: viol_G2 += 1
        if minG2 is None or slack < minG2[0]: minG2 = (slack, r)
    print("(G2) -E0 <= 2*gend_abs*N: viols=%d min slack=%s" % (viol_G2, str(minG2[0]) if minG2 else None))

    # dump a few extreme rows: largest delL2, most negative E0
    defrows.sort(key=lambda r: float(r['delL2']), reverse=True)
    print("\nTOP 5 by delL2:")
    for r in defrows[:5]:
        print("  %s L=%d N=%s delL2=%s E0=%s gend=%s D=%s (L/5)(N^2-G)=%s" %
              (r['name'][:18], r['L'], r['N'], r['delL2'], r['E0'], r['gend'], r['D'],
               F(r['L'],5)*r['RHSfull']))
    defrows.sort(key=lambda r: float(r['E0']))
    print("MOST NEGATIVE E0:")
    for r in defrows[:5]:
        print("  %s L=%d N=%s delL2=%s E0=%s gend=%s (L/5)(N^2-G)=%s" %
              (r['name'][:18], r['L'], r['N'], r['delL2'], r['E0'], r['gend'],
               F(r['L'],5)*r['RHSfull']))

if __name__ == "__main__":
    main()
