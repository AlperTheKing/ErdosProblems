# D-optimal Matrix of Order 198 — Approach Registry

Selected: 2026-07-18
Deadline: 2026-07-18T21:57:27+03:00
Status: DEAD — validation gate failed (0/64 zero-energy reproductions)

## Exact target

Construct a `{+1,-1}` matrix of order 198 attaining the Ehlich--Wojtas
determinant bound `394 * 196^98`. This is the smallest order for which the
existence of such an EW/D-optimal matrix remains unsettled. Emit the matrix,
a compact two-circulant certificate, two independent integer verifiers, and a
Lean 4 proof of the certificate bridge when feasible. No `native_decide` and
no `sorry` may occur in the submitted proof.

## DIRECT ROUTE

### 1. Exact final deliverable

Two subsets `X,Y` of `ZMod 99`, with `|X|=43` and `|Y|=42`, such that for
every nonzero `d` modulo 99,

`|X ∩ (X+d)| + |Y ∩ (Y+d)| = 36`.

The final artifacts are the two 99-bit strings, the resulting `198 x 198`
matrix, and two independent exact verifiers. A nonzero energy, a new lower
bound, or a solution for another order is not the deliverable.

### 2. Current frontier lemma / finite certificate

`D198-SDS`: find a cyclic supplementary difference set with parameters
`(99;43,42;36)`. Equivalently, for the two associated `{+1,-1}` sequences
`A,B`, their periodic autocorrelations satisfy

`PAF_A(d) + PAF_B(d) = 2`

for each of the 98 nonzero shifts. By reversal symmetry it suffices to score
the 49 shifts `1 <= d <= 49`, but the verifier must check all 98.

### 3. Explicit logical bridge

Let `C_A,C_B` be the circulant matrices with first rows `A,B`, and form

`M = [[C_A, C_B], [-C_B^T, C_A^T]]`.

Circulants commute, so the off-diagonal blocks of `M M^T` vanish. The SDS
equalities give

`C_A C_A^T + C_B C_B^T = 196 I_99 + 2 J_99 = L`.

Thus `M M^T = diag(L,L)`. Since `L` has eigenvalues 394 once and 196 with
multiplicity 98, `|det M| = det L = 394 * 196^98`, exactly the
Ehlich--Wojtas upper bound. Therefore the certificate settles the order-198
D-optimal existence problem, not merely a restricted optimization problem.

### 4. Next falsifiable action

Completed. The published `(87;38,36;31)` order-174 certificate passed two
independent exact audits. The unrestricted fixed-weight engine then ran 64
random starts of 2,000,000 swaps each; all 64 incremental states passed raw
recomputation, but none reached zero (best half-shift energy 18). The required
validation success rate was at least 90%, so no `v=99` run is permitted.


### 5. Exit condition

Exit immediately on any certificate/verifier disagreement. If the validation
success rate is below 90%, or validation exceeds 45 minutes, close the route;
an uncalibrated lottery has no time-to-solution bridge. If validation passes,
run the fixed `v=99` schedule only until the deadline. At the deadline, or
after three completed parameter/engine cycles without a verifiable zero,
preserve the best states and stop. Do not substitute a low-energy state, a
restricted symmetry lane, a fresh lower bound, or another matrix order.

## Exit record

The registered validation finished in 2.847 seconds with `0/64` successes,
`64/64` audited final states, and best energy 18. The route was closed before
any order-198 search or CUDA implementation. All artifacts are preserved.


## Novelty gate snapshot

- The maximal-determinant problem goes back to Hadamard (1893).
- Djokovic--Kotsireas (2014) identified order 198 as the smallest unsettled
  D-optimal order after constructing order 174.
- A 2025 thesis still states that order 198 is the smallest unsettled EW order.
- A search on 2026-07-18 found no construction or current solution claim for
  `(99;43,42;36)`.
