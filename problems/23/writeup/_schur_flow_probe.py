"""FLOW / TRANSPORTATION probe for the Schur-on-overload reduction of (H) D_{N-T}+Lstar>=0.

Findings to test EXACTLY (Fraction):
 (P1) STRUCTURE-OF-TIGHTNESS: across the battery, is the Schur complement S on O strictly PD
      (min pivot > 0) EXACTLY on the cuts where (H) is non-tight, and is every TIGHT (H) (min pivot 0)
      case one with O EMPTY?  i.e. tightness of (H) lives in the U-block Laplacian kernel, never in S.
 (P2) FLOW FEASIBILITY (the transportation reading).  (H)>=0  <=>  for the harmonic extension, the
      overload supply b_o = T_o - N at each o in O is "absorbable" by the underloaded capacity through the
      cycle conductances.  Concretely we test the natural energy/flow certificate:
         define on U the potential phi = H_UU^{-1} (-H_UO 1_O) ... no; instead use the variational fact
         min_x [ x^T H x : x_O = e_o ] = S[o,o]  (Schur diagonal = effective resistance-like energy).
      The transportation claim is: the overload at o is carried out to deficit with finite energy iff
      S[o,o] >= 0 for all o AND the cross terms are dominated, i.e. S>=0.  We verify S = the EXACT effective
      generalized-Laplacian on O by the variational identity  e_o^T S e_o = min{ x^T H x : x_O=e_o }.
 (P3) Is S an M-matrix (off-diagonal <=0)?  Data shows S has all-nonpositive off-diagonals on the witnesses.
      If S is a symmetric M-matrix with S 1 >= 0 it is automatically PSD (weakly diag dominant).  But row
      sums of S were sometimes NEGATIVE (N=23), so S is NOT diagonally dominant.  Test: off-diag sign of S,
      and whether  S = (genuine conductance Laplacian on O)  +  (diagonal correction).  Decompose
      S = L_S + diag(rho) with L_S the Laplacian of -offdiag(S); report rho and whether rho can be negative
      (if rho>=0 always, S>=0 is immediate; that would be the clean structural theorem).

Run:  python _schur_flow_probe.py
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import Cn, mycielski
from _hardy_gate import BETA, build_H, maxcut_ls
from _schur_overload_gate import ldl_psd, solve_exact, submatrix, matmul, schur_on_O, c5_blowup


def variational_diag(H, n, O, U, o_local):
    """min{ x^T H x : x_O = e_{o_local} } = (Schur S)[o_local,o_local], computed independently by
       solving for the harmonic minimizer on U.  Returns the exact min energy (Fraction) or None."""
    # x_U = -H_UU^{-1} H_{U,O} x_O ; with x_O = e_{o_local}, x_O picks column o_local of H_{U,O}=H_UO.
    if not U:
        return H[O[o_local]][O[o_local]]
    H_UU = submatrix(H, U, U)
    # rhs = -H_{U, o}  (column for the chosen o)
    o = O[o_local]
    rhs = [[-H[u][o] for u in U]]
    sol = solve_exact(H_UU, rhs)
    if sol is None:
        return None
    xU = sol[0]
    # energy = x^T H x with x_O = e_o, x_U = xU
    # = H[o][o] + 2 sum_u H[o][u] xU_u + sum_{u,v} H[u][v] xU_u xU_v
    E = H[o][o]
    for idx, u in enumerate(U):
        E += 2 * H[o][u] * xU[idx]
    for i, u in enumerate(U):
        for j, v in enumerate(U):
            E += H[u][v] * xU[i] * xU[j]
    return E


def analyze_S(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, mu, cyc = st
    if not M:
        return
    N = F(n)
    H = build_H(n, M, ell, T, cyc, BETA)
    r = schur_on_O(H, n, T, N)
    acc['cuts'] += 1
    O = r['O']
    psdH = r['psdH']
    # (P1) tightness location
    Htight = (r['minpivH'] == 0)
    if Htight:
        acc['H_tight'] += 1
        if not O:
            acc['H_tight_Oempty'] += 1
        else:
            acc['H_tight_Ononempty'] += 1
            if acc['Htight_Ononempty_ex'] is None:
                acc['Htight_Ononempty_ex'] = (name, n, ''.join(map(str, side)))
    if not O:
        return
    S = r['S']
    k = len(O)
    # (P2) variational identity: S[i][i] == min energy with x_O = e_i
    for i in range(k):
        ve = variational_diag(H, n, O, r['U'], i)
        if ve is None or ve != S[i][i]:
            acc['var_mismatch'] += 1
            if acc['var_ex'] is None:
                acc['var_ex'] = (name, n, str(ve), str(S[i][i]))
            break
    # Schur strict-PD where O nonempty?
    if r['minpivS'] is not None:
        if r['minpivS'] > 0:
            acc['S_strict_PD'] += 1
        elif r['minpivS'] == 0:
            acc['S_tight'] += 1
            if acc['S_tight_ex'] is None:
                acc['S_tight_ex'] = (name, n, ''.join(map(str, side)))
    # (P3) off-diagonal sign of S; Laplacian + diagonal decomposition
    all_offdiag_nonpos = True
    for i in range(k):
        for j in range(k):
            if i != j and S[i][j] > 0:
                all_offdiag_nonpos = False
    if all_offdiag_nonpos:
        acc['S_Mmatrix'] += 1
    else:
        acc['S_not_Mmatrix'] += 1
        if acc['notM_ex'] is None:
            acc['notM_ex'] = (name, n, ''.join(map(str, side)))
    # decompose S = L_S + diag(rho); L_S = Laplacian of conductances c_ij = -S[i][j] (i!=j)
    # L_S[i][i] = sum_{j!=i} c_ij ; rho_i = S[i][i] - L_S[i][i] = S[i][i] + sum_{j!=i} S[i][j] = rowsum_i
    rho = [sum(S[i]) for i in range(k)]   # = row sums of S
    rho_min = min(rho)
    if rho_min < 0:
        acc['rho_neg'] += 1
        if acc['rho_neg_ex'] is None:
            acc['rho_neg_ex'] = (name, n, ''.join(map(str, side)), [float(x) for x in rho])
    if acc['rho_min'] is None or rho_min < acc['rho_min']:
        acc['rho_min'] = rho_min
        acc['rho_min_ex'] = (name, n)
    # When S is an M-matrix with rho>=0 (rowsums>=0) it's diag-dominant => PSD trivially.
    if all_offdiag_nonpos and rho_min >= 0:
        acc['S_diagdom'] += 1


def gfam(name, n, E, acc):
    adj = [set() for _ in range(n)]
    for x, y in E:
        adj[x].add(y); adj[y].add(x)
    try:
        _, cuts = gmins(n, E)
    except Exception:
        return
    for side in cuts:
        analyze_S(name, n, adj, side, acc)


def main():
    acc = dict(cuts=0, H_tight=0, H_tight_Oempty=0, H_tight_Ononempty=0,
               Htight_Ononempty_ex=None,
               var_mismatch=0, var_ex=None,
               S_strict_PD=0, S_tight=0, S_tight_ex=None,
               S_Mmatrix=0, S_not_Mmatrix=0, notM_ex=None,
               rho_neg=0, rho_neg_ex=None, rho_min=None, rho_min_ex=None,
               S_diagdom=0)

    print("FLOW/TRANSPORTATION probe of Schur-on-overload S")
    # focused witnesses
    n, E = dec('H?AFBo]'); gfam("H?AFBo]_N9", n, E, acc)
    for t in (2, 3, 4):
        n, E = c5_blowup(t)
        if n <= 24:
            gfam("C5[%d]" % t, n, E, acc)
    # full census 5..10
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); gfam("cen%d" % nn, n, E, acc)
        print("  census N=%d done: cuts=%d Ononempty(S)=%d var_mismatch=%d"
              % (nn, acc['cuts'], acc['S_strict_PD'] + acc['S_tight'], acc['var_mismatch']), flush=True)
    # N=23
    grN, grE = mycielski(5, Cn(5))
    m2N, m2E = mycielski(grN, grE)
    adj = [set() for _ in range(m2N)]
    for x, y in m2E:
        adj[x].add(y); adj[y].add(x)
    side = maxcut_ls(m2N, adj)
    analyze_S("MycGrotzsch_N23", m2N, adj, side, acc)

    print("\n" + "=" * 64)
    print("RESULTS (flow probe)")
    print("  cuts tested                       :", acc['cuts'])
    print("  (P1) (H) tight (minpiv 0) cuts    :", acc['H_tight'],
          "| of which O EMPTY:", acc['H_tight_Oempty'],
          "| O NONEMPTY:", acc['H_tight_Ononempty'], acc['Htight_Ononempty_ex'] or '')
    print("  (P2) variational S[i,i] mismatch  :", acc['var_mismatch'], acc['var_ex'] or '')
    print("  Schur S strictly PD (O nonempty)  :", acc['S_strict_PD'])
    print("  Schur S TIGHT (minpiv 0)          :", acc['S_tight'], acc['S_tight_ex'] or '')
    print("  (P3) S is M-matrix (offdiag<=0)   :", acc['S_Mmatrix'],
          "| NOT M-matrix:", acc['S_not_Mmatrix'], acc['notM_ex'] or '')
    print("  S diag-dominant (M & rowsum>=0)   :", acc['S_diagdom'])
    print("  S rowsum(rho) can be NEGATIVE     :", acc['rho_neg'], acc['rho_neg_ex'] or '')
    print("  min S rowsum (rho) over battery   :", float(acc['rho_min']) if acc['rho_min'] is not None else None,
          "at", acc['rho_min_ex'])
    print("\nINTERPRETATION:")
    if acc['H_tight_Ononempty'] == 0:
        print("  * Every TIGHT (H) has O EMPTY: tightness lives in the U-block Laplacian kernel, never in S.")
        print("    => On O-nonempty cuts, S is STRICTLY PD with a uniform gap; the overload Schur complement")
        print("       is never the binding constraint.  The hard (equality) case is the all-underloaded C5[t].")
    if acc['var_mismatch'] == 0:
        print("  * S[o,o] = min{x^T H x : x_O=e_o} EXACTLY: Schur diagonal = effective energy to inject one")
        print("    unit of overload at o and let it relax through the cycle network (transportation energy).")
    if acc['S_not_Mmatrix'] == 0 and acc['rho_neg'] > 0:
        print("  * S is always an M-matrix (offdiag<=0) but NOT diagonally dominant (rho<0 possible).")
        print("    => S>=0 is NOT a free Laplacian fact; it needs the cycle conductance to beat the deficit.")
    elif acc['S_not_Mmatrix'] == 0 and acc['rho_neg'] == 0:
        print("  * S is an M-matrix with NONNEGATIVE row sums on the WHOLE battery => S>=0 is automatic")
        print("    (weakly diagonally dominant symmetric M-matrix). THIS WOULD BE A CLEAN STRUCTURAL PROOF on O.")


if __name__ == "__main__":
    main()
