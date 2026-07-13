# Erdos Problem 424: one-hour sprint result

## Verdict

**NOT SOLVED.** The sprint proves neither positive lower density nor zero
density for the distinct-value closure from seeds 2 and 3.

## Strongest unconditional advance

For every `X>=9`,

`|A intersect [1,X]| >= (1/6)(X/9)^(log 6 / log 30)`.

Proof: the six permutations of multipliers `2,3,5` give six distinct
base-30 digits `{9,10,13,16,19,21}` per three-operation block. See
`fanout/wave2/B07_nonlinear_bootstrap.md`.

## Exact evidence

- Two independent generators agree through `10^7`.
- `A(10^8)=51,899,129`; maximum observed gap is 21.
- The frozen `{2,3,5}` subsystem has `18,222,202,754` members through
  `10^11`, density `0.18222202754`.
- Its exact orbit modulo `30^7` occupies `6,011,481,468` of
  `21,870,000,000` residues.

These finite facts have no asymptotic force.

## Rigorous route obstructions

1. Every globally residue-decodable finite affine block automaton is strictly
   subcritical; see `fanout/wave2/B03_affine_automaton.md`.
2. Periodic composition covers require
   `exists d: d divides gcd(q,r+2)` on every residue `qZ+r`; exhaustive
   bounded searches found no certificate; see `B05_exact_cover_compositions.md`.
3. Word injectivity fails at length six:
   `T_322255=T_255232=600x-381`.
4. Generic nonlinear bootstrap is false. The full distinct-input closure of
   seeds `{9,10}` has polynomial lower growth and nevertheless density zero;
   see `B07_nonlinear_bootstrap.md`.
5. A factor sieve using only discovered small divisors has an unavoidable
   blind family of order `X/sqrt(log X)`; see
   `B08_nonlinear_factor_sieve.md`.

## Remaining theorem-strength frontier

Prove a seed-specific lower bound for distinct restricted products in

`A={2,3} disjoint_union ((A restricted-times A)-1)`,

or an equivalent collision estimate that exploits arithmetic special to 2
and 3. The frozen-alphabet summable-collision lemma is sufficient but current
exact data does not support its simplest forms.

## Verification boundary

No Lean formalization was completed. Exact computations are reproducible
under `problems/424/compute/`; the overall inventory is in
`fanout/SPRINT_REFEREE.md`.

6. No nonempty periodic set `P` can satisfy
   `P subset union_(d in D) (dP-1)` for finite `D`; a largest-negative-element
   argument kills every eventual-full-residue-class certificate. The 23-multiplier
   frozen subsystem nevertheless has `45,233,066` members through `10^8`.
   See `B06_complement_sieve.md`.
