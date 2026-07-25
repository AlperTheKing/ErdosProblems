#!/usr/bin/env python3
"""Run the r=5 codimension-two (e_4) nonnegativity LP EXACTLY.

Question (King--Tollu--Toumazet local-Ehrhart route, coefficient e_4):
    does the coset  alpha + rowspace(B)  contain a componentwise-nonnegative
    vector mu?  Equivalently, is there  mu >= 0  with  M mu = a  on the witness
    set whose rows Lambda(P_i) span ker(B)?

Here
    * B      = codim-2 ridge balancing matrix (405 x 342), built from source;
    * alpha  = 342-vector of Berline--Vergne ridge weights, built from source;
    * M      = 222 x 342 matrix whose rows are the witness ridge-volume vectors
               Lambda(P_i) (they span ker(B), rank 222 = dim ker B);
    * a       = M alpha  = the vector of witness e_4 values.

If mu >= 0 solves M mu = a, then (since a = M alpha) M(mu-alpha)=0, so
mu-alpha _|_ rowspan(M) = ker(B), i.e. mu in alpha + rowspace(B): the coset
contains the nonnegative vector mu.  For ANY hive polytope P, Lambda(P) in
ker(B) = rowspan(M), so mu . Lambda(P) = alpha . Lambda(P) = e_4(P), and both
mu >= 0 and Lambda(P) >= 0 give e_4(P) >= 0.

All arithmetic is exact (fractions.Fraction).  Floating point never decides.
"""
import hashlib
import json
import os
import sys
import time
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from alpha5 import alpha_vector          # noqa: E402  (rebuilt from source)
from balance5 import build_B             # noqa: E402  (rebuilt from source)
from polytope5 import PAIR_TYPES         # noqa: E402
from exactlin import solve_nonneg, rank_mod  # noqa: E402


def matvec_rows(rows, x):
    return [sum(r[c] * x[c] for c in range(len(x))) for r in rows]


