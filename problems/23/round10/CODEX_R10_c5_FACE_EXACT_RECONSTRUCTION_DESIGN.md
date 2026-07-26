# Sparse exact reconstruction of a future positive plateau-face point

## Fixed scope

This protocol keeps the registered ansatz unchanged:

- `c=25`;
- multiplier degree 4;
- all 56 cyclic-interval cuts of `Gamma_11`;
- lossless `D22` invariance;
- 526 live multiplier-orbit variables and 2,085 exact forced zeros;
- the exact Gram face `Hq=0`, with `H` of rank 6,129;
- the unchanged exact quotient PSD cones.

It does not run an SDP and it does not modify a solver.  It describes how to
turn a future strictly positive numerical iterate into a rational candidate
and exactly accept or reject that candidate.

## Pinned structural artifacts

```text
F5B8BA8B0D2460E8A8ACDB3841464E4984FCEB4B0E45A7926B4D3B4203AC205C  CODEX_R10_c5_FACE_ROW_REDUCTION_data.npz
2F82F46A5C740164D47AB74F532C8D7BBED3AE97270894A18BA04D8F78DFF8D2  CODEX_R10_c5_FACE_REPAIR_MAP_data.npz
3B120381926290147890ABC7BA2A50B85532F93F751B961A79F81653F6AC3730  CODEX_R10_BLOWUP_FACE_data.npz
08DC9A3A4A8B5931B67B128CB7FD393EA126BA233CDC208A3675CB650C4FDA0F  CODEX_R10_c5_FACE_EQUALITY_data.npz
```

The row-reduction artifact supplies the exact 388-row affine system

`A_nu nu + A_gram q = b`.

The repair-map artifact supplies:

- 322 selected live multiplier coordinates;
- 66 primitive integer Gram directions, assembled as an
  `8647 x 66` sparse matrix `D`;
- the exact square matrix
  `M=[A_nu[:,J], A_gram D]`, of order 388.

The 66 directions are stabilizer Reynolds averages of exact quotient matrix
units:

`primitive_integer(Reynolds(B E_ab B^T))`.

Consequently `H D=0` exactly and every direction is `D22`-invariant.  The
matrix `M` has rank 388 modulo 1,000,003, 2,000,003, and 998,244,353, hence is
invertible over `Q`.  No affine projector is needed.

## Preconditions on the numerical point

The input is steering evidence only.  It must contain:

- 526 finite live multiplier values;
- 8,647 finite representative Gram-orbit values, or the equivalent
  representative matrices;
- positive numerical live-multiplier margin;
- positive numerical eigenvalue margin on every nonempty quotient principal
  block;
- small residuals for the 388 affine equations, `Hq=0`, and stabilizer
  invariance.

These checks reject corrupt or boundary input early.  They are not proof
checks.

## Phase A: exact binary centering

1. Convert each input IEEE-754 value to its exact binary `Fraction`; do not
   use decimal text as an unrecorded approximation.

2. For representative Gram block `i`, rebuild its exact kernel matrix `U_i`.
   Choose the pinned pivot columns `P_i`, with complement `C_i`, and form

   `B_i[P_i,:] = -U_i[:,P_i]^{-1} U_i[:,C_i]`,
   `B_i[C_i,:] = I`.

3. Read the numerical quotient principal matrix
   `R_i=Q_i[C_i,C_i]`, symmetrize it exactly, lift
   `Q_i=B_i R_i B_i^T`, and average its full matrix over the exact stabilizer.
   This enforces `U_i Q_i=0` and stabilizer invariance exactly.  Read the
   invariant orbit values to obtain `q_binary`.

4. Form the exact rational residual

   `r = b - A_nu nu_binary - A_gram q_binary`.

5. Solve the square integer system

   `M delta = r`

   by fraction-free exact elimination (`DomainMatrix.solve_den` or an
   equivalent exact sparse solve).  Do not form `M^{-1}` and do not form a
   dense projector.

6. Apply the first 322 entries of `delta` to the selected multiplier
   coordinates and the remaining 66 through `D`:

   `nu_center[J] += delta_nu`,
   `q_center += D delta_gram`.

