# 3 by 3 Magic Square of Distinct Positive Squares — Approach Registry

Selected: 2026-07-21
Status: ACTIVE — direct construction route
Initial attack tranche: 8 hours

## Exact target

Determine whether there is a 3 by 3 array of nine distinct positive integer
squares whose three row sums, three column sums, and two diagonal sums are
equal. The constructive target is the current theorem
MagicSquares.exists_magic_square_squares in Google DeepMind Formal
Conjectures.

## DIRECT ROUTE

### 1. Exact final deliverable

Produce nine distinct positive integers r_ij and an integer S such that the
array (r_ij^2) has all eight line sums equal to S. Verify the certificate with:

1. a standalone exact-integer scalar verifier;
2. an independently implemented verifier using a different data layout; and
3. a Lean proof of the concrete witness and the exact Formal Conjectures
   existential statement, without sorry or native_decide.

A bounded search result, a rational square with nonintegral roots, a repeated
entry, or a seven-line near miss is not the final deliverable.

### 2. Current frontier lemma or finite certificate

For a positive square A = m^2, define

    D_A = {d > 0 : A-d and A+d are positive integer squares}.

The finite frontier certificate MSQ-D is a triple of positive integers
(m,b,c) such that b, c, b+c, and |b-c| all belong to D_(m^2), and the nine
values in the matrix below are positive and pairwise distinct. Membership in
D_A is certified by eight integer square roots.

### 3. Explicit logical bridge

Put A = m^2 and substitute the certificate into

    [ A-b,   A+b+c, A-c   ]
    [ A+b-c, A,     A-b+c ]
    [ A+c,   A-b-c, A+b   ]

The four D_A memberships make all four opposite pairs positive integer
squares; the center is the square m^2. Direct addition shows that every row,
column, and main diagonal has sum 3A. Positivity and pairwise distinctness
give exactly the target. Thus one verified MSQ-D certificate closes the
existence question, with no asymptotic or limiting step.

Equivalently, Bremner's elliptic formulation uses
E_c : y^2 = x(x^2-c^2): the three terms X-c, X, X+c are rational squares
exactly when a point with x-coordinate X lies in 2E_c(Q). Three suitable
doubled points with x-coordinates in arithmetic progression yield the same
finite square certificate after clearing denominators. This formulation is
permitted only when a lane emits the exact MSQ-D data.

### 4. Next falsifiable action

First build the two exact verifiers and reproduce both a valid general magic
square and a published seven-of-eight square near miss. Then freeze a manifest
of 64 distinct finite lanes:

- 16 exact Gaussian-factorization searches for centers m;
- 16 elliptic point-addition and exact-reconstruction lanes on fixed curves;
- 16 finite near-miss completion or algebraic-parameter lanes; and
- 16 independent structural lanes seeking an identity that emits MSQ-D.

The four available research agents rotate through 16 lanes each. CPU searches
may use at most 64 workers in aggregate. Every lane has an explicit finite
parameter range or a finite symbolic ansatz before execution. The initial
tranche ends after eight wall-clock hours. A candidate is accepted only after
both exact verifiers agree.

### 5. Exit condition

Stop immediately on a dual-verified MSQ-D certificate and perform the novelty
gate before any solution claim. At eight hours, stop every lane that has
produced neither an exact certificate nor a theorem-closing identity. Record
only NO_HIT for the declared finite lane ranges; do not infer nonexistence.
Do not extend an exhausted range, add an equivalent parameterization, or
replace the target with a density or asymptotic surrogate. If no direct lane
remains, mark this route DEAD and return to candidate selection.

## Current-status and priority snapshot

- Peter Müller, Acta Arithmetica 222.1 (2026), explicitly states that the
  size-3 magic square of squares problem remains open:
  https://doi.org/10.4064/aa250422-2-8
- Andrew Bremner, On squares of squares, Acta Arithmetica 88 (1999), gives
  the magic-square normal form and elliptic-curve bridge used here:
  https://matwbn.icm.edu.pl/ksiazki/aa/aa88/aa8837.pdf
