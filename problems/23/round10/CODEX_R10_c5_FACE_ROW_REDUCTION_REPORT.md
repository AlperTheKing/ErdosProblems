# Exact affine-row reduction on the Gamma_11 plateau face

## Result

The 448 original affine rows have exact rank 388 modulo the 6,129-row Gram face H.
All 56 normalization rows and 332 of 392 target rows are retained; 60 target rows are omitted.

The fully facially reduced linear model has 526 live multiplier variables plus the 2,518-dimensional Gram face, hence 3,044 linear face variables. The 2,085 forced-zero multiplier coordinates are not instantiated.

## Exact rank certificate

Each omitted row has a reconstructed integer relation whose coefficient on that omitted row is positive and whose other coefficients use retained rows only.
The 60 relations have support sizes 4 through 257 and maximum absolute coefficient 3522.
Exact integer multiplication gives lambda*A_nu=0 and lambda*b=0. For the Gram part, every relation was pulled back blockwise through the exact quotient Q=B R B^T and vanished identically.
Thus the triangular dependency family proves rank <=388. The independent modular minors prove rank >=388 over Q.

```text
p=1000003 rank(H)=6129 rank([H;A])=6517 rank(A mod H)=388
p=2000003 rank(H)=6129 rank([H;A])=6517 rank(A mod H)=388
```

## Solver-model selector

Use the exported matrices exactly as

```text
nu_live in R^526
affine_nu * nu_live + affine_gram * q = affine_rhs  # 388 rows
H * q = 0                                           # unchanged
nu_live >= t
t >= 0
quotient Gram principal blocks >= t I               # unchanged
```

Do not create the 2,085 forced multiplier variables and do not add 2,085 zero-fixing equalities. The constant c=25, degree 4, all 56 cuts, D22 invariance, H, and quotient PSD cones are unchanged.

## Scope

No SDP was solved. This is an exact facial/row reduction and does not itself constitute a Q4 certificate or theorem proof.
