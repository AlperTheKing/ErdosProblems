# R10 D22-reduced degree-4 arc-certificate experiment

## Scope

This experiment targets only the registered frontier

`ARCBOUND_Gamma_11(x) <= (sum x)^2 / 25`

with the 56 cyclic-interval cuts.  It does not prove Erdős Problem #23 or the
registered minimum-degree corollary unless an exact certificate passes the
independent arithmetic gate.

## Lossless reduction

`CODEX_R10_g11_d22_sdp.py` fixes `c=25` and uses degree-4
coefficientwise-nonnegative multipliers.  It identifies:

- multiplier coefficients in the same D22 orbit of
  `(arc cut, degree-4 monomial)`;
- parity Gram blocks in the same D22 orbit;
- symmetric entries in the same stabilizer orbit inside each representative
  Gram block; and
- coefficient equations in the same degree-4 or degree-6 monomial orbit.

This restriction is lossless: the 56-cut family and the polynomial identities
are D22-invariant, and averaging any feasible certificate preserves
coefficientwise nonnegativity and positive semidefiniteness.  Expansion uses
only coordinate permutations and writes the standard Q4 certificate layout.

## Build result

Command:

```text
python problems/23/round10/CODEX_R10_g11_d22_sdp.py
```

Result:

```text
graph=Gamma_11 vertices=11 edges=22 group_order=22 cuts=56
degree4_monomials=1001 multiplier_orbit_scalars=2611
normalization_orbit_equations=56
degree6_monomials=8008 target_orbit_equations=392
parity_block_orbits=52 gram_orbit_scalars=8647
representative_psd_orders={286: 1, 66: 5, 11: 20, 1: 26}
normalization_nnz=2611 multiplier_target_nnz=25626 gram_target_nnz=8647
BUILD_ONLY: no numerical feasibility claim
```

## Numerical solve

Command:

```text
python problems/23/round10/CODEX_R10_g11_d22_sdp.py --solve --solver CLARABEL --tol 1e-7 --max-iter 500
```

Result after 1626.563 seconds:

```text
status=optimal_inaccurate
normalization_max_abs_residual=2.072713526502e-05
target_max_abs_residual=3.453911682527e-05
minimum_multiplier=0
minimum_representative_gram_eigenvalue=-6.538181519338e-07
maximum_stabilizer_error=0
```

The expanded warm start is
`CODEX_R10_g11_d22_numeric.pkl`.  It is explicitly marked
`NUMERICAL_ONLY=True`.

## Independent expanded-object audit

Command:

```text
python problems/23/round10/CODEX_R10_g11_d22_numeric_gate.py
```

Result:

```text
G1_G2_OK edges=22 cuts=56
G3_G4_NUMERIC min_nu=1.290712750697e-09 normalization_residual=2.072713526502e-05
G5_G6_NUMERIC blocks=848 identity_residual=3.453911683593e-05
minimum_eigenvalue=-6.538181630119e-07
NUMERICAL_AUDIT_ONLY: exact rational gate still required
```

Thus the D22 expansion is internally consistent, but the returned iterate is
not a certificate.

## Exact induced-C5 face audit

Command:

```text
python problems/23/round10/CODEX_R10_c5_face_audit.py
```

Result:

```text
C5_TIGHTNESS_OK cycles=33 arc_minimum=1 tight_cut_count_range=24..25
MULTIPLIER_FACE forced_zero_orbits=1147/2611
max_abs_forced=5.553442204604e-06 orbit_tie_error=0
CENTRAL_FACE exact_kernel_rank=33 block_order=286
max_abs_QK=9.797149744156e-03 inf_norm_QK=1.211303995512e-01
CENTRAL_SPECTRUM min_eigenvalue=-5.094568219423e-07
nullity_at_1e-5=16 forced_nullity_lower_bound=33
```

For each induced C5 support `U`, tightness gives `T(1_U)=0`.  Hence every exact
PSD Gram block must kill its evaluation vector.  In the parity-zero block the
33 evaluation vectors have exact rational rank 33.  The raw numerical block
does not lie near this mandatory face: it has only 16 eigenvalues below
`1e-5`, and `max |QK|` is about `9.8e-3`.  Therefore entrywise rational
rounding of this iterate is invalid.

The same equality argument forces 1,147 of the 2,611 multiplier-orbit
coefficients to zero: whenever an arc cut has `q_S(1_U)>1`,
coefficientwise nonnegativity and `nu_S(1_U)=0` kill every multiplier
monomial supported inside `U`.

## Current exact status

No exact primal identity or exact separating dual has been produced.  The
numerical result is `BLOCKED`, not `DEAD`, under the registered exit rule.
The only justified next step is to impose the exact induced-C5 multiplier and
Gram face before any further feasibility computation, then reconstruct
Fractions and run `Q4_verify.verify(..., d=2)` plus an independent root gate.
The raw warm start must remain unchanged.

## SHA-256

```text
AB2F222EAE5052FD3DCD64311D05419E4150759C1DB4BD33E5AE30D313CDFEEE  CODEX_R10_g11_d22_sdp.py
BCE4332520667F6B23D404191413C520598F8DDF5C911CA162D7E015E068EDDF  CODEX_R10_g11_d22_numeric.pkl
F822CCC5E2275033B945D64533CA649898D4033E4B48BF7B9E38DB9CB1451702  CODEX_R10_g11_d22_numeric_gate.py
227B16DC4501C12F390FECC61DE0417A39E52E7632D9EB179A537DC4CFCD917E  CODEX_R10_c5_face_audit.py
```
