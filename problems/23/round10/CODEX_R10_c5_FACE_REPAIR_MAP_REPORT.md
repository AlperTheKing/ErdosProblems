# Sparse exact repair map for a future plateau-face iterate

## Result

A square exact affine repair uses 322 live multiplier coordinates and 66 D22-invariant quotient Gram directions.
The Gram directions occur in representative blocks {0: 64, 1: 1, 5: 1} and satisfy H d=0 exactly.
The integer repair matrix has shape [388, 388], 14316 nonzeros, and rank 388 modulo each of [1000003, 2000003, 998244353].

No dense affine projector is formed or stored.

## Finite exact reconstruction algorithm

1. Read a positive numerical point and extract 526 live nu values.
2. For each representative Gram block take Q[C,C], rationally round it, lift with exact B, and Reynolds-average over the stabilizer.
3. Form the exact residual r=b-A_nu*nu-A_gram*q.
4. Solve the stored 388x388 integer repair system M*delta=r exactly; do not form a dense projector.
5. Apply 322 corrections directly to selected nu coordinates and 66 corrections through the stored Gram directions.
6. Require exact nonnegative nu, Hq=0, all 448 original equations, exact quotient PSD, exact expanded Q4_verify, and an independent replay.
7. If a cone check fails, increase the rounding denominator. If the exact-binary repaired center itself lacks cone margin, reject the numerical point and request a more accurate positive iterate.

The exact repair solve changes only the 388 selected coordinates. Every Gram correction remains on the exact kernel face and inside the D22-invariant coordinate space.

## Acceptance gates

- Exact nonnegativity of all live multipliers; forced multipliers expand as exact zeros.
- Exact Hq=0 and exact satisfaction of the 388 retained rows.
- Direct exact replay of all 448 original affine rows.
- Exact blockwise factorization Q=B Q[C,C] B^T and exact PSD of every quotient principal matrix.
- Expansion to Fraction-valued D22 copies and round7/Q4_verify.verify with n=11, d=2, c=25.
- A separate independent exact replay that rebuilds Gamma_11, the 56 cuts, monomials, coefficient identity, and PSD checks.

A failed denominator attempt is not evidence against the certificate ansatz. Increase the denominator. If the exactly repaired binary-float center itself is not inside the relative interior, obtain a more accurate positive numerical point.

## Scope

This is a build-only repair map and acceptance protocol. No SDP was run and no theorem is claimed.
