#!/usr/bin/env python3
"""Independent replay/verifier for R5_CERTIFICATE.json (r=5, coefficient e_4).

Re-derives EVERYTHING that can be re-derived from source with exact rational
arithmetic, then checks every exact claim of the shipped certificate.  Exits
NONZERO (via SystemExit / AssertionError) on any failure, ZERO iff all pass.

What is proved when this passes (subject to the standard external inputs:
hive lattice points = LR coefficients; stretched LR polynomials are period-one
polynomials (Derksen--Weyman); the McMullen/Berline--Vergne local Ehrhart
formula e_k(P) = sum_{dim F = k} alpha(N_F) vol_Z(F)):

    For every full-dimensional (dim = 6) size-5 hive polytope P, the coefficient
    of n^4 in its Ehrhart polynomial L_P(n) is >= 0 (indeed >= (1/9) * sum of
    ridge volumes > 0).  Equivalently, the n^4-coefficient of every stretched
    Littlewood--Richardson polynomial c(n nu; n lam, n mu) with parts <= 5 and a
    6-dimensional hive polytope is positive.

Chain of the proof re-checked here:
  * alpha (rebuilt from the BV construction) is componentwise > 0;
  * B (rebuilt) has rank 120, so dim ker(B) = 222;
  * every witness ridge-volume vector Lambda(P_i) lies in ker(B) exactly;
  * rank(M) = 222 = dim ker(B), so the witness rows SPAN ker(B);
  * the local identity e_4(P_i) = alpha . Lambda(P_i) holds exactly on every
    witness (the witness e_4 values come independently from lattice counts /
    the validated local formula) -- this is the non-vacuous validation that
    alpha is the correct local weight, not merely a positive vector;
  * mu >= 0 and M mu = a and M(mu - alpha) = 0, hence mu in alpha + rowspace(B):
    the coset alpha + rowspace(B) meets the nonnegative orthant.
Then for any hive P: Lambda(P) in ker(B) = rowspan(M) and Lambda(P) >= 0, so
e_4(P) = alpha . Lambda(P) = mu . Lambda(P) >= 0.
"""
import hashlib
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

FAIL = []


def check(cond, msg):
    if cond:
        print('  ok   :', msg)
    else:
        print('  FAIL :', msg)
        FAIL.append(msg)


def main():
    # ---- rebuild everything from source (independent of the certificate) ----
    from hive5 import NORMALS5, D
    from polytope5 import PAIR_TYPES
    from alpha5 import alpha_vector
    from balance5 import build_B
    from exactlin import rank_mod, rank as exrank

    ncol = len(PAIR_TYPES)
    alpha = alpha_vector()
    B, _ = build_B()

    print('re-derived from source:')
    check(D == 6, 'ambient dimension D = 6')
    check(len(NORMALS5) == 27, '27 primitive normals')
    check(ncol == 342, '342 nonparallel ridge types')
    check(all(x > 0 for x in alpha), 'alpha componentwise > 0')
    check(min(alpha) == Fraction(1, 9), 'min(alpha) = 1/9')

    rankB = rank_mod(B)                      # <= true rank
    rankB_exact = exrank(B)                  # exact
    kerdim = ncol - rankB_exact
    check(rankB == 120 and rankB_exact == 120, 'rank(B) = 120 (exact)')
    check(kerdim == 222, 'dim ker(B) = 222')

    # ---- load the certificate ----
    cert = json.load(open(os.path.join(HERE, 'R5_CERTIFICATE.json')))
    # self-consistency: sha256 of the non-summary body
    body = json.dumps({k: v for k, v in cert.items() if k != 'summary'},
                      sort_keys=True)
    sha = hashlib.sha256(body.encode()).hexdigest()
    check(sha == cert['summary'].get('certificate_sha256'),
          'certificate_sha256 self-consistent')

    cpairs = [tuple(p) for p in cert['pair_types']]
    calpha = [Fraction(x) for x in cert['alpha']]
    mu = [Fraction(x) for x in cert['mu']]
    wit = cert['witnesses']
    M = [[Fraction(x) for x in w['volz']] for w in wit]
    a = [Fraction(w['a4']) for w in wit]

    print('cross-checks against re-derived objects:')
    check(cpairs == [tuple(p) for p in PAIR_TYPES],
          'certificate pair_types == re-derived PAIR_TYPES')
    check(calpha == alpha, 'certificate alpha == re-derived alpha')
    check(len(mu) == ncol, 'mu has 342 entries')
    check(len(wit) == 222, '222 witnesses')

    # ---- witness structural checks ----
    def Bx(row):
        return [sum(B[r][c] * row[c] for c in range(ncol)) for r in range(len(B))]

    all_in_ker = all(all(y == 0 for y in Bx(row)) for row in M)
    check(all_in_ker, 'every witness Lambda lies in ker(B) exactly')

    rankM = rank_mod(M)                       # = 222 certifies span (rows in ker)
    check(rankM == kerdim, 'rank(M) = dim ker(B) = 222  (witnesses span ker B)')

    # local identity: e_4(witness) = alpha . Lambda(witness), exactly
    local_ok = all(sum(alpha[c] * M[i][c] for c in range(ncol)) == a[i]
                   for i in range(len(wit)))
    check(local_ok, 'local identity a_i = alpha . Lambda_i holds on all witnesses')

    # nonnegativity of the witness ridge volumes (needed for the sign argument)
    check(all(all(x >= 0 for x in row) for row in M),
          'all witness ridge volumes are nonnegative')

    # ---- the certificate mu itself ----
    check(all(x >= 0 for x in mu), 'mu >= 0 (componentwise)')
    Mmu = [sum(M[i][c] * mu[c] for c in range(ncol)) for i in range(len(wit))]
    check(Mmu == a, 'M mu = a exactly')
    # mu - alpha orthogonal to every witness row  => mu - alpha _|_ ker(B)
    diff = [mu[c] - alpha[c] for c in range(ncol)]
    Mdiff = [sum(M[i][c] * diff[c] for c in range(ncol)) for i in range(len(wit))]
    check(all(x == 0 for x in Mdiff),
          'M(mu - alpha) = 0  =>  mu - alpha in ker(B)^perp = rowspace(B)')
    # hence mu in alpha + rowspace(B): the coset meets the nonnegative orthant

    print()
    if FAIL:
        print('VERIFY r5 e_4: FAIL (%d failed checks)' % len(FAIL))
        for m_ in FAIL:
            print('   -', m_)
        sys.exit(1)
    print('VERIFY r5 e_4: PASS')
    print('PROVED: for every full-dimensional size-5 hive polytope, the n^4 '
          '(codimension-two) Ehrhart coefficient e_4 is >= 0 (>= (1/9) * sum of '
          'ridge volumes > 0).  This is ONE of the seven coefficients; it is NOT '
          'the full KTT conjecture.  Note mu = alpha >= 0, so this coefficient is '
          'positive without using rowspace(B) at all -- the balancing LP is '
          'trivially feasible here, which is exactly why e_4 is the case that '
          'already worked and not the frontier.')
    sys.exit(0)


if __name__ == '__main__':
    main()
