r"""EXACT gate for Codex's SHARP Schur structure (block 10:03): the overload Schur complement S of H reduces
S>=0 to a SINGLE one-terminal scalar.

  H=diag(N-T)+Lstar (rational beta').  O={T_v>N}, U=V\O.  S = H_OO - H_OU H_UU^{-1} H_UO.
  rho_i = row-sum of S.  R = {i in O: rho_i < 0}.
  CLAIMS: (1) S is a symmetric M-matrix (S_ij<=0 i!=j).  (2) |R| <= 1.  (3) R empty => S diag-dominant => PSD.
          (4) R={r} => one-terminal Schur scalar s_r = S[r,r]-S[r,P]S[P,P]^{-1}S[P,r] >= 0 (P=O\{r}) => S PSD.
  If |R|<=1 robustly AND the one-terminal scalar>=0, then (P2)/S>=0 reduces to ONE scalar inequality.

Full battery incl N=23 + randoms/overloaded blowups/islands (where |R|>=2 would first appear).  Exact Fraction.
Also cross-checks S>=0 directly via exact LDL (ground truth) so a one-terminal pass is only meaningful if S is PSD.
"""
import subprocess, random
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _wf_deficit_farkas import odd_blowup
from _bdef_construct import Cn, union_disjoint, add_edges, mycielski, is_triangle_free
from _Klocal_gate import glued_c5_chain
from _hardy_gate import build_H, BETA
from _csmspec import is_psd


def solve_mat(A, B):
    """Exact solve A X = B (A m x m nonsingular sym, B m x k). Returns X (m x k) or None if singular."""
    m = len(A); k = len(B[0]) if B else 0
    Aug = [list(A[i]) + list(B[i]) for i in range(m)]
    for col in range(m):
        piv = None
        for r in range(col, m):
            if Aug[r][col] != 0:
                piv = r; break
        if piv is None:
            return None
        Aug[col], Aug[piv] = Aug[piv], Aug[col]
        pv = Aug[col][col]
        for r in range(m):
            if r != col and Aug[r][col] != 0:
                fac = Aug[r][col] / pv
                for c in range(col, m + k):
                    Aug[r][c] -= fac * Aug[col][c]
    X = [[Aug[i][m + j] / Aug[i][i] for j in range(k)] for i in range(m)]
    return X


def schur_on(S, keep, elim):
    """1-step Schur complement of S keeping `keep` indices, eliminating `elim` (lists of indices into S)."""
    if not elim:
        return [[S[a][b] for b in keep] for a in keep]
    See = [[S[a][b] for b in elim] for a in elim]
    Sek = [[S[a][b] for b in keep] for a in elim]
    X = solve_mat(See, Sek)  # See^{-1} Sek
    if X is None:
        return None
    out = []
    for ia, a in enumerate(keep):
        row = []
        for ib, b in enumerate(keep):
            corr = sum(S[a][elim[t]] * X[t][ib] for t in range(len(elim)))
            row.append(S[a][b] - corr)
        out.append(row)
    return out


