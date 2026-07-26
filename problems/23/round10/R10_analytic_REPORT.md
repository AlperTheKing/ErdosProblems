# Round 10 analytic arc-bound branch

## Scope and status

This branch tested the registered `ARCBOUND_Gamma11` frontier

    min_{4 <= |I| <= 7, I a cyclic interval} q_I(x) <= (sum_i x_i)^2/25

for the 11-vertex circulant graph with edge differences 4 and 5.  It did not
prove or disprove the inequality.  The branch status is **BLOCKED**: the one
permitted sign-plus-maximum refinement still has 451 unresolved leaves, so no
further comparison hierarchy is started here.

All LP feasibility statements below are floating-point diagnostics unless the
word `exact` is explicit.  In particular, the 1111 base certificates and 1089
refined certificates have not been reconstructed over the rationals and are
not a proof of the corresponding cases.

## Viability and an exact sharpness witness

The 22-cut length-4/5 inequality itself remains viable: this work found no
counterexample.  With `sum x_i=1`, 75 deterministic SLSQP starts reported a
largest local value `0.040000000000`; this is steering evidence, not a global
upper bound.

There is an exact equality witness:

    x_i = 1/5 for i in {0,1,4,5,8}, and x_i=0 otherwise.

The support edges are `(0,4),(0,5),(1,5),(1,8),(4,8)`.  Exact enumeration of
all 22 length-4/5 arc cuts gives values in `{1/25,3/25}` and minimum `1/25`.
Thus the max-min is at least `1/25`, so the proposed upper bound is sharp if
true.  The numerical search found no value above `1/25`, but it does not prove
that none exists.

## Exact local identities

Write `A_i=q_{i,4}`, `B_i=q_{i,5}`, with indices modulo 11, and put
`p_i=x_{i-3}+x_{i-2}+x_{i-1}`.  Direct expansion gives

    B_i = x_i x_{i+4} + x_{i+5} x_{i+9} + x_{i+5} x_{i+10}
          + x_{i+6} x_{i+10},

    A_i = x_{i+4} x_{i+8} + x_{i+4} x_{i+9} + x_{i+4} x_{i+10}
          + x_{i+5} x_{i+9} + x_{i+5} x_{i+10}
          + x_{i+6} x_{i+10},

and hence the exact factorization

    A_i - B_i = x_{i+4}(p_i-x_i).

The exact checker verifies all 11 identities coefficient by coefficient.
Thus a mask bit `i=1` means `p_i-x_i >= 0` and selects `B_i`; a zero bit
selects `A_i`.

## Exact obstruction to the coarse degree-2 ansatz

On `C_0={x>=0, x_0>=x_i}`, the coarse ansatz sought

    L^2/25 - sum_A lambda_A q_A
      = sum_{r<=s} mu_rs g_r g_s,

where `lambda` is a probability distribution on all 22 length-4/5 cuts and
the generators are `x_i` and `x_0-x_i`.  The exact checker supplies a Farkas
separator.  Its nonzero quadratic moments are

    ell(x_0^2)=2,
    ell(x_0 x_j)=1  (j>0),
    ell(x_i x_j)=1  for (i,j) in
      {(1,6),(1,8),(2,6),(2,9),(3,7),(3,10),(4,8),(5,9),(6,10)}.

Together with coefficient `-3` on `sum lambda_A=1`, every cut-column slack
and every generator-product slack is nonnegative, whereas the target slack is

    ell(L^2)/25 - 3 = 40/25 - 3 = -7/5.

Therefore this particular coarse degree-2 Handelman identity is exactly
infeasible.  This is an obstruction to the ansatz, not to `ARCBOUND_Gamma11`.

## Exhaustive sign-cone diagnostic

The 2048 sign masks split as follows:

| class | masks | rotation orbits |
|---|---:|---:|
| empty | 771 | 71 |
| floating degree-2 feasible | 1111 | 101 |
| unresolved | 166 | 16 |

The 16 unresolved representatives under rotation alone are

    0x1bf 0x1df 0x1ef 0x1f7 0x1ff 0x2bf 0x2df 0x2ef
    0x2f7 0x2ff 0x377 0x37f 0x3bf 0x3df 0x3ff 0x7ff.

Only cyclic rotation is used.  Ordinary reflection is not used because it
does not preserve the paired ordered family `(A_i,B_i)` without an additional
proof.  The earlier 14-representative reflection reduction is invalid and is
superseded by the 16 representatives above.

## One maximum-coordinate refinement

For each of the 166 unresolved masks and each possible maximum coordinate,
the refined cone adds `x_m-x_j>=0` for every `j`.  The 1826 leaves split as

| class | leaves |
|---|---:|
| empty | 286 |
| floating degree-2 feasible | 1089 |
| unresolved | 451 |

Every unresolved `(mask,maximum)` pair is recorded verbatim in
`R10_analytic_signmax.log`.  This is the direct-guard exit condition for this
analytic subroute.

## Higher-degree floating diagnostics

At degree 3, floating feasibility was reported for `0x1bf`, `0x1df`,
`0x1ef`, `0x1f7`, and `0x2df`.  HiGHS reported infeasibility for `0x2bf`,
`0x2ef`, `0x2f7`, `0x2ff`, `0x377`, `0x3bf`, and `0x3df`; it returned an
unknown status for `0x1ff`, `0x37f`, `0x3ff`, and `0x7ff` in the unscaled
formulation.  At degree 4, `0x1ff` was floating feasible; `0x2bf`, `0x2ef`,
`0x2ff`, `0x377`, `0x37f`, `0x3bf`, `0x3df`, `0x3ff`, and `0x7ff` reached the
60-second limit.  Degree 4 was not run for `0x2f7`.  None of these floating
outcomes is an exact certificate.

## Replay

From the repository root:

    python problems/23/round10/R10_analytic_handelman_obstruction.py
    python problems/23/round10/R10_analytic_signcones.py
    python problems/23/round10/R10_analytic_signmax.py > problems/23/round10/R10_analytic_signmax.log
    python problems/23/round10/R10_analytic_signcone_higher.py --degree 3 --mask 0x1bf
    python problems/23/round10/R10_analytic_signcone_higher.py --degree 4 --mask 0x1ff

The first command is the exact replay.  The remaining commands require
NumPy/SciPy and reproduce floating diagnostics; the full sign-plus-maximum
run may take several minutes.
