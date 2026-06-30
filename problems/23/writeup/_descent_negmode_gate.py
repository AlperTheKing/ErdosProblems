"""NEGATIVE-MODE hunt for the level-set DESCENT ESTIMATE.

v1 (_descent_levelset_gate) showed: on REAL gamma-min cuts S>=0 always, so E=phi^T H phi >=0 for
every test vector -> the descent estimate is never exercised on a true negative mode.  To put teeth
on it we must find cuts where S genuinely has a negative eigenvalue (these are NECESSARILY non-gamma-min,
by the very theorem we are trying to prove).  Then test, EXACTLY, with x = a vector achieving x^T S x<0:
   does a NEUTRAL level-set flip W={phi>t} give  dG = Gamma(flip W)-Gamma  <=  E = phi^T H phi (<0) ?

We scan ALL connected-B MAXIMUM cuts (gamma-min or not) of triangle-free graphs.  For each O-nonempty
cut we build H, S, get the exact min-eigvec direction, rationalize, and KEEP ONLY vectors x with E<0
verified exactly.  We then enumerate every level-set threshold t of phi, classify neutral (sigma=dB-dM==0)
vs non-neutral, recompute Gamma after the flip (exact struct_for_side), and tabulate whether dG<=E.

EXACT Fraction for all pass/fail.   Run:  python _descent_negmode_gate.py
"""
import subprocess, random
from fractions import Fraction as F

from _h import dec, GENG, Bconn, maxcut_all
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, mycielski, is_triangle_free
from _hardy_gate import BETA, build_H, maxcut_ls
from _schur_overload_gate import solve_exact, submatrix, matmul, ldl_psd
from _codex_k2t_switch_probe import adj_from_edges, flip_side, boundary_delta, gamma_of

try:
    import numpy as np
    HAVE_NP = True
except Exception:
    HAVE_NP = False


def mask_of(verts):
    m = 0
    for v in verts:
        m |= 1 << v
    return m


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


def quad(S, x):
    s = F(0)
    for i in range(len(x)):
        if x[i] == 0:
            continue
        for j in range(len(x)):
            if S[i][j] != 0 and x[j] != 0:
                s += x[i] * S[i][j] * x[j]
    return s


def neg_directions(S):
    """Yield exact rational direction vectors x on O with x^T S x < 0 (verified).
       Sources: float eigvecs with negative eigenvalue (rationalized at several denominators),
       and exact integer search over small coordinate combos for |O|<=3."""
    k = len(S)
    out = []
    if HAVE_NP:
        Sf = np.array([[float(S[i][j]) for j in range(k)] for i in range(k)], dtype=float)
        w, V = np.linalg.eigh(Sf)
        for col in range(k):
            if w[col] < -1e-12:
                vec = V[:, col]
                for D in (2520, 720720, 232792560):
                    rx = [F(round(x * D), D) for x in vec]
                    if any(c != 0 for c in rx) and quad(S, rx) < 0:
                        out.append(('eig%d_D%d' % (col, D), rx))
                        break
    # exact small-integer search (cheap for |O|<=3)
    if k <= 3:
        rng = range(-3, 4)
        import itertools
        for combo in itertools.product(rng, repeat=k):
            if all(c == 0 for c in combo):
                continue
            x = [F(c) for c in combo]
            if quad(S, x) < 0:
                out.append(('int%s' % (combo,), x))
                if len(out) > 6:
                    break
    return out


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
    E = F(0)
    for i in range(n):
        if phi[i] == 0:
            continue
        for j in range(n):
            if H[i][j] != 0 and phi[j] != 0:
                E += phi[i] * H[i][j] * phi[j]
    return phi, E


def gamma_change(n, adj, side, gamma0, mask):
    side2 = flip_side(side, mask)
    g2 = gamma_of(n, adj, side2)
    if g2 is None:
        return None
    return g2 - gamma0


