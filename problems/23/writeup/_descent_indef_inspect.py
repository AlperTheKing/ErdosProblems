"""Focused inspection of the indefinite-S max cuts found by _descent_negmode_gate.
For each O-nonempty MAX cut whose Schur S is indefinite, report exactly:
  - is the cut gamma-min? (compare Gamma to the gamma-min value over connected-B max cuts)
  - S, its min pivot, the exact min-eigvec direction and E=phi^T H phi
  - the FULL neutral-switch picture: over ALL vertex subsets W (n<=10 exhaustive), the neutral ones
    (sigma=0) that keep B connected and STRICTLY decrease Gamma -- do ANY exist? what is the min dG?
  - whether the harmonic level-set W={phi>t} ever coincides with a genuine neutral Gamma-decreasing flip.
This separates two failure modes:
  (F1) the cut is non-gamma-min and DOES admit some neutral Gamma-decrease, but NOT via a phi level set
       (=> the level-set CONSTRUCTION is wrong, estimate-as-inequality may still be salvageable);
  (F2) the cut is non-gamma-min yet admits NO neutral Gamma-decrease of size <=E (=> the descent
       estimate dG<=phi^T H phi is simply FALSE; the contrapositive route via this H is broken).
EXACT Fraction.   Run:  python _descent_indef_inspect.py
"""
import subprocess
from fractions import Fraction as F

from _h import dec, GENG, Bconn, maxcut_all, bdist_restr
from _satzmu_conn import struct_for_side
from _hardy_gate import BETA, build_H
from _schur_overload_gate import solve_exact, submatrix, matmul, ldl_psd
from _codex_k2t_switch_probe import adj_from_edges, flip_side, boundary_delta, gamma_of

try:
    import numpy as np
    HAVE_NP = True
except Exception:
    HAVE_NP = False


def schur_S(H, O, U):
    H_OO = submatrix(H, O, O); H_OU = submatrix(H, O, U)
    H_UO = submatrix(H, U, O); H_UU = submatrix(H, U, U)
    cols = [[H_UO[i][c] for i in range(len(U))] for c in range(len(O))]
    X = solve_exact(H_UU, cols)
    if X is None:
        return None
    Xm = [[X[c][i] for c in range(len(O))] for i in range(len(U))]
    HOU_X = matmul(H_OU, Xm)
    return [[H_OO[i][j] - HOU_X[i][j] for j in range(len(O))] for i in range(len(O))]


def quad(M, x):
    s = F(0)
    for i in range(len(x)):
        for j in range(len(x)):
            s += x[i] * M[i][j] * x[j]
    return s


def harmonic_extend(H, O, U, xO):
    n = len(H)
    H_UU = submatrix(H, U, U); H_UO = submatrix(H, U, O)
    rhs = [F(0)] * len(U)
    for i in range(len(U)):
        s = F(0)
        for kk in range(len(O)):
            s += H_UO[i][kk] * xO[kk]
        rhs[i] = -s
    sol = solve_exact(H_UU, [rhs])
    if sol is None:
        return None, None
    phiU = sol[0]
    phi = [F(0)] * n
    for idx, o in enumerate(O):
        phi[o] = xO[idx]
    for idx, u in enumerate(U):
        phi[u] = phiU[idx]
    E = quad(H, phi)
    return phi, E


def gamma_minval(n, adj):
    best = None
    for s in maxcut_all(n, adj):
        if not Bconn(n, adj, s):
            continue
        g = gamma_of(n, adj, s)
        if g is None:
            continue
        if best is None or g < best:
            best = g
    return best


def all_neutral_descents(n, adj, side, gamma0):
    """Exhaustive over all nonempty proper W: neutral (sigma=0), B-connected after flip, dG<0.
       Returns list of (mask, dG) sorted by dG."""
    res = []
    full = (1 << n) - 1
    for mask in range(1, full):
        if boundary_delta(n, adj, side, mask) != 0:
            continue
        side2 = flip_side(side, mask)
        g2 = gamma_of(n, adj, side2)  # None if disconnected
        if g2 is None:
            continue
        dG = g2 - gamma0
        if dG < 0:
            res.append((mask, dG))
    res.sort(key=lambda z: z[1])
    return res


def neg_eigvec_exact(S):
    """exact integer min-direction for small |O| by brute search; fallback to rationalized float."""
    k = len(S)
    import itertools
    best = None
    for combo in itertools.product(range(-4, 5), repeat=k):
        if all(c == 0 for c in combo):
            continue
        x = [F(c) for c in combo]
        q = quad(S, x)
        if q < 0:
            # normalize ranking by q / (x.x) to approximate min eigvec
            nn = sum(c * c for c in x)
            r = q / nn
            if best is None or r < best[0]:
                best = (r, x, combo)
    if best:
        return best[1], best[2]
    return None, None


