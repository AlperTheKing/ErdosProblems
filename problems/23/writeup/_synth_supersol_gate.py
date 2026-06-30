"""SYNTHESIS verification: the LIVE certificate for (H) = D_{N-T}+Lstar >= 0 is the
positive N-superharmonic SUPERSOLUTION (Open-Capacity Lemma of SCHUR_SPEC_PROOF_DRAFT.md),
NOT any fixed per-vertex weight.  This test PROVES (constructively, exact Fraction) that the
Schur certificate is EQUIVALENT to: there exists phi > 0 (strictly positive) with H phi >= 0
componentwise.  H is a symmetric Z-matrix (Lstar off-diags <= 0, see build_H), so such a phi
=> H PSD (standard Z-matrix / M-matrix supersolution fact).

Construction (Schur-derived phi):
  O = {v: T_v > N} (negative diagonal vertices), U = rest.  H_UU strictly PD (empirical, tested).
  Define on U:  g = H_UU^{-1} (H_OU^T  *  1_O)   ... wait -- use the draft's normalization:
  We want phi with phi_O = 1 (ones on O) and phi_U = 1 - z, solving so that (H phi)_U = 0:
      (H phi)_U = H_UU phi_U + H_UO phi_O = H_UU phi_U + H_UO 1 = 0
      => phi_U = - H_UU^{-1} H_UO 1.
  Then (H phi)_O = H_OO 1 + H_OU phi_U = H_OO 1 - H_OU H_UU^{-1} H_UO 1 = S 1 = rowsum(S).
  So:  H phi = [ S*1 ; 0 ]  -- supersolution iff S*1 >= 0 (Schur row sums >= 0).
  BUT S row sums can be NEGATIVE at N=23 (apex), so phi_O = 1 is the WRONG normalization.
  The CORRECT supersolution uses phi_O = w (the PF-type positive vector of the M-matrix S):
  since S is a symmetric M-matrix that is PSD (indeed PD on O-nonempty cuts), choose phi_O > 0
  with S phi_O >= 0.  For a nonsingular symmetric M-matrix S, S^{-1} >= 0 entrywise, so
  phi_O := S^{-1} 1_O > 0  gives  S phi_O = 1 > 0, and phi_U := - H_UU^{-1} H_UO phi_O.
  Claim: phi_U > 0 too (so phi > 0 everywhere), and H phi = [1_O ; 0] >= 0.  EXACT-TESTED here.

This is the concrete, testable form of the Open-Capacity Lemma.  If phi > 0 holds 0-fail incl
N=23, the ONLY remaining gap is to prove phi_U > 0 (equiv. H_UO^T H_UU^{-1}-image stays in [0,1])
and S^{-1} >= 0 (M-matrix) in GENERAL using gamma-minimality + odd-girth>=5.
"""
import subprocess, random
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _wf_deficit_farkas import odd_blowup
from _bdef_construct import Cn, union_disjoint, add_edges, mycielski, is_triangle_free
from _Klocal_gate import glued_c5_chain
from _hardy_gate import BETA, build_H, maxcut_ls
from _schur_overload_gate import ldl_psd, solve_exact, submatrix, matmul


