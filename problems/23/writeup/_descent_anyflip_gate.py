"""DECISIVE test of the descent INEQUALITY (not the level-set construction).

_descent_indef_inspect showed: on indefinite-S max cuts (NON-gamma-min), the harmonic-extension
LEVEL SETS W={phi>t} are the WRONG switch family -- they are non-neutral and disconnect B.
BUT a genuine neutral B-connected Gamma-DECREASING flip exists, and on the N=9 site it gives
dG=-24 <= E=phi^T H phi (~ -12.97).

So the operative closing claim is the INEQUALITY, with the witness flip allowed to be ANY neutral
B-connected switch (found exhaustively), not necessarily a phi level set:

    for every E<0 direction x on O,  min over neutral B-connected flips W of  dG(W)  <=  E = x^T S x.

This gate verifies that EXACTLY on EVERY indefinite-S max cut over the census (N<=10) and random
N=11/12 triangle-free graphs, for EVERY exact integer negative direction x (|x_o|<=4) with x^T S x<0.
We report 0-fail or the first (cut, x, E, best neutral dG) where dG > E.

Also reports: do ALL neutral descents satisfy dG<=E (stronger), or only the best one (the min)?

EXACT Fraction.   Run:  python _descent_anyflip_gate.py
"""
import subprocess, random, itertools
from fractions import Fraction as F

from _h import dec, GENG, Bconn, maxcut_all
from _satzmu_conn import struct_for_side
from _bdef_construct import is_triangle_free
from _hardy_gate import BETA, build_H
from _schur_overload_gate import solve_exact, submatrix, matmul, ldl_psd
from _codex_k2t_switch_probe import adj_from_edges, flip_side, boundary_delta, gamma_of


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


def neg_dirs_exact(S, rng_lim=4):
    k = len(S)
    out = []
    for combo in itertools.product(range(-rng_lim, rng_lim + 1), repeat=k):
        if all(c == 0 for c in combo):
            continue
        x = [F(c) for c in combo]
        if quad(S, x) < 0:
            out.append(combo)
    return out


def neutral_descents(n, adj, side, gamma0):
    """exhaustive: all nonempty proper W, neutral (sigma==0), B-conn after flip, dG<0. returns sorted [(mask,dG)]."""
    res = []
    full = (1 << n) - 1
    for mask in range(1, full):
        if boundary_delta(n, adj, side, mask) != 0:
            continue
        side2 = flip_side(side, mask)
        g2 = gamma_of(n, adj, side2)
        if g2 is None:
            continue
        dG = g2 - gamma0
        if dG < 0:
            res.append((mask, dG))
    res.sort(key=lambda z: z[1])
    return res


def scan(name, n, adj, side, acc, neutral_cache):
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
    psd, _, _ = ldl_psd(S)
    acc['cuts'] += 1
    if psd:
        return
    acc['indef'] += 1
    gamma0 = gamma_of(n, adj, side)
    if gamma0 is None:
        return
    nds = neutral_descents(n, adj, side, gamma0)
    min_neutral_dG = nds[0][1] if nds else None
    # negative directions and their E
    H_UU = submatrix(H, U, U); H_UO = submatrix(H, U, O)
    for combo in neg_dirs_exact(S):
        xO = [F(c) for c in combo]
        E = quad(S, xO)
        # harmonic extension just to double-check E (phi^T H phi == x^T S x) on a sample
        acc['negvecs'] += 1
        if min_neutral_dG is None:
            # indefinite S but NO neutral B-connected Gamma-descent at all -> estimate would be vacuous/violated
            acc['no_neutral_descent'] += 1
            if acc['nn_ex'] is None:
                acc['nn_ex'] = (name, combo, str(E))
            continue
        # the INEQUALITY: best (min) neutral dG <= E ?
        if min_neutral_dG <= E:
            acc['ineq_ok'] += 1
        else:
            acc['ineq_fail'] += 1
            if acc['fail_ex'] is None:
                acc['fail_ex'] = (name, ''.join(map(str, side)), combo, str(E), str(min_neutral_dG))
        # stronger: do ALL neutral descents satisfy dG<=E ?  (would let us pick ANY)
        if all(dG <= E for _, dG in nds):
            acc['all_le'] += 1
        else:
            acc['some_gt'] += 1


def scan_graph(name, n, edges, acc):
    adj = adj_from_edges(n, edges)
    nc = {}
    for side in maxcut_all(n, adj):
        scan(name, n, adj, side, acc, nc)


def new_acc():
    return dict(cuts=0, indef=0, negvecs=0, no_neutral_descent=0, nn_ex=None,
                ineq_ok=0, ineq_fail=0, fail_ex=None, all_le=0, some_gt=0)


def main():
    acc = new_acc()
    print("=" * 72)
    print("DESCENT INEQUALITY (any neutral B-conn flip):  min_neutral dG <= E = x^T S x  (E<0)")
    print("=" * 72)
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            scan_graph("cen%d_%s" % (nn, g6), n, E, acc)
        print("  census N=%d: cuts=%d indef=%d negvecs=%d ineq_ok=%d ineq_fail=%d no_neut_desc=%d all_le=%d some_gt=%d"
              % (nn, acc['cuts'], acc['indef'], acc['negvecs'], acc['ineq_ok'], acc['ineq_fail'],
                 acc['no_neutral_descent'], acc['all_le'], acc['some_gt']), flush=True)

    rng = random.Random(31337)
    made = 0; tries = 0
    while made < 300 and tries < 100000:
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
        scan_graph("rand%d" % made, nn, E, acc)
    print("  random N11/12 scanned:", made, flush=True)

    print("\n" + "=" * 72)
    print("RESULTS")
    print("  O-nonempty max cuts             :", acc['cuts'])
    print("  indefinite-S cuts               :", acc['indef'])
    print("  E<0 direction vectors tested    :", acc['negvecs'])
    print("  indef-S cuts w/ NO neutral desc :", acc['no_neutral_descent'], acc['nn_ex'] or '')
    print("-" * 72)
    print("  INEQ  min_neutral dG <= E  PASS :", acc['ineq_ok'])
    print("  INEQ  FAILURES (dG > E)         :", acc['ineq_fail'], acc['fail_ex'] or '')
    print("  (stronger) ALL neutral dG<=E    :", acc['all_le'])
    print("  (stronger) SOME neutral dG>E    :", acc['some_gt'])
    print("=" * 72)
    if acc['negvecs'] == 0:
        print("VERDICT: no indefinite-S / negative-mode site arose; inequality untested.")
    elif acc['ineq_fail'] == 0 and acc['no_neutral_descent'] == 0:
        print("VERDICT: DESCENT INEQUALITY HOLDS 0-FAIL -- on every indefinite-S max cut, every E<0 direction "
              "admits a NEUTRAL B-connected Gamma-descent with dG<=E<0. (Witness is generally NOT a phi level set: "
              "the closing lemma is the INEQUALITY min_neutral dG<=x^T S x, with the flip found by some other rule.)")
    elif acc['no_neutral_descent'] > 0:
        print("VERDICT: COUNTEREXAMPLE to the route -- an indefinite-S cut has NO neutral B-connected Gamma-descent "
              "at all, so x^T S x<0 cannot be converted to a neutral descent. See nn_ex.")
    else:
        print("VERDICT: INEQUALITY FALSE -- some E<0 direction has best neutral dG > E. The descent bound "
              "dG<=phi^T H phi does not hold even with the optimal neutral flip. See fail_ex.")


if __name__ == "__main__":
    main()
