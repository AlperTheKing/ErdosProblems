# Exact reconstruction of a future plateau-face semantic dual

## Fixed scope

This protocol stays on the registered direct route and changes no part of the
ansatz:

- `Gamma_11 = And(4)`;
- `c=25`;
- degree-4 multipliers;
- all 56 cyclic-interval cuts;
- lossless `D22` invariance;
- the exact C5 plateau face `Hq=0`;
- 526 live and 2,085 forced-zero multiplier orbits;
- the same 16 scalar and 26 matrix quotient cones.

It is a reconstruction and verification path for a future numerical archive
written by `CODEX_R10_c5_FACE_REDUCED_SDP_SCS_DUAL.py`.  It does not run a
solver.  No such numerical archive was processed while preparing or gating
this protocol.

## Pinned inputs

```text
B0C4A2EB4D50C21A6DEB1F0D83D1327546793D6B1D9B10DE9E92DABC7E6C168A  CODEX_R10_c5_FACE_REDUCED_SDP_SCS_DUAL.py
F5B8BA8B0D2460E8A8ACDB3841464E4984FCEB4B0E45A7926B4D3B4203AC205C  CODEX_R10_c5_FACE_ROW_REDUCTION_data.npz
EA9BE7AEC38FCF14470FEC1D36210FB25C4AAEFF9CE7A49C1B171CE42C02E34C  CODEX_R10_c5_FACE_KERNEL_PARAMETERIZATION_data.npz
3B120381926290147890ABC7BA2A50B85532F93F751B961A79F81653F6AC3730  CODEX_R10_BLOWUP_FACE_data.npz
08DC9A3A4A8B5931B67B128CB7FD393EA126BA233CDC208A3675CB650C4FDA0F  CODEX_R10_c5_FACE_EQUALITY_data.npz
AB2F222EAE5052FD3DCD64311D05419E4150759C1DB4BD33E5AE30D313CDFEEE  CODEX_R10_g11_d22_sdp.py
```

The exact verifier and its independent default-path gate are:

```text
9366CCD624C32CAC644D9E6DE79F17EA758450893EAE77D935A2AFFE42F72A60  CODEX_R10_c5_FACE_EXACT_DUAL_VERIFIER.py
F8FC2F0AE3B005AD584C00668D6740F219A8633A1C8C41516F3313E6F8B5A623  CODEX_R10_c5_FACE_EXACT_DUAL_VERIFIER_GATE.py
```

## Exact primal and cone maps

Write the reduced exact primal variables as

```text
u in R^526, q in ker(H) subset R^8647, t in R.
```

The retained affine equations are

```text
A_u u + A_q q = b                                      (P1)
```

with 388 rows.  For each nonempty quotient block `k`, let `P_k(q)` be
the exact principal quotient matrix formed with the pinned block offset,
free-coordinate list, and Gram-entry orbit IDs.  Order-one blocks are written
as the scalar `p_k(q)`.  The conic inequalities are

```text
u_i - t >= 0                          for i=1,...,526,   (P2)
t >= 0,                                                   (P3)
p_k(q) - t >= 0                       for 16 blocks,     (P4)
P_k(q) - t I >=_PSD 0                 for 26 blocks.     (P5)
```

The primal objective is to maximize `t`.

Let `Z` be the sealed integer `8647 x 2518` basis.  The exact gates

```text
rank(H)=6129, rank(Z)=2518, HZ=0
```

show that the columns of `Z` span `ker(H)` over `Q`.

## Semantic dual and sign convention

Use the semantic dual variables

```text
lambda in Q^388                         unrestricted,
alpha in Q_+^526                        for (P2),
beta in Q_+                              for (P3),
gamma_k in Q_+                          for the 16 scalar blocks,
S_k in S_+^{r_k}                        for the 26 PSD blocks.
```

Define the exact adjoint `C^*(gamma,S) in Q^8647` blockwise.  If the
quotient entry `(i,j)` reads local Gram-orbit coordinate `e_k(i,j)`, then

```text
[C^*(gamma,S)]_{offset_k+e_k(i,j)} += (S_k)_{ij}
```

for a matrix block.  For an order-one block, add `gamma_k` at its sole entry.
Both off-diagonal matrix entries are included; this is the ordinary trace
inner product, not SCS's scaled `svec` representation.

