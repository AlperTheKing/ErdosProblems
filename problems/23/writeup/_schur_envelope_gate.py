"""SCHUR/MAJORIZATION envelope gate for crux (A).
Claim chain to TEST exactly (rational):
  Row functional:  Phi = E_0 + delta*L^2,   need Phi <= (L/5)(N^2 - Gamma).        [the crux (A)]
  Schur envelope:  delta = mean^2 - q,  mean=S/L, q=min_i h_i h_{i+1} (cyclic), m=min_i h_i.
                   Since q = h_r h_{r+1} >= m^2,  delta <= mean^2 - m^2   (EXACT, Schur-convex envelope E1).
  Hence            delta*L^2 <= S^2 - L^2 m^2.
  STRENGTHENED (decoupled-via-envelope) inequality to test:
        (SE)   E_0 + S^2 - L^2 m^2  <=  (L/5)(N^2 - Gamma).
  If (SE) holds with ZERO violations on the battery, it PROVES (A) (since delta*L^2 <= S^2 - L^2 m^2).
  CRITICAL self-test: does (SE) avoid the decoupling failure?  We also log, per row, whether the
  envelope slack  env_gap := (S^2 - L^2 m^2) - delta*L^2 (>=0) and whether E_0<0 still needed.
Reuses chi_profile (renormalized E_0) and struct_for_side from existing harness.
"""
import subprocess
from fractions import Fraction as F
from _trunc_verify import chi_profile as endpt_chi
from _wf_deficit_farkas import odd_blowup
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins

def rows_for(name, n, adj, side, acc):
    if not Bconn(n, adj, side): return
    st = struct_for_side(n, adj, side)
    if st is None: return
    M, ell, T, cyc = st[0], st[1], st[2], st[4]
    if not M: return
    N = F(n); Gamma = sum(ell[g]**2 for g in M)
    RHSbase = (N*N - Gamma)
    for f in M:
        L = ell[f]
        if L % 2 == 0 or L < 5: continue
        for P in cyc[f]:
            if len(P) != L: continue
            h = [T[P[i]]/N for i in range(L)]; S = sum(h)
            q = min(h[i]*h[(i+1) % L] for i in range(L))
            mean = S/F(L); m = min(h)
            delta = mean*mean - q
            # renormalized E_0 (sum over both endpoints)
            chiP = [0]*n
            ok = True
            for end in (P[0], P[-1]):
                ch = endpt_chi(n, adj, side, end, M, n)
                for r in range(n): chiP[r] += ch[r]
            E0 = sum((2*r+1)*chiP[r] for r in range(n))
            Phi = E0 + delta*L*L
            RHS = F(L, 5)*RHSbase
            envLHS = E0 + S*S - F(L*L)*m*m
            acc['rows'] += 1
            # E1 envelope sanity (delta <= mean^2-m^2)
            if delta > mean*mean - m*m + F(0):
                acc['e1_fail'] += 1
            # original (A)
            if Phi > RHS:
                acc['A_fail'] += 1
                if acc['A_ex'] is None: acc['A_ex'] = (name, str(Phi), str(RHS))
            # strengthened (SE)
            if envLHS > RHS:
                acc['SE_fail'] += 1
                slack = RHS - envLHS
                if acc['SE_worst'] is None or slack < acc['SE_worst'][0]:
                    acc['SE_worst'] = (slack, name, L, n, str(envLHS), str(RHS))
                # is every SE-failing row an E0<0 row?
                if E0 >= 0: acc['SE_fail_with_E0nonneg'] += 1
            else:
                slack = RHS - envLHS
                if acc['SE_minslack'] is None or slack < acc['SE_minslack'][0]:
                    acc['SE_minslack'] = (slack, name, L, n)
            # CONDITIONAL claim (CE): on rows with E0>=0, does SE hold?
            if E0 >= 0:
                acc['E0nonneg_rows'] += 1
                if envLHS > RHS: acc['CE_fail'] += 1

def main():
    acc = dict(rows=0, e1_fail=0, A_fail=0, A_ex=None, SE_fail=0, SE_worst=None, SE_minslack=None,
               SE_fail_with_E0nonneg=0, E0nonneg_rows=0, CE_fail=0)
    # census triangle-free N<=9
    for nn in range(5, 10):
        out = subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split()
        for g6 in out:
            n, E = dec(g6); adj = [set() for _ in range(n)]
            for x, y in E: adj[x].add(y); adj[y].add(x)
            try: _, cuts = gmins(n, E)
            except Exception: continue
            for side in cuts: rows_for("cen%d" % nn, n, adj, side, acc)
    # C5[t] blow-ups (tight case)
    for sizes in [(2,2,2,2,2),(3,3,3,3,3),(2,1,2,1,2),(3,2,3,2,3)]:
        n, E = odd_blowup(5, list(sizes)); adj = [set() for _ in range(n)]
        for x, y in E: adj[x].add(y); adj[y].add(x)
        try: _, cuts = gmins(n, E)
        except Exception: continue
        for side in cuts: rows_for("C5%s" % str(sizes), n, adj, side, acc)
    print("rows=%d" % acc['rows'])
    print("E1 envelope (delta<=mean^2-m^2) failures:", acc['e1_fail'])
    print("(A) original  E_0+delta L^2 <= (L/5)(N^2-Gamma)  failures:", acc['A_fail'], acc['A_ex'] or '')
    print("(SE) STRENGTHENED E_0+S^2-L^2 m^2 <= (L/5)(N^2-Gamma)  failures:", acc['SE_fail'])
    if acc['SE_worst']: print("   (SE) WORST (negative slack):", acc['SE_worst'])
    if acc['SE_minslack']: print("   (SE) min nonneg slack:", acc['SE_minslack'])
    print("   SE failures that have E0>=0:", acc['SE_fail_with_E0nonneg'], "(if 0, ALL SE-failures are E0<0 rows)")
    print("(CE) CONDITIONAL: on E0>=0 rows (count=%d), SE failures:" % acc['E0nonneg_rows'], acc['CE_fail'])
    print(">>> SE PROVES (A) on battery" if acc['SE_fail'] == 0 and acc['e1_fail'] == 0 else ">>> SE INSUFFICIENT (decoupling-via-envelope fails)")
    print(">>> CE (E0>=0 => SE) HOLDS" if acc['CE_fail'] == 0 else ">>> CE FAILS")

if __name__ == "__main__":
    main()
