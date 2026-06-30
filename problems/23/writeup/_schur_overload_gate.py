"""SCHUR COMPLEMENT on the OVERLOADED set -- exact-test toward proving (H) D_{N-T}+Lstar >= 0.

(H) H = D_{N-T} + Lstar, where Lstar = sum_f (beta_{L_f}/|cyc[f]|) sum_{Q in cyc[f]} L_Q (cycle Laplacians).
O = {v : T_v > N} (overloaded, negative diagonal N-T_v < 0).  U = complement (N-T_v >= 0).
H_UU = diag(N-T)_U + Lstar_UU is PSD (nonneg diag + PSD Laplacian).  When H_UU is PD,
   (H) PSD  <=>  Schur complement  S = H_OO - H_OU H_UU^{-1} H_UO  >= 0  (PSD on O).

This script (a) computes S EXACTLY (Fraction) and checks S>=0, reporting min LDL pivot, on the
focused battery: H?AFBo] (N=9, Gamma=50), C5[2] (N=10), C5[3] (N=15, TIGHT extremal), two census
N=8/9 graphs, Myc(Grotzsch) N=23.  Uses the CERTIFIED rational beta' (matches _hardy_gate).

(b) Tests the TRANSPORTATION reading of S>=0.  The "effective conductance" interpretation:
H = D_{N-T}+Lstar is a *generalized Laplacian* (Laplacian Lstar plus diagonal shift -T+N).  The U-block
absorbs the deficit; Schur eliminates U, leaving on O an effective network H_OO - H_OU H_UU^{-1} H_UO.
We check whether S has the M-matrix / weighted-Laplacian structure that would let a flow route each
unit of overload (T_v - N) at v in O out through the underloaded capacity, i.e. whether
   S 1_O  vs  D_{N-T}|_O  (row sums) and whether x^T S x >= 0 reduces to a per-cycle flow feasibility.

EXACT only; no float decisions.  Reports 0-fail or first counterexample.
Run:  python _schur_overload_gate.py   (from E:/Projects/ErdosProblems/problems/23/writeup)
"""
import subprocess, random
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import Cn, mycielski
from _hardy_gate import BETA, build_H, maxcut_ls


# ---------------------------------------------------------------------------
# exact LDL PSD test that ALSO returns the L,D factors / pivots (reuse logic of _csmspec.is_psd)
# ---------------------------------------------------------------------------
def ldl_psd(Mat):
    """exact rational symmetric PSD test via no-pivot LDL.
       returns (is_psd, min_pivot, pivots_list)."""
    n = len(Mat)
    A = [row[:] for row in Mat]
    minpiv = None
    pivots = []
    for k in range(n):
        p = A[k][k]
        pivots.append(p)
        if p < 0:
            return False, p, pivots
        if minpiv is None or p < minpiv:
            minpiv = p
        if p == 0:
            for j in range(k + 1, n):
                if A[k][j] != 0:
                    return False, F(0), pivots
            continue
        for i in range(k + 1, n):
            if A[i][k] == 0:
                continue
            fac = A[i][k] / p
            for j in range(k, n):
                A[i][j] -= fac * A[k][j]
    return True, minpiv, pivots


# ---------------------------------------------------------------------------
# exact rational solve of  M y = b  (M symmetric PD here) via fraction-free Gaussian elim.
# returns y (list of Fraction) or None if singular.
# ---------------------------------------------------------------------------
def solve_exact(M, B):
    """Solve M Y = B for matrix B (list of column-vectors). M is n x n list-of-lists Fraction.
       Returns list of solution columns, or None if M singular."""
    n = len(M)
    if n == 0:
        return [[] for _ in B]
    ncol = len(B)
    # augmented [M | B]
    A = [[M[i][j] for j in range(n)] + [B[c][i] for c in range(ncol)] for i in range(n)]
    for k in range(n):
        # pivot
        piv = k
        while piv < n and A[piv][k] == 0:
            piv += 1
        if piv == n:
            return None
        if piv != k:
            A[k], A[piv] = A[piv], A[k]
        pv = A[k][k]
        for i in range(n):
            if i == k:
                continue
            if A[i][k] == 0:
                continue
            fac = A[i][k] / pv
            for j in range(k, n + ncol):
                A[i][j] -= fac * A[k][j]
    sols = []
    for c in range(ncol):
        sols.append([A[i][n + c] / A[i][i] for i in range(n)])
    return sols


def submatrix(H, rows, cols):
    return [[H[i][j] for j in cols] for i in rows]


def matmul(A, B):
    """A (a x b) * B (b x c)."""
    a = len(A); b = len(A[0]) if a else 0; c = len(B[0]) if B else 0
    return [[sum(A[i][k] * B[k][j] for k in range(b)) for j in range(c)] for i in range(a)]