The exact dual feasibility equations are

```text
A_u^T lambda = alpha,                                  (D1)
Z^T(A_q^T lambda - C^*(gamma,S)) = 0,                  (D2)
sum_i alpha_i + sum_k gamma_k + sum_k tr(S_k)
    - beta = 1.                                        (D3)
```

Together with exact nonnegativity and exact PSD, (D1)--(D3) are the complete
semantic stationarity and normalization conditions.  The CVXPY values
exported as

```text
dual_affine_equalities
dual_live_nu_minus_margin
dual_margin_nonnegative
dual_scalar_quotient_values
dual_psd_matrices_flat
```

have these semantic roles.  `raw_canonical_y` is retained only for auditing
the solver export.  It must not be rationalized directly because the PSD
portion uses solver-specific `svec` scaling.

## Weak-duality identity

For every exact primal-feasible `(u,q,t)` and exact dual-feasible tuple,
(D1), (D2), and `q in ker(H)` give

```text
lambda^T b
 = alpha^T u
   + sum_k gamma_k p_k(q)
   + sum_k <S_k,P_k(q)>.
```

Using (P2), (P4), (P5), and cone self-duality,

```text
lambda^T b
 >= t (sum alpha + sum gamma + sum tr(S))
 = t(1+beta)
 >= t.
```

This calculation fixes all signs independently of CVXPY's canonical row
convention.

## The two decisive exact outcomes

### A. Exact exposing face at maximum margin zero

An exact dual with

```text
lambda^T b = 0
```

proves only that every feasible primal has `t=0`.  It does **not** prove that
a feasible primal exists.  To claim an exposing face at maximum margin zero,
also supply an exact primal witness `(u,q,t=0)` satisfying:

- all 388 retained affine rows;
- `Hq=0`;
- all 56 original normalization rows and all 392 original target rows;
- exact multiplier nonnegativity;
- exact PSD of every quotient block.

The verifier then checks exact complementarity:

```text
alpha_i u_i = 0,
gamma_k p_k(q) = 0,
<S_k,P_k(q)> = 0.
```

Consequently:

- `alpha_i>0` exposes `u_i=0`;
- `gamma_k>0` exposes `p_k(q)=0`;
- `rank(S_k)>0` exposes the matrix face
  `range(P_k(q)) subset ker(S_k)`.

Exact primal feasibility plus the zero dual objective proves `max t=0`.
Without the primal witness, the accepted result is named `zero_bound`, never
`exposing_face`.

### B. Exact separating dual

An exact dual satisfying (D1)--(D3), all cone conditions, and

```text
lambda^T b < 0
```

contradicts `t>=0` by weak duality.  Therefore the fixed plateau-face primal
is infeasible.  This is an exact separating dual, not numerical evidence.
Combining it with the independently replayed necessity of the C5 plateau face
separates `c=25` from this fixed degree-4, 56-cut cone.

An exact objective greater than zero is not decisive.  A tiny floating
negative objective is not a separation.

## Reconstruction from a future numerical dual NPZ

### R1. Input and semantic replay

1. Require all hashes, format labels, dimensions, block indices, and block
   orders exported by the pinned wrapper.
2. Reject nonfinite values.
3. Rebuild `A_u`, `A_q`, `H`, `Z`, and every quotient entry map from the
   pinned exact artifacts.
4. Compute high-precision numerical residuals for (D1)--(D3) and
   `lambda^T b`.  This is steering only.
5. Use the semantic matrices, not `raw_canonical_y`, for reconstruction.

### R2. Determine a candidate dual face

For each nonnegative scalar, distinguish robustly positive coordinates from
candidate zeros.  For each numerical PSD dual matrix:

1. symmetrize it;
2. inspect its spectrum at increased arithmetic precision;
3. rationally reconstruct any numerically stable kernel;
4. verify the proposed kernel by exact linear equations.

If `U_k` is a verified exact kernel basis, form an exact rational basis
`B_k` for `ker(U_k)` and parameterize

```text
S_k = B_k R_k B_k^T
```

with symmetric `R_k`.  This keeps stationarity linear in the unknown entries
of `R_k`.  If no kernel is stable and the numerical matrix is robustly
positive definite, use `B_k=I`.  Never set a small eigenvalue to zero without
an exact affine consistency check.

### R3. Exact affine centering