7. Check exactly:

   `A_nu nu_center + A_gram q_center = b`,
   `H q_center=0`.

Because the repair directions stay in `ker H`, centering cannot leave the
exact Gram face.

8. Run exact nonnegativity and quotient-PSD checks on the centered point.  If
   every live multiplier and every nonempty quotient block is positive
   definite, the centered point is an exact relative-interior certificate,
   although its binary denominators may be large.  If it is not inside the
   relative interior, stop and request a more accurate positive numerical
   iterate; changing the denominator cannot repair a bad center.

## Phase B: compact denominator refinement

For `D_k=10^k`, beginning with a recorded user-selected exponent and increasing
it monotonically:

1. Round all 526 centered live multipliers to denominator `D_k`.

2. For each block, round the upper triangle of the centered quotient matrix
   `R_i` to denominator `D_k`, reflect it symmetrically, lift with the exact
   `B_i`, and Reynolds-average the lift.  This gives a rational
   kernel-preserving, invariant `q_k`.

3. Form the exact residual and solve `M delta_k=r_k` exactly.

4. Apply the sparse coordinate repair.

5. Accept this denominator only if every acceptance gate below passes.
   Otherwise increase `k`.

This loop is finite under the stated strict-interior precondition.  The
rounded point converges to the exact centered point, its affine residual tends
to zero, and the fixed linear repair tends to zero.  Strict multiplier
positivity and strict quotient positive definiteness are open conditions.

## Mandatory exact acceptance gates

### G1. Artifact and ordering gate

- Match all pinned SHA-256 hashes.
- Rebuild `Gamma_11`, the 56 cuts, the monomial orders, multiplier-pair
  orbits, parity blocks, Gram entry orbits, and all stored row/column orders.

### G2. Multiplier gate

- All 526 live orbit values are exact `Fraction`s and nonnegative.
- The 2,085 forced orbit values expand as exact zeros.
- Expansion through the multiplier pair-orbit table is exactly `D22`
  invariant.

### G3. Face and affine gate

- `Hq=0` exactly.
- All 388 retained affine rows hold exactly.
- Replay all 448 original normalization and target rows directly.  Do not
  rely only on the 60 dependency records at final acceptance.

### G4. Quotient and full-Gram gate

For every representative block:

- verify stabilizer invariance entry-by-entry;
- verify `Q U^T=0` exactly;
- verify `Q=B Q[C,C] B^T` exactly;
- run exact symmetric-pivoted `LDL^T` on `Q[C,C]`;
- require positive semidefiniteness.

The congruence identity proves the full representative matrix is PSD.  Expand
all `D22` parity-orbit copies and verify their exact permutations.

### G5. Standard Q4 gate

Construct a `Fraction`-valued standard Q4 payload and call

`problems/23/round7/Q4_verify.verify`

with `n=11`, `d=2`, and `c=25`.  It must pass V1--V4, including its own
expanded exact coefficient identity and full exact PSD replay.

### G6. Independent root replay

A separate program that imports neither the reconstruction code nor its
constructor must rebuild:

- the graph and cuts;
- degree-4 and degree-6 monomials;
- the full multiplier normalization;
- the full polynomial coefficient identity;
- every expanded Gram block;
- exact nonnegativity and PSD.

Only agreement of G1--G6 promotes the file from numerical steering evidence
to an exact certificate.

## Failure semantics

- A failed finite denominator attempt means only “increase the denominator.”
- Failure of the exact binary-centered point to remain strictly inside the
  cones means “obtain a more accurate positive numerical iterate.”
- Failure of any exact identity, invariance, kernel, PSD, or Q4 replay is a
  hard rejection of that rational candidate.
- No failed reconstruction attempt is evidence for or against the underlying
  theorem.

## Scope boundary

This protocol proves only that a successfully gated rational payload is an
exact certificate for the fixed `Gamma_11`, `c=25`, degree-4, 56-cut Q4
ansatz.  Until a future numerical point is reconstructed and all gates pass,
there is no certificate and no theorem claim.
