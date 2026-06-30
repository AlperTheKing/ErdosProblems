"""CRUX EXPERIMENT: the level-set DESCENT ESTIMATE for the Schur negative-mode argument.

Setting (all exact Fraction). For an O-nonempty gamma-min connected-B max cut:
  H = D_{N-T} + Lstar   (build_H, certified rational beta').
  O = {v: T_v>N}, U = rest.  S = H_OO - H_OU H_UU^{-1} H_UO   (Schur on O).
Given a test vector x supported on O, harmonically extend:
  phi_O = x_O,   phi_U = -H_UU^{-1} H_UO x_O      (exact via solve_exact)
so that  E := phi^T H phi = x_O^T S x_O   (verified exactly).

The CRUX claim (descent estimate): a level-set flip W = {v : phi(v) > t} for the right
threshold t is a NEUTRAL (cut-size preserving) Gamma-DECREASING switch with
       dG(W) := Gamma(flip W) - Gamma   <=   E = phi^T H phi.
If true for all x with the right t, then S has no negative mode (x^T S x<0 would force a
neutral strict Gamma-decrease, contradicting gamma-min) => S>=0 => (H) => #23.

This script tests, on N=23 apex + ~30 other O-nonempty gamma-min cuts, for several test
vectors x (basis e_o, min-eigvec direction of S, random +-1):
  (i)   exists a NEUTRAL t (sigma=0) with dG <= E exactly?
  (ii)  over ALL neutral t, is min dG <= E?
  (iii) discrete coarea sum_t dG(t)*(t-gap) vs E?
and searches for a threshold RULE t*(phi) with dG<=E always (0-fail).

EXACT Fraction for every pass/fail.  Run:  python _descent_levelset_gate.py
"""
import subprocess, random
from fractions import Fraction as F

from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import Cn, mycielski
from _hardy_gate import BETA, build_H, maxcut_ls
from _schur_overload_gate import solve_exact, submatrix, matmul, ldl_psd
from _codex_k2t_switch_probe import adj_from_edges, flip_side, boundary_delta, gamma_of

try:
    import numpy as np
    HAVE_NP = True
except Exception:
    HAVE_NP = False


def c5_blowup(t):
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


def mask_of(verts):
    m = 0
    for v in verts:
        m |= 1 << v
    return m


def harmonic_extend(H, O, U, xO):
    """phi (length n) with phi_O = xO, phi_U = -H_UU^{-1} H_UO xO.  Exact.
       Returns (phi list over original indices, E = phi^T H phi)."""
    n = len(H)
    H_UU = submatrix(H, U, U)
    H_UO = submatrix(H, U, O)
    # rhs column: -(H_UO xO)  (length |U|)
    rhs = [F(0)] * len(U)
    for i in range(len(U)):
        s = F(0)
        for k in range(len(O)):
            s += H_UO[i][k] * xO[k]
        rhs[i] = -s
    sol = solve_exact(H_UU, [rhs])  # one column
    if sol is None:
        return None, None
    phiU = sol[0]
    phi = [F(0)] * n
    for idx, o in enumerate(O):
        phi[o] = xO[idx]
    for idx, u in enumerate(U):
        phi[u] = phiU[idx]
    # E = phi^T H phi  (exact)
    E = F(0)
    for i in range(n):
        if phi[i] == 0:
            continue
        for j in range(n):
            if H[i][j] != 0 and phi[j] != 0:
                E += phi[i] * H[i][j] * phi[j]
    return phi, E


def schur_S(H, O, U):
    """S = H_OO - H_OU H_UU^{-1} H_UO  (exact), or None if H_UU singular."""
    H_OO = submatrix(H, O, O)
    H_OU = submatrix(H, O, U)
    H_UO = submatrix(H, U, O)
    H_UU = submatrix(H, U, U)
    cols = [[H_UO[i][c] for i in range(len(U))] for c in range(len(O))]
    X = solve_exact(H_UU, cols)
    if X is None:
        return None
    Xm = [[X[c][i] for c in range(len(O))] for i in range(len(U))]
    HOU_X = matmul(H_OU, Xm)
    S = [[H_OO[i][j] - HOU_X[i][j] for j in range(len(O))] for i in range(len(O))]
    return S