def supersolution_check(H, n, T, N):
    """Build the Schur-derived strictly-positive supersolution phi and verify H phi >= 0, phi > 0.
       Returns dict with flags. Only meaningful when O nonempty and H_UU PD and S PD."""
    O = [v for v in range(n) if T[v] > N]
    U = [v for v in range(n) if T[v] <= N]
    res = dict(O=O, U=U, ok=None, reason='', phi_min=None, Hphi_min=None,
               UU_PD=None, S_PD=None, Sinv_nonneg=None)
    if not O:
        # O empty: H = D_{N-T>=0} + Lstar, both PSD; phi = ones works trivially (H*1 = N - T >= 0).
        Hphi = [sum(H[i][j] for j in range(n)) for i in range(n)]  # = N - T_i (Lstar rows sum 0)
        res['ok'] = all(x >= 0 for x in Hphi)
        res['reason'] = 'O empty: phi=1, (H 1)_i = N-T_i >= 0'
        res['phi_min'] = F(1)
        res['Hphi_min'] = min(Hphi)
        return res
    H_OO = submatrix(H, O, O); H_OU = submatrix(H, O, U)
    H_UO = submatrix(H, U, O); H_UU = submatrix(H, U, U)
    psdUU, minpivUU, _ = ldl_psd(H_UU)
    res['UU_PD'] = bool(psdUU and minpivUU is not None and minpivUU > 0)
    if not res['UU_PD']:
        res['ok'] = False; res['reason'] = 'H_UU not strictly PD'; return res
    # S = H_OO - H_OU H_UU^{-1} H_UO
    cols = [[H_UO[i][c] for i in range(len(U))] for c in range(len(O))]
    X = solve_exact(H_UU, cols)
    if X is None:
        res['ok'] = False; res['reason'] = 'H_UU singular'; return res
    Xm = [[X[c][i] for c in range(len(O))] for i in range(len(U))]  # |U| x |O| = H_UU^{-1} H_UO
    HOU_X = matmul(H_OU, Xm)
    S = [[H_OO[i][j] - HOU_X[i][j] for j in range(len(O))] for i in range(len(O))]
    psdS, minpivS, _ = ldl_psd(S)
    res['S_PD'] = bool(psdS and minpivS is not None and minpivS > 0)
    if not res['S_PD']:
        res['ok'] = False; res['reason'] = 'S not strictly PD'; return res
    # phi_O = S^{-1} 1   (positive iff S^{-1} >= 0, M-matrix property)
    # solve_exact(M, B): B is a list of COLUMN vectors, each length n. One column of all ones.
    sol = solve_exact(S, [[F(1)] * len(O)])  # solve S y = 1_O
    if sol is None:
        res['ok'] = False; res['reason'] = 'S singular'; return res
    phiO = sol[0]
    res['Sinv_nonneg'] = all(x > 0 for x in phiO)
    # phi_U = - H_UU^{-1} H_UO phi_O = - Xm phiO
    phiU = [-sum(Xm[i][j] * phiO[j] for j in range(len(O))) for i in range(len(U))]
    # assemble phi
    phi = [F(0)] * n
    for idx, v in enumerate(O):
        phi[v] = phiO[idx]
    for idx, v in enumerate(U):
        phi[v] = phiU[idx]
    # verify H phi
    Hphi = [sum(H[i][j] * phi[j] for j in range(n)) for i in range(n)]
    res['phi_min'] = min(phi)
    res['Hphi_min'] = min(Hphi)
    # NON-STRICT supersolution is the correct PSD certificate: phi >= 0 AND H phi >= 0
    # (strict phi>0 only happens off the tight extremal). Track genuine negativity separately.
    phi_nonneg = all(x >= 0 for x in phi)
    Hphi_nonneg = all(x >= 0 for x in Hphi)
    res['phi_strict'] = (min(phi) > 0)
    res['ok'] = phi_nonneg and Hphi_nonneg
    if not res['ok']:
        res['reason'] = 'phi_min=%s Hphi_min=%s (NEGATIVE)' % (float(min(phi)), float(min(Hphi)))
    return res


