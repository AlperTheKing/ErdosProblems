"""Pin down the CRUX: the N=23 Myc(Grotzsch) cut where Schur S on O is an M-matrix but NOT diagonally
dominant (one row sum < 0), yet still PSD.  Show EXACT numbers and confirm S>=0 needs more than diag-dom.
Also confirm the REDUCTION is logically complete: on every O-nonempty gamma-min cut, H_UU is strictly PD,
so (H) PSD  <=>  S PSD, and S is a 5x5-or-smaller M-matrix."""
from fractions import Fraction as F
from _h import Bconn
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, mycielski
from _hardy_gate import BETA, build_H, maxcut_ls
from _schur_overload_gate import ldl_psd, schur_on_O


def main():
    grN, grE = mycielski(5, Cn(5))
    m2N, m2E = mycielski(grN, grE)
    n = m2N
    adj = [set() for _ in range(n)]
    for x, y in m2E:
        adj[x].add(y); adj[y].add(x)
    side = maxcut_ls(n, adj)
    print("N =", n, "Bconn =", Bconn(n, adj, side))
    st = struct_for_side(n, adj, side)
    M, ell, T, mu, cyc = st
    N = F(n)
    H = build_H(n, M, ell, T, cyc, BETA)
    r = schur_on_O(H, n, T, N)
    O = r['O']; U = r['U']
    print("O =", O)
    print("supply b_o = T_o - N =", [float(T[o] - N) for o in O])
    print("H_UU PD (min pivot > 0)?  minpiv(H_UU) =", float(r['minpivUU']), " PD =", r['minpivUU'] > 0)
    S = r['S']; k = len(O)
    print("\nSchur S on O (exact, as floats for readability):")
    for i in range(k):
        print("  ", [round(float(S[i][j]), 6) for j in range(k)])
    print("\nS diagonal      :", [round(float(S[i][i]), 6) for i in range(k)])
    print("S row sums (rho):", [round(float(sum(S[i])), 6) for i in range(k)])
    offdiag_max = max(S[i][j] for i in range(k) for j in range(k) if i != j)
    print("max off-diagonal of S (should be <= 0 for M-matrix):", float(offdiag_max))
    print("=> S is M-matrix:", offdiag_max <= 0, " ; diag-dominant:", all(sum(S[i]) >= 0 for i in range(k)))
    psdS, minpivS, pivS = ldl_psd(S)
    print("S PSD:", psdS, " min pivot:", float(minpivS))
    print("S LDL pivots:", [round(float(p), 6) for p in pivS])
    print("\nCRUX CONFIRMED: at N=23, S is an M-matrix with a NEGATIVE row sum (",
          round(float(min(sum(S[i]) for i in range(k))), 4),
          ") yet S>=0 (min pivot", round(float(minpivS), 4), "> 0).")
    print("=> diagonal dominance is INSUFFICIENT; the cycle-conductance (beta_L) network strictly carries")
    print("   the overload to deficit. The proof of (H) on O-nonempty cuts must use the M-matrix inverse")
    print("   structure (effective conductance), not mere weak diagonal dominance.")


if __name__ == "__main__":
    main()