def min_eigvec_rational(S):
    """Float min-eigenvector of S, rationalized to small-denominator Fraction vector (a DIRECTION).
       Returns list of Fraction over O-index, or None."""
    if not HAVE_NP:
        return None
    k = len(S)
    Sf = np.array([[float(S[i][j]) for j in range(k)] for i in range(k)], dtype=float)
    w, V = np.linalg.eigh(Sf)
    vec = V[:, 0]
    # rationalize with denominator 720720 (=lcm small), keep as direction
    D = 720720
    out = [F(round(x * D), D) for x in vec]
    if all(c == 0 for c in out):
        return None
    return out


def thresholds(phi):
    """distinct phi values, sorted descending; level sets W={v:phi(v)>t}."""
    return sorted(set(phi), reverse=True)


def gamma_change(n, adj, side, gamma0, mask):
    side2 = flip_side(side, mask)
    g2 = gamma_of(n, adj, side2)
    if g2 is None:
        return None  # disconnected/invalid => +inf
    return g2 - gamma0


def analyze_cut(name, n, adj, side, acc):
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
        acc['UU_singular'] += 1
        return
    gamma0 = gamma_of(n, adj, side)
    if gamma0 is None:
        return
    acc['cuts'] += 1
    acc['O_sizes'][len(O)] = acc['O_sizes'].get(len(O), 0) + 1

    # build test vectors xO on O
    vecs = []
    for idx in range(len(O)):
        e = [F(0)] * len(O)
        e[idx] = F(1)
        vecs.append(('e_%d' % O[idx], e))
    mv = min_eigvec_rational(S)
    if mv is not None:
        vecs.append(('mineig', mv))
        vecs.append(('-mineig', [-c for c in mv]))
    rng = random.Random(hash(name) & 0xffff)
    for r in range(3):
        pm = [F(rng.choice([-1, 1])) for _ in range(len(O))]
        vecs.append(('pm%d' % r, pm))

    for vname, xO in vecs:
        phi, E = harmonic_extend(H, O, U, xO)
        if phi is None:
            continue
        # cross-check E == xO^T S xO
        xSx = F(0)
        for i in range(len(O)):
            for j in range(len(O)):
                xSx += xO[i] * S[i][j] * xO[j]
        if xSx != E:
            acc['identity_fail'] += 1
            if acc['identity_ex'] is None:
                acc['identity_ex'] = (name, vname, str(E), str(xSx))
        acc['vecs'] += 1
        is_negmode = (E < 0)
        if is_negmode:
            acc['negmodes'] += 1

        ts = thresholds(phi)
        # for each threshold t (strict >), level set W
        neutral_dGs = []   # dG for neutral t (sigma==0), W nonempty/nonfull
        all_records = []   # (t, sigma, dG)
        for t in ts:
            W = [v for v in range(n) if phi[v] > t]
            if not W or len(W) == n:
                continue
            mask = mask_of(W)
            sigma = boundary_delta(n, adj, side, mask)  # dB - dM >=0 since max cut; neutral iff 0
            dG = gamma_change(n, adj, side, gamma0, mask)
            all_records.append((t, sigma, dG))
            if sigma == 0:
                neutral_dGs.append((t, dG))

        # (i)/(ii): over neutral thresholds, is there one with dG <= E ? min over neutral?
        valid_neutral = [(t, dG) for (t, dG) in neutral_dGs if dG is not None]
        if valid_neutral:
            acc['have_neutral'] += 1
            min_dG = min(dG for _, dG in valid_neutral)
            if min_dG <= E:
                acc['neutral_min_le_E'] += 1
            else:
                acc['neutral_min_gt_E'] += 1
                if is_negmode and acc['negmode_fail_ex'] is None:
                    acc['negmode_fail_ex'] = (name, vname, str(E), str(min_dG))
            # for negmode specifically: descent estimate REQUIRES some neutral strict decrease (dG<0<... wait E<0)
            if is_negmode:
                # need neutral t with dG <= E (<0) => strict Gamma decrease
                if any(dG <= E for _, dG in valid_neutral):
                    acc['negmode_covered'] += 1
                else:
                    acc['negmode_uncovered'] += 1
                    if acc['negmode_unc_ex'] is None:
                        acc['negmode_unc_ex'] = (name, vname, str(E),
                                                 str(min(dG for _, dG in valid_neutral)))
        else:
            acc['no_neutral'] += 1
            if is_negmode:
                acc['negmode_no_neutral'] += 1

        # candidate threshold RULES: evaluate dG<=E for specific t* choices (over ALL t, not just neutral)
        # Rule A: t* = 0  (W = {phi>0})
        # Rule B: t* = median split that is neutral and gives smallest dG among neutral (oracle)
        # Rule C: the threshold achieving min dG over ALL thresholds (oracle, ignoring neutrality)
        for rule_name, recs in [
            ('t=0', [(t, sg, dG) for (t, sg, dG) in all_records if t == F(0)]),
        ]:
            for (t, sg, dG) in recs:
                key = rule_name
                acc['rule_eval'].setdefault(key, dict(tot=0, le=0, gt=0, neutral=0, neutral_le=0))
                d = acc['rule_eval'][key]
                d['tot'] += 1
                if sg == 0:
                    d['neutral'] += 1
                if dG is not None and dG <= E:
                    d['le'] += 1
                    if sg == 0:
                        d['neutral_le'] += 1
                else:
                    d['gt'] += 1

        # ORACLE min over ALL thresholds (any t, ignoring sigma): is min dG <= E ?
        valid_all = [dG for (_, _, dG) in all_records if dG is not None]
        if valid_all:
            if min(valid_all) <= E:
                acc['oracle_all_le'] += 1
            else:
                acc['oracle_all_gt'] += 1
                if acc['oracle_gt_ex'] is None:
                    acc['oracle_gt_ex'] = (name, vname, str(E), str(min(valid_all)))
        # ORACLE min over NEUTRAL only already handled above (neutral_min_le_E)

        # (iii) discrete coarea: sum over consecutive thresholds of dG(t)*(gap) -- rough BV check.
        # Use level sets at each distinct value; gap = t_k - t_{k+1}. Compare to E.
        # (diagnostic only; report coarea_sum vs E sign agreement)
        if len(ts) >= 2 and is_negmode:
            coarea = F(0)
            for kk in range(len(ts) - 1):
                t = ts[kk]
                gap = ts[kk] - ts[kk + 1]
                W = [v for v in range(n) if phi[v] > t]
                if not W or len(W) == n:
                    continue
                dG = gamma_change(n, adj, side, gamma0, mask_of(W))
                if dG is None:
                    coarea = None
                    break
                coarea += dG * gap
            if coarea is not None:
                acc['coarea_samples'] += 1
                if coarea <= E:
                    acc['coarea_le_E'] += 1