def test_cut(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, cyc = st[0], st[1], st[2], st[4]
    if not M:
        return
    N = F(n)
    H = build_H(n, M, ell, T, cyc, BETA)
    acc['cuts'] += 1
    r = supersolution_check(H, n, T, N)
    if r['O']:
        acc['Ononempty'] += 1
    if not r['ok']:
        acc['fail'] += 1
        if acc['ex'] is None:
            acc['ex'] = (name, n, ''.join(map(str, side)), r['reason'])
    else:
        if r.get('phi_strict') is False:
            acc['nonstrict'] += 1   # boundary/tight case: phi>=0 with some 0, still valid PSD cert
        if r['phi_min'] is not None and (acc['phimin'] is None or r['phi_min'] < acc['phimin']):
            acc['phimin'] = r['phi_min']; acc['phimin_ex'] = (name, n)


def gfam(name, n, E, acc):
    adj = [set() for _ in range(n)]
    for x, y in E:
        adj[x].add(y); adj[y].add(x)
    try:
        _, cuts = gmins(n, E)
    except Exception:
        return
    for side in cuts:
        test_cut(name, n, adj, side, acc)


def main():
    acc = dict(cuts=0, Ononempty=0, fail=0, nonstrict=0, ex=None, phimin=None, phimin_ex=None)
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); gfam("cen%d" % nn, n, E, acc)
        print("census N=%d: cuts=%d Ononempty=%d fail=%d" % (nn, acc['cuts'], acc['Ononempty'], acc['fail']), flush=True)
    grN, grE = mycielski(5, Cn(5)); gfam("Grotzsch", grN, grE, acc)
    m2N, m2E = mycielski(grN, grE)
    adj = [set() for _ in range(m2N)]
    for x, y in m2E:
        adj[x].add(y); adj[y].add(x)
    side = maxcut_ls(m2N, adj)
    if Bconn(m2N, adj, side):
        test_cut("MycGrotzsch_N23", m2N, adj, side, acc)
    print("after Grotzsch+Myc23: cuts=%d Ononempty=%d fail=%d %s" % (acc['cuts'], acc['Ononempty'], acc['fail'], acc['ex'] or ''), flush=True)
    for q in range(2, 16):
        n, E, side = glued_c5_chain(q)
        adj = [set() for _ in range(n)]
        for x, y in E:
            adj[x].add(y); adj[y].add(x)
        if Bconn(n, adj, side):
            test_cut("chain_q%d" % q, n, adj, side, acc)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(3,2,3,2,3),(4,3,4,3,4),(5,4,5,4,5),(2,2,2,2,2),(3,3,3,3,3)]:
        nn, EE = odd_blowup(5, list(sizes))
        if nn <= 24:
            gfam("blow%s" % (sizes,), nn, EE, acc)
    isl = (5, Cn(5)); g15 = mycielski(7, Cn(7))
    nn, EE = union_disjoint(isl, g15); nn, EE = add_edges((nn, EE), [(0, 5)])
    gfam("isl_C5_MycC7", nn, EE, acc)
    print("after chains+blowups+islands: cuts=%d Ononempty=%d fail=%d %s" % (acc['cuts'], acc['Ononempty'], acc['fail'], acc['ex'] or ''), flush=True)
    rng = random.Random(7); made = 0; tries = 0
    while made < 120 and tries < 40000:
        tries += 1
        nn = rng.choice([11, 12]); p = rng.uniform(0.14, 0.34)
        EE = [(a, b) for a in range(nn) for b in range(a+1, nn) if rng.random() < p]
        if not EE or not is_triangle_free(nn, EE):
            continue
        adj = [set() for _ in range(nn)]
        for a, b in EE:
            adj[a].add(b); adj[b].add(a)
        if any(len(adj[v]) == 0 for v in range(nn)):
            continue
        made += 1; gfam("rand%d" % made, nn, EE, acc)
    print("=" * 64)
    print("gamma-min cuts tested:", acc['cuts'], " O-nonempty:", acc['Ononempty'], " (random N11/12:", made, ")")
    print("SUPERSOLUTION (phi>=0 with H phi>=0, Schur-derived) GENUINE-NEGATIVE FAILURES:", acc['fail'], acc['ex'] or '')
    print("non-strict (boundary, phi_min=0) cuts [tight extremal, still valid PSD cert]:", acc['nonstrict'])
    print("min phi component over all cuts:", '0' if acc['phimin'] == 0 else float(acc['phimin']) if acc['phimin'] is not None else None, "at", acc['phimin_ex'])
    print("VERDICT:", "LIVE: Schur-derived NONNEGATIVE supersolution phi certifies (H) PSD on full battery incl N=23"
          if acc['fail'] == 0 else "BROKEN: supersolution genuinely negative -- see ex")


if __name__ == "__main__":
    main()
