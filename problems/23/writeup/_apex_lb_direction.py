"""Diagnose the FAILURE of the structural lower bounds in _apex_conductance_gate.py.

On the unique |R|=1 cut (N=23 Myc Grotzsch), check the M-matrix-inverse direction:
  s_r = S[r,r] - S[r,P] S_PP^{-1} S[P,r].   The correction term C := S[r,P] S_PP^{-1} S[P,r].
  Diagonal estimate D := sum_{j in P} S[r,j]^2 / S[j,j].
Claim to test:  S_PP is a symmetric M-matrix => S_PP^{-1} >= 0 (entrywise) => C >= D (the off-diagonal
nonneg entries of the inverse ADD positive cross terms since S[r,j]=-a_j<=0, so a^T S_PP^{-1} a picks up
positive off-diag).  Hence B_diag = S[r,r]-D >= S[r,r]-C = s_r:  B_diag is an UPPER bound, NOT a lower bound.

Print exact: s_r, S[r,r], C, D, B_diag, and confirm S_PP^{-1} entrywise >=0, C>=D, B_diag>=s_r.
Run: python _apex_lb_direction.py
"""
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, mycielski
from _hardy_gate import build_H, BETA, maxcut_ls
from _Rsize_gate import solve_mat
from _apex_conductance_gate import build_S


def main():
    grN, grE = mycielski(5, Cn(5))
    m2N, m2E = mycielski(grN, grE)
    adj = [set() for _ in range(m2N)]
    for x, y in m2E:
        adj[x].add(y); adj[y].add(x)
    side = maxcut_ls(m2N, adj)
    assert Bconn(m2N, adj, side)
    st = struct_for_side(m2N, adj, side)
    M, ell, T, mu, cyc = st
    N = F(m2N)
    H = build_H(m2N, M, ell, T, cyc, BETA)
    S, O = build_S(H, m2N, T, N)
    m = len(O)
    rho = [sum(S[i][j] for j in range(m)) for i in range(m)]
    Rset = [i for i in range(m) if rho[i] < 0]
    print("O =", O, " rho =", [float(x) for x in rho], " R =", Rset)
    r = Rset[0]
    P = [i for i in range(m) if i != r]
    Spp = [[S[a][b] for b in P] for a in P]
    Spr = [[S[a][r]] for a in P]               # column |P|x1
    # S_PP^{-1} (full, to inspect entrywise sign)
    I = [[F(1) if i == j else F(0) for j in range(len(P))] for i in range(len(P))]
    Sinv = solve_mat(Spp, I)
    # entrywise nonneg?
    nonneg = all(Sinv[i][j] >= 0 for i in range(len(P)) for j in range(len(P)))
    # correction term C = Spr^T Sinv Spr
    y = solve_mat(Spp, Spr)   # |P|x1
    Cterm = sum(S[r][P[t]] * y[t][0] for t in range(len(P)))
    Dterm = sum(S[r][P[j]] * S[r][P[j]] / S[P[j]][P[j]] for j in range(len(P)) if S[P[j]][P[j]] != 0)
    Srr = S[r][r]
    s_r = Srr - Cterm
    Bdiag = Srr - Dterm
    print("S[r,r]      =", float(Srr))
    print("C (true corr)=", float(Cterm))
    print("D (diag est) =", float(Dterm))
    print("s_r = Srr-C =", float(s_r))
    print("Bdiag=Srr-D =", float(Bdiag))
    print("S_PP^{-1} entrywise >= 0 ?", nonneg, " (M-matrix => nonneg inverse)")
    print("C >= D ?", Cterm >= Dterm, " => Bdiag >= s_r ?", Bdiag >= s_r)
    print()
    print("CONCLUSION: B_diag (and B_star) are UPPER bounds on s_r, not lower bounds.")
    print("  The proposed local 'a^2/(a+R)' / diagonal-Schur lower bounds OVER-count s_r because")
    print("  S_PP^{-1} >= 0 (M-matrix) makes the true Schur correction LARGER than the diagonal one.")
    print("  => the apex inequality s_r>=0 holds 0-fail (validated) but is NOT certified by these")
    print("     apex-row-local bounds; a genuine LOWER bound must under-estimate the correction term.")


if __name__ == "__main__":
    main()