def test_cut(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, cyc = st[0], st[1], st[2], st[4]
    if not M:
        return
    acc['cuts'] += 1
    N = F(n)
    H = build_H(n, M, ell, T, cyc, BETA)
    O = [v for v in range(n) if T[v] > N]
    U = [v for v in range(n) if T[v] <= N]
    if not O:
        return
    acc['Ononempty'] += 1
    Huu = [[H[a][b] for b in U] for a in U]
    Huo = [[H[a][b] for b in O] for a in U]
    Hoo = [[H[a][b] for b in O] for a in O]
    Hou = [[H[a][b] for b in U] for a in O]
    X = solve_mat(Huu, Huo)  # Huu^{-1} Huo
    if X is None:
        acc['Huu_singular'] += 1
        return
    # S = Hoo - Hou X
    m = len(O)
    S = [[Hoo[i][j] - sum(Hou[i][t] * X[t][j] for t in range(len(U))) for j in range(m)] for i in range(m)]
    # (1) M-matrix: off-diag <=0
    for i in range(m):
        for j in range(m):
            if i != j and S[i][j] > 0:
                acc['Mmat_fail'] += 1
                if acc['Mmat_ex'] is None:
                    acc['Mmat_ex'] = (name, n, i, j, str(S[i][j]))
    # row sums, R
    rho = [sum(S[i][j] for j in range(m)) for i in range(m)]
    R = [i for i in range(m) if rho[i] < 0]
    acc['Rhist'][len(R)] = acc['Rhist'].get(len(R), 0) + 1
    if len(R) > acc['Rmax']:
        acc['Rmax'] = len(R)
    if len(R) >= 2:
        acc['R_ge2'] += 1
        if acc['R_ex'] is None:
            acc['R_ex'] = (name, n, ''.join(map(str, side)), len(R), [str(rho[i]) for i in R])
    # ground truth: is S PSD?
    psd, mp = is_psd([row[:] for row in S])
    if not psd:
        acc['S_notpsd'] += 1
        if acc['Snp_ex'] is None:
            acc['Snp_ex'] = (name, n, ''.join(map(str, side)), str(mp))
    # one-terminal check if |R|==1
    if len(R) == 1:
        r = R[0]; P = [i for i in range(m) if i != r]
        S1 = schur_on(S, [r], P)
        if S1 is None:
            acc['oneterm_singular'] += 1
        else:
            s_r = S1[0][0]
            if s_r < 0:
                acc['oneterm_fail'] += 1
                if acc['ot_ex'] is None:
                    acc['ot_ex'] = (name, n, ''.join(map(str, side)), str(s_r))
            else:
                if acc['ot_min'] is None or s_r < acc['ot_min']:
                    acc['ot_min'] = s_r


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


def maxcut_ls(n, adj, seeds=80):
    best = None; bv = -1; rng = random.Random(9)
    for _ in range(seeds):
        s = [rng.randint(0, 1) for _ in range(n)]; imp = True
        while imp:
            imp = False
            for v in range(n):
                if sum(1 for w in adj[v] if s[w] == s[v]) > sum(1 for w in adj[v] if s[w] != s[v]):
                    s[v] ^= 1; imp = True
        val = sum(1 for v in range(n) for w in adj[v] if w > v and s[v] != s[w])
        if val > bv:
            bv = val; best = s[:]
    return best


def main():
    acc = dict(cuts=0, Ononempty=0, Huu_singular=0, Mmat_fail=0, R_ge2=0, Rmax=0, Rhist={},
               S_notpsd=0, oneterm_fail=0, oneterm_singular=0, ot_min=None,
               Mmat_ex=None, R_ex=None, Snp_ex=None, ot_ex=None)
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); gfam("cen%d" % nn, n, E, acc)
        print("census N=%d: On=%d Rmax=%d R>=2=%d Mmat_fail=%d S_notpsd=%d oneterm_fail=%d"
              % (nn, acc['Ononempty'], acc['Rmax'], acc['R_ge2'], acc['Mmat_fail'], acc['S_notpsd'], acc['oneterm_fail']), flush=True)
    grN, grE = mycielski(5, Cn(5)); gfam("Grotzsch", grN, grE, acc)
    m2N, m2E = mycielski(grN, grE)
    adj = [set() for _ in range(m2N)]
    for x, y in m2E:
        adj[x].add(y); adj[y].add(x)
    side = maxcut_ls(m2N, adj)
    if Bconn(m2N, adj, side):
        test_cut("MycGrotzsch_N23", m2N, adj, side, acc)
    print("after Grotzsch+Myc23: On=%d Rmax=%d R>=2=%d %s" % (acc['Ononempty'], acc['Rmax'], acc['R_ge2'], acc['R_ex'] or ''), flush=True)
    for q in range(2, 16):
        n, E, side = glued_c5_chain(q)
        adj = [set() for _ in range(n)]
        for x, y in E:
            adj[x].add(y); adj[y].add(x)
        if Bconn(n, adj, side):
            test_cut("chain_q%d" % q, n, adj, side, acc)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(3,2,3,2,3),(4,3,4,3,4),(5,4,5,4,5),(2,2,2,2,2),(3,3,3,3,3),(4,2,4,2,4),(5,2,5,2,5)]:
        nn, EE = odd_blowup(5, list(sizes))
        if nn <= 24:
            gfam("blow%s" % (sizes,), nn, EE, acc)
    isl = (5, Cn(5)); g15 = mycielski(7, Cn(7))
    nn, EE = union_disjoint(isl, g15); nn, EE = add_edges((nn, EE), [(0, 5)])
    gfam("isl_C5_MycC7", nn, EE, acc)
    print("after chains+blowups+islands: On=%d Rmax=%d R>=2=%d %s" % (acc['Ononempty'], acc['Rmax'], acc['R_ge2'], acc['R_ex'] or ''), flush=True)
    rng = random.Random(7); made = 0; tries = 0
    while made < 200 and tries < 60000:
        tries += 1
        nn = rng.choice([11, 12, 13]); p = rng.uniform(0.12, 0.34)
        EE = [(a, b) for a in range(nn) for b in range(a+1, nn) if rng.random() < p]
        if not EE or not is_triangle_free(nn, EE):
            continue
        adj = [set() for _ in range(nn)]
        for a, b in EE:
            adj[a].add(b); adj[b].add(a)
        if any(len(adj[v]) == 0 for v in range(nn)):
            continue
        made += 1; gfam("rand%d" % made, nn, EE, acc)
    print("=" * 60)
    print("O-nonempty cuts tested:", acc['Ononempty'], " (random:", made, ")")
    print("Rmax (max |R|):", acc['Rmax'], " |R| histogram:", dict(sorted(acc['Rhist'].items())))
    print("|R|>=2 cases:", acc['R_ge2'], acc['R_ex'] or '')
    print("M-matrix (off-diag<=0) failures:", acc['Mmat_fail'], acc['Mmat_ex'] or '')
    print("S not PSD (ground truth):", acc['S_notpsd'], acc['Snp_ex'] or '')
    print("one-terminal scalar <0 failures:", acc['oneterm_fail'], acc['ot_ex'] or '')
    print("min one-terminal scalar (exact):", str(acc['ot_min']))
    ok = acc['R_ge2'] == 0 and acc['Mmat_fail'] == 0 and acc['oneterm_fail'] == 0 and acc['S_notpsd'] == 0
    print("VERDICT:", "|R|<=1 + M-matrix + one-terminal scalar>=0 HOLD exact incl N=23 + randoms/blowups -- (P2)/S>=0 reduces to ONE scalar"
          if ok else "FAIL (see above)")


if __name__ == "__main__":
    main()