def inspect(name, n, adj, side):
    st = struct_for_side(n, adj, side)
    if st is None:
        return False
    M, ell, T, mu, cyc = st
    if not M:
        return False
    N = F(n)
    O = [v for v in range(n) if T[v] > N]
    if not O:
        return False
    U = [v for v in range(n) if T[v] <= N]
    H = build_H(n, M, ell, T, cyc, BETA)
    S = schur_S(H, O, U)
    if S is None:
        return False
    psdS, minpiv, _ = ldl_psd(S)
    if psdS:
        return False
    gamma0 = gamma_of(n, adj, side)
    gmv = gamma_minval(n, adj)
    print("-" * 72)
    print("INDEF-S CUT %s  side=%s" % (name, ''.join(map(str, side))))
    print("  O=%s  U=%s  Gamma=%s  gamma-min(global)=%s  IS_GAMMA_MIN=%s"
          % (O, U, gamma0, gmv, gamma0 == gmv))
    print("  S min pivot (exact):", str(minpiv), " ~", float(minpiv) if minpiv is not None else None)
    print("  S =")
    for row in S:
        print("    ", [str(x) for x in row])
    # exact negative direction
    xneg, combo = neg_eigvec_exact(S)
    if xneg is None:
        print("  no integer negative direction found in [-4,4]^O")
        return True
    qx = quad(S, xneg)
    print("  exact neg direction x_O =", combo, " x^T S x =", str(qx), "~", float(qx))
    phi, E = harmonic_extend(H, O, U, xneg)
    print("  E = phi^T H phi =", str(E), "~", float(E), " (== x^T S x:", E == qx, ")")
    # phi values
    print("  phi =", [str(phi[v]) for v in range(n)])
    # ALL neutral Gamma-decreasing flips (exhaustive)
    nds = all_neutral_descents(n, adj, side, gamma0)
    print("  # neutral B-connected Gamma-DECREASING flips:", len(nds))
    if nds:
        bestmask, bestdG = nds[0]
        Wbest = tuple(v for v in range(n) if (bestmask >> v) & 1)
        print("    best neutral descent: W=%s dG=%s  (E=%s)  dG<=E? %s"
              % (Wbest, str(bestdG), str(E), bestdG <= E))
        print("    min neutral dG over ALL neutral descents = %s ; <= E ? %s"
              % (str(bestdG), bestdG <= E))
    else:
        print("    NO neutral Gamma-decreasing flip exists for this cut (contrapositive vacuous here).")
    # does any phi level set equal a neutral descent?
    ts = sorted(set(phi), reverse=True)
    matched = []
    for t in ts:
        W = tuple(v for v in range(n) if phi[v] > t)
        if not W or len(W) == n:
            continue
        mask = 0
        for v in W:
            mask |= 1 << v
        sigma = boundary_delta(n, adj, side, mask)
        side2 = flip_side(side, mask)
        g2 = gamma_of(n, adj, side2)
        dG = None if g2 is None else g2 - gamma0
        matched.append((t, W, sigma, None if dG is None else str(dG),
                        (dG is not None and dG <= E)))
    print("  phi level-set thresholds (t, W, sigma=dB-dM, dG, dG<=E):")
    for rec in matched:
        print("    ", rec)
    return True


def main():
    print("=" * 72)
    print("INSPECT indefinite-S max cuts (the descent-estimate failure sites)")
    print("=" * 72)
    targets = []
    for nn in (9, 10):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            adj = adj_from_edges(n, E)
            for side in maxcut_all(n, adj):
                if not Bconn(n, adj, side):
                    continue
                st = struct_for_side(n, adj, side)
                if st is None:
                    continue
                M, ell, T, mu, cyc = st
                if not M:
                    continue
                N = F(n)
                O = [v for v in range(n) if T[v] > N]
                if not O:
                    continue
                U = [v for v in range(n) if T[v] <= N]
                H = build_H(n, M, ell, T, cyc, BETA)
                S = schur_S(H, O, U)
                if S is None:
                    continue
                psd, _, _ = ldl_psd(S)
                if not psd:
                    targets.append(("cen%d_%s" % (nn, g6), n, adj, side))
    print("indefinite-S O-nonempty max cuts found:", len(targets))
    seen_g6 = set()
    shown = 0
    for name, n, adj, side in targets:
        # show distinct underlying graphs (avoid duplicate sides), cap at 8
        key = name.split('_', 1)[1]
        if (key, ''.join(map(str, side))) in seen_g6:
            continue
        seen_g6.add((key, ''.join(map(str, side))))
        if inspect(name, n, adj, side):
            shown += 1
        if shown >= 8:
            break


if __name__ == "__main__":
    main()
