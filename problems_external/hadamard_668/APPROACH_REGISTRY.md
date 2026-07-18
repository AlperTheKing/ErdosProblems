# Hadamard Matrix of Order 668 — Approach Registry

Selected: 2026-07-18
Deadline: 2026-07-18T21:57:27+03:00
Status: DEAD — all registered direct families closed; no certificate found

## Exact target

Prove the existing Google DeepMind Formal Conjectures theorem
`Hadamard.HadamardConjecture.variants.«167»` by constructing a matrix
`H : Matrix (Fin 668) (Fin 668) ℝ` with entries in `{1, -1}` and
`|H.det| = 668 ^ (668 / 2 : ℝ)`. Also emit an independently checkable CSV or
four-sequence certificate. The proof must add no `sorry` and must not use
`native_decide`.

## DIRECT ROUTE

### 1. Exact final deliverable

Four explicit subsets `X₁, X₂, X₃, X₄ ⊆ ZMod 167`, their Goethals–Seidel
matrix of order `4 * 167 = 668`, an integer verifier showing
`H * Hᵀ = 668 I`, and a Lean proof of the exact theorem above. A positive
certificate closes the order-668 case; a search bound or low-defect matrix
does not.

### 2. Current frontier lemma / finite certificate

`H668-SDS`: find cardinalities `k₁,...,k₄ ≤ 83`, put
`λ = k₁ + k₂ + k₃ + k₄ - 167`, and find four subsets of those cardinalities
such that, for every nonzero `d ∈ ZMod 167`,

`∑ᵢ |Xᵢ ∩ (Xᵢ + d)| = λ`.

Equivalently, the four associated `±1` sequences have summed periodic
autocorrelation zero at every nonzero shift. This is a finite certificate:
four 167-bit strings plus their cardinalities.

The highest-leverage instantiated frontier is `H668-Paley`: let `Q` be the
83 nonzero quadratic residues modulo 167. Find `Y,Z ⊆ ZMod 167` with
`|Y|=76`, `|Z|=73`, and

`|Y ∩ (Y+d)| + |Z ∩ (Z+d)| = 66`

for every nonzero `d`. The symmetric/symmetric subfamily is impossible:
for `X=-X`, `N_X(d) mod 2` is the membership bit of the sign-pair containing
`d/2`; an even target 66 would force `Y` and `Z` to choose identical sign
pairs, contradicting their required counts 38 and 36. The first live finite
subfamily is therefore symmetric/unrestricted (and its reciprocal), followed
by the fully unrestricted pair.

### 3. Explicit logical bridge

The SDS equalities imply that the four circulant `±1` matrices `A,B,C,D`
satisfy `AAᵀ + BBᵀ + CCᵀ + DDᵀ = 668 I`. Substitution into the standard
Goethals–Seidel block array gives a `668 × 668` `±1` matrix `H` with
`HHᵀ = 668 I`. Taking determinants gives
`|det H| = 668^(668/2)`, hence `Hadamard.IsHadamard H` and the exact Formal
Conjectures existential theorem.

For `H668-Paley`, `Q` is a `(167,83,41)` difference set, so two copies
contribute `41+41` at every nonzero difference. The two-block target
contributes 66, hence `(Y,Q,Q,Z)` is exactly an SDS with lambda 148 and the
same Goethals–Seidel implication gives the final order-668 matrix.

### 4. Next falsifiable action

Completed. The broad ten-parameter run, all three Paley pair lanes, and the
registered kick sizes `1,4,16,64` found no zero; the audited best pair energy
is 86. The only permitted final family was a cyclic `(667,333,166)` Hadamard
difference set. Its bordered-development bridge is valid, but Baumert--Gordon
Theorem 2.3 (Mann's test) excludes the antecedent: for `v=667=23*29`,
`n=k-lambda=167`, take `w=29`, `p=167`; then `p^2` does not divide `n` and
`167^7 = -1 (mod 29)`. No search is permitted for a theorem-impossible family.

### 5. Exit condition

Exit this route immediately if a purported certificate fails the independent
integer verifier. If no zero-defect SDS is found after the registered
parameter sets and scheduled restart budget, do not turn low defect, a larger
search bound, a restricted nonexistence result, or another matrix ansatz into
a substitute theorem. After the four registered kick sizes, no further cyclic
SDS restart or local-repair branch may be added. One further direct
construction family may be opened only after its implication to order 668 is
written here. At the deadline, preserve all artifacts and stop without a
solution claim. This exit condition was met before the deadline: the cyclic
SDS budget ended without a certificate, and the one allowed final family is
excluded by Mann's theorem. No registered direct construction route remains.

## Final-family audit

- The bridge was correct. If `C` is the development of a
  `(667,333,166)` cyclic difference set, then
  `C*C^T = 167 I + 166 J`. With `A=J-2C`, one gets
  `A*A^T=668 I-J` and `A*1=1`; bordering `A` gives a Hadamard matrix of
  order 668.
- The antecedent is impossible by Leonard D. Baumert and Daniel M. Gordon,
  *On the existence of cyclic difference sets with small parameters*,
  Theorem 2.3, arXiv:math/0304502. The instance is
  `w=29`, `p=167`, `j=7`.
- Bruck--Ryser--Chowla does not exclude it: its required equation has the
  solution `(x,y,z)=(1,1,1)`. The Mann obstruction is load-bearing.
- T-matrix/T-sequence order 167 and symmetric-conference/SRG routes were
  audited as distinct possibilities but do not provide a viable one-day
  finite frontier. Opening either would violate the registered final-family
  limit and the direct-proof guard.

## Novelty gate snapshot

- The conjecture was explicitly stated by Paley in 1933 and remains open.
- Order 668 has been the smallest unknown order since order 428 was
  constructed in 2004.
- Epoch AI's 2026 FrontierMath page asks for exactly a matrix of order 668.
- The local Formal Conjectures snapshot at commit `c252a410` contains the
  exact open theorem in `FormalConjectures/Wikipedia/Hadamard.lean`.
- No published construction or verifiable current solution claim was found
  in the selection search on 2026-07-18.