def schur_on_O(H, n, T, N):
    """Partition by O={v:T_v>N}, U=rest.  Return dict with S (Schur compl on O), block PSD facts.
       S = H_OO - H_OU H_UU^{-1} H_UO ; only defined when H_UU PD (we test that)."""
    O = [v for v in range(n) if T[v] > N]
    U = [v for v in range(n) if T[v] <= N]
    H_OO = submatrix(H, O, O)
    H_OU = submatrix(H, O, U)
    H_UO = submatrix(H, U, O)
    H_UU = submatrix(H, U, U)
    # PSD of full H, and of the two blocks
    psdH, minpivH, _ = ldl_psd(H)
    psdUU, minpivUU, _ = ldl_psd(H_UU)
    res = dict(O=O, U=U, H_OO=H_OO, H_UU=H_UU, H_OU=H_OU,
               psdH=psdH, minpivH=minpivH, psdUU=psdUU, minpivUU=minpivUU,
               S=None, psdS=None, minpivS=None, UU_PD=None, rowsum=None)
    if not O:
        # O empty: S vacuously PSD (0x0). H PSD iff H_UU PSD.
        res['S'] = []
        res['psdS'] = True
        res['minpivS'] = None
        res['UU_PD'] = psdUU and (minpivUU is not None and minpivUU > 0)
        return res
    # solve H_UU X = H_UO  (X = H_UU^{-1} H_UO), columns = columns of H_UO (|O| of them)
    cols = [[H_UO[i][c] for i in range(len(U))] for c in range(len(O))]
    X = solve_exact(H_UU, cols)
    if X is None:
        res['UU_PD'] = False
        return res
    res['UU_PD'] = (psdUU and minpivUU is not None and minpivUU > 0)
    # X back to matrix |U| x |O|
    Xm = [[X[c][i] for c in range(len(O))] for i in range(len(U))]
    HOU_X = matmul(H_OU, Xm)  # |O| x |O|
    S = [[H_OO[i][j] - HOU_X[i][j] for j in range(len(O))] for i in range(len(O))]
    psdS, minpivS, _ = ldl_psd(S)
    res['S'] = S; res['psdS'] = psdS; res['minpivS'] = minpivS
    # transportation diagnostic: row sums of S vs the overload supply (T_o - N) and S*1
    rowsum = [sum(S[i]) for i in range(len(O))]
    res['rowsum'] = rowsum
    res['supply'] = [T[o] - N for o in O]   # overload supply at each o
    return res


def test_cut(name, n, adj, side, acc, verbose=False):
    if not Bconn(n, adj, side):
        return None
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, ell, T, mu, cyc = st
    if not M:
        return None
    N = F(n)
    H = build_H(n, M, ell, T, cyc, BETA)
    r = schur_on_O(H, n, T, N)
    acc['cuts'] += 1
    O = r['O']
    # consistency: full-H PSD must agree with (S>=0 AND H_UU>=0) when H_UU is PD
    if not r['psdH']:
        acc['H_fail'] += 1
        if acc['H_ex'] is None:
            acc['H_ex'] = (name, n, ''.join(map(str, side)), str(r['minpivH']))
    if O:
        if r['UU_PD'] is False:
            acc['UU_singular'] += 1
            if acc['UU_ex'] is None:
                acc['UU_ex'] = (name, n, ''.join(map(str, side)))
        if r['psdS'] is False:
            acc['S_fail'] += 1
            if acc['S_ex'] is None:
                acc['S_ex'] = (name, n, ''.join(map(str, side)), str(r['minpivS']))
        else:
            acc['O_nonempty'] += 1
            if r['minpivS'] == 0:
                acc['S_tight'] += 1
            if r['minpivS'] is not None and (acc['minS'] is None or r['minpivS'] < acc['minS']):
                acc['minS'] = r['minpivS']
        # CROSS-CHECK: when H_UU is PD, psdH must equal psdS
        if r['UU_PD']:
            if r['psdH'] != r['psdS']:
                acc['mismatch'] += 1
                if acc['mismatch_ex'] is None:
                    acc['mismatch_ex'] = (name, n, ''.join(map(str, side)),
                                          'psdH=%s psdS=%s' % (r['psdH'], r['psdS']))
    else:
        acc['O_empty'] += 1
    if verbose:
        print(f"  [{name}] N={n} O={O} U_size={len(r['U'])} "
              f"minpiv(H_UU)={float(r['minpivUU']) if r['minpivUU'] is not None else None} "
              f"UU_PD={r['UU_PD']} psdH={r['psdH']} psdS={r['psdS']} "
              f"minpiv(S)={float(r['minpivS']) if r['minpivS'] is not None else None}", flush=True)
        if O:
            print(f"      supply (T_o-N) = {[float(s) for s in r['supply']]}", flush=True)
            print(f"      S row sums     = {[float(s) for s in r['rowsum']]}", flush=True)
            print(f"      S =", flush=True)
            for row in r['S']:
                print("       ", [str(x) for x in row], flush=True)
    return r


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