def scan_maxcut(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, mu, cyc = st
    if not M:
        return
    N = F(n)
    O = [v for v in range(n) if T[v] > N]
    if not O:
        return
    U = [v for v in range(n) if T[v] <= N]
    H = build_H(n, M, ell, T, cyc, BETA)
    S = schur_S(H, O, U)
    if S is None:
        return
    psdS, minpiv, _ = ldl_psd(S)
    acc['cuts'] += 1
    if psdS:
        acc['S_psd'] += 1
        return
    # S has a negative mode!
    acc['S_indef'] += 1
    gamma0 = gamma_of(n, adj, side)
    if gamma0 is None:
        return
    dirs = neg_directions(S)
    if not dirs:
        acc['no_negdir'] += 1
        return
    for dname, xO in dirs:
        phi, E = harmonic_extend(H, O, U, xO)
        if phi is None or E >= 0:
            continue
        # cross check E == x^T S x
        if quad(S, xO) != E:
            acc['identity_fail'] += 1
            continue
        acc['negmode_vecs'] += 1
        ts = sorted(set(phi), reverse=True)
        neutral_dGs = []
        all_dGs = []
        best_neutral = None  # (t, dG) min dG among neutral
        for t in ts:
            W = [v for v in range(n) if phi[v] > t]
            if not W or len(W) == n:
                continue
            mask = mask_of(W)
            sigma = boundary_delta(n, adj, side, mask)
            dG = gamma_change(n, adj, side, gamma0, mask)
            if dG is not None:
                all_dGs.append((t, sigma, dG))
                if sigma == 0:
                    neutral_dGs.append((t, dG))
        # does ANY neutral t have dG <= E (<0) ?
        cov_neutral = [(t, dG) for (t, dG) in neutral_dGs if dG <= E]
        # does ANY threshold (any sigma) have dG <= E ?
        cov_all = [(t, sg, dG) for (t, sg, dG) in all_dGs if dG <= E]
        if cov_neutral:
            acc['covered_neutral'] += 1
        else:
            acc['uncov_neutral'] += 1
            # record whether even any neutral t gives a strict DECREASE (dG<0)
            any_neutral_dec = any(dG < 0 for _, dG in neutral_dGs)
            if acc['uncov_ex'] is None:
                min_neu = min((dG for _, dG in neutral_dGs), default=None)
                acc['uncov_ex'] = (name, dname, str(E), str(min_neu),
                                   'neutral_exists' if neutral_dGs else 'NO_neutral',
                                   'has_neutral_decrease' if any_neutral_dec else 'no_neutral_decrease')
        if cov_all:
            acc['covered_all'] += 1
        else:
            acc['uncov_all'] += 1
            if acc['uncov_all_ex'] is None:
                min_all = min((dG for _, _, dG in all_dGs), default=None)
                acc['uncov_all_ex'] = (name, dname, str(E), str(min_all))


def scan_graph_allmax(name, n, edges, acc):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        scan_maxcut(name, n, adj, side, acc)


def new_acc():
    return dict(cuts=0, S_psd=0, S_indef=0, no_negdir=0,
                negmode_vecs=0, identity_fail=0,
                covered_neutral=0, uncov_neutral=0, uncov_ex=None,
                covered_all=0, uncov_all=0, uncov_all_ex=None)


def main():
    acc = new_acc()
    print("=" * 72)
    print("NEGATIVE-MODE descent test: find max cuts with S indefinite (E<0 possible),")
    print("then check a NEUTRAL level-set flip gives dG <= E.")
    print("=" * 72)

    # full census of triangle-free connected graphs, ALL maximum cuts
    for nn in range(5, 11):
        graphs = subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split()
        for g6 in graphs:
            n, E = dec(g6)
            scan_graph_allmax("cen%d_%s" % (nn, g6), n, E, acc)
        print("  census N=%d: cuts=%d S_indef=%d negmode_vecs=%d cov_neutral=%d uncov_neutral=%d cov_all=%d uncov_all=%d"
              % (nn, acc['cuts'], acc['S_indef'], acc['negmode_vecs'], acc['covered_neutral'],
                 acc['uncov_neutral'], acc['covered_all'], acc['uncov_all']), flush=True)

    # random triangle-free N=11,12 (more chance of indefinite S on non-gamma-min max cuts)
    rng = random.Random(20240630)
    made = 0; tries = 0
    while made < 200 and tries < 60000:
        tries += 1
        nn = rng.choice([11, 12])
        p = rng.uniform(0.14, 0.32)
        E = [(a, b) for a in range(nn) for b in range(a + 1, nn) if rng.random() < p]
        if not E or not is_triangle_free(nn, E):
            continue
        adj = adj_from_edges(nn, E)
        if any(len(adj[v]) == 0 for v in range(nn)):
            continue
        made += 1
        scan_graph_allmax("rand%d" % made, nn, E, acc)
    print("  random N11/12 scanned:", made, flush=True)
    print("  after randoms: cuts=%d S_indef=%d negmode_vecs=%d cov_neutral=%d uncov_neutral=%d cov_all=%d uncov_all=%d"
          % (acc['cuts'], acc['S_indef'], acc['negmode_vecs'], acc['covered_neutral'],
             acc['uncov_neutral'], acc['covered_all'], acc['uncov_all']), flush=True)

    print("\n" + "=" * 72)
    print("RESULTS")
    print("  O-nonempty max cuts scanned        :", acc['cuts'])
    print("  cuts with S PSD                    :", acc['S_psd'])
    print("  cuts with S INDEFINITE (neg mode)  :", acc['S_indef'])
    print("  indef cuts w/ no exact neg-dir     :", acc['no_negdir'])
    print("  E<0 test vectors built             :", acc['negmode_vecs'])
    print("  E==x^T S x identity FAILS          :", acc['identity_fail'])
    print("-" * 72)
    print("  NEUTRAL level-set covers (dG<=E<0) :", acc['covered_neutral'])
    print("  NEUTRAL uncovered                  :", acc['uncov_neutral'], acc['uncov_ex'] or '')
    print("  ANY-threshold covers (dG<=E<0)     :", acc['covered_all'])
    print("  ANY-threshold uncovered            :", acc['uncov_all'], acc['uncov_all_ex'] or '')
    print("=" * 72)
    if acc['negmode_vecs'] == 0:
        print("VERDICT: NO indefinite-S max cut found in this battery -- S>=0 even off gamma-min here; "
              "the level-set estimate cannot be falsified or confirmed for lack of a negative mode.")
    elif acc['uncov_neutral'] == 0:
        print("VERDICT: descent estimate HOLDS on every negative mode -- a NEUTRAL level-set flip achieves "
              "dG<=E<0 => closing rule confirmed.")
    elif acc['uncov_all'] == 0:
        print("VERDICT: NEUTRAL-only level-set is INSUFFICIENT but SOME (non-neutral) threshold gives dG<=E. "
              "The closing rule needs a non-neutral/relaxed flip, not the pure neutral level set.")
    else:
        print("VERDICT: descent estimate FALSE as stated -- some E<0 vector has NO threshold (neutral or not) "
              "with dG<=E. Level-set/coarea bound dG<=phi^T H phi does NOT hold in general. See uncov_all_ex.")


if __name__ == "__main__":
    main()
