"""SHARPEST NEXT LEMMA candidate test.  (H) PSD reduces (Schur, H_UU strictly PD) to:
   S = H_OO - H_OU H_UU^{-1} H_UO  is a NONSINGULAR symmetric M-matrix.
Since S off-diag <= 0 is AUTOMATIC (S_Mmatrix=True everywhere, verified), the remaining content is:
   (P2)  there exists u > 0 with S u > 0   (this certifies S nonsingular M-matrix => PSD, NON-circularly
         if u is graph-explicit and not S^{-1}-derived).
At N=23, S*1 has a NEGATIVE entry (apex, -3.20), so u=1 FAILS.  We hunt a graph-explicit u>0 with Su>=0.

Candidates for u_o (o in O):
  (u1) u=1            -- ones (KNOWN to fail at N=23)
  (u2) u=b            -- overload supply b_o = T_o - N
  (u3) u=1/b          -- inverse supply (down-weight the apex)
  (u4) u=diag(S)      -- the self-capacity S[o,o]
  (u5) u=1/diag(S)
  (u6) u=deg-in-O reciprocal proxy
The point: identify ANY simple positive u with Su>=0 robustly incl N=23.  A 0-fail u IS a proof skeleton
(then prove Su>=0 in general from gamma-min).  Report per-candidate failure count + first ex.
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


def get_S(H, n, T, N):
    O = [v for v in range(n) if T[v] > N]
    U = [v for v in range(n) if T[v] <= N]
    if not O:
        return None, O, U, None
    H_OO = submatrix(H, O, O); H_OU = submatrix(H, O, U)
    H_UO = submatrix(H, U, O); H_UU = submatrix(H, U, U)
    p, mp, _ = ldl_psd(H_UU)
    if not (p and mp is not None and mp > 0):
        return 'UUbad', O, U, None
    cols = [[H_UO[i][c] for i in range(len(U))] for c in range(len(O))]
    X = solve_exact(H_UU, cols)
    if X is None:
        return 'UUsing', O, U, None
    Xm = [[X[c][i] for c in range(len(O))] for i in range(len(U))]
    HX = matmul(H_OU, Xm)
    S = [[H_OO[i][j] - HX[i][j] for j in range(len(O))] for i in range(len(O))]
    b = [T[o] - N for o in O]  # supply (>0 on O)
    return S, O, U, b


def candidates(S, b):
    k = len(S)
    diag = [S[i][i] for i in range(k)]
    cands = {}
    cands['u1_ones'] = [F(1)] * k
    cands['u2_supply'] = b[:]
    cands['u3_invsupply'] = [F(1) / bb if bb != 0 else F(1) for bb in b]
    cands['u4_diagS'] = diag[:]
    cands['u5_invdiagS'] = [F(1) / d if d != 0 else F(1) for d in diag]
    return cands


def Su(S, u):
    k = len(S)
    return [sum(S[i][j] * u[j] for j in range(k)) for i in range(k)]


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
    S, O, U, b = get_S(H, n, T, N)
    if not O or not isinstance(S, list):
        return
    acc['Ocuts'] += 1
    cands = candidates(S, b)
    for name_u, u in cands.items():
        if any(x <= 0 for x in u):
            acc[name_u + '_badpos'] = acc.get(name_u + '_badpos', 0) + 1
            continue
        v = Su(S, u)
        if any(x < 0 for x in v):
            acc[name_u + '_fail'] = acc.get(name_u + '_fail', 0) + 1
            if acc.get(name_u + '_ex') is None:
                acc[name_u + '_ex'] = (name, n, ''.join(map(str, side)))


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
    acc = dict(Ocuts=0)
    for nn in range(8, 11):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); gfam("cen%d" % nn, n, E, acc)
        print("census N=%d done: Ocuts=%d" % (nn, acc['Ocuts']), flush=True)
    grN, grE = mycielski(5, Cn(5)); m2N, m2E = mycielski(grN, grE)
    adj = [set() for _ in range(m2N)]
    for x, y in m2E:
        adj[x].add(y); adj[y].add(x)
    side = maxcut_ls(m2N, adj)
    if Bconn(m2N, adj, side):
        test_cut("MycGrotzsch_N23", m2N, adj, side, acc)
    print("after Myc23: Ocuts=%d" % acc['Ocuts'], flush=True)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(3,2,3,2,3),(4,3,4,3,4),(5,4,5,4,5),(2,2,2,2,2),(3,3,3,3,3)]:
        nn, EE = odd_blowup(5, list(sizes))
        if nn <= 24:
            gfam("blow%s" % (sizes,), nn, EE, acc)
    for q in range(2, 16):
        n, E, side = glued_c5_chain(q)
        adj = [set() for _ in range(n)]
        for x, y in E:
            adj[x].add(y); adj[y].add(x)
        if Bconn(n, adj, side):
            test_cut("chain_q%d" % q, n, adj, side, acc)
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
    print("O-nonempty gamma-min cuts:", acc['Ocuts'])
    for u in ['u1_ones', 'u2_supply', 'u3_invsupply', 'u4_diagS', 'u5_invdiagS']:
        print("  %-14s : Su<0 fails=%d  badpos=%d  first_ex=%s"
              % (u, acc.get(u + '_fail', 0), acc.get(u + '_badpos', 0), acc.get(u + '_ex')))


if __name__ == "__main__":
    main()
