"""Broaden the indefinite-S evidence base for the descent inequality.

_descent_anyflip_gate found indef-S only on one census graph (H?AFBo], N=9). To make the
descent-inequality verdict robust we HUNT for more indefinite-S O-nonempty max cuts across:
  - denser random triangle-free graphs N=11..16,
  - non-uniform odd-cycle blow-ups of C5 / C7,
  - C5[t] uniform blow-ups, Mycielski(C5)=Grotzsch, Mycielski(Grotzsch)=N23.
For EVERY indefinite-S cut found we run the EXACT descent-inequality check:
  for every E<0 integer direction x (|x_o|<=3) with x^T S x<0, does the BEST neutral B-connected
  Gamma-descent satisfy dG <= E ?   (and the stronger ALL-neutral form).
0-fail or first counterexample.  EXACT Fraction.

Run:  python _descent_indef_hunt.py
"""
import subprocess, random, itertools
from fractions import Fraction as F

from _h import dec, GENG, Bconn, maxcut_all
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, mycielski, is_triangle_free
from _hardy_gate import BETA, build_H, maxcut_ls
from _schur_overload_gate import solve_exact, submatrix, matmul, ldl_psd
from _codex_k2t_switch_probe import adj_from_edges, flip_side, boundary_delta, gamma_of
from _stark1 import odd_blowup


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


def neg_dirs(S, lim=3):
    k = len(S)
    if k > 4:  # limit blow-up of the product
        lim = 2
    out = []
    for combo in itertools.product(range(-lim, lim + 1), repeat=k):
        if all(c == 0 for c in combo):
            continue
        x = [F(c) for c in combo]
        if quad(S, x) < 0:
            out.append(combo)
    return out


def neutral_descents(n, adj, side, gamma0):
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


def scan(name, n, adj, side, acc):
    if n > 22:  # exhaustive neutral-descent search is 2^n; cap to keep exact & finite
        return
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
    acc['indef_names'].add(name.split('|')[0])
    gamma0 = gamma_of(n, adj, side)
    if gamma0 is None:
        return
    nds = neutral_descents(n, adj, side, gamma0)
    min_dG = nds[0][1] if nds else None
    for combo in neg_dirs(S):
        xO = [F(c) for c in combo]
        E = quad(S, xO)
        acc['negvecs'] += 1
        if min_dG is None:
            acc['no_neutral'] += 1
            if acc['nn_ex'] is None:
                acc['nn_ex'] = (name, combo, str(E))
            continue
        if min_dG <= E:
            acc['ok'] += 1
        else:
            acc['fail'] += 1
            if acc['fail_ex'] is None:
                acc['fail_ex'] = (name, ''.join(map(str, side)), combo, str(E), str(min_dG))
        if all(dG <= E for _, dG in nds):
            acc['all_le'] += 1
        else:
            acc['some_gt'] += 1


def scan_graph(name, n, edges, acc):
    if n > 22:
        return
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        scan(name + "|" + ''.join(map(str, side)), n, adj, side, acc)


def new_acc():
    return dict(cuts=0, indef=0, indef_names=set(), negvecs=0,
                no_neutral=0, nn_ex=None, ok=0, fail=0, fail_ex=None,
                all_le=0, some_gt=0)


def main():
    acc = new_acc()
    print("=" * 72)
    print("INDEF-S HUNT + descent inequality (min neutral dG <= E=x^T S x)")
    print("=" * 72)

    # dense random triangle-free, N=11..16
    rng = random.Random(987654321)
    made = 0; tries = 0
    while made < 1500 and tries < 400000:
        tries += 1
        nn = rng.choice([11, 12, 13, 14, 15, 16])
        p = rng.uniform(0.18, 0.40)
        E = [(a, b) for a in range(nn) for b in range(a + 1, nn) if rng.random() < p]
        if not E or not is_triangle_free(nn, E):
            continue
        adj = adj_from_edges(nn, E)
        if any(len(adj[v]) == 0 for v in range(nn)):
            continue
        made += 1
        scan_graph("rnd%d_N%d" % (made, nn), nn, E, acc)
        if made % 300 == 0:
            print("   ...random %d done: indef=%d negvecs=%d ok=%d fail=%d no_neutral=%d"
                  % (made, acc['indef'], acc['negvecs'], acc['ok'], acc['fail'], acc['no_neutral']), flush=True)
    print("  random scanned:", made, " (graphs w/ indef-S so far:", len(acc['indef_names']), ")", flush=True)

    # non-uniform odd-cycle blow-ups of C5 (where omega-STAR-O1 historically died)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(3,2,3,2,3),(4,3,4,3,4),(3,1,3,1,3),
                  (4,1,4,1,4),(2,1,3,1,2),(3,2,2,1,3),(2,2,3,1,2),(4,2,3,1,3)]:
        nn, EE, adj, side0 = odd_blowup(5, list(sizes))
        if nn <= 22:
            scan_graph("blowC5%s" % (sizes,), nn, EE, acc)
    # C7 non-uniform
    for sizes in [(2,1,1,1,1,1,1),(2,1,2,1,2,1,1),(2,1,1,1,2,1,1)]:
        nn, EE, adj, side0 = odd_blowup(7, list(sizes))
        if nn <= 22:
            scan_graph("blowC7%s" % (sizes,), nn, EE, acc)

    # Grotzsch N=11 and one apex max-cut at N=23 (size cap excludes N=23 from neutral search; just Grotzsch)
    grN, grE = mycielski(5, Cn(5))
    scan_graph("Grotzsch_N11", grN, grE, acc)

    print("\n" + "=" * 72)
    print("RESULTS")
    print("  O-nonempty max cuts             :", acc['cuts'])
    print("  indefinite-S cuts               :", acc['indef'])
    print("  distinct graphs with indef-S    :", len(acc['indef_names']))
    print("  E<0 direction vectors tested    :", acc['negvecs'])
    print("  indef-S cuts w/ NO neutral desc :", acc['no_neutral'], acc['nn_ex'] or '')
    print("-" * 72)
    print("  INEQ  min_neutral dG <= E PASS  :", acc['ok'])
    print("  INEQ  FAILURES (dG > E)         :", acc['fail'], acc['fail_ex'] or '')
    print("  (stronger) ALL neutral dG<=E    :", acc['all_le'])
    print("  (stronger) SOME neutral dG>E    :", acc['some_gt'])
    print("=" * 72)
    if acc['negvecs'] == 0:
        print("VERDICT: still no indefinite-S site -- S>=0 on every cut in this enlarged battery too "
              "(S>=0 may be far more robust than gamma-min alone; descent inequality remains lightly tested).")
    elif acc['fail'] == 0 and acc['no_neutral'] == 0:
        print("VERDICT: descent inequality min_neutral dG<=E HOLDS 0-FAIL across the enlarged indef-S battery.")
    else:
        print("VERDICT: descent inequality VIOLATED or vacuous -- see fail_ex / nn_ex.")


if __name__ == "__main__":
    main()
