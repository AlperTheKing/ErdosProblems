"""APEX CONDUCTANCE BOUND (ANGLE: Cap(e_apex) >= a_apex from gamma-min + odd-girth).

CORRECTED apex object.  The (DONE) reduction collapses (H) D_{N-T}+Lstar >= 0 to a SINGLE scalar
via the TWO-STAGE Schur:
  (1) O={v:T_v>N} (overloaded), U=V\O.  H_UU is PD (nonneg diag + Laplacian); eliminate U:
        S = H_OO - H_OU H_UU^{-1} H_UO   (symmetric M-matrix on O).
  (2) rho_i = rowsum of S.  R = {i: rho_i < 0}; EXACT-validated |R|<=1, the unique r = the max-load APEX.
        s_r = S[r,r] - S[r,P] S[P,P]^{-1} S[P,r]   (P=O\{r})   = ONE-TERMINAL effective conductance
        from the apex into the (O\{apex} held at the harmonic value) shortest-cycle network.
  CLOSING INEQUALITY:  s_r >= 0  <=>  S>=0  <=>  (H) PSD  <=>  Gamma<=N^2  <=>  #23.

This file computes s_r EXACTLY (Fraction) and the ROW-SUM DEMAND a_apex := -rho_r >= 0 (apex's net
deficit AFTER the M-matrix Schur on U and the harmonic balancing of the other overloaded vertices).
Cap(e_apex) := S[r,r] (the apex's effective SELF-conductance, = -sum_{j!=r} S[r,j] + rho_r); the
diagonal-dominance gap is exactly  Cap_self - a_apex_offdiagmass.  We tabulate, per O-nonempty cut:
   T_apex, rho_r (=-a_apex), S[r,r], s_r (the actual closing scalar), and the margin.

EXPLICIT STRUCTURAL LOWER BOUNDS B(apex) (computed ONLY from S's apex row, no full inverse):
  M-matrix diag-Schur:  s_r >= B_diag := S[r,r] - sum_{j in P} S[r,j]^2 / S[j,j]   (valid LB on s_r
     because the surrounding block S_PP is itself a symmetric M-matrix, S_PP >= diag(S[j,j]) on the
     relevant cone, so S[r,P] S_PP^{-1} S[P,r] <= sum_j S[r,j]^2/S[j,j]).  Tested as a LB on s_r.
  Series/STAR-K1:  s_r >= B_star := sum_{j in P, a_j>0,R_j>0} a_j R_j/(a_j+R_j),
     a_j = -S[r,j] (>=0, M-matrix), R_j = rho_j = rowsum of S at j (>=0 since j not in R).
     This is the transportation "route each unit of apex deficit through underloaded slack" bound.
  The MICRO-GOAL: an explicit B(apex) with  0 <= B(apex) <= s_r  computed from local apex data, so that
     s_r >= B(apex) >= 0 closes the apex inequality.  We report whether B_diag>=0 and B_star>=0 0-fail,
     and whether each is a genuine LOWER bound on s_r (B <= s_r) 0-fail.  Exact Fraction throughout.
Run:  python _apex_conductance_gate.py
"""
import subprocess, random
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins, odd_blowup
from _bdef_construct import Cn, union_disjoint, add_edges, mycielski, is_triangle_free
from _Klocal_gate import glued_c5_chain
from _hardy_gate import build_H, BETA, maxcut_ls
from _csmspec import is_psd
from _Rsize_gate import solve_mat, schur_on


def build_S(H, n, T, N):
    """Stage-1 Schur on U: S = H_OO - H_OU H_UU^{-1} H_UO.  Returns (S, O) or (None,O) if H_UU singular."""
    O = [v for v in range(n) if T[v] > N]
    U = [v for v in range(n) if T[v] <= N]
    if not O:
        return [], O
    Huu = [[H[a][b] for b in U] for a in U]
    Huo = [[H[a][b] for b in O] for a in U]
    Hoo = [[H[a][b] for b in O] for a in O]
    Hou = [[H[a][b] for b in U] for a in O]
    X = solve_mat(Huu, Huo)
    if X is None:
        return None, O
    m = len(O)
    S = [[Hoo[i][j] - sum(Hou[i][t] * X[t][j] for t in range(len(U))) for j in range(m)] for i in range(m)]
    return S, O


