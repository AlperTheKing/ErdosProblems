"""Decompose the supersolution certificate into its two ATOMIC facts on O-nonempty cuts:
   (i)  S^{-1} >= 0  (S is an invertible symmetric M-matrix => Stieltjes => nonneg inverse)
   (ii) Xm := H_UU^{-1} H_UO  <= 0  entrywise  (since H_UU Stieltjes, H_UO <= 0)
   Together they give phi_O = S^{-1}1 > 0 and phi_U = -Xm phi_O >= 0, i.e. phi >= 0 supersolution.
   Probe both EXACTLY on N=23 + overloaded blowups; report whether they hold separately."""
from fractions import Fraction as F
from _h import Bconn
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, mycielski
from _wf_deficit_farkas import odd_blowup
from _stark1 import gmins
from _hardy_gate import BETA, build_H, maxcut_ls
from _schur_overload_gate import ldl_psd, solve_exact, submatrix, matmul


def probe(H, n, T, N):
    O = [v for v in range(n) if T[v] > N]
    U = [v for v in range(n) if T[v] <= N]
    if not O:
        return None
    H_OO = submatrix(H, O, O); H_OU = submatrix(H, O, U)
    H_UO = submatrix(H, U, O); H_UU = submatrix(H, U, U)
    cols = [[H_UO[i][c] for i in range(len(U))] for c in range(len(O))]
    X = solve_exact(H_UU, cols)
    Xm = [[X[c][i] for c in range(len(O))] for i in range(len(U))]
    HX = matmul(H_OU, Xm)
    S = [[H_OO[i][j] - HX[i][j] for j in range(len(O))] for i in range(len(O))]
    Icols = [[F(1) if i == j else F(0) for i in range(len(O))] for j in range(len(O))]
    Sinv = solve_exact(S, Icols)
    if Sinv is None:
        return ('S_singular', len(O))
    sinv_nn = all(Sinv[c][r] >= 0 for c in range(len(O)) for r in range(len(O)))
    phiO = solve_exact(S, [[F(1)] * len(O)])[0]
    phiU = [-sum(Xm[i][j] * phiO[j] for j in range(len(O))) for i in range(len(U))]
    phiU_nn = all(x >= 0 for x in phiU)
    Xm_nonpos = all(Xm[i][j] <= 0 for i in range(len(U)) for j in range(len(O)))
    S_offdiag_nonpos = all(S[i][j] <= 0 for i in range(len(O)) for j in range(len(O)) if i != j)
    return (sinv_nn, phiU_nn, Xm_nonpos, S_offdiag_nonpos, len(O))


def main():
    grN, grE = mycielski(5, Cn(5)); m2N, m2E = mycielski(grN, grE)
    adj = [set() for _ in range(m2N)]
    for x, y in m2E:
        adj[x].add(y); adj[y].add(x)
    side = maxcut_ls(m2N, adj)
    st = struct_for_side(m2N, adj, side); M, ell, T, mu, cyc = st
    H = build_H(m2N, M, ell, T, cyc, BETA)
    print("N=23 (Sinv>=0, phiU>=0, Xm<=0, S_offdiag<=0, |O|):", probe(H, m2N, T, F(m2N)))

    for sizes in [(2,1,2,1,2),(3,2,3,2,3),(4,3,4,3,4),(2,2,2,2,2),(5,4,5,4,5)]:
        nn, EE = odd_blowup(5, list(sizes))
        if nn > 24:
            continue
        adj = [set() for _ in range(nn)]
        for x, y in EE:
            adj[x].add(y); adj[y].add(x)
        try:
            _, cuts = gmins(nn, EE)
        except Exception:
            continue
        res = []
        for sd in cuts:
            if not Bconn(nn, adj, sd):
                continue
            s = struct_for_side(nn, adj, sd)
            if s is None or not s[0]:
                continue
            H = build_H(nn, s[0], s[1], s[2], s[4], BETA)
            r = probe(H, nn, s[2], F(nn))
            if r and len(r) == 5:
                res.append(r)
        if res:
            allsinv = all(r[0] for r in res); allphi = all(r[1] for r in res)
            allxm = all(r[2] for r in res); alloff = all(r[3] for r in res)
            print("blow%s N=%d: Sinv>=0=%s phiU>=0=%s Xm<=0=%s S_Mmatrix=%s  #O-cuts=%d"
                  % (sizes, nn, allsinv, allphi, allxm, alloff, len(res)))


if __name__ == "__main__":
    main()
