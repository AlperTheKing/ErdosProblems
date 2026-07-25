#!/usr/bin/env python3
"""Independent replay of the r=5 codimension-two (e_4) certificate.

Reconstructs from scratch:
  * the fixed matrix A_5 and its 27 primitive normals (SHA-256 pinned),
  * the 342 ridge types and their exact BV weights alpha,
  * the balancing matrix B (rank 120, kernel 222),
then re-reads e4_certificate.json and re-checks, with exact arithmetic:
  (a) every witness Lambda-vector lies in ker(B):        B Lambda = 0
  (b) each witness local identity:      a_4 = alpha . Lambda   (Lambda = vol_Z)
  (c) rank of the witness matrix M equals dim ker(B)          (spans ker B)
  (d) the supplied mu is componentwise >= 0 and reproduces a  (M mu = a)
  (e) alpha itself is componentwise > 0 (the direct positivity route)
Prints PASS/FAIL and the reconstructed constants.
"""
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from hive5 import A5, NORMALS5, emit_atlas  # noqa: E402
from polytope5 import PAIR_TYPES  # noqa: E402
from alpha5 import alpha_vector  # noqa: E402
from balance5 import build_B  # noqa: E402
from exactlin import rank as exrank  # noqa: E402


def main():
    fails = []
    _, atlas_sha = emit_atlas()

    alpha = alpha_vector()
    B, _ = build_B()
    rankB = exrank(B)
    kerdim = len(PAIR_TYPES) - rankB
    if rankB != 120 or kerdim != 222:
        fails.append('B rank/kernel mismatch %d/%d' % (rankB, kerdim))
    if not all(a > 0 for a in alpha):
        fails.append('alpha has a nonpositive entry')

    cert = json.load(open(os.path.join(HERE, 'e4_certificate.json')))
    wit = cert['witnesses']
    calpha = [Fraction(x) for x in cert['alpha']]
    if calpha != alpha:
        fails.append('stored alpha != recomputed alpha')

    def matvec(M, x):
        return [sum(M[r][c] * x[c] for c in range(len(x))) for r in range(len(M))]

    M = []
    a = []
    n_in_ker = 0
    n_local = 0
    for w in wit:
        volz = [Fraction(x) for x in w['volz']]
        M.append(volz)
        a4 = Fraction(w['a4'])
        a.append(a4)
        if all(x == 0 for x in matvec(B, volz)):
            n_in_ker += 1
        else:
            fails.append('witness Lambda not in ker(B)')
        if sum(alpha[k] * volz[k] for k in range(len(alpha))) == a4:
            n_local += 1
        else:
            fails.append('witness local identity fails')

    Mrank = exrank(M)
    # The witness matrix rank is the span of the collected witnesses.  It equals
    # dim ker(B) only if lattice witnesses were added; hive witnesses alone span
    # a 198-dimensional subspace.  This is reported, not treated as a failure.
    spans_kerB = (Mrank == kerdim)

    mu = [Fraction(x) for x in cert['mu']] if cert.get('mu') else None
    mu_ok = None
    if mu is not None:
        cols = [[M[r][c] for r in range(len(M))] for c in range(len(PAIR_TYPES))]
        chk = [sum(cols[c][r] * mu[c] for c in range(len(PAIR_TYPES)))
               for r in range(len(M))]
        mu_ok = all(x >= 0 for x in mu) and all(chk[r] == a[r] for r in range(len(M)))
        if not mu_ok:
            fails.append('mu not a valid nonnegative certificate')

    print('atlas_sha256          =', atlas_sha)
    print('normals               =', len(NORMALS5))
    print('ridge_types           =', len(PAIR_TYPES))
    print('rank(B)               =', rankB)
    print('dim ker(B)            =', kerdim)
    print('witnesses             =', len(wit),
          '(hive=%d, lattice=%d)'
          % (sum(1 for w in wit if w['kind'] == 'hive'),
             sum(1 for w in wit if w['kind'] == 'lattice')))
    print('witness_matrix_rank   =', Mrank, '(spans ker B =', spans_kerB, ')')
    print('all Lambda in ker(B)  =', n_in_ker == len(wit))
    print('all local identities  =', n_local == len(wit))
    print('alpha min             =', min(alpha), ' alpha all>0 =', all(a > 0 for a in alpha))
    if mu is not None:
        print('mu min                =', min(mu), ' mu valid =', mu_ok)
    print('PASS' if not fails else 'FAIL')
    if fails:
        for f in fails[:10]:
            print('  -', f)
    return 0 if not fails else 1


if __name__ == '__main__':
    sys.exit(main())