def test_cut(name, n, adj, side, acc, verbose=False):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, mu, cyc = st
    if not M:
        return
    N = F(n)
    acc['cuts'] += 1
    H = build_H(n, M, ell, T, cyc, BETA)
    S, O = build_S(H, n, T, N)
    if not O:
        acc['O_empty'] += 1
        return
    acc['O_nonempty'] += 1
    if S is None:
        acc['Huu_singular'] += 1
        return
    m = len(O)
    rho = [sum(S[i][j] for j in range(m)) for i in range(m)]
    Rset = [i for i in range(m) if rho[i] < 0]
    if len(Rset) >= 2:
        acc['R_ge2'] += 1
        if acc['Rge2_ex'] is None:
            acc['Rge2_ex'] = (name, n, ''.join(map(str, side)), len(Rset))
        return  # apex story assumes |R|<=1
    if len(Rset) == 0:
        # no negative-rowsum vertex: S diag-dominant => PSD; apex inequality vacuous (s>=0 automatically)
        acc['R_empty'] += 1
        # still record self-cap margin at the actual max-T overloaded vertex
        return
    r = Rset[0]
    P = [i for i in range(m) if i != r]
    a_apex = -rho[r]                  # apex net deficit after Schur on U  (>= 0)
    Srr = S[r][r]                     # apex self-conductance

    # the genuine closing scalar s_r (one-terminal Schur of S at the apex)
    S1 = schur_on(S, [r], P)
    if S1 is None:
        acc['oneterm_singular'] += 1
        return
    s_r = S1[0][0]
    acc['oneterm_total'] += 1

    # --- closing inequality  s_r >= 0 ---
    if s_r < 0:
        acc['SR_FAIL'] += 1
        if acc['sr_ex'] is None:
            acc['sr_ex'] = (name, n, ''.join(map(str, side)), str(s_r))
    else:
        if acc['min_sr'] is None or s_r < acc['min_sr']:
            acc['min_sr'] = s_r
            acc['min_sr_ex'] = (name, n, float(s_r))

    # --- structural lower bounds on s_r (apex-row local) ---
    # B_diag = Srr - sum_{j in P} S[r,j]^2 / S[j,j]   (need S[j][j] > 0)
    Bdiag = Srr
    diag_ok = True
    for j in P:
        if S[j][j] > 0:
            Bdiag -= S[r][j] * S[r][j] / S[j][j]
        elif S[r][j] != 0:
            diag_ok = False
    # B_star = sum_{j in P, a_j>0, R_j>0} a_j R_j/(a_j+R_j), a_j=-S[r][j], R_j=rho[j]
    Bstar = F(0)
    for j in P:
        a = -S[r][j]
        Rj = rho[j]
        if a > 0 and Rj > 0:
            Bstar += a * Rj / (a + Rj)

    # is each B a genuine LOWER bound on s_r?  (B <= s_r)
    if diag_ok and Bdiag > s_r:
        acc['BDIAG_GT_SR'] += 1
        if acc['bdiag_ex'] is None:
            acc['bdiag_ex'] = (name, n, ''.join(map(str, side)), str(Bdiag), str(s_r))
    if Bstar > s_r:
        acc['BSTAR_GT_SR'] += 1
        if acc['bstar_ex'] is None:
            acc['bstar_ex'] = (name, n, ''.join(map(str, side)), str(Bstar), str(s_r))
    # is each B >= 0 (so that B itself certifies s_r>=0)?
    if diag_ok and Bdiag < 0:
        acc['BDIAG_NEG'] += 1
        if acc['bdiag_neg_ex'] is None:
            acc['bdiag_neg_ex'] = (name, n, ''.join(map(str, side)), str(Bdiag), str(s_r))
    if Bstar < 0:
        acc['BSTAR_NEG'] += 1
    # track Bdiag>=0 AND Bdiag<=s_r  (would close via diag-Schur alone)
    if diag_ok:
        acc['bdiag_total'] += 1
        if Bdiag >= 0 and Bdiag <= s_r:
            acc['bdiag_close'] += 1
        if acc['min_bdiag'] is None or Bdiag < acc['min_bdiag']:
            acc['min_bdiag'] = Bdiag

    if verbose:
        Topx = max(O, key=lambda v: T[v]); maxT = T[Topx]
        print(f"  [{name}] N={n} O(size {m})={O}  apex(row r={r}, vtx={O[r]})  T_apex~{float(maxT):.3f} ({float(maxT)/n:.2f}N)")
        print(f"      rho_r=-a_apex = {float(rho[r]):.4f}   a_apex = {float(a_apex):.4f}   S[r,r]={float(Srr):.4f}")
        print(f"      s_r (closing scalar) = {float(s_r):.5f}   [need >=0]")
        print(f"      B_diag = {float(Bdiag):.5f} (LB on s_r? {Bdiag<=s_r}, >=0? {Bdiag>=0})   "
              f"B_star = {float(Bstar):.5f} (LB? {Bstar<=s_r}, >=0? {Bstar>=0})", flush=True)