def main():
    t0 = time.time()
    ncol = len(PAIR_TYPES)               # 342
    alpha = alpha_vector()               # exact, from source
    B, _ = build_B()                     # exact, from source
    assert len(alpha) == ncol

    # ---- load the witness set (M rows = Lambda(P_i), and a_i = e_4(P_i)) ----
    cert = json.load(open(os.path.join(HERE, 'e4_certificate.json')))
    wit = cert['witnesses']
    M = [[Fraction(x) for x in w['volz']] for w in wit]      # 222 x 342
    a = [Fraction(w['a4']) for w in wit]                     # 222
    m = len(M)
    print('witnesses = %d, ridge types = %d' % (m, ncol), flush=True)

    # ---- structural facts we depend on (exact) ----
    # (1) every witness Lambda lies in ker(B):
    in_ker = all(all(y == 0 for y in matvec_rows(B, row)) for row in M)
    # (2) rows of M span ker(B): rank(M) == dim ker(B). rank(B)=120 => ker=222.
    rankB = rank_mod(B)
    kerdim = ncol - rankB
    rankM = rank_mod(M)
    spans_ker = (rankM == kerdim and in_ker)
    # (3) local identity a = M alpha  (a_i = alpha . Lambda_i):
    a_from_alpha = [sum(alpha[c] * M[i][c] for c in range(ncol)) for i in range(m)]
    a_eq_Malpha = (a_from_alpha == a)
    print('rank(B) = %d, dim ker(B) = %d, rank(M) = %d, M spans ker(B) = %s'
          % (rankB, kerdim, rankM, spans_ker), flush=True)
    print('all witness Lambda in ker(B) = %s' % in_ker, flush=True)
    print('a == M.alpha (local identity) = %s' % a_eq_Malpha, flush=True)
    assert in_ker and spans_ker and a_eq_Malpha, 'structural preconditions failed'

    # ---- EXACT LP VERDICT via a constructive feasible point -----------------
    # alpha itself is an exact, componentwise-nonnegative solution of M mu = a
    # (this IS the LP being feasible: a rational feasible point is a complete,
    # exact proof that {mu >= 0 : M mu = a} is nonempty, i.e. that the coset
    # alpha + rowspace(B) meets the nonnegative orthant).  No floating point.
    alpha_nonneg = all(x >= 0 for x in alpha)
    alpha_feasible = alpha_nonneg and a_eq_Malpha
    print('alpha >= 0 and M.alpha = a  (alpha is an exact feasible point) = %s'
          % alpha_feasible, flush=True)
    assert alpha_feasible, 'alpha is not a feasible point -- unexpected'
    lp_feasible = True

    # ---- optional independent corroboration: exact phase-1 simplex ----------
    mu_lp = None
    simplex_status = 'not_run'
    if '--simplex' in sys.argv:
        print('running exact rational phase-1 simplex (independent) ...',
              flush=True)
        Acols = [[M[i][j] for i in range(m)] for j in range(ncol)]
        mu_lp = solve_nonneg(Acols, a)   # exact; None iff infeasible
        if mu_lp is None:
            raise SystemExit('CONTRADICTION: exact simplex reported INFEASIBLE '
                             'but alpha is an exact nonnegative solution '
                             '-> solver bug; refusing to emit certificate')
        assert all(x >= 0 for x in mu_lp), 'simplex mu has a negative entry'
        assert matvec_rows(M, mu_lp) == a, 'simplex mu fails M mu = a exactly'
        simplex_status = 'feasible_confirmed'
        print('exact simplex independently returned a nonnegative solution '
              '[%.1fs]' % (time.time() - t0), flush=True)

    # canonical shipped mu = alpha (strictly positive, fully reproducible)
    mu = list(alpha)
    assert matvec_rows(M, mu) == a and all(x >= 0 for x in mu)

    out = {
        'coefficient': 'e_4',
        'r': 5,
        'question': 'does alpha + rowspace(B) contain a nonnegative vector mu? '
                    '(equiv. mu>=0 with M mu = a on witnesses spanning ker B)',
        'outcome': 'FEASIBLE',
        'ncol_ridge_types': ncol,
        'n_witnesses': m,
        'rank_B': rankB,
        'dim_ker_B': kerdim,
        'rank_M': rankM,
        'M_rows_span_ker_B': spans_ker,
        'all_witness_lambda_in_ker_B': in_ker,
        'a_equals_M_alpha_local_identity': a_eq_Malpha,
        'lp_feasible': lp_feasible,
        'feasibility_proof': 'constructive exact nonnegative point (mu=alpha)',
        'exact_simplex_status': simplex_status,
        'alpha_is_feasible_point': alpha_feasible,
        'mu_source': 'alpha (canonical, strictly positive)',
        'mu_min': str(min(mu)),
        'mu_all_nonneg': all(x >= 0 for x in mu),
        'mu_all_positive': all(x > 0 for x in mu),
        'M_mu_equals_a': matvec_rows(M, mu) == a,
    }
    R5 = {
        'summary': out,
        'pair_types': [list(p) for p in PAIR_TYPES],
        'alpha': [str(x) for x in alpha],
        'mu': [str(x) for x in mu],
        'mu_simplex': ([str(x) for x in mu_lp] if mu_lp is not None else None),
        'a': [str(x) for x in a],
        'witnesses': wit,
    }
    body = json.dumps({k: v for k, v in R5.items() if k != 'summary'},
                      sort_keys=True)
    out['certificate_sha256'] = hashlib.sha256(body.encode()).hexdigest()
    with open(os.path.join(HERE, 'R5_CERTIFICATE.json'), 'w') as f:
        json.dump(R5, f, indent=1)
    print(json.dumps(out, indent=1))
    print('wrote R5_CERTIFICATE.json  [%.1fs total]' % (time.time() - t0))


if __name__ == '__main__':
    main()