For the selected face, collect the unknowns

```text
(lambda, alpha, beta, gamma, upper triangles of all R_k)
```

and build the exact sparse linear system consisting of (D1)--(D3).

- For a zero-gap candidate, append `b^T lambda=0`.
- For a separating candidate, do not force the objective to zero; retain the
  normalized system and require a strictly negative exact objective after
  repair.

Use modular rank calculations to choose a full-row-rank pivot column set.
Convert the numerical center to exact IEEE-binary `Fraction`s.  Round only
the free coordinates to a recorded denominator, then solve the pivot
coordinates by fraction-free exact elimination.  Do not form a floating
projector or a dense inverse.

### R4. Monotone denominator refinement

For denominators `D_k=10^k`, with a recorded starting `k`:

1. round the free coordinates;
2. solve the exact pivot system;
3. reconstruct every `S_k=B_k R_k B_k^T`;
4. run all exact stationarity, normalization, sign, PSD, and objective gates;
5. increase `k` on rejection.

This loop is guaranteed to stabilize only when the centered point lies in
the relative interior of the selected exact face.  If it does not, revise the
single proposed face using exact nullspace evidence or stop.  Failure at a
denominator is not evidence of infeasibility, and this protocol must not
become a solver, degree, or face cascade.

### R5. Serialize exact semantics

Write a new, non-overwriting JSON file with format

```text
R10-c5-face-exact-semantic-dual-v1
```

Fractions are canonical strings `p/q` or JSON integers.  Store:

- the six pinned input hashes;
- mode `zero_bound`, `exposing_face`, or `separating`;
- 388 exact `lambda` values;
- 526 exact `alpha` values;
- exact `beta`;
- the 16 ordered scalar block records;
- the 26 ordered PSD blocks as exact upper triangles;
- for `exposing_face`, the exact 526-entry `u` and 8,647-entry `q` witness.

The accepted JSON contains semantic dual data only.  SCS scaling, tolerances,
and status strings have no role in exact acceptance.

## Exact verifier

Build-only:

```powershell
python problems\23\round10\CODEX_R10_c5_FACE_EXACT_DUAL_VERIFIER.py
```

Explicit candidate verification:

```powershell
python problems\23\round10\CODEX_R10_c5_FACE_EXACT_DUAL_VERIFIER.py `
  --verify NEW_EXACT_DUAL.json
```

The verifier:

- rejects floats and noncanonical fractions;
- rebuilds the graph, cuts, monomial order, multiplier face, quotient order,
  and exact `H,Z` relation;
- checks exact nonnegativity and PSD by rational symmetric elimination;
- checks all of (D1)--(D3);
- checks the exact objective sign;
- for `exposing_face`, checks an exact primal witness, all 448 original rows,
  quotient PSD, and complementarity.

The independent gate has no solver, canonicalizer, candidate-processing, or
file-write call on its default path.  Its recorded log is
`CODEX_R10_c5_FACE_EXACT_DUAL_VERIFIER_GATE.log`, SHA-256
`82033370BB49025D50E8669DBE86C9EC4229A62E60EBC483A010A26630AEACCE`.

## Mandatory promotion gates

Passing the semantic verifier promotes a reconstructed object only to an
exact result about the pinned reduced cone.  Before using it in a theorem or
an impossibility claim, a separate root verifier must:

1. rebuild `Gamma_11` and all 56 cuts without importing the constructor;
2. replay the C5 equality-face necessity from the 132 complete blow-up
   supports;
3. rebuild all 448 original affine equations;
4. independently expand the dual weak-duality identity coefficient by
   coefficient;
5. independently check every rational nonnegative scalar and PSD matrix;
6. for an exposing face, independently replay the exact primal witness and
   its full Q4 identity.

Only then may:

- `exposing_face` be used for one further exact facial reduction; or
- `separating` close the fixed degree-4 cone as impossible.

Neither outcome alone proves `ARCBOUND_Gamma_11`.  A separating dual is an
exit certificate for this fixed ansatz; an exposing face is a load-bearing
finite reduction that must lead to an exact primal certificate or a later
exact separator.

## Present status

The default verifier and its independent gate pass without invoking a solver
or processing a candidate.  No numerical dual NPZ has been reconstructed,
no exact dual candidate exists, and no theorem or infeasibility claim is made.