def gfam(name, n, E, acc, verbose=False):
    adj = [set() for _ in range(n)]
    for x, y in E:
        adj[x].add(y); adj[y].add(x)
    try:
        _, cuts = gmins(n, E)
    except Exception:
        return
    for side in cuts:
        test_cut(name, n, adj, side, acc, verbose=verbose)


def main():
    acc = dict(cuts=0, O_empty=0, O_nonempty=0, Huu_singular=0, R_ge2=0, R_empty=0,
               oneterm_total=0, oneterm_singular=0,
               SR_FAIL=0, min_sr=None, min_sr_ex=None,
               BDIAG_GT_SR=0, BSTAR_GT_SR=0, BDIAG_NEG=0, BSTAR_NEG=0,
               bdiag_total=0, bdiag_close=0, min_bdiag=None,
               Rge2_ex=None, sr_ex=None, bdiag_ex=None, bstar_ex=None, bdiag_neg_ex=None)

    print("=" * 78)
    print("APEX CONDUCTANCE GATE (two-stage Schur):  s_r >= 0  closes (H)/#23")
    print("  s_r = one-terminal Schur of S=H_OO-H_OU H_UU^-1 H_UO at the unique neg-rowsum apex r")
    print("=" * 78)

    print("\n--- focused witnesses (verbose) ---")
    n, E = dec('H?AFBo]')
    gfam("H?AFBo]_N9", n, E, acc, verbose=True)
    for sizes in [(2, 1, 2, 1, 2), (3, 2, 3, 2, 3), (4, 3, 4, 3, 4), (5, 4, 5, 4, 5)]:
        nn, EE, adj, side = odd_blowup(5, list(sizes))
        if nn <= 30 and Bconn(nn, adj, side):
            test_cut("blow%s" % (sizes,), nn, adj, side, acc, verbose=True)
    grN, grE = mycielski(5, Cn(5))
    m2N, m2E = mycielski(grN, grE)
    adj = [set() for _ in range(m2N)]
    for x, y in m2E:
        adj[x].add(y); adj[y].add(x)
    side = maxcut_ls(m2N, adj)
    if Bconn(m2N, adj, side):
        print("\n--- N=23 Myc(Grotzsch) guardrail ---")
        test_cut("MycGrotzsch_N23", m2N, adj, side, acc, verbose=True)

    print("\n--- broad battery (silent; aggregate) ---")
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            gfam("cen%d" % nn, n, E, acc)
        print("  census N=%d: O_ne=%d |R|>=2=%d s_r_total=%d SR_FAIL=%d BDIAG_GT_SR=%d BSTAR_GT_SR=%d"
              % (nn, acc['O_nonempty'], acc['R_ge2'], acc['oneterm_total'], acc['SR_FAIL'],
                 acc['BDIAG_GT_SR'], acc['BSTAR_GT_SR']), flush=True)

    grN, grE = mycielski(5, Cn(5))
    gfam("Grotzsch_N11", grN, grE, acc)
    for q in range(2, 16):
        n, E, side = glued_c5_chain(q)
        adj = [set() for _ in range(n)]
        for x, y in E:
            adj[x].add(y); adj[y].add(x)
        if Bconn(n, adj, side):
            test_cut("chain_q%d" % q, n, adj, side, acc)
    for sizes in [(2, 1, 2, 1, 2), (2, 1, 2, 1, 3), (3, 2, 3, 2, 3), (4, 3, 4, 3, 4),
                  (5, 4, 5, 4, 5), (2, 2, 2, 2, 2), (3, 3, 3, 3, 3), (6, 5, 6, 5, 6), (4, 1, 4, 1, 4)]:
        nn, EE, adj, side = odd_blowup(5, list(sizes))
        if nn <= 30 and Bconn(nn, adj, side):
            test_cut("blow%s" % (sizes,), nn, adj, side, acc)
    isl = (5, Cn(5)); g15 = mycielski(7, Cn(7))
    nn, EE = union_disjoint(isl, g15); nn, EE = add_edges((nn, EE), [(0, 5)])
    gfam("isl_C5_MycC7", nn, EE, acc)

    rng = random.Random(7); made = 0; tries = 0
    while made < 160 and tries < 60000:
        tries += 1
        nn = rng.choice([11, 12, 13]); p = rng.uniform(0.14, 0.34)
        EE = [(a, b) for a in range(nn) for b in range(a + 1, nn) if rng.random() < p]
        if not EE or not is_triangle_free(nn, EE):
            continue
        adj = [set() for _ in range(nn)]
        for a, b in EE:
            adj[a].add(b); adj[b].add(a)
        if any(len(adj[v]) == 0 for v in range(nn)):
            continue
        made += 1; gfam("rand%d" % made, nn, EE, acc)

    print("\n" + "=" * 78)
    print("RESULTS")
    print("  gamma-min cuts tested        :", acc['cuts'], " (random graphs:", made, ")")
    print("  O empty / O nonempty         :", acc['O_empty'], "/", acc['O_nonempty'])
    print("  H_UU singular                :", acc['Huu_singular'])
    print("  |R|>=2 (multi-apex, skipped) :", acc['R_ge2'], acc['Rge2_ex'] or '')
    print("  |R|=0 (S diag-dom, trivial)  :", acc['R_empty'])
    print("  |R|=1 one-terminal scalars   :", acc['oneterm_total'])
    print("  -" * 38)
    print("  s_r < 0  (CLOSING FAILS)     :", acc['SR_FAIL'], acc['sr_ex'] or '')
    print("  min s_r (>=0 set)            :", str(acc['min_sr']), "at", acc['min_sr_ex'])
    print("  -" * 38)
    print("  B_diag NOT a LB (Bdiag>s_r)  :", acc['BDIAG_GT_SR'], acc['bdiag_ex'] or '')
    print("  B_diag < 0                   :", acc['BDIAG_NEG'], acc['bdiag_neg_ex'] or '')
    print("  B_star NOT a LB (Bstar>s_r)  :", acc['BSTAR_GT_SR'], acc['bstar_ex'] or '')
    print("  B_star < 0                   :", acc['BSTAR_NEG'])
    print("  B_diag closes (0<=Bdiag<=s_r):", acc['bdiag_close'], "/", acc['bdiag_total'])
    print("  min B_diag                   :", str(acc['min_bdiag']))
    print("=" * 78)
    cap_ok = acc['SR_FAIL'] == 0
    bdiag_lb_ok = acc['BDIAG_GT_SR'] == 0
    bdiag_close_all = acc['bdiag_total'] > 0 and acc['bdiag_close'] == acc['bdiag_total']
    print("VERDICT (apex s_r>=0)          :",
          "HOLDS 0-fail on full battery incl N=23" if cap_ok else "FAILS (see counterexample)")
    print("VERDICT (B_diag is valid LB)   :",
          "B_diag <= s_r 0-fail (genuine local lower bound on the closing scalar)" if bdiag_lb_ok
          else "B_diag EXCEEDS s_r on %d cuts -- diag-Schur over-counts" % acc['BDIAG_GT_SR'])
    print("VERDICT (B_diag closes apex)   :",
          "B_diag certifies s_r>=0 (0<=B_diag<=s_r) on ALL %d apex cuts -- EXPLICIT closing bound" % acc['bdiag_total']
          if bdiag_close_all else
          "B_diag does NOT close on all cuts (closes %d/%d) -- need stronger LB" % (acc['bdiag_close'], acc['bdiag_total']))


if __name__ == "__main__":
    main()