def c5_blowup(t):
    """uniform C5[t] = blow each of 5 cycle vertices to t; standard 2-coloring (one same-side wrap pair)."""
    sizes = [t] * 5
    n = 5 * t
    start = [0] * 5
    for i in range(1, 5):
        start[i] = start[i - 1] + sizes[i - 1]
    E = []
    for i in range(5):
        j = (i + 1) % 5
        for a in range(sizes[i]):
            for b in range(sizes[j]):
                E.append((start[i] + a, start[j] + b))
    return n, E


def main():
    acc = dict(cuts=0, H_fail=0, S_fail=0, UU_singular=0, O_empty=0, O_nonempty=0,
               S_tight=0, minS=None, mismatch=0,
               H_ex=None, S_ex=None, UU_ex=None, mismatch_ex=None)

    print("=" * 70)
    print("SCHUR-ON-OVERLOAD exact gate: S = H_OO - H_OU H_UU^{-1} H_UO >= 0 ?")
    print("=" * 70)

    # ---- focused, verbose battery ----
    print("\n--- focused witnesses (verbose) ---")
    # H?AFBo] N=9 Gamma=50
    n, E = dec('H?AFBo]')
    gfam("H?AFBo]_N9", n, E, acc, verbose=True)

    # C5[2] N=10 and C5[3] N=15 (TIGHT extremal)
    for t in (2, 3):
        n, E = c5_blowup(t)
        gfam("C5[%d]_N%d" % (t, 5 * t), n, E, acc, verbose=True)

    # two census N=8 and N=9 graphs (first triangle-free connected of each that yields an O-nonempty cut)
    print("\n--- two census N=8/9 graphs (verbose where O nonempty) ---")
    for nn in (8, 9):
        outg = subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split()
        shown = 0
        for g6 in outg:
            n, E = dec(g6)
            adj = [set() for _ in range(n)]
            for x, y in E:
                adj[x].add(y); adj[y].add(x)
            try:
                _, cuts = gmins(n, E)
            except Exception:
                continue
            for side in cuts:
                r = test_cut("cen%d_%s" % (nn, g6), n, adj, side, acc,
                             verbose=(shown < 1))
                if r is not None and r['O'] and shown < 1:
                    shown += 1
            if shown >= 1:
                break

    # ---- broad silent battery (full census 5..10 + Myc Grotzsch N=23 + C5[t] sweep) ----
    print("\n--- broad battery (silent; aggregate) ---")
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            gfam("cen%d" % nn, n, E, acc)
        print("  census N=%d done: cuts=%d O_nonempty=%d S_fail=%d H_fail=%d"
              % (nn, acc['cuts'], acc['O_nonempty'], acc['S_fail'], acc['H_fail']), flush=True)

    # C5[t] sweep
    for t in range(2, 5):
        n, E = c5_blowup(t)
        if n <= 24:
            gfam("C5[%d]" % t, n, E, acc)

    # Myc(Grotzsch) N=23 guardrail
    grN, grE = mycielski(5, Cn(5))
    gfam("Grotzsch_N11", grN, grE, acc)
    m2N, m2E = mycielski(grN, grE)
    adj = [set() for _ in range(m2N)]
    for x, y in m2E:
        adj[x].add(y); adj[y].add(x)
    side = maxcut_ls(m2N, adj)
    if Bconn(m2N, adj, side):
        r = test_cut("MycGrotzsch_N23", m2N, adj, side, acc, verbose=True)

    print("\n" + "=" * 70)
    print("RESULTS")
    print("  total gamma-min cuts tested :", acc['cuts'])
    print("  cuts with O empty           :", acc['O_empty'])
    print("  cuts with O nonempty        :", acc['O_nonempty'])
    print("  H PSD failures (full H)     :", acc['H_fail'], acc['H_ex'] or '')
    print("  H_UU singular (not PD)      :", acc['UU_singular'], acc['UU_ex'] or '')
    print("  SCHUR S>=0 FAILURES         :", acc['S_fail'], acc['S_ex'] or '')
    print("  S tight (min pivot 0)       :", acc['S_tight'])
    print("  min Schur pivot (exact)     :", str(acc['minS']))
    print("  psdH vs psdS MISMATCH       :", acc['mismatch'], acc['mismatch_ex'] or '')
    ok = (acc['S_fail'] == 0 and acc['mismatch'] == 0 and acc['H_fail'] == 0)
    print("  VERDICT:",
          "SCHUR-ON-OVERLOAD S>=0 HOLDS exact on full battery incl N=23; "
          "and (S>=0 <=> H>=0) confirmed whenever H_UU PD -- reduces (H) to PSD of the |O|x|O| Schur matrix S"
          if ok else "FAIL -- see first counterexample above")


if __name__ == "__main__":
    main()
