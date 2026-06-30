"""TRUE (unrestricted) signed endpoint curvature for the DIRECT angle.

The admissible endpoint_dg (neutral+connected) is >=0 by gamma-minimality and HIDES the
signed curvature.  Here we compute the RAW Gamma-change of flipping the endpoint pair
{x_0, x_{L-1}} TOGETHER and SINGLY, WITHOUT requiring neutrality, and renormalize so that
the value is 0 on the balanced C5[t] blow-up.  We then test direct couplings to delta.

Raw flip Gamma change: flip a set U of vertices to the other side, recompute the WHOLE
structure (M', ell', T', Gamma') via struct_for_side on the flipped side.  If the flip is
not max-cut (delta_M(U) > delta_B(U)) the cut is no longer maximum -> we still record the
RAW Gamma change but FLAG it (these are exactly the rows where the curvature is informative).

E0raw(U) = Gamma'(flip U) - Gamma     (None if struct invalid / disconnected B)

We test, per odd-L row:
  pair flip U={x_0,x_{L-1}} -> E0pair
  We look at whether  delL2 + E0pair <= (L/5)(N^2-G)   (the coupled atom with RAW curvature)
  and whether E0pair correlates NEGATIVELY with delL2 (dispersion -> negative curvature).
ALL exact Fraction.
"""
import sys, subprocess
from fractions import Fraction as F
from _wf_deficit_farkas import gamma_of, deltas, flip
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins

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

def raw_dg(n, adj, side, U, Gamma):
    s2 = flip(side, list(U))
    if not Bconn(n, adj, s2): return None
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
            delL2 = S*S - (L*L)*q
            D = sum(Ti[i] - N for i in range(L))
            RHSfull = N*N - Gamma
            # RAW pair flip and single flips (no neutrality requirement)
            E0pair = raw_dg(n, adj, side, {x[0], x[-1]}, Gamma)
            dM_pair, dB_pair = (lambda r: (r[1], r[0]))(deltas(n, adj, side, {x[0], x[-1]}))
            out.append(dict(name=None, N=N, L=L, Gamma=Gamma, delL2=delL2, D=D,
                            RHSfull=RHSfull, E0pair=E0pair,
                            dB_pair=dB_pair, dM_pair=dM_pair,
                            gend=(Ti[0]-N)+(Ti[-1]-N)))
    return out

def families():
    fams = []
    for nn in range(5, 11):
        outg = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        for g6 in outg:
            n, E = dec(g6); fams.append(("cen%d-%s" % (nn, g6), n, E))
    for sizes in [(1,1,1,1,1),(2,2,2,2,2),(2,1,2,1,2),(3,2,3,2,3),(2,1,2,1,3),
                  (3,1,1,1,1),(2,1,1,1,1),(1,2,1,2,1)]:
        if sum(sizes) <= 12:
            n, E = odd_blowup(5, list(sizes)); fams.append(("C5%s" % (sizes,), n, E))
    for sizes in [(1,1,1,1,1,1,1),(2,1,1,1,1,1,1)]:
        if sum(sizes) <= 12:
            n, E = odd_blowup(7, list(sizes)); fams.append(("C7%s" % (sizes,), n, E))
    return fams

def main():
    fams = families()
    rows = []
    for (name, n, E) in fams:
        adj, cuts = gmins(n, E)
        for side in cuts:
            for r in rows_for_cut(n, adj, side):
                r['name'] = name; rows.append(r)
    defr = [r for r in rows if r['E0pair'] is not None]
    print("rows:", len(rows), " with RAW E0pair defined:", len(defr))

    neg = [r for r in defr if r['E0pair'] < 0]
    zer = [r for r in defr if r['E0pair'] == 0]
    pos = [r for r in defr if r['E0pair'] > 0]
    def avg(rs,k):
        return float(sum(r[k] for r in rs))/len(rs) if rs else None
    print("RAW E0pair<0: %d  avg delL2=%s  avg gend=%s" % (len(neg), avg(neg,'delL2'), avg(neg,'gend')))
    print("RAW E0pair=0: %d  avg delL2=%s" % (len(zer), avg(zer,'delL2')))
    print("RAW E0pair>0: %d  avg delL2=%s  avg gend=%s" % (len(pos), avg(pos,'delL2'), avg(pos,'gend')))

    # CORE COUPLED ATOM with RAW curvature: does delL2 + E0pair <= (L/5)(N^2-G)?
    v1=0; m1=None
    for r in defr:
        slack = F(r['L'],5)*r['RHSfull'] - (r['delL2'] + r['E0pair'])
        if slack < 0: v1 += 1
        if m1 is None or slack < m1[0]: m1=(slack,r)
    print("\n(RAW-CL) delL2 + E0pair <= (L/5)(N^2-G):  viols=%d  min slack=%s" %
          (v1, str(m1[0]) if m1 else None))
    if m1 and m1[0] < 0:
        r=m1[1]; print("  WORST: %s L=%d N=%s delL2=%s E0pair=%s dM=%s dB=%s" %
                        (r['name'][:20], r['L'], r['N'], r['delL2'], r['E0pair'], r['dM_pair'], r['dB_pair']))

    # Restrict to MAX-CUT-PRESERVING pair flips (dM<=dB): on those, is E0pair>=0 (gamma-min)?
    presv = [r for r in defr if r['dM_pair'] <= r['dB_pair']]
    pneg = [r for r in presv if r['E0pair'] < 0]
    print("\nmax-cut-preserving pair flips: %d, of which E0pair<0: %d" % (len(presv), len(pneg)))

    # Among NON-preserving (dM>dB) pair flips, E0pair can be <0: is delL2 bounded by -E0pair there?
    nonp = [r for r in defr if r['dM_pair'] > r['dB_pair']]
    print("non-preserving pair flips: %d, E0pair<0 among them: %d" %
          (len(nonp), len([r for r in nonp if r['E0pair']<0])))

    # rank most-negative RAW E0pair
    defr.sort(key=lambda r: float(r['E0pair']))
    print("\nMOST NEGATIVE RAW E0pair:")
    for r in defr[:8]:
        print("  %s L=%d N=%s delL2=%s E0pair=%s gend=%s dM=%s dB=%s (L/5)(N^2-G)=%s" %
              (r['name'][:18], r['L'], r['N'], r['delL2'], r['E0pair'], r['gend'],
               r['dM_pair'], r['dB_pair'], F(r['L'],5)*r['RHSfull']))

if __name__ == "__main__":
    main()