def gfam(name, n, E, acc):
    adj, cuts = gmins(n, E)
    for side in cuts:
        analyze_cut(name, n, adj, side, acc)


def new_acc():
    return dict(
        cuts=0, vecs=0, negmodes=0, identity_fail=0, identity_ex=None,
        UU_singular=0, O_sizes={},
        have_neutral=0, no_neutral=0,
        neutral_min_le_E=0, neutral_min_gt_E=0, negmode_fail_ex=None,
        negmode_covered=0, negmode_uncovered=0, negmode_unc_ex=None, negmode_no_neutral=0,
        oracle_all_le=0, oracle_all_gt=0, oracle_gt_ex=None,
        coarea_samples=0, coarea_le_E=0,
        rule_eval={},
    )


def main():
    acc = new_acc()
    print("=" * 72)
    print("LEVEL-SET DESCENT ESTIMATE  dG(W={phi>t}) <= E=phi^T H phi  (exact)")
    print("=" * 72)

    # N=23 apex (Myc(Grotzsch)) FIRST
    grN, grE = mycielski(5, Cn(5))
    m2N, m2E = mycielski(grN, grE)
    adj = adj_from_edges(m2N, m2E)
    side = maxcut_ls(m2N, adj)
    if Bconn(m2N, adj, side):
        print("N=23 apex cut side =", ''.join(map(str, side)), flush=True)
        analyze_cut("MycGrotzsch_N23", m2N, adj, side, acc)
        print("  after N=23: cuts=%d vecs=%d negmodes=%d neutral_min_le_E=%d neutral_min_gt_E=%d oracle_all_gt=%d"
              % (acc['cuts'], acc['vecs'], acc['negmodes'], acc['neutral_min_le_E'],
                 acc['neutral_min_gt_E'], acc['oracle_all_gt']), flush=True)

    # census N=9,10 O-nonempty gamma-min cuts
    for nn in (9, 10):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            gfam("cen%d_%s" % (nn, g6), n, E, acc)
        print("  after census N=%d: cuts=%d vecs=%d negmodes=%d neutral_min_gt_E=%d oracle_all_gt=%d"
              % (nn, acc['cuts'], acc['vecs'], acc['negmodes'], acc['neutral_min_gt_E'],
                 acc['oracle_all_gt']), flush=True)

    # a C5 blowup (C5[2] N=10, C5[3] N=15)
    for t in (2, 3):
        n, E = c5_blowup(t)
        gfam("C5[%d]" % t, n, E, acc)
    print("  after C5 blowups: cuts=%d vecs=%d negmodes=%d" % (acc['cuts'], acc['vecs'], acc['negmodes']), flush=True)

    print("\n" + "=" * 72)
    print("RESULTS")
    print("  O-nonempty gamma-min cuts analyzed :", acc['cuts'], " O-size hist:", dict(sorted(acc['O_sizes'].items())))
    print("  H_UU singular skips                :", acc['UU_singular'])
    print("  test vectors evaluated             :", acc['vecs'])
    print("  E<0 (negative-mode) vectors        :", acc['negmodes'])
    print("  E == x^T S x identity FAILURES     :", acc['identity_fail'], acc['identity_ex'] or '')
    print("-" * 72)
    print("  (i)/(ii) NEUTRAL-threshold descent:")
    print("    vectors with >=1 valid neutral t :", acc['have_neutral'])
    print("    vectors with NO neutral t        :", acc['no_neutral'])
    print("    min over neutral dG  <= E        :", acc['neutral_min_le_E'])
    print("    min over neutral dG  >  E (FAIL) :", acc['neutral_min_gt_E'], acc['negmode_fail_ex'] or '')
    print("-" * 72)
    print("  NEGATIVE-MODE coverage (the actual contradiction needed):")
    print("    negmode vectors                  :", acc['negmodes'])
    print("    covered (neutral t with dG<=E<0) :", acc['negmode_covered'])
    print("    UNCOVERED (no neutral dG<=E)     :", acc['negmode_uncovered'], acc['negmode_unc_ex'] or '')
    print("    negmode with NO neutral t at all :", acc['negmode_no_neutral'])
    print("-" * 72)
    print("  ORACLE min dG over ALL thresholds (any sigma):")
    print("    min-all-dG <= E                  :", acc['oracle_all_le'])
    print("    min-all-dG >  E (FAIL)           :", acc['oracle_all_gt'], acc['oracle_gt_ex'] or '')
    print("-" * 72)
    print("  (iii) coarea sum_t dG*gap <= E (negmode samples):", acc['coarea_le_E'], "/", acc['coarea_samples'])
    print("-" * 72)
    print("  THRESHOLD RULES (dG<=E hit rate over all eval'd vectors):")
    for k, d in sorted(acc['rule_eval'].items()):
        print("    rule %-6s : tot=%d  dG<=E=%d  dG>E=%d  | neutral=%d neutral&dG<=E=%d"
              % (k, d['tot'], d['le'], d['gt'], d['neutral'], d['neutral_le']))
    print("=" * 72)
    # VERDICT focuses on whether the descent estimate (some neutral t, dG<=E) holds for ALL negmode vectors.
    closing = (acc['negmode_uncovered'] == 0 and acc['negmode_no_neutral'] == 0
               and acc['identity_fail'] == 0 and acc['negmodes'] > 0)
    if acc['negmodes'] == 0:
        print("VERDICT: NO negative-mode test vector arose (S>=0 on all tested gamma-min cuts) -- "
              "descent estimate UNTESTED on a real contradiction; need a constructed negmode probe.")
    elif closing:
        print("VERDICT: descent estimate HOLDS -- every E<0 vector admits a NEUTRAL level-set flip with dG<=E<0 "
              "(strict Gamma decrease) => contradiction with gamma-min => S>=0. CLOSING RULE candidate found.")
    else:
        print("VERDICT: descent estimate FAILS as stated -- some E<0 vector has NO neutral level-set t with dG<=E. "
              "The naive level-set threshold rule does NOT close S>=0; see negmode_unc_ex.")


if __name__ == "__main__":
    main()
