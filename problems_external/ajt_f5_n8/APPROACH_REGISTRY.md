# Alon-Jaeger-Tarsi over F5 in dimension 8 — Approach Registry

Status checked: 2026-07-21.

## CURRENT-STATUS GATE

- AJT states that every nonsingular matrix `A` over a finite field of size at least 4 has a vector `x` such that both `x` and `Ax` have no zero coordinate.
- Nagy and Pach (2026), arXiv:2604.26320, state that the prime cases `5 <= p <= 61` and `p = 79` remain open.
- Yu's theorem, quoted in Nagy and Pach (2021), arXiv:2107.03956, proves AJT for `n < 2^(p-2)`. For `p=5`, this covers `n <= 7` and does not cover `n=8`.
- A targeted current search found no published resolution of the case `p=5, n=8`. This is a novelty gate for the finite case, not a claim that no unpublished computation exists.

## DIRECT ROUTE — explicit counterexample at p=5, n=8

1. Exact final deliverable

   An explicit matrix `A in GL(8,F5)` for which every `x in (F5*)^8` has at least one zero coordinate in `Ax`, together with two independent exhaustive verifiers over all `4^8 = 65536` vectors. This single certificate refutes the AJT conjecture.

2. Current frontier lemma or finite certificate

   Find eight linearly independent row vectors `r_1,...,r_8 in F5^8` whose kernel hyperplanes cover the torus `T=(F5*)^8`:

   `T subseteq ker(r_1) union ... union ker(r_8)`.

3. Explicit logical bridge

   Linear independence makes the row matrix `A` nonsingular. Hyperplane coverage says that, for every nowhere-zero `x`, some row dot product is zero; hence `Ax` is not nowhere-zero. Therefore `A` has no AJT witness and is a counterexample to the full conjecture.

4. Next falsifiable action

   Build exact 65536-bit kernel masks for normalized projective rows, validate the mask and rank implementations on exhaustive small cases, and run independent stochastic-cover and SAT/CP-SAT searches for eight masks whose union is `T` and whose rows have rank 8. Every reported hit must be checked by separate scalar and bitset verifiers.

5. Exit condition

   - Success: a matrix passes both independent exhaustive verifiers; stop search and run a fresh novelty check.
   - Finite closure: a proof-producing exact solver establishes that no such matrix exists for `p=5,n=8`; report only this finite theorem, not AJT, and stop this lane.
   - Resource exit: if the frozen `n=8` attack cannot produce a verified hit or exact no-hit certificate within the agreed compute budget, stop. Do not cascade to larger dimensions or replace the target by asymptotic surrogates.

## ALLOWED NORMALIZATIONS

- Permute rows and scale individual rows by nonzero field elements.
- Permute columns and scale individual columns by nonzero field elements.
- Do not use general row addition or general changes of basis: the nowhere-zero condition is not invariant under them.

## REFERENCES

- J. Nagy and P. P. Pach, *On a group ring identity related to the Alon-Jaeger-Tarsi conjecture*, arXiv:2604.26320 (2026).
- J. Nagy and P. P. Pach, *The Alon-Jaeger-Tarsi conjecture via group ring identities*, arXiv:2107.03956 (2021).
- Y. Yu, *The Permanent Rank of a Matrix*, J. Combin. Theory Ser. A 85 (1999), 237-242.
