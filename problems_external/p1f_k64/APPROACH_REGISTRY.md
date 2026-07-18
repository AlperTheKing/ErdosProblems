# Perfect 1-Factorisation of K64 — Approach Registry

Selected: 2026-07-18
Deadline: 2026-07-18T21:57:27+03:00
Status: DEAD — mandatory CUDA throughput gate failed

## Exact target

Construct a perfect 1-factorisation (P1F) of the complete graph `K_64`: a
partition of its 2016 edges into 63 perfect matchings such that the union of
every two distinct matchings is a Hamilton cycle. Emit a compact certificate,
an independent verifier, and, if the certificate exists, a no-`sorry`,
no-`native_decide` Lean proof suitable for a Google DeepMind Formal
Conjectures pull request.

## DIRECT ROUTE

### 1. Exact final deliverable

Thirty disjoint unordered pairs `E = {{x_r,y_r} : 1 <= r <= 30}` in
`ZMod 62`, an independently checked text/JSON certificate, the 63 developed
perfect matchings on `ZMod 62 ∪ {∞₀,∞₁}`, and verification that every pair of
matchings has a 64-cycle union. The Lean deliverable will formalise Kotzig's
conjecture and its exact `K_64` variant, then prove the variant from the
certificate without `sorry` or `native_decide`.

### 2. Current frontier lemma / finite certificate

`K64-EVEN-STARTER`: find 30 disjoint pairs in `ZMod 62` whose signed
differences are exactly `ZMod 62 \ {0,31}`.

Let `a,b` be the two omitted residues. Define

`M_i = (E+i) ∪ {{∞₀,a+i},{∞₁,b+i}}` for `i ∈ ZMod 62`,

and

`M_* = {{∞₀,∞₁}} ∪ {{x,x+31} : 0 <= x < 31}`.

The certificate must pass exactly 32 cycle tests: `M_* ∪ M_0`, and
`M_0 ∪ M_d` for `d=1,...,31`. Every union must be one 64-cycle.

The instantiated frontier is the Wolfe--Pike representation: two compatible
starters in `ZMod 31` whose union is an alternating Hamilton path, plus 15
complementary high/low bits. Wolfe's merger maps this finite state to an even
starter in `ZMod 62`.

### 3. Explicit logical bridge

Difference uniqueness makes the 62 translates `M_i` partition all finite
non-antipodal edges. The omitted residues make them partition all
infinity--finite edges. `M_*` supplies every antipodal finite edge and
`{∞₀,∞₁}`. Thus the 63 matchings partition every edge of `K_64` exactly once.

Cyclic translation fixes `M_*` and sends `M_i` to `M_(i+t)`. Hence all 1953
unordered factor pairs lie in 32 orbits: one represented by `M_* ∪ M_0`, and
31 represented by `M_0 ∪ M_d` modulo `d ~ -d`. Each union is spanning and
2-regular, so the 32 single-cycle checks imply a P1F of `K_64`.

### 4. Next falsifiable action

Build two independent integer verifiers. First reproduce David Pike's
published `K_56` even starter, its factorisation, and all 28 symmetry-orbit
Hamilton checks. Then reproduce Pike's merger from his two `ZMod 27` starters.
Only after both agree, compile a CUDA `K_64` merger/evaluator.

Run a correctness warm-up over at least `2^16` distinct compatible `ZMod 31`
starter pairs with all `2^15` masks. Then run a 300-second sustained gate that
must supply and consume at least `2^26` compatible pairs while reporting host
generation and GPU evaluation separately.

The gate passes only if end-to-end rates reach both 300,000 compatible
starter pairs/second and 10 billion high/low assignments/second, with sampled
scores rechecked independently. These are the minimum rates needed to match
the roughly 10.3-billion-pair exposure of the historical `K_56` search within
the remaining budget. A pass permits one checkpointed run until the deadline;
it does not justify a nonexistence claim.

### 5. Exit condition

Exit immediately if either verifier rejects the published `K_56` certificate,
the merger reproduction fails, either benchmark threshold is missed, a prior
`K_64` certificate/claim is found, or a candidate fails independent checking.
If the single registered full run finds no exact certificate by the deadline,
preserve all artifacts and stop. Do not add another symmetry family, restart
portfolio, weakened Hamilton result, lower bound, or nonexistence claim.

## Novelty gate snapshot

- Anton Kotzig posed the P1F conjecture in 1963.
- Cheng and Sgueglia (arXiv:2607.09459, 10 July 2026) call it famous, state
  that it remains far from solved, and give only an asymptotic result.
- Current sources still identify `K_64` as the smallest unresolved order.
- Exact-title, arXiv, web, indexed GitHub, and the local Formal Conjectures
  snapshot contained no `K_64` certificate or solution claim on 2026-07-18.
- Pike's `K_56` discovery (arXiv:1810.08734) required an estimated 10.3
  billion starter pairs and about 1,064,700 worker-hours; this motivates the

## Exit record — 2026-07-18

The independently checked final exact kernel evaluated
`5 × 65,536 × 32,768 = 10,737,418,240` assignments in 2.046 seconds:
`5.2478` billion assignments/second and `160,150` compatible starter
pairs/second. Both mandatory thresholds (`10` billion assignments/second
and at least `300,000` pairs/second) failed. The registered exit condition
therefore forbids the 300-second gate and the full K64 search.
  mandatory throughput gate rather than a claim of likely success.
